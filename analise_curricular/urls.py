# analise_curricular/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ... (suas outras URLs existentes) ...
    path('analise/<int:candidato_id>/', views.analisar_candidato, name='analisar_candidato'),
    # As linhas abaixo foram REMOVIDAS
    # path('upload_documento/<int:candidato_id>/', views.upload_documento, name='upload_documento'),
    # path('documento/<int:documento_id>/deletar/', views.deletar_documento, name='deletar_documento'),
    
    # Manter a URL listar_documentos se desejar uma página separada para listar os documentos
    path('candidato/<int:candidato_id>/documentos/', views.listar_documentos, name='listar_documentos'),

    path('inscricao_finalizada/', views.inscricao_finalizada, name='inscricao_finalizada'),
    path('tela_entrada/', views.tela_entrada, name='tela_entrada'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('selecionar_selecao/', views.selecionar_selecao, name='selecionar_selecao'),
    path('avaliador_signup/', views.avaliador_signup, name='avaliador_signup'),
    path('painel_avaliador/<int:selecao_id>/', views.painel_avaliador, name='painel_avaliador'),
    path('finalizar_analise/', views.finalizar_analise, name='finalizar_analise'),
]