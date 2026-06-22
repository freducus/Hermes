"""Nested layout example — demonstrates ContainerElement with nested grids, generates PDF, HTML, PPTX."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.grid import Grid
from reporting.layout.sizing import Fill
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Nested Layouts")

    slide = Slide()
    slide.title = "Dashboard Overview"
    slide.grid_layout(rows=1, cols=2, gap=10)

    inner = Grid(rows=2, cols=1, row_sizes=[Fill, Fill], gap=5)
    inner[0, 0].background_color = "aliceblue"
    inner[0, 0].text("Top panel content", size=12)
    inner[1, 0].background_color = "aliceblue"
    inner[1, 0].text("Bottom panel content", size=12)
    slide[0, 0].grid_layout(inner)

    slide[0, 1].text("Side panel content")

    doc.add_slide(slide)

    out = Path(__file__).parent / "nested_layouts"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated nested_layouts.pdf")


if __name__ == "__main__":
    main()
