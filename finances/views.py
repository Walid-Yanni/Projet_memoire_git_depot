import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TransactionForm
from .models import Transaction
from . import services


def _qs(request):
    qs = Transaction.objects.filter(ferme=request.user.ferme)
    t = request.GET.get('type')
    if t in (Transaction.RECETTE, Transaction.DEPENSE):
        qs = qs.filter(type=t)
    cat = request.GET.get('categorie')
    if cat:
        qs = qs.filter(categorie=cat)
    mois = request.GET.get('mois')  # AAAA-MM
    if mois:
        try:
            y, m = map(int, mois.split('-'))
            qs = qs.filter(date__year=y, date__month=m)
        except ValueError:
            pass
    return qs


@login_required
def transaction_list(request):
    ferme = request.user.ferme
    qs = _qs(request)
    page = Paginator(qs.select_related('createur'), 25).get_page(request.GET.get('page'))
    ctx = {
        'page_obj': page,
        'transactions': page,
        'is_paginated': page.paginator.num_pages > 1,
        'totals': services.totals(qs),
        'serie': services.monthly_series(ferme),
        'cat_depenses': services.by_category(Transaction.objects.filter(ferme=ferme), Transaction.DEPENSE),
        'cat_recettes': services.by_category(Transaction.objects.filter(ferme=ferme), Transaction.RECETTE),
        'categories': Transaction.CATEGORIES,
        'filtre': {k: request.GET.get(k, '') for k in ('type', 'categorie', 'mois')},
    }
    return render(request, 'finances/transaction_list.html', ctx)


@login_required
def transaction_export(request):
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="transactions_{date.today():%Y%m%d}.csv"'
    resp.write('﻿')
    w = csv.writer(resp, delimiter=';')
    w.writerow(['Date', 'Type', 'Catégorie', 'Libellé', 'Tiers', 'Montant FCFA'])
    for t in _qs(request).order_by('date'):
        w.writerow([t.date.isoformat(), t.get_type_display(), t.get_categorie_display(),
                    t.libelle, t.tiers, t.montant])
    return resp


@login_required
def transaction_create(request):
    form = TransactionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.ferme, obj.createur = request.user.ferme, request.user
        obj.save()
        messages.success(request, 'Transaction enregistrée.')
        return redirect('finances:transaction_list')
    return render(request, 'finances/transaction_form.html', {'form': form, 'titre': 'Nouvelle transaction'})


@login_required
def transaction_update(request, pk):
    obj = get_object_or_404(Transaction, pk=pk, ferme=request.user.ferme)
    form = TransactionForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Transaction mise à jour.')
        return redirect('finances:transaction_list')
    return render(request, 'finances/transaction_form.html', {'form': form, 'titre': 'Modifier la transaction'})


@login_required
def transaction_delete(request, pk):
    obj = get_object_or_404(Transaction, pk=pk, ferme=request.user.ferme)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Transaction supprimée.')
        return redirect('finances:transaction_list')
    return render(request, 'finances/transaction_confirm_delete.html', {'obj': obj})
