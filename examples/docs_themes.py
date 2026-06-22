"""Built-in themes, custom theme creation.

Used by docs 07_themes.rst.
"""

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.styles.theme import CorporateTheme, DarkTheme, LightTheme, Theme
from reporting.styles.colors import ColorPalette, Color
from reporting.styles.typography import Typography, FontSpec
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer

OUT_DIR = Path(__file__).parent


class OceanTheme(Theme):
    """Custom ocean-themed palette (teal/blue on light cyan)."""

    def __init__(self) -> None:
        super().__init__(
            name="Ocean",
            palette=ColorPalette(
                primary=Color.from_hex("#006994"),
                secondary=Color.from_hex("#00B4D8"),
                accent=Color.from_hex("#FF6B35"),
                background=Color.from_hex("#E0F7FA"),
                text_primary=Color.from_hex("#003B5C"),
                text_secondary=Color.from_hex("#0077B6"),
                border=Color.from_hex("#90E0EF"),
                error=Color.from_hex("#C00000"),
                warning=Color.from_hex("#FFC000"),
                success=Color.from_hex("#2E7D32"),
            ),
            typography=Typography(
                heading_1=FontSpec("Helvetica", 28, bold=True, color="#006994"),
                heading_2=FontSpec("Helvetica", 22, bold=True, color="#00B4D8"),
                body=FontSpec("Helvetica", 11, color="#003B5C"),
                caption=FontSpec("Helvetica", 9, italic=True, color="#0077B6"),
            ),
        )


def main() -> None:
    doc = Document("Themes Demo", author="Docs")

    # ---- Slide 1: Corporate theme ----
    slide1 = Slide(theme=CorporateTheme())
    slide1.title = "Corporate Theme"
    slide1.subtitle = "Default theme (blue/grey, Arial)"
    slide1.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide1[0, 0].text(
        "This slide uses the built-in CorporateTheme.\n"
        "Blue/grey palette, Arial fonts, white background.",
        style="body",
    )
    doc.add_slide(slide1)

    # ---- Slide 2: Dark theme ----
    slide2 = Slide(theme=DarkTheme())
    slide2.title = "Dark Theme"
    slide2.subtitle = "Dark background, light text, blue accents"
    slide2.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide2[0, 0].text(
        "This slide uses the built-in DarkTheme.\n"
        "Dark background (#1E1E1E), light text, Helvetica.",
        style="body",
    )
    doc.add_slide(slide2)

    # ---- Slide 3: Light theme ----
    slide3 = Slide(theme=LightTheme())
    slide3.title = "Light Theme"
    slide3.subtitle = "Soft blue on near-white background"
    slide3.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide3[0, 0].text(
        "This slide uses the built-in LightTheme.\n"
        "Blue on #FAFAFA background, Helvetica.",
        style="body",
    )
    doc.add_slide(slide3)

    # ---- Slide 4: OceanTheme — custom theme with layouts and slide types ----
    slide4 = Slide(theme=OceanTheme())
    slide4.title = "Ocean Theme"
    slide4.subtitle = "Teal/blue palette, Helvetica, custom slide types"
    slide4[0, 0].text(
        "This slide uses a fully custom theme:\n"
        "- Custom ColorPalette (teal/blue/orange)\n"
        "- Named LayoutConfig layouts\n"
        "- Custom SlideTypeConfig variants\n"
        "- @Theme.register('ocean') for name-based lookup\n"
        "- SolidBackground from palette",
        style="body",
    )
    doc.add_slide(slide4)

    # ---- Slide 5: Ocean theme ----
    slide5 = Slide(theme=OceanTheme())
    slide5.title = "Ocean Theme"
    slide5.grid_layout(rows=3, cols=2, gap=8, padding=Edges.all(20))
    slide5[1, 0].text("Manually added cell", style="body")
    slide5[1, 1].text("Extra content", style="body")
    slide5[2, :].text("Spans both columns", style="body")
    doc.add_slide(slide5)

    # ---- Slide 6: Ocean theme ----
    slide6 = Slide(theme=OceanTheme())
    slide6.title = "Ocean by Name"
    slide6.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide6[0, 0].text(
        "Themes can be created directly as Theme subclasses\n"
        "and applied via theme=OceanTheme().",
        style="body",
    )
    doc.add_slide(slide6)

    # ---- Slide 7: Theme via Document ----
    slide7 = Slide(theme=DarkTheme())
    slide7.title = "Theme via Document"
    slide7.subtitle = "Pass theme= to Slide and let slides inherit"
    slide7.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide7[0, 0].text(
        "When a theme is set on a Slide, it inherits\n"
        "the theme's palette and typography.\n\n"
        "slide = Slide(theme=DarkTheme())",
        style="body",
    )
    doc.add_slide(slide7)

    out = OUT_DIR / "docs_themes"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_themes.pdf and docs_themes.html")


if __name__ == "__main__":
    main()
