from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from apps.accounts.models import Profile
from .models import Category

DEFAULT_CATEGORIES = [
    {'name': 'Trabajo/Estudio', 'color': '#006EE9', 'icon': 'ti-briefcase', 'is_default': False},
    {'name': 'Ejercicio',       'color': '#FB5607', 'icon': 'ti-run',        'is_default': False},
    {'name': 'Salud',           'color': '#8338EC', 'icon': 'ti-stethoscope', 'is_default': False},
    {'name': 'Dormir',          'color': '#415A77', 'icon': 'ti-moon',        'is_default': False},
    {'name': 'Comida',          'color': '#8BC34A', 'icon': 'ti-tools-kitchen-2', 'is_default': False},
    {'name': 'Descanso',        'color': '#FFBC42', 'icon': 'ti-coffee',      'is_default': False},
    {'name': 'Personal',        'color': '#EA638C', 'icon': 'ti-heart',       'is_default': False},
    {'name': 'Otros',           'color': '#8B909A', 'icon': 'ti-bulb',        'is_default': True},
]


@receiver(post_save, sender=User)
def crear_categorias_predeterminadas(sender, instance, created, **kwargs):
    """
    Se ejecuta automáticamente cada vez que se guarda un User.
    `created=True` solo la primera vez (cuando el usuario se registra),
    por eso el if — evita duplicar categorías en cada login o edición
    de perfil. Crea las 8 categorías predeterminadas y el Profile
    del usuario nuevo, con los valores por defecto del modelo.
    """
    if created:
        categorias = [
            Category(owner=instance, **data) for data in DEFAULT_CATEGORIES
        ]
        Category.objects.bulk_create(categorias)
        Profile.objects.create(user=instance)
