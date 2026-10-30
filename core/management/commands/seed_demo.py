"""
Génère une ferme de démonstration entièrement fictive (idempotent).

    python manage.py seed_demo            # recrée la ferme de démo
    python manage.py seed_demo --keep     # ne fait rien si elle existe déjà

Les dates sont relatives à aujourd'hui : relancer la commande rafraîchit les données.
Le compte visiteur n'a pas de mot de passe utilisable (connexion via /demo/ uniquement).
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Ferme, User
from cheptel.models import (Animal, ComptageOeufs, Espece, LotPondeuses, Produit,
                            RapportJournalier, Traitement)
from cultures.models import ActiviteAgricole, Culture, CultureParcelle, Parcelle
from finances.models import Transaction
from stocks.models import MouvementStock, ProduitStock
from taches.models import Tache
from stocks.services import StockService

DEMO_EMAIL = 'demo@fermeapp.example'


class Command(BaseCommand):
    help = 'Crée la ferme de démonstration fictive.'

    def add_arguments(self, parser):
        parser.add_argument('--keep', action='store_true', help='Ne rien faire si la démo existe.')

    @transaction.atomic
    def handle(self, *args, **opts):
        old = Ferme.objects.filter(email=DEMO_EMAIL).first()
        if old and opts['keep']:
            self.stdout.write('Démo déjà présente, rien à faire.')
            return
        if old:
            MouvementStock.objects.filter(produit__ferme=old).delete()  # FK PROTECT
            old.delete()
        rnd = random.Random(2026)
        today = timezone.localdate()

        ferme = Ferme.objects.create(nom='Ferme Les Collines (démo)', localisation='Abomey-Calavi, Bénin',
                                     email=DEMO_EMAIL, telephone='+229 00 00 00 00')
        admin = User(username='demo_gerant', role='ADMIN', ferme=ferme, first_name='Awa', last_name='Gérante')
        admin.set_unusable_password(); admin.save()
        visiteur = User(username=settings.DEMO_VISITOR_USERNAME, role='VISITEUR', ferme=ferme,
                        first_name='Visiteur', last_name='Démo')
        visiteur.set_unusable_password(); visiteur.save()
        emp = User(username='demo_employe', role='EMPLOYE', ferme=ferme, first_name='Koffi', last_name='Soigneur')
        emp.set_unusable_password(); emp.save()

        # ── Cheptel ────────────────────────────────────────
        esp = {n: Espece.objects.get_or_create(nom=n)[0] for n in
               ['Poule pondeuse', 'Poulet de chair', 'Caprin', 'Porc', 'Lapin']}
        lots = [
            LotPondeuses.objects.create(ferme=ferme, nom='Lot A - Pondeuses', espece=esp['Poule pondeuse'],
                                        nombre_sujets=420, date_mise_en_place=today - timedelta(days=240),
                                        race='ISA Brown', createur=admin),
            LotPondeuses.objects.create(ferme=ferme, nom='Lot B - Pondeuses', espece=esp['Poule pondeuse'],
                                        nombre_sujets=310, date_mise_en_place=today - timedelta(days=150),
                                        race='Lohmann', createur=admin),
            LotPondeuses.objects.create(ferme=ferme, nom='Lot C - Chair', espece=esp['Poulet de chair'],
                                        nombre_sujets=250, date_mise_en_place=today - timedelta(days=28),
                                        race='Cobb 500', createur=admin),
        ]
        animaux = []
        spec = [('Caprin', 'Djallonké', 'CAP', 14), ('Porc', 'Large White', 'POR', 8), ('Lapin', 'Néo-zélandais', 'LAP', 8)]
        for nom_esp, race, pre, n in spec:
            for i in range(1, n + 1):
                statut = 'ACTIF' if i % 7 else 'VENDU'
                animaux.append(Animal.objects.create(
                    identifiant=f'DEMO-{pre}-{i:03d}', nom='', ferme=ferme, espece=esp[nom_esp], race=race,
                    sexe='F' if i % 3 else 'M', statut=statut,
                    date_naissance=today - timedelta(days=rnd.randint(150, 900)), createur=admin))

        vaccin = [Produit.objects.get_or_create(nom=n)[0] for n in
                  ['Vaccin Newcastle', 'Vaccin Gumboro', 'Antiparasitaire (ivermectine)', 'Vitamines AD3E', 'Antibiotique large spectre']]
        actifs = [a for a in animaux if a.statut == 'ACTIF']
        for k in range(26):
            a = rnd.choice(actifs)
            d = today - timedelta(days=rnd.randint(2, 170))
            t = rnd.choice(['VACCIN', 'TRAITEMENT', 'TRAITEMENT', 'MALADIE'])
            rappel = d + timedelta(days=rnd.choice([21, 30, 90, 180])) if t == 'VACCIN' else None
            Traitement.objects.create(animal=a, ferme=ferme, type=t, date=d, produit=rnd.choice(vaccin),
                                      dose=rnd.choice(['0,5 ml', '1 ml', '2 ml', '1 dose']),
                                      rappel_le=rappel, operateur=emp)
        # Quelques rappels à venir pour alimenter les alertes
        for a, delta in zip(actifs[:3], (3, 9, 18)):
            Traitement.objects.create(animal=a, ferme=ferme, type='VACCIN', date=today - timedelta(days=60),
                                      produit=vaccin[0], dose='1 dose', rappel_le=today + timedelta(days=delta),
                                      operateur=emp)

        # ── Rapports journaliers et comptages d'œufs ──────
        for back in range(0, 120):
            d = today - timedelta(days=back)
            oeufs = 0
            for lot, base in ((lots[0], 360), (lots[1], 270)):
                n = max(0, int(base * rnd.uniform(0.88, 0.98) - back * 0.15))
                oeufs += n
                if back < 75:
                    ComptageOeufs.objects.create(lot=lot, date=d, nombre=n, createur=emp)
            RapportJournalier.objects.create(
                ferme=ferme, date=d, nombre_morts=rnd.choice([0, 0, 0, 0, 1, 2]), oeufs_pondus=oeufs,
                aliment_kg=Decimal(rnd.randint(85, 110)), eau_litres=Decimal(rnd.randint(180, 260)),
                sujets_malades=rnd.choice([0, 0, 0, 1, 3, 5]), createur=emp)

        # ── Stocks (mouvements chronologiques) ─────────────
        prods = {
            'Aliment pondeuse': ('KG', 'Magasin 1', 600, 400, 330),
            'Aliment poulet de chair': ('KG', 'Magasin 1', 500, 250, 350),
            'Maïs concassé': ('KG', 'Magasin 2', 300, 150, 260),
            'Vaccins Newcastle': ('UNITE', 'Réfrigérateur', 20, 15, 1500),
            'Semences de maïs': ('KG', 'Magasin 2', 50, 20, 900),
            'Engrais NPK': ('SAC', 'Magasin 2', 8, 6, 18500),
        }
        stock_objs = {}
        for nom, (u, emp_, seuil, init, prix) in prods.items():
            stock_objs[nom] = ProduitStock.objects.create(
                ferme=ferme, nom=nom, unite=u, emplacement=emp_, seuil_alerte=Decimal(seuil),
                fournisseur_principal='Agri-Sud Cotonou', prix_moyen_unitaire=Decimal(prix))
        events = []
        for nom, p in stock_objs.items():
            init = prods[nom][3]
            events.append((today - timedelta(days=170), p, 'ENTREE', Decimal(init * 2), 'Stock initial'))
            for w in range(24):
                d = today - timedelta(days=165 - w * 7)
                if rnd.random() < 0.9:
                    events.append((d, p, 'SORTIE', Decimal(init * Decimal('0.18')).quantize(Decimal('1')), 'Consommation'))
                if w % 5 == 4:
                    events.append((d, p, 'ENTREE', Decimal(init), 'Réapprovisionnement'))
        for d, p, typ, q, motif in sorted(events, key=lambda e: e[0]):
            try:
                StockService.creer_mouvement(p.id, typ, q, emp, date=d, motif=motif,
                                             prix_unitaire=p.prix_moyen_unitaire if typ == 'ENTREE' else None)
            except ValueError:
                pass
        # Deux produits sous le seuil d'alerte
        for nom in ('Aliment poulet de chair', 'Engrais NPK'):
            p = ProduitStock.objects.get(ferme=ferme, nom=nom)
            reste = p.quantite_actuelle - p.seuil_alerte + Decimal(1)
            if reste > 0:
                StockService.creer_mouvement(p.id, 'SORTIE', reste, emp, date=today, motif='Consommation')

        # ── Cultures ──────────────────────────────────────
        cult = {n: Culture.objects.get_or_create(nom=n)[0] for n in ['Maïs', 'Soja', 'Manioc', 'Tomate', 'Piment']}
        parcelles = [Parcelle.objects.create(ferme=ferme, nom=n, superficie=Decimal(s), type_sol=sol,
                                             localisation=loc) for n, s, sol, loc in [
            ('Parcelle Nord', '2.50', 'Argilo-sableux', 'Près du forage'),
            ('Parcelle Est', '1.80', 'Sableux', 'Côté route'),
            ('Parcelle Sud', '3.20', 'Argileux', 'Bas-fond'),
            ('Potager', '0.60', 'Limoneux', 'Derrière les bâtiments')]]
        cps = []
        plan = [(0, 'Maïs', 150, 70), (1, 'Soja', 110, 25), (2, 'Manioc', 260, 60), (3, 'Tomate', 70, 12)]
        for pi, c, ago, to_harvest in plan:
            semis = today - timedelta(days=ago)
            prevue = semis + timedelta(days=ago + (to_harvest if ago < 120 else 0) - (ago - 100 if ago >= 120 else 0))
            reelle = semis + timedelta(days=105) if c == 'Maïs' else None
            cps.append(CultureParcelle.objects.create(
                parcelle=parcelles[pi], culture=cult[c], date_semis=semis, date_recolte_prevue=max(prevue, semis + timedelta(days=60)),
                date_recolte_reelle=reelle, rendement=Decimal(4800) if reelle else None))
        types = ['LABOUR', 'SEMIS', 'IRRIGATION', 'FERTILISATION', 'DESHERBAGE', 'TRAITEMENT']
        for cp in cps:
            for k, tp in enumerate(types):
                d = cp.date_semis + timedelta(days=k * 9)
                if d <= today:
                    ActiviteAgricole.objects.create(culture_parcelle=cp, type=tp, date=d, operateur=emp,
                                                    description=f'{dict(ActiviteAgricole.TYPES)[tp]} - {cp.parcelle.nom}',
                                                    intrants_utilises='NPK' if tp == 'FERTILISATION' else '')
            if cp.date_recolte_reelle:
                ActiviteAgricole.objects.create(culture_parcelle=cp, type='RECOLTE', date=cp.date_recolte_reelle,
                                                operateur=emp, description='Récolte principale')

        # ── Finances (12 mois) ────────────────────────────
        tx = []
        for m in range(12):
            base = today - timedelta(days=30 * m)
            for k in range(rnd.randint(8, 12)):
                d = base - timedelta(days=rnd.randint(0, 27))
                tx.append(('RECETTE', 'VENTE_OEUFS', rnd.randint(140, 210) * 1000, d, 'Vente d\'œufs - alvéoles', rnd.choice(['Marché Dantokpa', 'Restaurant Le Palmier', 'Grossiste Houénou'])))
            tx.append(('RECETTE', 'VENTE_ANIMAUX', rnd.randint(2, 5) * 45000, base - timedelta(days=rnd.randint(0, 25)), 'Vente de caprins', 'Particulier'))
            if m % 3 == 1:
                tx.append(('RECETTE', 'VENTE_RECOLTE', rnd.randint(220, 380) * 1000, base - timedelta(days=5), 'Vente de maïs', 'Coopérative locale'))
            tx.append(('DEPENSE', 'ALIMENT', rnd.randint(380, 470) * 1000, base - timedelta(days=rnd.randint(0, 6)), 'Achat aliments volaille', 'Agri-Sud Cotonou'))
            tx.append(('DEPENSE', 'SALAIRES', 180000, base - timedelta(days=2), 'Salaires du personnel', ''))
            tx.append(('DEPENSE', 'SANTE', rnd.randint(15, 60) * 1000, base - timedelta(days=rnd.randint(8, 20)), 'Vaccins et médicaments', 'Pharmacie vétérinaire'))
            tx.append(('DEPENSE', 'TRANSPORT', rnd.randint(20, 40) * 1000, base - timedelta(days=rnd.randint(8, 20)), 'Transport livraisons', ''))
            if m % 4 == 0:
                tx.append(('DEPENSE', 'MAINTENANCE', rnd.randint(30, 90) * 1000, base - timedelta(days=12), 'Entretien équipements', ''))
            if m % 6 == 0:
                tx.append(('DEPENSE', 'SEMENCES', 85000, base - timedelta(days=15), 'Semences et engrais', 'Agri-Sud Cotonou'))
        Transaction.objects.bulk_create([Transaction(ferme=ferme, type=t, categorie=c, montant=Decimal(a), date=d,
                                                     libelle=l, tiers=ti, createur=admin)
                                         for t, c, a, d, l, ti in tx if d <= today])
        Tache.objects.bulk_create([Tache(ferme=ferme, titre=t, statut=st, priorite=pr, assignee=a, createur=admin,
                                         echeance=today + timedelta(days=d)) for t, st, pr, a, d in [
            ('Vacciner le lot B contre Gumboro', 'A_FAIRE', 'HAUTE', emp, 3),
            ('Commander 50 sacs d\'aliment ponte', 'A_FAIRE', 'NORMALE', admin, 6),
            ('Réparer la clôture de la parcelle Sud', 'EN_COURS', 'NORMALE', emp, 2),
            ('Désherber le potager', 'EN_COURS', 'BASSE', emp, -1),
            ('Inventaire mensuel du magasin', 'TERMINEE', 'NORMALE', admin, -5),
            ('Livraison hebdomadaire d\'œufs', 'TERMINEE', 'HAUTE', emp, -2)]])
        self.stdout.write(self.style.SUCCESS(
            f'Démo prête : ferme « {ferme.nom} », {len(animaux)} animaux, {Transaction.objects.filter(ferme=ferme).count()} transactions.'))
