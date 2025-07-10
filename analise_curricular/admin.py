# analise_curricular/admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Candidato, Selecao # <--- Certifique-se que Candidato e Selecao estão importados

# 1. Classe Resource para o modelo Candidato
# Esta classe define como os dados do Candidato serão importados/exportados.
class CandidatoResource(resources.ModelResource):
    # O campo 'selecao' é um ForeignKey e vamos mapeá-lo para uma coluna 'selecao' no CSV.
    # O ForeignKeyWidget usará o 'nome' da Selecao para encontrar o objeto correto no banco de dados.
    selecao = fields.Field(
        column_name='selecao',  # Nome da coluna no seu arquivo CSV para a Seleção
        attribute='selecao',    # Atributo correspondente no modelo Candidato
        widget=ForeignKeyWidget(Selecao, 'nome') # Mapeia para o campo 'nome' do modelo Selecao
    )

    class Meta:
        model = Candidato
        # Campos que serão incluídos na importação e exportação.
        # 'selecao' deve estar listado aqui, pois será lido/escrito do CSV.
        fields = (
            'id', 'nome', 'inscricao', 'cargo',
            'requisito', 'avaliacao', 'justificativa', 'observacao',
            'pontuacao', 'analisado', 'data_analise', 'selecao',
        )
        # Ordem das colunas na exportação.
        export_order = (
            'id', 'nome', 'inscricao', 'cargo',
            'requisito', 'avaliacao', 'justificativa', 'observacao',
            'pontuacao', 'analisado', 'data_analise', 'selecao',
        )
        # Configurações de importação:
        # 'inscricao' é usado para identificar registros existentes.
        # Se um candidato com a mesma 'inscricao' já existe, o registro será ATUALIZADO.
        import_id_fields = ['inscricao'] # <--- Essencial para evitar 'UNIQUE constraint failed'
        skip_unchanged = True # Pula linhas que não tiveram mudanças
        report_skipped = True # Reporta as linhas que foram puladas (útil na prévia da importação)

    # O método 'before_import_row' NÃO é mais necessário aqui
    # porque a atribuição da seleção virá diretamente de uma coluna no CSV,
    # e o 'ForeignKeyWidget' junto com 'import_id_fields' faz o trabalho.

# 2. Classe Admin para o modelo Candidato
# Herda de ImportExportModelAdmin para habilitar os botões de Importar/Exportar.
@admin.register(Candidato) # Registra o modelo Candidato com esta classe Admin
class CandidatoAdmin(ImportExportModelAdmin):
    # Campos a serem exibidos na lista de Candidatos no Admin
    list_display = (
        'nome',
        'inscricao',
        'cargo',
        'requisito',
        'avaliacao',
        'pontuacao',
        'analisado',
        'data_analise',
        'selecao' # Adicionado 'selecao' para visualização
    )
    # Campos para filtrar a lista de Candidatos no Admin
    list_filter = (
        'cargo',
        'requisito',
        'avaliacao',
        'analisado',
        'selecao' # Adicionado 'selecao' aos filtros
    )
    # Campos para a barra de pesquisa no Admin
    search_fields = (
        'nome',
        'inscricao',
        'cargo'
    )
    # Ordem padrão para a lista de Candidatos
    ordering = (
        'nome',
        'cargo'
    )
    # Campos que não podem ser editados manualmente no formulário do Admin
    readonly_fields = ('pontuacao', 'data_analise')

    # Organização dos campos no formulário de edição do Candidato no Admin
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'inscricao', 'cargo', 'selecao'), # 'selecao' adicionado aqui
        }),
        ('Análise Curricular', {
            'fields': ('requisito', 'avaliacao', 'justificativa', 'observacao'),
        }),
        ('Resultados', {
            'fields': ('pontuacao', 'analisado', 'data_analise'),
        }),
    )

    # Associa a CandidatoResource a esta classe Admin, habilitando import/export.
    resource_class = CandidatoResource

# 3. Classe Admin para o modelo Selecao
# Registra o modelo Selecao no Admin.
class SelecaoAdmin(admin.ModelAdmin):
    # Campos a serem exibidos na lista de Seleções no Admin
    list_display = ('nome', 'ativa', 'descricao')
    # Campos para filtrar a lista de Seleções
    list_filter = ('ativa',)
    # Campos para a barra de pesquisa de Seleções
    search_fields = ('nome', 'descricao')

admin.site.register(Selecao, SelecaoAdmin) # <--- Registro explícito para Selecao