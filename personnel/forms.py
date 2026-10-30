from django import forms
from django.contrib.auth.password_validation import validate_password

from accounts.models import User


class EmployeForm(forms.ModelForm):
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput, required=False,
                               help_text='Laisser vide pour conserver le mot de passe actuel.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'adresse', 'is_active']

    def clean_password(self):
        pw = self.cleaned_data.get('password')
        if not self.instance.pk and not pw:
            raise forms.ValidationError('Un mot de passe est requis pour un nouveau compte.')
        if pw:
            validate_password(pw)
        return pw
