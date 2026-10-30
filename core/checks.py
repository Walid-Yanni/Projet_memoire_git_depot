from django.conf import settings
from django.core.checks import Error, register


@register()
def production_config(app_configs, **kwargs):
    errors = []
    if settings.DATABASES['default']['NAME'] == '/tmp/fermeapp-missing-db.sqlite3':
        errors.append(Error('DATABASE_URL manquante : SQLite est interdit en production.',
                            hint="Définissez DATABASE_URL (Supabase Postgres).", id='fermeapp.E001'))
    return errors
