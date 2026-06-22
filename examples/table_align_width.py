"""Example: Cell alignment × column width modes in tables.

Shows:
  - Cell text alignment: left / center / right  ×  top / middle / bottom
  - Column width distributions: CONTENT, EQUAL, FIXED, FIXED mixed
"""

from __future__ import annotations
from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, cell
from reporting.tablespec.sizing import ColumnDistrib, TableFitMode, TableSizing
from reporting.tablespec.style import TableStyle, CellStyle
from reporting.layout.panel import HAlign, VAlign
from reporting.renderers.pdf.renderer import PDFRenderer

DATA = [
    ("C-01",  "Front Spar",       "Carbon Fiber",  450.0,  "OK"),
    ("C-02",  "Rear Spar",        "Al 7075-T6",    385.7,  "WARN"),
    ("C-03",  "Center Rib",       "Al 7075-T6",    180.3,  "OK"),
    ("C-04",  "Upper Skin",       "Ti-6Al-4V",     320.0,  "OK"),
    ("D-01",  "Bulkhead #2",      "Steel 4340",    560.2,  "FAIL"),
]

COL_NAMES = ["ID", "Component", "Material", "Stress", "Status"]


def base_table() -> TableSpec:
    cols = [
        Column("id",        label="ID"),
        Column("component", label="Component"),
        Column("material",  label="Material"),
        Column("stress",    label="Stress", format="{:.1f}"),
        Column("status",    label="Status"),
    ]
    t = TableSpec(columns=cols, style=TableStyle(font_size=9, header_font_size=10))
    for row in DATA:
        t.row(*row)
    return t


# ─── Slide 1: Column width modes ────────────────────────────────────────
s1 = Slide()
s1.title = "Column width distributions"
s1.grid_layout(rows=2, cols=2, gap=8)

distribs: list[tuple[str, ColumnDistrib, list[float | None]]] = [
    ("CONTENT — proportional to text width",     ColumnDistrib.CONTENT, [None, None, None, None, None]),
    ("EQUAL — all columns same width",            ColumnDistrib.EQUAL,   [None, None, None, None, None]),
    ("FIXED — every column has explicit width",   ColumnDistrib.FIXED,  [30, 70, 60, 45, 35]),
    ("FIXED mixed — some fixed, some flexible",     ColumnDistrib.FIXED,  [None, 80, None, None, 40]),
]

for idx, (label, distrib, widths) in enumerate(distribs):
    r, c = divmod(idx, 2)
    cols = [
        Column("id",        label="ID",       width=widths[0]),
        Column("component", label="Component", width=widths[1]),
        Column("material",  label="Material",  width=widths[2]),
        Column("stress",    label="Stress",    format="{:.1f}", width=widths[3]),
        Column("status",    label="Status",    width=widths[4]),
    ]
    t = TableSpec(
        columns=cols,
        style=TableStyle(font_size=9, header_font_size=10),
        sizing=TableSizing(fit_mode=TableFitMode.STRETCH, column_distrib=distrib),
    )
    for row in DATA:
        t.row(*row)
    s1[r, c].align(HAlign.CENTER, VAlign.BOTTOM).table(t)

doc = Document("Table Alignment & Width Demo")
doc.add_slide(s1)


# ─── Slide 2: Cell text alignment ────────────────────────────────────────
s2 = Slide()
s2.title = "Cell text alignment — align_h × align_v (per-column)"
s2.grid_layout(rows=3, cols=1, gap=6)

alignments_per_col: list[tuple[str, list[str | None], list[str | None]]] = [
    ("align_h: left, center, right (each column)", ["left", "center", "right", "left", "center"], [None]*5),
    ("align_v: top, middle, bottom (each column)", [None]*5, ["top", "middle", "bottom", "top", "middle"]),
    ("align_h + align_v mixed",                    ["left", "right", "center", "left", "right"], ["top", "bottom", "middle", "bottom", "top"]),
]

for ridx, (label, h_aligns, v_aligns) in enumerate(alignments_per_col):
    cols = [
        Column("id",        label="ID",       style=CellStyle(align_h=h_aligns[0], align_v=v_aligns[0])),
        Column("component", label="Component", style=CellStyle(align_h=h_aligns[1], align_v=v_aligns[1])),
        Column("material",  label="Material",  style=CellStyle(align_h=h_aligns[2], align_v=v_aligns[2])),
        Column("stress",    label="Stress",    format="{:.1f}", style=CellStyle(align_h=h_aligns[3], align_v=v_aligns[3])),
        Column("status",    label="Status",    style=CellStyle(align_h=h_aligns[4], align_v=v_aligns[4])),
    ]
    t = TableSpec(
        columns=cols,
        style=TableStyle(font_size=9, header_font_size=10),
        sizing=TableSizing(fit_mode=TableFitMode.STRETCH, column_distrib=ColumnDistrib.CONTENT),
    )
    for row in DATA:
        t.row(*row)
    s2[ridx, 0].align(HAlign.STRETCH, VAlign.STRETCH).table(t)

doc.add_slide(s2)


# ─── Slide 3: Combining alignment and width modes ───────────────────────
s3 = Slide()
s3.title = "Mixed: fixed-width columns with per-cell alignment"
s3.grid_layout(rows=3, cols=2, gap=8)

cells_info = [
    # (h_align, v_align, distrib, widths_desc, widths)
    (HAlign.CENTER, VAlign.TOP,    ColumnDistrib.FIXED, "FIXED + LEFT text",        [30, 70, 60, 45, 35]),
    (HAlign.CENTER, VAlign.TOP,    ColumnDistrib.FIXED, "FIXED mixed + RIGHT text", [None, 80, None, None, 40]),
    (HAlign.LEFT,   VAlign.MIDDLE, ColumnDistrib.CONTENT, "CONTENT + LEFT align",  [None, None, None, None, None]),
    (HAlign.LEFT,   VAlign.MIDDLE, ColumnDistrib.EQUAL, "EQUAL + LEFT align",       [None, None, None, None, None]),
    (HAlign.RIGHT,  VAlign.BOTTOM, ColumnDistrib.FIXED, "FIXED + RIGHT align",     [35, 75, 55, 45, 35]),
    (HAlign.RIGHT,  VAlign.BOTTOM, ColumnDistrib.CONTENT, "CONTENT + RIGHT align", [None, None, None, None, None]),
]

for idx, (ha, va, distrib, wlabel, widths) in enumerate(cells_info):
    r, c_ = divmod(idx, 2)
    cols = [
        Column("id",        label="ID",       style=CellStyle(align_h="left"),   width=widths[0]),
        Column("component", label="Component", style=CellStyle(align_h="left"),   width=widths[1]),
        Column("material",  label="Material",  style=CellStyle(align_h="right"),  width=widths[2]),
        Column("stress",    label="Stress",    format="{:.1f}", style=CellStyle(align_h="right"), width=widths[3]),
        Column("status",    label="Status",    style=CellStyle(align_h="center"), width=widths[4]),
    ]
    t = TableSpec(
        columns=cols,
        style=TableStyle(font_size=9, header_font_size=10),
        sizing=TableSizing(fit_mode=TableFitMode.STRETCH, column_distrib=distrib),
    )
    for row in DATA:
        t.row(*row)
    s3[r, c_].align(ha, va).table(t)

doc.add_slide(s3)

out = Path(__file__).parent / "table_align_width"
PDFRenderer().render_document(doc, str(out) + ".pdf")
print("Generated table_align_width.pdf")
