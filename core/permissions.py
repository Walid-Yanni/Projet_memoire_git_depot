"""
Politique d'accès centralisée.

- ADMIN     : tout dans sa ferme.
- EMPLOYE   : consulte et saisit (animaux, rapports, traitements, activités,
              mouvements de stock) mais ne modifie/supprime rien et ne
              touche pas à la configuration (lots, produits, parcelles...).
- VISITEUR  : compte de démonstration, lecture seule (aucune écriture en base).
"""
import re

# Écrans réservés à l'administrateur (nom d'URL complet "namespace:nom")
ADMIN_ONLY_URLS = {
    'cheptel:lot_create',
    'stocks:produit_create',
    'cultures:parcelle_create',
    'cultures:cultureparcelle_create',
}
# Préfixes de namespaces entiers réservés à l'administrateur (modules sensibles)
ADMIN_ONLY_NAMESPACES = {'personnel', 'finances'}
# Suffixes d'actions de modification
ADMIN_ONLY_SUFFIX = re.compile(r'_(edit|update|delete|cancel|archive|toggle)$')

# Vues accessibles sans connexion
PUBLIC_NAMESPACES = {'core', 'accounts'}
PUBLIC_URL_NAMES = {'admin:login'}


def requires_admin(namespace, url_name):
    full = f'{namespace}:{url_name}' if namespace else url_name
    if full in ADMIN_ONLY_URLS:
        return True
    if namespace in ADMIN_ONLY_NAMESPACES:
        return True
    return bool(ADMIN_ONLY_SUFFIX.search(url_name or ''))
