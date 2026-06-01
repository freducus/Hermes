"""Dashboard report example — multi-panel layout with tables and plots, generates PDF, HTML, PPTX."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer
from reporting.renderers.pptx.renderer import PPTXRenderer


def create_plot(title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(3, 2))
    x = np.linspace(0, 10, 50)
    y = np.sin(x) * np.exp(-x / 5)
    ax.plot(x, y)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    return fig


def main() -> None:
    doc = Document(title="Performance Dashboard", author="Engineering")

    slide = Slide("KPIs Overview")
    slide.grid_layout(rows=2, cols=5, gap=8, padding=Edges.all(15))

    slide[0, 0].plot(create_plot("Efficiency"), format="pdf")
    slide[0, 1].plot(create_plot("Power Output"), format="pdf")
    slide[0, 2].plot(create_plot("Temperature"), format="pdf")

    data = pd.DataFrame({
        "Parameter": ["Efficiency", "Power", "Temp", "Pressure"],
        "Value": [94.5, 250.0, 85.3, 101.3],
        "Status": ["Pass", "Pass", "Warning", "Pass"],
    })
    slide[1, 0:2].table(data, zebra=True)
    doc.add_slide(slide)

    out = Path(__file__).parent / "dashboard_report"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    PPTXRenderer().render_document(doc, str(out) + ".pptx")
    print("Generated dashboard_report.{pdf,html,pptx}")


if __name__ == "__main__":
    main()
