from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # A rota vazia '' agora é o login
    path('', auth_views.LoginView.as_view(), name='login_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # Funcionários
    path('funcionarios/', views.funcionario_list, name='funcionario_list'),
    path('funcionarios/novo/', views.funcionario_form, name='funcionario_create'),
    path('funcionarios/<int:id>/', views.funcionario_detail, name='funcionario_detail'),
    path('funcionarios/<int:id>/holerite/', views.funcionario_holerite, name='funcionario_holerite'),
    path('funcionarios/editar/<int:id>/', views.funcionario_form, name='funcionario_update'),
    path('funcionarios/excluir/<int:id>/', views.funcionario_delete, name='funcionario_delete'),
    path('registros/excluir/<int:id>/', views.registro_trabalho_delete, name='registro_trabalho_delete'),

    # Gastos
    path('gastos/', views.gasto_list, name='gasto_list'),
    path('gastos/novo/', views.gasto_form, name='gasto_create'),
    path('gastos/editar/<int:id>/', views.gasto_form, name='gasto_update'),
    path('gastos/excluir/<int:id>/', views.gasto_delete, name='gasto_delete'),

    # Empresas
    path('empresas/', views.empresa_list, name='empresa_list'),
    path('empresas/novo/', views.empresa_form, name='empresa_create'),
    path('empresas/editar/<int:id>/', views.empresa_form, name='empresa_update'),
    path('empresas/excluir/<int:id>/', views.empresa_delete, name='empresa_delete'),

    # Adiantamentos
    path('adiantamentos/', views.adiantamento_list, name='adiantamento_list'),
    path('adiantamentos/novo/', views.adiantamento_form, name='adiantamento_create'),
    path('adiantamentos/editar/<int:id>/', views.adiantamento_form, name='adiantamento_update'),
    path('adiantamentos/excluir/<int:id>/', views.adiantamento_delete, name='adiantamento_delete'),

    # Receitas
    path('receitas/', views.receita_list, name='receita_list'),
    path('receitas/novo/', views.receita_form, name='receita_create'),
    path('receitas/editar/<int:id>/', views.receita_form, name='receita_update'),
    path('receitas/excluir/<int:id>/', views.receita_delete, name='receita_delete'),

    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
]
