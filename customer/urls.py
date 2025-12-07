from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name="login"),
    path('signup', views.signup, name="guests_signup"),
    path('forgot_password', views.forgot_password, name="forgot_password"),
    path('post', views.islogin, name="post"),
    path('deconnexion', views.deconnexion, name="deconnexion"),
    path('inscription', views.inscription, name="inscription"),
    path('cart/add/product', views.add_to_cart, name="add_to_cart"),
    path('cart/add/coupon', views.add_coupon, name="add_coupon"),
    path('cart/delete/product', views.delete_from_cart, name="delete_from_cart"),
    path('cart/udpate/product', views.update_cart, name="update_cart"),
    path('reset-password/', views.request_reset_password, name='request_reset_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
]
