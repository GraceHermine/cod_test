import unittest
from unittest.mock import MagicMock, patch
from customer.models import Commande, Customer
from client.views import avis, commande_detail, evaluation, profil, commande, parametre, invoice_pdf, souhait, suivie_commande
from shop.models import CategorieEtablissement, CategorieProduit, Etablissement, Produit, Favorite
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

class ProfilLogicTest(unittest.TestCase):
    """Tests unitaires purs des vues client"""

    def setUp(self):
        # --- Fake user + customer ---
        self.mock_user = MagicMock()
        self.mock_customer = MagicMock()
        self.mock_user.customer = self.mock_customer

        # --- Fake request ---
        self.request = MagicMock()
        self.request.user = self.mock_user
        self.request.method = 'GET'
        self.request.GET = {}

    # ---------- VUE : PROFIL ----------

    @patch('client.views.render')
    @patch('client.views.Commande')
    def test_profil_logic_success(self, mock_commande, mock_render):
        """Le customer existe et seules 5 commandes sont envoyées"""

        mock_orders = [MagicMock() for _ in range(10)]

        # Simule : Commande.objects.filter(...).order_by(...)[:5]
        mock_commande.objects.filter.return_value.order_by.return_value = mock_orders[:5]

        profil(self.request)

        mock_render.assert_called_once()

        context = mock_render.call_args[0][2]

        self.assertEqual(len(context['dernieres_commandes']), 5)
        self.assertEqual(context['customer'], self.mock_customer)

    @patch('client.views.redirect')
    def test_profil_logic_except_redirect(self, mock_redirect):
        """L'utilisateur n'a pas de customer"""

        # Supprime l'attribut pour déclencher l'exception
        del self.mock_user.customer

        profil(self.request)

        mock_redirect.assert_called_once_with('index')

    # ---------- VUE : COMMANDE ----------

    @patch('client.views.render')
    @patch('client.views.Commande')
    def test_commande_search_query_logic(self, mock_commande, mock_render):
        """Recherche avec paramètre q"""

        self.request.GET = {'q': 'chaussures'}

        mock_qs = MagicMock()
        mock_commande.objects.filter.return_value.order_by.return_value = mock_qs

        commande(self.request)

        self.assertTrue(mock_commande.objects.filter.called)
        mock_render.assert_called_once()


    @patch('client.views.render')
    @patch('client.views.ProduitPanier')
    @patch('client.views.Commande')
    def test_commande_data_formatting_loop(self, mock_commande, mock_pp, mock_render):

        # Une fausse commande
        mock_commande_instance = MagicMock()
        mock_commande.objects.filter.return_value.order_by.return_value = [mock_commande_instance]

        # Simule filter().select_related()
        mock_qs = MagicMock()
        mock_qs.select_related.return_value = []
        mock_pp.objects.filter.return_value = mock_qs

        commande(self.request)

        context = mock_render.call_args[0][2]
        self.assertIn('commandes_data', context)

    # ---------- VUE : PARAMETRE ----------

    @patch('client.views.redirect')
    def test_parametre_post_save_logic(self, mock_redirect):
        """POST : sauvegarde des données"""

        self.request.method = 'POST'
        self.request.POST = {
            'first_name': 'Jean',
            'last_name': 'Test',
            'contact': '01020304',
            'city': '',
            'address': 'Rue test'
        }

        self.mock_user.save = MagicMock()
        self.mock_customer.save = MagicMock()

        parametre(self.request)

        self.assertTrue(self.mock_user.save.called)
        self.assertTrue(self.mock_customer.save.called)
        mock_redirect.assert_called_once_with('parametre')

    # ---------- VUE : INVOICE_PDF ----------

    @patch('client.views.redirect')
    @patch('client.views.get_object_or_404')
    def test_invoice_pdf_security_check(self, mock_get_obj, mock_redirect):
        """Blocage accès facture si ce n'est pas le bon client"""

        mock_order = MagicMock()
        mock_order.customer_id = 99
        mock_get_obj.return_value = mock_order

        self.mock_customer.id = 1

        invoice_pdf(self.request, order_id=10)

        mock_redirect.assert_called_once_with('commande')


    @patch('client.views.render')
    @patch('client.views.ProduitPanier')
    @patch('client.views.get_object_or_404')
    def test_commande_detail_success(self, mock_get_object, mock_produitpanier, mock_render):
        # Mock du rendu pour éviter TemplateDoesNotExist et NoReverseMatch
        mock_render.return_value = MagicMock()

        # Simuler la commande et les produits
        commande = MagicMock()
        commande.id = 1  # <- important pour ne pas casser {% url 'invoice_pdf' %}
        mock_get_object.return_value = commande
        produits_commande = ['prod1', 'prod2']
        mock_produitpanier.objects.filter.return_value.select_related.return_value = produits_commande

        response = commande_detail(self.request, commande_id=1)

        # Vérifier que render est appelé avec le bon contexte
        mock_render.assert_called_once()
        context = mock_render.call_args[0][2]
        assert context['commande'] == commande
        assert context['produits_commande'] == produits_commande

    def test_commande_detail_no_customer(self):
        # L'user n'a pas de customer
        del self.mock_user.customer

        response = commande_detail(self.request, commande_id=1)
        # Vérifier que la redirection vers 'index' se fait
        self.assertEqual(response.status_code, 302)


    @patch('client.views.render')
    def test_suivie_commande_success(self, mock_render):
        # Simuler le retour de render
        mock_render.return_value = MagicMock()
        
        self.mock_user.customer = MagicMock()
        response = suivie_commande(self.request)
        
        # Vérifier que render a été appelé
        mock_render.assert_called_once()
        context = mock_render.call_args[0][2]
        self.assertIn('customer', context)


    def test_suivie_commande_no_customer(self):
        del self.mock_user.customer
        response = suivie_commande(self.request)
        self.assertEqual(response.status_code, 302)


    @patch('client.views.Favorite')
    @patch('client.views.render')
    def test_souhait_success(self, mock_render, mock_favorite):
        # Simuler render
        mock_render.return_value = MagicMock()
        
        # Utiliser le bon utilisateur mock
        self.mock_user.customer = MagicMock()
        
        favoris = ['f1', 'f2']
        mock_favorite.objects.filter.return_value.select_related.return_value = favoris

        response = souhait(self.request)

        # Vérifier que render est appelé avec le bon contexte
        mock_render.assert_called_once()
        context = mock_render.call_args[0][2]
        self.assertEqual(context['favoris'], favoris)


    def test_souhait_no_customer(self):
        del self.mock_user.customer
        response = souhait(self.request)
        self.assertEqual(response.status_code, 302)


    @patch('client.views.render')
    def test_avis_success(self, mock_render):
        # Mock du rendu pour éviter TemplateDoesNotExist ou NoReverseMatch
        mock_render.return_value = MagicMock()

        response = avis(self.request)

        # Vérifier que render a été appelé et que le contexte contient le customer
        mock_render.assert_called_once()
        context = mock_render.call_args[0][2]
        assert 'customer' in context
        assert context['customer'] == self.mock_customer


    def test_avis_no_customer(self):
        del self.mock_user.customer
        response = avis(self.request)
        self.assertEqual(response.status_code, 302)


    @patch('client.views.render')
    def test_evaluation_success(self, mock_render):
        # Mock du rendu pour éviter TemplateDoesNotExist
        mock_render.return_value = MagicMock()

        response = evaluation(self.request)

        # Vérifier que render a été appelé
        mock_render.assert_called_once()
        context = mock_render.call_args[0][2]  # le contexte passé à render
        assert 'customer' in context
        assert context['customer'] == self.mock_customer


# LES TESTS FONCTIONELS DE L'APPLICATION CLIENT

@pytest.mark.django_db
class TestCustomerFonctionnel:
    """
    Tests fonctionnels complets pour l'espace client (customer).
    Vérifie tous les comportements demandés : accès, redirection, contenu, sécurité.
    """

    # Fixtures au niveau de la classe (disponibles pour tous les tests)

    @pytest.fixture()
    def client(self, client):
        """Le client de test (fourni par pytest-django)."""
        return client

    @pytest.fixture()
    def categorie_etab(self, db):
        """Catégorie d'établissement commune."""
        return CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie pour les tests"
        )

    @pytest.fixture
    def user_and_customer(db):
        user = User.objects.create_user(
            username="client_test",
            password="password123",
            email="client@test.com",
            first_name="Jean",
            last_name="Client"
        )
        customer = Customer.objects.create(
            user=user,
            adresse="123 Rue Test",
            contact_1="0000000000",
            photo=SimpleUploadedFile("photo.jpg", b"file_content", content_type="image/jpeg")
        )
        return user, customer


    @pytest.fixture()
    def other_user_and_customer(self, db):
        """Autre utilisateur pour tester la sécurité."""
        other_user = User.objects.create_user(
            username="autre_client",
            password="password123",
            email="autre@test.com"
        )
        other_customer = Customer.objects.create(
            user=other_user,
            adresse="456 Rue Autre",
            contact_1="1111111111",
            photo=SimpleUploadedFile("photo2.jpg", b"")
        )
        return other_user, other_customer

    @pytest.fixture
    def etablissement_and_categories(db, user_and_customer, categorie_etab):
        user, customer = user_and_customer
        etablissement = Etablissement.objects.create(
            user=user,
            nom="Boutique Test",
            description="Description pour les tests",
            logo=SimpleUploadedFile("logo.jpg", b"file_content", content_type="image/jpeg"),
            couverture=SimpleUploadedFile("couv.jpg", b"file_content", content_type="image/jpeg"),
            categorie=categorie_etab,
            adresse="123 Rue Test",
            pays="France",
            contact_1="0000000000",
            email="boutique@test.com",
            nom_du_responsable="Dupont",
            prenoms_duresponsable="Hermine",
        )
        categorie_produit = CategorieProduit.objects.create(
            nom="Électronique",
            description="Catégorie test",
            categorie=categorie_etab,
        )
        produit = Produit.objects.create(
            nom="Produit Favori",
            slug="produit-favori",
            prix=1000,
            description="Test",
            description_deal="Deal",
            prix_promotionnel=800,
            etablissement=etablissement,
            categorie=categorie_produit,
        )
        # Favori pour l'utilisateur principal
        Favorite.objects.create(user=user, produit=produit)
        # Commandes
        commande_user = Commande.objects.create(
            customer=customer,  # ← Utiliser directement le customer de la fixture
            prix_total=1500,
            id_paiment="PAIEMENT123",
            status=True
        )
        # Création d'un autre utilisateur et customer pour les tests de sécurité
        other_user = User.objects.create_user(
            username="autre_client",
            password="password123",
            email="autre@test.com"
        )
        other_customer = Customer.objects.create(
            user=other_user,
            adresse="456 Rue Autre",
            contact_1="1111111111",
            photo=SimpleUploadedFile("photo2.jpg", b"file_content", content_type="image/jpeg")
        )
        commande_autre = Commande.objects.create(
            customer=other_customer,
            prix_total=800,
            id_paiment="PAIEMENT999",
            status=True
        )
        return {
            "etablissement": etablissement,
            "categorie_produit": categorie_produit,
            "produit": produit,
            "commande_user": commande_user,
            "commande_autre": commande_autre,
        }

    # =========================
    # 1️⃣ PROFIL
    # =========================

    def test_profil_connecte(self, user_and_customer):
        user, _ = user_and_customer
        self.client.force_login(user)
        response = self.client.get(reverse("profil"))
        assert response.status_code == 200
        content = response.content.decode()
        assert user.username in content or "Profil" in content or "client_test" in content

    def test_profil_anonyme_redirection(self):
        response = self.client.get(reverse("profil"))
        assert response.status_code == 302
        assert "login" in response.url.lower()

    # =========================
    # 2️⃣ COMMANDE (liste)
    # =========================

    def test_commande_connecte_avec_commandes(client, user_and_customer):
        user, customer = user_and_customer
        Commande.objects.create(
            customer=customer,
            prix_total=1500,
            id_paiment="PAIEMENT123",
            status=True
        )
        client.force_login(user)
        response = client.get(reverse("commande"))
        assert response.status_code == 200
        assert "1500" in response.content.decode()



    def test_commande_connecte_sans_commandes(self, user_and_customer):
        user, _ = user_and_customer
        Commande.objects.filter(customer__user=user).delete()
        self.client.force_login(user)
        response = self.client.get(reverse("commande"))
        assert response.status_code == 200
        content = response.content.decode().lower()
        assert "aucune commande" in content or "pas de commande" in content or "vide" in content

    def test_commande_anonyme_redirection(self):
        response = self.client.get(reverse("commande"))
        assert response.status_code == 302
        assert "login" in response.url.lower()

    # =========================
    # 3️⃣ COMMANDE DETAIL
    # =========================

    def test_commande_detail_appartenant_utilisateur(client, user_and_customer, etablissement_and_categories):
        user, _ = user_and_customer
        commande_user = etablissement_and_categories["commande_user"]
        client.force_login(user)
        response = client.get(reverse("commande-detail", args=[commande_user.id]))
        assert response.status_code == 200


    def test_commande_detail_autre_utilisateur(client, user_and_customer, etablissement_and_categories):
        user, _ = user_and_customer
        commande_autre = etablissement_and_categories["commande_autre"]
        client.force_login(user)
        response = client.get(reverse("commande-detail", args=[commande_autre.id]))
        assert response.status_code in [403, 404]

    def test_commande_detail_inexistante(self, user_and_customer):
        user, _ = user_and_customer
        self.client.force_login(user)
        response = self.client.get(reverse("commande-detail", args=[999999]))
        assert response.status_code == 404

    def test_commande_detail_anonyme_redirection(self):
        response = self.client.get(reverse("commande-detail", args=[1]))
        assert response.status_code == 302
        assert "login" in response.url.lower()

    # =========================
    # 4️⃣ LISTE SOUHAIT (FAVORIS)
    # =========================

    def test_liste_souhait_connecte_avec_favoris(client, user_and_customer, etablissement_and_categories):
        user, _ = user_and_customer
        produit = etablissement_and_categories["produit"]
        client.force_login(user)
        response = client.get(reverse("liste-souhait"))
        assert response.status_code == 200
        assert produit.nom in response.content.decode()

    def test_liste_souhait_connecte_sans_favoris(self, user_and_customer):
        user, _ = user_and_customer
        Favorite.objects.filter(user=user).delete()
        self.client.force_login(user)
        response = self.client.get(reverse("liste-souhait"))
        assert response.status_code == 200
        content = response.content.decode().lower()
        assert "aucun" in content or "vide" in content or "pas de favori" in content

    def test_liste_souhait_anonyme_redirection(self):
        response = self.client.get(reverse("liste-souhait"))
        assert response.status_code == 302
        assert "login" in response.url.lower()

    # =========================
    # 5️⃣ PARAMÈTRE
    # =========================

    def test_parametre_connecte(self, user_and_customer):
        user, _ = user_and_customer
        self.client.force_login(user)
        response = self.client.get(reverse("parametre"))
        assert response.status_code == 200

    def test_parametre_anonyme_redirection(self):
        response = self.client.get(reverse("parametre"))
        assert response.status_code == 302
        assert "login" in response.url.lower()

    def test_parametre_modification_valide(self, user_and_customer):
        user, _ = user_and_customer
        self.client.force_login(user)
        new_email = "nouveau@email.com"
        response = self.client.post(reverse("parametre"), {
            "email": new_email,
            # Ajoute d'autres champs si ton formulaire en a
        }, follow=True)
        assert response.status_code == 200
        user.refresh_from_db()
        # Si la vue met à jour l'email ou affiche un message
        assert user.email == new_email or "modifié" in response.content.decode().lower()

    # =========================
    # 6️⃣ RECEIPT / FACTURE PDF
    # =========================

    def test_receipt_commande_appartenant_utilisateur(client, user_and_customer, etablissement_and_categories):
        user, _ = user_and_customer
        commande_user = etablissement_and_categories["commande_user"]
        client.force_login(user)
        response = client.get(reverse("invoice_pdf", args=[commande_user.id]))
        assert response.status_code == 200
        assert "pdf" in response["Content-Type"].lower()

    def test_receipt_commande_inexistante(self, user_and_customer):
        user, _ = user_and_customer
        self.client.force_login(user)
        response = self.client.get(reverse("invoice_pdf", args=[999999]))
        assert response.status_code == 404

    def test_receipt_commande_autre_utilisateur(client, user_and_customer, etablissement_and_categories):
        user, _ = user_and_customer
        commande_autre = etablissement_and_categories["commande_autre"]
        client.force_login(user)
        response = client.get(reverse("invoice_pdf", args=[commande_autre.id]))
        assert response.status_code in [403, 404]

    def test_receipt_anonyme_redirection(self):
        response = self.client.get(reverse("invoice_pdf", args=[1]))
        assert response.status_code == 302
        assert "login" in response.url.lower()


@pytest.mark.django_db
class TestIntegration:


    # =========================
    # FIXTURES
    # =========================
    @pytest.fixture
    def categorie_etab(db):
        return CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie test"
        )

    @pytest.fixture
    def user_and_customer(db):
        user = User.objects.create_user(
            username="client_test",
            password="password123",
            email="client@test.com"
        )
        customer = Customer.objects.create(
            user=user,
            adresse="123 Rue Test",
            contact_1="0000000000",
            photo=SimpleUploadedFile("photo.jpg", b"file_content", content_type="image/jpeg")
        )
        return user, customer

    @pytest.fixture
    def other_user_and_customer(db):
        other_user = User.objects.create_user(
            username="autre_client",
            password="password123",
            email="autre@test.com"
        )
        other_customer = Customer.objects.create(
            user=other_user,
            adresse="456 Rue Autre",
            contact_1="1111111111",
            photo=SimpleUploadedFile("photo2.jpg", b"file_content", content_type="image/jpeg")
        )
        return other_user, other_customer

    @pytest.fixture
    def etablissement_and_produit(db, user_and_customer, categorie_etab):
        user, customer = user_and_customer

        etablissement = Etablissement.objects.create(
            user=user,
            nom="Boutique Test",
            description="Description test",
            logo=SimpleUploadedFile("logo.jpg", b"file_content", content_type="image/jpeg"),
            couverture=SimpleUploadedFile("couv.jpg", b"file_content", content_type="image/jpeg"),
            categorie=categorie_etab,
            adresse="123 Rue Test",
            pays="France",
            contact_1="0000000000",
            email="boutique@test.com",
            nom_du_responsable="Dupont",
            prenoms_duresponsable="Hermine",
        )

        categorie_produit = CategorieProduit.objects.create(
            nom="Électronique",
            description="Catégorie test",
            categorie=categorie_etab,
        )

        produit = Produit.objects.create(
            nom="Produit Favori",
            slug="produit-favori",
            prix=1000,
            description="Description produit",
            description_deal="Deal test",
            prix_promotionnel=800,
            etablissement=etablissement,
            categorie=categorie_produit,
        )

        # Favori pour l'utilisateur
        Favorite.objects.create(user=user, produit=produit)

        # Commande pour l'utilisateur
        commande = Commande.objects.create(
            customer=customer,
            prix_total=1500,
            id_paiment="PAIEMENT123",
            status=True
        )

        return {
            "etablissement": etablissement,
            "categorie_produit": categorie_produit,
            "produit": produit,
            "commande": commande
        }

    @pytest.fixture
    def commande_autre_user(other_user_and_customer):
        other_user, other_customer = other_user_and_customer
        return Commande.objects.create(
            customer=other_customer,
            prix_total=800,
            id_paiment="PAIEMENT999",
            status=True
        )

    # =========================
    # TEST D’INTÉGRATION
    # =========================
    @pytest.mark.django_db
    def test_flux_complet_client(client, user_and_customer, etablissement_and_produit, other_user_and_customer, commande_autre_user):
        user, customer = user_and_customer
        produit = etablissement_and_produit["produit"]
        commande = etablissement_and_produit["commande"]
        other_user, other_customer = other_user_and_customer
        commande_autre = commande_autre_user

        # 1️⃣ Connexion utilisateur
        client.force_login(user)

        # 2️⃣ Accès au profil
        response = client.get(reverse("profil"))
        assert response.status_code == 200
        assert user.username in response.content.decode()

        # 3️⃣ Liste des commandes
        response = client.get(reverse("commande"))
        assert response.status_code == 200
        content = response.content.decode()
        assert str(commande.prix_total) in content

        # 4️⃣ Détail de la commande (propre)
        response = client.get(reverse("commande-detail", args=[commande.id]))
        assert response.status_code == 200
        assert str(commande.id) in response.content.decode()

        # 5️⃣ Détail de la commande (autre utilisateur → interdit)
        response = client.get(reverse("commande-detail", args=[commande_autre.id]))
        assert response.status_code in [403, 404]

        # 6️⃣ Téléchargement facture PDF (propre)
        response = client.get(reverse("invoice_pdf", args=[commande.id]))
        assert response.status_code == 200
        assert "pdf" in response["Content-Type"].lower()

        # 7️⃣ Téléchargement facture PDF (autre utilisateur → interdit)
        response = client.get(reverse("invoice_pdf", args=[commande_autre.id]))
        assert response.status_code in [403, 404]

        # 8️⃣ Liste de souhaits / favoris
        response = client.get(reverse("liste-souhait"))
        assert response.status_code == 200
        content = response.content.decode()
        assert produit.nom in content

        # 9️⃣ Modification des paramètres
        new_email = "nouveau@email.com"
        response = client.post(reverse("parametre"), {"email": new_email}, follow=True)
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email == new_email

        # 🔟 Cas limites : commande inexistante
        response = client.get(reverse("commande-detail", args=[999999]))
        assert response.status_code == 404
        response = client.get(reverse("invoice_pdf", args=[999999]))
        assert response.status_code == 404

        # 1️⃣1️⃣ Accès anonyme → redirection login
        client.logout()
        response = client.get(reverse("profil"))
        assert response.status_code == 302 and "login" in response.url.lower()
        response = client.get(reverse("commande"))
        assert response.status_code == 302 and "login" in response.url.lower()
        response = client.get(reverse("liste-souhait"))
        assert response.status_code == 302 and "login" in response.url.lower()
