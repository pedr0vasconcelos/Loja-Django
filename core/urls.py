from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Rota para o painel administrativo
    path('admin/', admin.site.urls),
    
    # Rota principal que puxa as URLs da pasta 'ordens'
    path('', include('ordens.urls')),
]