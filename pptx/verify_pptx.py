"""
Chequeo estructural de un .pptx generado.

No reemplaza mirarlo: garantiza que el archivo no está roto, no que se ve bien.
Lo que sí caza —y es lo que más duele en un entregable— es el texto que se sale
de su caja, la forma que se escapa del slide, la fuente que se coló fuera de la
paleta y la imagen enlazada en vez de embebida.

    .venv/bin/python verify_pptx.py ../reviews/sprint-14/sprint-14.pptx
"""

import sys
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

import theme as T

EMU_PT = 12700
ALLOWED_FONTS = {T.HEADING, T.BODY, T.MONO}
TOLERANCE = 1.06  # 6 % de holgura: PowerPoint corta un pelo distinto que las métricas


def pt(v):
    return (v or 0) / EMU_PT


def text_overflows(shape):
    """Alto estimado del texto contra el alto de la caja."""
    tf = shape.text_frame
    w = pt(shape.width) - pt(tf.margin_left.emu) - pt(tf.margin_right.emu)
    h = pt(shape.height) - pt(tf.margin_top.emu) - pt(tf.margin_bottom.emu)
    if w <= 0:
        return None
    total = 0.0
    for p in tf.paragraphs:
        runs = [r for r in p.runs if r.text]
        if not runs:
            continue
        size = max(pt(r.font.size.emu) if r.font.size else 12 for r in runs)
        name = runs[0].font.name or T.BODY
        bold = bool(runs[0].font.bold)
        text = "".join(r.text for r in runs)
        ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.2
        total += T.wrap_count(text, w, size, name, bold) * size * (ls or 1.2)
        total += pt(p.space_before.emu if p.space_before else 0)
        total += pt(p.space_after.emu if p.space_after else 0)
    return (total, h) if total > h * TOLERANCE else None


def main(path):
    prs = Presentation(str(path))
    W, H = pt(prs.slide_width.emu), pt(prs.slide_height.emu)
    problems, stats = [], {"slides": 0, "pictures": 0, "textboxes": 0, "shapes": 0}

    if (round(W), round(H)) != (960, 540):
        problems.append(f"tamaño de slide {W:.0f}×{H:.0f} pt — se esperaba 960×540 (16:9 widescreen)")

    fonts, linked = set(), 0
    for i, slide in enumerate(prs.slides, 1):
        stats["slides"] += 1
        for shape in slide.shapes:
            stats["shapes"] += 1
            x, y = pt(shape.left), pt(shape.top)
            w, h = pt(shape.width), pt(shape.height)
            if x < -1 or y < -1 or x + w > W + 1 or y + h > H + 1:
                problems.append(f"slide {i}: forma fuera del slide ({x:.0f},{y:.0f} {w:.0f}×{h:.0f})")

            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                stats["pictures"] += 1
                if shape.image.blob is None:
                    linked += 1

            if shape.has_text_frame and shape.text_frame.text.strip():
                stats["textboxes"] += 1
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        if r.font.name:
                            fonts.add(r.font.name)
                over = text_overflows(shape)
                if over:
                    txt = shape.text_frame.text.replace("\n", " ")[:52]
                    problems.append(
                        f"slide {i}: texto se sale de su caja "
                        f"({over[0]:.0f} pt en {over[1]:.0f} pt) — “{txt}…”"
                    )

    if linked:
        problems.append(f"{linked} imagen(es) enlazadas en vez de embebidas")
    rogue = fonts - ALLOWED_FONTS
    if rogue:
        problems.append(f"fuentes fuera del kit: {', '.join(sorted(rogue))}")

    print(f"{Path(path).name}")
    print(f"  {stats['slides']} slides · {stats['shapes']} formas · "
          f"{stats['pictures']} imágenes · {stats['textboxes']} cajas de texto")
    print(f"  fuentes: {', '.join(sorted(fonts))}")
    if problems:
        print(f"\n  {len(problems)} problema(s):")
        for p in problems:
            print(f"    · {p}")
    else:
        print("\n  sin problemas estructurales")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "../reviews/sprint-14/sprint-14.pptx"))
