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
    slide.grid_layout(rows=7, cols=3, gap=6)

    pal = theme.palette
    h1 = theme.typography.heading_1
    body = theme.typography.body
    h2 = theme.typography.heading_2

    # --- Column 0: font samples (one row per variant) ---
    # Row 0 — font info
    slide[0, 0].text(
        f"heading_1: {h1.family} size={h1.size}"
        f"{' bold' if h1.bold else ''}{' italic' if h1.italic else ''}\n"
        f"heading_2: {h2.family} size={h2.size}"
        f"{' bold' if h2.bold else ''}{' italic' if h2.italic else ''}\n"
        f"body:      {body.family} size={body.size}"
        f"{' bold' if body.bold else ''}{' italic' if body.italic else ''}",
        font_name=body.family,
        size=9,
        color=pal.text_secondary.css,
    )
    # Row 1 — body text in theme body font
    slide[1, 0].text(
        f"{name} body — regular weight.",
        font_name=body.family,
        size=body.size,
        bold=body.bold,
        italic=body.italic,
        color=pal.text_primary.css,
    )
    # Row 2 — bold weight
    slide[2, 0].text(
        "Bold weight in heading_2 font.",
        font_name=h2.family,
        size=h2.size,
        bold=True,
        color=pal.primary.css,
    )
    # Row 3 — italic
    slide[3, 0].text(
        "Italic styled for emphasis.",
        font_name=body.family,
        size=body.size,
        italic=True,
        color=pal.text_secondary.css,
    )
    # Row 4 — bold + italic
    slide[4, 0].text(
        "Bold + italic combined.",
        font_name=body.family,
        size=body.size,
        bold=True,
        italic=True,
        color=pal.primary.css,
    )
    # Row 5 — caption
    if theme.typography.caption:
        cap = theme.typography.caption
        slide[5, 0].text(
            f"Caption ({cap.family} size={cap.size})",
            size=cap.size,
            color=cap.color or pal.text_secondary.css,
        )
    # Row 6 — code font
    if theme.typography.code:
        code = theme.typography.code
        slide[6, 0].text(
            f"Code: print('hello')  # {code.family}",
            size=code.size,
            color=code.color or pal.text_secondary.css,
        )

    # --- Column 1: color palette ---
    slide[0, 1].text("Color Palette", bold=True, size=h2.size, color=pal.text_primary.css)
    slide[1, 1].text(
        f"■ primary        #{pal.primary.hex.lstrip('#')}\n"
        f"■ background     #{pal.background.hex.lstrip('#')}\n"
        f"■ text_primary   #{pal.text_primary.hex.lstrip('#')}\n"
        f"■ text_secondary #{pal.text_secondary.hex.lstrip('#')}\n"
        f"■ border         #{pal.border.hex.lstrip('#')}",
        size=9,
        color=pal.text_secondary.css,
    )
    # Fill remaining palette rows with empty text to keep layout clean
    for r in range(2, 7):
        slide[r, 1].text("")

    # --- Column 2: table with theme styling ---
    df = pd.DataFrame({
        "Property": ["Primary", "Body Font", "Table Header"],
        "Value": [pal.primary.css, body.family, "Styled"],
        "Notes": [f"#{pal.primary.hex.lstrip('#')}", f"size={body.size}", "zebra rows"],
    })
    slide[0:7, 2].table(df, zebra=True)

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
