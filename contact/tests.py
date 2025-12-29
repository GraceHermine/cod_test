from django.test import TestCase
import unittest
from unittest.mock import patch, MagicMock
import json
from django.http import HttpRequest
from contact import views
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