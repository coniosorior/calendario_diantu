from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Category(models.Model):
    """
    Categoría que clasifica un bloque de tiempo. Cada usuario tiene su propio
    set de categorías. Al registrarse un usuario, se le crean automáticamente
    las 8 categorías predeterminadas de Diantu (ver signals.py).
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
    )
    name = models.CharField(max_length=50)
    color = models.CharField(
        max_length=7,
        help_text='Color hexadecimal, ej: #006EE9',
    )
    icon = models.CharField(
        max_length=50,
        help_text='Nombre del ícono de Tabler Icons, ej: ti-briefcase',
    )
    is_default = models.BooleanField(
        default=False,
        help_text='True solo para la categoría "Otros". No se puede eliminar.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_category_name_per_owner',
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def delete(self, *args, **kwargs):
        """
        Impide eliminar la categoría 'Otros' (is_default=True) desde el ORM.
        Esta es la categoría de respaldo para SET_DEFAULT en Block.category.
        """
        if self.is_default:
            raise ValidationError('La categoría "Otros" no puede eliminarse.')
        super().delete(*args, **kwargs)
