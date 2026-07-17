from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm, FuncionarioForm, GastoForm, AdiantamentoForm, RegistroTrabalhoForm, ReceitaForm, UsuarioUpdateForm, UserProfileForm, AtestadoForm, ApontamentoForm, FazendaClienteForm
from .models import Funcionario, Gasto, CategoriaGasto, Adiantamento, RegistroTrabalho, Receita, UserProfile, Atestado, Apontamento, FazendaCliente
from django.db.models import Sum
from django.contrib.auth import login
from django.contrib import messages

# ==========================================
# PERFIL DO USUÁRIO
# ==========================================

@login_required
def perfil_usuario(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = UsuarioUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    return render(request, 'perfil.html', {'form': form, 'profile_form': profile_form})

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Fazer o login automático do usuário recém-cadastrado
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
    else:
        form = CadastroForm()
    
    return render(request, 'registration/cadastro.html', {'form': form})

@login_required
def dashboard(request):
    from datetime import datetime, date
    mes_ano = request.GET.get('mes_ano')
    if mes_ano:
        try:
            dt = datetime.strptime(mes_ano, '%Y-%m')
            mes_atual = dt.month
            ano_atual = dt.year
        except ValueError:
            mes_atual = date.today().month
            ano_atual = date.today().year
    else:
        mes_atual = date.today().month
        ano_atual = date.today().year
    
    mes_ano_str = f"{ano_atual}-{mes_atual:02d}"

    # Receitas
    total_receitas = Receita.objects.filter(usuario=request.user, data_recebimento__month=mes_atual, data_recebimento__year=ano_atual).aggregate(total=Sum('valor'))['total'] or 0.00

    # Gastos
    total_gastos = Gasto.objects.filter(usuario=request.user, data_gasto__month=mes_atual, data_gasto__year=ano_atual).aggregate(total=Sum('valor'))['total'] or 0.00
    
    # Salários Base dos funcionários ativos
    total_salarios = Funcionario.objects.filter(usuario=request.user, ativo=True).aggregate(total=Sum('salario'))['total'] or 0.00

    # Margem / Balanço
    balanco = float(total_receitas) - (float(total_gastos) + float(total_salarios))
    lucro = True if balanco >= 0 else False

    total_funcionarios = Funcionario.objects.filter(usuario=request.user, ativo=True).count()
    
    # Últimas movimentações
    ultimos_gastos = Gasto.objects.filter(usuario=request.user).order_by('-data_gasto', '-id')[:5]
    ultimas_receitas = Receita.objects.filter(usuario=request.user).order_by('-data_recebimento', '-id')[:5]

    context = {
        'total_gastos': total_gastos,
        'total_funcionarios': total_funcionarios,
        'total_receitas': total_receitas,
        'balanco': balanco,
        'lucro': lucro,
        'ultimos_gastos': ultimos_gastos,
        'ultimas_receitas': ultimas_receitas,
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'mes_ano_str': mes_ano_str,
    }
    return render(request, 'dashboard.html', context)


# ==========================================
# FUNCIONÁRIOS
# ==========================================

@login_required
def funcionario_list(request):
    q = request.GET.get('q', '')
    funcionarios = Funcionario.objects.filter(usuario=request.user)
    if q:
        funcionarios = funcionarios.filter(nome__icontains=q)
    funcionarios = funcionarios.order_by('nome')
    return render(request, 'funcionarios_list.html', {'funcionarios': funcionarios, 'q': q})

@login_required
def funcionario_form(request, id=None):
    funcionario = get_object_or_404(Funcionario, id=id, usuario=request.user) if id else None
    
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()
            return redirect('funcionario_list')
    else:
        form = FuncionarioForm(instance=funcionario)
        
    return render(request, 'funcionario_form.html', {'form': form, 'funcionario': funcionario})

@login_required
def funcionario_detail(request, id):
    funcionario = get_object_or_404(Funcionario, id=id, usuario=request.user)
    
    if request.method == 'POST':
        if 'submit_adiantamento' in request.POST:
            form_adiantamento = AdiantamentoForm(request.POST, user=request.user)
            if form_adiantamento.is_valid():
                adiantamento = form_adiantamento.save(commit=False)
                adiantamento.funcionario = funcionario
                adiantamento.usuario = request.user
                adiantamento.save()
                return redirect('funcionario_detail', id=funcionario.id)
    else:
        form_adiantamento = AdiantamentoForm(initial={'funcionario': funcionario.id}, user=request.user)

    atestados = funcionario.atestados_medicos.all().order_by('-data_inicio')
    apontamentos = funcionario.apontamentos.all().order_by('-data_inicio')
    adiantamentos = funcionario.adiantamentos.all().order_by('-data')
    
    # Calculos Rápidos para Resumo (Todo o histórico)
    dias_trabalhados = sum(ap.dias_trabalhados for ap in apontamentos)
    dias_falta = sum(ap.dias_falta for ap in apontamentos)
    
    # Adicionando dias de atestado do histórico
    dias_atestado = 0
    for at in atestados:
        delta = at.data_fim - at.data_inicio
        dias_atestado += delta.days + 1
    
    total_adiantado_pendente = adiantamentos.filter(status='PENDENTE').aggregate(total=Sum('valor'))['total'] or 0.00
    
    total_ganhos = sum(ap.calculo_ganhos for ap in apontamentos)
    total_descontos_faltas = sum(ap.calculo_desconto_faltas for ap in apontamentos)
    
    salario_liquido = float(total_ganhos) - float(total_adiantado_pendente) - float(total_descontos_faltas)

    context = {
        'funcionario': funcionario,
        'atestados': atestados,
        'apontamentos': apontamentos,
        'adiantamentos': adiantamentos,
        'form_adiantamento': form_adiantamento,
        'dias_trabalhados': dias_trabalhados,
        'dias_falta': dias_falta,
        'dias_atestado': dias_atestado,
        'total_adiantado_pendente': total_adiantado_pendente,
        'salario_liquido': salario_liquido,
        'total_ganhos': total_ganhos,
    }
    return render(request, 'funcionario_detail.html', context)

@login_required
def registro_trabalho_delete(request, id):
    registro = get_object_or_404(RegistroTrabalho, id=id, usuario=request.user)
    func_id = registro.funcionario.id
    if request.method == 'POST':
        registro.delete()
    return redirect('funcionario_detail', id=func_id)

@login_required
def funcionario_holerite(request, id):
    funcionario = get_object_or_404(Funcionario, id=id, usuario=request.user)
    
    # Holerite geralmente é do último fechamento, ou de todos.
    # Vamos pegar o último apontamento para exibir em destaque, ou somar todos dependendo da lógica do cliente.
    # O cliente disse "imprimir relatorio de cada funcionario individual apareça todas essas informações".
    # Vamos passar todos os apontamentos e atestados
    apontamentos = funcionario.apontamentos.all().order_by('-data_inicio')
    atestados = funcionario.atestados_medicos.all().order_by('-data_inicio')
    adiantamentos = funcionario.adiantamentos.filter(status='PENDENTE').order_by('-data')
    
    total_adiantado_pendente = adiantamentos.aggregate(total=Sum('valor'))['total'] or 0.00
    
    total_ganhos = sum(ap.calculo_ganhos for ap in apontamentos)
    total_descontos_faltas = sum(ap.calculo_desconto_faltas for ap in apontamentos)
        
    salario_liquido = float(total_ganhos) - float(total_adiantado_pendente) - float(total_descontos_faltas)
    
    context = {
        'funcionario': funcionario,
        'apontamentos': apontamentos,
        'atestados': atestados,
        'adiantamentos': adiantamentos,
        'total_ganhos': total_ganhos,
        'total_adiantado_pendente': total_adiantado_pendente,
        'total_descontos_faltas': total_descontos_faltas,
        'salario_liquido': salario_liquido,
    }
    return render(request, 'funcionario_holerite.html', context)

@login_required
def funcionario_delete(request, id):
    funcionario = get_object_or_404(Funcionario, id=id, usuario=request.user)
    if request.method == 'POST':
        funcionario.delete()
        return redirect('funcionario_list')
    return render(request, 'funcionario_confirm_delete.html', {'funcionario': funcionario})

# ==========================================
# GASTOS E DESPESAS
# ==========================================

@login_required
def gasto_list(request):
    gastos = Gasto.objects.filter(usuario=request.user).order_by('-data_gasto', '-id')
    return render(request, 'gastos_list.html', {'gastos': gastos})

@login_required
def gasto_form(request, id=None):
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user) if id else None
    
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()
            return redirect('gasto_list')
    else:
        form = GastoForm(instance=gasto, user=request.user)
        
    return render(request, 'gasto_form.html', {'form': form, 'gasto': gasto})

@login_required
def gasto_delete(request, id):
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user)
    if request.method == 'POST':
        gasto.delete()
        return redirect('gasto_list')
    return render(request, 'gasto_confirm_delete.html', {'gasto': gasto})

# ==========================================
# ADIANTAMENTOS
# ==========================================

@login_required
def adiantamento_list(request):
    adiantamentos = Adiantamento.objects.filter(usuario=request.user).order_by('-data', '-id')
    return render(request, 'adiantamentos_list.html', {'adiantamentos': adiantamentos})

@login_required
def adiantamento_form(request, id=None):
    adiantamento = get_object_or_404(Adiantamento, id=id, usuario=request.user) if id else None
    if request.method == 'POST':
        form = AdiantamentoForm(request.POST, instance=adiantamento, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()
            # Tenta vincular retroativamente a um fechamento existente que cubra a data ou seja posterior
            apontamento = obj.funcionario.apontamentos.filter(data_fim__gte=obj.data).order_by('data_fim').first()
            if apontamento:
                obj.apontamento_vinculado = apontamento
                obj.status = 'DESCONTADO'
                obj.save()
            return redirect('adiantamento_list')
    else:
        form = AdiantamentoForm(instance=adiantamento, user=request.user)
    return render(request, 'adiantamento_form.html', {'form': form, 'adiantamento': adiantamento})

@login_required
def adiantamento_delete(request, id):
    adiantamento = get_object_or_404(Adiantamento, id=id, usuario=request.user)
    if request.method == 'POST':
        adiantamento.delete()
        return redirect('adiantamento_list')
    return render(request, 'adiantamento_confirm_delete.html', {'adiantamento': adiantamento})

# --- RECEITAS ---

@login_required
def receita_list(request):
    receitas = Receita.objects.filter(usuario=request.user).order_by('-data_recebimento')
    return render(request, 'receitas_list.html', {'receitas': receitas})

@login_required
def receita_form(request, id=None):
    if id:
        receita = get_object_or_404(Receita, id=id, usuario=request.user)
    else:
        receita = None

    if request.method == 'POST':
        form = ReceitaForm(request.POST, instance=receita, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()
            return redirect('receita_list')
    else:
        form = ReceitaForm(instance=receita, user=request.user)
    
    return render(request, 'receita_form.html', {'form': form, 'receita': receita})

@login_required
def receita_delete(request, id):
    receita = get_object_or_404(Receita, id=id, usuario=request.user)
    if request.method == 'POST':
        receita.delete()
        return redirect('receita_list')
    return render(request, 'receita_confirm_delete.html', {'receita': receita})

# ==========================================
# RELATÓRIOS
# ==========================================

@login_required
def relatorios(request):
    from datetime import datetime, date, timedelta
    
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')
    
    hoje = date.today()
    
    if data_inicio_str and data_fim_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            data_inicio = hoje.replace(day=1)
            data_fim = (hoje.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    else:
        # Padrão: mês atual inteiro
        data_inicio = hoje.replace(day=1)
        data_fim = (hoje.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    total_gastos = Gasto.objects.filter(usuario=request.user, data_gasto__range=[data_inicio, data_fim]).aggregate(total=Sum('valor'))['total'] or 0.00
    
    gastos_por_categoria = Gasto.objects.filter(usuario=request.user, data_gasto__range=[data_inicio, data_fim]).values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')

    funcionarios = Funcionario.objects.filter(usuario=request.user, ativo=True)
    dados_funcionarios = []
    
    for f in funcionarios:
        # Pega apontamentos que cruzam com o período do relatório
        apontamentos = f.apontamentos.filter(data_inicio__gte=data_inicio, data_fim__lte=data_fim)
        
        # Para atestados, mesma lógica
        atestados_qs = f.atestados_medicos.filter(data_inicio__gte=data_inicio, data_fim__lte=data_fim)
        
        # Vales do período
        vales_qs_periodo = f.adiantamentos.filter(data__range=[data_inicio, data_fim])
        
        if apontamentos.exists():
            total_ganhos = float(sum(ap.calculo_ganhos for ap in apontamentos))
            dias_falta = sum(ap.dias_falta for ap in apontamentos)
            dias_trabalhados = sum(ap.dias_trabalhados for ap in apontamentos)
            desconto_faltas = float(sum(ap.calculo_desconto_faltas for ap in apontamentos))
            
            # Vales descontados nos fechamentos do período (mesmo que o vale seja antigo)
            vales_fechamento = float(sum(ap.calculo_adiantamentos for ap in apontamentos))
            # Vales pendentes (incluindo de meses anteriores) que ainda não foram descontados e são <= data_fim
            vales_pendentes = float(sum(v.valor for v in f.adiantamentos.filter(status='PENDENTE', data__lte=data_fim)))
            
            desconto_vales = vales_fechamento + vales_pendentes
            
            # Ajustar queryset para exibição no relatório: vales do período + vales descontados nos apontamentos
            from django.db.models import Q
            vales_descontados_ids = []
            for ap in apontamentos:
                vales_descontados_ids.extend(ap.vales_descontados.values_list('id', flat=True))
                
            vales_qs = f.adiantamentos.filter(
                Q(data__range=[data_inicio, data_fim]) | Q(id__in=vales_descontados_ids)
            ).distinct().order_by('-data')
        else:
            # Simulação dinâmica caso não haja fechamento salvo
            registros_periodo = f.registros_trabalho.filter(data__range=[data_inicio, data_fim])
            dias_falta = registros_periodo.filter(tipo='FALTA').count()
            dias_trabalhados = registros_periodo.filter(tipo='PRESENCA').count()
            
            if f.tipo_pagamento == 'DIARISTA':
                total_ganhos = float(dias_trabalhados) * float(f.valor_diaria or 0)
                desconto_faltas = 0.0
            elif f.tipo_pagamento == 'MENSALISTA':
                total_ganhos = float(f.salario or 0)
                valor_dia = total_ganhos / 30.0
                desconto_faltas = float(dias_falta) * valor_dia
            else:
                total_ganhos = 0.0
                desconto_faltas = 0.0
                
            vales_pendentes = float(sum(v.valor for v in f.adiantamentos.filter(status='PENDENTE', data__lte=data_fim)))
            vales_qs = f.adiantamentos.filter(
                Q(data__range=[data_inicio, data_fim]) | Q(id__in=f.adiantamentos.filter(status='PENDENTE', data__lte=data_fim).values_list('id', flat=True))
            ).distinct().order_by('-data')
            desconto_vales = float(sum(v.valor for v in vales_qs.filter(status='PENDENTE')))
        
        dias_atestado = 0
        for at in atestados_qs:
            delta = at.data_fim - at.data_inicio
            dias_atestado += delta.days + 1
            
        liquido = total_ganhos - desconto_faltas - desconto_vales
        
        dados_funcionarios.append({
            'funcionario': f,
            'ganhos': total_ganhos,
            'desconto_faltas': desconto_faltas,
            'desconto_vales': desconto_vales,
            'faltas': dias_falta,
            'atestados': dias_atestado,
            'liquido': liquido,
            'dias_trabalhados': dias_trabalhados if f.tipo_pagamento == 'DIARISTA' else None,
            'atestados_list': atestados_qs,
            'apontamentos_list': apontamentos,
            'vales_list': vales_qs
        })

    total_ganhos_geral = sum(d['ganhos'] for d in dados_funcionarios)
    total_descontos_geral = sum(d['desconto_faltas'] + d['desconto_vales'] for d in dados_funcionarios)
    total_liquido_geral = sum(d['liquido'] for d in dados_funcionarios)

    context = {
        'total_gastos': total_gastos,
        'total_ganhos_geral': total_ganhos_geral,
        'total_descontos_geral': total_descontos_geral,
        'total_liquido_geral': total_liquido_geral,
        'gastos_por_categoria': gastos_por_categoria,
        'dados_funcionarios': dados_funcionarios,
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'data_inicio_fmt': data_inicio.strftime('%d/%m/%Y'),
        'data_fim_fmt': data_fim.strftime('%d/%m/%Y'),
    }
    return render(request, 'relatorios.html', context)


# ==========================================
# AÇÕES DE RH (CONSOLIDADA)
# ==========================================

@login_required
def acoes_rh(request):
    atestados = Atestado.objects.filter(usuario=request.user).order_by('-data_inicio')
    apontamentos = Apontamento.objects.filter(usuario=request.user).order_by('-data_inicio')
    active_tab = request.GET.get('tab', 'fechamentos')
    
    context = {
        'atestados': atestados,
        'apontamentos': apontamentos,
        'active_tab': active_tab,
    }
    return render(request, 'acoes_rh.html', context)

# ==========================================
# ATESTADOS (REDIRECIONAMENTO & AÇÕES)
# ==========================================

@login_required
def atestado_list(request):
    return redirect('/acoes-rh/?tab=atestados')

@login_required
def atestado_form_global(request):
    if request.method == 'POST':
        form = AtestadoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            atestado = form.save(commit=False)
            atestado.usuario = request.user
            atestado.save()
            return redirect('/acoes-rh/?tab=atestados')
    else:
        form = AtestadoForm(user=request.user)
        
    return render(request, 'atestado_form.html', {'form': form, 'is_global': True})

@login_required
def atestado_form(request, func_id):
    funcionario = get_object_or_404(Funcionario, id=func_id, usuario=request.user)
    
    if request.method == 'POST':
        form = AtestadoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            atestado = form.save(commit=False)
            atestado.funcionario = funcionario
            atestado.usuario = request.user
            atestado.save()
            return redirect('funcionario_detail', id=funcionario.id)
    else:
        form = AtestadoForm(initial={'funcionario': funcionario.id}, user=request.user)
        
    return render(request, 'atestado_form.html', {'form': form, 'funcionario': funcionario, 'is_global': False})

@login_required
def atestado_delete(request, id):
    atestado = get_object_or_404(Atestado, id=id, usuario=request.user)
    func_id = atestado.funcionario.id
    if request.method == 'POST':
        atestado.delete()
        referer = request.META.get('HTTP_REFERER', '')
        if 'acoes-rh' in referer or 'atestado' in referer:
            return redirect('/acoes-rh/?tab=atestados')
        return redirect('funcionario_detail', id=func_id)
    return render(request, 'atestado_confirm_delete.html', {'atestado': atestado})

# ==========================================
# APONTAMENTOS / FECHAMENTO (REDIRECIONAMENTO & AÇÕES)
# ==========================================

@login_required
def apontamento_list(request):
    return redirect('/acoes-rh/?tab=fechamentos')

@login_required
def apontamento_form_global(request):
    if request.method == 'POST':
        form = ApontamentoForm(request.POST, user=request.user)
        if form.is_valid():
            apontamento = form.save(commit=False)
            apontamento.usuario = request.user
            apontamento.save()
            # Descontar os adiantamentos pendentes (até o fim do período)
            Adiantamento.objects.filter(
                funcionario=apontamento.funcionario,
                usuario=request.user,
                status='PENDENTE',
                data__lte=apontamento.data_fim
            ).update(status='DESCONTADO', apontamento_vinculado=apontamento)
            return redirect('/acoes-rh/?tab=fechamentos')
    else:
        form = ApontamentoForm(user=request.user)
        
    funcionarios_dados = {
        f.id: {
            'tipo_pagamento': f.tipo_pagamento,
            'valor_diaria': float(f.valor_diaria or 0),
            'salario': float(f.salario or 0),
            'adiantamentos': [
                {
                    'id': adv.id,
                    'valor': float(adv.valor),
                    'data': adv.data.isoformat(),
                    'observacao': adv.observacao or ''
                }
                for adv in f.adiantamentos.filter(status='PENDENTE')
            ],
            'registros': [
                {
                    'data': reg.data.isoformat(),
                    'tipo': reg.tipo
                }
                for reg in f.registros_trabalho.all()
            ]
        } for f in Funcionario.objects.filter(usuario=request.user, ativo=True)
    }
        
    return render(request, 'apontamento_form.html', {'form': form, 'is_global': True, 'funcionarios_dados': funcionarios_dados})

@login_required
def apontamento_form(request, func_id):
    funcionario = get_object_or_404(Funcionario, id=func_id, usuario=request.user)
    
    if request.method == 'POST':
        form = ApontamentoForm(request.POST, user=request.user)
        if form.is_valid():
            apontamento = form.save(commit=False)
            apontamento.funcionario = funcionario
            apontamento.usuario = request.user
            apontamento.save()
            # Descontar os adiantamentos pendentes (até o fim do período)
            Adiantamento.objects.filter(
                funcionario=funcionario,
                usuario=request.user,
                status='PENDENTE',
                data__lte=apontamento.data_fim
            ).update(status='DESCONTADO', apontamento_vinculado=apontamento)
            return redirect('funcionario_detail', id=funcionario.id)
    else:
        form = ApontamentoForm(initial={'funcionario': funcionario.id}, user=request.user)
        
    funcionarios_dados = {
        funcionario.id: {
            'tipo_pagamento': funcionario.tipo_pagamento,
            'valor_diaria': float(funcionario.valor_diaria or 0),
            'salario': float(funcionario.salario or 0),
            'adiantamentos': [
                {
                    'id': adv.id,
                    'valor': float(adv.valor),
                    'data': adv.data.isoformat(),
                    'observacao': adv.observacao or ''
                }
                for adv in funcionario.adiantamentos.filter(status='PENDENTE')
            ],
            'registros': [
                {
                    'data': reg.data.isoformat(),
                    'tipo': reg.tipo
                }
                for reg in funcionario.registros_trabalho.all()
            ]
        }
    }
        
    return render(request, 'apontamento_form.html', {'form': form, 'funcionario': funcionario, 'is_global': False, 'funcionarios_dados': funcionarios_dados})

@login_required
def apontamento_delete(request, id):
    apontamento = get_object_or_404(Apontamento, id=id, usuario=request.user)
    func_id = apontamento.funcionario.id
    if request.method == 'POST':
        # Restaurar adiantamentos descontados por este apontamento
        apontamento.vales_descontados.update(status='PENDENTE', apontamento_vinculado=None)
        apontamento.delete()
        referer = request.META.get('HTTP_REFERER', '')
        if 'acoes-rh' in referer or 'apontamento' in referer:
            return redirect('/acoes-rh/?tab=fechamentos')
        return redirect('funcionario_detail', id=func_id)
    return render(request, 'apontamento_confirm_delete.html', {'apontamento': apontamento})

# ==========================================
# FAZENDAS / CLIENTES
# ==========================================

@login_required
def fazenda_list(request):
    fazendas = FazendaCliente.objects.filter(usuario=request.user).order_by('nome')
    return render(request, 'fazendas_list.html', {'fazendas': fazendas})

@login_required
def fazenda_form(request, id=None):
    fazenda = get_object_or_404(FazendaCliente, id=id, usuario=request.user) if id else None
    
    if request.method == 'POST':
        form = FazendaClienteForm(request.POST, instance=fazenda)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()
            return redirect('fazenda_list')
    else:
        form = FazendaClienteForm(instance=fazenda)
        
    return render(request, 'fazenda_form.html', {'form': form, 'fazenda': fazenda})

@login_required
def fazenda_delete(request, id):
    fazenda = get_object_or_404(FazendaCliente, id=id, usuario=request.user)
    if request.method == 'POST':
        fazenda.delete()
        return redirect('fazenda_list')
    return render(request, 'fazenda_confirm_delete.html', {'fazenda': fazenda})
