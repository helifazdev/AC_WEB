# analise_curricular/admin.py (Versão corrigida para usar o CandidatoAdminForm)

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Selecao, Candidato, DocumentoCandidato, FormQuestion
from .forms import DynamicCandidatoForm, CandidatoAdminForm # Importe o novo formulário para o Admin

# Admin para o modelo Selecao
@admin.register(Selecao)
class SelecaoAdmin(ImportExportModelAdmin):
    list_display = ('nome', 'ativa', 'descricao')
    list_filter = ('ativa',)
    search_fields = ('nome',)

# Admin para o modelo FormQuestion
@admin.register(FormQuestion)
class FormQuestionAdmin(ImportExportModelAdmin):
    list_display = ('question_text', 'selecao', 'question_type', 'order', 'required')
    list_filter = ('selecao', 'question_type', 'required')
    search_fields = ('question_text',)
    list_editable = ('order', 'required')
    raw_id_fields = ('selecao',)

# Admin para o modelo Candidato
@admin.register(Candidato)
class CandidatoAdmin(ImportExportModelAdmin):
    # Use o NOVO CandidatoAdminForm para o formulário de adição/alteração no Admin
    form = CandidatoAdminForm 

    list_display = (
        'nome', 'inscricao', 'cargo', 'selecao', 
        'analisado', 'pontuacao', 'data_analisado', 'avaliador_analise',
        'declarou_deficiencia', 'tipo_deficiencia_display'
    )
    list_filter = (
        'selecao', 'analisado', 'avaliador_analise', 
        'declarou_deficiencia',
    )
    search_fields = ('nome', 'inscricao', 'cargo')
    readonly_fields = ('data_importacao', 'data_analisado', 'avaliador_analise', 'pontuacao')
    
    fieldsets = (
        (None, {
            'fields': ('selecao', 'nome', 'inscricao', 'cargo')
        }),
        ('Informações de Deficiência', {
            'fields': ('declarou_deficiencia', 'tipo_deficiencia'),
            'classes': ('collapse',)
        }),
        ('Status de Análise', {
            'fields': ('analisado', 'pontuacao', 'data_analisado', 'avaliador_analise'),
        }),
        # Exibe o JSONField 'respostas_dinamicas' no admin se você o incluiu no CandidatoAdminForm
        ('Respostas Dinâmicas do Formulário', {
             'fields': ('respostas_dinamicas',),
             'classes': ('collapse',),
         }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('selecao', 'avaliador_analise')

    def tipo_deficiencia_display(self, obj):
        return obj.tipo_deficiencia if obj.declarou_deficiencia == 'Sim' else 'N/A'
    tipo_deficiencia_display.short_description = 'Tipo de Deficiência'


# Admin para o modelo DocumentoCandidato
@admin.register(DocumentoCandidato)
class DocumentoCandidatoAdmin(ImportExportModelAdmin):
    list_display = ('candidato', 'tipo', 'arquivo', 'data_upload', 'observacoes')
    list_filter = ('tipo', 'candidato__selecao')
    search_fields = ('candidato__nome', 'observacoes')
    raw_id_fields = ('candidato',)