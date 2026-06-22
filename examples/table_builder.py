"""Example 8: Builder pattern — chained construction with TableBuilder."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import TableBuilder
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Builder Pattern", author="Engineer")

    slide = Slide()
    slide.title = "Builder Pattern"
    slide.grid_layout(rows=1, cols=1)

    t = (
        TableBuilder()
        .column("name", label="Student")
        .column("score", label="Score")
        .column("grade", label="Grade")
        .row("Student", "Score", "Grade")
        .row("Alice", 95.5, "A")
        .row("Bob", 82.0, "B")
        .row("Charlie", 67.3, "C")
        .row("Diana", 91.2, "A-")
        .zebra()
        .highlight_max("score")
        .highlight_min("score")
        .build()
    )

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_builder"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_builder.pdf")


if __name__ == "__main__":
    main()
