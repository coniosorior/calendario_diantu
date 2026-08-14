from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
]
