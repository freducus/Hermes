"""9-column table with a merged row (colspan=3 + colspan=2) in a 6-col grid."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, cell
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Merged Row with Colspan", author="Engineer")

    slide = Slide()
    slide.title = "Colspan Example"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(columns=[
        Column("col_a", label="A"),
        Column("col_b", label="B"),
        Column("col_c", label="C"),
        Column("col_d", label="D"),
        Column("col_e", label="E"),
        Column("col_f", label="F"),
    ])

    # Header row — merged across all 6 columns
    t.row(cell("Full-Width Header", colspan=6, bold=True,
               background_color="steelblue", text_color="white"))

    # Row with two cells: first spans 3 cols, second spans 2 cols
    # Total = 3 + 2 = 5, leaving the 6th position empty
    t.row(
        cell("Group A (3 cols)", colspan=3, background_color="lightsteelblue"),
        cell("Group B (2 cols)", colspan=2, background_color="honeydew"),
    )

    # Normal data rows
    t.row("A1", "B1", "C1", "D1", "E1", "F1")
    t.row("A2", "B2", "C2", "D2", "E2", "F2")
    t.row("A3", "B3", "C3", "D3", "E3", "F3")
    t.row("A4", "B4", "C4", "D4", "E4", "F4")

    t.zebra()

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_colspan"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_colspan.pdf")


if __name__ == "__main__":
    main()
