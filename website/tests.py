from django.test import TestCase, Client
from unittest.mock import patch, MagicMock

from shop.models import Produit


class TestUnitaire(TestCase):
    def setUp(self):
        self.client = Client()  # Client active le middleware → context et rendu complet

    @patch('website.views.models.About.objects.filter')
    @patch('website.views.models.Partenaire.objects.filter')
    @patch('website.views.models.Banniere.objects.filter')
    @patch('website.views.models.Appreciation.objects.filter')
    @patch('website.views.shop_models.Produit.objects.filter')
    def test_index_view(self, mock_produit, mock_appreciation, mock_banniere, mock_partenaire, mock_about):
        # Mock des données simples
        mock_about.return_value = [MagicMock()]
        mock_partenaire.return_value = [MagicMock(), MagicMock()]
        mock_banniere.return_value = [MagicMock(), MagicMock()]
        mock_appreciation.return_value = [MagicMock()]

        # Mock des produits avec les attributs utilisés dans le template
        # prod1 = MagicMock()
        # Remplacez la création de vos produits par ceci :
        prod1 = MagicMock(spec=Produit) # spec aide à se comporter comme le modèle
        prod1.slug = 'produit-1'
        prod1.nom = 'Produit Test 1'
        prod1.prix = 5000
        prod1.prix_promotionnel = 4000
        prod1.image = 'media/test.jpg'

        prod2 = MagicMock(spec=Produit)
        prod2.slug = 'produit-2'
        prod2.nom = 'Produit Test 2'
        prod2.prix = 10000
        prod2.prix_promotionnel = 8000
        prod2.image = 'media/test2.jpg'

        mock_produit.return_value = [prod1, prod2]

        # Requête avec Client
        response = self.client.get('/')

        # Vérifications de base
        self.assertEqual(response.status_code, 200)

        # Vérification du contexte
        self.assertIn('produits', response.context)
        self.assertEqual(len(response.context['produits']), 2)

        # Vérification du rendu (éléments qui apparaissent forcément)
        content = response.content.decode('utf-8')
        self.assertIn('Produit Test 1', content)
        self.assertIn('Produit Test 2', content)
        self.assertIn('produit-1', content)  # slug dans l'URL
        self.assertIn('produit-2', content)

        # Vérification que les prix sont affichés (si ton template les montre)
        self.assertIn('4000', content)  # prix promo
        self.assertIn('8000', content)

    @patch('website.views.models.About.objects.filter')
    @patch('website.views.models.WhyChooseUs.objects.filter')
    def test_about_view(self, mock_why_choose, mock_about):
        # Mock des objets About
        about_obj = MagicMock()
        about_obj.titre = "À propos de Cool Deal"
        about_obj.description = "Nous sommes la meilleure plateforme de deals en ligne."
        about_obj.image = "media/about.jpg"

        mock_about.return_value = [about_obj]

        # Mock des objets WhyChooseUs
        why1 = MagicMock()
        why1.titre = "Meilleurs prix"
        why1.description = "Nous négocions les meilleurs tarifs pour vous"
        why1.icon = "zmdi zmdi-money"

        why2 = MagicMock()
        why2.titre = "Service client 24/7"
        why2.description = "Une équipe dédiée à votre disposition"
        why2.icon = "zmdi zmdi-headset"

        mock_why_choose.return_value = [why1, why2]

        # Requête avec la bonne URL
        response = self.client.get('a-propos')

        # Vérification de base
        self.assertEqual(response.status_code, 200)

        # Vérification du contexte
        self.assertIn('about', response.context)
        self.assertEqual(len(response.context['about']), 1)

        self.assertIn('why_choose', response.context)
        self.assertEqual(len(response.context['why_choose']), 2)

        # Vérification du rendu
        content = response.content.decode('utf-8')
        self.assertIn("À propos de Cool Deal", content)
        self.assertIn("Meilleurs prix", content)
        self.assertIn("Service client 24/7", content)
        self.assertIn("Nous sommes la meilleure plateforme", content)