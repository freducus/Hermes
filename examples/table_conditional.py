"""Example 4: Conditional formatting — highlight max, min, heatmap, custom rules."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Conditional Formatting", author="Engineer")

    slide = Slide()
    slide.title = "Conditional Formatting"
    slide.grid_layout(rows=1, cols=1)

    t = TableSpec(columns=[
        Column("part", label="Part"),
        Column("defects", label="Defects", format="{:.0f}"),
        Column("cost", label="Cost ($)", format="${:.2f}"),
    ])
    t.row("Part", "Defects", "Cost ($)")
    t.row("A-100", 5, 1200.00)
    t.row("A-200", 12, 3400.00)
    t.row("B-100", 3, 800.00)
    t.row("B-200", 8, 2100.00)
    t.row("C-100", 15, 5600.00)
    t.add_highlight_max("defects", color="#FFC7CE")
    t.add_highlight_min("defects", color="#C6EFCE")
    t.add_heatmap("cost", min_color="lightyellow", max_color="#FF6600")

    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_conditional"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_conditional.pdf")


if __name__ == "__main__":
    main()
