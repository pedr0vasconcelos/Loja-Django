from django.db import models
from django.db.models import Sum, F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=14, unique=True, verbose_name="CPF/CNPJ")
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    endereco = models.TextField(blank=True, verbose_name="Endereço")
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Equipamento(models.Model):
    TIPOS = [
        ('NB', 'Notebook'),
        ('DT', 'Desktop'),
        ('MN', 'Monitor'),
        ('OU', 'Outros'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='equipamentos')
    tipo = models.CharField(max_length=2, choices=TIPOS)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    num_serie = models.CharField(max_length=100, blank=True, verbose_name="Número de Série")

    def __str__(self):
        return f"{self.get_tipo_display()} {self.marca} {self.modelo}"


class OrdemServico(models.Model):
    STATUS = [
        ('aberto', 'Aberto'),
        ('analise', 'Em Análise'),
        ('orcamento', 'Aguardando Orçamento'),
        ('autorizado', 'Autorizado'),
        ('pronto', 'Pronto para Retirada'),
        ('entregue', 'Entregue/Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    defeito_relatado = models.TextField(verbose_name="Defeito Relatado")
    laudo_tecnico = models.TextField(blank=True, verbose_name="Laudo Técnico")
    status = models.CharField(max_length=20, choices=STATUS, default='aberto')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_entrada = models.DateTimeField(auto_now_add=True)
    data_saida = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"

    def __str__(self):
        return f"OS {self.id} - {self.cliente.nome}"


class ItemOS(models.Model):
    os = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name='itens')
    descricao = models.CharField(max_length=200, verbose_name="Descrição do Item/Serviço")
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.descricao

    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario


# --- SIGNALS PARA CÁLCULO AUTOMÁTICO ---

@receiver([post_save, post_delete], sender=ItemOS)
def atualizar_total_os(sender, instance, **kwargs):
    """
    Sempre que um item for salvo ou deletado, recalcula o valor_total da OS.
    """
    os = instance.os
    # Agrega a soma de (quantidade * valor_unitario) de todos os itens da OS
    resultado = os.itens.aggregate(
        total_calculado=Sum(F('quantidade') * F('valor_unitario'))
    )
    
    os.valor_total = resultado['total_calculado'] or 0.00
    os.save()