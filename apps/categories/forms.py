from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Lectura, Voluntariado...',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-input color-picker',
                'type': 'color',
            }),
            'icon': forms.Select(attrs={'class': 'form-input'}),
            # El widget real de 'icon' se define con choices en el propio
            # campo del formulario si se quiere restringir a un set fijo
            # de íconos de Tabler (ver nota abajo).
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return name

    def clean_color(self):
        color = self.cleaned_data.get('color', '')
        if not color.startswith('#') or len(color) != 7:
            raise forms.ValidationError('El color debe ser un código hexadecimal válido, ej: #06D6A0.')
        return color
