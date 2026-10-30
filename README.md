# FermeApp

Application web de gestion de ferme agro-pastorale : élevage, cultures, stocks, finances, tâches, alertes, exports.
Démo publique sans inscription (compte visiteur en lecture seule, données fictives).

**Stack** : Django 5.2, PostgreSQL (Supabase), Vercel, HTMX, Chart.js, design system CSS maison, icônes Lucide.

## Lancer en local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # renseigner SECRET_KEY ; DEBUG=True ; DATABASE_URL vide = SQLite locale
python manage.py migrate
python manage.py seed_demo  # ferme fictive complète
python manage.py runserver
```
Ouvrir http://127.0.0.1:8000 puis « Essayer la démo ».

## Rôles
| Rôle | Droits |
|---|---|
| Administrateur | Tout dans sa ferme |
| Employé | Consulte et saisit ; ni modification, ni suppression, ni configuration, ni finances/personnel |
| Visiteur | Lecture seule (aucune écriture possible, bloquée côté serveur) |

La politique d'accès est centralisée dans `core/permissions.py` et appliquée par `core/middleware.py`.

## Tests
```bash
DEBUG=True SECRET_KEY=test python manage.py test
```

## Déploiement (Supabase + Vercel)
1. Supabase : créer le projet, relever les chaînes de connexion « pooler » (session 5432, transaction 6543).
2. En local, avec le pooler **session** dans `.env` (`DATABASE_URL`) : `python manage.py migrate && python manage.py seed_demo`.
3. Vercel : importer le dépôt, définir `SECRET_KEY`, `DATABASE_URL` (pooler **transaction**, port 6543), `DEBUG=False`, `DEMO_ENABLED=True` pour tous les environnements.
4. GitHub : variable de dépôt `SITE_URL` (ex. `https://fermeapp.vercel.app`) ; le workflow `keepalive.yml` appelle `/health/` chaque jour pour éviter la mise en pause de Supabase.
5. Limite connue : le disque Vercel est en lecture seule, donc pas d'upload de photos en production (prévoir Supabase Storage si besoin).

Rafraîchir les dates de la démo : relancer `python manage.py seed_demo`.
