from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('accounts/cadastro/', views.cadastro, name='cadastro'),
]
