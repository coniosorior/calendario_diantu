# Diantu — Autenticación y Autorización

> Documento de referencia para desarrollo humano y agentic coding (IA). Define el flujo completo de registro, login, logout, y la señal que crea las categorías predeterminadas para cada usuario nuevo.

---

## Decisión de diseño: usuario + contraseña (no correo)

Diantu usa el sistema de autenticación nativo de Django — login con `username` + `password`, no con correo electrónico. El formulario de login (`LoginForm`) extiende `AuthenticationForm` únicamente para agregar clases CSS a los campos, sin modificar la lógica de autenticación. Esto evita tener que crear un backend de autenticación personalizado, que añade complejidad innecesaria para un proyecto de este tamaño. El correo se solicita en el registro únicamente para futuras funcionalidades de recuperación de cuenta.

---

## URLs de autenticación

Django provee automáticamente login, logout y cambio de contraseña al incluir sus URLs nativas:

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from apps.accounts.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/login/', LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('cuentas/logout/', LogoutView.as_view(), name='logout'),
    path('cuentas/password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('cuentas/password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('cuentas/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('cuentas/password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('cuentas/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('cuentas/reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('cuentas/', include('apps.accounts.urls')),
    path('categorias/', include('apps.categories.urls')),
]
```

| URL | Nombre | Función | Origen |
|---|---|---|---|
| `/cuentas/login/` | `login` | Iniciar sesión — usa `LoginForm` (custom, no el formulario nativo sin modificar) | Django nativo (form custom) |
| `/cuentas/logout/` | `logout` | Cerrar sesión | Django nativo |
| `/cuentas/password_change/` | `password_change` | Cambiar contraseña | Django nativo |
| `/cuentas/password_reset/` | `password_reset` | Recuperar contraseña vía correo | Django nativo |
| `/cuentas/registro/` | `accounts:registro` | Crear cuenta nueva | Custom (Diantu) |
| `/cuentas/eliminar-cuenta/` | `accounts:eliminar_cuenta` | Eliminar cuenta (soft delete) | Custom (Diantu) |

---

## Settings de autenticación (`config/settings/base.py`)

```python
LOGIN_REDIRECT_URL = 'planner:day'      # a dónde va el usuario tras iniciar sesión
LOGOUT_REDIRECT_URL = 'login'            # a dónde va tras cerrar sesión
LOGIN_URL = 'login'                       # a dónde se redirige si @login_required falla
```

Además, `config/settings/base.py` define `AUTH_PASSWORD_VALIDATORS` (la lista estándar de Django: similitud con datos del usuario, longitud mínima, contraseñas comunes, contraseñas solo numéricas). Es relevante para el flujo de registro: `RegistroForm` hereda de `UserCreationForm`, que ejecuta estos validadores automáticamente al crear la cuenta — por eso una contraseña débil o muy similar al username hace fallar el registro antes de llegar a la señal `post_save`.

---

## Vista de registro (`apps/accounts/views.py`)

Ya definida en `diantu-vistas-urls.md`, se repite aquí con foco en el flujo de autenticación:

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import RegistroForm


def registro(request):
    """
    FBV porque además de crear el User, dispara la creación de las
    categorías predeterminadas mediante la señal post_save (ver
    diantu-autenticacion.md). No es un CRUD estándar de Django.
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()  # ← dispara la señal post_save (ver abajo)
            messages.success(request, f'Cuenta creada. ¡Bienvenido a Diantu, {user.username}!')
            return redirect('login')
        else:
            messages.error(request, 'Revisa los datos ingresados.')
    else:
        form = RegistroForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
@require_POST
def eliminar_cuenta(request):
    """
    Solo responde a POST para que la baja de cuenta nunca se dispare
    por accidente con un simple link (GET).
    """
    user = request.user
    user.is_active = False
    user.save()
    logout(request)
    messages.success(request, 'Tu cuenta fue eliminada. ¡Gracias por usar Diantu!')
    return redirect('login')
```

---

## Señal: crear categorías predeterminadas al registrarse

Esta es la pieza más importante del flujo de autenticación de Diantu. Cuando un `User` nuevo se crea, se disparan automáticamente las 8 categorías predeterminadas (ver `diantu-modelos.md` para la tabla completa).

### `apps/categories/signals.py`

```python
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from apps.accounts.models import Profile
from .models import Category

DEFAULT_CATEGORIES = [
    {'name': 'Trabajo/Estudio', 'color': '#006EE9', 'icon': 'ti-briefcase', 'is_default': False},
    {'name': 'Ejercicio',       'color': '#FB5607', 'icon': 'ti-run',        'is_default': False},
    {'name': 'Salud',           'color': '#8338EC', 'icon': 'ti-stethoscope', 'is_default': False},
    {'name': 'Dormir',          'color': '#415A76', 'icon': 'ti-moon',        'is_default': False},
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
```

### Registro obligatorio de la señal en `apps/categories/apps.py`

```python
from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.categories'

    def ready(self):
        import apps.categories.signals  # noqa: F401 — necesario para que la señal se registre
```

> ⚠️ **Error común a evitar:** si `signals.py` no se importa dentro de `ready()`, la señal **nunca se conecta** y las categorías predeterminadas jamás se crean, aunque el código de `signals.py` sea correcto. Este es el paso que más se olvida al implementar señales en Django.

---

## Proteger vistas con `@login_required`

Todas las vistas de `planner` y las vistas custom de `categories` deben estar protegidas:

```python
from django.contrib.auth.decorators import login_required

@login_required
def day_view(request, date_str=None):
    ...
```

Para CBV, se usa el mixin equivalente:

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class CategoryListView(LoginRequiredMixin, ListView):
    ...
```

Si el usuario no está autenticado, Django lo redirige automáticamente a `LOGIN_URL` con un parámetro `?next=` para volver a la página solicitada tras iniciar sesión.

---

## Acceder al usuario en templates

```html
{% if user.is_authenticated %}
    <p>Hola, {{ user.username }}</p>
    <a href="{% url 'logout' %}">Cerrar sesión</a>
{% else %}
    <a href="{% url 'login' %}">Iniciar sesión</a>
{% endif %}
```

---

## Diferencia entre superusuario y usuario normal (uso en desarrollo)

| Tipo | Se crea con | Propósito en Diantu |
|---|---|---|
| **Superusuario** | `python manage.py createsuperuser` | Acceso al panel `/admin/` para revisar y depurar datos directamente en la base de datos. Nunca se usa para "probar la app como usuario final". |
| **Usuario normal** | Formulario de registro de Diantu (`/cuentas/registro/`) | Simula la experiencia real de cualquier persona: crear bloques, ver el timeline, probar login/logout, verificar alarmas. |

Se recomienda mantener ambos durante el desarrollo: un superusuario fijo (ej. `admin`) y al menos un usuario de prueba normal para validar el flujo real de principio a fin, incluyendo la verificación de que los bloques de un usuario nunca sean visibles ni editables por otro (ver el patrón `owner=request.user` en `diantu-vistas-urls.md`).

---

## Template de login personalizado

Django usa `registration/login.html` por defecto. Para que coincida con el diseño de Diantu, se sobreescribe en `templates/registration/login.html`:

```html
{% extends "base.html" %}
{% load static %}

{% block titulo %}Iniciar sesión — Diantú{% endblock %}

{% block main_extra_class %}app-main--center{% endblock %}

{% block contenido %}
<div class="auth-card">
    <h1>Iniciar sesión</h1>
    <p class="auth-subtitle">Ingresa a tu cuenta para continuar.</p>

    {% if form.non_field_errors %}
    <div class="form-error-banner">
        {% for error in form.non_field_errors %}
        <p>{{ error }}</p>
        {% endfor %}
    </div>
    {% endif %}

    <form method="post" novalidate>
        {% csrf_token %}

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

        <button type="submit" class="btn-primary">Ingresar</button>
    </form>

    <p class="auth-hint">¿No tienes cuenta? <a href="{% url 'accounts:registro' %}">Regístrate</a></p>
</div>
{% endblock %}
```

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-modelos.md`, `diantu-vistas-urls.md`, `diantu-testing.md`, `diantu-formularios.md`.*
