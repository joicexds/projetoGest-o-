import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Configura o Site
site, created = Site.objects.get_or_create(id=1)
site.domain = '127.0.0.1:8000'
site.name = 'Florasylver Local'
site.save()

# Cria o app do Google
google_app, _ = SocialApp.objects.get_or_create(provider='google', defaults={'name': 'Login Google'})
google_app.client_id = 'FALTA_PREENCHER_NO_ADMIN'
google_app.secret = 'FALTA_PREENCHER_NO_ADMIN'
google_app.save()
google_app.sites.add(site)

# Cria o app do Facebook
facebook_app, _ = SocialApp.objects.get_or_create(provider='facebook', defaults={'name': 'Login Facebook'})
facebook_app.client_id = 'FALTA_PREENCHER_NO_ADMIN'
facebook_app.secret = 'FALTA_PREENCHER_NO_ADMIN'
facebook_app.save()
facebook_app.sites.add(site)

print("Social Apps criados com sucesso!")
