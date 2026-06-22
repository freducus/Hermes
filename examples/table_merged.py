"""Example 3: Merged cells — header spans, multi-row headers, merge API."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, cell
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Merged Cells", author="Engineer")

    slide = Slide()
    slide.title = "Merged & Spanned Cells"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(columns=[
        Column("region", label="Region"),
        Column("q1", label="Q1"),
        Column("q2", label="Q2"),
        Column("q3", label="Q3"),
        Column("q4", label="Q4"),
    ])
    t.row("Region", "Q1", "Q2", "Q3", "Q4")
    t.row(
        cell("North", colspan=5, bold=True, background_color="lightsteelblue"),
    )
    t.row("Jan", 100, 110, 105, 115)
    t.row("Feb", 90, 95, 100, 110)
    t.row(
        cell("South", colspan=5, bold=True, background_color="honeydew"),
    )
    t.row("Jan", 80, 85, 90, 95)
    t.row("Feb", 75, 80, 85, 90)
    t.zebra()

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_merged"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_merged.pdf")


if __name__ == "__main__":
    main()
