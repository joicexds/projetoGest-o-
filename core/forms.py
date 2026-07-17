from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Funcionario, Gasto, CategoriaGasto, Adiantamento, RegistroTrabalho, Receita, UserProfile, Atestado, Apontamento, FazendaCliente

class CadastroForm(UserCreationForm):
    nome = forms.CharField(max_length=150, required=True, label="Nome completo")
    email = forms.EmailField(max_length=254, required=True, label="E-mail")

    class Meta:
        model = User
        fields = ("username", "nome", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Nome de Usuário (para Login)"
        self.fields['username'].help_text = "Letras, números e os símbolos @/./+/-/_ apenas."

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.lower()
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UsuarioUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="Nome completo")
    email = forms.EmailField(max_length=254, required=True, label="E-mail")

    class Meta:
        model = User
        fields = ("first_name", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado por outro usuário.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('foto',)
        labels = {
            'foto': 'Foto de Perfil'
        }

class CustomLoginForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.lower()
        return username

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'cpf', 'cargo', 'tipo_pagamento', 'salario', 'valor_diaria', 'telefone', 'data_admissao', 'ativo']
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        if not cpf:
            return cpf
        import re
        cpf_numeros = re.sub(r'[^0-9]', '', cpf)
        if len(cpf_numeros) != 11:
            raise forms.ValidationError("CPF inválido. Deve conter exatamente 11 números.")
        
        if cpf_numeros == cpf_numeros[0] * 11:
            raise forms.ValidationError("CPF inválido.")
            
        def calcula_digito(cpf_parcial):
            soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial) + 1, 1, -1)))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)
            
        digito1 = calcula_digito(cpf_numeros[:9])
        digito2 = calcula_digito(cpf_numeros[:9] + digito1)
        
        if cpf_numeros[-2:] != digito1 + digito2:
            raise forms.ValidationError("CPF inválido.")
            
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"

class RegistroTrabalhoForm(forms.ModelForm):
    class Meta:
        model = RegistroTrabalho
        fields = ['data', 'tipo', 'valor_diaria_aplicada', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 2}),
        }

class FazendaClienteForm(forms.ModelForm):
    class Meta:
        model = FazendaCliente
        fields = ['nome']

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descricao', 'valor', 'data_gasto', 'categoria', 'funcionario_vinculado', 'fazenda_cliente', 'observacoes']
        widgets = {
            'data_gasto': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = CategoriaGasto.objects.filter(usuario=user)
            self.fields['funcionario_vinculado'].queryset = Funcionario.objects.filter(usuario=user)
            self.fields['fazenda_cliente'].queryset = FazendaCliente.objects.filter(usuario=user)

class AdiantamentoForm(forms.ModelForm):
    class Meta:
        model = Adiantamento
        fields = ['funcionario', 'valor', 'data', 'status', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['funcionario'].queryset = Funcionario.objects.filter(usuario=user)

    def clean_data(self):
        data = self.cleaned_data.get('data')
        from datetime import date
        if data and data.year < date.today().year:
            raise forms.ValidationError("Não é permitido lançar vales com datas de anos anteriores.")
        return data

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['descricao', 'valor', 'data_recebimento', 'fazenda_cliente', 'observacoes']
        widgets = {
            'data_recebimento': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['fazenda_cliente'].queryset = FazendaCliente.objects.filter(usuario=user)

class AtestadoForm(forms.ModelForm):
    class Meta:
        model = Atestado
        fields = ['funcionario', 'data_inicio', 'data_fim', 'foto', 'observacao']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['funcionario'].queryset = Funcionario.objects.filter(usuario=user)

class ApontamentoForm(forms.ModelForm):
    class Meta:
        model = Apontamento
        fields = ['funcionario', 'data_inicio', 'data_fim', 'dias_trabalhados', 'dias_falta', 'valor_horas_extras', 'bonificacao', 'observacao']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['funcionario'].queryset = Funcionario.objects.filter(usuario=user)
        self.fields['dias_trabalhados'].required = False
        self.fields['dias_falta'].required = False
        self.fields['valor_horas_extras'].required = False
        self.fields['bonificacao'].required = False

    def clean_dias_trabalhados(self):
        val = self.cleaned_data.get('dias_trabalhados')
        return val if val is not None else 0

    def clean_dias_falta(self):
        val = self.cleaned_data.get('dias_falta')
        return val if val is not None else 0

    def clean_valor_horas_extras(self):
        val = self.cleaned_data.get('valor_horas_extras')
        return val if val is not None else 0.00

    def clean_bonificacao(self):
        val = self.cleaned_data.get('bonificacao')
        return val if val is not None else 0.00
