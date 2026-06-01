from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.layout.grid import Grid
from reporting.layout.sizing import Fill
from reporting.elements.container import ContainerElement
from reporting.elements.text import TextElement
from reporting.renderers.pdf.renderer import PDFRenderer


def create_plot(title: str, color: str = "C0") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(3.5, 2.2))
    x = np.linspace(0, 10, 80)
    y = np.sin(x) * np.exp(-x / 4) + np.random.normal(0, 0.05, 80)
    ax.plot(x, y, color=color, linewidth=1.5)
    ax.set_title(title, fontsize=9)
    ax.grid(True, alpha=0.25)
    ax.tick_params(labelsize=7)
    return fig


def create_table_data() -> pd.DataFrame:
    return pd.DataFrame({
        "Parameter": ["Efficiency", "Power (kW)", "Temperature (C)", "Pressure (bar)"],
        "Value": [94.5, 250.0, 85.3, 101.3],
        "Target": [92.0, 240.0, 90.0, 100.0],
        "Deviation (%)": [2.7, 4.2, -5.2, 1.3],
        "Status": ["Pass", "Pass", "Warning", "Pass"],
    })


def main() -> None:
    doc = Document(title="Comprehensive Report", author="pyreportengine Demo")

    # ---- Slide 1: Typography showcase ----
    slide = Slide("Typography Showcase")
    slide.grid_layout(rows=3, cols=3, gap=10, padding=Edges.all(15))

    slide[0, 0]._cell.panel.background_color = "#E8F0FE"
    slide[0, 0].text("Helvetica Bold 14", font_name="Helvetica-Bold", size=14)

    slide[0, 1]._cell.panel.background_color = "#FFF3E0"
    slide[0, 1].text("Times-Roman 12 italic", font_name="Times-Roman", size=12, italic=True)

    slide[0, 2]._cell.panel.background_color = "#E8F5E9"
    slide[0, 2].text("Courier 10 bold red", font_name="Courier", size=10, bold=True, color="#C62828")

    slide[1, 0]._cell.panel.background_color = "#F3E5F5"
    slide[1, 0].text("Times-Bold 16 blue", font_name="Times-Bold", size=16, color="#1565C0")

    slide[1, 1]._cell.panel.background_color = "#FBE9E7"
    slide[1, 1].text("Helvetica 11 black", size=11, color="#212121")

    slide[1, 2]._cell.panel.background_color = "#E0F7FA"
    slide[1, 2].text("Courier-Bold 9 green", font_name="Courier-Bold", size=9, color="#2E7D32")

    slide[2, 0]._cell.panel.background_color = "#FFF8E1"
    slide[2, 0].text("Helvetica-Oblique 13 gray", font_name="Helvetica-Oblique", size=13, color="#616161")

    slide[2, 1]._cell.panel.background_color = "#EDE7F6"
    slide[2, 1].text("Times-Italic 15 dark magenta", font_name="Times-Italic", size=15, color="#6A1B9A")

    slide[2, 2]._cell.panel.background_color = "#E1F5FE"
    slide[2, 2].text("Helvetica 9 teal center", size=9, color="#00695C", alignment="center")
    doc.add_slide(slide)

    # ---- Slide 2: Matplotlib plots ----
    slide = Slide("Plots Gallery")
    slide.grid_layout(rows=2, cols=3, gap=12, padding=Edges.all(15))

    plots = [
        ("Sine Wave", "C0"),
        ("Cosine", "C1"),
        ("Damped", "C2"),
        ("Random Walk", "C3"),
        ("Exponential", "C4"),
        ("Square Root", "C5"),
    ]
    for i, (title, color) in enumerate(plots):
        r, c = divmod(i, 3)
        slide[r, c].plot(create_plot(title, color))
    doc.add_slide(slide)

    # ---- Slide 3: Tables ----
    slide = Slide("Data Tables")
    slide.grid_layout(rows=2, cols=2, gap=15, padding=Edges.all(15))

    df = create_table_data()
    slide[0, 0].text("Zebra table", font_name="Helvetica-Bold", size=12)
    slide[0, 0]._cell.panel.background_color = "#E3F2FD"

    df2 = pd.DataFrame({
        "Metric": ["Iterations", "Residual", "Lift Coeff", "Drag Coeff"],
        "Value": [250, 1.2e-6, 0.523, 0.041],
        "Converged": [True, True, True, True],
    })
    slide[0, 1].text("Engineering data", font_name="Times-Bold", size=12, color="#1F4E79")
    slide[0, 1]._cell.panel.background_color = "#FFF8E1"

    slide[1, :].table(df, zebra=True)
    doc.add_slide(slide)

    # ---- Slide 4: Dashboard mix ----
    slide = Slide("Dashboard")
    slide.grid_layout(rows=3, cols=3, gap=8, padding=Edges.all(12))

    slide[0, 0].plot(create_plot("Efficiency", "C2"))
    slide[0, 1].plot(create_plot("Power", "C1"))
    slide[0, 2].plot(create_plot("Temperature", "C3"))

    slide[1, 0].text("Summary:\nAll systems nominal.", font_name="Times-Roman", size=10)
    slide[1, 0]._cell.panel.background_color = "#E8F5E9"

    slide[1, 1].text("Warnings: 1\nCritical: 0", font_name="Helvetica-Bold", size=11, color="#E65100")
    slide[1, 1]._cell.panel.background_color = "#FFF3E0"

    slide[1, 2].text("Uptime: 99.8%\nStatus: OK", font_name="Courier", size=9)
    slide[1, 2]._cell.panel.background_color = "#E3F2FD"

    df_dash = pd.DataFrame({
        "Component": ["Pump", "Valve", "Sensor", "Actuator", "Controller"],
        "Status": ["OK", "OK", "Warning", "OK", "OK"],
        "Temp (C)": [45.2, 38.1, 72.8, 41.5, 36.0],
    })
    slide[2, :].table(df_dash, zebra=True)
    doc.add_slide(slide)

    # ---- Slide 5: Nested containers ----
    slide = Slide("Nested Layouts", subtitle="Container element with sub-grids")
    slide.grid_layout(rows=1, cols=2, gap=15, padding=Edges.all(15))

    inner = Grid(rows=3, cols=1, row_sizes=[Fill, Fill, Fill], gap=6)
    inner[0, 0].panel.background_color = "#E8F0FE"
    inner[0, 0].element = TextElement("Top panel", font_name="Helvetica-Bold", size=11)
    inner[1, 0].panel.background_color = "#FFF8E1"
    inner[1, 0].element = TextElement("Middle panel with info", font_name="Times-Roman", size=10, color="#333333")
    inner[2, 0].panel.background_color = "#E8F5E9"
    inner[2, 0].element = TextElement("Bottom panel, all good", font_name="Courier", size=9, color="#2E7D32", italic=True)
    container = ContainerElement(grid=inner)
    slide._set_cell_element(slide._grid[0, 0], container)

    inner2 = Grid(rows=2, cols=2, row_sizes=[Fill, Fill], col_sizes=[Fill, Fill], gap=6)
    inner2[0, 0].panel.background_color = "#F3E5F5"
    inner2[0, 0].element = TextElement("A", font_name="Times-Bold", size=14, color="#6A1B9A", alignment="center")
    inner2[0, 1].panel.background_color = "#FBE9E7"
    inner2[0, 1].element = TextElement("B", font_name="Helvetica-Bold", size=14, color="#BF360C", alignment="center")
    inner2[1, 0].panel.background_color = "#E0F7FA"
    inner2[1, 0].element = TextElement("C", font_name="Courier-Bold", size=14, color="#00695C", alignment="center")
    inner2[1, 1].panel.background_color = "#FFF8E1"
    inner2[1, 1].element = TextElement("D", font_name="Times-Italic", size=14, color="#E65100", alignment="center")
    container2 = ContainerElement(grid=inner2)
    slide._set_cell_element(slide._grid[0, 1], container2)
    doc.add_slide(slide)

    # ---- Slide 6: Long-form text content ----
    slide = Slide("Detailed Analysis", subtitle="Technical notes across multiple columns")
    slide.grid_layout(rows=2, cols=3, gap=10, padding=Edges.all(15))

    slide[0, 0].text(
        "The simulation converged after 312 iterations. "
        "The residual dropped below 1e-6. Mesh quality was adequate.",
        font_name="Times-Roman", size=9, color="#212121",
    )
    slide[0, 0]._cell.panel.background_color = "#FAFAFA"
    slide[0, 1].text(
        "Temperature distribution shows a maximum gradient of "
        "15 K/m near the leading edge. Further refinement recommended.",
        font_name="Helvetica", size=9, color="#424242",
    )
    slide[0, 1]._cell.panel.background_color = "#FAFAFA"
    slide[0, 2].text(
        "Pressure coefficient matches experimental data within 3% "
        "across the entire chord. Validation criteria met.",
        font_name="Courier", size=8, color="#333333",
    )
    slide[0, 2]._cell.panel.background_color = "#FAFAFA"

    slide[1, 0].text("WARNING: Temperature exceeds limits.", font_name="Helvetica-Bold", size=10, color="#C62828")
    slide[1, 0]._cell.panel.background_color = "#FFEBEE"
    slide[1, 1].text("All other parameters nominal.", font_name="Times-Roman", size=10, color="#2E7D32", italic=True)
    slide[1, 1]._cell.panel.background_color = "#E8F5E9"
    slide[1, 2].text("Report generated automatically.", font_name="Helvetica", size=10, color="#616161")
    slide[1, 2]._cell.panel.background_color = "#F5F5F5"
    doc.add_slide(slide)

    renderer = PDFRenderer()
    doc.render(renderer, str(Path(__file__).parent / "comprehensive_report.pdf"))
    print("Generated comprehensive_report.pdf")


if __name__ == "__main__":
    main()
