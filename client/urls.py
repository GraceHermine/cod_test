from django.urls import path
from . import views


urlpatterns = [
    path('', views.profil, name="profil"),
    path('commande', views.commande, name="commande"),
    path('commande-detail/<int:commande_id>/', views.commande_detail, name="commande-detail"),
    path('liste-souhait', views.souhait, name="liste-souhait"),
    path('parametre', views.parametre, name="parametre"),
    path('receipt/<int:order_id>/', views.invoice_pdf, name="invoice_pdf"),

]
