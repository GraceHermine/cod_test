from shop import models
from . import models as config_models
from customer import models as customer_models
from django.contrib.sessions.models import Session
from cities_light.models import City


def categories(request):
    cat = models.CategorieEtablissement.objects.filter(status=True)

    return {'cat':cat}


def site_infos(request):
    try:
        infos = config_models.SiteInfo.objects.latest('date_add')
    except:
        infos = None
    return {'infos':infos}


def cities(request):

    cities = City.objects.all()

    return {'cities': cities}


def galeries(request):
    galerie = config_models.Galerie.objects.filter(status=True)[:6]

    return {'galeries':galerie}


def horaires(request):
    horaire = config_models.Horaire.objects.filter(status=True)

    return {'horaires':horaire}


def cart(request):
    carts = ""
    try:
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session_id = Session.objects.get(session_key=request.session.session_key)
        if request.user.is_authenticated:
            try:
                customer = customer_models.Customer.objects.get(user=request.user)
                carts = customer_models.Panier.objects.get(customer=customer, session_id=session_id)
            except Exception as e:

                customer = customer_models.Customer.objects.get(user=request.user)
                carts = customer_models.Panier()
                carts.session_id = session_id
                carts.customer = customer
                carts.save()
        else:
            try:
                carts = customer_models.Panier.objects.get(session_id=session_id)
            except Exception as e:

                carts = customer_models.Panier()
                carts.session_id = session_id
                carts.save()
    except:
        pass
    return {'cart':carts}