# kunnafoni/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views


# UN SEUL TABLEAU UNIQUE contenant toutes les routes de l'application
urlpatterns = [
    # 1. L'administration native de Django
    path('admin/', admin.site.urls),
    
    # 2. Les routes d'authentification (Page 9)
    path('connexion/', auth_views.LoginView.as_view(template_name='core/connexion.html'), name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # 3. Les routes principales du site (Page 7)
    path('inscription/', views.inscription, name='inscription'),
    path('', views.accueil, name='accueil'),
    path('infos/', views.portail_infos, name='infos'),
    path('portail-informations/symptomes/images/', views.galerie_symptomes, name='galerie_symptomes'),
    
    # NOUVELLES URLs : LE CARNET DE SUIVI CRUD (Page 7)
    path('carnet/guide-gestes/', views.guide_autopalpation, name='guide_autopalpation'),
    path('carnet/', views.carnet_liste, name='carnet_liste'),
    path('carnet/ajouter/', views.carnet_ajouter, name='carnet_ajouter'),
    path('carnet/<int:pk>/modifier/', views.carnet_modifier, name='carnet_modifier'),
    path('carnet/<int:pk>/supprimer/', views.carnet_supprimer, name='carnet_supprimer'),
    
    path('carnet/evolution/', views.carnet_evolution, name='carnet_evolution'),
    
    # 4. Route test de sécurité fournisseur (Critère d'acceptation F1)
    path('fournisseur/campagnes/publier/', views.publier_campagne_template, name='publier_campagne'),
    path('portail-informations/campagnes/toutes/', views.toutes_les_campagnes, name='toutes_campagnes'),
    path('assistant-sante/', views.chatbot_assistant, name='chatbot'),
    path('campagne/supprimer/<int:pk>/', views.supprimer_campagne, name='supprimer_campagne'),
]

# 5. Gestion des fichiers médias en local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
