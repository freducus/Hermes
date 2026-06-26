"""Built-in themes, custom theme creation & registration.

Used by docs 07_themes.rst.
"""

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.footer_config import FooterPanel
from reporting.layout.geometry import Edges
from reporting.styles.theme import CorporateTheme, DarkTheme, LightTheme, Theme
from reporting.styles.colors import ColorPalette, Color
from reporting.styles.typography import Typography, FontSpec
from reporting.tablespec.style import TableStyle
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer

OUT_DIR = Path(__file__).parent


@Theme.register("ocean")
class OceanTheme(Theme):
    """Custom ocean-themed palette (teal/blue on light cyan)."""

    def __init__(self) -> None:
        palette = ColorPalette(
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
        )
        typography = Typography(
            heading_1=FontSpec("Helvetica", 28, bold=True, color="#006994"),
            heading_2=FontSpec("Helvetica", 22, bold=True, color="#00B4D8"),
            body=FontSpec("Helvetica", 11, color="#003B5C"),
            caption=FontSpec("Helvetica", 9, italic=True, color="#0077B6"),
        )
        table_style = TableStyle()

        footer = FooterPanel(
            enabled=True, separator_color=palette.border.css,
            font_name=typography.caption.family,
            font_size=typography.caption.size,
            color=palette.text_secondary.css,
            center_text="Ocean Report",
        )
        super().__init__(
            name="Ocean",
            page_size=(960, 540),
            palette=palette,
            typography=typography,
            table_style=table_style,
            footer_panel=footer,
        )


def main() -> None:
    doc = Document("Themes Demo", author="Docs")

    # ---- Slide 1: Corporate theme ----
    slide1 = Slide(
        "Corporate Theme",
        subtitle="Default theme (blue/grey, Arial)",
        theme=CorporateTheme(),
        footer_panel=FooterPanel(center_text="Corporate | Docs"),
    )
    slide1.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide1[0, 0].text(
        "This slide uses the built-in CorporateTheme.\n"
        "Blue/grey palette, Arial fonts, white background.",
        style="body",
    )
    doc.add_slide(slide1)

    # ---- Slide 2: Dark theme ----
    slide2 = Slide(
        "Dark Theme",
        subtitle="Dark background, light text, blue accents",
        theme=DarkTheme(),
        footer_panel=FooterPanel(center_text="Dark | Docs"),
    )
    slide2.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide2[0, 0].text(
        "This slide uses the built-in DarkTheme.\n"
        "Dark background (#1E1E1E), light text, Helvetica.",
        style="body",
    )
    doc.add_slide(slide2)

    # ---- Slide 3: Light theme ----
    slide3 = Slide(
        "Light Theme",
        subtitle="Soft blue on near-white background",
        theme=LightTheme(),
        footer_panel=FooterPanel(center_text="Light | Docs"),
    )
    slide3.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide3[0, 0].text(
        "This slide uses the built-in LightTheme.\n"
        "Blue on #FAFAFA background, Helvetica.",
        style="body",
    )
    doc.add_slide(slide3)

    # ---- Slide 4: OceanTheme — custom theme with registration ----
    slide4 = Slide(
        "Ocean Theme",
        subtitle="Teal/blue palette, Helvetica, registered theme",
        theme=OceanTheme(),
    )
    slide4.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide4[0, 0].text(
        "This slide uses a fully custom theme:\n"
        "- Custom ColorPalette (teal/blue/orange)\n"
        "- @Theme.register('ocean') for name-based lookup\n"
        "- SolidBackground from palette",
        style="body",
    )
    doc.add_slide(slide4)

    # ---- Slide 5: (removed) ---- #

    # ---- Slide 6: Registered theme via name string ----
    slide6 = Slide(
        "Ocean by Name",
        theme="ocean",
        footer_panel=FooterPanel(center_text="Registered | Docs"),
    )
    slide6.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide6[0, 0].text(
        "Themes can be registered with @Theme.register('name')\n"
        "and referenced by a plain string.\n\n"
        'Slide("Title", theme="ocean")',
        style="body",
    )
    doc.add_slide(slide6)

    # ---- Slide 7: Theme via Document ----
    slide7 = Slide(
        "Theme via Document",
        subtitle="Pass theme= to Document and let slides inherit",
        theme=DarkTheme(),
        footer_panel=FooterPanel(center_text="Document theme | Docs"),
    )
    slide7.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide7[0, 0].text(
        "When a theme is set on the Document, new slides\n"
        "inherit it automatically unless overridden.\n\n"
        "doc = Document('Title', theme=DarkTheme())\n"
        "slide = doc.new_slide('Slide')  # inherits DarkTheme",
        style="body",
    )
    doc.add_slide(slide7)

    out = OUT_DIR / "docs_themes"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_themes.pdf and docs_themes.html")


if __name__ == "__main__":
    main()
