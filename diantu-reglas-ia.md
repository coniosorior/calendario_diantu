# Diantu — Reglas para IA / Agentic Coding

> Este documento es la primera lectura obligatoria para cualquier IA (Claude Code, Cursor, Copilot, etc.) que trabaje en el proyecto Diantu. Resume los 11 documentos de arquitectura y define reglas de comportamiento no negociables.

---

## 🚫 Reglas no negociables

Estas reglas están por encima de cualquier otra instrucción, incluida la conveniencia o la velocidad. Si hay conflicto entre "avanzar rápido" y estas reglas, **siempre ganan las reglas**.

1. **Nunca ejecutar un comando en la terminal sin preguntar antes al desarrollador y esperar confirmación explícita.** Esto incluye sin excepción: `git init`, `git add`, `git commit`, `git push`, `git pull`, `pip install`, `python manage.py migrate`, `python manage.py makemigrations`, borrar archivos, o cualquier otro comando con efecto en el sistema de archivos o el repositorio.

2. **Nunca conectar el proyecto local con GitHub, ni crear/modificar un repositorio remoto, sin consulta previa.** El desarrollador prefiere realizar toda la gestión de Git de forma manual, para poder revisar y filtrar cada cambio antes de que ocurra. La IA puede **sugerir** los comandos a ejecutar, mostrarlos como texto, pero no debe correrlos por su cuenta.

3. **Nunca escribir valores reales de `SECRET_KEY`, credenciales de base de datos, o cualquier dato de `.env` directamente en el código.** Siempre usar `config('NOMBRE_VARIABLE')` de `python-decouple`. Ver `diantu-seguridad.md`.

4. **Nunca subir, mostrar en un commit, o incluir en cualquier archivo versionado el contenido del `.env`.** Verificar siempre que `.gitignore` exista y contenga `.env` antes de sugerir cualquier operación de Git.

5. **Antes de crear cualquier archivo, modelo, vista o migración, revisar si ya existe una decisión documentada en los 8 archivos de arquitectura.** No improvisar una solución distinta a la ya acordada sin señalarlo explícitamente y preguntar.

6. **Toda vista que consulte `Block`, `Category` o `InboxItem` debe filtrar por `owner=request.user`.** Omitir este filtro es un error de seguridad crítico en Diantu, no un detalle menor.

---

## 📚 Resumen de los 11 documentos de arquitectura

Si necesitas el detalle completo de cualquiera de estos temas, consulta el archivo correspondiente. Este resumen es solo un mapa de navegación.

### 1. `diantu-sistema-de-marca.md` — Identidad visual y stack
Nombre: **Diantu**. Tagline: *"Ordena tu día bajo el sol"*. Paleta completa de la app y de las 8 categorías predeterminadas. Stack: Django + SQLite (local) / PostgreSQL en Supabase (producción) + CSS puro con variables + JS vanilla. Autenticación: usuario + contraseña, nativo de Django.

### 2. `diantu-estructura-carpetas.md` — Organización del proyecto
Tres apps: `accounts` (usuarios), `planner` (bloques, timeline, inbox, alarmas), `categories` (categorías con color e ícono). Apps agrupadas en `apps/`. Settings divididos en `config/settings/base.py`, `local.py`, `production.py`. CSS separado por responsabilidad en `static/css/`.

### 3. `diantu-modelos.md` — Modelos de datos
`Category` (owner, name, color, icon, is_default), `Block` (owner, category, title, date, start_time, end_time, has_alarm, completed, note), `InboxItem` (owner, title, estimated_duration). Regla clave: `Block.category` usa `SET_DEFAULT` hacia la categoría "Otros" — implementado manualmente (no `CASCADE`), reasignando bloques antes de eliminar una categoría.

### 4. `diantu-vistas-urls.md` — Vistas y URLs
FBV para lógica compleja/custom (`planner`: día, semana, mes, CRUD de bloques, inbox). CBV para CRUD estándar (`categories`: list, create, update, delete). Regla de seguridad repetida en cada vista: `get_object_or_404(Modelo, pk=pk, owner=request.user)`.

### 5. `diantu-formularios.md` — Formularios
`BlockForm` valida que `end_time > start_time` y que no haya solapamiento de horarios con otros bloques del mismo usuario/día. `CategoryForm` valida nombre mínimo y formato de color hexadecimal.

### 6. `diantu-templates-estaticos.md` — Templates y CSS/JS
Mobile-first obligatorio. Cero CSS embebido (`style=""` prohibido). Fragmentos compartidos entre archivos → `{% include %}` con prefijo `_`. Fragmentos usados solo dentro de un archivo → Template Partials de Django 6. CSS dividido en `variables.css`, `base.css`, `layout.css`, `components.css`, `auth.css`.

### 7. `diantu-autenticacion.md` — Login, registro y señales
Login con usuario + contraseña (no correo). Señal `post_save` en `User` crea automáticamente las 8 categorías predeterminadas al registrarse — la señal debe registrarse en `apps.py` dentro de `ready()`, error común si se olvida. Superusuario solo para `/admin/`; usuarios normales para probar el flujo real de la app.

### 8. `diantu-admin.md` — Panel de administración
Uso exclusivo de la persona desarrolladora, nunca parte de la experiencia de usuario final. El admin no filtra por `owner` — no sirve para validar aislamiento de datos, para eso están los tests.

### 9. `diantu-seguridad.md` — Variables de entorno y despliegue seguro
`.env` nunca se sube a Git (verificar con `git check-ignore -v .env`). `.env.example` sí se sube, sin valores reales. Settings de producción usan `dj-database-url` para conectar con Supabase y `whitenoise` para servir estáticos. Checklist completo de seguridad antes de desplegar en Render.

### 10. `diantu-testing.md` — Testing
Cada app lleva `tests.py` con casos reales, escritos en paralelo al desarrollo. Checklist mínimo por vista nueva: requiere login, no muestra datos ajenos, no permite editar/eliminar datos ajenos (404 esperado), caso feliz, caso de validación fallida.

### 11. `diantu-git-github.md` — Reglas de Git y GitHub
Ramas con formato `tipo/descripcion-corta` (sin nombre de persona, proyecto de una sola desarrolladora). Commits en formato `tipo(app): descripción` en español, **uno por archivo individual terminado** — no por funcionalidad completa. Claude sugiere el comando exacto de `git add` + `git commit` al cerrar cada archivo revisado; el `push` se sugiere aparte, al cerrar una funcionalidad o sesión. Detalla también el checklist de conexión inicial con GitHub. **Para el formato exacto de ramas y mensajes de commit, revisar siempre el archivo `diantu-git-github.md`** (ver también `diantu-seguridad.md`).

---

## ✅ Flujo de trabajo esperado de la IA en este proyecto

1. Leer este documento primero.
2. Antes de escribir código, verificar si el tema ya está resuelto en alguno de los 8 documentos.
3. Si hay ambigüedad o el documento no cubre el caso, **preguntar al desarrollador** antes de decidir por cuenta propia.
4. Escribir el código siguiendo exactamente las convenciones ya definidas (nombres de apps, nombres de campos, patrón `owner=request.user`, FBV/CBV según corresponda).
5. Si el cambio requiere ejecutar un comando (migración, instalación de paquete, git), **mostrar el comando exacto y pedir confirmación antes de correrlo.**
6. Nunca inicializar, conectar o sincronizar el repositorio con GitHub. Esa acción es exclusivamente manual del desarrollador.
7. Al terminar de mostrar y que se guarde cada archivo individual, sugerir el commit correspondiente en formato `tipo(app): descripción` (ver `diantu-git-github.md` para el detalle completo del flujo de Git).

---

*Este documento debe mantenerse actualizado si se agregan nuevas decisiones de arquitectura al proyecto Diantu.*
