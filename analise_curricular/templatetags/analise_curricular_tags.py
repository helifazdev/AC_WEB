# analise_curricular/templatetags/analise_curricular_tags.py

from django import template

register = template.Library()

@register.filter
def get_dynamic_field_by_id(form, question_id):
    """
    Retorna o campo dinâmico de um formulário com base no ID da pergunta.
    """
    field_name = f'question_{question_id}'
    return form[field_name]