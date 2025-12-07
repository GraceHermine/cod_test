from django.db import models
from django.utils.text import slugify
import datetime
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from cities_light.models import City


# Create your models here.
class CategorieEtablissement(models.Model):

    nom = models.CharField(max_length=254)
    description = models.TextField()
    couverture = models.ImageField(upload_to="media/categories/etablissements/couvertures", null=True)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, editable=False, null=True,  blank=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug is None:
            self.slug = '-'.join((slugify(self.nom), slugify(datetime.datetime.now().microsecond)))
        super(CategorieEtablissement, self).save(*args, **kwargs)

    def __str__(self):
        return self.nom


class CategorieProduit(models.Model):

    nom = models.CharField(max_length=254)
    description = models.TextField()
    categorie = models.ForeignKey(CategorieEtablissement, related_name="categorie_produits", on_delete=models.CASCADE, null=True)
    couverture = models.ImageField(upload_to="media/categories/produits/couvertures", null=True)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, editable=False, null=True,  blank=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug is None:
            self.slug = '-'.join((slugify(self.nom), slugify(datetime.datetime.now().microsecond)))
        super(CategorieProduit, self).save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Etablissement(models.Model):
    user = models.OneToOneField(User, related_name='etablissement', on_delete=models.CASCADE)
    nom = models.CharField(max_length=254)
    description = models.TextField()
    logo = models.ImageField(upload_to="media/etablissements/logo")
    couverture = models.ImageField(upload_to="media/etablissements/couvertures")
    categorie = models.ForeignKey(CategorieEtablissement, related_name="produit", on_delete=models.CASCADE)
    nom_du_responsable = models.CharField(max_length=254, null=True)
    prenoms_duresponsable = models.CharField(max_length=254, null=True)
    ville = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    adresse = models.CharField(max_length=254)
    pays = models.CharField(max_length=100)
    site_web = models.URLField(max_length=100, null=True, blank=True)
    contact_1 = models.CharField(max_length=100)
    contact_2 = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100)
    code_acces = models.CharField(max_length=100, default="12345678@@")

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):

        user = self.user
        if user:
            user.last_name = self.nom_du_responsable
            user.first_name = self.prenoms_duresponsable
            user.email = self.email
            user.save(update_fields=['first_name', 'last_name', 'email']) 
        
        if not self.slug:
            self.slug = '-'.join((slugify(self.nom), slugify(datetime.datetime.now().microsecond)))
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    nom = models.CharField(max_length=254)
    description = models.TextField()
    description_deal = models.TextField()
    prix_promotionnel = models.FloatField(default=0)
    prix = models.FloatField()
    quantite = models.IntegerField(null=True, blank=True)
    date_debut_promo = models.DateField(null=True, blank=True)
    date_fin_promo = models.DateField(null=True, blank=True)
    categorie_etab = models.ForeignKey(CategorieEtablissement, related_name="produit_etab", on_delete=models.CASCADE, null=True, blank=True)
    categorie = models.ForeignKey(CategorieProduit, related_name="produit", on_delete=models.CASCADE)
    etablissement = models.ForeignKey(Etablissement, related_name="produits", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='produis/images', default="b-1.jpg")
    image_2 = models.ImageField(upload_to='produis/images', default="b-1.jpg")
    image_3 = models.ImageField(upload_to='produis/images', default="b-1.jpg")
    super_deal = models.BooleanField(default=False)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, editable=False, null=True,  blank=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug is None:
            self.slug = '-'.join((slugify(self.nom), slugify(datetime.datetime.now().microsecond)))
        self.categorie_etab = self.etablissement.categorie
        super(Produit, self).save(*args, **kwargs)

    def __str__(self):
        return self.nom

    @property
    def check_promotion(self):
        result = True
        if self.date_debut_promo:
            if self.date_debut_promo > datetime.date.today():
                result = False
        else:
            result = False
        if self.date_fin_promo:
            if self.date_fin_promo < datetime.date.today():
                result = False
        else:
            result=False
        
        return result


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'produit')
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.produit.nom}"

