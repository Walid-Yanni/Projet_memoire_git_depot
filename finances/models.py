from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models import Ferme, User


class Transaction(models.Model):
    """Journal financier : source de vérité des recettes et dépenses de la ferme."""

    RECETTE, DEPENSE = 'RECETTE', 'DEPENSE'
    TYPE_CHOICES = [(RECETTE, 'Recette'), (DEPENSE, 'Dépense')]

    CATEGORIES = [
        ('VENTE_OEUFS', 'Vente d\'œufs'),
        ('VENTE_ANIMAUX', 'Vente d\'animaux'),
        ('VENTE_RECOLTE', 'Vente de récolte'),
        ('AUTRE_RECETTE', 'Autre recette'),
        ('ALIMENT', 'Aliments'),
        ('SANTE', 'Santé et vétérinaire'),
        ('SEMENCES', 'Semences et intrants'),
        ('SALAIRES', 'Salaires'),
        ('MAINTENANCE', 'Maintenance et équipement'),
        ('TRANSPORT', 'Transport'),
        ('AUTRE_DEPENSE', 'Autre dépense'),
    ]
    CATEGORIES_RECETTE = ['VENTE_OEUFS', 'VENTE_ANIMAUX', 'VENTE_RECOLTE', 'AUTRE_RECETTE']

    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    montant = models.DecimalField(max_digits=12, decimal_places=0, help_text='Montant en FCFA')
    date = models.DateField(default=timezone.now)
    libelle = models.CharField(max_length=200)
    tiers = models.CharField(max_length=120, blank=True, help_text='Client ou fournisseur')
    notes = models.TextField(blank=True)

    createur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='transactions_creees')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        indexes = [models.Index(fields=['ferme', 'date']), models.Index(fields=['type'])]

    def clean(self):
        super().clean()
        if self.montant is not None and self.montant <= 0:
            raise ValidationError('Le montant doit être strictement positif.')
        if self.type == self.RECETTE and self.categorie not in self.CATEGORIES_RECETTE:
            raise ValidationError('Catégorie incompatible avec une recette.')
        if self.type == self.DEPENSE and self.categorie in self.CATEGORIES_RECETTE:
            raise ValidationError('Catégorie incompatible avec une dépense.')

    def __str__(self):
        signe = '+' if self.type == self.RECETTE else '-'
        return f'{self.libelle} ({signe}{self.montant})'

    @property
    def signed(self):
        return self.montant if self.type == self.RECETTE else -self.montant
