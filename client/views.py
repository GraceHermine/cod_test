from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from customer.models import Customer, Commande, ProduitPanier
from shop.models import  Favorite, Produit
from django.core.paginator import Paginator
from django.db.models import Q
from cities_light.models import City
from django.template.loader import render_to_string
from django.http import HttpResponse
from .utils import render_to_pdf
from .utils import qrcode_base64
from website.models import SiteInfo
import qrcode
from playwright.sync_api import sync_playwright
import base64
from io import BytesIO


# Create your views here.


@login_required
def profil(request):
    user = request.user

    try:
        customer = user.customer  
    except:
        return redirect('index')

    # Récupérer les 5 dernières commandes de l'utilisateur (classées par date décroissante)
    dernieres_commandes = Commande.objects.filter(customer=customer).order_by('-date_add')[:5]

    datas = {
        'user': user,
        'customer': customer,
        'dernieres_commandes': dernieres_commandes 
    }

    return render(request, 'profil.html', datas)


@login_required
def commande(request):
    user = request.user

    try:
        customer = user.customer  
    except:
        return redirect('index')

    # Récupération de toutes les commandes de l'utilisateur
    commandes = Commande.objects.filter(customer=customer).order_by('-date_add')

    # Recherche par ID transaction, produit ou date
    query = request.GET.get('q')
    if query:
        commandes = commandes.filter(
            Q(transaction_id__icontains=query) |
            Q(date_add__icontains=query) |
            Q(produit_commande__produit__nom__icontains=query)
        ).distinct()

    # Pagination : Limite à 10 articles par page
    paginator = Paginator(commandes, 10)  # 10 commandes par page
    page = request.GET.get('page')
    commandes_paginated = paginator.get_page(page)

    # Récupération des produits associés aux commandes paginées
    commandes_data = []
    for commande in commandes_paginated:
        produits_commande = ProduitPanier.objects.filter(commande=commande).select_related('produit')
        commandes_data.append({
            'commande': commande,
            'produits': produits_commande,
        })

    datas = {
        'user': user,
        'customer': customer,
        'commandes_data': commandes_data,
        'commandes_paginated': commandes_paginated,
        'query': query
    }

    return render(request, 'commande.html', datas)


@login_required
def commande_detail(request, commande_id):
    user = request.user

    try:
        customer = user.customer 
    except:
        return redirect('index')

    # Récupération de la commande sélectionnée
    commande = get_object_or_404(Commande, id=commande_id, customer=customer)

    # Récupération des produits associés à cette commande
    produits_commande = ProduitPanier.objects.filter(commande=commande).select_related('produit')

    datas = {
        'user': user,
        'customer': customer,
        'commande': commande,
        'produits_commande': produits_commande
    }

    return render(request, 'commande-detail.html', datas)



@login_required
def suivie_commande(request):
    user = request.user
    try:
        customer = user.customer 
    except:
        return redirect('index')
    datas = {
        'user': user,
        'customer': customer
    }
    return render(request, 'suivie-commande.html', datas)


@login_required
def souhait(request):
    user = request.user
    try:
        customer = user.customer  
    except:
        return redirect('index')
    favoris = Favorite.objects.filter(user=user).select_related('produit')

    datas = {
        'user': user,
        'customer': customer,
        'favoris': favoris,  
    }
    return render(request, 'liste-souhait.html', datas)


@login_required
def avis(request):
    user = request.user
    try:
        customer = user.customer  
    except:
        return redirect('index')
    datas = {
        'user': user,
        'customer': customer
    }
    return render(request, 'avis.html', datas)


@login_required
def evaluation(request):
    user = request.user
    customer = user.customer  

    datas = {
        'user': user,
        'customer': customer
    }
    return render(request, 'evaluation-avis.html', datas)


@login_required
def parametre(request):
    user = request.user
    customer = user.customer 
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact = request.POST.get('contact')
        ville = request.POST.get('city')
        adresse = request.POST.get('address')

        if ville:
            ville = City.objects.get(id=int(ville))
        else:
            ville = None
   
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        
        customer.contact_1 = contact
        customer.ville = ville
        customer.adresse = adresse

        if 'profile_picture' in request.FILES:
            customer.photo = request.FILES['profile_picture']
        customer.save()

        return redirect('parametre')

    datas = {
        'user': user,
        'customer': customer
    }
    return render(request, 'parametre.html', datas)


@login_required
def invoice_pdf(request, order_id):
    order = get_object_or_404(Commande, id=order_id)
    if not hasattr(request.user, "customer") or order.customer_id != request.user.customer.id:
        return redirect("commande")

    # 1. Générer le QR code en base64

    detail_url = request.build_absolute_uri(
        reverse("commande-reçu-detail", args=[order.id])  # ou une URL publique de vérif
    )
    qr_b64 = qrcode_base64(detail_url)

    # 2. Construire le HTML à partir du template
    html = render_to_string("receipt.html", {
        "order_id": order,
        "produits_commande": order.produit_commande.all(),
        "qr_code": qr_b64,
        "logo": request.build_absolute_uri(SiteInfo.objects.latest('date_add').logo.url)
    }, request=request)

    # 3. Lancer Playwright et générer le PDF
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")  # on imprime directement le HTML rendu
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"}
        )
        browser.close()

    # 4. Forcer le téléchargement du PDF
    filename = f"Recu_{order.transaction_id}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

#
# @login_required
# def invoice_pdf(request, order_id):
#     # 1) Construit le HTML depuis un template
#     order = get_object_or_404(Commande, id=order_id)
#     if not hasattr(request.user, "customer") or order.customer_id != request.user.customer.id:
#         return redirect("commande")
#
#     page_url = request.build_absolute_uri(  # URL courante du reçu
#         reverse("commande-reçu-detail", args=[order.id])
#     )
#     qr_b64 = qrcode_base64(page_url)
#
#     return render(request, "receipt.html", {
#         "order_id": order,
#         "produits_commande": order.produit_commande.all(),
#         "qr_code": qr_b64,  # <— base64 prêt pour <img>
#     })