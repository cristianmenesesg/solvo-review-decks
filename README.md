# Solvo Review Decks

Sitio estático (sin build) para las **presentaciones de Sprint Review** del equipo de Product Owner. Decks HTML animados, con navegación por teclado, controles auto-ocultables y pantalla completa. Brand **Solvo GenAI**.

> No reemplaza el vault: el contenido canónico de cada review vive en `sprints/…` y en los productos. Este sitio es solo la **capa de presentación**.

## Estructura

```
index.html                     — hub: lista de decks de review
assets/design-system/          — tokens.css + logos Solvo GenAI (vendorizados por copia)
engine/                        — motor reutilizable entre decks
  deck.css / deck.js           — slides 16:9, navegación, fullscreen, controles, progreso
  flow.css / flow.js           — "pipeline vivo": nodos interactivos + scrubber (proyectos de automatización)
  media.css / media.js         — slider de capturas + toggle de dispositivo del iframe
reviews/<sprint>/index.html    — un deck por review
```

El escenario es un contenedor 16:9; la tipografía y el espaciado escalan en **unidades de contenedor** (`cqh`/`cqw`), así el deck se ve igual en laptop, proyector o pantalla completa.

## Presentar

```bash
npx serve .        # o: python3 -m http.server 5173
```

Abrir `http://localhost:3000/reviews/sprint-14/` (el puerto lo indica `serve`).

**Controles**: `→` / `Espacio` avanza · `←` retrocede · `F` pantalla completa · `Home` / `End` a los extremos. Controles flotantes en la esquina inferior derecha (prev/next, índice y pantalla completa); se auto-ocultan. En los slides de flujo: **click en un nodo** para ver ese paso en grande; el estado de despliegue va en una banda visible bajo los pasos.

## Autoría de un deck nuevo

1. Copiar `reviews/sprint-14/` a `reviews/sprint-NN/` y editar el contenido.
2. Cada slide es un `<section class="slide …">` dentro de `.stage`; el motor los descubre solos. Actualizar el total del contador (`data-counter-tot`).
3. **Flujo interactivo**: un `.flow` con nodos `<button class="flow-node" data-label data-title data-desc [data-cr]>`; el `data-title` admite HTML (`<span class="hl">`). El nodo con `data-cr` recibe el anillo y la etiqueta *change request*. El estado va en `<div class="deploy" data-state="qa|none|prod">` bajo los pasos.
4. **Landing por iframe**: `iframe[data-src]` se carga en diferido al activarse su slide. El toggle Desktop/Tablet/Mobile cambia el ancho del marco.
5. **Imágenes empotradas**: las capturas y los logos van **dentro del HTML/CSS como data URI** (WebP en base64), no como archivos referenciados. Así el deck no depende de cómo se sirva la página: si carga el HTML, cargan las imágenes. Los PNG originales quedan en `reviews/<sprint>/assets/` como fuente para regenerar.
6. Añadir una card al hub (`index.html`).

## Convenciones de review

Portada de sección = una frase de alcance; nunca el número de épica (nombre completo); títulos de HU literales cuando se citan; siglas vigentes (CCO, TPS, ODO, ECO). Estados de despliegue y próximos pasos salen de `shared/tracking/Roadmap-Entregas-Handoff.md`.

## Design system

`tokens.css` y logos se copian de `shared/design-system/solvo-genai/`. Cuando el DS cambie, re-copiarlos. Los fondos se generan por CSS (gradiente de firma 135° púrpura→azul), no por PNG, para mantener el sitio liviano.

## Deploy

Estático en Vercel (raíz del proyecto, sin build). `vercel.json` incluido.

Dos notas sobre esa config:

- `trailingSlash: true` — sin la barra final, el navegador resolvería una ruta relativa como `assets/x.png` contra el directorio padre y daría 404.
- **No agregar claves propias a `vercel.json`** (por ejemplo un `_comment`): Vercel lo valida contra un esquema estricto y cualquier propiedad desconocida hace **fallar el build**. Cuando el build falla, Vercel deja vivo el último deploy exitoso, así que el sitio parece "viejo" en vez de roto — un síntoma engañoso.
