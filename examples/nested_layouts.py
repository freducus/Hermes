"""Nested layout example — demonstrates ContainerElement with nested grids, generates PDF, HTML, PPTX."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.elements.container import ContainerElement
from reporting.layout.grid import Grid
from reporting.layout.sizing import Fill
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer
from reporting.renderers.pptx.renderer import PPTXRenderer


def main() -> None:
    doc = Document(title="Nested Layouts")

    slide = Slide("Dashboard Overview")
    slide.grid_layout(rows=1, cols=2, gap=10)

    inner = Grid(rows=2, cols=1, row_sizes=[Fill, Fill], gap=5)
    inner[0, 0].panel.background_color = "#E8F0FE"
    inner[1, 0].panel.background_color = "#E8F0FE"
    container = ContainerElement(grid=inner)
    slide._set_cell_element(slide._grid[0, 0], container)

    slide[0, 1].text("Side panel content")

    doc.add_slide(slide)

    out = Path(__file__).parent / "nested_layouts"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    PPTXRenderer().render_document(doc, str(out) + ".pptx")
    print("Generated nested_layouts.{pdf,html,pptx}")


if __name__ == "__main__":
    main()
