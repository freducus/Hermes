"""Image embedding demo — external PNG/JPG with fit modes, scale, rotation.

Generates its own test images via matplotlib, then embeds them to
demonstrate the ``Panel.image()`` API.
"""

from __future__ import annotations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.layout.panel import HAlign, VAlign
from reporting.elements.image import ImageFitMode
from reporting.renderers.pdf.renderer import PDFRenderer


def _make_image(path: Path, kind: str = "chart") -> None:
    """Generate a test image and save to *path*."""
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)

    if kind == "chart":
        cats = ["A", "B", "C", "D", "E"]
        vals = [3, 7, 2, 9, 5]
        bars = ax.bar(cats, vals, color=["#4472C4", "#70AD47", "#FFC000", "#ED7D31", "#5B9BD5"])
        ax.set_title("Bar Chart", fontsize=10, fontweight="bold")
        ax.set_ylim(0, 11)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    str(v), ha="center", va="bottom", fontsize=8)
    elif kind == "photo":
        x = np.linspace(0, 4 * np.pi, 300)
        y = np.sin(x) * np.exp(-x / 6)
        ax.plot(x, y, color="#4472C4", linewidth=2)
        ax.fill_between(x, y, alpha=0.15, color="#4472C4")
        ax.set_title("Damped Sine Wave", fontsize=10, fontweight="bold")
        ax.set_xlabel("Time")
        ax.set_ylabel("Amplitude")
    elif kind == "palette":
        colours = ["#4472C4", "#70AD47", "#FFC000", "#ED7D31", "#5B9BD5",
                   "#264478", "#375623", "#806000", "#772200", "#2E4A7A"]
        for i, c in enumerate(colours):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=c))
            ax.text(i + 0.5, 0.5, c, ha="center", va="center",
                    fontsize=7, color="white" if i < 6 else "black")
        ax.set_xlim(0, len(colours))
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title("Colour Palette", fontsize=10, fontweight="bold")

    fig.tight_layout(pad=1)
    fig.savefig(str(path), dpi=100, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    out_dir = Path(__file__).parent
    assets = out_dir / "_images"
    assets.mkdir(exist_ok=True)

    # --- generate test images ---
    chart_png = assets / "chart.png"
    wave_png = assets / "wave.png"
    palette_png = assets / "palette.png"

    _make_image(chart_png, "chart")
    _make_image(wave_png, "photo")
    _make_image(palette_png, "palette")

    doc = Document("Image Embedding Demo", author="pyreportengine")

    # ─── Slide 1 — Basic image embedding ───────────────────────────────
    s1 = Slide("Basic Image Embedding")
    s1.grid_layout(rows=2, cols=3, gap=8, padding=Edges.all(6))

    s1[0, 0].text("Original size", bold=True, size=11)
    s1[0, 0].image(str(chart_png))

    s1[0, 1].text("Scale 0.5", bold=True, size=11)
    s1[0, 1].image(str(chart_png), scale=0.5)

    s1[0, 2].text("Scale 1.5", bold=True, size=11)
    s1[0, 2].image(str(chart_png), scale=1.5)

    s1[1, 0].text("Fit vertical", bold=True, size=11)
    s1[1, 0].image(str(wave_png), fit_mode=ImageFitMode.FIT_VERTICAL)

    s1[1, 1].text("Fit horizontal", bold=True, size=11)
    s1[1, 1].image(str(wave_png), fit_mode=ImageFitMode.FIT_HORIZONTAL)

    s1[1, 2].text("Rotation 45°", bold=True, size=11)
    s1[1, 2].image(str(palette_png), rotation=45)

    doc.add_slide(s1)

    # ─── Slide 2 — Alignment and explicit sizing ───────────────────────
    s2 = Slide("Alignment & Explicit Sizing")
    s2.grid_layout(rows=2, cols=3, gap=8, padding=Edges.all(6))

    s2[0, 0].text("Left / Top", bold=True, size=11)
    s2[0, 0].align(HAlign.LEFT, VAlign.TOP).image(str(chart_png), scale=0.6)

    s2[0, 1].text("Center / Middle", bold=True, size=11)
    s2[0, 1].align(HAlign.CENTER, VAlign.MIDDLE).image(str(chart_png), scale=0.6)

    s2[0, 2].text("Right / Bottom", bold=True, size=11)
    s2[0, 2].align(HAlign.RIGHT, VAlign.BOTTOM).image(str(chart_png), scale=0.6)

    s2[1, 0].text("Width=120pt", bold=True, size=11)
    s2[1, 0].image(str(wave_png), width=120)

    s2[1, 1].text("Height=80pt", bold=True, size=11)
    s2[1, 1].image(str(wave_png), height=80)

    s2[1, 2].text("Width=150, Height=60", bold=True, size=11)
    s2[1, 2].image(str(wave_png), width=150, height=60)

    doc.add_slide(s2)

    # ─── Slide 3 — Opacity and composition ─────────────────────────────
    s3 = Slide("Opacity & Composition")
    s3.grid_layout(rows=2, cols=3, gap=8, padding=Edges.all(6))

    s3[0, 0].text("Opacity 0.3", bold=True, size=11)
    s3[0, 0].image(str(palette_png), opacity=0.3)

    s3[0, 1].text("Opacity 0.6", bold=True, size=11)
    s3[0, 1].image(str(palette_png), opacity=0.6)

    s3[0, 2].text("Opacity 1.0 (default)", bold=True, size=11)
    s3[0, 2].image(str(palette_png), opacity=1.0)

    s3[1, :].text(
        "Images can be combined with text, tables, and plots in the same grid. "
        "Use Panel.image() for external assets and Panel.plot() for matplotlib figures.",
        size=10,
    )

    doc.add_slide(s3)

    # ─── render ────────────────────────────────────────────────────────
    out = out_dir / "image_demo"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated image_demo.pdf")


if __name__ == "__main__":
    main()
