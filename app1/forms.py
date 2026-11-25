# your_app_name/forms.py

from django import forms
from .models import Arrivage, Poste, TypePiece, Comptable, Trimestre

class ArrivageForm(forms.ModelForm):
    class Meta:
        model = Arrivage
        fields = ['poste', 'type_piece', 'comptables', 'date_arrivage', 'trimestres', 'user']
        widgets = {
            'date_arrivage': forms.DateInput(attrs={'type': 'date'}),
            # Use SelectMultiple and add a specific class for Select2
            'comptables': forms.SelectMultiple(attrs={'class': 'select2-comptables form-control'}),
            'trimestres': forms.CheckboxSelectMultiple,
        }
        labels = {
            'poste': 'Poste Comptable',
            'type_piece': 'Type de Pièce',
            'comptables': 'Comptables Concernés',
            'date_arrivage': 'Date d\'Arrivage',
            'trimestres': 'Trimestres Concernés',
            'user': 'Utilisateur TGR',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_arrivage'].label = 'Date d\'Arrivage'
        self.fields['poste'].queryset = Poste.objects.all()
        self.fields['type_piece'].queryset = TypePiece.objects.all()
        self.fields['comptables'].queryset = Comptable.objects.all()
        self.fields['trimestres'].queryset = Trimestre.objects.all()
        self.fields['user'].widget = forms.HiddenInput()