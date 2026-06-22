"""Row grouping via TableSpec.group() — tag rows with category names.

Groups are metadata on TableRow; they are not rendered visually by the
PDF renderer but are available programmatically via to_dict(), to_records(),
or direct row inspection.
"""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Row Grouping", author="Engineer")

    # Slide 1: table with groups, rendered normally
    slide = Slide()
    slide.title = "Grouped Rows"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(columns=[
        Column("component", label="Component"),
        Column("material", label="Material"),
        Column("mass", label="Mass (kg)", format="{:.1f}"),
        Column("cost", label="Cost ($)", format="${:.2f}"),
    ])

    t.row("Component", "Material", "Mass (kg)", "Cost ($)")

    t.group("Frame")
    t.row("Beam A", "Steel", 45.2, 320.00)
    t.row("Beam B", "Aluminum", 22.8, 450.00)

    t.group("Engine")
    t.row("Piston", "Cast Iron", 12.3, 180.00)
    t.row("Crankshaft", "Steel", 28.1, 520.00)

    t.group("Controls")
    t.row("ECU", "PCB", 0.8, 1200.00)

    t.zebra()
    slide[0, 0].table(t)
    doc.add_slide(slide)

    # Show group metadata in console
    print("Row groups via t.to_dict():")
    for row_dict in t.to_dict()["rows"]:
        g = row_dict['group'] or "(header)"
        print(f"  {g:>10s} | {row_dict['cells']}")

    out = Path(__file__).parent / "table_grouped"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print(f"\nGenerated {out.name}.pdf")


if __name__ == "__main__":
    main()
