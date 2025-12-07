from django.urls import path
from . import views


urlpatterns = [
    path('', views.shop, name="shop"),
    path('produit/<str:slug>', views.product_detail, name="product_detail"),
    path('cart', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path('<str:slug>', views.single, name="categorie"),
    path('paiement/success', views.paiement_success, name="paiement_success"),
    path('paiement/details', views.post_paiement_details, name="paiement_detail"),
    path('toggle_favorite/<int:produit_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ajout-article/', views.ajout_article, name='ajout-article'),
    path('article-detail/', views.article_detail, name='article-detail'),
    path('modifier-article/<int:article_id>/', views.modifier_article, name='modifier'),
    path('supprimer-article/<int:article_id>/', views.supprimer_article, name='supprimer-article'),
    path('commande-reçu/', views.commande_reçu, name='commande-reçu'),
    path('commande-reçu-detail/<int:commande_id>/', views.commande_reçu_detail, name='commande-reçu-detail'),
    path('etablissement-parametre/', views.etablissement_parametre, name='etablissement-parametre'),
]
