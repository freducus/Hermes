"""Hierarchical table — grouped categories with merged labels and multi-level headers."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, cell
from reporting.tablespec.style import TableStyle
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Hierarchical Table", author="Engineer")

    slide = Slide()
    slide.title = "Hierarchical Table"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(
        columns=[
            Column("category", label="Category"),
            Column("part", label="Part"),
            Column("material", label="Material"),
            Column("mass", label="Mass (kg)", format="{:.1f}"),
            Column("cost", label="Cost ($)", format="${:.2f}"),
        ],
        style=TableStyle(
            header_background="steelblue",
            header_text_color="white",
            font_size=9.0,
            padding=4,
        ),
    )

    # ── Header row (column labels) ──
    t.row("Category", "Part", "Material", "Mass (kg)", "Cost ($)")

    # ── Row 1: category header spanning all data rows ──
    t.row(
        cell("Frame", rowspan=3, bold=True, background_color="lightsteelblue"),
        cell("Beam A", bold=True),
        "Steel",
        45.2,
        320.00,
    )
    t.row(cell("Beam B"), "Aluminum", 22.8, 450.00)
    t.row(cell("Beam C", bold=True), "Steel", 38.5, 290.00)

    # ── Row 2: another category ──
    t.row(
        cell("Engine", rowspan=2, bold=True, background_color="honeydew"),
        cell("Piston", bold=True),
        "Cast Iron",
        12.3,
        180.00,
    )
    t.row(cell("Crankshaft", bold=True), "Steel", 28.1, 520.00)

    # ── Row 3: single-item category ──
    t.row(
        cell("Controls", rowspan=1, bold=True, background_color="bisque"),
        cell("ECU", bold=True),
        "PCB",
        0.8,
        1200.00,
    )

    # t.zebra()

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_hierarchical"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_hierarchical.pdf")


if __name__ == "__main__":
    main()
