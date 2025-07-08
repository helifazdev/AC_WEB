# analise_curricular/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.tela_entrada, name='tela_entrada'), # URL para a tela de entrada
    path('analise/', views.analisar_candidato, name='analisar_candidato'), # URL sem ID para o primeiro candidato
    path('analise/<int:candidato_id>/', views.analisar_candidato, name='analisar_candidato_com_id'), # URL com ID para navegação
    path('finalizar/', views.finalizar_analise, name='finalizar_analise'), # URL para a tela de finalização
]