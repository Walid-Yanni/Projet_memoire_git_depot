"""
Réglages Django de FermeApp.

Toute la configuration sensible vient de l'environnement (variables ou fichier .env).
Voir .env.example pour la liste des variables.
"""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

try:  # .env local (ignoré par git) ; sur Vercel les variables sont déjà injectées
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:  # pragma: no cover
    pass


def _bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def _list(name, default=''):
    return [v.strip() for v in os.environ.get(name, default).split(',') if v.strip()]


DEBUG = _bool('DEBUG', False)
ON_VERCEL = bool(os.environ.get('VERCEL'))

_DEV_KEY = 'dev-only-insecure-key-do-not-use-in-production'
SECRET_KEY = os.environ.get('SECRET_KEY', _DEV_KEY if DEBUG else '')
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY manquante (définissez-la dans .env ou dans Vercel).')
if not DEBUG and SECRET_KEY == _DEV_KEY:
    raise ImproperlyConfigured('Clé de développement interdite en production.')

ALLOWED_HOSTS = _list('ALLOWED_HOSTS', 'localhost,127.0.0.1' if DEBUG else '')
if ON_VERCEL:
    ALLOWED_HOSTS += ['.vercel.app']
CSRF_TRUSTED_ORIGINS = _list('CSRF_TRUSTED_ORIGINS')
if ON_VERCEL:
    CSRF_TRUSTED_ORIGINS += ['https://*.vercel.app']

# ── Application ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'cheptel',
    'cultures',
    'stocks',
    'dashboard',
    'finances',
    'taches',
    'personnel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.ReadOnlyVisitorMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fermeapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.app',
            ],
        },
    },
]

WSGI_APPLICATION = 'fermeapp.wsgi.application'

# ── Base de données ─────────────────────────────────────────
# Local : SQLite par défaut. Production : DATABASE_URL (Supabase Postgres) obligatoire.
_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    DATABASES = {'default': dj_database_url.parse(_db_url, conn_max_age=0)}
    if DATABASES['default']['ENGINE'].endswith('postgresql'):
        # Compatible pooler Supabase en mode transaction (port 6543)
        DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
        DATABASES['default'].setdefault('OPTIONS', {})['sslmode'] = 'require'
elif DEBUG:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                             'NAME': BASE_DIR / 'db_backend.sqlite3'}}
else:
    # Production sans DATABASE_URL : l'app démarre (le build Vercel exécute manage.py) mais
    # `manage.py check` échoue (voir core/checks.py) et aucune donnée n'est persistée.
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/fermeapp-missing-db.sqlite3'}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Porto-Novo'
USE_I18N = True
USE_TZ = True

# ── Fichiers statiques et médias ────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG
                    else 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'core:landing'

# ── Démo publique ───────────────────────────────────────────
DEMO_ENABLED = _bool('DEMO_ENABLED', True)
DEMO_ADMIN_USERNAME = 'demo_admin'
DEMO_VISITOR_USERNAME = 'demo_visiteur'

# ── Sécurité production ─────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Vercel termine déjà le TLS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_CONTENT_TYPE_NOSNIFF = True
