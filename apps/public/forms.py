from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Formulario público de contacto. No requiere que el usuario tenga
    sesión iniciada.
    """

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form__input',
                'placeholder': 'Tu nombre',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form__input',
                'placeholder': 'nombre@ejemplo.com',
            }),
            'message_type': forms.Select(attrs={
                'class': 'form__input',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form__input',
                'placeholder': 'Escribe tu mensaje aquí...',
                'rows': 5,
            }),
        }
        labels = {
            'name': 'Nombre',
            'email': 'Correo electrónico',
            'message_type': 'Tipo de solicitud',
            'message': 'Mensaje',
        }
