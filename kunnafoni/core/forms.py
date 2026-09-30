
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profil
from .models import Autopalpation

class InscriptionForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=Profil.ROLES, 
        widget=forms.RadioSelect(attrs={'class': 'form-radio'}),
        label="Je m'inscris en tant que :"
    )
    structure = forms.CharField(
        max_length=150, 
        required=False, 
        label="Nom de la structure (Hôpitaux, CSPS, Associations uniquement)",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: CHU de Bogodogo'})
    )
    telephone = forms.CharField(
        max_length=20, 
        required=False, 
        label="Numéro de téléphone professionnel",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: +226 25 XX XX XX'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    # Validation personnalisée pour forcer les fournisseurs à renseigner leur structure
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        structure = cleaned_data.get('structure')

        if role == 'FOURNISSEUR' and not structure:
            self.add_error('structure', "Les fournisseurs de données doivent obligatoirement renseigner le nom de leur structure.")
        return cleaned_data


class AutopalpationForm(forms.ModelForm):
    class Meta:
        model = Autopalpation
        # Les champs modifiables par l'utilisatrice (L'utilisatrice est gérée en arrière-plan par la vue)
        fields = ['date', 'sein', 'observation', 'notes']
        
        # Personnalisation des widgets pour un affichage mobile confortable (Page 8)
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'style': 'width: 100%; padding: var(--xs); box-sizing: border-box;'
            }),
            'sein': forms.Select(attrs={
                'style': 'width: 100%; padding: var(--xs); box-sizing: border-box;'
            }),
            'observation': forms.Select(attrs={
                'style': 'width: 100%; padding: var(--xs); box-sizing: border-box;'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Précisions libres (facultatif)... Ex: Une légère sensibilité au toucher.',
                'rows': 4,
                'style': 'width: 100%; padding: var(--xs); box-sizing: border-box; font-family: inherit;'
            }),
        }
        
        labels = {
            'date': "Date de l'examen",
            'sein': "Quel sein a été examiné ?",
            'observation': "Qu'avez-vous constaté ? (Factuel)",
            'notes': "Notes et remarques complémentaires",
        }