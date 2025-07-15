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
from django.utils.translation import gettext_lazy as _


from .forms import CandidatoForm, AvaliadorSignUpForm, SelecaoForm, DocumentoForm
from .models import Candidato, Selecao, DocumentoCandidato

def inscricao_finalizada(request):
    return render(request, 'Registration/inscricao_finalizada.html')

def tela_entrada(request):
    return render(request, 'tela_entrada.html')

@login_required
def analisar_candidato(request, candidato_id=None):
    selecao_id = request.session.get('selecao_id')
    selecao_nome = request.session.get('selecao_nome', 'Nenhuma Seleção Selecionada')

    if not selecao_id:
        return redirect('selecionar_selecao')
    
    candidatos_da_selecao = Candidato.objects.filter(selecao__id=selecao_id).order_by('id')
    total_candidatos = candidatos_da_selecao.count()

    if total_candidatos == 0:
        return render(request, 'Registration/sem_candidatos_na_selecao.html', {'selecao_nome': selecao_nome})

    # Obter candidato atual
    if candidato_id:
        try:
            candidato = candidatos_da_selecao.get(id=candidato_id)
        except Candidato.DoesNotExist:
            return redirect('analisar_candidato')
    else:
        candidato = candidatos_da_selecao.first()
        if not candidato:
            return render(request, 'Registration/sem_candidatos_na_selecao.html', {'selecao_nome': selecao_nome})

    # Busca documentos do candidato usando o relacionamento do Django (mais robusto)
    documentos_candidato = candidato.documentos.all()

    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            
            # Redirecionar para próximo candidato ou finalizar (usando o nome de URL unificado)
            next_candidato = candidatos_da_selecao.filter(id__gt=candidato.id).order_by('id').first()
            if next_candidato:
                return redirect('analisar_candidato', candidato_id=next_candidato.id)
            return redirect('finalizar_analise')
    else:
        form = CandidatoForm(instance=candidato)

    # Calcular índice e candidato anterior
    ids_ordenados = list(candidatos_da_selecao.values_list('id', flat=True))
    try:
        indice_atual = ids_ordenados.index(candidato.id) + 1
    except ValueError:
        indice_atual = 0

    anterior_candidato_id = None
    if indice_atual > 1:
        anterior_candidato = candidatos_da_selecao.filter(id__lt=candidato.id).order_by('-id').first()
        if anterior_candidato:
            anterior_candidato_id = anterior_candidato.id

    context = {
        'form': form,
        'indice_atual': indice_atual,
        'total_candidatos': total_candidatos,
        'anterior_candidato_id': anterior_candidato_id,
        'data_formatada': _("Hoje é %(date)s") % {'date': timezone.now().strftime('%d de %B de %Y')},
        'selecao_nome': selecao_nome,
        'documentos_candidato': documentos_candidato,
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
                return redirect('painel_avaliador')
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
            return redirect('painel_avaliador')
    else:
        form = SelecaoForm()
    
    return render(request, 'Registration/selecionar_selecao.html', {'form': form})

@login_required
def upload_documento(request, candidato_id):
    candidato = get_object_or_404(Candidato, pk=candidato_id)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.candidato = candidato
            documento.save()
            
            # Adiciona mensagem de sucesso
            messages.success(request, f"Documento '{documento.get_tipo_display()}' enviado com sucesso!")
            return redirect('analisar_candidato', candidato_id=candidato.id)
    else:
        form = DocumentoForm()
    
    # Busca documentos já enviados
    documentos = candidato.documentos.all()
    
    context = {
        'candidato': candidato,
        'form': form,
        'documentos': documentos,
    }
    return render(request, 'upload_documento.html', context)

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
def painel_avaliador(request):
    usuario = request.user
    selecao_id = request.session.get('selecao_id')

    # Verifica se uma seleção foi escolhida. Se não, redireciona.
    if not selecao_id:
        messages.info(request, "Por favor, selecione um processo seletivo para continuar.")
        return redirect('selecionar_selecao')

    # Busca a seleção de forma segura, tratando o caso de não existir.
    try:
        selecao = Selecao.objects.get(id=selecao_id)
    except Selecao.DoesNotExist:
        # O ID na sessão é inválido. Limpa a sessão e redireciona.
        del request.session['selecao_id']
        if 'selecao_nome' in request.session:
            del request.session['selecao_nome']
        messages.error(request, "A seleção escolhida não foi encontrada. Por favor, selecione novamente.")
        return redirect('selecionar_selecao')

    candidatos = Candidato.objects.filter(selecao=selecao).order_by('id')
    todos_avaliados = all(c.analisado for c in candidatos) if candidatos.exists() else False
    return render(request, 'Registration/painel_avaliador.html', {
        'usuario': usuario,
        'selecao': selecao,
        'candidatos': candidatos,
        'todos_avaliados': todos_avaliados,
    })