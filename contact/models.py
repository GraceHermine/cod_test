from django.db import models


# Create your models here.
class Contact(models.Model):
    nom = models.CharField(max_length=255)
    sujet = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    message = models.TextField()

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


class NewsLetter(models.Model):
    email = models.EmailField(max_length=255)

    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.email