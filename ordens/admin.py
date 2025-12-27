from django.contrib import admin
from .models import Cliente, Equipamento, OrdemServico, ItemOS

class ItemOSInline(admin.TabularInline):
    model = ItemOS
    extra = 1  # Define quantas linhas vazias aparecem por padrão

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'equipamento', 'status', 'data_entrada')
    list_filter = ('status', 'data_entrada')
    inlines = [ItemOSInline]  # Aqui acontece a "mágica"
    
    # Campo de busca para facilitar encontrar a OS
    search_fields = ('cliente__nome', 'equipamento__marca', 'id')

admin.site.register(Cliente)
admin.site.register(Equipamento)