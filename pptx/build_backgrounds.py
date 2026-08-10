"""
Genera los fondos de marca de los slides oscuros (portada, divisores, cierre).

Los slides `.slide--cover`, `.slide--section` y `.slide--end` superponen un
gradiente lineal de 135° con dos halos radiales en `mix-blend-mode: screen`.
PowerPoint no tiene un relleno que reproduzca eso, así que se hornea a PNG una
sola vez y el texto va encima, real y seleccionable.

La matemática replica el CSS de `engine/deck.css` (§ COVER), no lo aproxima:

    --grad-sign: linear-gradient(135deg, #2E206D 0%, #775AE5 52%, #3869E0 100%)

    .slide--cover::after {
      background:
        radial-gradient(60% 60% at 82% 18%, rgba(241,149,86,.30) 0%, rgba(241,149,86,0) 60%),
        radial-gradient(70% 70% at  8% 96%, rgba(120,159,255,.28) 0%, rgba(120,159,255,0) 60%);
      mix-blend-mode: screen;
    }

Se corre una vez; el PNG queda versionado en assets/.

    .venv/bin/python build_backgrounds.py
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).parent / "assets" / "bg-signature.png"
W, H = 1920, 1080


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)])


def linear_gradient(w, h, angle_deg, stops):
    """Gradiente lineal con la semántica de CSS: 0° apunta arriba, 90° a la derecha."""
    a = math.radians(angle_deg)
    dx, dy = math.sin(a), -math.cos(a)
    # Longitud de la línea de gradiente según la spec de CSS.
    length = abs(w * math.sin(a)) + abs(h * math.cos(a))

    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    t = ((xs - w / 2) * dx + (ys - h / 2) * dy) / length + 0.5
    t = np.clip(t, 0, 1)

    out = np.zeros((h, w, 3))
    positions = [p for p, _ in stops]
    colors = [hex_rgb(c) for _, c in stops]
    for i in range(len(stops) - 1):
        p0, p1 = positions[i], positions[i + 1]
        seg = (t >= p0) & (t <= p1)
        local = np.zeros_like(t)
        local[seg] = (t[seg] - p0) / (p1 - p0)
        for ch in range(3):
            out[..., ch] = np.where(
                seg, colors[i][ch] + (colors[i + 1][ch] - colors[i][ch]) * local, out[..., ch]
            )
    out[t <= positions[0]] = colors[0]
    out[t >= positions[-1]] = colors[-1]
    return out


def radial_halo(w, h, cx, cy, rx, ry, rgb, alpha0, fade_to):
    """Elipse `rx ry at cx cy` que va de `alpha0` en el centro a 0 en `fade_to`."""
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    d = np.sqrt(((xs - cx * w) / (rx * w)) ** 2 + ((ys - cy * h) / (ry * h)) ** 2)
    a = np.clip(alpha0 * (1 - d / fade_to), 0, alpha0)
    color = np.broadcast_to(hex_rgb(rgb), (h, w, 3))
    return color, a


def main():
    base = linear_gradient(W, H, 135, [(0.0, "#2E206D"), (0.52, "#775AE5"), (1.0, "#3869E0")])

    # Los dos halos del ::after, apilados con source-over (el primero arriba).
    c1, a1 = radial_halo(W, H, 0.82, 0.18, 0.60, 0.60, "#F19556", 0.30, 0.60)
    c2, a2 = radial_halo(W, H, 0.08, 0.96, 0.70, 0.70, "#789FFF", 0.28, 0.60)

    a = a1 + a2 * (1 - a1)
    safe = np.where(a > 0, a, 1)[..., None]
    c = (c1 * a1[..., None] + c2 * (a2 * (1 - a1))[..., None]) / safe

    # mix-blend-mode: screen, respetando el alfa de la capa que se mezcla.
    screen = base + c - base * c
    out = base * (1 - a[..., None]) + screen * a[..., None]

    img = Image.fromarray((np.clip(out, 0, 1) * 255).round().astype(np.uint8), "RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"{OUT.name}  {img.size[0]}×{img.size[1]}  {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
