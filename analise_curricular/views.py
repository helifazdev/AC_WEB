# analise_curricular/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Candidato
from .forms import CandidatoForm
from django.contrib import messages
from datetime import datetime

def tela_entrada(request):
    return render(request, 'analise_curricular/tela_entrada.html')

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