from django.db import models


class TimestampedModel(models.Model):
    """
    Modelo base abstracto con fecha de creación y última actualización.
    Otros modelos del proyecto heredan de esta clase en vez de repetir
    estos dos campos cada vez.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContactMessage(TimestampedModel):
    """
    Mensaje enviado desde el formulario público de contacto. No requiere
    que el usuario tenga sesión iniciada.
    """

    TYPE_CHOICES = [
        ('problema', 'Reportar un problema'),
        ('sugerencia', 'Sugerencia para la app'),
        ('otra', 'Otra consulta o solicitud'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='tipo de mensaje')
    message = models.TextField()
    resolved = models.BooleanField(default=False, verbose_name='resuelto')

    class Meta:
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'

    def __str__(self):
        return f"{self.name} — {self.get_message_type_display()}"
