from django import forms

from accounts.models import User
from .models import Tache


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ['titre', 'description', 'priorite', 'statut', 'echeance', 'assignee']
        widgets = {'echeance': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                   'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, ferme=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignee'].queryset = User.objects.filter(ferme=ferme) if ferme else User.objects.none()
        self.fields['assignee'].required = False
