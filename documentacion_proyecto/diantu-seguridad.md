# Diantu — Seguridad y Variables de Entorno

> Documento de referencia para desarrollo humano y agentic coding (IA). Basado en la clase 13 (Seguridad, Variables de Entorno y Settings Divididos). Su objetivo principal: que ningún dato sensible de Diantu llegue nunca a GitHub.

---

## Seguridad integrada de Django — qué ya viene resuelto

Django protege automáticamente contra las vulnerabilidades más comunes. Esto no requiere configuración extra en Diantu, pero es importante saber que está ahí y no desactivarlo por accidente:

| Vulnerabilidad | Qué es | Cómo Django la previene en Diantu |
|---|---|---|
| **SQL Injection** | SQL malicioso inyectado en una consulta | El ORM escapa automáticamente todos los valores de `filter()`, `get()`, `create()`, etc. Nunca se debe usar SQL crudo con datos del usuario sin escapar. |
| **XSS** | JavaScript malicioso inyectado en el HTML | Los templates de Django escapan todo el contenido por defecto (`{{ variable }}`). Nunca usar `{{ variable\|safe }}` con contenido escrito por un usuario. |
| **CSRF** | Solicitudes falsificadas desde otro sitio | Todo formulario POST de Diantu debe llevar `{% csrf_token %}` — ya aplicado en `RegistroForm`, login, y se aplicará en los formularios futuros de `planner` (`BlockForm`, aún no existe). `CategoryForm` fue eliminado: las categorías ya no se crean/editan desde la app. |
| **Clickjacking** | Embeber Diantu en un iframe malicioso | El middleware `XFrameOptionsMiddleware` bloquea esto automáticamente. |
| **Contraseñas en texto plano** | Almacenamiento inseguro de contraseñas | Django hashea con PBKDF2 (más de 720.000 iteraciones) automáticamente al usar `User.objects.create_user()` o `UserCreationForm`. |

---

## Qué información es sensible en Diantu (y nunca va en el código)

```
🔴 NUNCA hardcodear en ningún archivo .py:
   - SECRET_KEY
   - Credenciales de la base de datos (Supabase: usuario, password, host)
   - Cualquier API key futura (si se agrega envío de correos, etc.)

🟡 DEPENDE del entorno (local vs producción):
   - DEBUG
   - ALLOWED_HOSTS
   - CSRF_TRUSTED_ORIGINS

🟢 Puede ir directo en el código (no es sensible):
   - INSTALLED_APPS
   - MIDDLEWARE
   - LANGUAGE_CODE = 'es-cl'
   - TIME_ZONE = 'America/Santiago'
```

---

## El archivo `.env` — la pieza central de esta protección

El `.env` vive **solo en tu computador**, nunca se sube a GitHub. Es el único lugar donde existen los valores reales de `SECRET_KEY` y las credenciales de base de datos.

### `.env` (ejemplo para desarrollo local de Diantu — este archivo NO se sube)

```bash
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=una-clave-larga-y-aleatoria-solo-para-tu-maquina
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### `.env.example` (este SÍ se sube a GitHub, como plantilla)

```bash
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
```

> La diferencia es simple pero crítica: `.env.example` tiene las **claves** (los nombres de las variables) sin sus **valores**. Así, cualquiera que clone el repositorio de Diantu (incluida tú misma en otro computador) sabe exactamente qué variables debe definir, sin exponer ningún dato real.

---

## `.gitignore` — la barrera que impide subir el `.env` por accidente

Este archivo debe existir **desde el primer commit** del proyecto, antes de conectar con GitHub. Contenido mínimo para Diantu:

```gitignore
# Variables de entorno — NUNCA subir
.env

# Base de datos local
db.sqlite3

# Entorno virtual de Python
venv/
env/
.venv/

# Cache de Python
__pycache__/
*.pyc

# Archivos estáticos recolectados (se generan en el deploy)
staticfiles/

# Archivos subidos por usuarios en desarrollo
media/

# Configuración de editores
.vscode/
.idea/

# Sistema operativo
.DS_Store
Thumbs.db
```

> ⚠️ **Orden de operaciones importante:** si el `.env` ya se subió a GitHub alguna vez (aunque sea en un commit antiguo), agregar `.gitignore` después **no lo elimina del historial**. Sigue existiendo en versiones anteriores del repositorio, visible para cualquiera. Si esto llega a pasar, la `SECRET_KEY` expuesta debe considerarse comprometida y regenerarse — nunca "confiar" en que un archivo borrado en un commit nuevo ya no es accesible.

---

## Instalación de `python-decouple`

```bash
pip install python-decouple
```

Y se agrega a `requirements.txt`:

```
python-decouple==3.8
```

---

## Settings divididos — cómo se conectan con el `.env`

### `config/settings/base.py`

```python
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')   # ← lee el valor real desde .env, nunca hardcodeado

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps de Diantu
    'apps.accounts',
    'apps.categories',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'planner:day'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
```

### `config/settings/local.py` (desarrollo — SQLite, `.env` local)

```python
from .base import *
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

### `config/settings/production.py` (Render + Supabase)

```python
import dj_database_url
from .base import *
from decouple import config

DEBUG = False

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
    # dj_database_url lee la variable de entorno DATABASE_URL,
    # que en Render se configura con la cadena de conexión de Supabase
}

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Content Security Policy — nativo en Django 6
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src":  ["'self'"],
        "style-src":   ["'self'", "'unsafe-inline'"],
        "img-src":     ["'self'", "data:"],
    }
}
```

> En producción, `DATABASE_URL` (la cadena de conexión completa de Supabase) y `SECRET_KEY` **no van en un `.env`** — se configuran directamente como variables de entorno en el panel de Render, que las mantiene fuera del código igual que el `.env` lo hace en local.

---

## Actualizar `manage.py` y `wsgi.py` para usar `local.py` por defecto

```python
# manage.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
```

```python
# config/wsgi.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
```

> En Render, la variable de entorno `DJANGO_SETTINGS_MODULE=config.settings.production` se configura en el panel del servicio, sobreescribiendo este valor por defecto sin tocar el código.

---

## Flujo completo: de local a GitHub sin exponer nada

> Este flujo se detalla también, con el mismo checklist, en `diantu-git-github.md` (sección "Checklist antes de conectar el proyecto con GitHub por primera vez"), que además define el formato de ramas y de mensajes de commit usado en todo el proyecto.

Este es el orden de pasos que responde directamente a tu preocupación:

```
1. Crear el proyecto Django en local
2. Crear el archivo .env con los valores reales (SECRET_KEY, DEBUG, etc.)
3. Crear .env.example con las mismas claves, sin valores
4. Crear .gitignore ANTES del primer commit, incluyendo ".env"
5. git init
6. git add .
7. Verificar con "git status" que .env NO aparece en la lista de archivos
   a subir (si aparece, el .gitignore está mal escrito o mal ubicado)
8. git commit -m "Estructura inicial del proyecto"
9. Conectar con el repositorio remoto en GitHub
10. git push
```

### Verificación rápida antes de cada push

```bash
git status
```

Si `.env` aparece en la lista de "Changes to be committed" o "Untracked files", **detente** — algo falló en el `.gitignore`. El comando correcto para revisar si un archivo específico está siendo ignorado:

```bash
git check-ignore -v .env
```

Si no devuelve nada, `.env` **no está siendo ignorado** y hay que revisar el `.gitignore` antes de continuar.

---

## Checklist de seguridad antes de desplegar Diantu a producción

Basado en el Django Deployment Checklist oficial, aplicado específicamente a Diantu:

- [ ] `.env` no está en el repositorio de GitHub (verificado con `git check-ignore -v .env`)
- [ ] `.env.example` sí está en el repositorio, sin valores reales
- [ ] `SECRET_KEY` de producción es distinta a la de desarrollo local
- [ ] `DEBUG = False` en `production.py`
- [ ] `ALLOWED_HOSTS` configurado con el dominio real de Render (no vacío, no `*`)
- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production` configurado como variable de entorno en Render
- [ ] `DATABASE_URL` de Supabase configurada como variable de entorno en Render (no en el código)
- [ ] `SECURE_SSL_REDIRECT = True` en producción
- [ ] `SESSION_COOKIE_SECURE = True` y `CSRF_COOKIE_SECURE = True` en producción
- [ ] Content Security Policy configurada en `production.py`
- [ ] `python manage.py check --deploy` ejecutado sin advertencias críticas antes del primer deploy

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-estructura-carpetas.md`, `diantu-autenticacion.md`, `diantu-git-github.md`.*
