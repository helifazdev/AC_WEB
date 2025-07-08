from django.contrib import admin

# Register your models here.

# analise_curricular/admin.py

from django.contrib import admin
from .models import Candidato

# Register your models here.

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'inscricao',
        'cargo',
        'requisito',
        'avaliacao',
        'pontuacao',
        'analisado',
        'data_analise'
    )
    list_filter = (
        'cargo',
        'requisito',
        'avaliacao',
        'analisado'
    )
    search_fields = (
        'nome',
        'inscricao',
        'cargo'
    )
    ordering = (
        'nome',
        'cargo'
    )
    readonly_fields = ('pontuacao', 'data_analise') # Esses campos não devem ser editáveis manualmente no admin

    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'inscricao', 'cargo'),
        }),
        ('Análise Curricular', {
            'fields': ('requisito', 'avaliacao', 'justificativa', 'observacao'),
        }),
        ('Resultados', {
            'fields': ('pontuacao', 'analisado', 'data_analise'),
        }),
    )