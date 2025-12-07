from django.contrib import admin

import website.models as models


class SiteInfoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'slogan',
        'description',
        'horaire_description',
        'text_pourquoi_nous_choisir',
        'logo',
        'icon',
        'arriere_plan_appreciation',
        'arriere_plan_appreciation_2',
        'image_session_pourquoi_nous_choisir',
        'image_page_contact',
        'image_pied_de_page',
        'couverture_page_contact',
        'couverture_page_panier',
        'couverture_page_paiement',
        'couverture_page_shop',
        'couverture_page_about',
        'contact_1',
        'contact_2',
        'email',
        'email_2',
        'adresse',
        'map_url',
        'facebook_url',
        'instagram_url',
        'twitter_url',
        'whatsapp',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'titre',
        'slogan',
        'description',
        'horaire_description',
        'text_pourquoi_nous_choisir',
        'logo',
        'icon',
        'arriere_plan_appreciation',
        'arriere_plan_appreciation_2',
        'image_session_pourquoi_nous_choisir',
        'image_page_contact',
        'image_pied_de_page',
        'couverture_page_contact',
        'couverture_page_panier',
        'couverture_page_paiement',
        'couverture_page_shop',
        'couverture_page_about',
        'contact_1',
        'contact_2',
        'email',
        'email_2',
        'adresse',
        'map_url',
        'facebook_url',
        'instagram_url',
        'twitter_url',
        'whatsapp',
    )


class BanniereAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'description',
        'couverture',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'titre',
        'description',
        'couverture',
    )


class AppreciationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'description',
        'auteur',
        'role',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'titre',
        'description',
        'auteur',
        'role',
    )


class AboutAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'sous_titre',
        'description',
        'image',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'titre',
        'sous_titre',
        'description',
        'image',
    )


class WhyChooseUsAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'description',
        'icon',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'titre',
        'description',
        'icon',
    )


class GalerieAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'description',
        'image',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'titre',
        'description',
        'image',
    )


class HoraireAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'titre',
        'description',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'titre',
        'description',
    )


class PartenaireAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom',
        'description',
        'image',
        'date_add',
        'date_update',
        'status',
    )
    list_filter = (
        'date_add',
        'date_update',
        'status',
        'id',
        'nom',
        'description',
        'image',
    )


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(models.SiteInfo, SiteInfoAdmin)
_register(models.Banniere, BanniereAdmin)
_register(models.Appreciation, AppreciationAdmin)
_register(models.About, AboutAdmin)
_register(models.WhyChooseUs, WhyChooseUsAdmin)
_register(models.Galerie, GalerieAdmin)
_register(models.Horaire, HoraireAdmin)
_register(models.Partenaire, PartenaireAdmin)