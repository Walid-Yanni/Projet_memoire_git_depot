# accounts/decorators.py
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view_func):
    """Réserve la vue à l'administrateur.

    Le visiteur de démonstration peut consulter l'écran (GET) ; toute écriture
    est bloquée par ReadOnlyVisitorMiddleware.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role not in ('ADMIN', 'VISITEUR'):
            messages.error(request, "Accès refusé. Cette action est réservée aux administrateurs.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper
