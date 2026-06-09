"""Title panel and footer configuration — used by docs 04_header_footer.rst."""

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.footer_config import FooterConfig
from reporting.title_config import (
    TitleConfig, SubtitleConfig, TitlePanelConfig,
    SubtitlePlacement,
)
from reporting.elements.text import TextAlignment
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer

OUT_DIR = Path(__file__).parent


def main() -> None:
    doc = Document("Header & Footer Demo", author="Docs")

    # ---- Slide 1: Default header/footer ----
    slide1 = Slide(
        "Default Header & Footer",
        subtitle="Built-in title panel and auto-footer",
        footer_config=FooterConfig(center_text="Page {page} of {total}"),
    )
    slide1.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide1[0, 0].text(
        "This slide uses the default title panel (60px, separator)\n"
        "and the auto-generated footer with page numbering.\n\n"
        "FooterConfig(center_text=\"Page {page} of {total}\")",
        size=11,
    )
    doc.add_slide(slide1)

    # ---- Slide 2: Disabled footer ----
    slide2 = Slide(
        "No Footer",
        subtitle="FooterConfig(enabled=False)",
        footer_config=FooterConfig(enabled=False),
    )
    slide2.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide2[0, 0].text(
        "Footer is disabled via FooterConfig(enabled=False).\n"
        "The content area extends to the bottom of the slide.",
        size=11,
    )
    doc.add_slide(slide2)

    # ---- Slide 3: Customised footer ----
    slide3 = Slide(
        "Custom Footer",
        subtitle="Styled footer with separator and logo",
        footer_config=FooterConfig(
            height=36,
            separator_color="#1565C0",
            separator_width=2,
            font_size=9,
            color="#1565C0",
            center_text="Confidential",
            padding=Edges(left=24, right=24, top=6, bottom=6),
        ),
        footer_logo=str(OUT_DIR / "_docs_elements_logo.png"),
    )
    slide3.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide3[0, 0].text(
        "Footer with blue separator, larger height (36px),\n"
        "custom font, center text, and a logo in the left cell.",
        size=11,
    )
    doc.add_slide(slide3)

    # ---- Slide 4: Custom title formatting ----
    slide4 = Slide(
        "Custom Title Panel",
        subtitle="TitleConfig + SubtitleConfig + SubtitlePlacement.BESIDE",
        title_config=TitleConfig(
            font_name="Times-Bold",
            font_size=28,
            bold=False,
            color="#1565C0",
            alignment=TextAlignment.LEFT,
            show_separator=False,
        ),
        subtitle_config=SubtitleConfig(
            font_name="Helvetica-Oblique",
            font_size=12,
            italic=True,
            color="#666666",
            alignment=TextAlignment.RIGHT,
        ),
        title_panel_config=TitlePanelConfig(
            subtitle_placement=SubtitlePlacement.BESIDE,
            subtitle_width_ratio=0.35,
        ),
        title_panel_height=70,
        footer_config=FooterConfig(center_text="Styled title | Docs"),
    )
    slide4.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide4[0, 0].text(
        "Title uses Times-Bold 28pt (not actually bold),\n"
        "subtitle appears beside on the right (35% width),\n"
        "separator hidden, panel height 70px.",
        size=11,
    )
    doc.add_slide(slide4)

    # ---- Slide 5: Subtitle below with separator ----
    slide5 = Slide(
        "Title with Separator",
        subtitle="Subtitle placed below with a visible separator",
        title_config=TitleConfig(
            font_size=24,
            bold=True,
            color="#2E7D32",
            alignment=TextAlignment.CENTER,
            show_separator=True,
            separator_color="#A5D6A7",
            separator_width=2,
        ),
        subtitle_config=SubtitleConfig(
            font_size=13,
            color="#558B2F",
            alignment=TextAlignment.CENTER,
        ),
        title_panel_height=80,
        footer_config=FooterConfig(enabled=False),
    )
    slide5.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide5[0, 0].text(
        "Centered title, centered subtitle below,\n"
        "green separator line, no footer.",
        size=11,
    )
    doc.add_slide(slide5)

    out = OUT_DIR / "docs_header_footer"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_header_footer.pdf and docs_header_footer.html")


if __name__ == "__main__":
    main()
