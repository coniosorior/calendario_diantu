from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('contacto/', views.contact, name='contact'),
    path('privacidad/', views.privacy, name='privacy'),
]
