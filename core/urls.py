from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    # A rota vazia '' agora é o login
    path('', auth_views.LoginView.as_view(authentication_form=CustomLoginForm), name='login_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/', views.perfil_usuario, name='perfil'),

    # Funcionários
    path('funcionarios/', views.funcionario_list, name='funcionario_list'),
    path('funcionarios/novo/', views.funcionario_form, name='funcionario_create'),
    path('funcionarios/<int:id>/', views.funcionario_detail, name='funcionario_detail'),
    path('funcionarios/<int:id>/holerite/', views.funcionario_holerite, name='funcionario_holerite'),
    path('funcionarios/editar/<int:id>/', views.funcionario_form, name='funcionario_update'),
    path('funcionarios/excluir/<int:id>/', views.funcionario_delete, name='funcionario_delete'),
    path('registros/excluir/<int:id>/', views.registro_trabalho_delete, name='registro_trabalho_delete'),

    # Atestados e Apontamentos
    path('acoes-rh/', views.acoes_rh, name='acoes_rh'),
    path('atestados/', views.atestado_list, name='atestado_list'),
    path('atestados/novo/', views.atestado_form_global, name='atestado_create_global'),
    path('funcionarios/<int:func_id>/atestado/novo/', views.atestado_form, name='atestado_create'),
    path('atestados/excluir/<int:id>/', views.atestado_delete, name='atestado_delete'),
    
    path('apontamentos/', views.apontamento_list, name='apontamento_list'),
    path('apontamentos/novo/', views.apontamento_form_global, name='apontamento_create_global'),
    path('funcionarios/<int:func_id>/apontamento/novo/', views.apontamento_form, name='apontamento_create'),
    path('apontamentos/excluir/<int:id>/', views.apontamento_delete, name='apontamento_delete'),

    # Gastos
    path('gastos/', views.gasto_list, name='gasto_list'),
    path('gastos/novo/', views.gasto_form, name='gasto_create'),
    path('gastos/editar/<int:id>/', views.gasto_form, name='gasto_update'),
    path('gastos/excluir/<int:id>/', views.gasto_delete, name='gasto_delete'),



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

    # Fazendas / Clientes
    path('fazendas/', views.fazenda_list, name='fazenda_list'),
    path('fazendas/novo/', views.fazenda_form, name='fazenda_create'),
    path('fazendas/editar/<int:id>/', views.fazenda_form, name='fazenda_update'),
    path('fazendas/excluir/<int:id>/', views.fazenda_delete, name='fazenda_delete'),

    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
]
