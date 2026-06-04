"""Theme demo — demonstrates different themes with fonts, colors, and tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from reporting.document import Document
from reporting.slide import Slide
from reporting.styles.theme import CorporateTheme, DarkTheme, LightTheme
from reporting.renderers.pdf.renderer import PDFRenderer


def _build_theme_slide(name: str, theme) -> Slide:
    slide = Slide(f"{name} Theme", theme=theme)
    slide.grid_layout(rows=1, cols=3, gap=8)

    pal = theme.palette

    # --- Left: font samples ---
    h1 = theme.typography.heading_1
    body = theme.typography.body
    h2 = theme.typography.heading_2
    slide[0, 0].text(
        f"Fonts: {h1.family} / {body.family}\n"
        f"heading_1: {h1.family} size={h1.size}"
        f"{' bold' if h1.bold else ''}{' italic' if h1.italic else ''}\n"
        f"heading_2: {h2.family} size={h2.size}"
        f"{' bold' if h2.bold else ''}{' italic' if h2.italic else ''}\n"
        f"body:      {body.family} size={body.size}"
        f"{' bold' if body.bold else ''}{' italic' if body.italic else ''}",
        size=9,
        color=pal.text_secondary.css,
    )
    # body text in the theme's body font
    slide[0, 0].text(
        f"This is {name} body text — regular weight.",
        size=body.size,
        bold=body.bold,
        italic=body.italic,
        color=pal.text_primary.css,
    )
    slide[0, 0].text(
        "Bold weight text in the heading_2 font.",
        size=h2.size,
        bold=True,
        color=pal.primary.css,
    )
    slide[0, 0].text(
        "Italic styled text for emphasis.",
        size=body.size,
        italic=True,
        color=pal.text_secondary.css,
    )
    slide[0, 0].text(
        "Bold + italic combined.",
        size=body.size,
        bold=True,
        italic=True,
        color=pal.primary.css,
    )

    # --- Center: color swatches ---
    slide[0, 1].text("Color Palette", bold=True, size=h2.size, color=pal.text_primary.css)
    slide[0, 1].text(
        f"■ primary        #{pal.primary.hex.lstrip('#')}\n"
        f"■ background     #{pal.background.hex.lstrip('#')}\n"
        f"■ text_primary   #{pal.text_primary.hex.lstrip('#')}\n"
        f"■ text_secondary #{pal.text_secondary.hex.lstrip('#')}\n"
        f"■ border         #{pal.border.hex.lstrip('#')}",
        size=9,
        color=pal.text_secondary.css,
    )

    # --- Right: table with theme styling ---
    df = pd.DataFrame({
        "Property": ["Primary", "Body Font", "Table Header"],
        "Value": [pal.primary.css, body.family, "Styled"],
        "Notes": [f"#{pal.primary.hex}", f"size={body.size}", "zebra rows"],
    })
    slide[0, 2].table(df, zebra=True)

    return slide


def main() -> None:
    doc = Document(title="Theme Demo", author="Design Team")

    themes = {
        "Corporate": CorporateTheme(),
        "Dark": DarkTheme(),
        "Light": LightTheme(),
    }

    for name, theme in themes.items():
        doc.add_slide(_build_theme_slide(name, theme))

    out = Path(__file__).parent / "theme_demo"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated theme_demo.pdf")


if __name__ == "__main__":
    main()
