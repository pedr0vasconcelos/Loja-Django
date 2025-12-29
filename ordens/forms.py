from django import forms
from .models import OrdemServico, Equipamento, ItemOS

class OrdemServicoForm(forms.ModelForm):
    # Marcamos como required=False para evitar erros no POST de 'Nova OS'
    status = forms.ChoiceField(choices=OrdemServico.STATUS, required=False)
    valor_total = forms.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = OrdemServico
        fields = ['cliente', 'equipamento', 'defeito_relatado', 'status', 'valor_total', 'laudo_tecnico']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'hx-get': '/carregar-equipamentos/',
                'hx-target': '#id_equipamento',
                'hx-trigger': 'change'
            }),
            'equipamento': forms.Select(attrs={'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'defeito_relatado': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'laudo_tecnico': forms.Textarea(attrs={'rows': 4, 'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'status': forms.Select(attrs={'class': 'w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            # No forms.py, dentro de Meta widgets:
            'valor_total': forms.NumberInput(attrs={'class': 'w-full bg-gray-100 rounded-lg border-gray-300 shadow-sm', 'step': '0.01', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Lógica para Nova OS: Esconde status e valor inicial
        if not self.instance.pk:
            self.fields['status'].initial = 'aberto'
            self.fields['valor_total'].initial = 0.00
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['valor_total'].widget = forms.HiddenInput()
        else:
            # Na Edição: Deixa o valor_total como apenas leitura pois os Signals cuidam do cálculo
            self.fields['valor_total'].widget.attrs['readonly'] = True

        # Lógica de filtragem de equipamentos (Mantenha igual)
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

# NOVA CLASSE PARA ADICIONAR PEÇAS E SERVIÇOS
class ItemOSForm(forms.ModelForm):
    class Meta:
        model = ItemOS
        fields = ['descricao', 'quantidade', 'valor_unitario']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 text-sm focus:ring-blue-500', 
                'placeholder': 'Ex: Troca de Conector'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 text-sm focus:ring-blue-500',
                'min': '1'
            }),
            'valor_unitario': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 text-sm focus:ring-blue-500',
                'step': '0.01',
                'placeholder': 'Valor Unitário R$'
            }),
        }