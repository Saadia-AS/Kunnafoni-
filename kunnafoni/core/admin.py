
from django.contrib import admin
from .models import Profil, Article, Autopalpation, Campagne

# 1. Enregistrement simple des modèles de base
admin.site.register(Profil)
admin.site.register(Article)
admin.site.register(Autopalpation)

# 2. Personnalisation avancée et enregistrement de Campagne (Issue #7)
@admin.register(Campagne)  # 👈 Cette ligne force Django à afficher le bouton Campagnes
class CampagneAdmin(admin.ModelAdmin):
    list_display = ('structure', 'lieu', 'date', 'heure', 'validee', 'fournisseur')
    list_filter = ('validee', 'date', 'structure')
    search_fields = ('structure', 'lieu')
    ordering = ('-date',)
    actions = ['approuver_campagnes', 'suspendre_campagnes']

    @admin.action(description="Approuver et publier les campagnes sélectionnées (Grand Public)")
    def approuver_campagnes(self, request, queryset):
        lignes_mises_a_jour = queryset.update(validee=True)
        self.message_user(request, f"Succès : {lignes_mises_a_jour} campagne(s) officielle(s) approuvée(s) et publiée(s) sur le site.")

    @admin.action(description="Masquer temporairement les campagnes sélectionnées")
    def suspendre_campagnes(self, request, queryset):
        lignes_mises_a_jour = queryset.update(validee=False)
        self.message_user(request, f"Attention : {lignes_mises_a_jour} campagne(s) masquée(s) du tableau de bord grand public.")
