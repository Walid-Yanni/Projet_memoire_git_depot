# dashboard/services/finance_service.py
"""Indicateurs financiers du tableau de bord, calculés depuis le journal réel (module Finances)."""
from datetime import date, timedelta

from finances import services as fin
from finances.models import Transaction


def get_finances(user):
    ferme = user.ferme
    qs = Transaction.objects.filter(ferme=ferme)
    mois = qs.filter(date__gte=date.today() - timedelta(days=30))
    t30 = fin.totals(mois)
    return {
        'recettes': float(t30['recettes']),
        'depenses': float(t30['depenses']),
        'marge': float(t30['solde']),
        'serie': fin.monthly_series(ferme, months=12),
    }
