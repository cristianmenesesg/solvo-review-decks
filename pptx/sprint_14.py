"""
Sprint Review 14 (6 → 17 jul 2026) — versión PowerPoint.

Deriva del deck HTML `reviews/sprint-14/index.html`, que es la fuente del
contenido y no se toca. Acá cada slide se dibuja explícitamente: no hay parser
ni mapeo automático, porque el layout de un deck tipográfico se decide slide por
slide. Lo único compartido con otros sprints es `theme.py`.

El HTML tiene 14 slides y este PPTX tiene 17: las cuatro capturas de On-Demand
comparten un slider en el HTML y acá se separan, porque en una grilla 2×2 quedan
a un cuarto de tamaño e ilegibles.

    .venv/bin/python sprint_14.py
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Pt

import theme as T
from theme import (
    CONTENT_R, CONTENT_W, PAD_TOP, PAD_X, SLIDE_H, SLIDE_W,
    badge, blank, chip_row, cqh, cqw, eyebrow, foot, oval, para,
    picture, pill, rect, signature_bg, simple_text, slide_head, text_width, textbox,
)

ROOT = Path(__file__).parent
DECK = ROOT.parent / "reviews" / "sprint-14"
SHOTS = DECK / "assets"
LOGO_WHITE = ROOT.parent / "assets" / "design-system" / "solvo-genai" / "logos" / "SolvoGenAI_Logo_White.png"
OUT = DECK / "sprint-14.pptx"

FOOTER = "Sprint Review 14"

# ═══════════════════════════════════════════════════════════════ contenido ══

PROJECTS = [
    ("CCO", "Current Client Openings", "Cada semana busca las vacantes nuevas de los clientes activos", "qa", "En QA"),
    ("TPS", "Talent Pool Scraping", "Captura del email del candidato en el pipeline · change request", "qa", "En QA"),
    ("ODO", "On-Demand Openings", "Scraping de vacantes por demanda desde Solvo Platform", "qa", "En QA"),
    ("ECO", "Landing de Agendamiento", "Landing propia para reservar reuniones con un comercial", "none", "Sin desplegar"),
]

FLOWS = [
    {
        "sigla": "CCO",
        "section": "Current Client Openings",
        "scope": "Cada semana busca, sin que nadie la dispare, las vacantes que publican los clientes activos de Solvo y le arma a cada vendedor el listado de sus cuentas.",
        "title": "Detección semanal de vacantes",
        "sub": "Cada viernes, en automático: encuentra las vacantes nuevas de los clientes y avisa a su vendedor.",
        "steps": [
            ("Arranque semanal", "Cada viernes el proceso arranca solo, sin que nadie lo dispare."),
            ("Chequeo de salud", "Antes de empezar, verifica que los servicios externos respondan; si alguno está caído, no arranca para no dejar resultados a medias."),
            ("Clientes activos", "Toma solo las empresas que hoy son clientes de Solvo."),
            ("Búsqueda en portales", "Busca en paralelo las vacantes publicadas por cada cliente en ambos portales; si una empresa falla, el resto continúa."),
            ("Consolidación", "Guarda las vacantes nuevas y descarta las que ya conocía."),
            ("Reporte al vendedor", "Envía a cada vendedor un correo con las vacantes recientes de sus clientes."),
        ],
        "cr": None,
        "state": "qa",
        "badge": "En QA",
        "note": "En pruebas con el listado oficial de clientes que entregó Solvo. Sale a producción apenas pase la validación — objetivo Sprint 15.",
        "stack": ["n8n", "PostgreSQL", "Oxylabs", "Apify", "Brevo"],
    },
    {
        "sigla": "TPS",
        "section": "Talent Pool Scraping — Release 2",
        "scope": "Busca en LinkedIn candidatos abiertos a trabajar fuera de USA y arma un pool listo para reclutar. Este sprint suma la captura del email de cada candidato.",
        "title": "Scraping de candidatos #OpenToWork",
        "sub": "Busca candidatos abiertos a trabajar en LinkedIn y, desde este sprint, también guarda su email.",
        "steps": [
            ("Disparo programado", "Arranca según la frecuencia configurada y recorre cada perfil de búsqueda, país por país y ciudad por ciudad."),
            ("Búsqueda de perfiles", "Busca en español e inglés, prioriza la señal open-to-work y excluye reclutadores."),
            ("Validación", "Revisa cada perfil, confirma que esté abierto a trabajar y descarta a quienes no lo están."),
            ("Captura de email", "Nuevo este sprint: en la misma ejecución busca y guarda el email de cada candidato. Antes se hacía después y a mano; ahora el candidato ya queda listo para contactar."),
            ("Disponibilidad oculta", "Revisa candidatos que no figuraban disponibles para detectar desempleo o freelance y reincorporarlos al pool."),
        ],
        "cr": 3,
        "state": "qa",
        "badge": "En QA",
        "note": "En QA la parte nueva: la búsqueda del email de cada candidato. Pasa a producción en el Sprint 16.",
        "stack": ["n8n", "Oxylabs", "PostgreSQL", "servicio de email", "OpenAI", "Brevo"],
    },
    {
        "sigla": "ODO",
        "section": "On-Demand Openings",
        "scope": "Desde Solvo Platform, el comercial pide las vacantes de una empresa puntual y revisa el resultado antes de guardarlo, sin esperar al barrido semanal.",
        "title": "Scraping de vacantes por demanda",
        "sub": "El comercial dispara, revisa un preview y decide qué guardar.",
        "steps": [
            ("Disparo", "Un comercial pide las vacantes de una empresa puntual; la plataforma verifica que no se haya consultado hace poco."),
            ("Búsqueda", "Busca las vacantes recientes de esa empresa en Indeed y LinkedIn, sin guardar nada todavía."),
            ("Preview", "Muestra el resultado en la plataforma para que el comercial revise y elija qué aceptar."),
            ("Confirmación", "Las vacantes aceptadas se traen completas, se evalúa con IA su viabilidad remota y se guardan asociadas a la empresa."),
            ("Trazabilidad", "Cada ejecución queda registrada: resultados, conteos y consumo."),
        ],
        "cr": None,
        "state": "qa",
        "badge": "En QA",
        "note": "En QA. Antes de salir a producción falta decidir en qué máquina va a correr — objetivo Sprint 16.",
        "stack": ["n8n", "Oxylabs", "OpenAI", "PostgreSQL", "Solvo Platform"],
    },
]

ODO_SHOTS = [
    ("on-demand-1.png", "Disparo desde el listado de Empresas",
     "Listado de Empresas con el popup Scrape Vacancies y la empresa buscada por nombre."),
    ("on-demand-2.png", "Preview antes de guardar",
     "Las vacantes encontradas por portal, listas para confirmar."),
    ("on-demand-3.png", "Vacantes guardadas en la empresa",
     "Detalle de la empresa, tab Vacantes, con el botón Scrape Vacancies Now."),
    ("on-demand-4.png", "Aviso por consulta reciente",
     "La plataforma avisa que la empresa ya se consultó hace poco."),
]

NEXT = [
    ("Current Client Openings", "Cargar el listado oficial de clientes y cerrar QA.", "Producción · Sprint 15 (31 jul)"),
    ("Talent Pool Scraping", "Instancia n8n dedicada en producción y cierre de QA de la captura de email.", "Producción · Sprint 16 (14 ago)"),
    ("On-Demand Openings", "Definir y aprovisionar la máquina destino en producción; el release de Solvo Platform con On-Demand entra a validación.", "Producción · Sprint 16 (14 ago)"),
    ("Landing de Agendamiento", "Resolver los 4 bloqueantes de infraestructura e integrar el despliegue real; luego Email Cold Outreach agenda con la landing.", "Producción · Sprint 15 (31 jul)"),
]

# ══════════════════════════════════════════════════════════════ componentes ══


def browser_frame(slide, x, y, w, h, url):
    """Marco de navegador: barra con semáforo y URL, y el viewport debajo."""
    bar_h = cqh(4)
    rect(slide, x, y, w, h + bar_h, fill=T.SURFACE, line=T.LINE, radius=8)
    rect(slide, x, y, w, bar_h, fill=T.GRAY_100, line=None)
    rect(slide, x, y + bar_h - 1, w, 1, fill=T.LINE)
    d = cqh(0.9)
    for i, c in enumerate(("#F87171", "#FBBF24", "#34D399")):
        oval(slide, x + cqh(1.4) + i * (d + cqh(0.7)), y + (bar_h - d) / 2, d, d, fill=T._c(c))
    simple_text(
        slide, x + cqh(1.4) + 3 * (d + cqh(0.7)) + cqw(0.8), y, w, bar_h, url,
        anchor="middle", size=cqh(1.4), font=T.MONO, color=T.INK_3, spacing=1.0,
    )
    return y + bar_h


def fit_image(path, box_w, box_h):
    """Escala una imagen para que entre en la caja, devolviendo (w, h)."""
    from PIL import Image

    iw, ih = Image.open(path).size
    r = min(box_w / iw, box_h / ih)
    return iw * r, ih * r


def accent_card(slide, x, y, w, h, radius=10):
    """Tarjeta clara con la barra naranja a la izquierda."""
    rect(slide, x, y, w, h, fill=T.SURFACE_2, line=T.LINE, radius=radius)
    rect(slide, x, y + 2, 3.5, h - 4, fill=T.ENERGY_D)


def deploy_band(slide, x, y, w, state, badge_text, note):
    """Banda de estado de despliegue bajo los pasos del flujo."""
    fill, border = T.DEPLOY_STATES[state]
    h = cqh(8.4)
    rect(slide, x, y, w, h, fill=fill, line=border, radius=cqh(1.2))
    bw, bh = badge(slide, x + cqh(2.2), y + (h - cqh(4.55)) / 2, state, badge_text, size=cqh(1.75))
    nx = x + cqh(2.2) + bw + cqw(1.6)
    simple_text(
        slide, nx, y, w - (nx - x) - cqh(2.2), h, note,
        anchor="middle", size=cqh(1.75), color=T.INK_2, spacing=1.35,
    )
    return h


# ═══════════════════════════════════════════════════════════════════ slides ══


def s_cover(prs):
    s = blank(prs)
    signature_bg(s)
    picture(s, LOGO_WHITE, PAD_X, PAD_TOP, h=cqh(4.4))

    # El bloque se centra verticalmente, como el `justify-content: center` del CSS.
    k = cqh(1.9)
    h1 = cqh(9)
    m = cqh(2)
    ph = cqh(1.9) * 1.2 + cqh(1.8)
    block = (k * 1.4 + cqh(2.2) + h1 * 1.1 * 2 + cqh(2.4) + m * 1.4 + cqh(4) + ph)
    y = (SLIDE_H - block) / 2 + cqh(2)
    simple_text(
        s, PAD_X, y, CONTENT_W, k * 1.4, "SPRINT REVIEW · SPRINT 14",
        size=k, font=T.HEADING, bold=True, color=T.ON_DARK_EYEBROW, tracking=k * 0.26, spacing=1.0,
    )
    y += k * 1.4 + cqh(2.2)

    tb = textbox(s, PAD_X, y, CONTENT_W, h1 * 1.1 * 2)
    para(tb.text_frame, "Cuatro proyectos", first=True, size=h1, font=T.HEADING, bold=True,
         color=T.WHITE, spacing=1.05)
    para(tb.text_frame, "camino a producción", size=h1, font=T.HEADING, bold=True,
         color=T.ON_DARK_HL, spacing=1.05)
    y += h1 * 1.1 * 2 + cqh(2.4)

    left = "6 – 17 de julio de 2026"  # `→` no existe en Poppins ni en Open Sans
    lw = text_width(left, m)
    simple_text(s, PAD_X, y, lw + 6, m * 1.4, left, size=m, color=T.ON_DARK_SOFT, spacing=1.0)
    rect(s, PAD_X + lw + cqw(1.5), y + m * 0.15, 1, m * 1.1, fill=T.ON_DARK_SOFT)
    mx = PAD_X + lw + cqw(3)
    simple_text(s, mx, y, CONTENT_R - mx, m * 1.4, "Softgic · Product Owner",
                size=m, color=T.ON_DARK_SOFT, spacing=1.0)
    y += m * 1.4 + cqh(4)

    size = cqh(1.9)
    cx = PAD_X
    for sigla, name, *_ in PROJECTS:
        label = f"{sigla} · {name}"
        w = cqh(1.6) * 2 + text_width(label, size, T.HEADING, True)
        if cx + w > CONTENT_R:
            cx, y = PAD_X, y + ph + cqh(1)
        pill(s, cx, y, w, ph, fill=T._c("#6B5BC4"), line=T._c("#9A8AE0"))
        tb = textbox(s, cx, y, w, ph, anchor="middle")
        p = para(tb.text_frame, first=True, spacing=1.0, align="center")
        T.add_run(p, sigla, size=size, font=T.HEADING, bold=True, color=T.ON_DARK_EYEBROW)
        T.add_run(p, f" · {name}", size=size, font=T.HEADING, bold=True, color=T.WHITE)
        cx += w + cqw(1.2)
    return s


def s_agenda(prs):
    s = blank(prs)
    y = slide_head(s, "Agenda", "Los cuatro proyectos del sprint")
    y += cqh(3.2)

    # Las filas se reparten el alto disponible en vez de amontonarse arriba.
    gap = cqh(1)
    row_h = (SLIDE_H - cqh(9) - y - gap * (len(PROJECTS) - 1)) / len(PROJECTS)
    for sigla, name, desc, state, btext in PROJECTS:
        simple_text(s, PAD_X, y, cqw(8), row_h, sigla, anchor="middle",
                    size=cqh(3), font=T.HEADING, bold=True, color=T.ENERGY_D, spacing=1.0)

        nx = PAD_X + cqw(8)
        nw = CONTENT_W - cqw(8) - cqw(16)
        tb = textbox(s, nx, y, nw, row_h, anchor="middle")
        para(tb.text_frame, name, first=True, size=cqh(2.8), font=T.HEADING, bold=True,
             color=T.INK, spacing=1.1, after=cqh(0.5))
        para(tb.text_frame, desc, size=cqh(1.7), color=T.INK_3, spacing=1.2)

        bw = cqh(1.4) * 2 + cqh(1.1) + cqh(1.7) * 0.7 + text_width(btext, cqh(1.7), T.HEADING, True)
        badge(s, CONTENT_R - bw, y + (row_h - cqh(4.5)) / 2, state, btext)

        rect(s, PAD_X, y + row_h, CONTENT_W, 1, fill=T.LINE)
        y += row_h + gap

    foot(s, FOOTER)
    return s


def s_section(prs, index, total, title, scope):
    s = blank(prs)
    signature_bg(s)

    idx = f"{index:02d} / {total:02d}"
    isz = cqh(1.8)
    iw = text_width(idx, isz, T.HEADING, True, tracking=isz * 0.2)
    simple_text(s, CONTENT_R - iw - 4, PAD_TOP, iw + 8, isz * 1.4, idx,
                size=isz, font=T.HEADING, bold=True, color=T.ON_DARK_SOFT,
                tracking=isz * 0.2, spacing=1.0, align="right")

    tsz = cqh(7.2)
    lines = 2 if text_width(title, tsz, T.HEADING, True) > CONTENT_W * 0.62 else 1
    ssz = cqh(2.6)
    slines = 1 + int(text_width(scope, ssz) // (CONTENT_W * 0.66))
    block = 3 + cqh(3.2) + tsz * 1.1 * lines + cqh(2.8) + ssz * 1.4 * slines
    y = (SLIDE_H - block) / 2

    rect(s, PAD_X, y, cqh(7), 3, fill=T.ENERGY)
    y += 3 + cqh(3.2)
    simple_text(s, PAD_X, y, CONTENT_W * 0.66, tsz * 1.1 * lines, title,
                size=tsz, font=T.HEADING, bold=True, color=T.WHITE, spacing=1.05)
    y += tsz * 1.1 * lines + cqh(2.8)
    simple_text(s, PAD_X, y, CONTENT_W * 0.66, ssz * 1.4 * slines, scope,
                size=ssz, color=T.ON_DARK_SCOPE, spacing=1.4)
    return s


def s_flow(prs, f):
    s = blank(prs)
    y = slide_head(s, f["section"], f["title"], f["sub"])

    # ── rail ────────────────────────────────────────────────────────────────
    steps = f["steps"]
    n = len(steps)
    node_d = cqh(8.2)
    # El nodo con change request lleva etiqueta encima: hay que dejarle aire.
    rail_top = y + (cqh(6.4) if f["cr"] is not None else cqh(2.6))
    slot = CONTENT_W / n
    centers = [PAD_X + (i + 0.5) * slot for i in range(n)]

    track_y = rail_top + node_d / 2
    rect(s, centers[0], track_y - 1.5, centers[-1] - centers[0], 3, fill=T.ENERGY)

    for i, (label, _) in enumerate(steps):
        cx = centers[i]
        is_cr = f["cr"] == i
        if is_cr:
            r = node_d / 2 + cqh(0.9)
            oval(s, cx - r, track_y - r, r * 2, r * 2, line=T.ENERGY, line_w=1.5, dashed=True)
            tag = "CHANGE REQUEST"
            tsz = cqh(1.25)
            tw = cqh(1) * 2 + text_width(tag, tsz, T.HEADING, True, tracking=tsz * 0.14)
            th = tsz * 1.2 + cqh(1)
            pill(s, cx - tw / 2, rail_top - th - cqh(1.4), tw, th,
                 fill=T._c("#FEF3EC"), line=T._c("#EFB88C"))
            simple_text(s, cx - tw / 2, rail_top - th - cqh(1.4), tw, th, tag,
                        anchor="middle", align="center", size=tsz, font=T.HEADING, bold=True,
                        color=T.ENERGY_D, tracking=tsz * 0.14, spacing=1.0)

        oval(s, cx - node_d / 2, rail_top, node_d, node_d,
             fill=T.ENERGY_D if is_cr else T.SURFACE, line=T.ENERGY if is_cr else T.LINE_2, line_w=2)
        simple_text(s, cx - node_d / 2, rail_top, node_d, node_d, str(i + 1),
                    anchor="middle", align="center", size=cqh(3), font=T.HEADING, bold=True,
                    color=T.WHITE if is_cr else T.INK_3, spacing=1.0)

        lsz = cqh(1.65)
        ly = rail_top + node_d + cqh(1.4)
        simple_text(s, cx - slot / 2 + cqw(0.4), ly, slot - cqw(0.8), lsz * 1.25 * 2, label,
                    align="center", size=lsz, font=T.HEADING, bold=True,
                    color=T.INK if is_cr else T.INK_2, spacing=1.25)

    rail_bottom = rail_top + node_d + cqh(1.4) + cqh(1.65) * 1.25 * 2

    # ── tarjetas de paso ────────────────────────────────────────────────────
    cols = 3
    gap = cqw(1.5)
    card_w = (CONTENT_W - gap * (cols - 1)) / cols
    rows = (n + cols - 1) // cols
    band_top = SLIDE_H - cqh(3) - cqh(1.35) * 1.4 - cqh(2.4) - cqh(3.6) - cqh(8.4)

    # La tarjeta se dimensiona por su contenido, no por el hueco disponible: si
    # se estira al hueco, las descripciones cortas dejan un vacío enorme abajo.
    pad = cqh(1.6)
    inner_w = card_w - pad * 2 - 3
    t_size, d_size = cqh(1.9), cqh(1.6)
    card_h = pad * 2 + cqh(0.9) + max(
        T.wrap_count(f"{i + 1:02d}  {label}", inner_w, t_size, T.HEADING, True) * t_size * 1.15
        + T.wrap_count(desc, inner_w, d_size) * d_size * 1.32
        for i, (label, desc) in enumerate(steps)
    )
    row_gap = cqh(1.6)
    grid_h = rows * card_h + (rows - 1) * row_gap
    cards_top = rail_bottom + max((band_top - rail_bottom - grid_h) / 2, cqh(2))

    for i, (label, desc) in enumerate(steps):
        r, c = divmod(i, cols)
        x = PAD_X + c * (card_w + gap)
        cy = cards_top + r * (card_h + row_gap)
        accent_card(s, x, cy, card_w, card_h, radius=8)

        tb = textbox(s, x + pad + 3, cy + pad, inner_w, card_h - pad * 2)
        p = para(tb.text_frame, first=True, spacing=1.15, after=cqh(0.9))
        T.add_run(p, f"{i + 1:02d}", size=cqh(1.9), font=T.HEADING, bold=True, color=T.ENERGY_D)
        T.add_run(p, f"  {label}", size=cqh(1.9), font=T.HEADING, bold=True, color=T.INK)
        para(tb.text_frame, desc, size=cqh(1.6), color=T.INK_2, spacing=1.32)

    # ── estado + stack ──────────────────────────────────────────────────────
    deploy_band(s, PAD_X, band_top, CONTENT_W, f["state"], f["badge"], f["note"])
    chip_row(s, PAD_X, band_top + cqh(8.4) + cqh(2.4), f["stack"])
    foot(s, f"{FOOTER} · {f['sigla']}")
    return s


def s_shot(prs, i, total, filename, caption, desc):
    s = blank(prs)
    y = PAD_TOP
    y += eyebrow(s, PAD_X, y, "On-Demand Openings") + cqh(1.0)
    simple_text(s, PAD_X, y, CONTENT_W, cqh(4.6) * 1.15, "La experiencia en Solvo Platform",
                size=cqh(4.6), font=T.HEADING, bold=True, color=T.INK, spacing=1.05)

    col_w = cqw(24)
    frame_x = PAD_X + col_w + cqw(3)
    frame_w = CONTENT_R - frame_x
    top = cqh(22)
    avail_h = SLIDE_H - top - cqh(8)
    iw, ih = fit_image(SHOTS / filename, frame_w, avail_h - cqh(4))
    fx = frame_x + (frame_w - iw) / 2
    vy = browser_frame(s, fx, top, iw, ih, "solvoplatform.solvoglobal.com · Sales Hub")
    picture(s, SHOTS / filename, fx, vy, iw, ih)

    # La columna se centra contra la captura en vez de colgar del borde superior.
    isz, csz, dsz = cqh(1.5), cqh(3), cqh(1.9)
    c_lines = T.wrap_count(caption, col_w, csz, T.HEADING, True)
    d_lines = T.wrap_count(desc, col_w, dsz)
    block = isz * 1.4 + cqh(1.6) + c_lines * csz * 1.15 + cqh(1.4) + d_lines * dsz * 1.4
    ty = top + (ih + cqh(4) - block) / 2

    idx = f"{i:02d} / {total:02d}"
    simple_text(s, PAD_X, ty, col_w, isz * 1.4, idx, size=isz, font=T.HEADING, bold=True,
                color=T.ENERGY_D, tracking=isz * 0.22, spacing=1.0)
    ty += isz * 1.4 + cqh(1.6)
    simple_text(s, PAD_X, ty, col_w, c_lines * csz * 1.15, caption,
                size=csz, font=T.HEADING, bold=True, color=T.INK, spacing=1.12)
    ty += c_lines * csz * 1.15 + cqh(1.4)
    simple_text(s, PAD_X, ty, col_w, d_lines * dsz * 1.4, desc,
                size=dsz, color=T.INK_2, spacing=1.4)

    foot(s, f"{FOOTER} · ODO")
    return s


def s_landing(prs):
    s = blank(prs)
    y = slide_head(s, "Landing de Agendamiento", "La landing en vivo · QA",
                   "Integración real con el calendario, corriendo en QA.")

    col_w = cqw(29)
    frame_w = CONTENT_W - col_w - cqw(3)
    top = y + cqh(3)
    iw, ih = fit_image(ROOT / "assets" / "landing-qa.png", frame_w, SLIDE_H - top - cqh(12))
    vy = browser_frame(s, PAD_X, top, iw, ih, "book.solvoglobal.com · QA")
    picture(s, ROOT / "assets" / "landing-qa.png", PAD_X, vy, iw, ih)

    ax = CONTENT_R - col_w
    ay = top
    simple_text(s, ax, ay, col_w, cqh(2.1) * 1.4 * 3,
                "El prospecto llega ya identificado por la URL del cold email — sin formulario.",
                size=cqh(2.1), font=T.HEADING, bold=True, color=T.INK, spacing=1.35)
    ay += cqh(2.1) * 1.4 * 3 + cqh(2)

    for step in ("Ve la disponibilidad real del calendario.",
                 "Elige día y hora y confirma.",
                 "Se crea la reunión con videollamada en Teams.",
                 "Recibe el correo de confirmación y descarga el .ics."):
        h = cqh(1.85) * 1.35 * 2
        oval(s, ax + 1, ay + cqh(0.75), cqh(0.9), cqh(0.9), fill=T.ENERGY)
        simple_text(s, ax + cqh(2.4), ay, col_w - cqh(2.4), h, step,
                    size=cqh(1.85), color=T.INK_2, spacing=1.35)
        ay += h * 0.62 + cqh(1.1)

    ay += cqh(1.4)
    chip_row(s, ax, ay, ["Azure Static Web App", "Microsoft Graph", "M365"])
    ay += cqh(4.3)
    chip_row(s, ax, ay, ["Azure Container App", "Brevo", "PostgreSQL"], label="")
    ay += cqh(5)

    badge(s, ax, ay, "none", "Sin desplegar")
    simple_text(s, ax, ay + cqh(5.2), col_w, cqh(1.5) * 1.4 * 4,
                "MVP con 4 bloqueantes de infraestructura. Producción en el Sprint 15; el dominio "
                "book.solvoglobal.com queda pendiente del go-live.",
                size=cqh(1.5), color=T.INK_3, spacing=1.4)

    foot(s, f"{FOOTER} · ECO")
    return s


def s_mails(prs):
    s = blank(prs)
    y = slide_head(s, "Landing de Agendamiento", "Correos de confirmación")
    y += cqh(2.2)

    note = ("Cada reserva dispara dos correos con marca propia: al prospecto, con la fecha, la hora "
            "y el enlace de la videollamada; y un aviso interno a la cuenta de agendamiento, con los "
            "datos del prospecto para reasignar el comercial.")
    mails = [
        ("Al prospecto", "“Your meeting with Solvo is confirmed”", "email-prospect.png"),
        ("Aviso interno", "“New meeting booked: Sarah Chen (Acme Corp)”", "email-account.png"),
    ]
    # El asunto del aviso interno ocupa dos líneas: el alto del epígrafe se mide,
    # no se asume, o la captura se le monta encima.
    sub_size, cap_w0 = cqh(1.75), cqw(24)
    sub_lines = max(T.wrap_count(sj, cap_w0, sub_size, T.HEADING, True) for _, sj, _ in mails)
    head_h = cqh(2.4) + sub_lines * sub_size * 1.35 + cqh(1.8)
    # Las capturas van a la izquierda con el título, y la nota ocupa la columna
    # que dejan libres: un slide centrado dejaría un tercio vacío a cada lado.
    note_w = cqw(26)
    body_w = CONTENT_W - note_w - cqw(4)
    avail = SLIDE_H - y - cqh(8.5) - head_h
    # Las capturas son muy verticales: mandan ellas el ancho de columna, y el par
    # se centra. Así el epígrafe queda pegado a su imagen y no flotando lejos.
    sizes = [fit_image(SHOTS / fn, body_w / 2 - cqw(2), avail) for _, _, fn in mails]
    gap = cqw(4)
    pair_w = sum(w for w, _ in sizes) + gap
    x0 = PAD_X + (body_w - pair_w) / 2

    for (to, subject, fn), (iw, ih) in zip(mails, sizes):
        cx = x0 + (iw - cap_w0) / 2
        simple_text(s, cx, y, cap_w0, cqh(1.5) * 1.4, to.upper(),
                    align="center", size=cqh(1.5), font=T.HEADING, bold=True, color=T.ENERGY_D,
                    tracking=cqh(1.5) * 0.18, spacing=1.0)
        simple_text(s, cx, y + cqh(2.4), cap_w0, sub_lines * sub_size * 1.35, subject,
                    align="center", size=sub_size, font=T.HEADING, bold=True, color=T.INK,
                    spacing=1.35)

        shot_top = y + head_h
        rect(s, x0 - 4, shot_top - 4, iw + 8, ih + 8, fill=T.SURFACE, line=T.LINE, radius=8)
        picture(s, SHOTS / fn, x0, shot_top, iw, ih)
        x0 += iw + gap

    nx = PAD_X + body_w + cqw(4)
    simple_text(s, nx, y + head_h, note_w, avail, note,
                size=cqh(1.95), color=T.INK_2, spacing=1.5)

    foot(s, f"{FOOTER} · ECO")
    return s


def s_next(prs):
    s = blank(prs)
    y = slide_head(s, "Próximos pasos", "Qué sigue por proyecto")
    y += cqh(3.4)

    gap_x, gap_y = cqw(2.6), cqh(2.6)
    cw = (CONTENT_W - gap_x) / 2
    t_size, s_size, g_size = cqh(2.4), cqh(1.85), cqh(1.6)

    # La grilla cuelga del encabezado como en el resto de los slides; el aire
    # sobrante se reparte en el padding de la tarjeta, no en un hueco bajo el título.
    avail = SLIDE_H - y - cqh(9)
    body = t_size * 1.1 + cqh(1.2) + cqh(1.6) + g_size * 1.2 + max(
        T.wrap_count(step, cw - cqh(2.6) * 2 - 3, s_size) * s_size * 1.4 for _, step, _ in NEXT
    )
    ch = (avail - gap_y) / 2
    pad = max(min((ch - body) / 2, cqh(7)), cqh(2.4))
    ch = min(ch, body + pad * 2)
    inner_w = cw - pad * 2 - 3

    for i, (title, step, target) in enumerate(NEXT):
        r, c = divmod(i, 2)
        x = PAD_X + c * (cw + gap_x)
        cy = y + r * (ch + gap_y)
        accent_card(s, x, cy, cw, ch, radius=cqh(1.6))

        tb = textbox(s, x + pad + 3, cy + pad, inner_w, ch - pad * 2)
        para(tb.text_frame, title, first=True, size=t_size, font=T.HEADING, bold=True,
             color=T.INK, spacing=1.1, after=cqh(1.2))
        para(tb.text_frame, step, size=s_size, color=T.INK_2, spacing=1.4)

        gy = cy + ch - pad - g_size * 1.2
        T.arrow(s, x + pad + 3, gy + g_size * 0.22, g_size * 0.85, g_size * 0.62)
        simple_text(s, x + pad + 3 + g_size * 1.3, gy, inner_w, g_size * 1.2, target,
                    size=g_size, font=T.HEADING, bold=True, color=T.ENERGY_D, spacing=1.2)

    foot(s, FOOTER)
    return s


def s_end(prs):
    s = blank(prs)
    signature_bg(s)
    lh = cqh(5)
    logo_w = lh * (1333 / 460)
    picture(s, LOGO_WHITE, (SLIDE_W - logo_w) / 2, cqh(30), h=lh)

    simple_text(s, 0, cqh(38), SLIDE_W, cqh(8) * 1.15, "¿Preguntas?",
                align="center", size=cqh(8), font=T.HEADING, bold=True, color=T.WHITE, spacing=1.05)
    simple_text(s, 0, cqh(49), SLIDE_W, cqh(2.4) * 1.4,
                "Gracias — Sprint Review 14 · Softgic Product Owner",
                align="center", size=cqh(2.4), color=T.ON_DARK_SOFT, spacing=1.0)
    return s


# ═════════════════════════════════════════════════════════════════════ main ══


def build():
    prs = Presentation()
    prs.slide_width = Pt(SLIDE_W)
    prs.slide_height = Pt(SLIDE_H)

    s_cover(prs)
    s_agenda(prs)

    for i, f in enumerate(FLOWS, 1):
        s_section(prs, i, 4, f["section"], f["scope"])
        s_flow(prs, f)
        if f["sigla"] == "ODO":
            for j, (fn, cap, desc) in enumerate(ODO_SHOTS, 1):
                s_shot(prs, j, len(ODO_SHOTS), fn, cap, desc)

    s_section(prs, 4, 4, "Landing de Agendamiento",
              "Una página propia con marca Solvo donde el prospecto elige día y hora y agenda su "
              "reunión. Reemplaza la página genérica de Microsoft Bookings.")
    s_landing(prs)
    s_mails(prs)
    s_next(prs)
    s_end(prs)

    prs.save(str(OUT))
    print(f"{OUT.relative_to(ROOT.parent)}  ·  {len(prs.slides.__iter__.__self__._sldIdLst)} slides  ·  {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    build()
