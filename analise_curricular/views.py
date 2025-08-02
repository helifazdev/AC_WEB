# analise_curricular/views.py

import os
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Max
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
# Remova DocumentoForm deste import
from .forms import DynamicCandidatoForm, AvaliadorSignUpForm, SelecaoForm
from .models import Candidato, Selecao, DocumentoCandidato, FormQuestion

logger = logging.getLogger(__name__)

def inscricao_finalizada(request):
    return render(request, 'Registration/inscricao_finalizada.html')

def tela_entrada(request):
    return render(request, 'tela_entrada.html')

@login_required
def analisar_candidato(request, candidato_id):
    logger.debug(f"Session data: {dict(request.session)}")
    logger.debug(f"Candidato ID: {candidato_id}")
    
    selecao_id = request.session.get('selecao_id')
    logger.debug(f"Selecao ID from session: {selecao_id}")
    
    if not selecao_id:
        logger.error("Nenhum selecao_id encontrado na sessão")
        messages.error(request, "Por favor, selecione uma seleção antes de analisar candidatos.")
        return redirect('selecionar_selecao')
    
    try:
        candidato = Candidato.objects.get(pk=candidato_id, selecao__id=selecao_id)
    except Candidato.DoesNotExist:
        messages.error(request, "Candidato não encontrado ou não pertence à seleção atual.")
        return redirect('painel_avaliador', selecao_id=selecao_id)
    except Exception as e:
        logger.error(f"Erro ao buscar candidato: {e}")
        messages.error(request, "Ocorreu um erro ao carregar o candidato.")
        return redirect('selecionar_selecao')

    candidatos_da_selecao = Candidato.objects.filter(selecao__id=selecao_id).order_by('id')
    total_candidatos = candidatos_da_selecao.count()

    if total_candidatos == 0:
        return render(request, 'Registration/sem_candidatos_nao_selecao.html', {
            'selecao_nome': request.session.get('selecao_nome', 'Nenhuma Seleção Selecionada')
        })

    # 4. Processar documentos do candidato - AGORA SOMENTE LENDO DO DIRETÓRIO
    documentos_candidato = []
    # Usar a inscrição do candidato para formar o padrão de busca no nome do arquivo
    # Remove qualquer '#' do início da inscrição, se houver, para a busca
    inscricao_limpa = candidato.inscricao.lstrip('#') 
    
    documentos_dir = os.path.join(settings.MEDIA_ROOT, 'candidatos_documentos')
    
    if os.path.exists(documentos_dir):
        for filename in os.listdir(documentos_dir):
            # Verifica se a inscrição do candidato (limpa) está presente no nome do arquivo
            # Ex: 'Pergunta1_105500_fdpffgf' -> busca por '105500'
            if f'_{inscricao_limpa}_' in filename:
                document_url = settings.MEDIA_URL + 'candidatos_documentos/' + filename
                documentos_candidato.append({
                    'nome': filename,
                    'url': document_url,
                })

    # 5. Processar POST request
    if request.method == 'POST':
        form = DynamicCandidatoForm(
            request.POST, 
            instance=candidato,
            selecao_id=selecao_id
        )
        if form.is_valid():
            candidato = form.save(commit=False)
            candidato.analisado = True
            candidato.data_analisado = timezone.now()
            candidato.avaliador_analise = request.user
            candidato.save()

            messages.success(request, "Dados salvos com sucesso!")

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Dados salvos com sucesso!'})
            
            next_candidato = candidatos_da_selecao.filter(id__gt=candidato.id).order_by('id').first()
            if next_candidato:
                return redirect('analisar_candidato', candidato_id=next_candidato.id)
            
            return redirect('finalizar_analise') 
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
         form = DynamicCandidatoForm(
            instance=candidato,
            selecao_id=selecao_id
        )

    # 6. Calcular navegação entre candidatos
    ids_ordenados = list(candidatos_da_selecao.values_list('id', flat=True))
    try:
        indice_atual = ids_ordenados.index(candidato.id) + 1
    except ValueError:
        indice_atual = 0

    anterior_candidato = None
    if indice_atual > 1:
        anterior_candidato = candidatos_da_selecao.filter(id__lt=candidato.id).order_by('-id').first()

    proximo_candidato = None
    if indice_atual < total_candidatos:
        proximo_candidato = candidatos_da_selecao.filter(id__gt=candidato.id).order_by('id').first()

    # 7. Preparar contexto final
    context = {
        'form': form,
        'candidato': candidato,
        'selecao_id': selecao_id,
        'selecao_nome': candidato.selecao.nome if candidato.selecao else request.session.get('selecao_nome', ''),
        'indice_atual': indice_atual,
        'total_candidatos': total_candidatos,
        'anterior_candidato_id': anterior_candidato.id if anterior_candidato else None,
        'proximo_candidato_id': proximo_candidato.id if proximo_candidato else None,
        'data_formatada': _("Hoje é %(date)s") % {'date': timezone.now().strftime('%d de %B de %Y')},
        'documentos_candidato': documentos_candidato,
        'data_avaliacao': candidato.data_analisado,
        'avaliador': candidato.avaliador_analise,
        'perguntas': FormQuestion.objects.filter(selecao=candidato.selecao).order_by('order')
    }

    return render(request, 'Registration/formulario.html', context)


@login_required
def finalizar_analise(request):
    messages.success(request, "Análise finalizada. Todas as informações foram salvas.")
    return render(request, 'finalizar_analise.html', {
        'data_formatada': _("Hoje é %(date)s") % {'date': timezone.now().strftime('%d de %B de %Y')}
    })

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('selecionar_selecao')
            else:
                form.add_error(None, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

@login_required
def selecionar_selecao(request):
    if request.method == 'POST':
        form = SelecaoForm(request.POST)
        if form.is_valid():
            selecao_escolhida = form.cleaned_data['selecao_disponivel']
            request.session['selecao_id'] = selecao_escolhida.id
            request.session['selecao_nome'] = selecao_escolhida.nome
            return redirect('painel_avaliador', selecao_id=selecao_escolhida.id)
    else:
        form = SelecaoForm()
    
    return render(request, 'Registration/selecionar_selecao.html', {'form': form})

# As views upload_documento e deletar_documento não são mais necessárias e foram removidas.
# O modelo DocumentoCandidato pode ser removido se não for usado para mais nada.

def avaliador_signup(request):
    if request.method == 'POST':
        form = AvaliadorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inscricao_finalizada')
    else:
        form = AvaliadorSignUpForm()
    return render(request, 'Registration/signup.html', {'form': form})

@login_required
def painel_avaliador(request, selecao_id):
    selecao = get_object_or_404(Selecao, pk=selecao_id)
    candidatos = Candidato.objects.filter(selecao=selecao).order_by('inscricao')

    nome_filtro = request.GET.get('nome_filtro')
    inscricao_filtro = request.GET.get('inscricao')
    cargo_filtro = request.GET.get('cargo')

    if nome_filtro:
        candidatos = candidatos.filter(nome__icontains=nome_filtro)
    
    if inscricao_filtro:
        inscricao_limpa = ''.join(c for c in inscricao_filtro if c.isdigit())
        candidatos = candidatos.filter(inscricao__endswith=inscricao_limpa)
    
    if cargo_filtro:
        candidatos = candidatos.filter(cargo__icontains=cargo_filtro)

    context = {
        'selecao': selecao,
        'candidatos': candidatos,
        'todos_avaliados': not candidatos.filter(analisado=False).exists()
    }
    return render(request, 'Registration/painel_avaliador.html', context)

@login_required
def listar_documentos(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)
    
    documentos = []
    inscricao_limpa = candidato.inscricao.lstrip('#') 
    pasta = os.path.join(settings.MEDIA_ROOT, 'candidatos_documentos')
    
    if os.path.exists(pasta):
        for arquivo in os.listdir(pasta):
            # Verifica se a inscrição do candidato está no nome do arquivo
            if f'_{inscricao_limpa}_' in arquivo:
                documentos.append({
                    'nome': arquivo,
                    'url': os.path.join(settings.MEDIA_URL, 'candidatos_documentos', arquivo)
                })
    
    return render(request, 'listar_documentos.html', {
        'candidato': candidato,
        'documentos': documentos
    })