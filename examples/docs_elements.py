"""Element types — used by docs 02_elements.rst."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.layout.grid import Grid
from reporting.elements.text import TextElement
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer

OUT_DIR = Path(__file__).parent


def _create_logo() -> str:
    """Generate a small logo PNG for the image example."""
    path = OUT_DIR / "_docs_elements_logo.png"
    if path.exists():
        return str(path)
    fig, ax = plt.subplots(figsize=(0.6, 0.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.5)
    ax.set_facecolor("none")
    ax.text(0.02, 0.25, "PE", fontsize=16, fontweight="bold",
            color="#1565C0", va="center", ha="left")
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=96, bbox_inches="tight", pad_inches=0,
                transparent=True)
    plt.close(fig)
    return str(path)


def _create_plot() -> plt.Figure:
    """Create a sample matplotlib figure."""
    fig, ax = plt.subplots(figsize=(3.5, 1.8))
    x = np.linspace(0, 10, 50)
    ax.plot(x, np.sin(x), label="sin(x)", color="#1565C0")
    ax.plot(x, np.cos(x), label="cos(x)", color="#C62828")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(fontsize=8)
    ax.set_title("Trigonometric functions", fontsize=10)
    fig.tight_layout()
    return fig


def main() -> None:
    doc = Document("Element Types Demo", author="Docs")

    slide = Slide()
    slide.title = "Element Types"
    slide.subtitle = "Text, Figure, Image, Table, Container"
    slide.grid_layout(rows=3, cols=2, gap=12, padding=Edges.all(20))

    # 1. TextElement — simple and mixed-format
    te = slide[0, 0].text(
        "Text with style",
        style="h1",
    )

    te.add_run(" and mixed-format: ")
    te.add_run("bold", bold=True)
    te.add_run(", ")
    te.add_run("italic", italic=True)
    te.add_run(", ")
    te.add_run("colored", color="#C62828")

    # 2. FigureElement — matplotlib plot
    fig = _create_plot()
    slide[0, 1].plot(fig, format="png", dpi=120, preserve_aspect=True)

    # 3. ImageElement — from file
    logo_path = _create_logo()
    slide[1, 0].image(logo_path, scale=1.5)

    # 4. TableElement — pandas DataFrame with zebra
    df = pd.DataFrame({
        "Metric": ["Alpha", "Beta", "Gamma"],
        "Value": [12.3, 45.6, 78.9],
        "Status": ["OK", "WARN", "OK"],
    })
    slide[1, 1].table(df, zebra=True, include_index=False)

    # 5. ContainerElement — nested sub-grid
    inner = Grid(rows=2, cols=1, gap=6)
    inner[0, 0].text("Sub-grid top cell")
    inner[1, 0].text(
        "Sub-grid bottom cell with\nmultiple lines",
        size=9, color="#666666",
    )
    slide[2, :].grid_layout(inner)

    doc.add_slide(slide)

    out = OUT_DIR / "docs_elements"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_elements.pdf and docs_elements.html")


if __name__ == "__main__":
    main()


