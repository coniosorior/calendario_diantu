# Diantu — Estructura de Carpetas del Proyecto

---

## Apps del proyecto

Siguiendo la regla de oro de Django (*una app debe poder describirse en una sola frase*), Diantu se divide en tres apps con responsabilidades claramente separadas:

| App | Responsabilidad | Descripción en una frase |
|---|---|---|
| **accounts** | Usuarios | Gestiona todo lo relacionado con usuarios: registro, login, logout, perfil, cambio de contraseña, eliminar cuenta. |
| **planner** | Planificación | Es el corazón de la app: bloques de tiempo, el timeline del día, el inbox, las alarmas. |
| **categories** | Categorías | Gestiona las categorías con sus colores e íconos que clasifican los bloques. |

> **¿Por qué separar `categories` de `planner`?**
> Aunque las categorías son parte de la planificación, tienen su propio CRUD independiente, son configurables por el usuario, y en el futuro podrían tener más lógica propia (estadísticas por categoría, por ejemplo). Mantenerlas separadas evita que `planner` crezca demasiado y mezcle responsabilidades.

---

## Estructura completa

```
diantu/                          ← carpeta raíz del proyecto
│
├── config/                      ← configuración central del proyecto
│   ├── __init__.py
│   ├── settings/                ← separamos settings por entorno
│   │   ├── __init__.py
│   │   ├── base.py              ← configuración común a todos los entornos
│   │   ├── local.py             ← desarrollo local: SQLite, DEBUG=True, etc.
│   │   └── production.py        ← Supabase PostgreSQL, DEBUG=False, etc.
│   ├── urls.py                  ← URLs raíz del proyecto
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        ← todas las apps del proyecto agrupadas
│   ├── accounts/                ← autenticación y perfiles
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── accounts/
│   │   │       ├── login.html
│   │   │       └── register.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py             ← formularios de login y registro
│   │   ├── models.py            ← extensión del modelo User si se necesita
│   │   ├── tests/                ← casos de prueba de registro, login y perfil
│   │   │   ├── __init__.py
│   │   │   └── test_models.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── planner/                 ← núcleo de la app
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── planner/
│   │   │       ├── day.html     ← vista Día
│   │   │       ├── week.html    ← vista Semana
│   │   │       ├── month.html   ← vista Mes
│   │   │       ├── inbox_list.html
│   │   │       ├── inbox_form.html
│   │   │       └── inbox_move_form.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py             ← formulario de crear/editar bloque
│   │   ├── models.py            ← Block, DayPlan, InboxItem
│   │   ├── tests/                ← casos de prueba de bloques, timeline y permisos por usuario
│   │   │   ├── __init__.py
│   │   │   └── test_models.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── categories/              ← gestión de categorías
│       ├── migrations/
│       ├── templates/
│       │   └── categories/
│       │       ├── list.html
│       │       ├── form.html
│       │       └── confirm_delete.html
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py            ← Category
│       ├── tests/                ← casos de prueba del modelo y CRUD de categorías
│       │   ├── __init__.py
│       │   └── test_models.py
│       ├── urls.py
│       └── views.py
│
├── static/                      ← archivos estáticos globales
│   ├── css/
│   │   ├── variables.css        ← todas las CSS variables de Diantú
│   │   ├── base.css             ← estilos globales, reset
│   │   ├── layout.css           ← estructura de página
│   │   ├── components/
│   │   │   ├── pill.css          ← la píldora de bloque
│   │   │   ├── button.css        ← .btn-primary, .btn-secondary, .fab
│   │   │   ├── form.css          ← .form-input, .form-group, etc.
│   │   │   ├── nav.css           ← .app-nav, .nav-links
│   │   │   ├── message.css       ← mensajes flash
│   │   │   ├── card.css          ← tarjeta genérica base
│   │   │   ├── color-picker.css  ← paleta de colores custom
│   │   │   └── overlay.css       ← fondo oscurecido, reservado para uso futuro
│   │   └── auth.css              ← estilos del login/registro
│   ├── js/
│   │   ├── timeline.js          ← lógica del timeline del día
│   │   ├── alarms.js            ← lógica de notificaciones y alarmas
│   │   ├── calendar.js          ← vistas semana y mes
│   │   └── inbox.js             ← lógica del panel inbox
│   └── icons/                   ← si necesitas íconos locales
│
├── templates/                   ← templates globales compartidos
│   ├── base.html                ← template base con navbar, head, CSS
│   ├── 404.html
│   └── 500.html
│
├── media/                       ← archivos subidos por usuarios (si aplica)
│
├── .env                         ← variables de entorno (SECRET_KEY, DB, etc.) — NO se sube a Git
├── .env.example                 ← plantilla del .env sin valores reales — sí se sube a Git
├── .gitignore                   ← excluye .env, db.sqlite3, __pycache__, etc.
├── manage.py
├── requirements.txt             ← dependencias: Django, python-decouple, dj-database-url, whitenoise, etc.
└── diantu-sistema-de-marca.md    ← documento de diseño visual y técnico
```

---

## Decisiones de organización

### Settings separados por entorno

El material de clase muestra `settings.py` como un solo archivo, lo cual es correcto para aprender. Para Diantu, que tendrá un entorno de desarrollo (SQLite, `DEBUG=True`) y uno de producción (Supabase PostgreSQL, `DEBUG=False`), separar en `base.py`, `local.py` y `production.py` es la práctica profesional. `base.py` contiene todo lo común, y cada entorno sobreescribe solo lo que cambia. Al desplegar en Render, se indica que use `production.py` mediante la variable de entorno `DJANGO_SETTINGS_MODULE`.

### Variables de entorno y seguridad

Siguiendo el material de la clase de seguridad, ningún valor sensible se escribe directo en el código. El archivo `.env` vive solo en el computador local, nunca se sube a Git (está excluido en `.gitignore`), y contiene valores como `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS`. Se acompaña de un `.env.example` que sí se sube al repositorio, con las mismas claves pero sin valores reales, para que cualquiera que clone el proyecto sepa qué variables debe definir.

Tres librerías del stack de seguridad completan esta parte:

| Librería | Función |
|---|---|
| `python-decouple` | Lee las variables desde `.env` con `config('SECRET_KEY')` en vez de escribirlas directo en el código |
| `dj-database-url` | Convierte la URL de conexión de Supabase en el diccionario `DATABASES` que Django necesita |
| `whitenoise` | Sirve los archivos estáticos (CSS, JS) en producción sin necesitar un servidor externo como Nginx |

En Django 6 además se configura **Content Security Policy (CSP)** en `production.py`, que le indica al navegador desde qué orígenes puede cargar scripts, estilos e imágenes — una capa extra de seguridad para el despliegue en Render.

### Testing por app

Siguiendo el material de testing, cada app (`accounts`, `planner`, `categories`) lleva su propia carpeta `tests/` con casos de prueba reales, separados por tipo (`test_models.py`, `test_views.py`, etc.), no vacío. Los tests se escriben en paralelo al desarrollo de cada funcionalidad, no al final del proyecto. Algunos ejemplos pensados para Diantu:

- **`accounts`**: el registro crea un usuario correctamente, el login redirige a la vista Día, las contraseñas no coincidentes fallan la validación
- **`planner`**: un `Block` calcula bien su duración, la vista Día devuelve status 200, un usuario solo ve sus propios bloques y no los de otros usuarios
- **`categories`**: el modelo `Category` tiene los campos correctos, el color por defecto de "Otros" es el gris de la paleta

### Apps agrupadas en `apps/`

El material de clase muestra las apps en la raíz del proyecto, lo habitual en proyectos simples. Agruparlas dentro de `apps/` es una decisión de orden: cuando el proyecto crece, tener `accounts/`, `planner/`, `categories/`, `config/` y otros archivos mezclados en la raíz dificulta la navegación. La carpeta `apps/` señala de inmediato dónde vive la lógica de negocio. Requiere un ajuste mínimo en `settings.py` para que Django las encuentre.

### CSS separado por responsabilidad

En lugar de un único `styles.css`, se separa en `variables.css`, `base.css`, `layout.css`, la carpeta `components/` (un archivo por componente visual: `pill.css`, `button.css`, `form.css`, `nav.css`, `message.css`, `card.css`, `color-picker.css`, `overlay.css`) y `auth.css`. Así, cuando se necesite cambiar el color de las píldoras, se sabe exactamente en qué archivo buscar. Si en el futuro se agrega el tema oscuro, solo se modifica `variables.css`.

---

*Documento creado durante la fase de planificación de la estructura del proyecto Diantu.*
