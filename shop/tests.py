import json
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User, AnonymousUser
from unittest.mock import patch, MagicMock
from django.urls import reverse

# Imports modèles
from shop.models import CategorieProduit, Favorite, Produit, CategorieEtablissement, Etablissement
from customer.models import Customer  # Nécessaire pour paiement_success

# Imports vues
from shop.views import (
    paiement_success, post_paiement_details, product_detail, 
    single, shop, supprimer_article, toggle_favorite, cart, 
    commande_reçu_detail, dashboard, ajout_article, 
    etablissement_parametre, modifier_article
)

class ShopTests(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

        # 1. Créer l'utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            password='password',
            email='test@example.com',
            first_name='Test',
            last_name='User',
        )

        # 2. Créer un Customer pour l'utilisateur (obligatoire pour paiement_success)
        self.customer = Customer.objects.create(
            user=self.user,
            # Ajoute ici les champs obligatoires de ton modèle Customer
            # Exemple si tu as un champ 'telephone' :
            # telephone="0000000000",
        )

        # 3. Créer catégorie établissement
        self.categorie_etab = CategorieEtablissement.objects.create(
            nom="Restaurant",
            description="Catégorie test",
        )

        # 4. Créer l'établissement
        self.etab = Etablissement.objects.create(
            user=self.user,
            nom="Boutique Test",
            description="Description test",
            logo="media/etablissements/logo/default.jpg",
            couverture="media/etablissements/couvertures/default.jpg",
            categorie=self.categorie_etab,
            nom_du_responsable="Dupont",
            prenoms_duresponsable="Jean",
            adresse="123 Rue Test",
            pays="France",
            contact_1="0123456789",
            email="contact@boutique.com",
        )

        # 5. Créer catégorie produit
        self.categorie_produit = CategorieProduit.objects.create(
            nom="Plat principal",
            description="Catégorie produit test",
            categorie=self.categorie_etab,
        )

        # 6. Créer le produit
        self.produit = Produit.objects.create(
            nom="Produit Test",
            slug="test-slug",
            description="Description produit",
            description_deal="Deal spécial",
            prix=100,
            prix_promotionnel=80,
            categorie=self.categorie_produit,
            etablissement=self.etab,
        )

    # === Tests simples (RequestFactory OK) ===
    def test_shop_returns_200(self):
        request = self.factory.get("/shop/")
        request.user = AnonymousUser()
        response = shop(request)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_anonymous(self):
        request = self.factory.get("/p/")
        request.user = AnonymousUser()
        response = product_detail(request, self.produit.slug)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_authenticated_favorited(self):
        Favorite.objects.create(user=self.user, produit=self.produit)
        request = self.factory.get("/p/")
        request.user = self.user
        response = product_detail(request, self.produit.slug)
        self.assertEqual(response.status_code, 200)


    def test_cart(self):
        request = self.factory.get("/cart/")
        request.user = AnonymousUser()
        response = cart(request)
        self.assertEqual(response.status_code, 200)


    @patch("shop.models.CategorieProduit.objects.get")
    def test_single_categorie_produit(self, mock_get):
        mock_cat = MagicMock()
        mock_cat.produit.all.return_value = []
        mock_get.return_value = mock_cat
        request = self.factory.get("/")
        response = single(request, "slug")
        self.assertEqual(response.status_code, 200)


    # === Tests avec authentification / messages / redirection ===
    def test_checkout_redirect_if_not_logged(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('next=/deals/checkout', response.url)  # ou '/checkout' selon ton prefixe

    def test_paiement_success_anonymous(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        response = paiement_success(request)
        self.assertEqual(response.status_code, 302)


    def test_paiement_success_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('paiement_success'))
        self.assertEqual(response.status_code, 200)

    

    def test_post_paiement_invalid_data(self):
        request = self.factory.post(
            "/paiement/details",
            data=json.dumps({
                "transaction_id": "fake_transaction_123",
                "notify_url": "http://example.com/notify",
                "return_url": "http://example.com/return",
                "panier": [],  # nécessaire
                "amount": "texte_invalide"  # valeur invalide pour provoquer une erreur
            }),
            content_type="application/json"
        )
        request.user = self.user

        response = post_paiement_details(request)
        self.assertEqual(response.status_code, 200)

        # Convertir le contenu JSON de la réponse
        data = json.loads(response.content)
        self.assertFalse(data["success"])


    # === Tests avec get_object_or_404 ===
    def test_dashboard(self):
        self.client.force_login(self.user)
        # On utilise l'objet réel au lieu d'un mock
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


    @patch("shop.views.get_object_or_404")
    def test_commande_recu_detail(self, mock_get):
        mock_commande = MagicMock()
        mock_commande.id = 1
        mock_get.return_value = mock_commande

        request = self.factory.get("/")
        request.user = self.user
        response = commande_reçu_detail(request, 1)
        self.assertEqual(response.status_code, 200)


    # === Tests avec messages (self.client + force_login) ===
    def test_toggle_favorite_not_authenticated(self):
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertEqual(response.status_code, 302)


    def test_toggle_favorite_create(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertTrue(Favorite.objects.filter(user=self.user, produit=self.produit).exists())


    def test_toggle_favorite_delete(self):
        Favorite.objects.create(user=self.user, produit=self.produit)
        self.client.force_login(self.user)
        response = self.client.get(reverse('toggle_favorite', args=[self.produit.id]))
        self.assertFalse(Favorite.objects.filter(user=self.user, produit=self.produit).exists())


    def test_ajout_article_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ajout-article'))
        self.assertEqual(response.status_code, 200)


    def test_modifier_article_invalid_price(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('modifier', args=[self.produit.id]),
            data={"prix": "abc"}
        )
        self.assertEqual(response.status_code, 302)


    def test_supprimer_article_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('supprimer-article', args=[self.produit.id]))
        self.assertEqual(response.status_code, 302)


    def test_etablissement_parametre_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('etablissement-parametre'))
        self.assertEqual(response.status_code, 200)