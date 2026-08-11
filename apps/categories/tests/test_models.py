from django.test import TestCase
from django.contrib.auth.models import User
from apps.categories.models import Category


class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='claveSegura123')

    def test_str_representation(self):
        cat = Category.objects.create(
            owner=self.user, name='Trabajo', color='#006EE9', icon='ti-briefcase'
        )
        self.assertEqual(str(cat), 'Trabajo (ana)')

    def test_categorias_predeterminadas_se_crean_al_registrar(self):
        """
        Verifica que la señal post_save (ver diantu-autenticacion.md)
        creó las 8 categorías predeterminadas automáticamente.
        """
        categorias = Category.objects.filter(owner=self.user)
        self.assertEqual(categorias.count(), 8)

    def test_categoria_otros_es_default(self):
        otros = Category.objects.get(owner=self.user, name='Otros')
        self.assertTrue(otros.is_default)

    def test_no_se_puede_eliminar_categoria_otros(self):
        otros = Category.objects.get(owner=self.user, name='Otros')
        with self.assertRaises(Exception):
            otros.delete()

    def test_nombre_unico_por_usuario(self):
        with self.assertRaises(Exception):
            Category.objects.create(
                owner=self.user, name='Otros', color='#000000', icon='ti-bulb'
            )

    def test_mismo_nombre_permitido_entre_usuarios_distintos(self):
        """Dos usuarios distintos SÍ pueden tener una categoría con el mismo nombre."""
        otro_user = User.objects.create_user(username='beto', password='claveSegura123')
        # 'Trabajo' ya existe para self.user (predeterminada) y para otro_user también
        cat_ana = Category.objects.get(owner=self.user, name='Trabajo/Estudio')
        cat_beto = Category.objects.get(owner=otro_user, name='Trabajo/Estudio')
        self.assertNotEqual(cat_ana.pk, cat_beto.pk)
