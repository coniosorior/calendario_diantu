from django.db import models
from django.conf import settings


class Profile(models.Model):
    """
    Extiende al usuario nativo de Django con preferencias que User
    no contempla. Se crea automáticamente junto con el User (misma
    señal post_save que crea las categorías predeterminadas).
    """

    TIME_FORMAT_CHOICES = [
        ('12h', '12 horas'),
        ('24h', '24 horas'),
    ]
    FIRST_DAY_CHOICES = [
        ('mon', 'Lunes'),
        ('sun', 'Domingo'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    time_format = models.CharField(
        max_length=3,
        choices=TIME_FORMAT_CHOICES,
        default='24h',
    )
    first_day_of_week = models.CharField(
        max_length=3,
        choices=FIRST_DAY_CHOICES,
        default='mon',
    )
    timezone = models.CharField(
        max_length=50,
        default='America/Santiago',
        help_text='Zona horaria en formato IANA, ej: America/Santiago',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f"Perfil de {self.user.username}"
