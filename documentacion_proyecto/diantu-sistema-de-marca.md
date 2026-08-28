# Diantú — Sistema de marca y landing page

Documento de referencia con las especificaciones del logo, la paleta de colores y la landing page actual. Pensado para que tanto una persona como una IA puedan retomar el proyecto sin perder contexto.

---

## 1. Logo

### 1.1 Concepto

El ícono representa un sol con 8 rayos rodeado por un anillo orbital casi completo; el hueco del anillo termina en una flecha tipo chevron, ubicada en la posición del octavo rayo (arriba a la izquierda, ángulo ≈225°). La flecha comunica movimiento/avance ("tu día avanza"); el sol y los rayos representan a la marca y, conceptualmente, los bloques de tiempo del día.

Especificaciones técnicas del ícono (sistema de coordenadas 0–100):
- Sol central: círculo de radio 11
- Rayos: 8, longitud 19.5 (desde radio 15 a radio 19.5 más el grosor del trazo), grosor de trazo 3.2
- Anillo: radio 36, grosor de trazo 5, con hueco entre 195° y 255°
- Flecha chevron: en el ángulo 195° (donde empieza el hueco), brazos de 10, apertura de 38°

### 1.2 Logo vertical / ícono solo (con contenedor)

Para uso como ícono de app, favicon, o cualquier contexto donde la marca deba sostenerse sola sin el nombre. Incluye el contenedor cuadrado con esquinas redondeadas (radio ≈22% del tamaño).

| Archivo | Descripción | Uso recomendado |
|---|---|---|
| `diantu_icon_emerald.svg` | Fondo verde esmeralda `#06D6A0`, ícono en blanco `#F8F9FA` | App móvil, splash screen, fondos oscuros |
| `diantu_icon_light.svg` | Fondo claro `#F8F9FA` (con borde sutil `#E2E6ED`), ícono en verde esmeralda `#06D6A0` | Favicon sobre fondo blanco, contextos claros |
| `diantu_icon_final.svg` | Panel comparativo con ambas versiones lado a lado | Solo referencia interna, no para producción |

### 1.3 Logo horizontal (ícono + wordmark, sin contenedor)

Para uso en headers, footers y cualquier contexto donde el nombre "Diantú" deba acompañar al ícono. A diferencia del logo vertical, **no lleva el contenedor cuadrado** — el ícono queda "suelto" al mismo nivel visual que el texto, como una sola pieza tipográfica. Esta decisión se tomó tras revisar referencias de marcas como Toku, donde el ícono y el nombre se leen como una sola unidad, no como dos elementos separados.

Reglas del logo horizontal:
- **Una sola voz de color**: el ícono y el texto "Diantú" usan siempre el mismo color entre sí (nunca colores distintos uno del otro).
- Sobre fondo claro → ícono + texto en verde esmeralda `#06D6A0`.
- Sobre fondo oscuro/esmeralda → ícono + texto en blanco `#F8F9FA`.
- Tipografía del wordmark: Plus Jakarta Sans, peso 600 (SemiBold).
- Espaciado entre ícono y texto: gap = 0px (se tocan, sin solaparse), usando un viewBox del ícono recortado a su borde visual real (no al borde del cuadrado original) para eliminar el espacio muerto que generaba separación visual aunque el gap fuera chico.
- El ícono dentro del logo horizontal es proporcionalmente más grande que en el ícono-solo, para igualar el peso visual del trazo fino del ícono contra el peso de la tipografía en negrita.

| Archivo | Descripción | Uso recomendado |
|---|---|---|
| `logo-h-claro.svg` | Ícono + "Diantú" en verde esmeralda `#06D6A0`, fondo transparente | Header sobre fondo blanco/claro (ej. footer claro, landing en modo claro) |
| `logo-h-emerald.svg` | Ícono + "Diantú" en blanco `#F8F9FA`, fondo transparente | Header sobre fondo oscuro o esmeralda (ej. hero oscuro de la landing actual) |

Ambos archivos tienen **fondo transparente** (no incluyen ningún rectángulo de color de fondo); el color de fondo lo aporta el contenedor donde se inserte el SVG.

### 1.4 Tipografía de marca

**Plus Jakarta Sans** — única familia tipográfica usada en todo el sistema (logo, landing, y pensada para la interfaz de la futura app). Pesos en uso: 400 (regular, cuerpo de texto), 500 (medium, links/nav), 600 (semibold, wordmark y subtítulos), 700–800 (bold/extrabold, títulos grandes).

Se eligió por ser una sans-serif geométrica-humanista: combina precisión/orden (formas geométricas) con calidez (proporciones humanistas, sin sentirse robótica), alineada con los valores de marca de calma, simplicidad y orden.

---

## 2. Paleta de colores

### 2.1 Colores principales de marca y UI

| Token | Hex | Uso |
|---|---|---|
| Verde esmeralda (principal/marca) | `#06D6A0` | Color de marca, botones primarios, acentos, logo |
| Fondo app (claro) | `#F8F9FA` | Fondo general de la app/landing en modo claro |
| Superficie cards/timeline | `#F5F7FA` | Tarjetas, fondo de bloques en el timeline |
| Bordes suaves | `#E2E6ED` | Bordes de inputs, tarjetas, separadores |
| Texto principal | `#1A1D23` | Texto principal sobre fondo claro |
| Texto secundario | `#8B909A` | Texto secundario, descripciones, metadatos |
| Completado / tachado | `#C4C8D0` | Estados completados o inactivos |
| Peligro / eliminar | `#FF6B6B` | Acciones destructivas, alertas |

### 2.2 Verde petróleo — variante oscura de marca (uso en landing)

Para el hero y el footer de la landing actual se introdujo una **variante oscura del mismo verde esmeralda** (mismo matiz/hue, distinta luminosidad y saturación), en vez de adoptar un color ajeno a la paleta:

| Token | Hex | Descripción |
|---|---|---|
| Verde petróleo (fondo oscuro) | `#0B3127` | Variante oscura de `#06D6A0` (mismo hue ≈164°, luminosidad reducida) |

Este color se usa **únicamente como fondo** (hero y footer de la landing); nunca aparece en el logo ni como color de acento/acción. El verde esmeralda `#06D6A0` sigue siendo el único color que se usa para identidad de marca, botones y acentos — el petróleo es un color de soporte, no reemplaza ni compite con el esmeralda como "color de Diantú". Esta distinción es importante: para que no haya ambigüedad sobre cuál es "el verde de la marca", todos los demás materiales (ícono de app, favicon, logo) deben seguir usando el esmeralda puro como protagonista.

Variante clara derivada para el badge del hero: `#62F2CD` (mismo hue, mayor luminosidad), usada en el texto del badge "☀ Ordena tu día bajo el sol" sobre fondo oscuro.

### 2.3 Colores de categoría (calendario)

Usados para clasificar actividades por tipo en el timeline/calendario:

| Categoría | Hex |
|---|---|
| Trabajo, estudio, productividad | `#006EE9` |
| Ejercicio, actividad física/recreativa | `#FB5607` |
| Salud (médico, kinesiólogo, psicólogo, etc.) | `#8338EC` |
| Dormir | `#415A76` |
| Almuerzo, comida, merienda | `#8BC34A` |
| Descanso, break | `#FFBC42` |
| Actividad personal, familiar, autocuidado | `#EA638C` |
| Otros | `#8B909A` |

---

## 3. Landing page actual

Archivo: `diantu-landing.html`. Una sola página HTML estática (sin backend/lógica de autenticación real todavía). Diseño de una sola sección de impacto (hero) más footer — sin sección intermedia de "características", por decisión deliberada de mantenerla minimalista dado que es un proyecto de uso personal/grupo cercano, no una landing de venta masiva.

### 3.1 Estructura general

1. **Header/Hero** (fondo oscuro `#0B3127`) — nav + mensaje principal + ilustración de producto.
2. **Footer** (mismo fondo oscuro `#0B3127`) — logo, link de contacto, copyright. Centrado.

No existe sección de "Por qué elegir Diantú" ni grid de características — se eliminó intencionalmente para simplificar la página a una sola pantalla de impacto.

### 3.2 Header / navegación

**Desktop:**
- Logo horizontal de Diantú a la izquierda (`logo-h-emerald`, en esmeralda ya que el fondo es oscuro).
- Links de navegación centrados: **Inicio** y **Contacto**.
  - El link de la página activa muestra una línea de acento esmeralda `#06D6A0` debajo (siempre en esmeralda, sin importar si el fondo de la página es oscuro o claro — color fijo para mantener un significado consistente de "estás aquí" en todo el sitio).
  - El link inactivo muestra la misma línea, sutil, solo en hover.
  - "Inicio" enlaza a la propia landing; "Contacto" enlaza a `contacto.html` (página separada, pendiente de construir).
- Acciones a la derecha: botón **"Iniciar sesión"** (estilo ghost/outline) + botón **"Registrarse"** (sólido, esmeralda).

**Mobile (≤760px):**
- Los links de navegación y los botones de acción se ocultan.
- Aparece un ícono de menú hamburguesa (3 líneas) a la derecha del logo.
- Al tocarlo, despliega un menú vertical con: **Inicio**, **Contacto**, **Iniciar sesión**.
- No hay lógica de sesión real conectada: el menú siempre muestra "Iniciar sesión" (no hay distinción logueado/no logueado todavía — queda como tarea pendiente para cuando exista backend de autenticación).
- Este navbar (Inicio/Contacto) es específico de las páginas públicas (landing + contacto). Aún no se ha definido si la futura app del calendario, ya logueada, reutilizará esta misma navegación o tendrá una propia — queda pendiente de decidir.

### 3.3 Hero — contenido y mensaje

- Badge superior: "☀ Ordena tu día bajo el sol" (texto en `#62F2CD` sobre fondo `rgba(6,214,160,0.14)`).
- Título: "Tu día, hora por hora. **Sin complicaciones.**" (segunda línea en verde esmeralda `#06D6A0`, resto en blanco).
- Descripción: "Organiza tus actividades en bloques de tiempo simples, sin calendarios eternos."
- CTA: un solo botón, **"Registrarse"** (sin "Iniciar sesión" como botón secundario en el hero — esa opción vive únicamente en el header/menú, para no competir visualmente con el CTA principal).

### 3.4 Hero — composición visual

Inspirada en el hero de la landing de Huddle (referencia), adaptada a los colores y contenido de Diantú:

- **Fondo**: verde petróleo `#0B3127` con una forma orgánica sutil (blob, `#0E3B2F`, opacidad 0.6) en la esquina superior izquierda, a modo de textura de fondo.
- **Formas geométricas decorativas**: deliberadamente pocas y sutiles (no un enjambre de figuras) — un rombo (cuadrado rotado 45°) en esmeralda al 16% de opacidad, y un punto pequeño en `#7EEBC8` al 55% de opacidad. Su función es decorativa/ambiental, no informativa.
- **Mockups de producto**: dos tarjetas solapadas representando el calendario de Diantú en dos tamaños de pantalla:
  - Una tarjeta ancha y baja (proporción tipo escritorio/laptop), detrás.
  - Una tarjeta angosta y alta (proporción tipo celular), delante, solapando la esquina inferior derecha de la primera.
  - **Ninguna de las dos tiene marco/carcasa de dispositivo** — son tarjetas simples con una barra superior mínima (decisión tomada tras revisar la referencia real de Huddle, donde tampoco hay marcos de dispositivo; la diferencia de proporción entre ambas tarjetas es suficiente para que se entienda cuál es "escritorio" y cuál "celular").
  - El contenido de ambas tarjetas es el mismo lenguaje visual: bloques de timeline con barra de color lateral según categoría (ver paleta de categorías en sección 2.3), simulando texto con barras grises de distinto largo (sin texto real legible, es una representación abstracta del calendario).

### 3.5 Footer

- Centrado en una sola columna (no distribución izquierda/derecha).
- Orden: logo horizontal de Diantú (versión blanca) → link "Contacto" → línea de copyright ("© 2026 Diantú — Ordena tu día bajo el sol").
- No incluye link "Inicio" (se consideró redundante en una página de una sola sección).
- Mismo fondo oscuro `#0B3127` que el hero, separado por una línea sutil (`border-top` en blanco al 14% de opacidad).

### 3.6 Responsive — comportamiento mobile del hero

- Los mockups reducen su tamaño máximo (hasta 300px de ancho) para no dominar la composición y sentirse parte de la misma unidad visual que el texto, no un bloque separado.
- Todo el contenido del hero (badge, título, descripción, botón) se centra horizontalmente (en escritorio está alineado a la izquierda).
- El botón "Registrarse" pasa a ocupar mayor ancho relativo (hasta 280px) mantenido centrado.
- Los mockups se reordenan visualmente arriba del texto (`order: -1`) en vez de al costado.

---

## 4. Pendientes / decisiones abiertas

- **Página de contacto** (`contacto.html`): aún no construida; el nav y el footer ya enlazan a ella.
- **Pantalla de registro/login**: se evaluó una referencia (Structured) pero se decidió posponerla; hoy "Registrarse" e "Iniciar sesión" no llevan a ningún destino funcional.
- **Navegación dentro de la app ya logueada**: no se ha decidido si reutiliza el navbar Inicio/Contacto de las páginas públicas o tiene una navegación propia distinta.
- **Estado logueado/no logueado en el menú mobile**: hoy el menú siempre muestra "Iniciar sesión"; falta lógica real cuando exista backend de autenticación.
