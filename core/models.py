from django.db import models

class Funcionario(models.Model):
    TIPO_PAGAMENTO_CHOICES = (
        ('MENSALISTA', 'Mensalista'),
        ('DIARISTA', 'Diarista'),
    )
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    tipo_pagamento = models.CharField(max_length=20, choices=TIPO_PAGAMENTO_CHOICES, default='MENSALISTA', verbose_name="Tipo de Pagamento")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salário Base / Mensal", default=0.00)
    valor_diaria = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da Diária", default=0.00, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    ativo = models.BooleanField(default=True, verbose_name="Está Ativo?")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.cargo}"

    @property
    def proximo_pagamento(self):
        from datetime import date
        hoje = date.today()
        dia = self.data_admissao.day
        
        # Tenta montar a data para o mês atual
        try:
            pagamento_mes_atual = hoje.replace(day=dia)
        except ValueError:
            # Se cair em dia inexistente (ex: dia 31 em fevereiro)
            pagamento_mes_atual = hoje.replace(day=28)
            
        if hoje > pagamento_mes_atual:
            # Se já passou, calcula para o próximo mês
            mes_seguinte = hoje.month + 1 if hoje.month < 12 else 1
            ano_seguinte = hoje.year if hoje.month < 12 else hoje.year + 1
            try:
                return hoje.replace(year=ano_seguinte, month=mes_seguinte, day=dia)
            except ValueError:
                return hoje.replace(year=ano_seguinte, month=mes_seguinte, day=28)
        return pagamento_mes_atual

class RegistroTrabalho(models.Model):
    TIPO_REGISTRO_CHOICES = (
        ('PRESENCA', 'Presença (Trabalhou)'),
        ('FALTA', 'Falta'),
        ('ATESTADO', 'Atestado Médico'),
        ('FOLGA', 'Folga'),
    )
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="registros_trabalho", verbose_name="Funcionário")
    data = models.DateField(verbose_name="Data")
    tipo = models.CharField(max_length=15, choices=TIPO_REGISTRO_CHOICES, default='PRESENCA', verbose_name="Tipo do Registro")
    valor_diaria_aplicada = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Diária Aplicada (R$)")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação / Detalhe do Atestado")
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcionario.nome} - {self.data} - {self.tipo}"


class CategoriaGasto(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição (Opcional)")

    def __str__(self):
        return self.nome


class Gasto(models.Model):
    descricao = models.CharField(max_length=255, verbose_name="Descrição do Gasto")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago (R$)")
    data_gasto = models.DateField(verbose_name="Data do Gasto")
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.PROTECT, related_name="gastos", verbose_name="Categoria")
    funcionario_vinculado = models.ForeignKey(
        Funcionario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="gastos_vinculados",
        verbose_name="Funcionário Referente (Opcional)",
        help_text="Preencha apenas se for um gasto direcionado a um funcionário específico (ex: EPI, Adiantamento)."
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"


class Empresa(models.Model):
    razao_social = models.CharField(max_length=200, verbose_name="Razão Social / Nome Fantasia")
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name="CNPJ")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço Completo")
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.razao_social


class Adiantamento(models.Model):
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente (A descontar)'),
        ('DESCONTADO', 'Descontado (Pago)'),
    )

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="adiantamentos", verbose_name="Funcionário")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Adiantamento (R$)")
    data = models.DateField(verbose_name="Data do Adiantamento")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcionario.nome} - R$ {self.valor} ({self.status})"

class Receita(models.Model):
    descricao = models.CharField(max_length=255, verbose_name="Descrição da Receita")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Recebido (R$)")
    data_recebimento = models.DateField(verbose_name="Data do Recebimento")
    empresa_cliente = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name="receitas", verbose_name="Cliente / Parceiro")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"
