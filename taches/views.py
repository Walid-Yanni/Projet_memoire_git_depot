from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TacheForm
from .models import Tache


@login_required
def board(request):
    taches = Tache.objects.filter(ferme=request.user.ferme).select_related('assignee')
    colonnes = [{'code': c, 'label': l, 'items': [t for t in taches if t.statut == c]} for c, l in Tache.STATUTS]
    return render(request, 'taches/board.html', {'colonnes': colonnes, 'total': len(taches), 'col_statuts': Tache.STATUTS})


@login_required
def tache_create(request):
    form = TacheForm(request.POST or None, ferme=request.user.ferme)
    if request.method == 'POST' and form.is_valid():
        t = form.save(commit=False)
        t.ferme, t.createur = request.user.ferme, request.user
        t.save()
        messages.success(request, 'Tâche créée.')
        return redirect('taches:board')
    return render(request, 'taches/tache_form.html', {'form': form, 'title': 'Nouvelle tâche'})


@login_required
def tache_update(request, pk):
    t = get_object_or_404(Tache, pk=pk, ferme=request.user.ferme)
    form = TacheForm(request.POST or None, instance=t, ferme=request.user.ferme)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tâche mise à jour.')
        return redirect('taches:board')
    return render(request, 'taches/tache_form.html', {'form': form, 'title': 'Modifier la tâche'})


@login_required
def tache_delete(request, pk):
    t = get_object_or_404(Tache, pk=pk, ferme=request.user.ferme)
    if request.method == 'POST':
        t.delete()
        messages.success(request, 'Tâche supprimée.')
        return redirect('taches:board')
    return render(request, 'taches/tache_confirm_delete.html', {'object': t})


@login_required
@require_POST
def tache_move(request, pk):
    t = get_object_or_404(Tache, pk=pk, ferme=request.user.ferme)
    statut = request.POST.get('statut')
    if statut in dict(Tache.STATUTS):
        t.statut = statut
        t.save(update_fields=['statut'])
    return redirect('taches:board')
