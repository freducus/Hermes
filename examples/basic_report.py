"""Basic report example — generates a PDF."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Basic Report", author="Engineer")

    slide = Slide("Executive Summary")
    slide.grid_layout(rows=2, cols=2, gap=10)
    slide[0, 0].text("Key metrics and findings.")
    slide[0, 1].text("Recommendations: proceed with optimization.")
    slide[1, :].text("Detailed analysis in subsequent sections.")
    doc.add_slide(slide)

    slide2 = Slide("Results")
    slide2.grid_layout(rows=1, cols=1)
    slide2[0, 0].text("Detailed results go here.")
    doc.add_slide(slide2)

    renderer = PDFRenderer()
    doc.render(renderer, str(Path(__file__).parent / "basic_report.pdf"))
    print("Generated basic_report.pdf")


if __name__ == "__main__":
    main()
