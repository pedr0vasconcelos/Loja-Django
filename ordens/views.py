from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import OrdemServico, Equipamento, Cliente
from .forms import OrdemServicoForm
from django.db.models import Q
from django.views.decorators.http import require_POST

def dashboard(request):
    # Captura o valor digitado na busca
    busca = request.GET.get('busca')
    
    # Métricas para os cards
    total_abertas = OrdemServico.objects.filter(status='aberto').count()
    em_analise = OrdemServico.objects.filter(status='analise').count()
    prontas = OrdemServico.objects.filter(status='pronto').count()
    
    # Lógica de busca
    if busca:
        ultimas_os = OrdemServico.objects.filter(
            Q(id__icontains=busca) | Q(cliente__nome__icontains=busca)
        ).select_related('cliente', 'equipamento').order_by('-data_entrada')
    else:
        ultimas_os = OrdemServico.objects.select_related('cliente', 'equipamento').order_by('-data_entrada')[:5]
    
    return render(request, 'ordens/dashboard.html', {
        'total_abertas': total_abertas,
        'em_analise': em_analise,
        'prontas': prontas,
        'ultimas_os': ultimas_os,
        'busca': busca
    })

def nova_os(request):
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST)
        
        # Aceita o equipamento que o HTMX acabou de criar e injetar no POST
        if 'equipamento' in request.POST and request.POST.get('equipamento'):
            form.fields['equipamento'].queryset = Equipamento.objects.filter(id=request.POST.get('equipamento'))
            
        if form.is_valid():
            os_instancia = form.save(commit=False)
            # Garante que os campos ocultos tenham valor antes do save final
            if not os_instancia.status:
                os_instancia.status = 'aberto'
            if os_instancia.valor_total is None:
                os_instancia.valor_total = 0.00
            os_instancia.save()
            return redirect('dashboard')
    else:
        form = OrdemServicoForm()
    
    return render(request, 'ordens/form_os.html', {'form': form, 'editando': False})

def editar_os(request, os_id):
    os_instancia = get_object_or_404(OrdemServico, id=os_id)
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST, instance=os_instancia)
        
        if 'equipamento' in request.POST:
            equip_id = request.POST.get('equipamento')
            form.fields['equipamento'].queryset = Equipamento.objects.filter(id=equip_id)
            
        if form.is_valid():
            form.save() # Na edição, os campos já estarão na tela e preenchidos
            return redirect('dashboard')
    else:
        form = OrdemServicoForm(instance=os_instancia)
    
    return render(request, 'ordens/form_os.html', {
        'form': form, 
        'os': os_instancia, 
        'editando': True
    })

def gerar_pdf_os(request, os_id): # Alterado de pk para os_id
    # Busca a OS pelo ID que vem da URL
    os = get_object_or_404(OrdemServico, id=os_id)
    
    template_path = 'ordens/pdf_os.html'
    context = {'os': os}
    
    # Cria a resposta do tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="os_{os.id}.pdf"'
    
    # Renderiza o template HTML
    template = get_template(template_path)
    html = template.render(context)
    
    # Converte HTML para PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    return response

def carregar_equipamentos(request):
    cliente_id = request.GET.get('cliente')
    if cliente_id:
        equipamentos = Equipamento.objects.filter(cliente_id=cliente_id).order_by('marca')
    else:
        equipamentos = Equipamento.objects.none()
    return render(request, 'ordens/dropdown_equipamentos.html', {'equipamentos': equipamentos})

@require_POST
def criar_cliente_equipamento_rapido(request):
    nome = request.POST.get('nome_novo_cliente')
    cpf = request.POST.get('cpf_novo_cliente')
    telefone = request.POST.get('telefone_novo_cliente')
    marca = request.POST.get('marca')
    modelo = request.POST.get('modelo')
    serie = request.POST.get('serie')

    if nome and marca and modelo and serie:
        # 1. Cria o Cliente
        cliente = Cliente.objects.create(nome=nome, cpf_cnpj=cpf, telefone=telefone)
        
        # 2. Cria o Equipamento
        Equipamento.objects.create(
            cliente=cliente,
            marca=marca,
            modelo=modelo,
            num_serie=serie
        )
        
        # 3. Resposta com o cliente selecionado
        response = HttpResponse(f'<option value="{cliente.id}" selected>{cliente.nome}</option>')
        
        # 4. O Gatilho 'clienteCriado' DEVE ser enviado exatamente assim:
        response['HX-Trigger'] = 'clienteCriado'
        return response
        
    return HttpResponse("Erro: Preencha todos os campos.", status=400)