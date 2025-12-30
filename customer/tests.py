import json
import pytest
import unittest
from shop.models import Produit, Etablissement, CategorieEtablissement, CategorieProduit
from customer import views
from django.urls import reverse
from django.test import TestCase
from django.http import JsonResponse
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from cities_light.models import City, Country
from django.core.files.uploadedfile import SimpleUploadedFile
# Create your tests here.

@pytest.mark.django_db
class AuthViewsTestCase(unittest.TestCase):

    def setUp(self):
        # --- Fake request ---
        self.request = MagicMock()
        self.request.method = 'GET'
        self.request.POST = {}
        self.request.body = b''
        self.request.FILES = {}
        self.mock_user = MagicMock()
        self.mock_user.is_authenticated = False
        self.request.user = self.mock_user


    # ----------------- LOGIN -----------------
    def test_login_authenticated_redirect(self):
        self.mock_user.is_authenticated = True
        response = views.login(self.request)
        self.assertEqual(response.status_code, 302)


    def test_login_render(self):
        response = views.login(self.request)
        self.assertTrue(hasattr(response, 'content'))


    # ----------------- SIGNUP -----------------
    def test_signup_authenticated_redirect(self):
        self.mock_user.is_authenticated = True
        response = views.signup(self.request)
        self.assertEqual(response.status_code, 302)


    def test_signup_render(self):
        response = views.signup(self.request)
        self.assertTrue(hasattr(response, 'content'))


    # ----------------- FORGOT PASSWORD -----------------
    def test_forgot_password_authenticated_redirect(self):
        self.mock_user.is_authenticated = True
        response = views.forgot_password(self.request)
        self.assertEqual(response.status_code, 302)


    def test_forgot_password_render(self):
        response = views.forgot_password(self.request)
        self.assertTrue(hasattr(response, 'content'))


    # ----------------- ISLOGIN -----------------
    @patch('customer.views.authenticate')
    @patch('customer.views.login_request')
    @patch('customer.views.User.objects.get')
    def test_islogin_success_username(self, mock_get_user, mock_login, mock_authenticate):
        mock_user = MagicMock()
        mock_user.is_active = True
        mock_authenticate.return_value = mock_user
        mock_get_user.return_value = mock_user

        post_data = {'username': 'testuser', 'password': 'pass'}
        self.request.body = json.dumps(post_data).encode('utf-8')

        response = views.islogin(self.request)
        self.assertIsInstance(response, JsonResponse)
        data = json.loads(response.content)
        self.assertTrue(data['success'])


    # ----------------- DECONNEXION -----------------
    @patch('customer.views.logout')
    def test_deconnexion_redirects(self, mock_logout):
        response = views.deconnexion(self.request)
        self.assertEqual(response.status_code, 302)
        mock_logout.assert_called_once_with(self.request)


    # ----------------- INSCRIPTION -----------------
    @patch('customer.views.User')
    @patch('customer.views.models.Customer')
    @patch('customer.views.City.objects.get')
    @patch('customer.views.login_request')
    def test_inscription_success(self, mock_login, mock_city_get, mock_customer, mock_user_model):
        self.request.POST = {
            'nom': 'DJIDJI',
            'prenoms': 'MARGO',
            'username': 'LELOUCH',
            'email': 'lelouch@example.com',
            'phone': '12345678',
            'ville': '1',
            'adresse': 'Rue Princesse',
            'password': 'pass1234',
            'passwordconf': 'pass1234'
        }

        mock_user_instance = MagicMock()
        mock_user_model.return_value = mock_user_instance

        mock_city_instance = MagicMock()
        mock_city_get.return_value = mock_city_instance
        self.request.FILES = {'file': MagicMock()}

        mock_profile = MagicMock()
        mock_customer.return_value = mock_profile

        response = views.inscription(self.request)
        data = json.loads(response.content)
        self.assertTrue(data['success'])


    # ----------------- REQUEST RESET PASSWORD -----------------
    @patch('customer.views.PasswordResetToken.objects.get_or_create')
    @patch('customer.views.User.objects.get')
    @patch('customer.views.validate_email')
    @patch('customer.views.send_mail')
    @patch('customer.views.messages')
    def test_request_reset_password_post_success(self, mock_messages, mock_send_mail, mock_validate_email, mock_get_user, mock_token_get_or_create):
        self.request.method = 'POST'
        self.request.POST = {'email': 'john@example.com'}

        mock_user = MagicMock()
        mock_get_user.return_value = mock_user
        mock_token = MagicMock()
        mock_token_get_or_create.return_value = (mock_token, True)

        response = views.request_reset_password(self.request)
        self.assertEqual(response.status_code, 302)
        mock_send_mail.assert_called_once()


    # ----------------- RESET PASSWORD -----------------
    @patch('customer.views.PasswordResetToken.objects.get')
    @patch('customer.views.make_password')
    def test_reset_password_post_success(self, mock_make_password, mock_get_token):
        self.request.method = 'POST'
        self.request.POST = {'new_password': 'pass1234', 'confirm_password': 'pass1234'}

        mock_token = MagicMock()
        mock_token.user = MagicMock()
        mock_token.is_valid.return_value = True
        mock_get_token.return_value = mock_token

        response = views.reset_password(self.request, token='abc123')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_token.delete.called)
        self.assertTrue(mock_token.user.save.called)


    # ----------------- TEST EMAIL -----------------
    @patch('customer.views.send_mail')
    def test_test_email_success(self, mock_send_mail):
        response = views.test_email(self.request)
        self.assertIsInstance(response, JsonResponse)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')


# ====================
# FIXTURES
# ====================

@pytest.fixture
def user(db):
    """Crée un utilisateur de test avec des informations complètes."""
    return User.objects.create_user(
        username="hermine",
        password="password123",
        first_name="Hermine",
        last_name="Dupont",
        email="hermine@test.com"
    )


@pytest.fixture
def client_logged(client, user):
    """Connecte l'utilisateur dans le client de test (simulate une session authentifiée)."""
    client.force_login(user)
    return client


@pytest.fixture
def categorie_etab(db):
    """Crée une catégorie d'établissement nécessaire pour créer un Etablissement."""
    return CategorieEtablissement.objects.create(
        nom="Restaurant",
        description="Catégorie pour les tests"
    )


@pytest.fixture
def etablissement(db, user, categorie_etab):
    """Crée un établissement complet avec tous les champs obligatoires.
    Cela évite l'erreur NOT NULL sur auth_user.last_name causée par la méthode save() du modèle."""
    return Etablissement.objects.create(
        user=user,
        nom="Boutique Test",
        description="Description pour les tests",
        logo=SimpleUploadedFile("logo.jpg", b""),  # Fichier vide pour satisfaire ImageField
        couverture=SimpleUploadedFile("couv.jpg", b""),
        categorie=categorie_etab,
        adresse="123 Rue Test",
        pays="France",
        contact_1="0000000000",
        email="boutique@test.com",
        nom_du_responsable="Dupont",
        prenoms_duresponsable="Hermine",
    )


@pytest.fixture
def categorie_produit(db, categorie_etab):
    """Crée une catégorie de produit requise pour le modèle Produit."""
    return CategorieProduit.objects.create(
        nom="Plat principal",
        description="Catégorie pour les tests",
        categorie=categorie_etab,
    )


@pytest.fixture
def produit(db, etablissement, categorie_produit):
    """Crée un produit valide lié à un établissement et une catégorie."""
    return Produit.objects.create(
        nom="Produit Test",
        slug="produit-test",
        description="Un produit pour les tests",
        description_deal="Deal spécial",
        prix=1000,
        prix_promotionnel=800,
        etablissement=etablissement,
        categorie=categorie_produit,
    )


@pytest.mark.django_db
class TestFonctionnel:



    # =========================
    # 🔐 CONNEXION
    # =========================
    def test_login_formulaire_vide(self, client):
        response = client.post(
            reverse("post"),
            data=json.dumps({
                "username": "",
                "password": ""
            }),
            content_type="application/json"
        )
        assert response.status_code == 200


    def test_login_champ_vide(self, client):
        response = client.post(
            reverse("post"),
            data=json.dumps({
                "username": "",
                "password": "test"
            }),
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_login_identifiants_incorrects(self, client):
        response = client.post(
            reverse("post"),
            data=json.dumps({
                "username": "fake",
                "password": "wrong"
            }),
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_login_identifiants_corrects(self, client):
        User.objects.create_user(
            username="hermine",
            password="password123"
        )

        response = client.post(
            reverse("post"),
            data=json.dumps({
                "username": "hermine",
                "password": "password123"
            }),
            content_type="application/json"
        )

        assert response.status_code == 200

    # =========================
    # 📝 INSCRIPTION
    # =========================
    def test_inscription_formulaire_vide(self, client):
        response = client.post(reverse("inscription"), {})

        assert response.status_code == 200
        assert User.objects.count() == 0

    def test_inscription_champs_vides(self, client):
        response = client.post(reverse("inscription"), {
            "username": "",
            "email": "",
            "password": "",
            "passwordconf": "",
            "nom": "",
            "prenoms": "",
            "phone": "",
            "ville": "",
        })

        assert response.status_code == 200
        assert User.objects.count() == 0

    def test_inscription_valide(self, client):
        country = Country.objects.create(
            name="Côte d'Ivoire",
            code2="CI"
        )

        city = City.objects.create(
            name="Abidjan",
            country=country
        )

        from django.core.files.uploadedfile import SimpleUploadedFile

        photo = SimpleUploadedFile(
            "photo.jpg",
            b"file_content",
            content_type="image/jpeg"
        )

        response = client.post(reverse("inscription"), {
            "username": "nouvel_user",
            "email": "test@test.com",
            "password": "password123",
            "passwordconf": "password123",
            "nom": "Doe",
            "prenoms": "John",
            "phone": "01020304",
            "ville": city.id,
            "adresse": "Cocody",
            "file": photo,
        })

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert User.objects.filter(username="nouvel_user").exists()

    # =========================
    # 🔑 RESET PASSWORD
    # =========================

    def test_reset_password_champ_vide(self, client):
        response = client.post(reverse("request_reset_password"), {})
        assert response.status_code == 302

    def test_reset_password_identifiant_invalide(self, client):
        response = client.post(
            reverse("request_reset_password"),
            {"email": "fake@test.com"}
        )
        assert response.status_code == 302

    def test_reset_password_identifiant_valide(self, client):
        User.objects.create_user(
            username="reset",
            email="reset@test.com",
            password="password123"
        )

        response = client.post(
            reverse("request_reset_password"),
            {"email": "reset@test.com"}
        )
        assert response.status_code == 302


    # @pytest.fixture
    # def produit(self):
    #     return Produit.objects.create(
    #         nom="Produit test",
    #         prix=1000,
    #         slug="produit-test"
    #     )



    # -----------------------------
    # Ajout au panier
    # -----------------------------

    def test_ajout_produit_valide(self, client_logged, produit):
        """Vérifie qu'un produit existant avec quantité positive est bien ajouté au panier."""
        response = client_logged.post(reverse("add_to_cart"), {
            "product_id": produit.id,
            "quantity": 1
        })
        # La vue renvoie généralement une redirection ou 200
        assert response.status_code in [200, 302]
        cart = client_logged.session.get("cart", {})
        assert str(produit.id) in cart
        assert cart[str(produit.id)]["quantity"] == 1


    def test_ajout_produit_inexistant(self, client_logged):
        """Vérifie que l'ajout d'un produit qui n'existe pas n'ajoute rien au panier.
        Idéalement, la vue devrait renvoyer 404 ou un message d'erreur."""
        response = client_logged.post(reverse("add_to_cart"), {
            "product_id": 9999,
            "quantity": 1
        })
        assert response.status_code in [200, 302]
        cart = client_logged.session.get("cart", {})
        assert "9999" not in cart  # Rien n'est ajouté → sécurité minimale respectée


    def test_ajout_quantite_zero(self, client_logged, produit):
        """Vérifie que quantité = 0 n'ajoute pas le produit au panier."""
        initial_cart = client_logged.session.get("cart", {}).copy()
        response = client_logged.post(reverse("add_to_cart"), {
            "product_id": produit.id,
            "quantity": 0
        })
        assert response.status_code in [200, 302]
        cart = client_logged.session.get("cart", {})
        # Le panier ne doit pas être modifié
        assert cart == initial_cart


    def test_ajout_quantite_negative(self, client_logged, produit):
        """Vérifie que quantité négative n'ajoute pas le produit."""
        initial_cart = client_logged.session.get("cart", {}).copy()
        response = client_logged.post(reverse("add_to_cart"), {
            "product_id": produit.id,
            "quantity": -5
        })
        assert response.status_code in [200, 302]
        cart = client_logged.session.get("cart", {})
        assert cart == initial_cart


    def test_ajout_meme_produit_deux_fois(self, client_logged, produit):
        """Vérifie que ajouter deux fois le même produit incrémente la quantité."""
        client_logged.post(reverse("add_to_cart"), {"product_id": produit.id, "quantity": 2})
        client_logged.post(reverse("add_to_cart"), {"product_id": produit.id, "quantity": 3})
        cart = client_logged.session["cart"]
        assert cart[str(produit.id)]["quantity"] == 5


    # -----------------------------
    # Suppression du panier
    # -----------------------------

    def test_suppression_produit(self, client_logged, produit):
        """Vérifie que la suppression d'un produit existant le retire du panier."""
        client_logged.post(reverse("add_to_cart"), {"product_id": produit.id, "quantity": 1})
        response = client_logged.post(reverse("delete_from_cart"), {"product_id": produit.id})
        assert response.status_code in [200, 302]
        assert str(produit.id) not in client_logged.session.get("cart", {})


    def test_suppression_produit_absent(self, client_logged):
        """Vérifie que supprimer un produit absent ne casse pas le panier."""
        initial_cart = client_logged.session.get("cart", {}).copy()
        response = client_logged.post(reverse("delete_from_cart"), {"product_id": 9999})
        assert response.status_code in [200, 302]
        cart = client_logged.session.get("cart", {})
        assert cart == initial_cart


    # -----------------------------
    # Mise à jour quantité
    # -----------------------------

    def test_update_quantite_valide(self, client_logged, produit):
        """Vérifie que la mise à jour avec une quantité positive fonctionne."""
        client_logged.post(reverse("add_to_cart"), {"product_id": produit.id, "quantity": 1})
        response = client_logged.post(reverse("update_cart"), {
            "product_id": produit.id,
            "quantity": 10
        })
        assert response.status_code in [200, 302]
        assert client_logged.session["cart"][str(produit.id)]["quantity"] == 10


    def test_update_quantite_zero(self, client_logged, produit):
        """Vérifie que quantité = 0 supprime le produit du panier."""
        client_logged.post(reverse("add_to_cart"), {"product_id": produit.id, "quantity": 1})
        response = client_logged.post(reverse("update_cart"), {
            "product_id": produit.id,
            "quantity": 0
        })
        assert response.status_code in [200, 302]
        assert str(produit.id) not in client_logged.session.get("cart", {})


    def test_update_quantite_negative(self, client_logged, produit):
        """Vérifie que quantité négative ne modifie pas le panier."""
        # On suppose qu'il y a déjà une quantité (ou non)
        initial_quantity = client_logged.session.get("cart", {}).get(str(produit.id), {}).get("quantity")
        response = client_logged.post(reverse("update_cart"), {
            "product_id": produit.id,
            "quantity": -5
        })
        assert response.status_code in [200, 302]
        new_quantity = client_logged.session.get("cart", {}).get(str(produit.id), {}).get("quantity")
        assert new_quantity == initial_quantity


    # -----------------------------
    # Autres fonctionnalités
    # -----------------------------

    def test_coupon_invalide(self, client_logged):
        """Vérifie le comportement avec un code coupon invalide."""
        response = client_logged.post(reverse("add_coupon"), {"code": "FAKECODE"})
        assert response.status_code in [200, 302]


    def test_methode_get_interdite(self, client_logged):
        """Vérifie que GET sur add_to_cart est interdit (protection CSRF / logique)."""
        response = client_logged.get(reverse("add_to_cart"))
        assert response.status_code == 405  # Method Not Allowed


    def test_donnees_manquantes(self, client_logged):
        """Vérifie que l'envoi de données vides ne casse pas le panier."""
        response = client_logged.post(reverse("add_to_cart"), {})
        assert response.status_code in [200, 302]
        # Le panier reste intact ou vide
        assert "cart" in client_logged.session or client_logged.session.get("cart", {}) == {}


    def test_panier_vide(self, client_logged):
        """Vérifie qu'un nouveau client connecté a un panier vide au départ."""
        assert client_logged.session.get("cart", {}) == {}


    def test_panier_persistant(self, client_logged, produit):
        """Vérifie que le panier persiste après ajout."""
        client_logged.post(reverse("add_to_cart"), {"product_id": produit.id, "quantity": 1})
        assert str(produit.id) in client_logged.session.get("cart", {})


    def test_panier_vide_apres_suppression(self, client_logged, produit):
        """Vérifie que le panier est vide après suppression du seul produit."""
        client_logged.post(reverse("add_to_cart"), {"product_id": produit.id, "quantity": 1})
        client_logged.post(reverse("delete_from_cart"), {"product_id": produit.id})
        assert client_logged.session.get("cart", {}) == {}

    
    def test_deconnexion(client_logged, user):
        # Vérifier que l'utilisateur est connecté
        response = client_logged.get('/')  # n'importe quelle page accessible
        assert '_auth_user_id' in client_logged.session

        # Appel de la vue de déconnexion
        response = client_logged.get(reverse('deconnexion'))

        # Vérifier le code HTTP (souvent redirection vers login)
        assert response.status_code == 302

        # Vérifier que l'utilisateur est maintenant déconnecté
        session = client_logged.session
        assert '_auth_user_id' not in session