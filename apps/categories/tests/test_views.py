from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.categories.models import Category


class CategoryListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ana', password='claveSegura123')
        self.other_user = User.objects.create_user(username='beto', password='claveSegura123')
        self.client.login(username='ana', password='claveSegura123')

    def test_lista_requiere_login(self):
        self.client.logout()
        response = self.client.get(reverse('categories:list'))
        self.assertEqual(response.status_code, 302)  # redirige a login

    def test_lista_status_200(self):
        response = self.client.get(reverse('categories:list'))
        self.assertEqual(response.status_code, 200)

    def test_lista_solo_muestra_categorias_propias(self):
        """
        CRÍTICO: un usuario nunca debe ver categorías de otro usuario,
        aunque tengan el mismo nombre (ej: ambos tienen 'Otros').
        """
        response = self.client.get(reverse('categories:list'))
        categorias_mostradas = response.context['categories']
        for cat in categorias_mostradas:
            self.assertEqual(cat.owner, self.user)
