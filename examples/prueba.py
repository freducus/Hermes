from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL.ImageOps import scale

from reporting.document import Document
from reporting.layout import Sizing
from reporting.layout.panel import HAlign, VAlign
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.layout.grid import Grid
from reporting.layout.sizing import Fill, Percent
from reporting.elements.text import TextElement, TextAlignment
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer
from reporting.styles import Theme, Typography, FontSpec
from reporting.tablespec import TableSpec, TableStyle, CellStyle, cell
from reporting.tablespec.sizing import TableSizing, TableFitMode, ColumnDistrib
from reporting.styles.colors import NAMED_COLORS, Color, ColorPalette
from reporting.background import SolidBackground, GradientBackground, ImageBackground
from reporting.title_config import TitleText, SubtitleText, TitlePanel

OUT_DIR = Path(__file__).parent


def create_plot(title: str, color: str = "C0", figsize=(3.5, 2.2)) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)
    x = np.linspace(0, 10, 80)
    y = np.sin(x) * np.exp(-x / 4) + np.random.normal(0, 0.05, 80)
    ax.plot(x, y, color=color, linewidth=1.5)
    ax.set_title(title, fontsize=9)
    ax.grid(True, alpha=0.25)
    ax.tick_params(labelsize=7)
    ax.text(5, 0.6, f'original figsize{figsize}')
    return fig



def create_table_data() -> pd.DataFrame:
    return pd.DataFrame({
        "Parameter": ["Efficiency", "Power (kW)", "Temperature (C)", "Pressure (bar)"],
        "Value": [94.5, 250.0, 85.3, 101.3],
        "Target": [92.0, 240.0, 90.0, 100.0],
        "Deviation (%)": [2.7, 4.2, -5.2, 1.3],
        "Status": ["Pass", "Pass", "Warning", "Pass"],
    })

def create_logo() -> str:
    """Generate a small PE logo PNG for the footer."""
    path = OUT_DIR / "_logo.png"
    if path.exists():
        return str(path)
    fig, ax = plt.subplots(figsize=(0.5, 0.25))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.5)
    ax.set_facecolor("none")
    ax.text(0.02, 0.25, "ITP", fontsize=14, fontweight="bold",
            color="#1565C0", va="center", ha="left")
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=96, bbox_inches="tight", pad_inches=0,
                transparent=True)
    plt.close(fig)
    return str(path)


def create_stripe_image() -> str:
    """Generate a PNG with coloured stripes to show stretch vs preserve."""
    path = OUT_DIR / "_stripes.png"
    if path.exists():
        return str(path)
    fig, ax = plt.subplots(figsize=(2, 1.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor("#E3F2FD")
    for i, color in enumerate(["#1565C0", "#ED7D31", "#2E75B6", "#FFC000"]):
        ax.axvspan(i * 0.25, (i + 1) * 0.25, alpha=0.6, color=color)
    ax.text(0.5, 0.85, "TEST IMAGE", fontsize=18, fontweight="bold",
            color="#1F4E79", ha="center", va="center")
    ax.text(0.5, 0.5, "STRETCH\nto fill", fontsize=11,
            color="#333333", ha="center", va="center")
    ax.axis("off")
    fig.savefig(path, dpi=96, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return str(path)

_CORPORATE_PALETTE = ColorPalette(
    primary=Color.from_hex("#1F4E79"),
    secondary=Color.from_hex("#2E75B6"),
    accent=Color.from_hex("#ED7D31"),
    background=Color.from_hex("#FFFFFF"),
    text_primary=Color.from_hex("#333333"),
    text_secondary=Color.from_hex("#666666"),
    border=Color.from_hex("#D9D9D9"),
    error=Color.from_hex("#C00000"),
    warning=Color.from_hex("#FFC000"),
    success=Color.from_hex("#70AD47"),
    extras={
        "background_title": Color.from_hex("#0042ED"),
        "background_content": Color.from_hex("#FFFFFF"),
    },
)

_CORPORATE_TYPOGRAPHY = Typography(
    heading_1=FontSpec(family="Arial", size=36.0, bold=True, color="#1F4E79"),
    heading_2=FontSpec(family="Arial", size=22.0, bold=True, color="#1F4E79"),
    heading_3=FontSpec(family="Arial", size=16.0, bold=True, color="#2E75B6"),
    body=FontSpec(family="Arial", size=11.0, color="#333333"),
    caption=FontSpec(family="Arial", size=9.0, color="#666666"),
    code=FontSpec(family="Courier New", size=10.0, color="#333333"),
    mono=FontSpec(family="Courier New", size=10.0, color="#333333")
)


class CompanyTheme(Theme):
    def __init__(self) -> None:
        super().__init__(
            palette=_CORPORATE_PALETTE,
            typography=_CORPORATE_TYPOGRAPHY,
        )

class Slide_title(Slide):
    def __init__(self) -> None:
        super().__init__(theme=CompanyTheme())
        self.setup()

    def setup(self):
        self.background = SolidBackground(color=self.theme.palette.background_title)

        self.grid_layout(rows=1, cols=2, col_sizes=[Percent(60), Percent(40)], padding=Edges(left=25, right=25), gap=12)

        self.inner_grid = inner_grid = Grid(rows=3, cols=1, row_sizes=[Percent(50), Percent(15), Percent(35)], padding=Edges(12,0,0,0))

        inner_grid[0,0].align(HAlign.LEFT, VAlign.BOTTOM)

        inner_grid[1, 0].align(HAlign.LEFT, VAlign.TOP)

        disclaimer_grid = Grid(rows=1, cols=2, col_sizes=[Percent(75), Percent(15)])
        disclaimer_grid[0,0].align(HAlign.LEFT, VAlign.BOTTOM)
        disclaimer_grid[0,0].text("PROPRIETARY AND CONFIDENTIAL \n"
                                  " © Industria de Turbo Propulsores S.A.U (ITP Aero) and/or "
                             "its affiliates 2026. All rights reserved.This Presentation is provided to the recipient "
                             "for informational purposes. No representations or warranties are made by ITP Aero or "
                             "its direct and indirect equity holders and their respective affiliates as to the "
                             "accuracy of the information contained herein and any guidance and/or projections.The "
                             "information in this document shall not be used for any purpose other than that for "
                             "which it is supplied, nor disclosed without the express previous written consent of "
                             "Industria de Turbo Propulsores S.A.U. and/or its affiliates.", style='body', size=6, color=NAMED_COLORS['white'])

        inner_grid[2, 0].grid_layout(disclaimer_grid)

        self[0, 0].grid_layout(inner_grid)

        self[0, 1].align(HAlign.CENTER, VAlign.MIDDLE)
        # self[0, 1].image(create_logo())
        self[0, 1].image('./Logo_ITP.png', scale=0.5)

        self.set_title("Título")
        self.set_subtitle('Subtítulo')

    def set_title(self, title: str) -> None:
        self.inner_grid[0, 0].text(title, style='heading_1', color=NAMED_COLORS['white'], )

    def set_subtitle(self, subtitle: str) -> None:
        self.inner_grid[1, 0].text(subtitle, style='heading_2', color=NAMED_COLORS['white'])


class Slide_content(Slide):
    def __init__(self) -> None:
        super().__init__(theme=CompanyTheme())
        self.setup()

    def setup(self) -> None:
        self.title_panel.enabled=True
        self.title_panel.show_separator = False
        self.title_panel.height = 70
        self.title.text = "Título"
        self.title.font_size = 32
        self.title.color = self.theme.palette.background_title

        self.footer_panel.enabled=True
        self.footer_panel.center_text = 'Propietary Information - Confidential'
        self.footer_panel.logo = './Logo_ITP_blue.png'
        self.footer_panel.show_separator = False
        self.footer_panel.height = 40
        self.footer_panel.font_size = 6
        self.footer_panel.color = NAMED_COLORS['lightgray']


def main() -> None:
    doc = Document(title="Comprehensive Report", author="pyreportengine Demo")
    LOGO_PATH = create_logo()
    STRIPE_PATH = create_stripe_image()

    # ---- Slide 1: Typography showcase ----
    slide = Slide_title()
    slide.set_title('Title')
    slide.set_subtitle('Subtitle')
    doc.add_slide(slide)

    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].plot(create_plot('default:(STRETCH, STRETCH)'))
    inner_grid = Grid(rows=2, cols=1)
    inner_grid[0, 0].plot(create_plot('default:(STRETCH, STRETCH)'))
    inner_grid[1, 0].plot(create_plot('default:(STRETCH, STRETCH)'))
    slide[0, 1].grid_layout(inner_grid)
    doc.add_slide(slide)

    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].plot(create_plot('default:(STRETCH, STRETCH)'), format='pdf')
    inner_grid = Grid(rows=2, cols=1)
    inner_grid[0, 0].plot(create_plot('default:(STRETCH, STRETCH)'), format='pdf')
    inner_grid[1, 0].plot(create_plot('default:(STRETCH, STRETCH)'), format='pdf')
    slide[0, 1].grid_layout(inner_grid)
    doc.add_slide(slide)

    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].plot(create_plot('default:(STRETCH, STRETCH)', figsize=(2,4)))
    slide[0, 1].align(h_align=HAlign.STRETCH, v_align=VAlign.MIDDLE)
    slide[0, 1].plot(create_plot('(STRETCH, MIDDLE)', figsize=(2, 4)))
    doc.add_slide(slide)

    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].plot(create_plot('default:(STRETCH, STRETCH)', figsize=(3,4)))
    slide[0, 1].align(h_align=HAlign.CENTER, v_align=VAlign.STRETCH)
    slide[0, 1].plot(create_plot('(CENTER, STRETCH)', figsize=(3,4)))
    doc.add_slide(slide)

    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].plot(create_plot('default:(STRETCH, STRETCH)', figsize=(3,4)))
    slide[0, 1].align(h_align=HAlign.CENTER, v_align=VAlign.STRETCH)
    slide[0, 1].plot(create_plot('(CENTER, STRETCH)', figsize=(3,4)), preserve_aspect=True)
    doc.add_slide(slide)

    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].align(h_align=HAlign.CENTER, v_align=VAlign.MIDDLE)
    slide[0, 0].plot(create_plot('(CENTER, MIDDLE)', figsize=(2,2)))
    slide[0, 1].align(h_align=HAlign.STRETCH, v_align=VAlign.MIDDLE)
    slide[0, 1].plot(create_plot('(STRETCH, MIDDLE)', figsize=(2,2)))
    doc.add_slide(slide)

    # IMAGENES — fill all space (default preserve_aspect=False)
    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].image(STRIPE_PATH)
    inner_grid = Grid(rows=2, cols=1)
    inner_grid[0, 0].image(STRIPE_PATH)
    inner_grid[1, 0].image(STRIPE_PATH)
    slide[0, 1].grid_layout(inner_grid)
    doc.add_slide(slide)

    # IMAGENES — preserve_aspect=True, centre-aligned
    slide = Slide_content()
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=12, right=12))
    slide[0, 0].align(HAlign.CENTER, VAlign.MIDDLE).image(STRIPE_PATH, preserve_aspect=True)
    inner_grid = Grid(rows=2, cols=1)
    inner_grid[0, 0].align(HAlign.CENTER, VAlign.MIDDLE).image(STRIPE_PATH, preserve_aspect=True)
    inner_grid[1, 0].align(HAlign.CENTER, VAlign.MIDDLE).image(STRIPE_PATH, preserve_aspect=True)
    slide[0, 1].grid_layout(inner_grid)
    doc.add_slide(slide)

    # TEXTO — mixed formatting in the same text
    slide = Slide_content()
    slide.title.text = "Text — mixed formatting & paragraph alignment"
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=18, right=18), gap=24)
    te = slide[0, 0].text("", size=16)
    te.add_run("Mixed ", size=16)
    te.add_run("formatting", bold=True, size=20, color="#1565C0")
    te.add_run(" in ", italic=True, size=16)
    te.add_run("one", font_name="Courier", size=14)
    te.add_run(" text ", size=16, color="#ED7D31")
    te.add_run("element.", bold=True, italic=True, size=18, color="#C62828")
    te.add_block(spacing_before=14)
    te.add_run("Different ", size=14, font_name="Times-Roman")
    te.add_run("fonts", bold=True, size=16, font_name="Times-Roman", color="#2E75B6")
    te.add_run(", sizes,", italic=True, size=13)
    te.add_run(" and ", size=14)
    te.add_run("colours", bold=True, size=17, color="#1B5E20")
    te.add_run(" in the same paragraph.", italic=True, size=12, color="#666666")

    te = slide[0, 1].text()
    te.add_block(alignment=TextAlignment.LEFT)
    te.add_run("Left-aligned paragraph.")
    te.add_block(alignment=TextAlignment.CENTER, spacing_before=16)
    te.add_run("Centred paragraph.\nSecond line centred.", size=14)
    te.add_block(alignment=TextAlignment.RIGHT, spacing_before=16)
    te.add_run("Right-aligned paragraph.", italic=True, size=13)
    te.add_block(alignment=TextAlignment.LEFT, spacing_before=24)
    te.add_run("Multi-line with\nforced line breaks\nand mixed ", size=13)
    te.add_run("bold", bold=True, size=13)
    te.add_run(" spans.", size=13)
    doc.add_slide(slide)

    # TEXTO — HAlign × VAlign combinations
    slide = Slide_content()
    slide.title.text = "Text — cell alignment (HAlign × VAlign)"
    slide.grid_layout(rows=3, cols=3, padding=Edges(left=18, right=18), gap=8)
    for r in range(3):
        for c in range(3):
            slide[r, c].background_color = "pink"
            ha = [HAlign.LEFT, HAlign.CENTER, HAlign.RIGHT][c]
            va = [VAlign.TOP, VAlign.MIDDLE, VAlign.BOTTOM][r]
            ta = [TextAlignment.LEFT, TextAlignment.CENTER, TextAlignment.RIGHT][c]
            label = f"{ha.value.upper()}\n{va.value.upper()}"
            slide[r, c].align(ha, va).text(label, size=11, color="#1F4E79",
                                           alignment=ta)
    doc.add_slide(slide)

    # TEXTO — lorem ipsum con HAlign × VAlign
    slide = Slide_content()
    slide.title.text = "Text — lorem ipsum (HAlign × VAlign)"
    slide.grid_layout(rows=3, cols=4, padding=Edges(left=18, right=18), gap=8)
    for r in range(1, 4):
        for c in range(4):
            slide[r - 1, c].background_color = "pink"
            ha = [HAlign.LEFT, HAlign.CENTER, HAlign.RIGHT, HAlign.STRETCH][c]
            va = [VAlign.TOP, VAlign.MIDDLE, VAlign.BOTTOM][r - 1]
            ta = TextAlignment.JUSTIFY if ha == HAlign.STRETCH else TextAlignment.LEFT
            label = (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
                "nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in "
                "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
                "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                "culpa qui officia deserunt mollit anim id est laborum."
            )
            slide[r - 1, c].align(ha, va).text(label, size=6, color="#1F4E79", alignment=ta)
    doc.add_slide(slide)

    # ---- TABLA: DataFrame sin formato vs TableSpec con formato ----
    slide = Slide_content()
    slide.title.text = "Tables — plain DataFrame vs styled TableSpec"
    slide.grid_layout(rows=1, cols=2, padding=Edges(left=24, right=24), gap=16)

    data = pd.DataFrame({
        "Item": ["Alpha", "Beta", "Gamma", "Delta"],
        "Value": [1234.567, 89.123, 4567.89, 12.34567],
        "Factor": [1.2345, 0.9876, 2.3456, 0.1234],
        "Count": [42, 137, 8, 256],
        "Price": [19.99, 249.50, 0.05, 1299.00],
    })

    # Left: plain DataFrame, no formatting at all
    slide[0, 0].table(data, zebra=False, header_style=False)

    # Right: TableSpec from same DataFrame with formatting.
    # NOTE: range("A1:...") addresses data rows only (header is auto-generated
    # from Column definitions). Style the header via TableStyle.
    ts = TableSpec.from_dataframe(data, style=TableStyle(
        header_background="#1F4E79",
        header_text_color="white",
    ))
    ts.range("A1:A4").style(bold=True)  # first column (data rows)
    ts.column("Value").set_format("{:.2f}")
    ts.column("Factor").set_format("{:.3f}")
    ts.column("Count").set_format("{:,.0f}")
    ts.column("Price").set_format("${:.2f}")
    ts.zebra()
    slide[0, 1].table_spec(ts)
    doc.add_slide(slide)

    # ---- TABLA: merged cells (colspan + rowspan) ----
    slide = Slide_content()
    slide.title.text = "Tables — merged cells (colspan & rowspan)"
    slide.grid_layout(rows=1, cols=1, padding=Edges(left=24, right=24))
    ts = TableSpec(
        style=TableStyle(header_rows=0, border_color="#333333", font_size=9),
    )
    ts.add_column("Division")
    ts.add_column("Project")
    ts.add_column("Q1")
    ts.add_column("Q2")
    # Title row: colspan across all 4 columns
    ts.add_row("", "", "", "")
    ts.cell(row=0, col=0, value="Consolidated Revenue Report (kEUR)",
            colspan=4, background_color="#1F4E79", text_color="white",
            style=CellStyle(bold=True, align_h="center", font_size=11))
    # Column headers
    ts.add_row("Division", "Project", "Q1", "Q2")
    ts.range("A2:D2").style(bold=True, background_color="#D9EAF7",
                             align_h="center")
    # Aero group — Division rowspan=2 covering Alpha + Beta
    ts.add_row("", "Alpha", 120, 135)
    ts.add_row("", "Beta", 95, 88)
    ts.cell(row=2, col=0, value="Aero", rowspan=2,
            background_color="#C6EFCE",
            style=CellStyle(bold=True, align_h="center", align_v="middle"))
    # Marine group — Division rowspan=2 covering Gamma + Delta
    ts.add_row("", "Gamma", 200, 180)
    ts.add_row("", "Delta", 55, 72)
    ts.cell(row=4, col=0, value="Marine", rowspan=2,
            background_color="#FFC7CE",
            style=CellStyle(bold=True, align_h="center", align_v="middle"))
    slide[0, 0].table_spec(ts)
    doc.add_slide(slide)

    # ---- TABLA: conditional formatting examples ----
    slide = Slide_content()
    slide.title.text = "Tables — conditional formatting"
    slide.grid_layout(rows=2, cols=2, padding=Edges(left=18, right=18), gap=12)

    # Top-left: highlight_max + highlight_min
    df1 = pd.DataFrame({
        "Sensor": ["T1", "T2", "T3", "T4", "T5"],
        "Temp (C)": [85, 92, 78, 105, 88],
        "Pressure (kPa)": [101.3, 98.7, 105.2, 95.0, 102.8],
        "Flow (kg/s)": [12.5, 11.8, 13.2, 10.5, 12.1],
    })
    ts1 = TableSpec.from_dataframe(df1,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=8))
    ts1.highlight_max("Temp (C)")
    ts1.highlight_min("Flow (kg/s)")
    ts1.zebra()
    slide[0, 0].table_spec(ts1)

    # Top-right: deferred heatmap (add_heatmap)
    df2 = pd.DataFrame({
        "Component": ["Blade A", "Blade B", "Disc", "Casing", "Seal"],
        "Max Stress (MPa)": [450, 520, 380, 290, 180],
        "Fatigue Life (cycles)": [12000, 8500, 22000, 45000, 60000],
        "Safety Factor": [1.8, 1.5, 2.2, 2.8, 3.5],
    })
    ts2 = TableSpec.from_dataframe(df2,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=8))
    ts2.add_heatmap("Max Stress (MPa)", min_color="#C6EFCE", max_color="#FFC7CE")
    ts2.add_heatmap("Safety Factor", min_color="#FFC7CE", max_color="#C6EFCE")
    ts2.zebra()
    slide[0, 1].table_spec(ts2)

    # Bottom-left: custom conditions (add_condition)
    df3 = pd.DataFrame({
        "Test": ["Run-1", "Run-2", "Run-3", "Run-4", "Run-5"],
        "Efficiency (%)": [94.2, 97.1, 91.5, 88.3, 96.8],
        "Vibration (mm/s)": [0.12, 0.08, 0.45, 0.92, 0.15],
        "Status": ["Pass", "Pass", "Warning", "Fail", "Pass"],
    })
    ts3 = TableSpec.from_dataframe(df3,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=8))
    ts3.add_condition("Efficiency (%)", lambda v: v < 90, background_color="#FFC7CE")
    ts3.add_condition("Efficiency (%)", lambda v: v >= 95, background_color="#C6EFCE")
    ts3.add_condition("Vibration (mm/s)", lambda v: v > 0.5, background_color="#FFC7CE")
    ts3.add_condition("Vibration (mm/s)", lambda v: v <= 0.15, background_color="#C6EFCE")
    ts3.add_condition("Status", lambda v: v == "Fail", background_color="#FFC7CE", text_color="#9C0006")
    ts3.add_condition("Status", lambda v: v == "Warning", background_color="#FFEB9C")
    ts3.zebra()
    slide[1, 0].table_spec(ts3)

    # Bottom-right: extremes + heatmap combined
    df4 = pd.DataFrame({
        "Machine": ["Comp-1", "Comp-2", "Turb-1", "Turb-2", "Fan-1"],
        "Power (kW)": [2500, 2300, 4200, 3900, 1800],
        "Efficiency": [0.88, 0.92, 0.94, 0.91, 0.85],
        "Temp Rise (C)": [45, 38, 52, 48, 32],
    })
    ts4 = TableSpec.from_dataframe(df4,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=8))
    ts4.add_highlight_max("Power (kW)")
    ts4.add_highlight_min("Temp Rise (C)")
    ts4.add_heatmap("Efficiency")
    ts4.zebra()
    slide[1, 1].table_spec(ts4)
    doc.add_slide(slide)

    # ---- Conditional formatting con auto_fit_header ----
    slide = Slide_content()
    slide.title.text = "Tables — conditional formatting + auto_fit_header"
    slide.grid_layout(rows=2, cols=2, padding=Edges(left=18, right=18), gap=14)

    # Top-left: highlight_max + highlight_min with long column names
    df1 = pd.DataFrame({
        "Sensor": ["T1", "T2", "T3", "T4", "T5"],
        "Temperature (Celsius)": [85, 92, 78, 105, 88],
        "Pressure (kPa abs)": [101.3, 98.7, 105.2, 95.0, 102.8],
        "Mass Flow Rate (kg/s)": [12.5, 11.8, 13.2, 10.5, 12.1],
    })
    ts1 = TableSpec.from_dataframe(df1,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=11))
    ts1.highlight_max("Temperature (Celsius)")
    ts1.highlight_min("Mass Flow Rate (kg/s)")
    ts1.zebra()
    slide[0, 0].table_spec(ts1)

    # Top-right: same data + config but with auto_fit_header
    df1b = pd.DataFrame({
        "Sensor": ["T1", "T2", "T3", "T4", "T5"],
        "Temperature (Celsius)": [85, 92, 78, 105, 88],
        "Pressure (kPa abs)": [101.3, 98.7, 105.2, 95.0, 102.8],
        "Mass Flow Rate (kg/s)": [12.5, 11.8, 13.2, 10.5, 12.1],
    })
    ts1b = TableSpec.from_dataframe(df1b,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=11))
    ts1b.highlight_max("Temperature (Celsius)")
    ts1b.highlight_min("Mass Flow Rate (kg/s)")
    ts1b.zebra()
    ts1b.sizing = TableSizing(
        fit_mode=TableFitMode.STRETCH,
        column_distrib=ColumnDistrib.EQUAL,
        auto_fit_header=True,
    )
    slide[0, 1].table_spec(ts1b)

    # Bottom-left: heatmap + deferred extremes with verbose headers
    df2 = pd.DataFrame({
        "Component ID": ["Blade A", "Blade B", "Disc", "Casing", "Seal"],
        "Max Principal Stress (MPa)": [450, 520, 380, 290, 180],
        "Fatigue Life (thousand cycles)": [12.0, 8.5, 22.0, 45.0, 60.0],
        "Safety Factor (—)": [1.8, 1.5, 2.2, 2.8, 3.5],
    })
    ts2 = TableSpec.from_dataframe(df2,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=11))
    ts2.add_heatmap("Max Principal Stress (MPa)", min_color="#C6EFCE", max_color="#FFC7CE")
    ts2.add_highlight_min("Fatigue Life (thousand cycles)")
    ts2.zebra()
    ts2.sizing = TableSizing(
        fit_mode=TableFitMode.STRETCH,
        column_distrib=ColumnDistrib.EQUAL,
        auto_fit_header=True,
    )
    slide[1, 0].table_spec(ts2)

    # Bottom-right: all effects + auto_fit_header
    df3 = pd.DataFrame({
        "Machine Unit": ["Comp-1", "Comp-2", "Turb-1", "Turb-2", "Fan-1"],
        "Shaft Power (kW)": [2500, 2300, 4200, 3900, 1800],
        "Isentropic Efficiency": [0.88, 0.92, 0.94, 0.91, 0.85],
        "Temperature Rise (deg C)": [45, 38, 52, 48, 32],
    })
    ts3 = TableSpec.from_dataframe(df3,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=11))
    ts3.add_highlight_max("Shaft Power (kW)")
    ts3.add_highlight_min("Temperature Rise (deg C)")
    ts3.add_heatmap("Isentropic Efficiency")
    ts3.zebra()
    ts3.sizing = TableSizing(
        fit_mode=TableFitMode.STRETCH,
        column_distrib=ColumnDistrib.EQUAL,
        auto_fit_header=True,
    )
    slide[1, 1].table_spec(ts3)
    doc.add_slide(slide)

    # ---- HEADER WRAPPING (instead of shrinking) ----
    slide = Slide_content()
    slide.title.text = "Tables — header_wrap (word-break long headers)"
    slide.grid_layout(rows=2, cols=2, padding=Edges(left=18, right=18), gap=14)

    # Top-left: NO wrapping (control — headers will overflow)
    df1 = pd.DataFrame({
        "Sensor": ["T1", "T2", "T3", "T4", "T5"],
        "Temperature (Celsius)": [85, 92, 78, 105, 88],
        "Pressure (kPa absolute)": [101.3, 98.7, 105.2, 95.0, 102.8],
        "Mass Flow Rate (kg/s)": [12.5, 11.8, 13.2, 10.5, 12.1],
    })
    ts1 = TableSpec.from_dataframe(df1,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=10))
    ts1.zebra()
    ts1.sizing = TableSizing(
        fit_mode=TableFitMode.STRETCH,
        column_distrib=ColumnDistrib.EQUAL,
    )
    slide[0, 0].table_spec(ts1)

    # Top-right: same data WITH header_wrap
    ts1w = TableSpec.from_dataframe(df1,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=10))
    ts1w.zebra()
    ts1w.sizing = TableSizing(
        fit_mode=TableFitMode.STRETCH,
        column_distrib=ColumnDistrib.EQUAL,
        header_wrap=True,
    )
    slide[0, 1].table_spec(ts1w)

    # Bottom-left: conditional formatting + header_wrap
    df2 = pd.DataFrame({
        "Component ID": ["Blade A", "Blade B", "Disc", "Casing", "Seal"],
        "Max Principal Stress (MPa)": [450, 520, 380, 290, 180],
        "Fatigue Life (thousand cycles)": [12.0, 8.5, 22.0, 45.0, 60.0],
        "Safety Factor (—)": [1.8, 1.5, 2.2, 2.8, 3.5],
    })
    ts2 = TableSpec.from_dataframe(df2,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=10))
    ts2.add_heatmap("Max Principal Stress (MPa)", min_color="#C6EFCE", max_color="#FFC7CE")
    ts2.add_highlight_min("Fatigue Life (thousand cycles)")
    ts2.zebra()
    ts2.sizing = TableSizing(
        fit_mode=TableFitMode.STRETCH,
        column_distrib=ColumnDistrib.EQUAL,
        header_wrap=True,
    )
    slide[1, 0].table_spec(ts2)

    # Bottom-right: extremes + heatmap + header_wrap
    df3 = pd.DataFrame({
        "Machine Unit": ["Comp-1", "Comp-2", "Turb-1", "Turb-2", "Fan-1"],
        "Shaft Power (kW)": [2500, 2300, 4200, 3900, 1800],
        "Isentropic Efficiency": [0.88, 0.92, 0.94, 0.91, 0.85],
        "Temperature Rise (deg C)": [45, 38, 52, 48, 32],
    })
    ts3 = TableSpec.from_dataframe(df3,
        style=TableStyle(header_background="#2E75B6", header_text_color="white", font_size=10))
    ts3.add_highlight_max("Shaft Power (kW)")
    ts3.add_highlight_min("Temperature Rise (deg C)")
    ts3.add_heatmap("Isentropic Efficiency")
    ts3.zebra()
    ts3.sizing = TableSizing(
        fit_mode=TableFitMode.STRETCH,
        column_distrib=ColumnDistrib.EQUAL,
        header_wrap=True,
    )
    slide[1, 1].table_spec(ts3)
    doc.add_slide(slide)

    out = OUT_DIR / "prueba"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")

if __name__ == "__main__":
    main()
