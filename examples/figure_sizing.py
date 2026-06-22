"""Example: Fixed-size figure vs panel-spanning figure."""
from __future__ import annotations
from pathlib import Path
from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.panel import HAlign, VAlign
from reporting.renderers.pdf.renderer import PDFRenderer

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _fig(figsize=(3.2, 1.8)) -> plt.Figure:
    f, ax = plt.subplots(figsize=figsize)
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin")
    ax.plot(x, np.cos(x), label="cos")
    ax.legend(fontsize=8)
    ax.set_title("Trigonometric functions", fontsize=9)
    f.tight_layout(pad=0.3)
    return f


doc = Document(title="Figure Sizing Demo")

# ── Slide 1: natural-size at right-bottom vs panel-spanning ──
s = Slide()
s.title = "Natural size (right, bottom) vs panel-spanning"
s.grid_layout(rows=1, cols=2, gap=8)

s[0, 0].align(HAlign.RIGHT, VAlign.BOTTOM).plot(_fig())
s[0, 1].plot(_fig())

doc.add_slide(s)

# ── Slide 2: 50%-width at top-left vs panel-spanning ──
# Cell width ~357 pt; 50 % = 178.5 pt = 2.48 in
s2 = Slide()
s2.title = "50% width (top, left) vs panel-spanning"
s2.grid_layout(rows=1, cols=2, gap=8)

s2[0, 0].align(HAlign.LEFT, VAlign.TOP).plot(_fig(figsize=(2.48, 1.5)))
s2[0, 1].plot(_fig())

doc.add_slide(s2)

out = Path(__file__).parent / "figure_sizing"
PDFRenderer().render_document(doc, str(out) + ".pdf")
print("OK")
