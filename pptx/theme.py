"""
Kit de marca Solvo GenAI para los decks de Sprint Review en PowerPoint.

No conoce ningún deck: expone los tokens del design system, la conversión de
unidades del CSS y un puñado de helpers de dibujo. Cada sprint es un script
aparte que llama a estos helpers y dibuja sus slides explícitamente.

CONVERSIÓN DE UNIDADES
    El escenario del HTML es un contenedor 16:9 y todo el CSS escala en `cqh`
    y `cqw`, que son porcentajes de ese escenario. Un PPTX widescreen mide
    960 × 540 pt, así que la conversión es lineal y exacta:

        1 cqh = 5.4 pt          1 cqw = 9.6 pt

    Toda medida de acá sale de multiplicar el valor del CSS. El PPT hereda la
    retícula del HTML, no una aproximación.

PESOS TIPOGRÁFICOS
    El CSS usa 400/600/700/800. PowerPoint solo distingue regular y bold por
    familia, salvo que se referencien familias separadas ("Poppins SemiBold"),
    que no existen en todas las máquinas. Se mapea 600 y 800 a bold: se pierde
    algo de matiz y se gana que el deck no se rompa en la máquina de otro.
"""

from pathlib import Path

from PIL import ImageFont
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

# ─────────────────────────────────────────────────────────────── geometría ──

SLIDE_W = 960.0  # pt — 13.333 in
SLIDE_H = 540.0  # pt — 7.5 in


def cqh(n):
    """Unidad de alto del contenedor del HTML → puntos."""
    return n * 5.4


def cqw(n):
    """Unidad de ancho del contenedor del HTML → puntos."""
    return n * 9.6


PAD_TOP = cqh(7)  # 37.8 — `.slide { padding: 7cqh 8cqw }`
PAD_X = cqw(8)  # 76.8
CONTENT_W = SLIDE_W - 2 * PAD_X  # 806.4
CONTENT_R = SLIDE_W - PAD_X

# ───────────────────────────────────────────────────────────────── colores ──


def _c(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


INK = _c("#111827")
INK_2 = _c("#4B5563")
INK_3 = _c("#9CA3AF")
SURFACE = _c("#FFFFFF")
SURFACE_2 = _c("#F9FAFB")
LINE = _c("#E5E7EB")
LINE_2 = _c("#D1D5DB")

ENERGY = _c("#F19556")
ENERGY_D = _c("#E07E3A")
VIOLET = _c("#775AE5")
BLUE = _c("#3869E0")

SUCCESS = _c("#16A34A")
SUCCESS_LIGHT = _c("#DCFCE7")
SUCCESS_DARK = _c("#166534")
WARNING = _c("#F59E0B")
WARNING_LIGHT = _c("#FEF3C7")
WARNING_DARK = _c("#92400E")
NEUTRAL_ACCENT = _c("#8F939E")
GRAY_100 = _c("#F3F4F6")

WHITE = _c("#FFFFFF")
# Sobre los slides oscuros el gradiente recortado del `.hl` se resuelve sólido.
ON_DARK_HL = _c("#FDBA8C")
ON_DARK_EYEBROW = _c("#FBBF77")
ON_DARK_SOFT = _c("#DAD5F2")  # rgba(255,255,255,.85) sobre el gradiente
ON_DARK_SCOPE = _c("#E4E0F6")  # rgba(255,255,255,.90)

# Estados de despliegue: (color de texto, relleno de la píldora, borde, punto)
BADGE_STATES = {
    "prod": (SUCCESS_DARK, SUCCESS_LIGHT, _c("#A7DDBA"), SUCCESS),
    "qa": (WARNING_DARK, WARNING_LIGHT, _c("#F6CE85"), WARNING),
    "none": (INK_2, GRAY_100, LINE_2, NEUTRAL_ACCENT),
}
# Banda de estado bajo los pasos del flujo: (relleno, borde)
DEPLOY_STATES = {
    "prod": (_c("#F1FBF4"), _c("#BCE5C9")),
    "qa": (_c("#FEFBF4"), _c("#F7DCA8")),
    "none": (SURFACE_2, LINE_2),
}

# ──────────────────────────────────────────────────────────── tipografía ──

HEADING = "Poppins"
BODY = "Open Sans"
MONO = "Consolas"  # JetBrains Mono no está en máquinas corporativas

# Los TTF locales sirven para medir el texto y para que el usuario los instale.
# Consolas no se distribuye: se lee de Windows solo para medir, con fallback.
_CONSOLAS = Path("/mnt/c/Windows/Fonts/consola.ttf")
_CONSOLAS_B = Path("/mnt/c/Windows/Fonts/consolab.ttf")

_FONT_FILES = {
    (HEADING, False): FONTS / "Poppins-400.ttf",
    (HEADING, True): FONTS / "Poppins-700.ttf",
    (BODY, False): FONTS / "OpenSans-400.ttf",
    (BODY, True): FONTS / "OpenSans-700.ttf",
    (MONO, False): _CONSOLAS if _CONSOLAS.exists() else FONTS / "OpenSans-400.ttf",
    (MONO, True): _CONSOLAS_B if _CONSOLAS_B.exists() else FONTS / "OpenSans-700.ttf",
}
_metrics_cache = {}


def font_file(name, bold):
    return _FONT_FILES.get((name, bold), _FONT_FILES[(BODY, bold)])


def text_width(text, size_pt, name=BODY, bold=False, tracking=0.0):
    """Ancho real de un texto en puntos, medido contra el TTF."""
    key = (name, bold)
    if key not in _metrics_cache:
        _metrics_cache[key] = ImageFont.truetype(str(font_file(name, bold)), 100)
    f = _metrics_cache[key]
    w = f.getlength(text) * size_pt / 100
    return w + tracking * max(len(text) - 1, 0)


def wrap_count(text, max_w, size_pt, name=BODY, bold=False, tracking=0.0):
    """Cuántas líneas ocupa un texto en `max_w`. Mismo corte por palabra que PowerPoint."""
    lines, cur = 1, ""
    for word in text.split(" "):
        probe = f"{cur} {word}".strip()
        if cur and text_width(probe, size_pt, name, bold, tracking) > max_w:
            lines += 1
            cur = word
        else:
            cur = probe
    return lines


def text_height(text, max_w, size_pt, name=BODY, bold=False, spacing=1.3, tracking=0.0):
    return wrap_count(text, max_w, size_pt, name, bold, tracking) * size_pt * spacing


# ─────────────────────────────────────────────────────────────── helpers ──


def blank(prs):
    """Slide en blanco, sin placeholders."""
    return prs.slides.add_slide(prs.slide_layouts[6])


def picture(slide, path, x, y, w=None, h=None):
    kw = {}
    if w is not None:
        kw["width"] = Pt(w)
    if h is not None:
        kw["height"] = Pt(h)
    return slide.shapes.add_picture(str(path), Pt(x), Pt(y), **kw)


def signature_bg(slide):
    """Fondo de marca a sangre: gradiente 135° + halos, horneado a PNG."""
    return picture(slide, ASSETS / "bg-signature.png", 0, 0, SLIDE_W, SLIDE_H)


def _no_shadow(shape):
    shape.shadow.inherit = False


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.0, radius=None):
    """Rectángulo, redondeado si `radius` (en pt) viene dado."""
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, Pt(x), Pt(y), Pt(w), Pt(h))
    if radius:
        # El ajuste va como fracción de la mitad del lado menor.
        s.adjustments[0] = min(radius / (min(w, h) / 2), 1.0) * 0.5
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    _no_shadow(s)
    s.text_frame.word_wrap = False
    return s


def pill(slide, x, y, w, h, fill=None, line=None, line_w=1.0):
    return rect(slide, x, y, w, h, fill=fill, line=line, line_w=line_w, radius=h / 2)


def oval(slide, x, y, w, h, fill=None, line=None, line_w=1.0, dashed=False):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(x), Pt(y), Pt(w), Pt(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
        if dashed:
            from pptx.enum.dml import MSO_LINE_DASH_STYLE

            s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    _no_shadow(s)
    return s


def arrow(slide, x, y, w, h, color=ENERGY_D):
    """Flecha a la derecha como forma. Ni Poppins ni Open Sans traen el glifo `→`,
    así que dibujarla evita depender del fallback de fuentes de cada máquina."""
    s = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Pt(x), Pt(y), Pt(w), Pt(h))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    _no_shadow(s)
    return s


def textbox(slide, x, y, w, h, anchor="top"):
    tb = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {
        "top": MSO_ANCHOR.TOP,
        "middle": MSO_ANCHOR.MIDDLE,
        "bottom": MSO_ANCHOR.BOTTOM,
    }[anchor]
    return tb


def para(
    tf,
    text="",
    size=12,
    font=BODY,
    bold=False,
    color=INK,
    spacing=1.2,
    before=0,
    after=0,
    align="left",
    tracking=0.0,
    first=False,
):
    """Agrega un párrafo. `tracking` es letter-spacing en pt."""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.line_spacing = spacing
    p.space_before = Pt(before)
    p.space_after = Pt(after)
    p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
    if text:
        add_run(p, text, size=size, font=font, bold=bold, color=color, tracking=tracking)
    return p


def add_run(p, text, size=12, font=BODY, bold=False, color=INK, tracking=0.0):
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.name = font
    r.font.bold = bold
    r.font.color.rgb = color
    if tracking:
        # `spc` va en centésimas de punto sobre a:rPr (font._element ES el rPr).
        r.font._element.set("spc", str(int(round(tracking * 100))))
    return r


def simple_text(slide, x, y, w, h, text, anchor="top", **kw):
    tb = textbox(slide, x, y, w, h, anchor=anchor)
    para(tb.text_frame, text, first=True, **kw)
    return tb


# ──────────────────────────────────────────────────── componentes de marca ──


def eyebrow(slide, x, y, text, on_dark=False):
    """Regla naranja + texto en versalitas espaciadas. Devuelve el alto usado."""
    size = cqh(1.7)  # 9.18 pt
    tracking = size * 0.26  # letter-spacing: .26em
    rule_w = cqh(2.6)
    gap = size * 0.8

    rect(slide, x, y + size * 0.46, rule_w, 2, fill=ENERGY_D)
    color = ON_DARK_EYEBROW if on_dark else ENERGY_D
    tx = x + rule_w + gap
    simple_text(
        slide, tx, y, CONTENT_W - rule_w - gap, size * 1.4, text.upper(),
        size=size, font=HEADING, bold=True, color=color, tracking=tracking, spacing=1.0,
    )
    return size * 1.4


def badge(slide, x, y, state, text, size=None):
    """Píldora de estado con su punto. Devuelve (ancho, alto)."""
    size = size or cqh(1.7)
    fg, bg, br, dot = BADGE_STATES[state]
    pad_x = cqh(1.4)
    dot_d = cqh(1.1)
    gap = size * 0.7
    h = size * 1.15 + cqh(1.6)
    w = pad_x * 2 + dot_d + gap + text_width(text, size, HEADING, True)

    pill(slide, x, y, w, h, fill=bg, line=br)
    oval(slide, x + pad_x, y + (h - dot_d) / 2, dot_d, dot_d, fill=dot)
    simple_text(
        slide, x + pad_x + dot_d + gap, y, w, h, text,
        anchor="middle", size=size, font=HEADING, bold=True, color=fg, spacing=1.0,
    )
    return w, h


def chip(slide, x, y, text, size=None):
    """Píldora de stack. Devuelve (ancho, alto)."""
    size = size or cqh(1.55)
    pad_x = cqh(1.1)
    h = size * 1.2 + cqh(1.4)
    w = pad_x * 2 + text_width(text, size, MONO)
    pill(slide, x, y, w, h, fill=SURFACE_2, line=LINE)
    simple_text(
        slide, x, y, w, h, text,
        anchor="middle", align="center", size=size, font=MONO, color=INK_2, spacing=1.0,
    )
    return w, h


def chip_row(slide, x, y, items, label="Stack"):
    """Etiqueta + fila de chips. Devuelve el ancho total usado."""
    size = cqh(1.4)
    lw = text_width(label.upper(), size, HEADING, True, tracking=size * 0.2)
    h = cqh(1.55) * 1.2 + cqh(1.4)
    simple_text(
        slide, x, y, lw + 4, h, label.upper(),
        anchor="middle", size=size, font=HEADING, bold=True, color=INK_3,
        tracking=size * 0.2, spacing=1.0,
    )
    cx = x + lw + cqw(0.4) + 4
    for it in items:
        w, _ = chip(slide, cx, y, it)
        cx += w + cqw(1)
    return cx - x


ICON = ASSETS.parent.parent / "assets" / "design-system" / "solvo-genai" / "logos" / "SolvoGenAI_Icon_Color.png"


def foot(slide, text):
    """Marca al pie de los slides de contenido."""
    size = cqh(1.35)
    y = SLIDE_H - cqh(3) - size * 1.4
    d = cqh(2.2)
    picture(slide, ICON, PAD_X, y + (size * 1.4 - d) / 2, d, d)
    simple_text(
        slide, PAD_X + d + cqw(0.8), y, CONTENT_W, size * 1.4, text.upper(),
        anchor="middle", size=size, font=HEADING, color=INK_3, tracking=size * 0.16, spacing=1.0,
    )


def slide_head(slide, eyebrow_text, title, sub=None, on_dark=False):
    """Encabezado estándar de slide de contenido. Devuelve la Y donde sigue el cuerpo."""
    y = PAD_TOP
    y += eyebrow(slide, PAD_X, y, eyebrow_text, on_dark=on_dark) + cqh(1.0)

    t_size = cqh(4.6)
    simple_text(
        slide, PAD_X, y, CONTENT_W, t_size * 1.15, title,
        size=t_size, font=HEADING, bold=True, color=INK, spacing=1.05,
    )
    y += t_size * 1.15

    if sub:
        s_size = cqh(2.1)
        lines = 1 + int(text_width(sub, s_size) // (CONTENT_W * 0.72))
        y += cqh(1.4)
        simple_text(
            slide, PAD_X, y, CONTENT_W * 0.72, s_size * 1.4 * lines, sub,
            size=s_size, color=INK_2, spacing=1.4,
        )
        y += s_size * 1.4 * lines
    return y
