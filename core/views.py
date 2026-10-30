from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'core/landing.html')


def health(request):
    """Réveille la base (anti-pause Supabase) et sert de sonde."""
    try:
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
        return JsonResponse({'status': 'ok'})
    except Exception:  # pragma: no cover
        return JsonResponse({'status': 'error'}, status=503)


@require_POST
def demo_login(request):
    """Connexion en un clic au compte visiteur (lecture seule, données fictives)."""
    if not settings.DEMO_ENABLED:
        messages.error(request, "La démonstration est désactivée.")
        return redirect('core:landing')
    User = get_user_model()
    user = User.objects.filter(username=settings.DEMO_VISITOR_USERNAME, role='VISITEUR').first()
    if not user:
        messages.error(request, "La démo n'est pas encore initialisée (commande seed_demo).")
        return redirect('core:landing')
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('dashboard:home')


def forbidden(request, exception=None):
    return render(request, '403.html', status=403)
