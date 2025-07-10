"""
URL configuration for IAUPECurricularWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # Importe 'include'
from django.conf import settings # Para arquivos estáticos em desenvolvimento
from django.conf.urls.static import static # Para arquivos estáticos em desenvolvimento

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('analise_curricular.urls')), # Inclui as URLs do seu aplicativo aqui
]

# IAUPECurricularWeb/IAUPECurricularWeb/urls.py

# Configuração para servir arquivos estáticos em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Configuração para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)