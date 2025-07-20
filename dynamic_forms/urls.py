from django.urls import path
from . import views

app_name = 'dynamic_forms'

urlpatterns = [
    path('form/<str:form_slug>/', views.dynamic_form, name='dynamic_form'),
]