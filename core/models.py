from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt

class Funcionario(models.Model):
    TIPO_PAGAMENTO_CHOICES = (
        ('MENSALISTA', 'Mensalista'),
        ('DIARISTA', 'Diarista'),
    )
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = encrypt(models.CharField(max_length=14, verbose_name="CPF"))
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    tipo_pagamento = models.CharField(max_length=20, choices=TIPO_PAGAMENTO_CHOICES, default='MENSALISTA', verbose_name="Tipo de Pagamento")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salário Base / Mensal", default=0.00)
    valor_diaria = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da Diária", default=0.00, blank=True, null=True)
    telefone = encrypt(models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone"))
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    ativo = models.BooleanField(default=True, verbose_name="Está Ativo?")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1, verbose_name="Usuário Proprietário")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'cpf']

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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcionario.nome} - {self.data} - {self.tipo}"


class FazendaCliente(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Fazenda / Cliente")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ['usuario', 'nome']

    def __str__(self):
        return self.nome


class CategoriaGasto(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição (Opcional)")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ['usuario', 'nome']

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
    fazenda_cliente = models.ForeignKey(FazendaCliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="gastos", verbose_name="Fazenda / Cliente")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"



class Adiantamento(models.Model):
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente (A descontar)'),
        ('DESCONTADO', 'Descontado (Pago)'),
    )

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="adiantamentos", verbose_name="Funcionário")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Adiantamento (R$)")
    data = models.DateField(verbose_name="Data do Adiantamento")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    apontamento_vinculado = models.ForeignKey('Apontamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='vales_descontados')
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcionario.nome} - R$ {self.valor} ({self.status})"

class Receita(models.Model):
    descricao = models.CharField(max_length=255, verbose_name="Descrição da Receita")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Recebido (R$)")
    data_recebimento = models.DateField(verbose_name="Data do Recebimento")
    fazenda_cliente = models.ForeignKey(FazendaCliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="receitas", verbose_name="Fazenda / Cliente")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"


class Atestado(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="atestados_medicos", verbose_name="Funcionário")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Retorno")
    foto = models.ImageField(upload_to="atestados/", blank=True, null=True, verbose_name="Foto do Atestado")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observações / CID")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Atestado: {self.funcionario.nome} ({self.data_inicio} a {self.data_fim})"

class Apontamento(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name="apontamentos", verbose_name="Funcionário")
    data_inicio = models.DateField(verbose_name="Data de Início do Período")
    data_fim = models.DateField(verbose_name="Data de Fim do Período")
    dias_trabalhados = models.PositiveIntegerField(default=0, verbose_name="Dias Trabalhados (Diaristas)")
    dias_falta = models.PositiveIntegerField(default=0, verbose_name="Dias de Falta (Mensalistas)")
    valor_horas_extras = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Horas Extras (R$)")
    bonificacao = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Bonificação (R$)")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observações")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Apontamento: {self.funcionario.nome} ({self.data_inicio} a {self.data_fim})"

    @property
    def calculo_ganhos(self):
        base = 0.0
        if self.funcionario.tipo_pagamento == 'DIARISTA':
            base = float(self.dias_trabalhados) * float(self.funcionario.valor_diaria or 0)
        else:
            base = float(self.funcionario.salario)
        return base + float(self.valor_horas_extras) + float(self.bonificacao)
            
    @property
    def calculo_desconto_faltas(self):
        if self.funcionario.tipo_pagamento == 'MENSALISTA':
            valor_dia = float(self.funcionario.salario) / 30.0
            return float(self.dias_falta) * valor_dia
        return 0.0

    @property
    def calculo_adiantamentos(self):
        # Novo formato: Vales explicitamente vinculados a este apontamento
        vales_fk = self.vales_descontados.aggregate(total=models.Sum('valor'))['total'] or 0.0
        
        # Legado: Vales antigos que dependem apenas do range de datas
        vales_legacy = self.funcionario.adiantamentos.filter(
            data__gte=self.data_inicio,
            data__lte=self.data_fim,
            status='DESCONTADO',
            apontamento_vinculado__isnull=True
        ).aggregate(total=models.Sum('valor'))['total'] or 0.0
        
        return float(vales_fk) + float(vales_legacy)

    @property
    def calculo_liquido(self):
        return self.calculo_ganhos - self.calculo_desconto_faltas - self.calculo_adiantamentos

    @property
    def calculo_total_descontos(self):
        return self.calculo_desconto_faltas + self.calculo_adiantamentos

from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    foto = models.ImageField(upload_to='perfil_fotos/', blank=True, null=True, verbose_name="Foto de Perfil")

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
