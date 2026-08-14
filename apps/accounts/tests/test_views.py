from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.categories.models import Category


class RegistroTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registro_status_200_get(self):
        response = self.client.get(reverse('accounts:registro'))
        self.assertEqual(response.status_code, 200)

    def test_registro_crea_usuario(self):
        response = self.client.post(reverse('accounts:registro'), data={
            'username': 'nuevo_usuario',
            'email': 'nuevo@ejemplo.com',
            'password1': 'claveSegura123',
            'password2': 'claveSegura123',
        })
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())

    def test_registro_dispara_creacion_de_categorias(self):
        self.client.post(reverse('accounts:registro'), data={
            'username': 'nuevo_usuario',
            'email': 'nuevo@ejemplo.com',
            'password1': 'claveSegura123',
            'password2': 'claveSegura123',
        })
        user = User.objects.get(username='nuevo_usuario')
        self.assertEqual(Category.objects.filter(owner=user).count(), 8)

    def test_registro_password_no_coincidentes_falla(self):
        response = self.client.post(reverse('accounts:registro'), data={
            'username': 'otro_usuario',
            'email': 'otro@ejemplo.com',
            'password1': 'claveSegura123',
            'password2': 'claveDiferente456',
        })
        self.assertFalse(User.objects.filter(username='otro_usuario').exists())


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ana', password='claveSegura123')

    def test_login_correcto_redirige_a_day(self):
        response = self.client.post(reverse('login'), data={
            'username': 'ana',
            'password': 'claveSegura123',
        })
        self.assertRedirects(response, reverse('planner:day'))

    def test_login_incorrecto_no_autentica(self):
        response = self.client.post(reverse('login'), data={
            'username': 'ana',
            'password': 'claveIncorrecta',
        })
        self.assertFalse(response.wsgi_request.user.is_authenticated)
