from django.contrib import admin

import shop.models as models
from shop.models import Favorite


class CategorieEtablissementAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom',
        'description',
        'couverture',
        'date_add',
        'date_update',
        'status',
        'slug',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'nom',
        'description',
        'couverture',
        'slug',
    )
    search_fields = ('slug',)


class CategorieProduitAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom',
        'description',
        'categorie',
        'couverture',
        'date_add',
        'date_update',
        'status',
        'slug',
    )
    list_filter = (
        'categorie',
        'date_add',
        'date_update',
        'status',
        'id',
        'nom',
        'description',
        'couverture',
        'slug',
    )
    search_fields = ('slug',)


class EtablissementAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom',
        'description',
        'logo',
        'couverture',
        'categorie',
        'ville',
        'adresse',
        'pays',
        'site_web',
        'contact_1',
        'contact_2',
        'email',
        'date_add',
        'date_update',
        'status',
        'slug',
    )
    list_filter = (
        'categorie',
        'date_add',
        'date_update',
        'status',
        'id',
        'nom',
        'description',
        'logo',
        'couverture',
        'ville',
        'adresse',
        'pays',
        'site_web',
        'contact_1',
        'contact_2',
        'email',
        'slug',
    )
    search_fields = ('slug',)


class ProduitAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom',
        'description',
        'description_deal',
        'prix',
        'prix_promotionnel',
        'date_debut_promo',
        'date_fin_promo',
        'categorie_etab',
        'categorie',
        'etablissement',
        'image',
        'image_2',
        'image_3',
        'super_deal',
        'date_add',
        'date_update',
        'status',
        'slug',
    )
    list_filter = (
        'date_debut_promo',
        'date_fin_promo',
        'categorie_etab',
        'categorie',
        'etablissement',
        'super_deal',
        'date_add',
        'date_update',
        'status',
        'id',
        'nom',
        'description',
        'description_deal',
        'prix',
        'prix_promotionnel',
        'image',
        'image_2',
        'image_3',
        'slug',
    )
    search_fields = ('slug',)

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'produit', 'added_at')  # Colonnes affichées dans la liste
    list_filter = ('user', 'produit', 'added_at')  # Filtres dans l'interface admin
    search_fields = ('user__username', 'produit__nom')  # Recherche par utilisateur ou produit

admin.site.register(Favorite, FavoriteAdmin)


def _register(model, admin_class):
    admin.site.register(model, admin_class)

_register(models.CategorieEtablissement, CategorieEtablissementAdmin)
_register(models.CategorieProduit, CategorieProduitAdmin)
_register(models.Etablissement, EtablissementAdmin)
_register(models.Produit, ProduitAdmin)
