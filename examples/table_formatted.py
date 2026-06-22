"""Example 7: Format strings and custom formatters — %, $, precision, lambdas."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Formatted Tables", author="Engineer")

    slide = Slide()
    slide.title = "Format Strings & Custom Formatters"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(columns=[
        Column("item", label="Item"),
        Column("revenue", label="Revenue", format="${:,.2f}"),
        Column("growth", label="Growth %", format="{:.1%}"),
        Column("score", label="Score", formatter=lambda v: f"{v}/100 ★"),
    ])
    t.row("Item", "Revenue", "Growth %", "Score")
    t.row("Product A", 1234567.89, 0.234, 92)
    t.row("Product B", 987654.32, -0.012, 78)
    t.row("Product C", 2500000.00, 0.157, 88)
    t.zebra()

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_formatted"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_formatted.pdf")


if __name__ == "__main__":
    main()
