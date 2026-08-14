from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Profile


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='claveSegura123')

    def test_profile_se_crea_al_registrar_usuario(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_valores_por_defecto(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.time_format, '24h')
        self.assertEqual(profile.first_day_of_week, 'mon')
        self.assertEqual(profile.timezone, 'America/Santiago')

    def test_str_representation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'Perfil de ana')

    def test_relacion_one_to_one_con_user(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(self.user.profile, profile)
        self.assertEqual(profile.user, self.user)
