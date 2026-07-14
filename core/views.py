from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm
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
    return render(request, 'dashboard.html')
