from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Ferme, User
from cheptel.models import Espece, LotPondeuses


class AccessPolicyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.f1 = Ferme.objects.create(nom='F1', localisation='x', email='f1@x.bj')
        cls.f2 = Ferme.objects.create(nom='F2', localisation='x', email='f2@x.bj')
        cls.admin = User.objects.create_user('adm', password='pw-Test-12345', role='ADMIN', ferme=cls.f1)
        cls.emp = User.objects.create_user('emp', password='pw-Test-12345', role='EMPLOYE', ferme=cls.f1)
        cls.vis = User.objects.create_user('vis', password='pw-Test-12345', role='VISITEUR', ferme=cls.f1)
        cls.admin2 = User.objects.create_user('adm2', password='pw-Test-12345', role='ADMIN', ferme=cls.f2)

    def test_landing_public(self):
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_health(self):
        self.assertEqual(self.client.get('/health/').status_code, 200)

    def test_dashboard_requires_login(self):
        r = self.client.get(reverse('dashboard:home'))
        self.assertEqual(r.status_code, 302)

    def test_employee_blocked_on_edit_delete_and_config(self):
        self.client.force_login(self.emp)
        for name in ['cheptel:lot_create', 'stocks:produit_create', 'cultures:parcelle_create']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403, name)
        self.assertEqual(self.client.get(reverse('cheptel:animal_edit', args=[1])).status_code, 403)
        self.assertEqual(self.client.post(reverse('cheptel:animal_delete', args=[1])).status_code, 403)

    def test_employee_can_use_entry_screens(self):
        self.client.force_login(self.emp)
        for name in ['cheptel:animal_list', 'cheptel:animal_add', 'cheptel:rapport_add',
                     'stocks:entree_create', 'cultures:activite_create', 'dashboard:home']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_visitor_reads_but_cannot_write(self):
        self.client.force_login(self.vis)
        self.assertEqual(self.client.get(reverse('cheptel:animal_list')).status_code, 200)
        from cheptel.models import Animal
        r = self.client.post(reverse('cheptel:animal_add'), {'identifiant': 'Z1', 'sexe': 'F'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Animal.objects.count(), 0)

    def test_admin_other_ferme_gets_404(self):
        esp = Espece.objects.create(nom='Poule')
        lot = LotPondeuses.objects.create(ferme=self.f1, nom='L', espece=esp,
                                          nombre_sujets=10, date_mise_en_place='2026-01-01')
        self.client.force_login(self.admin2)
        self.assertEqual(self.client.get(reverse('cheptel:lot_edit', args=[lot.pk])).status_code, 404)

    def test_demo_login_is_post_only(self):
        self.assertEqual(self.client.get(reverse('core:demo_login')).status_code, 405)
