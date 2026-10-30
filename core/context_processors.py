from django.conf import settings


def app(request):
    user = getattr(request, 'user', None)
    return {
        'APP_NAME': 'FermeApp',
        'DEMO_ENABLED': settings.DEMO_ENABLED,
        'is_visiteur': bool(user and user.is_authenticated and getattr(user, 'role', '') == 'VISITEUR'),
        'is_admin_role': bool(user and user.is_authenticated and getattr(user, 'role', '') == 'ADMIN'),
        'can_write': bool(user and user.is_authenticated and getattr(user, 'role', '') in ('ADMIN', 'EMPLOYE')),
        'can_admin': bool(user and user.is_authenticated and getattr(user, 'role', '') in ('ADMIN', 'VISITEUR')),
    }
