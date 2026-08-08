# Diantu — Vistas y URLs

> Documento de referencia para desarrollo humano y agentic coding (IA). Define qué vistas son FBV, cuáles son CBV, y por qué, junto con la estructura completa de URLs por app.

---

## Criterio de decisión FBV vs CBV en Diantu

Regla aplicada en todo el proyecto: **CRUD estándar y repetitivo → CBV. Lógica personalizada y compleja → FBV.** Ambas conviven en el mismo proyecto sin problema.

| App | Vista | Tipo | Razón |
|---|---|---|---|
| `accounts` | Registro | FBV | Lógica custom: crea usuario + categorías predeterminadas |
| `accounts` | Login/Logout | Django nativo (`include('django.contrib.auth.urls')`) | No se reescribe, Django ya lo resuelve |
| `planner` | Vista Día | FBV | Lógica compleja: agrupa bloques, calcula posiciones en el timeline |
| `planner` | Vista Semana | FBV | Lógica compleja: agrupa por día, resume categorías |
| `planner` | Vista Mes | FBV | Lógica compleja: calendario con conteo de bloques por día |
| `planner` | Crear/Editar/Eliminar Block | FBV | Requiere validación custom de solapamiento de horarios |
| `planner` | Inbox (listar/crear/mover a timeline) | FBV | Lógica custom: "mover" es una operación combinada (crear Block + borrar InboxItem) |
| `categories` | Listar Category | **CBV** | Solo lectura, sin CRUD — las 8 categorías son fijas, gestionables únicamente desde `/admin/` |

---

## URLs raíz del proyecto (`config/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('cuentas/', include('apps.accounts.urls')),
    path('', include('apps.planner.urls')),
    path('categorias/', include('apps.categories.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

> Nota: `apps.planner.urls` se monta en la raíz (`''`) porque la vista Día es la página principal de la app una vez logueado.

---

## App `accounts` — URLs y vistas

### `apps/accounts/urls.py`

```python
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
]
```

### `apps/accounts/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm


def registro(request):
    """
    FBV porque además de crear el User, dispara la creación de las
    categorías predeterminadas mediante la señal post_save (ver
    diantu-autenticacion.md). No es un CRUD estándar de Django.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Cuenta creada. ¡Bienvenido a Diantu, {user.username}!')
            return redirect('login')
        else:
            messages.error(request, 'Revisa los datos ingresados.')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})
```

### Settings relacionados (`config/settings/base.py`)

```python
LOGIN_REDIRECT_URL = 'planner:day'
LOGOUT_REDIRECT_URL = 'accounts:registro'  # o una landing pública
LOGIN_URL = 'login'
```

---

## App `planner` — URLs y vistas

### `apps/planner/urls.py`

```python
from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    # Vistas principales
    path('', views.day_view, name='day'),
    path('dia/<str:date_str>/', views.day_view, name='day_detail'),
    path('semana/', views.week_view, name='week'),
    path('mes/', views.month_view, name='month'),

    # CRUD de bloques
    path('bloque/nuevo/', views.block_create, name='block_create'),
    path('bloque/<int:pk>/editar/', views.block_update, name='block_update'),
    path('bloque/<int:pk>/eliminar/', views.block_delete, name='block_delete'),
    path('bloque/<int:pk>/completar/', views.block_toggle_complete, name='block_toggle_complete'),

    # Inbox
    path('inbox/', views.inbox_list, name='inbox_list'),
    path('inbox/nuevo/', views.inbox_create, name='inbox_create'),
    path('inbox/<int:pk>/mover/', views.inbox_move_to_timeline, name='inbox_move'),
    path('inbox/<int:pk>/eliminar/', views.inbox_delete, name='inbox_delete'),
]
```

### `apps/planner/views.py` — vista Día (ejemplo completo)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime, timedelta
from .models import Block, InboxItem
from .forms import BlockForm


@login_required
def day_view(request, date_str=None):
    """
    Vista principal de Diantu. Muestra el timeline vertical del día.
    FBV porque necesita: resolver la fecha desde la URL o usar hoy,
    calcular el bloque "activo" según la hora actual, y traer el
    inbox del usuario en la misma vista.
    """
    if date_str:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        current_date = date.today()

    blocks = (
        Block.objects
        .filter(owner=request.user, date=current_date)
        .select_related('category')
        .order_by('start_time')
    )

    inbox_items = InboxItem.objects.filter(owner=request.user)[:5]

    now = datetime.now().time()
    for block in blocks:
        block.is_active = block.start_time <= now <= block.end_time

    context = {
        'blocks': blocks,
        'inbox_items': inbox_items,
        'current_date': current_date,
        'prev_date': current_date - timedelta(days=1),
        'next_date': current_date + timedelta(days=1),
    }
    return render(request, 'planner/day.html', context)


@login_required
def block_create(request):
    if request.method == 'POST':
        form = BlockForm(request.POST, owner=request.user)
        if form.is_valid():
            block = form.save(commit=False)
            block.owner = request.user
            block.save()
            messages.success(request, 'Bloque creado correctamente.')
            return redirect('planner:day_detail', date_str=block.date.isoformat())
        messages.error(request, 'Revisa los datos del bloque.')
    else:
        form = BlockForm(owner=request.user)

    return render(request, 'planner/block_form.html', {'form': form, 'titulo': 'Nuevo bloque'})


@login_required
def block_update(request, pk):
    block = get_object_or_404(Block, pk=pk, owner=request.user)  # ← filtro por owner es CRÍTICO

    if request.method == 'POST':
        form = BlockForm(request.POST, instance=block, owner=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bloque actualizado.')
            return redirect('planner:day_detail', date_str=block.date.isoformat())
    else:
        form = BlockForm(instance=block, owner=request.user)

    return render(request, 'planner/block_form.html', {'form': form, 'titulo': f'Editar: {block.title}'})


@login_required
def block_delete(request, pk):
    block = get_object_or_404(Block, pk=pk, owner=request.user)
    target_date = block.date

    if request.method == 'POST':
        block.delete()
        messages.success(request, f'Bloque "{block.title}" eliminado.')
        return redirect('planner:day_detail', date_str=target_date.isoformat())

    return render(request, 'planner/block_confirm_delete.html', {'block': block})


@login_required
def block_toggle_complete(request, pk):
    """Marca/desmarca un bloque como completado. Se llama vía POST desde JS (fetch)."""
    block = get_object_or_404(Block, pk=pk, owner=request.user)
    block.completed = not block.completed
    block.save(update_fields=['completed'])
    return redirect('planner:day_detail', date_str=block.date.isoformat())
```

> ⚠️ **Regla de seguridad aplicada en cada vista de detalle/edición/eliminación:** siempre usar `get_object_or_404(Block, pk=pk, owner=request.user)`, nunca `get_object_or_404(Block, pk=pk)`. Sin el filtro `owner=request.user`, cualquier usuario logueado podría editar o borrar bloques de otro usuario cambiando el `pk` en la URL. Este patrón se repite en `InboxItem` y `Category`.

### Inbox — FBV con lógica de "mover"

```python
@login_required
def inbox_move_to_timeline(request, pk):
    """
    Convierte un InboxItem en un Block. Es una operación combinada
    (crear + borrar) que no encaja en ningún CRUD estándar, por eso FBV.
    """
    item = get_object_or_404(InboxItem, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = BlockForm(request.POST, owner=request.user)
        if form.is_valid():
            block = form.save(commit=False)
            block.owner = request.user
            block.save()
            item.delete()
            messages.success(request, f'"{item.title}" movido al timeline.')
            return redirect('planner:day_detail', date_str=block.date.isoformat())
    else:
        form = BlockForm(owner=request.user, initial={'title': item.title})

    return render(request, 'planner/inbox_move_form.html', {'form': form, 'item': item})
```

---

## App `categories` — URLs y vistas (CBV)

Las 8 categorías predeterminadas son fijas — no existe creación, edición ni eliminación desde la app de usuario final. Esa gestión queda reservada al panel `/admin/`, de uso exclusivo de la desarrolladora (ver `diantu-admin.md`).

### `apps/categories/urls.py`

```python
from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='list'),
]
```

### `apps/categories/views.py`

```python
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)
```

---

## Resumen de convención de nombres de URL

| Patrón | Ejemplo |
|---|---|
| Listar | `planner:day`, `categories:list` |
| Detalle con parámetro | `planner:day_detail` con `date_str` |
| Crear | `planner:block_create` |
| Editar | `planner:block_update` |
| Eliminar | `planner:block_delete` |
| Acción custom | `planner:block_toggle_complete`, `planner:inbox_move` |

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-modelos.md`, `diantu-formularios.md`, `diantu-autenticacion.md`.*
