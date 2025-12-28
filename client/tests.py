import unittest
from unittest.mock import MagicMock, patch

from client.views import profil, commande, parametre, invoice_pdf


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
