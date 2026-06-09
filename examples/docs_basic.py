"""Basic document — used by docs 01_basic_example.rst."""

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.footer_config import FooterConfig
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer


def main() -> None:
    doc = Document("My Report", author="Engineer")

    slide = Slide(
        "Introduction",
        subtitle="Getting started",
        footer_config=FooterConfig(center_text="My Report | Engineering"),
    )
    slide.grid_layout(rows=2, cols=2, gap=10, padding=Edges.all(20))

    slide[0, 0].text("Hello, world!", bold=True, size=14, color="#1F4E79")
    slide[0, 1].text("Second cell", size=11, color="#333333", alignment="center")
    slide[1, :].text("This spans both columns", italic=True, size=10, alignment="center")

    doc.add_slide(slide)

    out = Path(__file__).parent / "docs_basic"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_basic.pdf and docs_basic.html")


if __name__ == "__main__":
    main()
