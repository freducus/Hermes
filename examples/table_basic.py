"""Example 1: Basic table — columns, rows, auto-text from format strings."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Basic Tables", author="Engineer")

    slide = Slide()
    slide.title = "Basic Table"
    slide.grid_layout(rows=1, cols=1)
    t = TableSpec(columns=[
        Column("name", label="Component"),
        Column("stress", label="Max Stress (MPa)", format="{:.1f}"),
        Column("status", label="Status"),
    ])
    t.row("Component", "Max Stress (MPa)", "Status")
    t.row("Beam A", 245.3, "OK")
    t.row("Beam B", 389.1, "WARN")
    t.row("Beam C", 152.0, "OK")
    t.zebra()
    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_basic"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_basic.pdf")


if __name__ == "__main__":
    main()
