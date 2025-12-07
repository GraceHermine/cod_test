from django.shortcuts import render
from . import models
from shop import models as shop_models


# Create your views here.
def index(request):
    about = models.About.objects.filter(status=True)[:1]
    partenaires = models.Partenaire.objects.filter(status=True)[:5]
    bannieres = models.Banniere.objects.filter(status=True)[:4]
    appreciations = models.Appreciation.objects.filter(status=True)
    produits = shop_models.Produit.objects.filter(super_deal=True)[:3]
    datas = {
        'about': about,
        'partenaires': partenaires,
        'appreciations': appreciations,
        'produits': produits,
        'bannieres': bannieres,
    }

    return render(request, 'index.html', datas)


def about(request):
    about = models.About.objects.filter(status=True)[:1]
    why_choose = models.WhyChooseUs.objects.filter(status=True)[:3]
    datas = {
        'about': about,
        'why_choose': why_choose,

    }
    return render(request, 'about-us.html', datas)