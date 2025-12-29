from django.urls import path
from . import views

urlpatterns = [    
    path('', views.dashboard, name='dashboard'),    
    path('nova/', views.nova_os, name='nova_os'),
    path('os/<int:os_id>/pdf/', views.gerar_pdf_os, name='gerar_pdf_os'),
    path('carregar-equipamentos/', views.carregar_equipamentos, name='carregar_equipamentos'),   
    path('os/<int:os_id>/editar/', views.editar_os, name='editar_os'),
    path('cadastro-rapido-total/', views.criar_cliente_equipamento_rapido, name='criar_cliente_equipamento_rapido'),
    path('os/<int:os_id>/adicionar-item/', views.adicionar_item, name='adicionar_item'),
]