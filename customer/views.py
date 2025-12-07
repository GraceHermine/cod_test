from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.shortcuts import render
from . import models
from shop import models as shop_models
from django.contrib.auth import authenticate, login as login_request, logout
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from cities_light.models import City


from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.urls import reverse


from django.contrib.auth.hashers import make_password
from .models import PasswordResetToken
from django.core.exceptions import ValidationError
from django.utils.timezone import now

# Create your views here.
def login(request):
    if request.user.is_authenticated:
        return redirect("index")
    else:
        datas = {

        }
        return render(request, 'login.html', datas)


def signup(request):
    if request.user.is_authenticated:
        return redirect("index")
    else:
        datas = {
        }
        return render(request, 'register.html', datas)


def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("index")
    else:
        datas = {

        }
        return render(request, 'forgot-password.html', datas)


def islogin(request):
    postdata = json.loads(request.body.decode('utf-8'))

    # name = postdata['name']

    username = postdata['username']
    password = postdata['password']

    isSuccess = False
    try:

        if '@' in username:
            utilisateur = User.objects.get(email=username)
            user = authenticate(username=utilisateur.username, password=password)
        else:
            utilisateur = User.objects.get(username=username)
            user = authenticate(username=utilisateur.username, password=password)
        if user is not None and user.is_active:

            isSuccess = True
            _ = isSuccess
            login_request(request, user)
            datas = {
                'success': True,
                'message': 'Vous êtes connectés!!!',
            }
            return JsonResponse(datas, safe=False)  # page si connect
        else:

            data = {
                'success': False,
                'message': 'Vos identifiants ne sont pas correcte',
            }
            return JsonResponse(data, safe=False)
    except:
        data = {
            'success': False,
            'message': "Merci de vérifier vos informations",
        }
        return JsonResponse(data, safe=False)


def deconnexion(request):
    logout(request)
    return redirect('login')


# Fonction de recuperation et de traitement des données en cas de post ###############
def inscription(request):

    # name = postdata['name']
    nom = request.POST.get('nom')
    prenoms = request.POST.get('prenoms')
    username = request.POST.get('username')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    ville = request.POST.get('ville')
    adresse = request.POST.get('adresse')
    password = request.POST.get('password')
    passwordconf = request.POST.get('passwordconf')

    if ville:
        ville = City.objects.get(id=int(ville))
    else:
        ville = None

    if username is not None and nom is not None and password is not None and email is not None and phone is not None and passwordconf is not None:
        is_email = False
        try:
            validate_email(email)
            is_email = True
        except:
            is_email = False
        if is_email:

            if password != passwordconf:
                message = "mot de passe incorrect "
                issuccess = False
            else:
                try:
                    user = User()
                    user.username = username
                    user.last_name = nom
                    user.first_name = prenoms
                    user.email = email
                    user.save()
                    user.password = password
                    user.set_password(user.password)
                    user.save()
                    profile = models.Customer()
                    profile.user = user
                    profile.contact_1 = phone
                    profile.ville = ville
                    profile.adresse = adresse
                    profile.save()
                    if request.FILES['file']:

                        image = request.FILES['file']
                        profile.photo = image
                        profile.save()
                    message = "Votre Compte a été créé avec succès"
                    issuccess = True
                    if user is not None and user.is_active:
                        login_request(request, user)
                        message = "Votre Compte a été créé avec succès"
                        issuccess = True
                except Exception as _:

                    message = "Un utilisateur avec le même email ou username existe déjà"
                    issuccess = False
        else:

            message = 'Merci de vérifier vos informations'
            issuccess = False
    else:

        message = 'Merci de vérifier vos informations'
        issuccess = False

    datas = {
        'success': issuccess,
        'message': message
    }

    return JsonResponse(datas, safe=False)


def add_to_cart(request):
    postdata = json.loads(request.body.decode('utf-8'))

    # name = postdata['name']

    panier = postdata['panier']
    produit = postdata['produit']
    quantite = postdata['quantite']
    isSuccess = False
    if panier is not None and produit is not None and quantite is not None:
        panier = models.Panier.objects.get(id=panier)
        produit = shop_models.Produit.objects.get(id=produit)
        try:
            produit_panier = models.ProduitPanier.objects.get(produit=produit, panier=panier)

        except Exception as e:

            produit_panier = models.ProduitPanier()
        produit_panier.panier = panier
        produit_panier.produit = produit
        produit_panier.quantite = quantite
        produit_panier.save()
        isSuccess = True
        message = "Produit ajouté au panier avec succès"
    else:
        isSuccess = False
        message = "Une erreur s'est produite"
    data = {
        'message': message,
        'success': isSuccess
    }
    return JsonResponse(data, safe=False)


def delete_from_cart(request):
    postdata = json.loads(request.body.decode('utf-8'))

    # name = postdata['name']

    panier = postdata['panier']
    produit_panier = postdata['produit_panier']

    isSuccess = False
    if panier is not None and produit_panier is not None :
        produit_panier = models.ProduitPanier.objects.get(id=produit_panier)
        produit_panier.delete()
        isSuccess = True
        message = "Produit supprimé avec succès"
    else:
        isSuccess = False
        message = "Une erreur s'est produite"
    data = {
        'message': message,
        'success': isSuccess
    }
    return JsonResponse(data, safe=False)


def add_coupon(request):
    postdata = json.loads(request.body.decode('utf-8'))

    # name = postdata['name']

    panier = postdata['panier']
    coupon = postdata['coupon']

    isSuccess = False
    if panier is not None and coupon is not None :
        try:
            coupon = models.CodePromotionnel.objects.get(code_promo=coupon)
            panier = models.Panier.objects.get(id=panier)
            panier.coupon = coupon
            panier.save()
            isSuccess = True
            message = "Félicitations, vous avez ajouté un code coupon"
        except:
            isSuccess = False
            message = "Code coupon invalide"
    else:
        isSuccess = False
        message = "Une erreur s'est produite"
    data = {
        'message': message,
        'success': isSuccess
    }
    return JsonResponse(data, safe=False)


def update_cart(request):
    postdata = json.loads(request.body.decode('utf-8'))

    # name = postdata['name']

    panier = postdata['panier']
    produit = postdata['produit']
    quantite = postdata['quantite']

    isSuccess = False
    if panier is not None and produit is not None :
        panier = models.Panier.objects.get(id=panier)
        produit = shop_models.Produit.objects.get(id=produit)
        produit_panier = models.ProduitPanier.objects.get(panier=panier, produit=produit)
        produit_panier.quantite = quantite
        produit_panier.save()
        isSuccess = True
        message = "Panier modifié avec succès"
    else:
        isSuccess = False
        message = "Une erreur s'est produite"
    data = {
        'message': message,
        'success': isSuccess
    }
    return JsonResponse(data, safe=False)


# Étape 1 : Vue pour demander l'e-mail
def request_reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            validate_email(email)  # Valider l'adresse e-mail
            user = User.objects.get(email=email)
            token, created = PasswordResetToken.objects.get_or_create(user=user)
            if not created:
                # Mettre à jour l'horodatage si un token existant est trouvé
                token.created_at = now()
            token.token = get_random_string(64)
            token.save()

            # Envoyer l'e-mail
            reset_url = request.build_absolute_uri(reverse('reset_password', args=[token.token]))
            send_mail(
                'Réinitialisation de mot de passe',
                f'Cliquez sur le lien suivant pour réinitialiser votre mot de passe : {reset_url}',
                'nguessanlandry216@gmail.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Un e-mail de réinitialisation a été envoyé.')
            return redirect('request_reset_password')

        except ValidationError:
            messages.error(request, 'Adresse e-mail invalide.')
        except User.DoesNotExist:
            messages.error(request, 'Aucun compte trouvé avec cet e-mail.')
        except Exception as e:
            messages.error(request, f'Une erreur est survenue : {str(e)}')
        return redirect('request_reset_password')

    return render(request, 'reset_password/request.html')


# Étape 2 : Vue pour réinitialiser le mot de passe
def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, 'Le lien de réinitialisation a expiré.')
            reset_token.delete()  # Supprimer les tokens expirés
            return redirect('request_reset_password')

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                messages.error(request, 'Les mots de passe ne correspondent pas.')
                return redirect(request.path)

            # Modifier le mot de passe de l'utilisateur
            reset_token.user.password = make_password(new_password)
            reset_token.user.save()

            # Supprimer le token après utilisation
            reset_token.delete()

            messages.success(request, 'Votre mot de passe a été réinitialisé avec succès.')
            return redirect('login')

        return render(request, 'reset_password/reset.html', {'token': token})

    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Lien invalide.')
        return redirect('request_reset_password')


# Test Email
def test_email(request):
    try:
        send_mail(
            'Test Email',
            'Ceci est un test.',
            'nguessanlandry216@gmail.com',
            ['votre_email@exemple.com'],
            fail_silently=False,
        )
        return JsonResponse({'status': 'success', 'message': 'E-mail envoyé avec succès !'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur : {str(e)}'})