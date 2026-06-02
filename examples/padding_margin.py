"""Padding & Margin visual demonstration — generates PDF, HTML, PPTX with 4 slides
showing how grid.padding, grid.gap, panel.padding, and panel.margin affect layout."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer


def make_slide(title: str, subtitle: str = "") -> Slide:
    s = Slide(title, subtitle=subtitle)
    return s


def slide_grid_padding() -> Slide:
    """Slide 1: Compare grid.padding = 5 vs 30."""
    s = make_slide("Grid padding", "Edges.all(5) — left  |  Edges.all(30) — right")
    s.grid_layout(rows=1, cols=2, gap=0, padding=Edges.all(5))
    s[0, 0].text("padding=5", size=10)
    s[0, 0]._cell.panel.background_color = "#E3F2FD"

    s2 = Slide("", width=s.width, height=s.height, title_panel_height=s.title_panel_height)
    s2.grid_layout(rows=1, cols=2, gap=0, padding=Edges.all(30))
    s2[0, 0].text("padding=30", size=10)
    s2[0, 0]._cell.panel.background_color = "#FFF3E0"

    # Combine manually — we use two cells side-by-side in one slide instead
    s3 = make_slide("Grid padding comparison")
    s3.grid_layout(rows=1, cols=2, gap=10, padding=Edges.all(15))

    s3._set_cell_element(s3._grid[0, 0], s._grid.cells[0][0].element)
    s3._grid.cells[0][0].panel = s._grid.cells[0][0].panel
    s3._grid.cells[0][0].panel.background_color = "#E3F2FD"
    s3[0, 0].text("padding=5", size=10)
    s3._grid.cells[0][0].panel.padding = Edges.all(5)

    # Replace, simpler approach: just draw both on separate slides
    return s


def main() -> None:
    doc = Document(title="Padding & Margin Demo", author="pyreportengine")

    # ---- Slide 1: grid.padding comparison ----
    slide = Slide("Grid padding")
    slide.grid_layout(rows=1, cols=2, gap=8, padding=Edges.all(15))
    slide[0, 0].text("padding=Edges.all(5)")
    slide[0, 0]._cell.panel.background_color = "#E3F2FD"
    slide[0, 0]._cell.panel.padding = Edges.all(5)

    # Actually put the text back and set padding on the panel
    slide[0, 1].text("padding=Edges.all(30)")
    slide[0, 1]._cell.panel.background_color = "#FFF3E0"
    slide[0, 1]._cell.panel.padding = Edges.all(30)
    doc.add_slide(slide)

    # ---- Slide 2: grid.gap comparison ----
    slide = Slide("Grid gap", subtitle="gap=2  |  gap=20")
    slide.grid_layout(rows=2, cols=2, gap=2, padding=Edges.all(15))
    slide[0, 0].text("A", size=12, alignment="center")
    slide[0, 0]._cell.panel.background_color = "#C8E6C9"
    slide[0, 1].text("B", size=12, alignment="center")
    slide[0, 1]._cell.panel.background_color = "#C8E6C9"
    slide[1, 0].text("C", size=12, alignment="center")
    slide[1, 0]._cell.panel.background_color = "#C8E6C9"
    slide[1, 1].text("D", size=12, alignment="center")
    slide[1, 1]._cell.panel.background_color = "#C8E6C9"
    doc.add_slide(slide)

    slide = Slide("Grid gap (wide)", subtitle="gap=20  |  padding=Edges.all(5)")
    slide.grid_layout(rows=2, cols=2, gap=20, padding=Edges.all(5))
    slide[0, 0].text("A", size=12, alignment="center")
    slide[0, 0]._cell.panel.background_color = "#FFE0B2"
    slide[0, 1].text("B", size=12, alignment="center")
    slide[0, 1]._cell.panel.background_color = "#FFE0B2"
    slide[1, 0].text("C", size=12, alignment="center")
    slide[1, 0]._cell.panel.background_color = "#FFE0B2"
    slide[1, 1].text("D", size=12, alignment="center")
    slide[1, 1]._cell.panel.background_color = "#FFE0B2"
    doc.add_slide(slide)

    # ---- Slide 3: panel.padding ----
    slide = Slide("Panel padding", subtitle="padding=0 (left)  |  padding=20 (right)")
    slide.grid_layout(rows=1, cols=2, gap=10, padding=Edges.all(15))
    slide[0, 0].text("No padding\nContent touches\ncell edge")
    slide[0, 0]._cell.panel.background_color = "#F3E5F5"
    slide[0, 0]._cell.panel.padding = Edges()

    slide[0, 1].text("padding=20\nContent is inset\nfrom cell edge")
    slide[0, 1]._cell.panel.background_color = "#F3E5F5"
    slide[0, 1]._cell.panel.padding = Edges.all(20)
    doc.add_slide(slide)

    # ---- Slide 4: panel.margin ----
    slide = Slide("Panel margin", subtitle="Each labelled cell has margin=15 around it")
    slide.grid_layout(rows=2, cols=3, gap=0, padding=Edges.all(10))
    labels = ["A", "B", "C", "D", "E", "F"]
    colors = ["#E3F2FD", "#FFF3E0", "#E8F5E9", "#F3E5F5", "#FFEBEE", "#E0F7FA"]
    for i in range(2):
        for j in range(3):
            idx = i * 3 + j
            slide[i, j].text(labels[idx], size=12, alignment="center")
            slide[i, j]._cell.panel.background_color = colors[idx]
            slide[i, j]._cell.panel.margin = Edges.all(8)
    doc.add_slide(slide)

    # ---- Slide 5: Combined overview ----
    slide = Slide("Combined: padding + margin + gap")
    slide.grid_layout(rows=2, cols=2, gap=12, padding=Edges.all(20))

    slide[0, 0].text("padding=10\nmargin=5")
    slide[0, 0]._cell.panel.background_color = "#E3F2FD"
    slide[0, 0]._cell.panel.padding = Edges.all(10)
    slide[0, 0]._cell.panel.margin = Edges.all(5)

    slide[0, 1].text("padding=20\nmargin=2")
    slide[0, 1]._cell.panel.background_color = "#FFF3E0"
    slide[0, 1]._cell.panel.padding = Edges.all(20)
    slide[0, 1]._cell.panel.margin = Edges.all(2)

    slide[1, 0].text("padding=5\nmargin=10")
    slide[1, 0]._cell.panel.background_color = "#E8F5E9"
    slide[1, 0]._cell.panel.padding = Edges.all(5)
    slide[1, 0]._cell.panel.margin = Edges.all(10)

    slide[1, 1].text("padding=15\nmargin=8")
    slide[1, 1]._cell.panel.background_color = "#F3E5F5"
    slide[1, 1]._cell.panel.padding = Edges.all(15)
    slide[1, 1]._cell.panel.margin = Edges.all(8)
    doc.add_slide(slide)

    out = Path(__file__).parent / "padding_margin"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated padding_margin.{pdf,html}")


if __name__ == "__main__":
    main()
