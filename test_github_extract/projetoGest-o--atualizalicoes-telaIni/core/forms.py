from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Funcionario, Gasto, CategoriaGasto, Adiantamento, RegistroTrabalho, Receita, UserProfile

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

class RegistroTrabalhoForm(forms.ModelForm):
    class Meta:
        model = RegistroTrabalho
        fields = ['data', 'tipo', 'valor_diaria_aplicada', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 2}),
        }

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descricao', 'valor', 'data_gasto', 'categoria', 'funcionario_vinculado', 'observacoes']
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

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['descricao', 'valor', 'data_recebimento', 'observacoes']
        widgets = {
            'data_recebimento': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
