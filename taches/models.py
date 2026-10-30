from django.db import models
from django.utils import timezone

from accounts.models import Ferme, User


class Tache(models.Model):
    A_FAIRE, EN_COURS, TERMINEE = 'A_FAIRE', 'EN_COURS', 'TERMINEE'
    STATUTS = [(A_FAIRE, 'À faire'), (EN_COURS, 'En cours'), (TERMINEE, 'Terminée')]
    PRIORITES = [('BASSE', 'Basse'), ('NORMALE', 'Normale'), ('HAUTE', 'Haute')]

    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE, related_name='taches')
    titre = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=10, choices=STATUTS, default=A_FAIRE)
    priorite = models.CharField(max_length=10, choices=PRIORITES, default='NORMALE')
    echeance = models.DateField(null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taches_assignees')
    createur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taches_creees')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['echeance', '-created_at']
        indexes = [models.Index(fields=['ferme', 'statut'])]

    def __str__(self):
        return self.titre

    @property
    def en_retard(self):
        return bool(self.echeance and self.statut != self.TERMINEE and self.echeance < timezone.localdate())
