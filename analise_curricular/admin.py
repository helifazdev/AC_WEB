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

# analise_curricular/admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Candidato # Importe seu modelo Candidato

# 1. Crie uma classe Resource para o seu modelo
class CandidatoResource(resources.ModelResource):
    class Meta:
        model = Candidato
        # Campos que você quer exportar. Se omitir 'fields', todos serão exportados.
        fields = (
            'id', 'nome', 'inscricao', 'cargo',
            'requisito', 'avaliacao', 'justificativa', 'observacao',
            # Adicione outros campos do seu modelo Candidato aqui, se existirem
            # Por exemplo: 'data_criacao', 'ultima_atualizacao' etc.
        )
        # Campos que você quer excluir da exportação (alternativa a 'fields')
        # exclude = ('id',) # Exemplo: excluir o campo 'id'
        
        # Define se os campos com ForeingKey serão exportados com o ID ou o valor legível
        # Para campos ForeignKey, use 'widgets' para personalizar a exportação se precisar de mais do que o ID
        
        # 'export_order' pode ser usado para definir a ordem das colunas no arquivo exportado
        export_order = (
            'id', 'nome', 'inscricao', 'cargo',
            'requisito', 'avaliacao', 'justificativa', 'observacao',
        )

class CandidatoAdmin(ImportExportModelAdmin):
    list_display = ('nome', 'inscricao', 'cargo', 'requisito', 'avaliacao') # Campos exibidos na lista do admin
    search_fields = ('nome', 'inscricao', 'cargo') # Campos para pesquisa no admin
    list_filter = ('requisito', 'avaliacao', 'cargo') # Filtros na barra lateral
    resource_class = CandidatoResource # Associa o Resource que criamos acima
    # ... você pode manter outras configurações de seu Admin normal aqui