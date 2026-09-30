from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class Profil(models.Model):
    ROLES = [
        ('UTILISATRICE', 'Utilisatrice'),
        ('FOURNISSEUR', 'Fournisseur'),
    ]
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=15, choices=ROLES, default='UTILISATRICE')
    structure = models.CharField(max_length=150, blank=True, verbose_name="Nom de l'hôpital ou association")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Contact du fournisseur")

    def __str__(self):
        return f"{self.utilisateur.username} ({self.role})"

class Autopalpation(models.Model):
    SEINS = [
        ('GAUCHE', 'Sein Gauche'),
        ('DROIT', 'Sein Droit'),
        ('LES_DEUX', 'Les Deux Seins'),
    ]
    OBSERVATIONS = [
        ("RAS", "Rien de particulier"),
        ("MASSE", "Boule ou masse perçue"),
        ("DOULEUR", "Douleur inhabituelle"),
        ("ECOULEMENT", "Écoulement du mamelon"),
        ("PEAU", "Modification de la peau ou du mamelon"),
        ("AUTRE", "Autre observation"),
    ]
    utilisatrice = models.ForeignKey(User, on_delete=models.CASCADE, related_name='autopalpations')
    date = models.DateField(verbose_name="Date de l'autopalpation")
    sein = models.CharField(max_length=10, choices=SEINS)
    observation = models.CharField(max_length=15, choices=OBSERVATIONS)
    notes = models.TextField(blank=True, verbose_name="Précisions libres")
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-cree_le']

class Campagne(models.Model):
    fournisseur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campagnes')
    structure = models.CharField(max_length=120, verbose_name="Structure (ex: CHU de Bogodogo)")
    lieu = models.CharField(max_length=160, verbose_name="Adresse ou quartier")
    date = models.DateField(verbose_name="Jour du dépistage")
    heure = models.TimeField(verbose_name="Heure de début")
    communique = models.FileField(
        upload_to="communiques/%Y/%m/",
        validators=[FileExtensionValidator(["pdf", "png", "jpg", "jpeg"])],
        verbose_name="Communiqué officiel (5 Mo max)"
    )
    validee = models.BooleanField(default=False)
    publiee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

class Article(models.Model):
    RUBRIQUES = [
        ('PREVENTION', 'Prévention'),
        ('SYMPTOMES', 'Symptômes et signes d\'alerte'),
        ('DEPISTAGE', 'Dépistage et son importance'),
    ]
    titre = models.CharField(max_length=160, verbose_name="Titre de l'article")
    rubrique = models.CharField(max_length=15, choices=RUBRIQUES)
    contenu = models.TextField(verbose_name="Texte en langage simple")
    source = models.CharField(max_length=200, verbose_name="Source officielle (ex: OMS)")
    mis_a_jour_le = models.DateField(verbose_name="Date de la source")

    def __str__(self):
        return self.titre
