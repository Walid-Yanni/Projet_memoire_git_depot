from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .forms import EmployeForm


@login_required
def staff_list(request):
    equipe = User.objects.filter(ferme=request.user.ferme).exclude(role='VISITEUR').order_by('role', 'first_name', 'username')
    return render(request, 'personnel/staff_list.html', {'equipe': equipe})


@login_required
def staff_create(request):
    form = EmployeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        u = form.save(commit=False)
        u.role, u.ferme = 'EMPLOYE', request.user.ferme
        u.set_password(form.cleaned_data['password'])
        u.save()
        messages.success(request, 'Compte employé créé.')
        return redirect('personnel:staff_list')
    return render(request, 'personnel/staff_form.html', {'form': form, 'title': 'Nouvel employé'})


@login_required
def staff_update(request, pk):
    u = get_object_or_404(User, pk=pk, ferme=request.user.ferme, role='EMPLOYE')
    form = EmployeForm(request.POST or None, instance=u)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data['password'])
        obj.save()
        messages.success(request, 'Compte mis à jour.')
        return redirect('personnel:staff_list')
    return render(request, 'personnel/staff_form.html', {'form': form, 'title': "Modifier l'employé"})
