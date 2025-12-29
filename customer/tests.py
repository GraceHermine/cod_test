import json
import pytest
import unittest
from customer import views
from django.urls import reverse
from django.test import TestCase
from django.http import JsonResponse
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from cities_light.models import City, Country
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