# Diantu — Panel de Administración

> Documento de referencia para desarrollo humano y agentic coding (IA). Define cómo se registran y personalizan los modelos de Diantu en el panel `/admin/`, y su propósito exclusivo como herramienta de desarrollo.

---

## Propósito del admin en Diantu

El panel de administración **no es parte de la experiencia de usuario final** de Diantu — ningún usuario normal accede a `/admin/`. Su único propósito es servir como herramienta de trabajo para la persona desarrolladora: revisar datos directamente, depurar errores, verificar que las señales (categorías predeterminadas) se ejecutaron correctamente, y hacer ajustes puntuales sin escribir queries manuales.

Ver `diantu-autenticacion.md` para la distinción entre superusuario (usa el admin) y usuario normal (usa la app).

---

## `apps/categories/admin.py`

```python
from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'color', 'icon', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name', 'owner__username')
    ordering = ('owner', 'name')
    show_facets = admin.ShowFacets.ALWAYS
```

> **Estado actual de `apps/accounts/admin.py`:** el archivo existe pero está vacío (solo el boilerplate `# Register your models here.` que genera Django). El modelo `Profile` (ver `diantu-modelos.md`) todavía no está registrado en el admin.

---

## `apps/planner/admin.py`

```python
from django.contrib import admin
from .models import Block, InboxItem


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'date', 'start_time', 'end_time', 'completed', 'has_alarm')
    list_filter = ('date', 'category', 'completed', 'has_alarm')
    search_fields = ('title', 'owner__username', 'note')
    list_editable = ('completed',)
    date_hierarchy = 'date'
    ordering = ('-date', 'start_time')

    fieldsets = (
        ('Información básica', {
            'fields': ('owner', 'title', 'category'),
        }),
        ('Horario', {
            'fields': ('date', 'start_time', 'end_time'),
        }),
        ('Estado', {
            'fields': ('completed', 'has_alarm', 'note'),
        }),
    )


@admin.register(InboxItem)
class InboxItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'estimated_duration', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'owner__username')
    ordering = ('-created_at',)
```

---

## Tabla de opciones de personalización usadas

| Opción | Qué hace | Dónde se usa en Diantu |
|---|---|---|
| `list_display` | Columnas visibles en la lista | Todos los modelos |
| `list_filter` | Filtros laterales | `is_default` en Category; `date`, `category`, `completed` en Block |
| `search_fields` | Campos donde busca la barra de búsqueda | Nombre + username del owner en todos |
| `list_editable` | Campos editables directo desde la lista | `completed` en Block — marcar como hecho sin entrar al detalle |
| `date_hierarchy` | Navegación rápida por fecha arriba de la lista | `date` en Block |
| `fieldsets` | Agrupa campos del formulario en secciones | Block, para separar horario de estado |
| `show_facets` | Muestra conteo por filtro (Django 5.0+) | Todos |
| `ordering` | Orden por defecto de la lista | Todos |

---

## Crear el superusuario

```bash
python manage.py createsuperuser
```

Solicita: nombre de usuario, correo electrónico (opcional, puede dejarse vacío), contraseña (mínimo 8 caracteres, Django valida automáticamente robustez y similitud con el username).

Acceso: `http://127.0.0.1:8000/admin/`

---

## Advertencia sobre el uso del admin durante el desarrollo

El admin muestra **todos los datos de todos los usuarios** sin el filtro `owner=request.user` que sí aplican las vistas de la app (ver `diantu-vistas-urls.md`). Esto es intencional y correcto para el admin — un superusuario necesita ver todo. Pero significa que probar únicamente desde el admin **no valida** que el aislamiento de datos por usuario funcione correctamente en la app real. Para eso se necesita probar con usuarios normales o, mejor aún, escribir tests automatizados (ver `diantu-testing.md`).

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-modelos.md`, `diantu-autenticacion.md`.*
