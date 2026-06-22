"""Example 5: Excel-style range API — A1 notation, merge(), style(), range()."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Excel-Style API", author="Engineer")

    slide = Slide()
    slide.title = "Excel-Style Range API"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(columns=[
        Column("a", label="A"),
        Column("b", label="B"),
        Column("c", label="C"),
        Column("d", label="D"),
    ])
    t.row("Header", "", "", "")
    t["A1"] = "Merged Header"
    t.merge("A1:D1")
    t.apply_style("A1:D1", bold=True, background_color="steelblue", text_color="white")
    t.row(1, 2, 3, 4)
    t.row(5, 6, 7, 8)
    t.row(9, 10, 11, 12)
    t.apply_style("A2:C3", background_color="honeydew")

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_excel_api"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_excel_api.pdf")


if __name__ == "__main__":
    main()
