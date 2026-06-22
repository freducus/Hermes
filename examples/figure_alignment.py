"""Example: Matplotlib figures with different sizes, containers, and alignments."""
from __future__ import annotations
from pathlib import Path
from reporting.document import Document
from reporting.layout import Edges
from reporting.slide import Slide
from reporting.layout.panel import HAlign, VAlign
from reporting.renderers.pdf.renderer import PDFRenderer

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _figure(figsize=(4, 2.5), title: str = "") -> plt.Figure:
    f, ax = plt.subplots(figsize=figsize)
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin")
    ax.plot(x, np.cos(x), label="cos")
    ax.set_title(title or f"{figsize[0]:.1f}×{figsize[1]:.1f} in", fontsize=9)
    ax.legend(fontsize=7)
    f.tight_layout(pad=0.3)
    return f


doc = Document("Figure Alignment Demo")

# ─── Slide 1: natural size × all alignments ───────────────────────────────
s = Slide()
s.title = "Natural figure size — all alignments"
s.grid_layout(rows=3, cols=3, gap=6)
fig = _figure((3.2, 1.8), "3.2×1.8 in")
alignments: list[tuple[HAlign, VAlign]] = [
    (HAlign.LEFT,   VAlign.MIDDLE), (HAlign.CENTER, VAlign.MIDDLE), (HAlign.RIGHT,  VAlign.MIDDLE),
    (HAlign.LEFT,   VAlign.BOTTOM), (HAlign.CENTER, VAlign.BOTTOM), (HAlign.RIGHT,  VAlign.BOTTOM),
    (HAlign.LEFT, VAlign.TOP), (HAlign.CENTER, VAlign.TOP), (HAlign.RIGHT, VAlign.TOP),
]
for idx, (ha, va) in enumerate(alignments):
    r, c = divmod(idx, 3)
    s[r, c].align(ha, va).plot(_figure((1, 1)))
doc.add_slide(s)

# ─── Slide 2: preserve-aspect vs stretch ─────────────────────────────────
s2 = Slide()
s2.title = "preserve_aspect=True  (left)  vs  False (right)"
s2.grid_layout(rows=2, cols=2, gap=20, padding=Edges(left=20, right=20, top=20, bottom=20))
fig_wide = _figure((10.0, 1.8), "10.0×1.8 in")   # wide
fig_tall = _figure((1.8, 10.0), "1.8×10.0 in")   # tall

# STRETCH (default) + preserve_aspect — figure keeps ratio, centered in cell
s2[0, 0].align(HAlign.STRETCH, VAlign.STRETCH).plot(fig_wide, preserve_aspect=True)
# STRETCH (default) + no preserve_aspect — figure stretches to fill cell
s2[0, 1].align(HAlign.STRETCH, VAlign.STRETCH).plot(fig_wide, preserve_aspect=False)
s2[1, 0].align(HAlign.STRETCH, VAlign.STRETCH).plot(fig_tall, preserve_aspect=True)
s2[1, 1].align(HAlign.STRETCH, VAlign.STRETCH).plot(fig_tall, preserve_aspect=False)
doc.add_slide(s2)

# ─── Slide 3: container_width_pct / container_height_pct ─────────────────
s3 = Slide()
s3.title = "Width: 30%/60%/100%  / Height: 40%/70%/100% "
s3.grid_layout(rows=2, cols=3, gap=8, padding=Edges(left=20, right=20, top=20, bottom=20))
fig_pct = _figure((3.2, 2.0), "natural 3.2×2.0")

# row 0: width % variants
s3[0, 0].align(HAlign.LEFT, VAlign.TOP).plot(_figure((4, 2.0)), container_width_pct=30, container_height_pct=100)
s3[0, 1].align(HAlign.CENTER, VAlign.MIDDLE).plot(_figure((4, 2.0)), container_width_pct=60)
s3[0, 2].align(HAlign.RIGHT, VAlign.BOTTOM).plot(_figure((4, 2.0)), container_width_pct=100)

# row 1: height % variants
s3[1, 0].align(HAlign.LEFT, VAlign.TOP).plot(_figure((3.2, 2.0)), container_height_pct=40)
s3[1, 1].align(HAlign.CENTER, VAlign.MIDDLE).plot(_figure((3.2, 2.0)), container_height_pct=70)
s3[1, 2].align(HAlign.RIGHT, VAlign.BOTTOM).plot(_figure((3.2, 2.0)), container_height_pct=100)
doc.add_slide(s3)

# ─── Slide 4: mixed — different sizes + both % and preserve_aspect ───────
s4 = Slide()
s4.title = "Mixed: size variants, % sizing, aspect control"
s4.grid_layout(rows=2, cols=3, gap=8)
s4[0, 0].align(HAlign.LEFT, VAlign.TOP).plot(
    _figure((1.5, 1.5), "1.5×1.5"), preserve_aspect=True,
)
s4[0, 1].align(HAlign.CENTER, VAlign.MIDDLE).plot(
    _figure((4.5, 1.2), "4.5×1.2"), container_width_pct=80, preserve_aspect=True,
)
s4[0, 2].align(HAlign.RIGHT, VAlign.BOTTOM).plot(
    _figure((1.2, 4.5), "1.2×4.5"), container_height_pct=90, preserve_aspect=True,
)
s4[1, 0].align(HAlign.STRETCH, VAlign.STRETCH).plot(
    _figure((2.0, 2.0), "STRETCH"), preserve_aspect=False,
)
s4[1, 1].align(HAlign.LEFT, VAlign.BOTTOM).plot(
    _figure((3.0, 3.0), "3×3 left/bottom"),
)
s4[1, 2].align(HAlign.RIGHT, VAlign.TOP).plot(
    _figure((3.0, 2.0), "3×2 right/top"), container_width_pct=70,
)
doc.add_slide(s4)

out = Path(__file__).parent / "figure_alignment"
PDFRenderer().render_document(doc, str(out) + ".pdf")
print("OK")
