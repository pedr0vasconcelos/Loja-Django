from django import forms
from .models import OrdemServico, Equipamento

class OrdemServicoForm(forms.ModelForm):
    # Usamos o nome exato da constante no seu models.py: STATUS
    status = forms.ChoiceField(choices=OrdemServico.STATUS, required=False)
    valor_total = forms.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = OrdemServico
        fields = ['cliente', 'equipamento', 'defeito_relatado', 'status', 'valor_total']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'hx-get': '/carregar-equipamentos/',
                'hx-target': '#id_equipamento',
                'hx-trigger': 'change'
            }),
            'equipamento': forms.Select(attrs={'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'defeito_relatado': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'status': forms.Select(attrs={'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'valor_total': forms.NumberInput(attrs={'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.instance.pk:
            # Define valores iniciais automáticos
            self.fields['status'].initial = 'aberto'
            self.fields['valor_total'].initial = 0.00
            # Esconde os campos na criação (eles são obrigatórios no banco mas automáticos aqui)
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['valor_total'].widget = forms.HiddenInput()

        # Lógica de filtragem de equipamentos baseada no seu related_name='equipamentos'
        if 'cliente' in self.data:
            try:
                cliente_id = int(self.data.get('cliente'))
                self.fields['equipamento'].queryset = Equipamento.objects.filter(cliente_id=cliente_id).order_by('marca')
            except (ValueError, TypeError):
                self.fields['equipamento'].queryset = Equipamento.objects.none()
        elif self.instance.pk:
            self.fields['equipamento'].queryset = self.instance.cliente.equipamentos.all().order_by('marca')
        else:
            self.fields['equipamento'].queryset = Equipamento.objects.none()