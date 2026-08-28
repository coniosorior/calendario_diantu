# Diantu — Modelos de Datos

> Documento de referencia para desarrollo humano y agentic coding (IA). Contiene las definiciones completas de modelos, sus relaciones, decisiones de diseño y el razonamiento detrás de cada una. Basado en Django 6.

---

## Regla de idioma (norma general del proyecto)

Esta regla aplica a **todo** el código de Diantu, no solo a los modelos:

| Elemento | Idioma | Ejemplo |
|---|---|---|
| Nombres de clases, variables, funciones, campos de modelo | **Inglés** | `class Category`, `owner`, `is_default` |
| Docstrings y comentarios en el código | **Español**, breves y concisos, solo cuando aportan claridad (no comentar lo obvio) | `"""Categoría que clasifica un bloque de tiempo."""` |
| Mensajes de error/validación al usuario | **Español** | `'El color debe ser un código hexadecimal válido.'` |
| `verbose_name`, `verbose_name_plural`, y toda la interfaz visible | **Español** | `verbose_name = 'Categoría'` |

---

## Contexto del proyecto

Diantu es un planificador diario que divide el día en bloques de tiempo. Cada usuario tiene sus propios bloques, categorías e ideas sin horario (inbox). Los modelos viven distribuidos en tres apps:

- `apps/planner/models.py` → `Block`, `InboxItem`
- `apps/categories/models.py` → `Category`
- `apps/accounts/models.py` → `Profile` (extiende User con preferencias)

---

## Modelo `Category` (`apps/categories/models.py`)

```python
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
        Esta es la categoría de respaldo usada por reassign_to_default_category en Block.category.
        """
        if self.is_default:
            raise ValidationError('La categoría "Otros" no puede eliminarse.')
        super().delete(*args, **kwargs)
```

### Categorías predeterminadas (paleta oficial de Diantu)

Estas se crean automáticamente para cada usuario nuevo mediante una señal `post_save` en `User` (ver `diantu-autenticacion.md`):

| name | color | icon | is_default |
|---|---|---|---|
| Trabajo/Estudio | `#006EE9` | `ti-briefcase` | False |
| Ejercicio | `#FB5607` | `ti-run` | False |
| Salud | `#8338EC` | `ti-stethoscope` | False |
| Dormir | `#415A77` | `ti-moon` | False |
| Comida | `#8BC34A` | `ti-tools-kitchen-2` | False |
| Descanso | `#FFBC42` | `ti-coffee` | False |
| Personal | `#EA638C` | `ti-heart` | False |
| Otros | `#8B909A` | `ti-bulb` | **True** |

---

## Modelo `Profile` (`apps/accounts/models.py`)

```python
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
```

`Profile` se crea junto con las categorías predeterminadas dentro de la misma señal `post_save` sobre `User` (ver `apps/categories/signals.py` y `diantu-autenticacion.md`) — cuando `created=True`, además de las 8 `Category` se ejecuta `Profile.objects.create(user=instance)`. Sus 3 campos son preferencias de usuario, todas con valor por defecto:

- `time_format`: formato de hora preferido (`12h` o `24h`).
- `first_day_of_week`: primer día de la semana en el calendario (`mon` o `sun`).
- `timezone`: zona horaria del usuario en formato IANA.

---

## Modelo `Block` (`apps/planner/models.py`)

```python
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.categories.models import Category


def reassign_to_default_category(collector, field, sub_objs, using):
    """
    on_delete personalizado para Block.category. Reemplaza a SET_DEFAULT,
    que no sirve aquí porque el reemplazo ("Otros") es distinto por usuario,
    no un valor fijo global.

    Cuando se borra una Category, todos sus Block comparten el mismo owner
    que ella (BlockForm limita las categorías disponibles a las del propio
    usuario) — así que basta el owner del primer sub_obj para encontrar
    la "Otros" correcta.
    """
    if not sub_objs:
        return
    owner = sub_objs[0].owner
    fallback = Category.objects.get(owner=owner, is_default=True)
    collector.add_field_update(field, fallback, sub_objs)


class Block(models.Model):
    """
    Un bloque de tiempo dentro del día de un usuario. Es la unidad central
    de Diantu — representa una actividad con hora de inicio y fin.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocks',
    )
    category = models.ForeignKey(
        Category,
        on_delete=reassign_to_default_category,
        related_name='blocks',
    )
    title = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    has_alarm = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bloque'
        verbose_name_plural = 'Bloques'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} — {self.date} {self.start_time}-{self.end_time}"

    def clean(self):
        """Validación a nivel de modelo, además de la validación del form."""
        if self.end_time <= self.start_time:
            raise ValidationError(
                'La hora de fin debe ser posterior a la hora de inicio.'
            )

    @property
    def duration_minutes(self):
        """Duración del bloque en minutos, calculada dinámicamente."""
        from datetime import datetime, date as date_cls
        start = datetime.combine(date_cls.min, self.start_time)
        end = datetime.combine(date_cls.min, self.end_time)
        return int((end - start).total_seconds() / 60)
```

> ⚠️ **Nota sobre el on_delete personalizado de `Block.category`:** Django exige un valor fijo en `on_delete=SET_DEFAULT`, pero la categoría "Otros" es distinta para cada usuario (no hay una única fila global) — por eso no se puede usar esa constante. La solución es pasar una **función propia** como `on_delete` (`reassign_to_default_category`, definida arriba), que Django ejecuta automáticamente cada vez que se borra una `Category`, sin importar desde dónde se dispare el borrado (admin, un futuro comando, etc.) — evita tener que repetir la lógica de reasignación en cada lugar que pudiera eliminar una categoría. `Category.delete()` sigue bloqueando el borrado de `is_default=True` como defensa adicional a nivel de modelo. Hoy, la única vía real de borrar una categoría no-default es `/admin/`, exclusiva de la desarrolladora (ver `diantu-admin.md`) — no existe ninguna vista de este tipo en la app de usuario final.

---

## Modelo `InboxItem` (`apps/planner/models.py`)

```python
class InboxItem(models.Model):
    """
    Idea o tarea sin horario asignado. Vive en el panel Inbox hasta que el
    usuario la mueve al timeline (creando un Block a partir de ella).
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inbox_items',
    )
    title = models.CharField(max_length=100)
    estimated_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Duración estimada en minutos. Opcional.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Idea del Inbox'
        verbose_name_plural = 'Ideas del Inbox'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
```

---

## Resumen de relaciones

```
User (Django nativo)
  │
  ├── 1:1 → Profile     (user)
  ├── 1:N → Category   (owner)
  ├── 1:N → Block       (owner)
  └── 1:N → InboxItem   (owner)

Category
  └── 1:N → Block       (category)
```

## Resumen de decisiones de `on_delete`

| Relación | on_delete | Razón |
|---|---|---|
| `Category.owner → User` | `CASCADE` | Si se borra el usuario, sus categorías no tienen sentido sin él |
| `Block.owner → User` | `CASCADE` | Igual razón — no quedan bloques huérfanos |
| `Block.category → Category` | Función personalizada (`reassign_to_default_category`) | No perder datos del usuario al borrar una categoría; los bloques se reasignan automáticamente a "Otros" del mismo usuario, sin importar desde dónde se dispare el borrado |
| `InboxItem.owner → User` | `CASCADE` | Igual razón que arriba |
| `Profile.user → User` | `CASCADE` | Si se borra el usuario, su perfil de preferencias no tiene sentido sin él |

---

## Campos que requieren `blank`/`null` — checklist aplicado

Siguiendo la distinción de la clase de modelos: `null` afecta la base de datos, `blank` afecta la validación de formularios.

| Campo | blank | null | Razón |
|---|---|---|---|
| `Category.name`, `color`, `icon` | No | No | Obligatorios siempre |
| `Block.note` | `True` | No (usa `''` por defecto en texto) | Campo de texto opcional — se guarda como string vacío, no NULL |
| `InboxItem.estimated_duration` | `True` | `True` | Campo numérico opcional — puede no tener valor, requiere NULL real |

---

## Comandos de migración

```bash
python manage.py makemigrations categories
python manage.py makemigrations planner
python manage.py migrate
```

> Las apps `categories` y `planner` deben crearse en ese orden porque `Block` depende de `Category` mediante ForeignKey.

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-vistas-urls.md`, `diantu-formularios.md`.*
