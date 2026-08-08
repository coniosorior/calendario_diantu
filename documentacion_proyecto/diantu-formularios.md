# Diantu — Formularios (ModelForms)

> Documento de referencia para desarrollo humano y agentic coding (IA). Define los `ModelForm` de Diantu, sus widgets, y las validaciones personalizadas necesarias para el negocio (solapamiento de horarios, categoría protegida, etc.).

---

## `BlockForm` (`apps/planner/forms.py`)

```python
from django import forms
from django.core.exceptions import ValidationError
from apps.categories.models import Category
from .models import Block


class BlockForm(forms.ModelForm):
    """
    Formulario de creación/edición de un bloque de tiempo.

    Recibe `owner` en el __init__ (no es un campo del modelo) para:
    1. Filtrar el queryset de `category` solo a las categorías del usuario.
    2. Validar solapamiento de horarios contra los bloques existentes
       de ese mismo usuario.
    """

    class Meta:
        model = Block
        fields = ['title', 'date', 'start_time', 'end_time', 'category', 'has_alarm', 'note']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Trabajo, Ejercicio, Estudio...',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time',
            }),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'has_alarm': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Nota opcional...',
            }),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner
        if owner is not None:
            self.fields['category'].queryset = Category.objects.filter(owner=owner)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        block_date = cleaned_data.get('date')

        if start and end and end <= start:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

        if start and end and block_date and self.owner:
            self._validar_solapamiento(block_date, start, end)

        return cleaned_data

    def _validar_solapamiento(self, block_date, start, end):
        """
        Un bloque se solapa con otro si su inicio es anterior al fin del
        otro Y su fin es posterior al inicio del otro. Se excluye el
        propio bloque cuando se está editando (self.instance.pk).
        """
        qs = Block.objects.filter(owner=self.owner, date=block_date)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        solapados = qs.filter(start_time__lt=end, end_time__gt=start)
        if solapados.exists():
            bloque_existente = solapados.first()
            raise ValidationError(
                f'Este horario se superpone con "{bloque_existente.title}" '
                f'({bloque_existente.start_time.strftime("%H:%M")} - '
                f'{bloque_existente.end_time.strftime("%H:%M")}).'
            )
```

> 💡 **Por qué `owner` se pasa por `__init__` y no es un campo del modelo:** el `owner` de un `Block` nunca lo elige el usuario en el formulario — se asigna automáticamente en la vista (`block.owner = request.user`). Pasarlo al form permite filtrar `category` y validar solapamiento sin exponer ese campo en el HTML.

---

## `InboxItemForm` (`apps/planner/forms.py`)

```python
class InboxItemForm(forms.ModelForm):
    class Meta:
        model = InboxItem
        fields = ['title', 'estimated_duration']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '¿Qué tienes en mente?',
            }),
            'estimated_duration': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Duración estimada en minutos (opcional)',
            }),
        }
```

---

> `CategoryForm` ya no existe — las categorías son fijas (8 predeterminadas), sin creación ni edición desde la app de usuario final. Ver `diantu-vistas-urls.md` y `diantu-admin.md`.

---

## Template genérico de formulario (patrón reutilizable)

Aplica para `BlockForm` (y cualquier futuro ModelForm de la app `planner`), siguiendo la convención de la clase de formularios (sin CSS embebido, con `{% csrf_token %}` obligatorio):

```html
{% extends "base.html" %}
{% load static %}

{% block titulo %}{{ titulo }}{% endblock %}

{% block contenido %}
<div class="form-card">
    <h1>{{ titulo }}</h1>

    <form method="post" novalidate>
        {% csrf_token %}

        {% if form.non_field_errors %}
        <div class="form-error-banner">
            {% for error in form.non_field_errors %}
            <p>{{ error }}</p>
            {% endfor %}
        </div>
        {% endif %}

        {% for field in form %}
        <div class="form-group">
            <label for="{{ field.id_for_label }}" class="form-label">{{ field.label }}</label>
            {{ field }}
            {% if field.errors %}
            <div class="form-field-error">
                {% for error in field.errors %}
                <p>{{ error }}</p>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endfor %}

        <div class="form-actions">
            <button type="submit" class="btn-primary">Guardar</button>
            <a href="{% url 'planner:day' %}" class="btn-secondary">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

---

## Checklist de validación por formulario

| Formulario | Validación | Nivel |
|---|---|---|
| `BlockForm` | `end_time > start_time` | `clean()` |
| `BlockForm` | Sin solapamiento con otros bloques del mismo día/usuario | `clean()` |
| `BlockForm` | `category` limitada a las del usuario logueado | `__init__` (queryset) |

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-modelos.md`, `diantu-vistas-urls.md`.*
