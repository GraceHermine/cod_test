from django.contrib import admin

import customer.models as models
from .models import PasswordResetToken  


class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'adresse',
        'photo',
        'contact_1',
        'contact_2',
        'ville',
        'pays',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'user',
        'date_add',
        'date_update',
        'status',
        'id',
        'adresse',
        'photo',
        'contact_1',
        'contact_2',
        'ville',
        'pays',
    )


class CodePromotionnelAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'libelle',
        'etat',
        'date_fin',
        'reduction',
        'nombre_u',
        'code_promo',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'etat',
        'date_fin',
        'date_add',
        'date_update',
        'status',
        'id',
        'libelle',
        'reduction',
        'nombre_u',
        'code_promo',
    )
    raw_id_fields = ('forfait',)


class PanierAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'session_id',
        'customer',
        'date_add',
        'coupon',
        'date_update',
        'status',
    )
    list_filter = (
        'session_id',
        'customer',
        'date_add',
        'coupon',
        'date_update',
        'status',
    )


class CommandeAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer',
        'id_paiment',
        'payment_token',
        'payment_url',
        'api_response_id',
        'crypto',
        'prix_total',
        'date_add',
        'date_update',
        'status',
        'recu_paiement',
    )
    list_filter = (
        'customer',
        'date_add',
        'date_update',
        'status',
        'id',
        'id_paiment',
        'payment_token',
        'payment_url',
        'api_response_id',
        'crypto',
        'prix_total',
        'recu_paiement',
    )


class ProduitPanierAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'produit',
        'panier',
        'commande',
        'quantite',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'produit',
        'commande',
        'date_add',
        'date_update',
        'status',
        'id',
        'panier',
        'quantite',
    )
    raw_id_fields = ('panier',)


class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'created_at')  # Colonnes affichées dans la liste
    list_filter = ('created_at',)  # Filtres par champ
    search_fields = ('user__username', 'token')  # Champs de recherche

# Enregistrez le modèle avec l'administration
admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(models.Customer, CustomerAdmin)
_register(models.CodePromotionnel, CodePromotionnelAdmin)
_register(models.Panier, PanierAdmin)
_register(models.Commande, CommandeAdmin)
_register(models.ProduitPanier, ProduitPanierAdmin)