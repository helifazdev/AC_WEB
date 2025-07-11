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


from .forms import CandidatoForm, AvaliadorSignUpForm, SelecaoForm
from .models import Candidato, Selecao

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

    # Buscar documentos do candidato
    documentos_candidato = []
    documentos_dir = os.path.join(settings.MEDIA_ROOT, 'candidatos_documentos')
    
    if os.path.exists(documentos_dir):
        for filename in os.listdir(documentos_dir):
            if (candidato.inscricao in filename and 
                os.path.isfile(os.path.join(documentos_dir, filename))):
                document_url = settings.MEDIA_URL + 'candidatos_documentos/' + filename
                documentos_candidato.append({
                    'nome': filename,
                    'url': document_url,
                })

    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            
            # Redirecionar para próximo candidato ou finalizar
            next_candidato = candidatos_da_selecao.filter(id__gt=candidato.id).order_by('id').first()
            if next_candidato:
                return redirect('analisar_candidato_com_id', candidato_id=next_candidato.id)
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
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                form.add_error(None, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

def avaliador_signup(request):
    if request.method == 'POST':
        form = AvaliadorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = AvaliadorSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def selecionar_selecao(request):
    if request.method == 'POST':
        form = SelecaoForm(request.POST)
        if form.is_valid():
            selecao_escolhida = form.cleaned_data['selecao_disponivel']
            request.session['selecao_id'] = selecao_escolhida.id
            request.session['selecao_nome'] = selecao_escolhida.nome
            return redirect('analisar_candidato')
    else:
        form = SelecaoForm()
    
    return render(request, 'Registration/selecionar_selecao.html', {'form': form})