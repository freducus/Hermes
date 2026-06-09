"""Table data (pandas DataFrame + TableSpec) — used by docs 05_tables.rst."""

from pathlib import Path

import pandas as pd

from reporting.document import Document
from reporting.slide import Slide
from reporting.footer_config import FooterConfig
from reporting.layout.geometry import Edges
from reporting.elements.text import TextAlignment
from reporting.tablespec import TableSpec, TableStyle
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer

OUT_DIR = Path(__file__).parent


def main() -> None:
    doc = Document("Tables Demo", author="Docs")

    # ---- Slide 1: Simple table from DataFrame ----
    slide1 = Slide(
        "Table from DataFrame",
        subtitle="zebra=True, include_index=False",
        footer_config=FooterConfig(center_text="Tables | Docs"),
    )
    slide1.grid_layout(rows=1, cols=1, gap=0, padding=Edges.all(20))

    df = pd.DataFrame({
        "Case": ["Baseline", "Config A", "Config B", "Config C"],
        "Mach": [0.65, 0.75, 0.85, 0.95],
        "Efficiency": [0.914, 0.937, 0.892, 0.856],
        "PR": [28.5, 32.1, 27.3, 24.8],
    })
    slide1[0, 0].table(df, zebra=True, include_index=False)
    doc.add_slide(slide1)

    # ---- Slide 2: TableSpec with for-loop + formats + highlights ----
    slide2 = Slide(
        "TableSpec: for-loop, formats, highlights",
        subtitle="add_column, add_row, highlight_max/min, zebra",
        footer_config=FooterConfig(center_text="Tables | Docs"),
    )
    slide2.grid_layout(rows=1, cols=1, gap=0, padding=Edges.all(20))

    ts = TableSpec()
    ts.add_column("Case", format="{:.0f}")
    ts.add_column("Mach", format="{:.3f}")
    ts.add_column("Efficiency", format="{:.1%}")
    ts.add_column("PR", format="{:.2f}")

    for i, (mach, eff, pr) in enumerate([
        (0.85, 0.94, 28.5),
        (0.78, 0.91, 26.3),
        (0.65, 0.88, 24.2),
        (0.45, 0.72, 18.1),
    ], start=1):
        ts.add_row(i, mach, eff, pr)

    ts.highlight_max("Efficiency")
    ts.highlight_min("PR")
    ts.zebra()
    slide2[0, 0].table_spec(ts)
    doc.add_slide(slide2)

    # ---- Slide 3: Merged cells and range styling ----
    slide3 = Slide(
        "Merged Cells & Range Styling",
        subtitle="cell() with colspan, range().style(), range().merge()",
        footer_config=FooterConfig(center_text="Tables | Docs"),
    )
    slide3.grid_layout(rows=1, cols=1, gap=0, padding=Edges.all(20))

    ts3 = TableSpec(style=TableStyle(header_rows=0))
    ts3.add_column("Component")
    ts3.add_column("Value")
    ts3.add_column("Status")

    ts3.add_row("Engine Parameters", "", "")
    ts3.cell(row=0, col=0, value="Engine Parameters", colspan=3,
             background_color="steelblue", text_color="white")
    ts3.add_row("Temperature", "85.3 C", "OK")
    ts3.add_row("Pressure", "101.3 kPa", "OK")
    ts3.add_row("Efficiency", "94.5%", "Warning")
    ts3.add_row("Vibration", "0.12 mm/s", "OK")

    ts3.range("A2:D5").style(background_color="#F0F4F8")
    slide3[0, 0].table_spec(ts3)
    doc.add_slide(slide3)

    # ---- Slide 4: Heatmap + from_dataframe ----
    import numpy as np

    slide4 = Slide(
        "Heatmap & from_dataframe",
        subtitle="from_dataframe, heatmap, set_format",
        footer_config=FooterConfig(center_text="Tables | Docs"),
    )
    slide4.grid_layout(rows=1, cols=1, gap=0, padding=Edges.all(20))

    rng = np.random.default_rng(42)
    sensor_data = [
        {
            "Sensor": f"S{i:02d}",
            "Temp (C)": round(75 + float(rng.normal()) * 10, 1),
            "Pressure (kPa)": round(100 + float(rng.normal()) * 15, 1),
        }
        for i in range(1, 9)
    ]
    df_sensors = pd.DataFrame(sensor_data)
    ts4 = TableSpec.from_dataframe(df_sensors)
    ts4.column("Temp (C)").set_format("{:.1f}")
    ts4.column("Pressure (kPa)").set_format("{:.1f}")
    ts4.heatmap("Temp (C)")
    ts4.zebra()
    slide4[0, 0].table_spec(ts4)
    doc.add_slide(slide4)

    # ---- Slide 5: Text alignment in cells ----
    slide5 = Slide(
        "Text Alignment",
        subtitle="LEFT, CENTER, RIGHT via cell() and column defaults",
        footer_config=FooterConfig(center_text="Tables | Docs"),
    )
    slide5.grid_layout(rows=1, cols=1, gap=0, padding=Edges.all(20))

    ts5 = TableSpec()
    ts5.add_column("Item")
    ts5.add_column("Left", alignment=TextAlignment.LEFT)
    ts5.add_column("Center", alignment=TextAlignment.CENTER)
    ts5.add_column("Right", alignment=TextAlignment.RIGHT)

    ts5.add_row("Alpha", 1.0, 2.0, 3.0)
    ts5.add_row("Beta", 4.0, 5.0, 6.0)
    ts5.add_row("Gamma", 7.0, 8.0, 9.0)
    ts5.zebra()
    slide5[0, 0].table_spec(ts5)
    doc.add_slide(slide5)

    out = OUT_DIR / "docs_tables"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_tables.pdf and docs_tables.html")


if __name__ == "__main__":
    main()
