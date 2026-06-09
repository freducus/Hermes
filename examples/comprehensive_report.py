from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.layout.grid import Grid
from reporting.layout.sizing import Fill, Percent
from reporting.elements.text import TextElement, TextAlignment
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer
from reporting.tablespec import TableSpec
from reporting.styles.colors import NAMED_COLORS, Color
from reporting.background import SolidBackground, GradientBackground, ImageBackground
from reporting.title_config import TitleConfig, SubtitleConfig, TitlePanelConfig, SubtitlePlacement

OUT_DIR = Path(__file__).parent


def create_logo() -> str:
    """Generate a small PE logo PNG for the footer."""
    path = OUT_DIR / "_logo.png"
    if path.exists():
        return str(path)
    fig, ax = plt.subplots(figsize=(0.5, 0.25))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.5)
    ax.set_facecolor("none")
    ax.text(0.02, 0.25, "PE", fontsize=14, fontweight="bold",
            color="#1565C0", va="center", ha="left")
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=96, bbox_inches="tight", pad_inches=0,
                transparent=True)
    plt.close(fig)
    return str(path)


def create_bg_image() -> str:
    path = OUT_DIR / "bg_pattern.png"
    if path.exists():
        return str(path)
    fig, ax = plt.subplots(figsize=(10, 5.625))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.625)
    ax.set_facecolor("#0D1B2A")
    for i in range(30):
        x = i * 0.35
        y = 5.625 / 2
        r = 0.5 + (i % 7) * 0.2
        circle = plt.Circle(
            (x, y + (i % 3 - 1) * 1.2), r,
            color=f"#{(20 + i*8):02X}3A{(50 + i*6):02X}",
            alpha=0.35 + (i % 5) * 0.12,
            linewidth=0,
        )
        ax.add_patch(circle)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=96, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    return str(path)


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
    LOGO_PATH = create_logo()

    # ---- Slide 1: Typography showcase ----
    slide = Slide("Typography Showcase", footer_logo=LOGO_PATH)
    slide.grid_layout(rows=3, cols=3, gap=10, padding=Edges.all(15))

    slide[0, 0].background_color = "aliceblue"
    slide[0, 0].text("Helvetica Bold 14", font_name="Helvetica-Bold", size=14)

    slide[0, 1].background_color = "moccasin"
    slide[0, 1].text("Times-Roman 12 italic", font_name="Times-Roman", size=12, italic=True)

    slide[0, 2].background_color = "honeydew"
    slide[0, 2].text("Courier 10 bold red", font_name="Courier", size=10, bold=True, color="firebrick")

    slide[1, 0].background_color = "rgb(243, 229, 245)"
    slide[1, 0].text("Times-Bold 16 blue", font_name="Times-Bold", size=16, color="royalblue")

    slide[1, 1].background_color = "rgb(251, 233, 231)"
    slide[1, 1].text("Helvetica 11 black", size=11, color=(33, 33, 33))

    slide[1, 2].background_color = "lightcyan"
    slide[1, 2].text("Courier-Bold 9 green", font_name="Courier-Bold", size=9, color="forestgreen")

    slide[2, 0].background_color = "cornsilk"
    slide[2, 0].text("Helvetica-Oblique 13 gray", font_name="Helvetica-Oblique", size=13, color="dimgray")

    slide[2, 1].background_color = "rgb(237, 231, 246)"
    slide[2, 1].text("Times-Italic 15 dark magenta", font_name="Times-Italic", size=15, color=(106, 27, 154))

    slide[2, 2].background_color = "rgb(225, 245, 254)"
    slide[2, 2].text("Helvetica 9 teal center", size=9, color="teal", alignment="center")
    doc.add_slide(slide)

    # ---- Slide 2: Matplotlib plots ----
    slide = Slide("Plots Gallery", footer_logo=LOGO_PATH)
    slide.grid_layout(rows=1, cols=3, gap=12, padding=Edges.all(15))

    plots = [
        ("Sine Wave", "C0"),
        ("Cosine", "C1"),
        ("Damped", "C2")]
    for i, (title, color) in enumerate(plots):
        r, c = divmod(i, 3)
        slide[r, c].plot(create_plot(title, color), format="pdf")
    doc.add_slide(slide)

    # ---- Slide 3: Tables ----
    slide = Slide("Data Tables", footer_logo=LOGO_PATH)
    slide.grid_layout(rows=2, cols=2, gap=15, padding=Edges.all(15))

    df = create_table_data()
    slide[0, 0].text("Zebra table", font_name="Helvetica-Bold", size=12)
    slide[0, 0].background_color = "lightblue"

    df2 = pd.DataFrame({
        "Metric": ["Iterations", "Residual", "Lift Coeff", "Drag Coeff"],
        "Value": [250, 1.2e-6, 0.523, 0.041],
        "Converged": [True, True, True, True],
    })
    slide[0, 1].text("Engineering data", font_name="Times-Bold", size=12, color="midnightblue")
    slide[0, 1].background_color = "cornsilk"

    slide[1, :].table(df, zebra=True)
    doc.add_slide(slide)

    # ---- Slide 4: Dashboard mix ----
    slide = Slide("Dashboard", footer_logo=LOGO_PATH)
    slide.grid_layout(rows=3, cols=3, gap=8, padding=Edges.all(12))

    slide[0, 0].plot(create_plot("Efficiency", "C2"), format="pdf")
    slide[0, 1].plot(create_plot("Power", "C1"), format="pdf")
    slide[0, 2].plot(create_plot("Temperature", "C3"), format="pdf")

    slide[1, 0].text("Summary:\nAll systems nominal.", font_name="Times-Roman", size=10)
    slide[1, 0].background_color = "honeydew"

    slide[1, 1].text("Warnings: 1\nCritical: 0", font_name="Helvetica-Bold", size=11, color="orangered")
    slide[1, 1].background_color = "moccasin"

    slide[1, 2].text("Uptime: 99.8%\nStatus: OK", font_name="Courier", size=9)
    slide[1, 2].background_color = "lightblue"

    df_dash = pd.DataFrame({
        "Component": ["Pump", "Valve", "Sensor", "Actuator", "Controller"],
        "Status": ["OK", "OK", "Warning", "OK", "OK"],
        "Temp (C)": [45.2, 38.1, 72.8, 41.5, 36.0],
    })
    slide[2, :].table(df_dash, zebra=True)
    doc.add_slide(slide)

    # ---- Slide 5: Nested containers ----
    slide = Slide("Nested Layouts", footer_logo=LOGO_PATH, subtitle="Container element with sub-grids")
    slide.grid_layout(rows=1, cols=2, gap=15, padding=Edges.all(15))

    inner = Grid(rows=3, cols=1, row_sizes=[Fill, Fill, Fill], gap=6)
    inner[0, 0].panel.background_color = "aliceblue"
    inner[0, 0].element = TextElement("Top panel", font_name="Helvetica-Bold", size=11)
    inner[1, 0].panel.background_color = "cornsilk"
    inner[1, 0].element = TextElement("Middle panel with info", font_name="Times-Roman", size=10, color="rgb(51, 51, 51)")
    inner[2, 0].panel.background_color = "honeydew"
    inner[2, 0].element = TextElement("Bottom panel, all good", font_name="Courier", size=9, color="forestgreen", italic=True)
    slide[0, 0].grid_layout(inner)

    inner2 = Grid(rows=2, cols=2, row_sizes=[Fill, Fill], col_sizes=[Fill, Fill], gap=6)
    inner2[0, 0].panel.background_color = "rgb(243, 229, 245)"
    inner2[0, 0].element = TextElement("A", font_name="Times-Bold", size=14, color=(106, 27, 154), alignment="center")
    inner2[0, 1].panel.background_color = "rgb(251, 233, 231)"
    inner2[0, 1].element = TextElement("B", font_name="Helvetica-Bold", size=14, color="rgb(191, 54, 12)", alignment="center")
    inner2[1, 0].panel.background_color = "lightcyan"
    inner2[1, 0].element = TextElement("C", font_name="Courier-Bold", size=14, color="teal", alignment="center")
    inner2[1, 1].panel.background_color = "cornsilk"
    inner2[1, 1].element = TextElement("D", font_name="Times-Italic", size=14, color="orangered", alignment="center")
    slide[0, 1].grid_layout(inner2)
    doc.add_slide(slide)

    # ---- Slide 6: Long-form text content ----
    slide = Slide("Detailed Analysis", footer_logo=LOGO_PATH, subtitle="Technical notes across multiple columns")
    slide.grid_layout(rows=2, cols=3, gap=10, padding=Edges.all(15))

    slide[0, 0].text(
        "The simulation converged after 312 iterations. "
        "The residual dropped below 1e-6. Mesh quality was adequate.",
        font_name="Times-Roman", size=9, color=(33, 33, 33),
    )
    slide[0, 0].background_color = "whitesmoke"
    slide[0, 1].text(
        "Temperature distribution shows a maximum gradient of "
        "15 K/m near the leading edge. Further refinement recommended.",
        font_name="Helvetica", size=9, color="rgb(66, 66, 66)",
    )
    slide[0, 1].background_color = "whitesmoke"
    slide[0, 2].text(
        "Pressure coefficient matches experimental data within 3% "
        "across the entire chord. Validation criteria met.",
        font_name="Courier", size=8, color="rgb(51, 51, 51)",
    )
    slide[0, 2].background_color = "whitesmoke"

    slide[1, 0].text("WARNING: Temperature exceeds limits.", font_name="Helvetica-Bold", size=10, color="firebrick")
    slide[1, 0].background_color = "mistyrose"
    slide[1, 1].text("All other parameters nominal.", font_name="Times-Roman", size=10, color="forestgreen", italic=True)
    slide[1, 1].background_color = "honeydew"
    slide[1, 2].text("Report generated automatically.", font_name="Helvetica", size=10, color="dimgray")
    slide[1, 2].background_color = "rgb(245, 245, 245)"
    doc.add_slide(slide)

    # ---- Slide 7: TableSpec tables ----
    slide = Slide(
        "TableSpec Demo",
        subtitle="For-loops, spans, column formatting, heatmap",
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(rows=2, cols=2, gap=12, padding=Edges.all(15))

    # --- Table 1 (top-left): for-loop + set_format + header merged with colspan + zebra ---
    ts1 = TableSpec()
    ts1.add_column("Case", format="{:.0f}")
    ts1.add_column("Mach", format="{:.3f}")
    ts1.add_column("Efficiency", format="{:.1%}")
    ts1.add_column("PR", format="{:.2f}")

    cases = [(0.85, 0.94, 28.5), (0.78, 0.91, 26.3),
             (0.65, 0.88, 24.2), (0.45, 0.72, 18.1)]
    for i, (mach, eff, pr) in enumerate(cases, start=1):
        ts1.add_row(i, mach, eff, pr)

    ts1.column("Efficiency").set_format("{:.2%}")
    ts1.column("Mach").set_format("{:.4f}")
    ts1.cell(row=0, col=0, value="Engine Test Cases", colspan=4,
             background_color="steelblue", text_color="white")
    ts1.zebra()
    slide[0, 0].text("For-loop rows + colspan merge + set_format()", font_name="Helvetica-Bold", size=10)
    slide[0, 0].table_spec(ts1)

    # --- Table 2 (top-right): for-loop + highlight_max/min + custom formatter ---
    ts2 = TableSpec()
    ts2.add_column("Iteration", format="{:.0f}")
    ts2.add_column("Continuity")
    ts2.add_column("X-Momentum")
    ts2.add_column("Y-Momentum")

    for step in range(5):
        n = step + 1
        ts2.add_row(50 * n, 1.5e-3 / n, 4.2e-4 / n, 6.8e-4 / n)

    ts2.column("Continuity").set_formatter(lambda v: f"{v:.2e}")
    ts2.column("X-Momentum").set_formatter(lambda v: f"{v:.3e}")
    ts2.column("Y-Momentum").set_formatter(lambda v: f"{v:.3e}")
    ts2.highlight_max("Continuity")
    ts2.highlight_min("Y-Momentum")
    slide[0, 1].text("For-loop + highlight_max/min + formatter", font_name="Helvetica-Bold", size=10)
    slide[0, 0].background_color = "lightblue"
    slide[0, 1].table_spec(ts2)

    # --- Table 3 (bottom-left): rowspan groups + for-loop over stages ---
    ts3 = TableSpec()
    ts3.add_column("Stage")
    ts3.add_column("Section")
    ts3.add_column("Efficiency", format="{:.1%}")
    ts3.add_column("PR", format="{:.2f}")

    stages = [
        ("Stage 1", [("Rotor", 0.93, 1.85), ("Stator", 0.91, 1.72)]),
        ("Stage 2", [("Rotor", 0.94, 1.88), ("Stator", 0.92, 1.75)]),
        ("Stage 3", [("Rotor", 0.95, 1.91), ("Stator", 0.93, 1.78)]),
    ]
    for stage_name, rows in stages:
        for sect, eff, pr in rows:
            ts3.add_row(stage_name, sect, eff, pr)

    row_idx = 0
    for stage_name, rows in stages:
        ts3.cell(row=row_idx, col=0, value=stage_name,
                 rowspan=len(rows), background_color="rgb(214, 228, 240)")
        row_idx += len(rows)

    ts3.zebra()
    slide[1, 0].text("Rowspan groups via cell() + for-loop over nested data", font_name="Helvetica-Bold", size=10)
    slide[1, 0].table_spec(ts3)

    # --- Table 4 (bottom-right): from_dataframe + heatmap + for-loop generation ---
    rng = np.random.default_rng(42)
    sensor_data = []
    for i in range(1, 9):
        sensor_data.append({
            "Sensor": f"S{i:02d}",
            "Temp (\u00b0C)": round(75 + float(rng.normal()) * 10, 1),
            "Pressure (kPa)": round(100 + float(rng.normal()) * 15, 1),
            "Vibration (mm/s)": round(0.5 + abs(float(rng.normal())) * 0.3, 3),
        })
    df_sensors = pd.DataFrame(sensor_data)
    ts4 = TableSpec.from_dataframe(df_sensors)
    ts4.column("Temp (\u00b0C)").set_format("{:.1f}")
    ts4.column("Pressure (kPa)").set_format("{:.1f}")
    ts4.column("Vibration (mm/s)").set_format("{:.3f}")
    ts4.heatmap("Temp (\u00b0C)")
    ts4.zebra()
    slide[1, 1].text("from_dataframe + heatmap on Temp + for-loop rows", font_name="Helvetica-Bold", size=10)
    slide[1, 1].table_spec(ts4)
    doc.add_slide(slide)

    # ---- Slide 8: Solid background ----
    slide = Slide(
        "Solid Background",
        subtitle="SolidBackground('aliceblue')",
        background=SolidBackground("aliceblue"),
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide[0, 0].text(
        "This slide uses a solid background color.",
        font_name="Helvetica", size=14, color="midnightblue",
    )
    doc.add_slide(slide)

    # ---- Slide 9: Gradient background (pronounced) ----
    slide = Slide(
        "Gradient Background",
        subtitle="GradientBackground('midnightblue', 'tomato', angle=135)",
        background=GradientBackground("midnightblue", "tomato", angle=135),
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide[0, 0].text(
        "This slide uses a pronounced linear gradient.",
        font_name="Helvetica-Bold", size=16, color="white",
    )
    doc.add_slide(slide)

    # ---- Slide 10: Image background ----
    bg_path = create_bg_image()
    slide = Slide(
        "Image Background",
        subtitle=f"ImageBackground('{Path(bg_path).name}', opacity=0.85)",
        background=ImageBackground(bg_path, opacity=0.85),
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide[0, 0].text(
        "This slide uses an image as background.",
        font_name="Helvetica-Bold", size=16, color="white",
    )
    doc.add_slide(slide)

    # ---- Slide 11: Formatted title/subtitle with BESIDE placement ----
    slide = Slide(
        "Custom Title Formatting",
        subtitle="Subtitle beside title — panel 70px",
        background=SolidBackground("rgb(245, 245, 245)"),
        title_config=TitleConfig(
            font_name="Times-Bold",
            font_size=26,
            bold=False,
            color="royalblue",
            alignment=TextAlignment.LEFT,
            show_separator=False,
        ),
        subtitle_config=SubtitleConfig(
            font_name="Helvetica-Oblique",
            font_size=12,
            italic=True,
            color="gray",
            alignment=TextAlignment.RIGHT,
        ),
        title_panel_config=TitlePanelConfig(
            subtitle_placement=SubtitlePlacement.BESIDE,
            subtitle_width_ratio=0.3,
        ),
        title_panel_height=70,
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(
        rows=1, cols=2,
        col_sizes=[Percent(60), Percent(40)],
        padding=Edges.all(0), gap=16,
    )
    slide[0, 0].text(
        "60% column: title config demo.\n"
        "Times-Bold 26pt, subtitle italic right 12pt.",
        font_name="Helvetica", size=12, color="rgb(51, 51, 51)",
    )
    slide[0, 1].text(
        "40% column: right panel.",
        font_name="Helvetica", size=12, color="dimgray",
    )
    slide[0, 1].background_color = "rgb(232, 234, 246)"
    doc.add_slide(slide)

    # ---- Slide 12: BELOW placement (green theme) ----

    # ---- Slide 12: BELOW placement (green theme) ----
    slide = Slide(
        "BELOW Subtitle Placement",
        subtitle="Separator enabled, centered, taller panel (80px)",
        title_config=TitleConfig(
            font_size=24,
            bold=True,
            color="forestgreen",
            alignment=TextAlignment.CENTER,
            show_separator=True,
            separator_color="lightgreen",
            separator_width=2,
        ),
        subtitle_config=SubtitleConfig(
            font_name="Helvetica",
            font_size=13,
            color="olivedrab",
            alignment=TextAlignment.CENTER,
        ),
        title_panel_height=80,
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(
        rows=1, cols=2,
        col_sizes=[Percent(60), Percent(40)],
        padding=Edges.all(0), gap=16,
    )
    slide[0, 0].text(
        "60% column: title config demo.\n"
        "Times-Bold 26pt, subtitle italic right 12pt.",
        font_name="Helvetica", size=12, color="rgb(51, 51, 51)",
    )
    slide[0, 1].text(
        "40% column: right panel.",
        font_name="Helvetica", size=12, color="dimgray",
    )
    slide[0, 1].background_color = "rgb(232, 234, 246)"
    doc.add_slide(slide)

    # ---- Slide 13: BELOW placement (green theme, duplicate) ----
    slide = Slide(
        "BELOW Subtitle Placement",
        subtitle="Separator enabled, centered, taller panel (80px)",
        title_config=TitleConfig(
            font_size=24,
            bold=True,
            color="forestgreen",
            alignment=TextAlignment.CENTER,
            show_separator=True,
            separator_color="lightgreen",
            separator_width=2,
        ),
        subtitle_config=SubtitleConfig(
            font_name="Helvetica",
            font_size=13,
            color="olivedrab",
            alignment=TextAlignment.CENTER,
        ),
        title_panel_height=80,
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(
        rows=1, cols=2,
        col_sizes=[Percent(60), Percent(40)],
        padding=Edges.all(0), gap=16,
    )
    slide[0, 0].text(
        "60% column: centered title + subtitle,\n"
        "green separator, 80px panel.",
        font_name="Helvetica", size=12, color="rgb(51, 51, 51)",
    )
    slide[0, 1].text(
        "40% column: secondary info.",
        font_name="Helvetica", size=12, color="dimgray",
    )
    slide[0, 1].background_color = "honeydew"
    slide[0, 0].background_color = "dimgray"
    doc.add_slide(slide)

    # ---- Slide Final: Named colors swatch sorted by hue ----
    def _luminance(r: int, g: int, b: int) -> float:
        return 0.299 * r + 0.587 * g + 0.114 * b

    colors = Color.sort_by_hue(list(NAMED_COLORS.items()))
    n = len(colors)
    cols = 15
    rows = math.ceil(n / cols)

    slide = Slide(
        f"All {n} Named Colors",
        subtitle=f"Sorted by hue — {cols}×{rows} grid",
        title_panel_height=50,
        footer_logo=LOGO_PATH,
    )
    slide.grid_layout(rows=rows, cols=cols, gap=1, padding=Edges.all(8))

    for i, (name, hex_str) in enumerate(colors):
        r_idx = i // cols
        c_idx = i % cols
        cell = slide[r_idx, c_idx]
        cell.background_color = name
        c = Color.parse(hex_str)
        lum = _luminance(c.r, c.g, c.b)
        text_color = "white" if lum <= 128 else "black"
        cell.text(name, size=5, color=text_color, alignment="center")

    doc.add_slide(slide)

    out = OUT_DIR / "comprehensive_report"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated comprehensive_report.{pdf,html}")


if __name__ == "__main__":
    main()
