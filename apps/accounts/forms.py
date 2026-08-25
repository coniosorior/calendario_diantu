from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegistroForm(UserCreationForm):
    """
    Extiende UserCreationForm de Django agregando el campo email como
    obligatorio. El formulario nativo de Django no lo incluye por defecto,
    pero Diantu lo necesita para futuras funcionalidades de recuperación
    de cuenta (ver diantu-autenticacion.md).
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'nombre@ejemplo.com',
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'tu_usuario',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Mínimo 8 caracteres',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Repite tu contraseña',
        })
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class LoginForm(AuthenticationForm):
    """
    Extiende AuthenticationForm de Django solo para agregar las clases CSS
    a los campos username/password, ya que el formulario nativo no las trae.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'tu_usuario',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Tu contraseña',
        })
