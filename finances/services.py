"""Calculs financiers (agrégats) pour le module et le tableau de bord."""
from collections import OrderedDict
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from .models import Transaction


def totals(qs):
    rec = qs.filter(type=Transaction.RECETTE).aggregate(s=Sum('montant'))['s'] or Decimal('0')
    dep = qs.filter(type=Transaction.DEPENSE).aggregate(s=Sum('montant'))['s'] or Decimal('0')
    return {'recettes': rec, 'depenses': dep, 'solde': rec - dep,
            'marge': round((rec - dep) / rec * 100, 1) if rec else None}


def monthly_series(ferme, months=12, today=None):
    """Liste de dicts {label, recettes, depenses} sur les `months` derniers mois."""
    today = today or date.today()
    keys = []
    y, m = today.year, today.month
    for _ in range(months):
        keys.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    keys.reverse()
    start = date(keys[0][0], keys[0][1], 1)
    rows = (Transaction.objects.filter(ferme=ferme, date__gte=start)
            .annotate(mois=TruncMonth('date')).values('mois', 'type').annotate(total=Sum('montant')))
    data = OrderedDict(((y, m), {'recettes': 0, 'depenses': 0}) for y, m in keys)
    for r in rows:
        k = (r['mois'].year, r['mois'].month)
        if k in data:
            data[k]['recettes' if r['type'] == Transaction.RECETTE else 'depenses'] = float(r['total'])
    noms = ['Janv', 'Févr', 'Mars', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
    return [{'label': noms[m - 1], **v} for (y, m), v in data.items()]


def by_category(qs, type_):
    labels = dict(Transaction.CATEGORIES)
    rows = (qs.filter(type=type_).values('categorie').annotate(total=Sum('montant')).order_by('-total'))
    return [{'label': labels[r['categorie']], 'total': float(r['total'])} for r in rows]
