# core/admin.py
from django.contrib import admin
from .models import Profil, Autopalpation, Campagne, Article

# Enregistrement des modèles pour les rendre visibles dans l'interface /admin
admin.site.register(Profil)
admin.site.register(Autopalpation)
admin.site.register(Campagne)
admin.site.register(Article)
