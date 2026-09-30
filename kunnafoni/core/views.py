from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import InscriptionForm
from .models import Profil, Article

""" Vue d'Inscription (Création synchronisée Compte + Profil)"""
def inscription(request):
    if request.user.is_authenticated:
        return redirect('accueil')
        
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            """Création immédiate et obligatoire du profil lié (Consigne Page 10)"""
            Profil.objects.create(
                utilisateur=user,
                role=form.cleaned_data.get('role'),
                structure=form.cleaned_data.get('structure', ''),
                telephone=form.cleaned_data.get('telephone', '')
            )
            
            """ Connexion automatique après inscription et redirection"""
            login(request, user)
            return redirect('accueil')
    else:
        form = InscriptionForm()
    return render(request, 'core/inscription.html', {'form': form})

# MODIFICATION ICI : Sécurisation de la vue accueil pour le compte Superutilisateur
@login_required
def accueil(request):
    """ Filet de sécurité pour les comptes créés via le terminal (ex: Superuser) """
    try:
        profil = request.user.profil
    except Profil.DoesNotExist:
        # Génère automatiquement un profil par défaut pour l'admin afin d'éviter le crash
        profil = Profil.objects.create(utilisateur=request.user, role='UTILISATRICE')
        
    return render(request, 'core/accueil.html', {'profil': profil})

# 3. F2 - Vue du Portail d'Information (Sensibilisation médicale) - Page 2 & 7
@login_required
def portail_infos(request):
    """Récupération de tous les articles rédigés dans l'admin Django"""
    articles_prevention = Article.objects.filter(rubrique='PREVENTION')
    articles_symptomes = Article.objects.filter(rubrique='SYMPTOMES')
    articles_depistage = Article.objects.filter(rubrique='DEPISTAGE')
    
    context = {
        'articles_prevention': articles_prevention,
        'articles_symptomes': articles_symptomes,
        'articles_depistage': articles_depistage,
    }
    return render(request, 'core/infos.html', context)

# 4. Simulation d'URL Fournisseur protégée pour tester le critère d'acceptation (Page 2)
@login_required
def publier_campagne_template(request):
    if request.user.profil.role != "FOURNISSEUR":
        raise PermissionDenied 
    return render(request, 'core/fournisseur_campagnes.html')
