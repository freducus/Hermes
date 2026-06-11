"""Built-in themes and custom theme creation — used by docs 07_themes.rst."""

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


def main() -> None:
    # ---- Documento con CorporateTheme (por defecto) ----
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

    # ---- Slide 4: Custom theme with green palette ----
    custom_palette = ColorPalette(
        primary=Color.from_hex("#2E7D32"),
        secondary=Color.from_hex("#43A047"),
        accent=Color.from_hex("#FF8F00"),
        background=Color.from_hex("#F1F8E9"),
        text_primary=Color.from_hex("#1B5E20"),
        text_secondary=Color.from_hex("#558B2F"),
        border=Color.from_hex("#C8E6C9"),
        error=Color.from_hex("#C62828"),
        warning=Color.from_hex("#F57F17"),
        success=Color.from_hex("#2E7D32"),
    )
    custom_typo = Typography(
        heading_1=FontSpec(family="Times-Bold", size=30, bold=False, color="#1B5E20"),
        heading_2=FontSpec(family="Times-Roman", size=24, bold=True, color="#2E7D32"),
        body=FontSpec(family="Times-Roman", size=11, color="#333333"),
        caption=FontSpec(family="Times-Roman", size=9, italic=True, color="#558B2F"),
    )
    custom_theme = Theme(
        name="GreenFields",
        palette=custom_palette,
        typography=custom_typo,
        table_style=TableStyle(),
        footer=FooterPanel(center_text="GreenFields Report"),
    )

    slide4 = Slide(
        "Custom Theme: GreenFields",
        subtitle="Green palette, Times serif fonts",
        theme=custom_theme,
        footer_panel=FooterPanel(center_text="Custom | Docs"),
    )
    slide4.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide4[0, 0].text(
        "This slide uses a custom theme with:\n"
        "- Green colour palette\n"
        "- Georgia serif fonts\n"
        "- Light green background (#F1F8E9)",
        style="body",
    )
    doc.add_slide(slide4)

    # ---- Slide 5: Theme applied via Document ----
    slide5 = Slide(
        "Theme via Document",
        subtitle="Pass theme= to Document and let slides inherit",
        footer_panel=FooterPanel(center_text="Document theme | Docs"),
    )
    slide5.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide5[0, 0].text(
        "When a theme is set on the Document, new slides\n"
        "inherit it automatically unless overridden.\n\n"
        "doc = Document('Title', theme=DarkTheme())\n"
        "slide = doc.new_slide('Slide')  # inherits DarkTheme",
        style="body",
    )
    doc.add_slide(slide5)

    out = OUT_DIR / "docs_themes"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_themes.pdf and docs_themes.html")


if __name__ == "__main__":
    main()


