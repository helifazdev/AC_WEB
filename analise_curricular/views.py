# analise_curricular/views.py

import os
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
from .forms import CandidatoForm, AvaliadorSignUpForm, SelecaoForm, DocumentoForm
from .models import Candidato, Selecao, DocumentoCandidato

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
        return redirect('selecionar_selecao')
    
    # 1. Verificação inicial da sessão
    selecao_id = request.session.get('selecao_id')
    if not selecao_id:
        return redirect('selecionar_selecao')

    # 2. Obter candidato e verificar se pertence à seleção
    try:
        candidato = Candidato.objects.get(pk=candidato_id, selecao__id=selecao_id)
    except Candidato.DoesNotExist:
        return redirect('selecionar_selecao')

    # 3. Obter lista de candidatos da seleção
    candidatos_da_selecao = Candidato.objects.filter(selecao__id=selecao_id).order_by('id')
    total_candidatos = candidatos_da_selecao.count()

    if total_candidatos == 0:
        return render(request, 'Registration/sem_candidatos_na_selecao.html', {
            'selecao_nome': request.session.get('selecao_nome', 'Nenhuma Seleção Selecionada')
        })

    # 4. Processar documentos do candidato
    # Buscar documentos do candidato
    documentos_candidato = []
    documentos_dir = os.path.join(settings.MEDIA_ROOT, 'candidatos_documentos')
    
    if os.path.exists(documentos_dir):
            for filename in os.listdir(documentos_dir):
                # Verifica se o nome segue o padrão e corresponde à inscrição do candidato
                partes = filename.split('_')
                if len(partes) >= 3 and partes[1] == str(candidato.inscricao):
                    document_url = settings.MEDIA_URL + 'candidatos_documentos/' + filename
                    documentos_candidato.append({
                        'tipo': partes[0],
                        'nome': filename,
                        'url': document_url,
                    })

    # 5. Processar POST request
    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            candidato = form.save(commit=False)
            candidato.analisado = True
            candidato.analisado = True
            candidato.data_analisado = timezone.now()  # Adiciona a data atual
            candidato.avaliador_analise = request.user  # Adiciona o usuário logado
            candidato.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            next_candidato = candidatos_da_selecao.filter(id__gt=candidato.id).order_by('id').first()
            if next_candidato:
                return redirect('analisar_candidato', candidato_id=next_candidato.id)

            return redirect('finalizar_analise')  # Redirecionamento fora do bloco if
        elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        # Se não for AJAX e o form for inválido, continua para mostrar os erros
    else:
        form = CandidatoForm(instance=candidato)

    # 6. Calcular navegação entre candidatos
    ids_ordenados = list(candidatos_da_selecao.values_list('id', flat=True))
    try:
        indice_atual = ids_ordenados.index(candidato.id) + 1
    except ValueError:
        indice_atual = 1

    anterior_candidato = candidatos_da_selecao.filter(id__lt=candidato.id).order_by('-id').first()

    # 7. Preparar contexto final
    context = {
        'form': form,
        'candidato': candidato,
        'selecao_id': selecao_id,
        'selecao_nome': candidato.selecao.nome if candidato.selecao else request.session.get('selecao_nome', ''),
        'indice_atual': indice_atual,
        'total_candidatos': total_candidatos,
        'anterior_candidato_id': anterior_candidato.id if anterior_candidato else None,
        'data_formatada': _("Hoje é %(date)s") % {'date': timezone.now().strftime('%d de %B de %Y')},
        'documentos_candidato': documentos_candidato,
        'documentos_dir': settings.MEDIA_URL + 'candidatos_documentos/',
        'data_avaliacao': candidato.data_analisado,  # Adiciona ao contexto
        'avaliador': candidato.avaliador_analise     # Adiciona ao contexto
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
                return redirect('selecionar_selecao')  # Redirect to selection page
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
            # CRUCIAL CHANGE: Pass selecao_id as an argument to the URL
            return redirect('painel_avaliador', selecao_id=selecao_escolhida.id)
    else:
        form = SelecaoForm()
    
    return render(request, 'Registration/selecionar_selecao.html', {'form': form})

def upload_documento(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.candidato = candidato
            documento.save()
            messages.success(request, "Documento enviado com sucesso!")
            return redirect('analisar_candidato', candidato_id=candidato.id)
    else:
        form = DocumentoForm()
    
    return render(request, 'upload_documento.html', {
        'form': form,
        'candidato': candidato
    })

@login_required
def deletar_documento(request, documento_id):
    documento = get_object_or_404(DocumentoCandidato, pk=documento_id)
    candidato_id = documento.candidato.id
    
    if request.method == 'POST':
        documento.delete()
        messages.success(request, "Documento excluído com sucesso!")
        return redirect('upload_documento', candidato_id=candidato_id)
    
    return render(request, 'confirmar_delete.html', {'documento': documento})

def avaliador_signup(request):
    if request.method == 'POST':
        form = AvaliadorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inscricao_finalizada')  # Redireciona para a página de confirmação
    else:
        form = AvaliadorSignUpForm()
    return render(request, 'Registration/signup.html', {'form': form})

@login_required
def painel_avaliador(request, selecao_id):
    selecao = get_object_or_404(Selecao, pk=selecao_id)
    candidatos = Candidato.objects.filter(selecao=selecao).order_by('inscricao')  # Note o campo 'inscricao'

    # Filtros
    nome_filtro = request.GET.get('nome_filtro')
    inscricao_filtro = request.GET.get('inscricao')
    cargo_filtro = request.GET.get('cargo')

    if nome_filtro:
        candidatos = candidatos.filter(nome__icontains=nome_filtro)
    
    if inscricao_filtro:
        # Busca exata para inscrição (case insensitive)
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
    pasta = os.path.join(settings.MEDIA_ROOT, 'candidatos_documentos')
    
    if os.path.exists(pasta):
        for arquivo in os.listdir(pasta):
            if f"_{candidato.inscricao.lstrip('#')}_" in arquivo:
                documentos.append({
                    'nome': arquivo,
                    'url': os.path.join(settings.MEDIA_URL, 'candidatos_documentos', arquivo)
                })
    
    return render(request, 'listar_documentos.html', {
        'candidato': candidato,
        'documentos': documentos
    })

import logging
logger = logging.getLogger(__name__)

