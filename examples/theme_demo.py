"""Theme demo — demonstrates different themes, generates PDF, HTML, PPTX."""

from __future__ import annotations

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.styles.theme import CorporateTheme, DarkTheme, LightTheme
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="Theme Demo", author="Design Team")

    themes = {
        "Corporate": CorporateTheme(),
        "Dark": DarkTheme(),
        "Light": LightTheme(),
    }

    for name, theme in themes.items():
        slide = Slide(f"{name} Theme", theme=theme)
        slide.grid_layout(rows=1, cols=2, gap=10)
        slide[0, 0].text(f"This slide uses the {name} theme")
        slide[0, 1].text("Content area with theme styling applied.")
        doc.add_slide(slide)

    out = Path(__file__).parent / "theme_demo"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated theme_demo.pdf")


if __name__ == "__main__":
    main()
