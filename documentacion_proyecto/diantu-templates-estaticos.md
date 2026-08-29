# Diantu — Templates y Archivos Estáticos

> Documento de referencia para desarrollo humano y agentic coding (IA). Define la herencia de templates, el uso de Partials, y la convención de estáticos (CSS/JS) del proyecto.

---

## Reglas fundamentales (no negociables en Diantu)

Heredadas directamente del material de clase y ya acordadas en el proyecto:

1. **Mobile-first absoluto** — todo diseño parte de la vista móvil y escala hacia arriba con `@media` queries.

### Breakpoints oficiales

| Nombre | `min-width` | Rango que cubre | Qué cambia |
|---|---|---|---|
| Base (mobile) | *(ninguno)* | Desde 320px hasta 767px | Diseño de partida — todo en columna, mínimo soportado: 320px (iPhone SE / Android más chicos) |
| Tablet | `768px` | Desde 768px hasta 1023px | A definir según cada página |
| Desktop | `1024px` | Desde 1024px hasta 1439px | A definir según cada página |
| TV/Wide | `1440px` | 1440px en adelante | A definir según cada página |

> **Convención mobile-first:** el CSS de cada componente se define primero para el nivel Base (mobile), y los ajustes para niveles superiores se agregan mediante `@media (min-width: ...)` únicamente cuando la página en cuestión lo requiere. No se declaran bloques `@media` sin reglas dentro.

2. **Cero CSS embebido** — nunca usar el atributo `style=""` en HTML. Todo estilo va en archivos `.css` con clases. Excepción: el atributo `style` es aceptable únicamente cuando contiene una variable CSS dinámica proveniente de datos del usuario (ej. `style="--pill-color: {{ block.category.color }};"`), ya que es la única forma de inyectar un color definido por el usuario sin hardcodear clases para cada posibilidad. No es aceptable usar `style` con propiedades CSS completas y estáticas (ej. `style="color: red; font-size: 14px;"`) — eso siempre debe ir en una clase dentro de un archivo `.css`.
3. **Sistema de componentes** — fragmentos repetidos (la píldora de bloque, la tarjeta de categoría) se extraen con `{% include %}` o Template Partials, nunca se copian y pegan.
4. **`{% load static %}` en cada template que lo necesite** — no se hereda del `base.html`, hay que declararlo en cada archivo que use `{% static %}`.
5. **Nomenclatura BEM para clases CSS** — todo componente sigue la sintaxis Block, Element, Modifier: `.bloque` (el componente en sí, ej. `.btn`, `.form`, `.card`), `.bloque__elemento` (una pieza que vive dentro del bloque, ej. `.form__input`, `.nav__logo`), `.bloque--modificador` (una variante del mismo bloque, ej. `.btn--primary`, `.card--auth`). Se usa un solo guion (`-`) únicamente para separar palabras dentro de un mismo nombre (ej. `.form__help-text`), nunca para indicar relación entre elementos.

---

## `templates/base.html` — template raíz de Diantu

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block titulo %}Diantú{% endblock %}</title>

    {% load static %}
    <link rel="stylesheet" href="{% static 'css/variables.css' %}">
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    <link rel="stylesheet" href="{% static 'css/layout.css' %}">
    <link rel="stylesheet" href="{% static 'css/auth.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/pill.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/button.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/form.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/nav.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/message.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/overlay.css' %}">
    <link rel="stylesheet" href="{% static 'css/components/card.css' %}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css">

    {% block css_extra %}{% endblock %}
</head>
<body>

    {% if user.is_authenticated %}
    <header class="app-nav">
        <a href="#" class="nav-logo">
            {# TODO: volver a planner:day cuando exista planner #}
            <span class="nav-logo-icon"><i class="ti ti-sun"></i></span> Diantú
        </a>
        <nav class="nav-links">
            {% comment %} TODO: descomentar cuando exista apps.planner
            <a href="{% url 'planner:day' %}">Día</a>
            <a href="{% url 'planner:week' %}">Semana</a>
            <a href="{% url 'planner:month' %}">Mes</a>
            {% endcomment %}
            <a href="{% url 'categories:list' %}">Categorías</a>
        </nav>
        <div class="nav-actions">
            {% comment %} TODO: descomentar cuando exista apps.planner
            <a href="{% url 'planner:inbox_list' %}" class="btn-icon"><i class="ti ti-inbox"></i></a>
            {% endcomment %}
            <form method="post" action="{% url 'logout' %}" class="logout-form">
                {% csrf_token %}
                <button type="submit" class="btn-icon"><span class="sr-only">Cerrar sesión</span><i class="ti ti-logout"></i></button>
            </form>
        </div>
    </header>
    {% endif %}

    <main class="app-main {% block main_extra_class %}{% endblock %}">
        {% if messages %}
        <div class="messages-stack">
            {% for message in messages %}
            <div class="message message-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}

        {% block contenido %}{% endblock %}
    </main>

    {% block js_extra %}{% endblock %}
</body>
</html>
```

---

## Estructura de templates por app

```
templates/                          ← globales
├── base.html
├── 404.html
└── 500.html

apps/accounts/templates/accounts/
└── register.html

templates/registration/
└── login.html                      ← sobreescribe la vista nativa LoginView de Django, no vive dentro de accounts/

apps/planner/templates/planner/
├── day.html                        ← vista principal, timeline vertical
├── week.html
├── month.html
├── block_form.html                 ← crear/editar bloque
├── block_confirm_delete.html
├── inbox_list.html
├── inbox_form.html
├── inbox_move_form.html
└── partials/
    └── _block_pill.html            ← la píldora de bloque, reutilizada en day/week

apps/categories/templates/categories/
└── list.html  ← solo lectura, sin crear/editar/eliminar (las categorías son fijas, gestión vía /admin/)
```

---

## Partial reutilizable: la píldora de bloque

Este es el componente que más se repite en Diantu (aparece en `day.html`, potencialmente en `week.html`). Se implementa como `{% include %}` porque se comparte entre **distintos templates**, no solo dentro de uno (ahí sí usaríamos Partials de Django 6).

### `apps/planner/templates/planner/partials/_block_pill.html`

```html
{% load static %}
<div class="pill" style="--pill-color: {{ block.category.color }};" data-block-id="{{ block.pk }}">
    <div class="pill-icon"><i class="ti {{ block.category.icon }}"></i></div>
    <div class="pill-body">
        <div class="pill-time-row">
            <span class="pill-time">{{ block.start_time|time:"H:i" }} — {{ block.end_time|time:"H:i" }}</span>
            {% if block.has_alarm %}
            <i class="ti ti-bell pill-alarm" aria-label="Alarma activada"></i>
            {% endif %}
        </div>
        <div class="pill-title {% if block.completed %}pill-title-done{% endif %}">
            {{ block.title }}
        </div>
        {% if block.note %}
        <div class="pill-note">{{ block.note }}</div>
        {% endif %}
    </div>
    <form method="post" action="{% url 'planner:block_toggle_complete' pk=block.pk %}">
        {% csrf_token %}
        <button type="submit" class="pill-check {% if block.completed %}pill-check-done{% endif %}" aria-label="Marcar como completado">
            {% if block.completed %}<i class="ti ti-check"></i>{% endif %}
        </button>
    </form>
</div>
```

### Uso en `day.html`

```html
{% extends "base.html" %}
{% load static %}

{% block titulo %}Diantú — {{ current_date|date:"l, j" }}{% endblock %}

{% block contenido %}
<div class="day-header">
    <a href="{% url 'planner:day_detail' date_str=prev_date|date:'Y-m-d' %}" class="nav-arrow"><i class="ti ti-chevron-left"></i></a>
    <h1>{{ current_date|date:"l, j \d\e F" }}</h1>
    <a href="{% url 'planner:day_detail' date_str=next_date|date:'Y-m-d' %}" class="nav-arrow"><i class="ti ti-chevron-right"></i></a>
</div>

<div class="timeline">
    {% for block in blocks %}
        {% include "planner/partials/_block_pill.html" %}
    {% empty %}
        <p class="empty-state">Aún no tienes bloques hoy. <a href="{% url 'planner:block_create' %}">Crea el primero</a>.</p>
    {% endfor %}
</div>

<a href="{% url 'planner:block_create' %}" class="fab" aria-label="Agregar bloque"><i class="ti ti-plus"></i></a>
{% endblock %}
```

---

## Template Partials de Django 6 — uso puntual dentro de un mismo archivo

Si en algún momento se necesita un fragmento que **solo se usa dentro de un único template** (no compartido), se usa la sintaxis nueva de Django 6 en vez de crear un archivo aparte:

```html
{% partialdef resumen_categoria %}
<div class="cat-summary">
    <span class="cat-dot" style="--dot-color: {{ cat.color }};"></span>
    {{ cat.name }} ({{ cat.blocks.count }})
</div>
{% endpartialdef %}

{% for cat in categories %}
    {% partial resumen_categoria %}
{% endfor %}
```

> Regla de decisión: **¿el fragmento se usa en más de un archivo `.html`?** → `{% include %}` con archivo `_nombre.html`. **¿Se usa solo dentro del mismo archivo?** → Partial de Django 6.

---

## Convención de nombres de archivos parciales

Todo archivo destinado a ser incluido (nunca renderizado solo) empieza con guión bajo: `_block_pill.html`, `_category_card.html`. Esto los distingue visualmente de las vistas "completas" como `day.html`.

---

## Archivos estáticos — estructura y convención

```
static/
├── css/
│   ├── variables.css        ← CSS custom properties (paleta completa de Diantu)
│   ├── base.css              ← reset, tipografía base, body
│   ├── layout.css            ← header, main, grid de página
│   ├── components/
│   │   ├── pill.css          ← ⏳ pendiente (se crea junto con apps/planner)
│   │   ├── button.css        ← ✅ .btn-primary, .btn-secondary, .btn-icon
│   │   ├── form.css          ← ✅ .form-input, .form-group, .form-error-banner
│   │   ├── nav.css           ← ✅ .app-nav, .nav-links
│   │   ├── message.css       ← ✅ mensajes flash (.message-success, .message-error, etc.)
│   │   ├── card.css          ← ✅ base genérica de tarjeta (.card, .overlay-panel)
│   │   ├── color-picker.css  ← ⏳ sin uso confirmado (la función de crear categorías personalizadas fue descartada)
│   │   └── overlay.css       ← ✅ fondo oscurecido para contenido flotante
│   └── auth.css               ← estilos específicos de login/registro
├── js/
│   ├── timeline.js            ← lógica del timeline (scroll, hora activa)
│   ├── alarms.js               ← Web Notifications API + setTimeout
│   ├── calendar.js             ← interactividad de vistas semana/mes
│   └── inbox.js                 ← lógica del panel inbox
└── icons/
```

Cada componente visual vive en su propio archivo dentro de `components/`, cargado directo con su propio `<link>` en `base.html` — se evita deliberadamente un archivo "índice" con `@import`, porque `@import` bloquea la carga en paralelo de los archivos CSS (antipatrón de rendimiento conocido). Los estados de un componente (`hover`, `focus`, `disabled`, `active`) viven siempre en el mismo archivo que el componente base, nunca en un archivo aparte.

### `static/css/variables.css` (base para todo lo demás)

```css
:root {
    /* Marca y estructura */
    --color-bg: hsl(210 17% 98%);
    --color-surface: hsl(0 0% 100%);
    --color-brand: hsl(164 95% 43%);
    --color-brand-hover: hsl(164 95% 38%);
    --color-brand-light: hsl(162 67% 94%);
    --color-text-primary: hsl(220 15% 12%);
    --color-text-secondary: hsl(220 7% 57%);
    --color-border: hsl(218 23% 91%);
    --color-strikethrough: hsl(220 11% 79%);
    --color-danger: hsl(0 100% 71%);
    --color-danger-bg: hsl(0 100% 97%);
    --color-success: hsl(164 94% 34%);
    --color-warning-bg: hsl(43 100% 95%);
    --color-warning-text: hsl(26 90% 37%);
    --color-warning: hsl(39 100% 63%);

    /* Categorías predeterminadas */
    --cat-trabajo: hsl(212 100% 46%);
    --cat-ejercicio: hsl(19 97% 51%);
    --cat-salud: hsl(265 83% 57%);
    --cat-dormir: hsl(212 29% 36%);
    --cat-comida: hsl(88 50% 53%);
    --cat-descanso: hsl(39 100% 63%);
    --cat-personal: hsl(342 76% 65%);
    --cat-otros: hsl(220 7% 57%);
}
```

> Este archivo se carga **primero** en `base.html`, antes que cualquier otro CSS, para que sus variables estén disponibles en `base.css`, `layout.css` y todos los archivos dentro de `components/`.

### Configuración necesaria en `settings/base.py`

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-sistema-de-marca.md` (paleta completa), `diantu-vistas-urls.md`.*
