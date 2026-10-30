"""Chaque page doit s'afficher sans erreur pour chaque rôle, sur la ferme de démonstration."""
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import User

PAGES = [
    'dashboard:home', 'cheptel:animal_list', 'cheptel:animal_add', 'cheptel:lot_list', 'cheptel:lot_create',
    'cheptel:rapport_list', 'cheptel:rapport_add', 'cheptel:traitement_list', 'cheptel:traitement_add',
    'cultures:parcelle_list', 'cultures:parcelle_create', 'cultures:culture_list', 'cultures:cultureparcelle_list',
    'cultures:cultureparcelle_create', 'cultures:activite_list', 'cultures:activite_create',
    'stocks:dashboard', 'stocks:produit_list', 'stocks:produit_create', 'stocks:mouvement_list',
    'stocks:entree_create', 'stocks:sortie_create', 'finances:transaction_list', 'finances:transaction_create',
    'finances:transaction_export', 'taches:board', 'taches:tache_create', 'personnel:staff_list',
    'personnel:staff_create', 'dashboard:alertes', 'dashboard:rapports', 'dashboard:rapports_export',
]
EMPLOYEE_OK = {'cheptel:animal_add', 'stocks:entree_create', 'stocks:sortie_create', 'taches:tache_create'}


class PagesRenderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', verbosity=0)

    def _walk(self, username, skip_admin=False):
        self.client.force_login(User.objects.get(username=username))
        for name in PAGES:
            if skip_admin and ((name.endswith('_create') and name not in EMPLOYEE_OK) or name.startswith(('finances:', 'personnel:'))):
                continue
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 200, f'{username} {name}')
            if r['Content-Type'].startswith('text/html'):
                self.assertNotContains(r, 'Traceback')

    def test_visitor_sees_everything(self):
        self._walk('demo_visiteur')

    def test_admin_sees_everything(self):
        self._walk('demo_gerant')

    def test_employee_pages(self):
        self._walk('demo_employe', skip_admin=True)

    def test_public_pages(self):
        self.assertContains(self.client.get('/'), 'Essayer la démo')
        self.assertEqual(self.client.get(reverse('accounts:login')).status_code, 200)

    def test_no_emoji_in_rendered_pages(self):
        import re
        emo = re.compile('[\U0001F000-\U0001FAFF☀-➿⬀-⯿]')
        self.client.force_login(User.objects.get(username='demo_visiteur'))
        for name in PAGES:
            if name.endswith('export') or name.endswith('rapports_export'):
                continue
            self.assertIsNone(emo.search(self.client.get(reverse(name)).content.decode()), name)

    def test_demo_login_flow(self):
        r = self.client.post(reverse('core:demo_login'))
        self.assertRedirects(r, reverse('dashboard:home'))
        self.assertEqual(self.client.get(reverse('dashboard:home')).status_code, 200)
