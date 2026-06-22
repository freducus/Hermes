"""Named Colors Swatch — one slide, all 147 CSS named colors."""
from __future__ import annotations

import math
from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.styles.colors import NAMED_COLORS, Color
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer

OUT = Path(__file__).parent


def _luminance(r: int, g: int, b: int) -> float:
    return 0.299 * r + 0.587 * g + 0.114 * b


def main() -> None:
    colors = list(NAMED_COLORS.items())  # (name, hex) pairs
    n = len(colors)

    cols = 13
    rows = math.ceil(n / cols)

    slide = Slide()
    slide.title = f"All {n} Named Colors"
    slide.subtitle = f"CSS named colors in a {cols}×{rows} grid — each cell shows the color name parsed via Color.parse()"
    slide.grid_layout(rows=rows, cols=cols, gap=1, padding=Edges.all(10))

    for i, (name, hex_str) in enumerate(colors):
        r_idx = i // cols
        c_idx = i % cols
        cell = slide[r_idx, c_idx]
        cell.background_color = name

        c = Color.parse(hex_str)
        lum = _luminance(c.r, c.g, c.b)
        text_color = "white" if lum <= 128 else "black"
        cell._cell.element = None
        cell.text(name, size=6, color=text_color, alignment="center")

    doc = Document(title="Named Colors Reference")
    doc.add_slide(slide)

    out = OUT / "named_colors"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print(f"Generated named_colors.pdf — {n} colors in {cols}×{rows}")


if __name__ == "__main__":
    main()
