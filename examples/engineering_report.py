"""Engineering report example — CFD/FEM style report with matplotlib and pandas, generates PDF, HTML, PPTX."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer
from reporting.renderers.pptx.renderer import PPTXRenderer


def create_pressure_plot() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(5, 3))
    x = np.linspace(0, 1, 100)
    y = np.sin(2 * np.pi * x) * np.exp(-x)
    ax.plot(x, y, label="Pressure coefficient")
    ax.set_xlabel("x/c")
    ax.set_ylabel("Cp")
    ax.set_title("Pressure Distribution")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return fig


def main() -> None:
    doc = Document(title="CFD Analysis Report", author="Aero Team")

    slide = Slide("CFD Results - Pressure Distribution")
    slide.grid_layout(rows=1, cols=2, gap=20, padding=Edges.all(20))
    fig = create_pressure_plot()
    slide[0, 0].plot(fig, format="pdf")
    slide[0, 1].text("Convergence achieved at iteration 250.\nTarget lift within 2%.", size=10)
    doc.add_slide(slide)

    out = Path(__file__).parent / "engineering_report"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    PPTXRenderer().render_document(doc, str(out) + ".pptx")
    print("Generated engineering_report.{pdf,html,pptx}")


if __name__ == "__main__":
    main()
