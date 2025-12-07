from django.db import models


# Create your models here.
class SiteInfo(models.Model):
    titre = models.CharField(max_length=150)
    slogan = models.CharField(max_length=150)
    description = models.TextField()
    horaire_description = models.TextField()
    text_pourquoi_nous_choisir = models.TextField()
    logo = models.ImageField(upload_to="site/info", default="logo.png")
    icon = models.ImageField(upload_to="site/info", default="icon.png")
    arriere_plan_appreciation = models.ImageField(upload_to="site/info")
    arriere_plan_appreciation_2 = models.ImageField(upload_to="site/info", null=True)
    image_session_pourquoi_nous_choisir = models.ImageField(upload_to="site/info")
    image_page_contact = models.ImageField(upload_to="site/info")
    image_pied_de_page = models.ImageField(upload_to="site/info", null=True)
    couverture_page_contact = models.ImageField(upload_to="site/info", null=True)
    couverture_page_panier = models.ImageField(upload_to="site/info", null=True)
    couverture_page_paiement = models.ImageField(upload_to="site/info", null=True)
    couverture_page_shop = models.ImageField(upload_to="site/info", null=True)
    couverture_page_about = models.ImageField(upload_to="site/info", null=True)
    contact_1 = models.CharField(max_length=150)
    contact_2 = models.CharField(max_length=150)
    email = models.EmailField(max_length=155)
    email_2 = models.EmailField(max_length=155, null=True)
    adresse = models.TextField()
    map_url = models.TextField()
    facebook_url = models.TextField()
    instagram_url = models.TextField()
    twitter_url = models.TextField()
    whatsapp = models.TextField()

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.titre


class Banniere(models.Model):

    titre = models.CharField(max_length=254)
    description = models.TextField()
    couverture = models.ImageField(upload_to="media/bannieres", null=True)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.titre


class Appreciation(models.Model):

    titre = models.CharField(max_length=254)
    description = models.TextField()
    auteur = models.CharField(max_length=254)
    role = models.CharField(max_length=254)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.titre


class About(models.Model):

    titre = models.CharField(max_length=254)
    sous_titre = models.CharField(max_length=254)
    description = models.TextField()
    image = models.ImageField(upload_to="media/bannieres", null=True)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Session A propos"
        verbose_name_plural = "Sessions A propos"

    def __str__(self):
        return self.titre


class WhyChooseUs(models.Model):

    ICON_CHOICES = [('zmdi-favorite', 'zmdi-favorite'), ('fa-pagelines', 'fa-pagelines'), ('zmdi-mood', 'zmdi-mood'), \
                    ('zmdi-dribbble', 'zmdi-dribbble')]
    titre = models.CharField(max_length=254)
    description = models.TextField()
    icon = models.CharField(max_length=254, choices=ICON_CHOICES)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Pourquoi Nous choisir"

    def __str__(self):
        return self.titre


class Galerie(models.Model):

    titre = models.CharField(max_length=254)
    description = models.TextField()
    image = models.ImageField(upload_to="media/bannieres", null=True)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.titre


class Horaire(models.Model):

    titre = models.CharField(max_length=254)
    description = models.TextField()

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.titre


class Partenaire(models.Model):

    nom = models.CharField(max_length=254)
    description = models.TextField()
    image = models.ImageField(upload_to="media/bannieres", null=True)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

