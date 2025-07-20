from django.shortcuts import render, get_object_or_404
from .models import FormSelection

def dynamic_form(request, form_slug):
    form_selection = get_object_or_404(FormSelection, name__iexact=form_slug)
    questions = form_selection.questions.all().order_by('order')
    
    if request.method == 'POST':
        # Processar as respostas do formulário
        # Aqui você pode implementar a lógica condicional
        pass
    
    context = {
        'form_selection': form_selection,
        'questions': questions,
    }
    return render(request, 'dynamic_forms/form.html', context)