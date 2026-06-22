"""Example 2: Styled table — CellStyle, RowStyle, ColumnStyle, TableStyle."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, cell
from reporting.tablespec.style import CellStyle, ColumnStyle, RowStyle, TableStyle
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Styled Tables", author="Engineer")

    slide = Slide()
    slide.title = "Styled Table"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(
        columns=[
            Column("item", label="Item", style=ColumnStyle(align_h="left")),
            Column("qty", label="Qty", format="{:.0f}", style=ColumnStyle(align_h="center")),
            Column("price", label="Price", format="${:.2f}", style=ColumnStyle(align_h="right")),
        ],
        style=TableStyle(
            font_name="Helvetica",
            font_size=10.0,
            padding=6,
            header_background="steelblue",
            header_text_color="white",
        ),
    )
    t.row("Item", "Qty", "Price")
    t.row("Widget A", 12, 3.50)
    t.row("Widget B", 5, 12.00)
    t.row("Total", 17, 15.50)
    t.rows[2].cells[0].style = CellStyle(bold=True)
    t.rows[2].cells[2].style = CellStyle(bold=True)

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_styled"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_styled.pdf")


if __name__ == "__main__":
    main()
