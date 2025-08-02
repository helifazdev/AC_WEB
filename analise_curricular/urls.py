# analise_curricular/urls.py

from django.urls import path
from . import views # Importa todas as views do seu arquivo views.py

urlpatterns = [
    # URLs de Páginas Principais
    path('', views.tela_entrada, name='tela_entrada'), # Esta URL é para a raiz do APP
    path('finalizar/', views.finalizar_analise, name='finalizar_analise'),
    path('inscricao_finalizada/', views.inscricao_finalizada, name='inscricao_finalizada'),

    # URLs de Autenticação Customizadas
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.avaliador_signup, name='signup'),

    # URLs de Seleção e Painel do Avaliador
    path('selecionar-selecao/', views.selecionar_selecao, name='selecionar_selecao'),
    path('painel/<int:selecao_id>/', views.painel_avaliador, name='painel_avaliador'),

    # URLs de Análise de Candidato e Documentos
    path('analise/<int:candidato_id>/', views.analisar_candidato, name='analisar_candidato'),
    path('candidato/<int:candidato_id>/documentos/', views.listar_documentos, name='listar_documentos'),
]