"""Applique la politique d'accès à toutes les vues, en un seul endroit."""
from django.contrib import messages
from django.shortcuts import redirect, render

from .permissions import PUBLIC_NAMESPACES, requires_admin

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class ReadOnlyVisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match
        user = getattr(request, 'user', None)
        if not match or not user or not user.is_authenticated:
            return None
        ns, name = match.namespace or '', match.url_name or ''
        if ns in ('admin', 'core') or ns == 'accounts' and name in ('logout', 'login'):
            return None

        role = getattr(user, 'role', None)

        # Visiteur : aucune écriture, jamais.
        if role == 'VISITEUR' and request.method not in SAFE_METHODS:
            messages.info(request, "Mode démonstration : l'application est en lecture seule.")
            return redirect(request.META.get('HTTP_REFERER') or 'dashboard:home')

        # Employé : pas d'accès aux écrans réservés à l'administrateur.
        if role == 'EMPLOYE' and requires_admin(ns, name):
            return render(request, '403.html', status=403)
        return None
