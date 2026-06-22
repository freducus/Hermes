"""Example: Element alignment with tables, text, and figures."""
from __future__ import annotations
from pathlib import Path
from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, TableSizing, TableFitMode
from reporting.tablespec.style import TableStyle
from reporting.layout.panel import HAlign, VAlign
from reporting.renderers.pdf.renderer import PDFRenderer

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def fig() -> plt.Figure:
    f, ax = plt.subplots(figsize=(2.8, 1.6))
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x))
    ax.set_title("sin(x)", fontsize=9)
    f.tight_layout(pad=0.3)
    return f


doc = Document(title="Alignment Demo")

# ── 1. PERCENT table, 9 positions — HAlign + VAlign both visible ──
s1 = Slide()
s1.title = "PERCENT tables — HAlign + VAlign both visible"
s1.grid_layout(rows=3, cols=3)
tiny = TableSpec(
    columns=[Column("x", "X"), Column("y", "Y")],
    style=TableStyle(font_size=9, padding=3),
    sizing=TableSizing(fit_mode=TableFitMode.PERCENT, percent_width=0.28),
)
tiny.row("a", 1).row("b", 2)

for c, v in enumerate([VAlign.TOP, VAlign.MIDDLE, VAlign.BOTTOM]):
    for r, h in enumerate([HAlign.LEFT, HAlign.CENTER, HAlign.RIGHT]):
        s1[r, c].align(h, v).table(tiny)
doc.add_slide(s1)

# ── 2. Text alignment ──
s2 = Slide()
s2.title = "Text alignment"
s2.grid_layout(rows=2, cols=2)
s2[0, 0].align(HAlign.LEFT, VAlign.TOP).text("Left/Top", size=14)
s2[0, 1].align(HAlign.CENTER, VAlign.MIDDLE).text("Center/Middle", size=14)
s2[1, 0].align(HAlign.RIGHT, VAlign.BOTTOM).text("Right/Bottom", size=14)
s2[1, 1].align(HAlign.CENTER, VAlign.TOP).text("Center/Top", size=14)
doc.add_slide(s2)

# ── 3. Figure positions ──
s3 = Slide()
s3.title = "Figure positions"
s3.grid_layout(rows=1, cols=3)
s3[0, 0].align(HAlign.LEFT, VAlign.TOP).plot(fig())
s3[0, 1].align(HAlign.CENTER, VAlign.MIDDLE).plot(fig())
s3[0, 2].align(HAlign.RIGHT, VAlign.BOTTOM).plot(fig())
doc.add_slide(s3)

# ── 4. Table + Figure side by side ──
s4 = Slide()
s4.title = "Table + Figure"
s4.grid_layout(rows=1, cols=2)
perf = TableSpec(
    columns=[Column("c", "Case"), Column("t", "Temp", format="{:.0f}")],
    style=TableStyle(font_size=10),
)
perf.row("Cruise", 22).row("Climb", 45)
s4[0, 0].align(HAlign.CENTER, VAlign.MIDDLE).table(perf)
s4[0, 1].align(HAlign.CENTER, VAlign.MIDDLE).plot(fig())
doc.add_slide(s4)

out = Path(__file__).parent / "alignment_demo"
PDFRenderer().render_document(doc, str(out) + ".pdf")
print("OK")
