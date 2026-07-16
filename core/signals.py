from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CategoriaGasto

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    """
    Sempre que um novo Usuário for cadastrado (created=True),
    cria automaticamente as categorias básicas para que ele possa usar o sistema.
    """
    if created:
        categorias_padrao = [
            "Alimentação",
            "Transporte",
            "Materiais/Insumos",
            "Pagamento de Pessoal",
            "Manutenção",
            "Outros"
        ]
        for nome in categorias_padrao:
            CategoriaGasto.objects.create(nome=nome, usuario=instance)
