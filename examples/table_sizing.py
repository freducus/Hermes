"""Example: Table sizing modes — STRETCH, SHRINK_FONT, PERCENT + element alignment.

Demonstrates fit modes and ``.align()`` for tables, text, and figures.
"""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, cell
from reporting.tablespec.sizing import ColumnDistrib, TableFitMode, TableSizing
from reporting.tablespec.style import TableStyle
from reporting.layout.panel import HAlign, VAlign
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Table Sizing & Element Alignment", author="Engineer")

    # ── Slide 1: Element alignment demo ─────────────────────────────
    slide = Slide()
    slide.title = "Element alignment — .align(HAlign.CENTER, VAlign.MIDDLE)"
    slide.grid_layout(rows=2, cols=2)

    # Top-left: text centered both ways
    slide[0, 0].align(HAlign.CENTER, VAlign.MIDDLE).text(
        "Centered Text", size=14, color="#333333"
    )

    # Top-right: text right-aligned, middle
    slide[0, 1].align(HAlign.RIGHT, VAlign.MIDDLE).text(
        "Right-aligned", size=12, color="#555555"
    )

    # Bottom-left: table centered
    t1 = TableSpec(
        columns=[
            Column("item", label="Part"),
            Column("val", label="Value", format="{:.2f}"),
        ],
        style=TableStyle(font_size=10),
    )
    t1.row("Alpha", 1.5).row("Beta", 2.7)
    slide[1, 0].align(HAlign.CENTER, VAlign.MIDDLE).table(t1)

    # Bottom-right: table left-aligned, top
    t2 = TableSpec(
        columns=[
            Column("item", label="Part"),
            Column("val", label="Value", format="{:.2f}"),
        ],
        style=TableStyle(font_size=10),
    )
    t2.row("Gamma", 3.2).row("Delta", 4.8)
    slide[1, 1].align(HAlign.LEFT, VAlign.TOP).table(t2)

    doc.add_slide(slide)

    # ── Slide 2: STRETCH ───────────────────────────────────────────
    slide2 = Slide()
    slide2.title = "STRETCH — content-aware columns, font unchanged"
    slide2.grid_layout(rows=1, cols=1)
    t3 = TableSpec(
        columns=[
            Column("item", label="Component"),
            Column("material", label="Material"),
            Column("stress", label="Stress (MPa)", format="{:.1f}"),
            Column("safety", label="Safety Factor", format="{:.2f}"),
        ],
        style=TableStyle(font_size=10.0, header_font_size=11.0),
        sizing=TableSizing(fit_mode=TableFitMode.STRETCH),
    )
    t3.row("Spar", "Carbon Fiber", 450.0, 2.50)
    t3.row("Rib", "Aluminum", 180.3, 3.80)
    t3.row("Skin", "Titanium", 320.0, 1.95)
    t3.row("Bulkhead", "Steel", 560.2, 1.50)
    slide2[0, 0].table(t3)
    doc.add_slide(slide2)

    # ── Slide 3: SHRINK_FONT ───────────────────────────────────────
    slide3 = Slide()
    slide3.title = "SHRINK_FONT — verbose headers, font shrinks to fit"
    slide3.grid_layout(rows=1, cols=6)
    t4 = TableSpec(
        columns=[
            Column("item", label="Component / Assembly Part Number"),
            Column("material", label="Material Specification"),
            Column("stress", label="Max Von Mises Stress (MPa)", format="{:.1f}"),
            Column("safety", label="Safety Factor (Yield / Ultimate)", format="{:.2f}"),
        ],
        style=TableStyle(font_size=10.0, header_font_size=11.0),
        sizing=TableSizing(
            fit_mode=TableFitMode.SHRINK_FONT,
            min_font_size=5.0,
        ),
    )
    t4.row("Front Spar LH", "Carbon Fiber / Epoxy Prepreg T700", 450.0, 2.50)
    t4.row("Rear Spar RH", "Carbon Fiber / Epoxy Prepreg T700", 385.7, 2.80)
    t4.row("Center Rib Assy", "Aluminum 7075-T6", 180.3, 3.80)
    t4.row("Upper Skin Panel", "Titanium Ti-6Al-4V", 320.0, 1.95)
    t4.row("Lower Skin Panel", "Titanium Ti-6Al-4V", 298.4, 2.10)
    t4.row("Bulkhead #2", "Steel AISI 4340", 560.2, 1.50)
    slide3[0, 0].table(t4)
    doc.add_slide(slide3)

    # ── Slide 4: PERCENT + column distributions ────────────────────
    slide4 = Slide()
    slide4.title = "PERCENT — 60% width, column distributions"
    slide4.grid_layout(rows=3, cols=1)

    t5a = TableSpec(
        columns=[
            Column("item", label="Component"),
            Column("stress", label="Stress (MPa)", format="{:.1f}"),
            Column("safety", label="Safety Factor", format="{:.2f}"),
        ],
        style=TableStyle(font_size=10.0),
        sizing=TableSizing(
            fit_mode=TableFitMode.PERCENT,
            percent_width=0.60,
            column_distrib=ColumnDistrib.CONTENT,
        ),
    )
    t5a.row("Spar", 450.0, 2.50)
    t5a.row("Rib", 180.3, 3.80)
    t5a.row("Skin", 320.0, 1.95)
    t5a.row("Bulkhead", 560.2, 1.50)
    slide4[0, 0].table(t5a)

    t5b = TableSpec(
        columns=[
            Column("item", label="Component"),
            Column("stress", label="Stress (MPa)", format="{:.1f}"),
            Column("safety", label="Safety Factor", format="{:.2f}"),
        ],
        style=TableStyle(font_size=10.0),
        sizing=TableSizing(
            fit_mode=TableFitMode.PERCENT,
            percent_width=0.60,
            column_distrib=ColumnDistrib.EQUAL,
        ),
    )
    t5b.row("Spar", 450.0, 2.50)
    t5b.row("Rib", 180.3, 3.80)
    t5b.row("Skin", 320.0, 1.95)
    t5b.row("Bulkhead", 560.2, 1.50)
    slide4[1, 0].table(t5b)

    t5c = TableSpec(
        columns=[
            Column("item", label="Component", width=120.0),
            Column("stress", label="Stress (MPa)", format="{:.1f}", width=80.0),
            Column("safety", label="Safety Factor", format="{:.2f}"),
        ],
        style=TableStyle(font_size=10.0),
        sizing=TableSizing(
            fit_mode=TableFitMode.PERCENT,
            percent_width=0.60,
            column_distrib=ColumnDistrib.FIXED,
        ),
    )
    t5c.row("Spar", 450.0, 2.50)
    t5c.row("Rib", 180.3, 3.80)
    t5c.row("Skin", 320.0, 1.95)
    t5c.row("Bulkhead", 560.2, 1.50)
    slide4[2, 0].table(t5c)

    doc.add_slide(slide4)

    out = Path(__file__).parent / "table_sizing"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_sizing.pdf")


if __name__ == "__main__":
    main()
