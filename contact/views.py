from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.shortcuts import render
from . import models
from django.contrib.auth import authenticate, login as login_request, logout
import json
from django.http import JsonResponse
from django.contrib.auth.models import User


# Create your views here.
def contact(request):
    datas = {}
    return render(request, 'contact-us.html', datas)


def post_contact(request):
    postdata = json.loads(request.body.decode('utf-8'))

    # name = postdata['name']

    email = postdata['email']
    sujet = postdata['sujet']
    messages = postdata['messages']
    nom = postdata['nom']
    try:
        validate_email(email)
        is_email = True
    except:
        is_email = False

    isSuccess = False
    if is_email  and nom is not None and sujet is not None and messages is not None and nom:
        contact = models.Contact()
        contact.nom = nom
        contact.email = email
        contact.sujet = sujet
        contact.message = messages
        contact.save()
        isSuccess = True
        message = "Merci pour votre message"
    else:
        isSuccess = False
        message = "Merci de renseigner correctement les champs"
    data = {
        'message':message,
        'success':isSuccess
    }
    return JsonResponse(data, safe=False)

def post_newsletter(request):
    postdata = json.loads(request.body.decode('utf-8'))

    # name = postdata['name']

    email = postdata['email']
    try:
        validate_email(email)
        is_email = True
    except:
        is_email = False
    isSuccess = False
    if is_email:
        newsletter = models.NewsLetter()
        
        newsletter.email = email
        isSuccess = True
        message = "Félicitations vous êtes abonnés à notre newsletter"
    else:
        isSuccess = False
        message = "Merci de renseigner une adresse email correcte"
    data = {
        'message':message,
        'success':isSuccess
    }
    return JsonResponse(data, safe=False)