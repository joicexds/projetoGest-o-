from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm, FuncionarioForm, GastoForm, EmpresaForm, AdiantamentoForm, RegistroTrabalhoForm, ReceitaForm
from .models import Funcionario, Gasto, CategoriaGasto, Empresa, Adiantamento, RegistroTrabalho, Receita
from django.db.models import Sum
from django.contrib.auth import login

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Fazer o login automático do usuário recém-cadastrado
            login(request, user)
            return redirect('dashboard')
    else:
        form = CadastroForm()
    
    return render(request, 'registration/cadastro.html', {'form': form})

@login_required
def dashboard(request):
    from datetime import date
    mes_atual = date.today().month
    ano_atual = date.today().year

    # Receitas
    total_receitas = Receita.objects.filter(data_recebimento__month=mes_atual, data_recebimento__year=ano_atual).aggregate(total=Sum('valor'))['total'] or 0.00

    # Gastos
    total_gastos = Gasto.objects.filter(data_gasto__month=mes_atual, data_gasto__year=ano_atual).aggregate(total=Sum('valor'))['total'] or 0.00
    
    # Salários Base dos funcionários ativos
    total_salarios = Funcionario.objects.filter(ativo=True).aggregate(total=Sum('salario'))['total'] or 0.00

    # Margem / Balanço
    balanco = float(total_receitas) - (float(total_gastos) + float(total_salarios))
    lucro = True if balanco >= 0 else False

    total_funcionarios = Funcionario.objects.filter(ativo=True).count()
    
    # Últimas movimentações
    ultimos_gastos = Gasto.objects.order_by('-data_gasto', '-id')[:5]
    ultimas_receitas = Receita.objects.order_by('-data_recebimento', '-id')[:5]

    context = {
        'total_gastos': total_gastos,
        'total_funcionarios': total_funcionarios,
        'total_receitas': total_receitas,
        'balanco': balanco,
        'lucro': lucro,
        'ultimos_gastos': ultimos_gastos,
        'ultimas_receitas': ultimas_receitas,
        'mes_atual': mes_atual,
    }
    return render(request, 'dashboard.html', context)


# ==========================================
# FUNCIONÁRIOS
# ==========================================

@login_required
def funcionario_list(request):
    funcionarios = Funcionario.objects.all().order_by('nome')
    return render(request, 'funcionarios_list.html', {'funcionarios': funcionarios})

@login_required
def funcionario_form(request, id=None):
    funcionario = get_object_or_404(Funcionario, id=id) if id else None
    
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            return redirect('funcionario_list')
    else:
        form = FuncionarioForm(instance=funcionario)
        
    return render(request, 'funcionario_form.html', {'form': form, 'funcionario': funcionario})

@login_required
def funcionario_detail(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    
    # Processa o formulário de Registro de Trabalho
    if request.method == 'POST':
        form_registro = RegistroTrabalhoForm(request.POST)
        if form_registro.is_valid():
            registro = form_registro.save(commit=False)
            registro.funcionario = funcionario
            # Se não definiu valor da diária, puxa o padrão do funcionário (se for diarista)
            if registro.valor_diaria_aplicada == 0 and funcionario.tipo_pagamento == 'DIARISTA':
                registro.valor_diaria_aplicada = funcionario.valor_diaria
            registro.save()
            return redirect('funcionario_detail', id=funcionario.id)
    else:
        form_registro = RegistroTrabalhoForm()

    registros = funcionario.registros_trabalho.all().order_by('-data')
    adiantamentos = funcionario.adiantamentos.all().order_by('-data')
    
    # Calculos Rápidos para Resumo
    dias_trabalhados = registros.filter(tipo='PRESENCA').count()
    dias_falta = registros.filter(tipo='FALTA').count()
    dias_atestado = registros.filter(tipo='ATESTADO').count()
    
    total_adiantado_pendente = adiantamentos.filter(status='PENDENTE').aggregate(total=Sum('valor'))['total'] or 0.00
    
    total_diarias = 0
    total_ganhos = 0
    
    if funcionario.tipo_pagamento == 'DIARISTA':
        total_diarias = registros.filter(tipo='PRESENCA').aggregate(total=Sum('valor_diaria_aplicada'))['total'] or 0.00
        total_ganhos = total_diarias
    else:
        total_ganhos = funcionario.salario
        
    salario_liquido = float(total_ganhos) - float(total_adiantado_pendente)

    context = {
        'funcionario': funcionario,
        'registros': registros,
        'adiantamentos': adiantamentos,
        'form_registro': form_registro,
        'dias_trabalhados': dias_trabalhados,
        'dias_falta': dias_falta,
        'dias_atestado': dias_atestado,
        'total_adiantado_pendente': total_adiantado_pendente,
        'total_diarias': total_diarias,
        'salario_liquido': salario_liquido,
        'total_ganhos': total_ganhos,
    }
    return render(request, 'funcionario_detail.html', context)

@login_required
def registro_trabalho_delete(request, id):
    registro = get_object_or_404(RegistroTrabalho, id=id)
    func_id = registro.funcionario.id
    if request.method == 'POST':
        registro.delete()
    return redirect('funcionario_detail', id=func_id)

@login_required
def funcionario_holerite(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    registros = funcionario.registros_trabalho.all().order_by('-data')
    adiantamentos = funcionario.adiantamentos.filter(status='PENDENTE').order_by('-data')
    
    # Cálculos idênticos aos do Detail
    total_adiantado_pendente = adiantamentos.aggregate(total=Sum('valor'))['total'] or 0.00
    
    total_diarias = 0
    total_ganhos = 0
    if funcionario.tipo_pagamento == 'DIARISTA':
        total_diarias = registros.filter(tipo='PRESENCA').aggregate(total=Sum('valor_diaria_aplicada'))['total'] or 0.00
        total_ganhos = total_diarias
    else:
        total_ganhos = funcionario.salario
        
    salario_liquido = float(total_ganhos) - float(total_adiantado_pendente)
    
    context = {
        'funcionario': funcionario,
        'registros': registros,
        'adiantamentos': adiantamentos,
        'total_ganhos': total_ganhos,
        'total_adiantado_pendente': total_adiantado_pendente,
        'salario_liquido': salario_liquido,
    }
    return render(request, 'funcionario_holerite.html', context)

@login_required
def funcionario_delete(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    if request.method == 'POST':
        funcionario.delete()
        return redirect('funcionario_list')
    return render(request, 'funcionario_confirm_delete.html', {'funcionario': funcionario})

# ==========================================
# GASTOS E DESPESAS
# ==========================================

@login_required
def gasto_list(request):
    gastos = Gasto.objects.all().order_by('-data_gasto', '-id')
    return render(request, 'gastos_list.html', {'gastos': gastos})

@login_required
def gasto_form(request, id=None):
    gasto = get_object_or_404(Gasto, id=id) if id else None
    
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            return redirect('gasto_list')
    else:
        form = GastoForm(instance=gasto)
        
    return render(request, 'gasto_form.html', {'form': form, 'gasto': gasto})

@login_required
def gasto_delete(request, id):
    gasto = get_object_or_404(Gasto, id=id)
    if request.method == 'POST':
        gasto.delete()
        return redirect('gasto_list')
    return render(request, 'gasto_confirm_delete.html', {'gasto': gasto})

# ==========================================
# EMPRESAS
# ==========================================

@login_required
def empresa_list(request):
    empresas = Empresa.objects.all().order_by('razao_social')
    return render(request, 'empresas_list.html', {'empresas': empresas})

@login_required
def empresa_form(request, id=None):
    empresa = get_object_or_404(Empresa, id=id) if id else None
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('empresa_list')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'empresa_form.html', {'form': form, 'empresa': empresa})

@login_required
def empresa_delete(request, id):
    empresa = get_object_or_404(Empresa, id=id)
    if request.method == 'POST':
        empresa.delete()
        return redirect('empresa_list')
    return render(request, 'empresa_confirm_delete.html', {'empresa': empresa})

# ==========================================
# ADIANTAMENTOS
# ==========================================

@login_required
def adiantamento_list(request):
    adiantamentos = Adiantamento.objects.all().order_by('-data', '-id')
    return render(request, 'adiantamentos_list.html', {'adiantamentos': adiantamentos})

@login_required
def adiantamento_form(request, id=None):
    adiantamento = get_object_or_404(Adiantamento, id=id) if id else None
    if request.method == 'POST':
        form = AdiantamentoForm(request.POST, instance=adiantamento)
        if form.is_valid():
            form.save()
            return redirect('adiantamento_list')
    else:
        form = AdiantamentoForm(instance=adiantamento)
    return render(request, 'adiantamento_form.html', {'form': form, 'adiantamento': adiantamento})

@login_required
def adiantamento_delete(request, id):
    adiantamento = get_object_or_404(Adiantamento, id=id)
    if request.method == 'POST':
        adiantamento.delete()
        return redirect('adiantamento_list')
    return render(request, 'adiantamento_confirm_delete.html', {'adiantamento': adiantamento})

# --- RECEITAS ---

@login_required
def receita_list(request):
    receitas = Receita.objects.all().order_by('-data_recebimento')
    return render(request, 'receitas_list.html', {'receitas': receitas})

@login_required
def receita_form(request, id=None):
    if id:
        receita = get_object_or_404(Receita, id=id)
    else:
        receita = None

    if request.method == 'POST':
        form = ReceitaForm(request.POST, instance=receita)
        if form.is_valid():
            form.save()
            return redirect('receita_list')
    else:
        form = ReceitaForm(instance=receita)
    
    return render(request, 'receita_form.html', {'form': form, 'receita': receita})

@login_required
def receita_delete(request, id):
    receita = get_object_or_404(Receita, id=id)
    if request.method == 'POST':
        receita.delete()
        return redirect('receita_list')
    return render(request, 'receita_confirm_delete.html', {'receita': receita})

# ==========================================
# RELATÓRIOS
# ==========================================

@login_required
def relatorios(request):
    total_gastos = Gasto.objects.aggregate(total=Sum('valor'))['total'] or 0.00
    total_adiantamentos = Adiantamento.objects.filter(status='PENDENTE').aggregate(total=Sum('valor'))['total'] or 0.00
    total_salarios = Funcionario.objects.filter(ativo=True).aggregate(total=Sum('salario'))['total'] or 0.00
    
    gastos_por_categoria = Gasto.objects.values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')

    context = {
        'total_gastos': total_gastos,
        'total_adiantamentos': total_adiantamentos,
        'total_salarios': total_salarios,
        'gastos_por_categoria': gastos_por_categoria
    }
    return render(request, 'relatorios.html', context)
