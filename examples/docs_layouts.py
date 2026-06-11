"""Layout: grid sizing, panel padding/margin, alignment — used by docs 03_layouts.rst."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from reporting.document import Document
from reporting.slide import Slide
from reporting.footer_config import FooterPanel
from reporting.layout.geometry import Edges
from reporting.layout.panel import HAlign, VAlign
from reporting.layout.sizing import Fill, Px, Percent
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer


def _fig(title: str, color: str = "C0") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(3, 1.8))
    x = np.linspace(0, 10, 60)
    ax.plot(x, np.sin(x) * np.exp(-x / 5), color=color, linewidth=1.5)
    ax.set_title(title, fontsize=8)
    ax.tick_params(labelsize=6)
    fig.tight_layout(pad=1.0)
    return fig


def main() -> None:
    doc = Document("Layout Demo", author="Docs")

    # ---- Slide 1: Row/Col sizing ----
    slide = Slide(
        "Row & Column Sizing",
        subtitle="Fill, Px, and Percent",
        footer_panel=FooterPanel(center_text="Layout Demo | Docs"),
    )
    slide.grid_layout(
        rows=3, cols=3,
        row_sizes=[Px(60), Fill, Percent(30)],
        col_sizes=[Percent(25), Fill, Px(120)],
        gap=8, padding=Edges.all(20),
    )

    slide[0, 0].text("Px(60) row\nPercent(25) col", size=8)
    slide[0, 1].text("Fill col", size=8)
    slide[0, 2].text("Px(120) col", size=8)

    slide[1, 0].text("Fill row", size=8)
    slide[1, 1].text("Cell [1,1]\nFill/Fill", size=10, bold=True)
    slide[1, 2].text("Fill / Px", size=8)

    slide[2, 0].background_color = "#E3F2FD"
    slide[2, 0].text("Percent(30) row\nPercent(25) col", size=8)
    slide[2, 1].background_color = "#FFF3E0"
    slide[2, 1].text("Percent / Fill", size=8)
    slide[2, 2].background_color = "#E8F5E9"
    slide[2, 2].text("Percent / Px", size=8)

    doc.add_slide(slide)

    # ---- Slide 2: Panel padding, margin, alignment ----
    slide2 = Slide(
        "Panel: Padding & Alignment",
        subtitle="Edges, HAlign, VAlign",
        footer_panel=FooterPanel(center_text="Layout Demo | Docs"),
    )
    slide2.grid_layout(rows=2, cols=2, gap=10, padding=Edges.all(20))

    cell = slide2[0, 0]
    cell.background_color = "#E3F2FD"
    cell.align(HAlign.LEFT, VAlign.TOP)
    cell.text("HAlign.LEFT\nVAlign.TOP\npadding=Edges.all(10)", size=8)
    cell.padding = Edges.all(10)

    cell = slide2[0, 1]
    cell.background_color = "#FFF3E0"
    cell.align(HAlign.CENTER, VAlign.MIDDLE)
    cell.text("HAlign.CENTER\nVAlign.MIDDLE\npadding=Edges.all(15)", size=8)
    cell.padding = Edges.all(15)

    cell = slide2[1, 0]
    cell.background_color = "#E8F5E9"
    cell.align(HAlign.RIGHT, VAlign.BOTTOM)
    cell.text("HAlign.RIGHT\nVAlign.BOTTOM", size=8)
    cell.padding = Edges(left=5, right=5, top=5, bottom=5)

    cell = slide2[1, 1]
    cell.background_color = "#FCE4EC"
    cell.align(HAlign.STRETCH, VAlign.STRETCH)
    cell.text("HAlign.STRETCH\nVAlign.STRETCH\n(fills cell)", size=8)

    doc.add_slide(slide2)

    # ---- Slide 3: Figures in layout ----
    slide3 = Slide(
        "Figures in Layout",
        subtitle="Figures respect panel padding & alignment",
        footer_panel=FooterPanel(center_text="Layout Demo | Docs"),
    )
    slide3.grid_layout(rows=2, cols=2, gap=10, padding=Edges.all(20))

    cell = slide3[0, 0]
    cell.background_color = "#F3E5F5"
    cell.align(HAlign.LEFT, VAlign.TOP)
    cell.plot(_fig("LEFT / TOP", "C4"))
    cell.padding = Edges.all(8)

    cell = slide3[0, 1]
    cell.background_color = "#E8EAF6"
    cell.align(HAlign.CENTER, VAlign.MIDDLE)
    cell.plot(_fig("CENTER / MIDDLE", "C5"))
    cell.padding = Edges.all(8)

    cell = slide3[1, 0]
    cell.background_color = "#FFF8E1"
    cell.align(HAlign.RIGHT, VAlign.BOTTOM)
    cell.plot(_fig("RIGHT / BOTTOM", "C6"))
    cell.padding = Edges.all(8)

    cell = slide3[1, 1]
    cell.background_color = "#E0F2F1"
    cell.align(HAlign.STRETCH, VAlign.STRETCH)
    cell.plot(_fig("STRETCH (default)", "C7"))
    cell.padding = Edges.all(8)

    doc.add_slide(slide3)

    out = Path(__file__).parent / "docs_layouts"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_layouts.pdf and docs_layouts.html")


if __name__ == "__main__":
    main()


