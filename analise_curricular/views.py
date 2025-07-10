# analise_curricular/views.py
import os # Importe 'os' para manipulação de caminhos de arquivo
from django.conf import settings # Importe settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate # Importações para autenticação
from django.contrib.auth.forms import AuthenticationForm # Importar formulário de login
from django.contrib.auth.decorators import login_required # Decorador para proteger views
from django.db.models import Max # Importado para o indice_atual e total_candidatos
from .models import Candidato
from .forms import CandidatoForm
from django.contrib import messages
from datetime import datetime
from django.conf import settings

from .forms import CandidatoForm, AvaliadorSignUpForm, SelecaoForm # Importe seus formulários
from .models import Candidato, Selecao # Importe seu modelo Candidato

def tela_entrada(request):
    return render(request, 'analise_curricular/tela_entrada.html')

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

    candidato = None
    if candidato_id:
        try:
            candidato = candidatos_da_selecao.get(id=candidato_id)
        except Candidato.DoesNotExist:
            return redirect('analisar_candidato')
    
    if not candidato:
        candidato = candidatos_da_selecao.first()
        if not candidato: # Redundância caso a primeira busca falhe por algum motivo
            return render(request, 'Registration/sem_candidatos_na_selecao.html', {'selecao_nome': selecao_nome})

    # Lógica para encontrar documentos do candidato
    documentos_candidato = []
    # Diretório onde os documentos estão armazenados
    documentos_dir = os.path.join(settings.MEDIA_ROOT, 'candidatos_documentos')
    
    if os.path.exists(documentos_dir):
        # Percorre todos os arquivos na pasta de documentos
        for filename in os.listdir(documentos_dir):
            # Verifica se o número de inscrição do candidato está no nome do arquivo
            # E se o arquivo não é um diretório e termina em .pdf (ou outros formatos que você queira)
            if candidato.inscricao in filename and os.path.isfile(os.path.join(documentos_dir, filename)):
                # Cria a URL completa para o documento
                document_url = settings.MEDIA_URL + 'candidatos_documentos/' + filename
                documentos_candidato.append({
                    'nome': filename,
                    'url': document_url,
                    # Você pode adicionar mais metadados aqui se quiser, ex: tipo de documento
                })
    
    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            # Antes de salvar, se a avaliação for 'Nao possui', garantir que justificativa não esteja vazia
            # (Já tratamos isso no clean() do formulário, mas é bom ter em mente)
            
            form.save() # Salva as alterações no candidato

            # Lógica para o próximo candidato
            next_candidato = candidatos_da_selecao.filter(id__gt=candidato.id).order_by('id').first()
            if next_candidato:
                return redirect('analisar_candidato_com_id', candidato_id=next_candidato.id)
            else:
                return redirect('finalizar_analise')
        else:
            # Formulário inválido, renderiza com erros. Os documentos ainda estarão no contexto.
            pass
    else:
        form = CandidatoForm(instance=candidato)

    indice_atual = 0
    if candidato:
        ids_ordenados = list(candidatos_da_selecao.values_list('id', flat=True))
        try:
            indice_atual = ids_ordenados.index(candidato.id) + 1
        except ValueError:
            indice_atual = 0

    anterior_candidato_id = None
    if candidato and indice_atual > 1:
        anterior_candidato = candidatos_da_selecao.filter(id__lt=candidato.id).order_by('-id').first()
        if anterior_candidato:
            anterior_candidato_id = anterior_candidato.id

    context = {
        'form': form,
        'indice_atual': indice_atual,
        'total_candidatos': total_candidatos,
        'anterior_candidato_id': anterior_candidato_id,
        'data_hoje': '09 de Julho de 2025', # Atualizei o ano para o ano atual
        'selecao_nome': selecao_nome,
        'documentos_candidato': documentos_candidato, # <--- Passa os documentos para o template
    }
    return render(request, 'Registration/formulario.html', context)

@login_required
def analisar_candidato(request, candidato_id=None):
    candidatos_ordenados = Candidato.objects.all().order_by('nome', 'cargo')
    total_candidatos = candidatos_ordenados.count()

    if total_candidatos == 0:
        messages.info(request, "Não há candidatos para analisar.")
        return redirect('tela_entrada')

    candidato_atual = None
    indice_atual = 0

    if candidato_id:
        candidato_atual = get_object_or_404(Candidato, id=candidato_id)
        for i, c in enumerate(candidatos_ordenados):
            if c.id == candidato_atual.id:
                indice_atual = i
                break
    else:
        candidato_atual = candidatos_ordenados.filter(analisado=False).first()
        if not candidato_atual:
            candidato_atual = candidatos_ordenados.first()
            if candidato_atual:
                messages.info(request, "Todos os candidatos foram analisados. Você está revisando o primeiro.")
        
        if candidato_atual:
             for i, c in enumerate(candidatos_ordenados):
                if c.id == candidato_atual.id:
                    indice_atual = i
                    break
        else:
            messages.info(request, "Não há candidatos para analisar.")
            return redirect('tela_entrada')

    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES, instance=candidato_atual) # Adicionado request.FILES
        if form.is_valid():
            candidato = form.save(commit=False)
            
            # --- Lógica de Aviso para Requisito "Nao" (movida para o JavaScript) ---
            # O alerta será tratado no frontend (formulario.html) com JavaScript.
            
            candidato.analisado = True # Sempre marca como analisado ao submeter o formulário
            candidato.save()
            messages.success(request, f"Informações do candidato {candidato.nome} salvas com sucesso!")

            # Lógica para ir para o próximo candidato
            if indice_atual < total_candidatos - 1:
                proximo_candidato = candidatos_ordenados[indice_atual + 1]
                return redirect('analisar_candidato_com_id', candidato_id=proximo_candidato.id)
            else:
                messages.info(request, "Todos os candidatos foram analisados.")
                return redirect('finalizar_analise')
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = CandidatoForm(instance=candidato_atual)

    proximo_candidato_id = None
    anterior_candidato_id = None

    if indice_atual < total_candidatos - 1:
        proximo_candidato_id = candidatos_ordenados[indice_atual + 1].id
    if indice_atual > 0:
        anterior_candidato_id = candidatos_ordenados[indice_atual - 1].id

    context = {
        'form': form,
        'candidato': candidato_atual,
        'indice_atual': indice_atual + 1,
        'total_candidatos': total_candidatos,
        'data_hoje': datetime.now().strftime("%d/%m/%Y"),
        'proximo_candidato_id': proximo_candidato_id,
        'anterior_candidato_id': anterior_candidato_id,
    }
    return render(request, 'analise_curricular/formulario.html', context)

def finalizar_analise(request):
    messages.success(request, "Análise finalizada. Todas as informações foram salvas.")
    return render(request, 'analise_curricular/finalizar_analise.html')

def tela_entrada(request):
    return render(request, 'tela_entrada.html')

@login_required # Protege esta view: só acessível se o usuário estiver logado
def analisar_candidato(request, candidato_id=None):
    selecao_id = request.session.get('selecao_id')
    selecao_nome = request.session.get('selecao_nome', 'Nenhuma Seleção Selecionada')

    if not selecao_id:
        return redirect('selecionar_selecao')
    
    candidatos_da_selecao = Candidato.objects.filter(selecao__id=selecao_id).order_by('id')

    total_candidatos = candidatos_da_selecao.count()

    if total_candidatos == 0:
        messages.info(request, f"Não há candidatos na seleção '{selecao_nome}' para analisar.")
        # ALTERE AQUI: Use o caminho completo para o template
        return render(request, 'Registration/sem_candidatos_na_selecao.html', {'selecao_nome': selecao_nome})

    total_candidatos = Candidato.objects.count()
    candidato = None

    if candidato_id:
        try:
            candidato = Candidato.objects.get(id=candidato_id)
        except Candidato.DoesNotExist:
            return redirect('analisar_candidato') # Redireciona para o primeiro se o ID não existir

    if not candidato:
        # Pega o primeiro candidato não analisado ou o primeiro de todos
        # Você pode precisar de uma lógica mais sofisticada para "próximo candidato"
        candidato = Candidato.objects.first() 
        if not candidato:
            # Caso não haja nenhum candidato cadastrado ainda
            return render(request, 'sem_candidatos.html') # Crie um template para isso
    
    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            # Lógica para o próximo candidato
            # Por exemplo, encontrar o próximo ID
            next_candidato = Candidato.objects.filter(id__gt=candidato.id).order_by('id').first()
            if next_candidato:
                return redirect('analisar_candidato_com_id', candidato_id=next_candidato.id)
            else:
                return redirect('finalizar_analise')
        else:
            # Se o formulário não for válido, renderiza com os erros
            pass # O template já mostrará os erros
    else:
        form = CandidatoForm(instance=candidato)

    indice_atual = list(Candidato.objects.values_list('id', flat=True)).index(candidato.id) + 1 if candidato else 0

    anterior_candidato_id = None
    if candidato and indice_atual > 1:
        # Lógica para o candidato anterior
        anterior_candidato = Candidato.objects.filter(id__lt=candidato.id).order_by('-id').first()
        if anterior_candidato:
            anterior_candidato_id = anterior_candidato.id

    context = {
        'form': form,
        'indice_atual': indice_atual,
        'total_candidatos': total_candidatos,
        'anterior_candidato_id': anterior_candidato_id,
        'data_hoje': '08 de Julho de 2024' # Pode ser obtido com datetime.now().strftime(...)
    }
    return render(request, 'Registration/formulario.html', context)

@login_required
def finalizar_analise(request):
    # Aqui você pode adicionar lógica para mostrar um resumo, etc.
    return render(request, 'finalizar_analise.html', {'data_hoje': '08 de Julho de 2024'})


# NOVO: View de Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redireciona para a URL definida em settings.LOGIN_REDIRECT_URL
                return redirect(LOGIN_REDIRECT_URL) 
            else:
                # Caso as credenciais sejam inválidas
                form.add_error(None, "Usuário ou senha inválidos.") # Adiciona um erro geral
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# NOVO: View de Logout
def user_logout(request):
    logout(request)
    # Redireciona para a URL definida em settings.LOGOUT_REDIRECT_URL
    return redirect(LOGOUT_REDIRECT_URL) 

# NOVO: View de Cadastro de Avaliador
def avaliador_signup(request):
    if request.method == 'POST':
        form = AvaliadorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Faz login do usuário automaticamente após o cadastro
            # Redireciona para a URL definida em settings.LOGIN_REDIRECT_URL
            return redirect(LOGIN_REDIRECT_URL)
    else:
        form = AvaliadorSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# NOVO: View de Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Agora use settings.LOGIN_REDIRECT_URL
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                form.add_error(None, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# NOVO: View de Logout
def user_logout(request):
    logout(request)
    # Agora use settings.LOGOUT_REDIRECT_URL
    return redirect(settings.LOGOUT_REDIRECT_URL)

# NOVO: View de Cadastro de Avaliador
def avaliador_signup(request):
    if request.method == 'POST':
        form = AvaliadorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Agora use settings.LOGIN_REDIRECT_URL
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = AvaliadorSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# NOVO: View para selecionar a seleção
@login_required # Apenas avaliadores logados podem acessar esta tela
def selecionar_selecao(request):
    if request.method == 'POST':
        form = SelecaoForm(request.POST)
        if form.is_valid():
            selecao_escolhida = form.cleaned_data['selecao_disponivel']
            # Aqui você deve armazenar a seleção escolhida na sessão do usuário
            # ou em algum outro lugar para que as próximas views saibam qual seleção usar.
            request.session['selecao_id'] = selecao_escolhida.id
            request.session['selecao_nome'] = selecao_escolhida.nome
            
            # Redireciona para a tela de análise de candidatos
            # Você precisará ajustar a sua view analisar_candidato para usar essa 'selecao_id'
            return redirect('analisar_candidato') 
    else:
        form = SelecaoForm()
    
    context = {
        'form': form,
    }
    return render(request, 'Registration/selecionar_selecao.html', context)

