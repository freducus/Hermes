from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
from reporting.tablespec import TableSpec
from reporting.styles.colors import NAMED_COLORS, Color, ColorPalette
from reporting.background import SolidBackground, GradientBackground, ImageBackground
from reporting.title_config import TitleText, SubtitleText, TitlePanel

OUT_DIR = Path(__file__).parent


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

_CORPORATE_PALETTE = ColorPalette(
    primary=Color.from_hex("#1F4E79"),
    secondary=Color.from_hex("#2E75B6"),
    accent=Color.from_hex("#ED7D31"),
    background_title=Color.from_hex("#0042ED"),
    background_content=Color.from_hex("#FFFFFF"),
    text_primary=Color.from_hex("#333333"),
    text_secondary=Color.from_hex("#666666"),
    border=Color.from_hex("#D9D9D9"),
    error=Color.from_hex("#C00000"),
    warning=Color.from_hex("#FFC000"),
    success=Color.from_hex("#70AD47"),
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
            name="Corporate",
            palette=_CORPORATE_PALETTE,
            typography=_CORPORATE_TYPOGRAPHY,
        )

class Slide_title(Slide):
    def __init__(self) -> None:
        super().__init__(theme=CompanyTheme())
        self.setup()

    def setup(self):
        self.background = SolidBackground(color=self.theme.palette.background_title)

        self.grid_layout(rows=1, cols=2, col_sizes=[Percent(60), Percent(40)], padding=Edges.all(25), gap=12)

        self.inner_grid = inner_grid = Grid(rows=3, cols=1, row_sizes=[Percent(50), Percent(25), Percent(25)], padding=Edges(12,0,0,0))

        inner_grid[0,0].align(HAlign.LEFT, VAlign.BOTTOM)

        inner_grid[1, 0].align(HAlign.LEFT, VAlign.TOP)

        disclaimer_grid = Grid(rows=1, cols=2, col_sizes=[Percent(90), Percent(10)])
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

        self[0, 1].align(HAlign.STRETCH, VAlign.STRETCH)
        self[0, 1].image(create_logo())

        self.set_title("Título")
        self.set_subtitle('Subtítulo')

    def set_title(self, title: str) -> None:
        self.inner_grid[0, 0].text(title, style='heading_1', color=NAMED_COLORS['white'])

    def set_subtitle(self, subtitle: str) -> None:
        self.inner_grid[1, 0].text(subtitle, style='heading_2', color=NAMED_COLORS['white'])

def main() -> None:
    doc = Document(title="Comprehensive Report", author="pyreportengine Demo")
    LOGO_PATH = create_logo()

    # ---- Slide 1: Typography showcase ----
    slide = Slide_title()
    slide.set_title('T')
    slide.set_subtitle('ST')

    # slide.grid_layout(rows=1, cols=2)
    # slide[0,0].plot(create_plot("Typography Showcase"))
    # grid = Grid(rows=2, cols=1, row_sizes=[Percent(60), Percent(40)])
    # slide[0,1].grid_layout(grid)
    # grid[0,0].plot(create_plot("Typography Showcase"))
    # grid[1,0].plot(create_plot("Typography Showcase"))
    doc.add_slide(slide)

    out = OUT_DIR / "prueba"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")

if __name__ == "__main__":
    main()

