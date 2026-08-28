# Diantu — Reglas de Git y GitHub

> Documento de referencia para desarrollo humano y agentic coding (IA). Define cómo se organizan las ramas, cómo se escriben los mensajes de commit, y cómo Claude debe guiar el flujo de Git en este proyecto. Diantu es un proyecto de una sola desarrolladora (la desarrolladora), trabajando con Claude Code como copiloto — por eso este documento **no** sigue el formato de equipo (sin ramas por persona, sin Pull Requests de revisión cruzada), pero sí mantiene la disciplina de commits ordenados y trazables.

---

## 1. Rol de la IA en Git — regla no negociable

Esta regla ya está establecida en `diantu-reglas-ia.md` (reglas 1 y 2) y se repite aquí porque este documento es justamente sobre Git:

> **Claude nunca ejecuta comandos de Git por su cuenta.** Puede sugerir el comando exacto, mostrarlo como texto listo para copiar, y explicar qué hace — pero quien lo ejecuta, revisa y confirma es siempre la desarrolladora, manualmente, en su propia terminal.

Esto aplica a **todos** los comandos de Git sin excepción: `git init`, `git add`, `git commit`, `git branch`, `git checkout`, `git merge`, `git push`, `git pull`, y también a la conexión inicial del repositorio remoto en GitHub. Claude no inicializa, no conecta, ni sincroniza nada por su cuenta.

---

## 2. La rama principal: `main`

`main` es la versión estable del proyecto. La idea es no dejarla nunca en un estado roto (que no corra `python manage.py runserver` o que fallen los tests) — no porque haya un equipo revisando, sino porque es la única copia de referencia del proyecto y conviene poder volver a ella con confianza en cualquier momento.

---

## 3. Ramas de trabajo — formato simple (sin nombre de persona)

Como la desarrolladora es la única desarrolladora, las ramas **no llevan nombre de persona** — eso solo tiene sentido en equipos donde hay que distinguir quién hizo qué. El formato en Diantu es:

```
tipo/descripcion-corta
```

**Reglas del nombre:**

- Todo en **minúsculas**
- Sin espacios (usar guiones `-` para separar palabras)
- Descripción corta y clara, en español

### Tipos permitidos

| Tipo | ¿Cuándo se usa? | Ejemplo |
|---|---|---|
| `feature` | Funcionalidad nueva | `feature/categories-crud` |
| `fix` | Corrección de un bug | `fix/solapamiento-bloques` |
| `refactor` | Mejorar código sin cambiar funcionalidad | `refactor/limpiar-forms-planner` |
| `docs` | Solo cambios en documentación | `docs/actualizar-contexto-proyecto` |
| `test` | Solo cambios en tests | `test/tests-inbox` |

### Ejemplos válidos vs inválidos

```bash
# ✅ Correcto
feature/categories-crud
fix/validacion-color-hex
refactor/vistas-planner

# ❌ Incorrecto
Feature-Categorias        # mayúsculas, sin guion en el tipo
categories-crud            # falta el tipo
feature/Categorias CRUD    # mayúsculas y espacio
```

> **¿Cuándo conviene abrir una rama en vez de trabajar directo en `main`?** Cuando la tarea es lo bastante grande como para dejar el proyecto en un estado intermedio roto (ej. armar todo el modelo + forms + vistas de `categories`). Para cambios chicos y aislados (ej. corregir un typo en un template), trabajar directo en `main` es razonable. Ante la duda, Claude puede sugerir cuál conviene.

---

## 4. Commits — formato de mensajes

### Formato obligatorio

```
tipo(app): qué se hizo
```

- **tipo:** mismo que el de la rama (`feature`, `fix`, `refactor`, `docs`, `test`)
- **app:** la parte del proyecto que se modificó (ver tabla abajo)
- **descripción:** en español, corta, en infinitivo o tiempo pasado

### Nombres de "app" válidos en Diantu

| app | Cuándo se usa |
|---|---|
| `accounts` | Registro, login, señales de categorías predeterminadas |
| `planner` | Modelos `Block`/`InboxItem`, timeline, inbox, alarmas |
| `categories` | Modelo `Category`, CRUD de categorías |
| `config` | Settings, `urls.py` raíz, `wsgi.py`, `asgi.py` |
| `static` | CSS o JS en `static/` |
| `templates` | `base.html` u otros templates globales |
| `docs` | Archivos `.md` de documentación del proyecto |
| `deploy` | Cambios relacionados a Render/Supabase/despliegue |

### Ejemplos válidos (con casos reales de Diantu)

```bash
feature(categories): crear modelo Category con constraint de nombre único
feature(categories): agregar señal de categorías predeterminadas
feature(planner): crear modelo Block con validación de horario
fix(planner): corregir solapamiento de bloques en el mismo día
refactor(planner): extraer validación de horario a método privado del form
docs(contexto): actualizar estado del proyecto en sección 14
test(categories): agregar tests de aislamiento por owner
```

### Ejemplos inválidos

```bash
# ❌ NO hacer esto
"avances"                                  # sin formato, sin contexto
"fix bug"                                  # sin app, en inglés
"feature: modelo category"                 # falta el (app)
"feature(categories): add category model"  # descripción en inglés
```

---

## 5. Cuándo Claude debe sugerir hacer commit

**Decisión para Diantu: un commit por archivo individual terminado**, no por funcionalidad completa. Esto mantiene el historial granular y facilita volver atrás si algo se rompe a mitad de una funcionalidad.

Cada vez que Claude termine de mostrarte un archivo (siguiendo la regla 7 del contexto general — mostrar archivos uno por uno) y tú lo hayas revisado y guardado, Claude debe entregarte el bloque de comandos listo para copiar, con este formato:

```bash
git add ruta/al/archivo.py
git commit -m "tipo(app): descripción específica de ese archivo"
```

**Ejemplo real del flujo esperado**, al terminar `apps/categories/models.py`:

> Ya tienes el archivo `apps/categories/models.py` guardado. Cuando quieras, puedes hacer commit con:
> ```bash
> git add apps/categories/models.py
> git commit -m "feature(categories): crear modelo Category con constraint de nombre único"
> ```

Claude **no** agrupa varios archivos en un solo `git add .` salvo que la desarrolladora lo pida explícitamente (por ejemplo, al cerrar una sesión de trabajo con varios archivos ya revisados uno por uno).

El `git push` se sugiere aparte, normalmente al terminar una funcionalidad completa o al final de una sesión de trabajo — no después de cada commit individual, para no generar ruido de pushes constantes. Claude puede preguntar si conviene hacer push en ese momento.

Los archivos `__init__.py` y otro boilerplate sin lógica propia (contenido generado automáticamente por Django, sin cambios reales de la desarrolladora) no llevan su propio commit individual — se agrupan con el commit del archivo "real" más cercano al que pertenecen. Por ejemplo, `apps/categories/tests/__init__.py` (vacío, solo marca el paquete) se incluye en el mismo commit que `apps/categories/tests/test_models.py`, en vez de generar un commit separado sin contenido sustantivo que revisar.

---

## 6. Flujo de trabajo paso a paso

### Paso 1: Actualizar `main` local (si ya existe la rama)

```bash
git checkout main
git pull origin main
```

### Paso 2: Crear una rama (si la tarea lo amerita, ver sección 3)

```bash
git checkout -b feature/descripcion-corta
```

### Paso 3: Trabajar archivo por archivo, con commits individuales

```bash
git add apps/categories/models.py
git commit -m "feature(categories): crear modelo Category"

git add apps/categories/admin.py
git commit -m "feature(categories): registrar Category en el admin"
```

### Paso 4: Subir la rama a GitHub (al terminar la funcionalidad o la sesión)

```bash
git push origin feature/descripcion-corta
```

### Paso 5: Mergear a `main`

Como no hay equipo revisando, el merge puede hacerse localmente sin necesidad de un Pull Request formal en GitHub, aunque también es válido abrir un PR si la desarrolladora prefiere revisar el diff completo antes de integrar:

```bash
git checkout main
git merge feature/descripcion-corta
git push origin main
```

---

## 7. Checklist antes de conectar el proyecto con GitHub por primera vez

Este es el orden correcto para la primera conexión del proyecto con GitHub — ya definido en `diantu-seguridad.md`, repetido aquí en el contexto de Git:

```
1. Verificar que .gitignore existe y contiene ".env" (ANTES del primer commit)
2. git init
3. git add .
4. git status → confirmar que .env NO aparece en la lista
5. git check-ignore -v .env → debe confirmar que está ignorado
6. git commit -m "docs(inicial): estructura base del proyecto Diantu"
7. Crear el repositorio en GitHub (manual, vía la web de GitHub)
8. git remote add origin <url-del-repo>
9. git branch -M main
10. git push -u origin main
```

> ⚠️ Todos estos comandos los ejecuta la desarrolladora manualmente. Claude solo los muestra y explica, incluida la creación del repositorio remoto — ese paso se hace en la web de GitHub, no por terminal.

---

## 8. Comandos rápidos de referencia

| Qué quiero hacer | Comando |
|---|---|
| Ver en qué rama estoy | `git branch` |
| Cambiar a `main` | `git checkout main` |
| Crear una rama nueva | `git checkout -b tipo/descripcion` |
| Ver cambios pendientes | `git status` |
| Agregar un archivo específico | `git add ruta/al/archivo` |
| Hacer un commit | `git commit -m "tipo(app): descripción"` |
| Subir la rama actual | `git push origin tipo/descripcion` |
| Actualizar `main` | `git checkout main && git pull origin main` |
| Mergear una rama a `main` | `git checkout main && git merge tipo/descripcion` |
| Ver historial resumido | `git log --oneline` |
| Verificar que `.env` está ignorado | `git check-ignore -v .env` |

---

## 9. Estado actual de conexión a Git/GitHub

*(actualizar esta sección en cada sesión, igual que la sección 14 de `diantu-contexto-proyecto.md`)*

- [x] Repositorio local inicializado (`git init`)
- [x] `.gitignore` verificado antes del primer commit
- [x] Repositorio remoto creado en GitHub (https://github.com/coniosorior/calendario_diantu)
- [x] Primer push a `main` realizado

---

## 10. Resumen de reglas no negociables (Git)

1. Claude nunca ejecuta comandos de Git — solo los sugiere y explica.
2. Claude nunca inicializa ni conecta el repositorio remoto por su cuenta.
3. Ningún commit debe incluir `.env` ni credenciales reales — verificar con `git check-ignore -v .env` antes de cualquier commit si hay dudas.
4. Un commit = un archivo terminado y revisado, con mensaje en formato `tipo(app): descripción` en español.
5. `main` debe mantenerse en un estado funcional siempre que sea posible.

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-reglas-ia.md`, `diantu-seguridad.md`, `diantu-contexto-proyecto.md`.*
