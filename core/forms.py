from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CadastroForm(UserCreationForm):
    nome = forms.CharField(max_length=150, required=True, label="Nome completo")
    email = forms.EmailField(max_length=254, required=True, label="E-mail")

    class Meta:
        model = User
        fields = ("nome", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Removendo o username padrão para usar o e-mail no lugar
        if 'username' in self.fields:
            del self.fields['username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['nome']
        user.email = self.cleaned_data['email']
        # Usaremos o próprio e-mail como 'username' único do sistema
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user
