# analise_curricular/urls.py

from django.urls import path
from . import views
from .views import upload_documento, deletar_documento

from django.contrib.auth import views as auth_views # Importar as views de autenticação padrão do Django

urlpatterns = [
    path('', views.tela_entrada, name='tela_entrada'), # URL para a tela de entrada
    path('analise/', views.analisar_candidato, name='analisar_candidato'), # URL sem ID para o primeiro candidato
    path('analise/<int:candidato_id>/', views.analisar_candidato, name='analisar_candidato_com_id'), # URL com ID para navegação
    path('finalizar/', views.finalizar_analise, name='finalizar_analise'), # URL para a tela de finalização

     # NOVO: URL para a tela de seleção de avaliação
    path('selecionar-selecao/', views.selecionar_selecao, name='selecionar_selecao'),


     # NOVAS URLs para Autenticação
    path('login/', views.user_login, name='login'), # Usaremos nossa view customizada
    path('logout/', views.user_logout, name='logout'), # Usaremos nossa view customizada
    path('signup/', views.avaliador_signup, name='signup'), # Nossa view de cadastro

    path('candidato/<int:candidato_id>/documentos/', upload_documento, name='upload_documento'),
    path('documento/<int:documento_id>/deletar/', deletar_documento, name='deletar_documento'),
    path('inscricao_finalizada/', views.inscricao_finalizada, name='inscricao_finalizada')
] 
