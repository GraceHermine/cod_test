from django.urls import path
from . import views


urlpatterns = [
    path('', views.contact, name='contact'),
    path('contact/post', views.post_contact, name='post_contact'),
    path('newsletter/post', views.post_newsletter, name='post_newsletter'),
]
