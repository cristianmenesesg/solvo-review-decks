# Export a PowerPoint de los decks de Sprint Review — Diseño

**Fecha**: 2026-08-10
**Repo**: `websites/solvo-review-decks` (submódulo, sitio estático en Vercel)
**Estado**: aprobado por el usuario, pendiente de plan de implementación

---

## 1 · Problema

Los decks de Sprint Review son HTML animado e interactivo: transiciones entre slides, reveals escalonados, un "pipeline vivo" donde se hace click en cada nodo, un slider de capturas y un iframe con la landing de QA corriendo en vivo. Eso funciona presentando desde el navegador, pero deja al equipo sin un artefacto que se pueda adjuntar a un acta o archivar.

Hace falta una versión `.pptx` de cada review **sin degradar la versión HTML**, que sigue siendo la que se presenta.

## 2 · Decisiones tomadas

| Decisión | Elección | Razón |
|---|---|---|
| Tipo de PPTX | **Editable — texto y formas reales** | Es un entregable de archivo: debe ser buscable y autocontenido, no un carrusel de imágenes |
| Uso previsto | **Entregable / archivo formal** | Se adjunta al acta de review o al paquete de handoff. Se abre poco, casi no se edita |
| Slides de flujo | **Todo el flujo en un slide** | Se lee de un vistazo, que es lo que sirve en un documento archivado |
| Fuentes | **Incrustar Poppins y Open Sans** | "Autocontenido" fue requisito explícito; ambas tienen licencia que lo permite (OFL / Apache) |
| Modelo de producción | **Autoría manual por deck (enfoque C)** | Ver §3 |

### Por qué autoría manual y no un generador

Se evaluó un generador que parsea el HTML del deck y emite el PPTX automáticamente. Se descartó a favor de la autoría manual por sprint.

La objeción estándar contra la autoría manual es el drift: dos formatos editados en paralelo divergen. **El flujo de trabajo elegido la neutraliza**: el HTML se cierra y se aprueba *antes* de tocar el PPTX. El contenido está congelado cuando arranca la derivación, así que no hay dos fuentes de verdad — hay una fuente y una derivación puntual.

A cambio, la autoría manual permite decidir el layout slide por slide, que es justamente lo que un deck tipográfico necesita y lo que un mapeo automático hace mal.

## 3 · Alcance

**Dentro**:

- Piloto: `sprint-14.pptx` a partir del deck existente (`reviews/sprint-14/`, *Sprint Review 14*, 6→17 jul 2026).
- Kit de marca reutilizable entre decks (`pptx/theme.py`).
- Fondos de marca renderizados una sola vez como assets.
- Incrustado de fuentes en el `.pptx`.
- Link de descarga del `.pptx` en la card del hub.

**Fuera** (trabajo posterior, con su propio ciclo):

- El deck HTML del Sprint 15 (20→31 jul 2026) y su `.pptx`.
- Cualquier cambio al motor HTML (`engine/`) o al deck existente, salvo el punto abierto de §11.

## 4 · Arquitectura de archivos

```
websites/solvo-review-decks/
├─ index.html                    ← gana un enlace "Descargar .pptx" en la card
├─ reviews/sprint-14/
│  ├─ index.html                 ← el deck HTML, INTACTO
│  ├─ assets/*.png               ← capturas originales (ya existen)
│  └─ sprint-14.pptx             ← el entregable
└─ pptx/
   ├─ .venv/                     ← gitignored
   ├─ requirements.txt           ← python-pptx, pillow, numpy, fonttools
   ├─ DESIGN.md                  ← este documento
   ├─ theme.py                   ← kit de marca: tokens, geometría, helpers
   ├─ build_backgrounds.py       ← genera los fondos de marca (se corre una vez)
   ├─ sprint_14.py               ← autoría slide por slide de ESTE deck
   ├─ preview.py                 ← renderer .pptx → PNG, para verlo sin PowerPoint
   ├─ verify_pptx.py             ← chequeo estructural del archivo generado
   ├─ out/                       ← PNGs del preview, gitignored
   └─ assets/
      ├─ bg-signature.png        ← gradiente 135° + halos radiales, 1920×1080
      ├─ landing-qa.png          ← captura de la landing (el iframe congelado)
      └─ fonts/                  ← Poppins*.ttf, OpenSans*.ttf
```

`pptx/` es tooling: no se sirve, no participa del deploy de Vercel, y el sitio sigue siendo estático sin build.

### Separación de responsabilidades

- **`theme.py`** no conoce ningún deck. Expone constantes de marca y helpers de dibujo (`eyebrow`, `badge`, `chip`, `foot`, `section_bg`). Es un kit de estilo, no un generador.
- **`sprint_14.py`** conoce un solo deck. Dibuja sus 17 slides explícitamente, llamando a los helpers. Un deck nuevo es un archivo nuevo; ninguno toca al otro.
- **`embed_fonts.py`** opera sobre un `.pptx` ya escrito y no sabe nada de decks ni de marca.
- **`build_backgrounds.py`** se corre una vez y produce assets versionados.

### Librería

**python-pptx** sobre venv del repo. Le gana a `pptxgenjs` en control de cajas de texto — interlineado, espaciado entre párrafos, autofit, runs con formato mixto — que es lo que decide si un deck tipográfico se ve bien o se ve de plantilla. El pip del sistema está bloqueado por PEP 668, de ahí el venv.

## 5 · Sistema de medidas

El escenario del HTML es un contenedor 16:9 y **todo el CSS escala en unidades de contenedor** (`cqh`/`cqw`), que son porcentajes de ese escenario. Un PPTX widescreen mide 13.333 × 7.5 in = 960 × 540 pt. La conversión es lineal y exacta:

```
1 cqh = 5.4 pt          1 cqw = 9.6 pt
```

`theme.py` expone `cqh(n)` y `cqw(n)`. Toda medida del PPT se deriva del CSS multiplicando — **el PPT hereda la retícula del HTML, no una aproximación a ojo**.

Valores derivados del CSS actual:

| Elemento | CSS | PPT |
|---|---|---|
| Padding del slide | `7cqh 8cqw` | 37.8 / 76.8 pt |
| Ancho de contenido | — | 806.4 pt |
| `h1` de portada | `9cqh` | 48.6 pt |
| `.sec-title` (divisor) | `7.2cqh` | 38.9 pt |
| `h2` de contenido | `4.6cqh` | 24.8 pt |
| `.sec-scope` | `2.6cqh` | 14.0 pt |
| `.lead` | `2.4cqh` | 13.0 pt |
| `.slide-head .sub` | `2.1cqh` | 11.3 pt |
| `.eyebrow` | `1.7cqh` | 9.2 pt |
| `.chip` | `1.55cqh` | 8.4 pt |
| `.slide-foot` | `1.35cqh` | 7.3 pt |
| Nodo del rail (diámetro) | `8.2cqh` | 44.3 pt |
| Número del nodo | `3cqh` | 16.2 pt |
| Etiqueta del nodo | `1.65cqh` | 8.9 pt |

## 6 · Kit de marca (`theme.py`)

Valores tomados de `engine/deck.css` y `assets/design-system/solvo-genai/tokens.css`:

```
ink        #111827    ink_2      #4B5563    ink_3      #9CA3AF
surface    #FFFFFF    surface_2  #F9FAFB
line       #E5E7EB    line_2     #D1D5DB
energy     #F19556    energy_d   #E07E3A
violet     #775AE5    blue       #3869E0    lav        #789FFF

success #16A34A · light #DCFCE7 · dark #166534
warning #F59E0B · light #FEF3C7 · dark #92400E
neutral_accent #8F939E · gray_100 #F3F4F6

grad_sign  135° #2E206D 0% → #775AE5 52% → #3869E0 100%   (va como PNG, §8)
grad_heat   90° #E07E3A → #F19556

radius_lg 12px · radius_xl 16px · radius_full → forma "pill"

font_heading  Poppins      font_body  Open Sans      font_mono  JetBrains Mono
```

Helpers:

| Helper | Qué dibuja |
|---|---|
| `eyebrow(slide, x, y, text, on_dark=False)` | Regla naranja de 2.6cqh + texto en versalitas espaciadas |
| `badge(slide, x, y, state, text)` | Píldora de estado (`qa` / `prod` / `none`) con su punto de color |
| `chip(slide, x, y, text)` | Píldora de stack, mono, borde `line` |
| `foot(slide, text)` | Marca al pie, versalitas, `ink_3` |
| `section_bg(slide)` | Aplica `bg-signature.png` a sangre completa |

## 7 · Mapa de slides — 17 en total

| # | Slide | Origen HTML | Cómo se resuelve |
|---|---|---|---|
| 1 | Portada | `.slide--cover` | Fondo PNG · logo · kicker · `h1` a 48.6 pt · meta · 4 chips de proyecto como formas píldora blanco 12% |
| 2 | Agenda | `.slide--agenda` | 4 filas de 3 columnas (sigla `energy_d` 16.2 pt · nombre + bajada · badge), separadas por línea `line` |
| 3 | Divisor CCO | `.slide--section` | Fondo PNG · `01 / 04` · regla naranja · título 38.9 pt · alcance 14 pt |
| 4 | Flujo CCO | `.slide--flow` | Ver §7.1 — 6 pasos |
| 5 | Divisor TPS | `.slide--section` | `02 / 04` |
| 6 | Flujo TPS | `.slide--flow` | Ver §7.1 — 5 pasos, uno marcado *change request* |
| 7 | Divisor ODO | `.slide--section` | `03 / 04` |
| 8 | Flujo ODO | `.slide--flow` | Ver §7.1 — 5 pasos |
| 9–12 | Capturas ODO (×4) | `.slide--media-slide` | **Una captura por slide**, casi a sangre, con epígrafe y marco de navegador |
| 13 | Divisor ECO | `.slide--section` | `04 / 04` |
| 14 | Landing | `.slide--landing-slide` | Captura de la landing QA en marco de navegador + columna derecha (lead, 4 pasos, stack, estado) |
| 15 | Correos | `.slide--mails-slide` | Las dos capturas lado a lado con sus epígrafes + la nota al pie |
| 16 | Próximos pasos | `.slide--next` | 4 tarjetas 2×2, barra naranja de 4 px a la izquierda |
| 17 | Cierre | `.slide--end` | Fondo PNG · logo centrado · "¿Preguntas?" 43.2 pt |

**Asimetría deliberada**: los flujos van todos en un slide, pero las capturas de Solvo Platform van una por slide. En un 2×2 quedan a un cuarto de tamaño e ilegibles, y el punto de esas capturas es que se vea la pantalla.

El HTML tiene 14 slides; el PPTX tiene 17. La diferencia son las tres capturas de ODO que en el HTML comparten un slider y acá se separan.

### 7.1 · Layout del slide de flujo

Es el slide que más se aleja del HTML, porque colapsa N estados interactivos en una vista estática. Distribución vertical sobre 540 pt:

```
  37.8  ─ eyebrow (9.2 pt)
        ─ h2 (24.8 pt)
        ─ sub (11.3 pt)
 ~120   ─────────────────────────────────────────────
        RAIL: círculos numerados unidos por línea
        · diámetro 44.3 pt, número 16.2 pt
        · línea de 3 px con relleno grad_heat completo
        · etiqueta debajo, 8.9 pt, centrada
        · nodo change-request: anillo punteado fijo + etiqueta encima
 ~215   ─────────────────────────────────────────────
        TARJETAS DE PASO: grilla 3 columnas
        · 258 pt de ancho, ~97 pt de alto, gap 16 pt
        · título: "04 · Búsqueda en portales" (11 pt, num en energy_d)
        · descripción (8.5 pt / 1.4, ink_2)
        · 6 pasos → 2 filas · 5 pasos → 2 filas (3 + 2)
 ~425   ─────────────────────────────────────────────
        BANDA DE ESTADO: badge + nota, fondo y borde según el estado
 ~490   ─────────────────────────────────────────────
        chips de stack · marca al pie
```

El paso más largo del deck actual son 165 caracteres, que a 8.5 pt en 258 pt de ancho dan ~4 líneas (~48 pt) — entra con holgura en la tarjeta.

## 8 · Fidelidad: qué se pierde y su sustituto

Declarado explícitamente para que nadie espere que el PPTX se comporte como el HTML:

| Se pierde | Sustituto en el PPTX |
|---|---|
| Drift del gradiente de portada (18 s, infinito) | Gradiente estático dentro del PNG de fondo |
| Pulso corriendo por el rail | Rail estático con el relleno completo |
| Anillo punteado giratorio del nodo *change request* | Anillo punteado fijo + su etiqueta |
| Texto con gradiente recortado (`.hl`) | Color sólido: `#FDBA8C` sobre oscuro, `#E07E3A` sobre claro |
| `backdrop-filter: blur` de los chips de portada | Relleno blanco al 12 % con borde blanco al 28 % |
| `mix-blend-mode: screen` de los halos | Horneado dentro del PNG de fondo |
| iframe en vivo + toggle Desktop/Tablet/Mobile | Captura desktop de la landing QA |
| Slider de capturas | Una captura por slide |
| Click en nodo del flujo | Todos los pasos visibles a la vez |
| Teclado, fullscreen, controles auto-ocultables | Los provee PowerPoint |

**Los fondos de marca van como PNG y no como gradiente nativo de PowerPoint.** Los slides de portada, divisor y cierre superponen un gradiente lineal de 135° con dos halos radiales en `mix-blend-mode: screen`. Ningún relleno de PowerPoint reproduce eso. Se renderizan una sola vez a 1920×1080 con el Chromium ya cacheado de Playwright (`~/.cache/ms-playwright/chromium-1228`) y quedan como asset versionado. El texto va encima, real y seleccionable.

## 9 · Imágenes

Las capturas embebidas en el HTML son **data URIs WebP** — PowerPoint 2019 y anteriores no las renderizan. El PPTX usa los **PNG originales** que ya están en `reviews/sprint-14/assets/` (`on-demand-1..4.png`, `email-prospect.png`, `email-account.png`).

La landing se captura una vez desde la URL de QA (verificada viva, HTTP 200) y queda como `pptx/assets/landing-qa.png`. Así el `.pptx` no depende de que ese ambiente siga en pie.

## 10 · Fuentes

**El spike se corrió y el resultado cambió la decisión.** Los `.fntdata` de PowerPoint no son TTF crudo: son **EOT (Embedded OpenType)**, un formato propio de Microsoft. Incrustar exige convertir TTF → EOT, y un EOT mal formado hace que PowerPoint declare el archivo **corrupto** — mucho peor que una fuente sustituida. Sin PowerPoint en esta máquina no hay forma de verificar la conversión, así que **el incrustado queda diferido**.

Estado actual: el `.pptx` declara Poppins y Open Sans. En una máquina que las tenga se ve exacto; sin ellas, PowerPoint sustituye por Segoe UI/Calibri y el deck sigue legible y bien maquetado, pero pierde carácter de marca.

Los siete TTF quedan en `assets/fonts/` para instalarlos con doble click. Ni Poppins ni Open Sans están instaladas en el Windows de esta máquina, así que sin ese paso el deck se ve sustituido.

**Pendiente**: convertir a EOT y probar el incrustado generando dos archivos —uno con y otro sin— para comparar cuál abre bien.

### Pesos tipográficos

El CSS usa 400/600/700/800. PowerPoint solo distingue regular y bold por familia, salvo que se referencien familias separadas ("Poppins SemiBold"), que no existen en todas las máquinas. Se mapea **600 y 800 a bold**: se pierde algo de matiz y se gana que el deck no se rompa en la máquina de otro.

### Glifos ausentes

Ni Poppins ni Open Sans traen `→` (U+2192). En el HTML el navegador hace fallback; en PowerPoint el resultado depende de la máquina. Por eso la flecha de "Próximos pasos" se **dibuja como forma** y el rango de fechas de la portada usa un guion corto (`6 – 17 de julio`) en vez de la flecha.

## 11 · Punto abierto de contenido

El deck HTML usa **"corrida"** en tres lugares (`index.html` líneas 143 y 193) y la convención del vault es **"ejecución"**.

En el PPTX se escribió **"ejecución"**: es contenido nuevo y la convención es vigente. El HTML sigue diciendo "corrida" porque ya fue presentado y corregirlo toca un artefacto entregado. **Queda a decisión del usuario** si se alinea el HTML o se dejan divergentes.

## 12 · Verificación

No hay PowerPoint ni LibreOffice en esta máquina —ni en WSL ni en el Windows anfitrión—, así que maquetar sería a ciegas. La verificación es en tres capas:

**Visual** (`preview.py`): un renderer propio lee el `.pptx` **ya generado** —posiciones, tamaños, rellenos, corridas de texto— y lo dibuja a PNG con los mismos TTF. Es un viaje de ida y vuelta: verifica lo que quedó en el archivo, no lo que el script creía estar escribiendo. No es fiel a PowerPoint al píxel, pero caza lo que de verdad falla al maquetar: desbordes, solapamientos, jerarquía rota.

**Estructural** (`verify_pptx.py`): tamaño de slide, formas fuera del área, texto que excede su caja según métricas de la fuente, imágenes embebidas y no enlazadas, y fuentes fuera del kit.

**Humana**: el usuario abre el `.pptx` y lo mira. Esa es la verificación definitiva y es el propósito del piloto — las dos primeras capas garantizan que el archivo no está roto, no que se ve bien en PowerPoint.

## 13 · Orden de trabajo

1. ~~Spike de `.fntdata`~~ — hecho; resultado en §10: es EOT, el incrustado se difiere.
2. ~~`theme.py` + `build_backgrounds.py` + los assets~~ — hecho.
3. ~~`preview.py`~~ — hecho (no previsto en el diseño original; lo obligó la ausencia de renderer).
4. ~~`sprint_14.py` — los 17 slides~~ — hecho.
5. ~~`verify_pptx.py`~~ — hecho; pasa sin problemas estructurales.
6. ~~Link de descarga en el hub~~ — hecho.
7. **El usuario abre el `.pptx` y da feedback.** ← acá estamos
8. Con ese feedback: deck HTML del Sprint 15 (20→31 jul 2026) → revisión de contenido → `sprint_15.py`.

## 14 · Riesgos

| Riesgo | Estado |
|---|---|
| El formato `.fntdata` no es TTF crudo | **Confirmado**: es EOT. Incrustado diferido, fallback en uso (§10) |
| El PPTX se ve distinto de lo esperado al abrirlo | Mitigado por `preview.py`, pero **no eliminado**: nadie lo abrió todavía en PowerPoint |
| Las tarjetas de paso quedan apretadas en flujos con pasos largos | Resuelto: la tarjeta se dimensiona por su contenido y la grilla se centra en el hueco |
| `pptx/` desentona con un repo "sin build" | Es tooling: no se sirve, no entra al deploy, el sitio sigue estático |
| La captura de la landing muestra el showcase del Release 2 | La landing de QA evolucionó desde el Sprint 14. **Pendiente**: decidir si se acepta o se busca una captura de época |
