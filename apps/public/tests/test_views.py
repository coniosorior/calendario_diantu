from django.test import TestCase
from django.urls import reverse
from apps.public.models import ContactMessage


class LandingViewTest(TestCase):
    def test_landing_status_200(self):
        response = self.client.get(reverse('public:landing'))
        self.assertEqual(response.status_code, 200)


class PrivacyViewTest(TestCase):
    def test_privacy_status_200(self):
        response = self.client.get(reverse('public:privacy'))
        self.assertEqual(response.status_code, 200)


class ContactViewTest(TestCase):
    def test_contact_status_200_get(self):
        response = self.client.get(reverse('public:contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_post_valido_crea_mensaje(self):
        data = {
            'name': 'Ana',
            'email': 'ana@ejemplo.com',
            'message_type': 'problema',
            'message': 'Encontré un error en la app.',
        }
        response = self.client.post(reverse('public:contact'), data=data)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertRedirects(response, reverse('public:contact'))

    def test_contact_post_invalido_no_crea_mensaje(self):
        data = {
            'name': '',
            'email': 'correo-invalido',
            'message_type': 'problema',
            'message': '',
        }
        response = self.client.post(reverse('public:contact'), data=data)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
