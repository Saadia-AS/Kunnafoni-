from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import InscriptionForm
from .models import Profil, Article
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Autopalpation
from .forms import AutopalpationForm
from django.utils import timezone
from datetime import timedelta
from collections import OrderedDict

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


# 1. LIRE : Liste historique du carnet (Page 3)
@login_required
def carnet_liste(request):
    # 🛡️ SÉCURITÉ ABSOLUE : Uniquement les entrées de l'utilisatrice connectée
    entrees = Autopalpation.objects.filter(utilisatrice=request.user)
    return render(request, 'core/carnet_liste.html', {'entrees': entrees})

# 2. CRÉER : Enregistrer une nouvelle autopalpation (Page 3)
@login_required
def carnet_ajouter(request):
    if request.method == 'POST':
        form = AutopalpationForm(request.POST)
        if form.is_valid():
            # commit=False permet de bloquer l'enregistrement pour y injecter l'utilisatrice connectée
            instance = form.save(commit=False)
            instance.utilisatrice = request.user
            instance.save()
            
            # Gestion du message post-saisie (Page 2 et 6)
            if instance.observation != "RAS":
                # Message d'invitation à consulter fixe, calme et factuel
                messages.warning(request, "Votre observation a été enregistrée. Par mesure de prévention, nous vous invitons à consulter rapidement un professionnel de santé pour un examen de contrôle.")
            else:
                messages.success(request, "Votre autopalpation mensuelle a été enregistrée avec succès.")
                
            return redirect('carnet_liste')
    else:
        form = AutopalpationForm()
    return render(request, 'core/carnet_form.html', {'form': form, 'titre': "Nouvel examen"})

# 3. MODIFIER : Éditer une entrée existante (Page 3)
@login_required
def carnet_modifier(request, pk):
    # 🛡️ SÉCURITÉ ANTI-FRAUDE : Le get_object_or_404 filtre AUSSI sur l'utilisatrice connectée (Page 9)
    entree = get_object_or_404(Autopalpation, pk=pk, utilisatrice=request.user)
    
    if request.method == 'POST':
        form = AutopalpationForm(request.POST, instance=entree)
        if form.is_valid():
            form.save()
            messages.success(request, "L'entrée de votre carnet a été modifiée.")
            return redirect('carnet_liste')
    else:
        form = AutopalpationForm(instance=entree)
    return render(request, 'core/carnet_form.html', {'form': form, 'titre': "Modifier l'examen"})

# 4. SUPPRIMER : Retirer une entrée avec confirmation (Page 3)
@login_required
def carnet_supprimer(request, pk):
    # 🛡️ SÉCURITÉ ANTI-FRAUDE : Verrouillage strict par ID et propriétaire
    entree = get_object_or_404(Autopalpation, pk=pk, utilisatrice=request.user)
    
    if request.method == 'POST':
        entree.delete()
        messages.success(request, "L'entrée a été définitivement supprimée de votre historique.")
        return redirect('carnet_liste')
        
    return render(request, 'core/carnet_sup_confirmer.html', {'entree': entree})

@login_required
def carnet_evolution(request):
    maintenant = timezone.now().date()
    il_y_a_un_an = maintenant - timedelta(days=365)
    
    # 🛡️ CLOISONNEMENT STRICT : Uniquement les données de l'utilisatrice connectée
    toutes_palpations = Autopalpation.objects.filter(utilisatrice=request.user)
    palpations_annee = toutes_palpations.filter(date__gte=il_y_a_un_an)

    # 1. CALCUL DU NOMBRE DE JOURS ÉCOULÉS DEPUIS LA DERNIÈRE PALPATION
    derniere_palpation = toutes_palpations.order_by('-date').first()
    if derniere_palpation:
        jours_ecoules = (maintenant - derniere_palpation.date).days
    else:
        jours_ecoules = None # Signifie "Aucun examen enregistré à ce jour"

    # 2. PRÉPARATION DU GRAPHIQUE MENSUEL EN CSS PUR (12 derniers mois glissants)
    # On initialise un dictionnaire pour les 12 derniers mois avec 0 palpation
    mois_graphique = OrderedDict()
    for i in range(11, -1, -1):
        date_mois = maintenant - timedelta(days=i*30)
        cle_mois = date_mois.strftime("%Y-%m")
        nom_mois_court = date_mois.strftime("%b") # Ex: "Jan", "Feb"...
        mois_graphique[cle_mois] = {'nom': nom_mois_court, 'total': 0, 'hauteur_css': 0}

    # On remplit avec les vraies données de l'utilisatrice
    for p in palpations_annee:
        cle_p = p.date.strftime("%Y-%m")
        if cle_p in mois_graphique:
            mois_graphique[cle_p]['total'] += 1

    # On calcule la hauteur de chaque barre en pourcentage (1 palpation/mois = 100% de l'objectif mensuel)
    for cle, data in mois_graphique.items():
        # Si l'utilisatrice a fait 1 palpation ou plus, la barre monte à 100% max
        data['hauteur_css'] = min(data['total'] * 100, 100)

    # 3. LISTE FACTUELLE DES ANOMALIES (Sans aucun jugement médical)
    anomalies = toutes_palpations.exclude(observation="RAS").order_by('-date')

    context = {
        'jours_ecoules': jours_ecoules,
        'mois_graphique': mois_graphique.values(),
        'anomalies': anomalies,
    }
    return render(request, 'core/evolution.html', context)
