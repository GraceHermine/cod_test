from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('a-propos', views.about, name='about'),
]
