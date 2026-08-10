"""
Renderiza un .pptx a PNG para poder verlo sin PowerPoint.

En esta máquina no hay PowerPoint ni LibreOffice, así que maquetar el deck sería
a ciegas. Este renderer lee el .pptx **ya generado** —posiciones, tamaños,
rellenos, corridas de texto— y lo dibuja con Pillow usando los mismos TTF. Es un
viaje de ida y vuelta: verifica lo que quedó en el archivo, no lo que el script
creía estar escribiendo.

No pretende ser fiel a PowerPoint al píxel. Cubre el subconjunto que usan estos
decks —imágenes, rectángulos, rectángulos redondeados, óvalos y cajas de texto—
y sirve para cazar lo que de verdad falla al maquetar: desbordes, solapamientos,
jerarquía rota, contraste insuficiente.

    .venv/bin/python preview.py reviews/sprint-14/sprint-14.pptx out/ [--slide N]
"""

import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

import theme

SCALE = 2  # px por punto
EMU_PT = 12700


def pt(v):
    return (v or 0) / EMU_PT


def px(v):
    return int(round(v * SCALE))


_fcache = {}


def load_font(name, bold, size_pt):
    key = (name, bold, round(size_pt, 2))
    if key not in _fcache:
        path = theme.font_file(name, bold)
        _fcache[key] = ImageFont.truetype(str(path), max(px(size_pt), 1))
    return _fcache[key]


def rgb(color):
    try:
        c = color.rgb
        return (c[0], c[1], c[2])
    except Exception:
        return None


def fill_color(shape):
    try:
        if shape.fill.type is None or shape.fill.type == 5:  # BACKGROUND
            return None
        return rgb(shape.fill.fore_color)
    except Exception:
        return None


def line_color(shape):
    try:
        if shape.line.fill.type is None or shape.line.fill.type == 5:
            return None
        return rgb(shape.line.color)
    except Exception:
        return None


def rounded(d, box, radius, fill, outline, width):
    if radius and radius > 0.5:
        d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    else:
        d.rectangle(box, fill=fill, outline=outline, width=width)


# ───────────────────────────────────────────────────────────────── texto ──


def run_style(run, para_obj):
    f = run.font
    size = pt(f.size.emu) if f.size else 12.0
    name = f.name or theme.BODY
    bold = bool(f.bold)
    color = rgb(f.color) or (17, 24, 39)
    spc = run.font._element.get("spc")
    tracking = (int(spc) / 100) if spc else 0.0
    return dict(size=size, name=name, bold=bold, color=color, tracking=tracking)


def measure(text, st):
    f = load_font(st["name"], st["bold"], st["size"])
    w = f.getlength(text)
    if st["tracking"]:
        w += px(st["tracking"]) * max(len(text) - 1, 0)
    return w


def draw_text_run(d, x, y, text, st):
    f = load_font(st["name"], st["bold"], st["size"])
    if not st["tracking"]:
        d.text((x, y), text, font=f, fill=st["color"])
        return x + f.getlength(text)
    tr = px(st["tracking"])
    for ch in text:
        d.text((x, y), ch, font=f, fill=st["color"])
        x += f.getlength(ch) + tr
    return x


def wrap_paragraph(para_obj, max_w, word_wrap):
    """Parte el párrafo en líneas de (texto, estilo), respetando las corridas."""
    pieces = [(r.text, run_style(r, para_obj)) for r in para_obj.runs if r.text]
    if not pieces:
        return []
    if not word_wrap:
        return [pieces]

    lines, cur, cur_w = [], [], 0.0
    for text, st in pieces:
        # Se parte por palabras conservando los espacios.
        tokens = []
        buf = ""
        for ch in text:
            buf += ch
            if ch == " ":
                tokens.append(buf)
                buf = ""
        if buf:
            tokens.append(buf)

        for tok in tokens:
            w = measure(tok, st)
            if cur and cur_w + w > max_w and tok.strip():
                lines.append(cur)
                cur, cur_w = [], 0.0
            if cur and cur[-1][1] is st:
                cur[-1] = (cur[-1][0] + tok, st)
            else:
                cur.append((tok, st))
            cur_w += w
    if cur:
        lines.append(cur)
    return lines


def draw_textframe(d, shape):
    tf = shape.text_frame
    x0, y0 = pt(shape.left), pt(shape.top)
    w, h = pt(shape.width), pt(shape.height)
    ml, mr = pt(tf.margin_left.emu), pt(tf.margin_right.emu)
    mt, mb = pt(tf.margin_top.emu), pt(tf.margin_bottom.emu)
    inner_x, inner_w = x0 + ml, w - ml - mr

    blocks = []
    total_h = 0.0
    for p in tf.paragraphs:
        lines = wrap_paragraph(p, px(inner_w), tf.word_wrap is not False)
        sizes = [st["size"] for ln in lines for _, st in ln] or [12.0]
        lead = max(sizes)
        ls = p.line_spacing
        line_h = lead * (ls if isinstance(ls, float) else 1.2) if ls else lead * 1.2
        before = pt(p.space_before.emu) if p.space_before else 0
        after = pt(p.space_after.emu) if p.space_after else 0
        blk_h = before + line_h * len(lines) + after
        blocks.append((p, lines, line_h, before, after, lead))
        total_h += blk_h

    anchor = tf.vertical_anchor
    if anchor == MSO_ANCHOR.MIDDLE:
        y = y0 + mt + (h - mt - mb - total_h) / 2
    elif anchor == MSO_ANCHOR.BOTTOM:
        y = y0 + h - mb - total_h
    else:
        y = y0 + mt

    for p, lines, line_h, before, after, lead in blocks:
        y += before
        for ln in lines:
            lw = sum(measure(t, s) for t, s in ln)
            if p.alignment == PP_ALIGN.CENTER:
                lx = px(inner_x) + (px(inner_w) - lw) / 2
            elif p.alignment == PP_ALIGN.RIGHT:
                lx = px(inner_x) + px(inner_w) - lw
            else:
                lx = px(inner_x)
            # Pillow ancla el texto arriba; se centra la caja de línea sobre el leading.
            ty = px(y) + (px(line_h) - px(lead) * 1.0) / 2
            for t, s in ln:
                lx = draw_text_run(d, lx, ty, t, s)
            y += line_h
        y += after


# ───────────────────────────────────────────────────────────────── shapes ──


def draw_shape(img, d, shape):
    st = shape.shape_type
    x, y = pt(shape.left), pt(shape.top)
    w, h = pt(shape.width), pt(shape.height)
    box = [px(x), px(y), px(x + w), px(y + h)]

    if st == MSO_SHAPE_TYPE.PICTURE:
        im = Image.open(io.BytesIO(shape.image.blob)).convert("RGBA")
        im = im.resize((max(box[2] - box[0], 1), max(box[3] - box[1], 1)), Image.LANCZOS)
        img.paste(im, (box[0], box[1]), im)
        return

    if shape.has_text_frame or st == MSO_SHAPE_TYPE.AUTO_SHAPE:
        f = fill_color(shape)
        lc = line_color(shape)
        lw = max(px(pt(shape.line.width.emu)) if shape.line.width else 1, 1) if lc else 0
        name = ""
        try:
            name = shape._element.find(".//{*}prstGeom").get("prst") or ""
        except Exception:
            pass

        if f or lc:
            if name == "ellipse":
                d.ellipse(box, fill=f, outline=lc, width=lw)
            elif name == "roundRect":
                adj = 0.16
                try:
                    adj = shape.adjustments[0]
                except Exception:
                    pass
                rounded(d, box, adj * min(px(w), px(h)), f, lc, lw)
            elif name == "rightArrow":
                x0, y0, x1, y1 = box
                mid, half = (y0 + y1) / 2, (y1 - y0) * 0.25
                neck = x0 + (x1 - x0) * 0.45
                d.polygon(
                    [(x0, mid - half), (neck, mid - half), (neck, y0),
                     (x1, mid), (neck, y1), (neck, mid + half), (x0, mid + half)],
                    fill=f, outline=lc,
                )
            else:
                d.rectangle(box, fill=f, outline=lc, width=lw)

    if shape.has_text_frame and shape.text_frame.text.strip():
        draw_textframe(d, shape)


def render(pptx_path, out_dir, only=None):
    prs = Presentation(str(pptx_path))
    W = px(pt(prs.slide_width.emu))
    H = px(pt(prs.slide_height.emu))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for i, slide in enumerate(prs.slides, 1):
        if only and i not in only:
            continue
        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)
        for shape in slide.shapes:
            try:
                draw_shape(img, d, shape)
            except Exception as e:  # una forma rota no debe tumbar el preview
                print(f"  slide {i}: {shape.shape_type} → {e}")
        p = out_dir / f"slide-{i:02d}.png"
        img.save(p)
        written.append(p)
    print(f"{len(written)} slides → {out_dir}/")
    return written


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = None
    if "--slide" in sys.argv:
        only = {int(sys.argv[sys.argv.index("--slide") + 1])}
    render(args[0], args[1] if len(args) > 1 else "out", only)
