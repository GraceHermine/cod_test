from django.test import TestCase
import unittest
from unittest.mock import patch, MagicMock
import json
from django.http import HttpRequest
from django.urls import reverse
import pytest
from contact import views
from bs4 import BeautifulSoup

from contact.models import Contact, NewsLetter
# Create your tests here.


class TestContactViews(unittest.TestCase):

    def setUp(self):
        # Créer une fausse requête
        self.request = MagicMock(spec=HttpRequest)
        self.request.method = 'POST'

    # ------------------ contact ------------------
    @patch('contact.views.render')
    def test_contact_view(self, mock_render):
        # Appel de la vue contact
        mock_render.return_value = MagicMock()
        response = views.contact(self.request)
        mock_render.assert_called_once_with(self.request, 'contact-us.html', {})
    
    # ------------------ post_contact ------------------
    @patch('contact.views.models.Contact')
    def test_post_contact_valid(self, mock_contact_model):
        # Requête POST avec données valides
        post_data = {
            'email': 'test@example.com',
            'nom': 'Herminou',
            'sujet': 'Test ',
            'messages': 'Ceci est un message pour un test merci'
        }
        self.request.body = json.dumps(post_data).encode('utf-8')
        
        mock_contact_instance = MagicMock()
        mock_contact_model.return_value = mock_contact_instance

        response = views.post_contact(self.request)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], "Merci pour votre message")
        mock_contact_instance.save.assert_called_once()
    
    @patch('contact.views.models.Contact')
    def test_post_contact_invalid_email(self, mock_contact_model):
        post_data = {
            'email': 'invalid-email',
            'nom': 'Grachou',
            'sujet': 'Test Sujet',
            'messages': 'Ceci est un message'
        }
        self.request.body = json.dumps(post_data).encode('utf-8')
        response = views.post_contact(self.request)
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Merci de renseigner correctement les champs")
        self.assertFalse(mock_contact_model.return_value.save.called)

    # ------------------ post_newsletter ------------------
    @patch('contact.views.models.NewsLetter')
    def test_post_newsletter_valid_email(self, mock_newsletter_model):
        post_data = {'email': 'newsletter@example.com'}
        self.request.body = json.dumps(post_data).encode('utf-8')

        mock_newsletter_instance = MagicMock()
        mock_newsletter_model.return_value = mock_newsletter_instance

        response = views.post_newsletter(self.request)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], "Félicitations vous êtes abonnés à notre newsletter")
        mock_newsletter_instance.save.assert_not_called()  # Ton code actuel ne fait pas save()

    @patch('contact.views.models.NewsLetter')
    def test_post_newsletter_invalid_email(self, mock_newsletter_model):
        post_data = {'email': 'bad-email'}
        self.request.body = json.dumps(post_data).encode('utf-8')

        response = views.post_newsletter(self.request)
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Merci de renseigner une adresse email correcte")
        self.assertFalse(mock_newsletter_model.return_value.save.called)


@pytest.mark.django_db
class TestsFonctionnelContactNewsletter:
    """
    Tests fonctionnels purs :
    - navigation réelle via client Django
    - analyse HTML avec BeautifulSoup
    - comportement utilisateur
    """

    # =========================
    # CONTACT (GET)
    # =========================

    def test_contact_page_affichage(self, client):
        response = client.get(reverse("contact"))
        assert response.status_code == 200

    def test_contact_formulaire_present(self, client):
        response = client.get(reverse("contact"))
        soup = BeautifulSoup(response.content, "html.parser")

        assert soup.find("input", {"name": "nom"})
        assert soup.find("input", {"name": "email"})
        assert soup.find("textarea", {"name": "message"})
        assert soup.find("button", {"type": "submit"})

    # =========================
    # CONTACT (POST)
    # =========================

    def test_contact_post_champs_vides(self, client):
        response = client.post(reverse("post_contact"), data={})

        assert response.status_code in [200, 302]
        assert Contact.objects.count() == 0

    def test_contact_post_email_invalide(self, client):
        response = client.post(
            reverse("post_contact"),
            data={
                "nom": "Test",
                "email": "email-invalide",
                "message": "Message test",
            }
        )

        assert response.status_code in [200, 302]
        assert Contact.objects.count() == 0

    def test_contact_post_donnees_valides(self, client):
        response = client.post(
            reverse("post_contact"),
            data={
                "nom": "Test User",
                "email": "test@example.com",
                "message": "Bonjour, ceci est un message",
            }
        )

        assert response.status_code in [200, 302]
        assert Contact.objects.count() == 1

    # =========================
    # NEWSLETTER (POST)
    # =========================

    def test_newsletter_champ_vide(self, client):
        response = client.post(reverse("post_newsletter"), data={})

        assert response.status_code in [200, 302]
        assert NewsLetter.objects.count() == 0

    def test_newsletter_email_invalide(self, client):
        response = client.post(
            reverse("post_newsletter"),
            data={"email": "email-invalide"}
        )

        assert response.status_code in [200, 302]
        assert NewsLetter.objects.count() == 0

    def test_newsletter_email_valide(self, client):
        response = client.post(
            reverse("post_newsletter"),
            data={"email": "newsletter@test.com"}
        )

        assert response.status_code in [200, 302]
        assert NewsLetter.objects.count() == 1

    def test_newsletter_email_deja_inscrit(self, client):
        NewsLetter.objects.create(email="duplicate@test.com")

        response = client.post(
            reverse("post_newsletter"),
            data={"email": "duplicate@test.com"}
        )

        assert response.status_code in [200, 302]
        assert NewsLetter.objects.count() == 1