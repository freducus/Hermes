"""Title panel and footer configuration — used by docs 04_header_footer.rst."""

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer

OUT_DIR = Path(__file__).parent


def main() -> None:
    doc = Document("Header & Footer Demo", author="Docs")

    # ---- Slide 1: Default header/footer ----
    slide1 = Slide()
    slide1.title = "Default Header & Footer"
    slide1.subtitle = "Built-in title panel and auto-footer"
    slide1.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide1[0, 0].text(
        "This slide uses the default title panel (60px, separator)\n"
        "and the auto-generated footer with page numbering.\n\n"
        "FooterPanel(center_text=\"Page {page} of {total}\")",
        size=11,
    )
    doc.add_slide(slide1)

    # ---- Slide 2: Disabled footer ----
    slide2 = Slide()
    slide2.title = "No Footer"
    slide2.subtitle = "FooterPanel(enabled=False)"
    slide2.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide2[0, 0].text(
        "Footer is disabled via FooterPanel(enabled=False).\n"
        "The content area extends to the bottom of the slide.",
        size=11,
    )
    doc.add_slide(slide2)

    # ---- Slide 3: Customised footer ----
    slide3 = Slide()
    slide3.title = "Custom Footer"
    slide3.subtitle = "Styled footer with separator and logo"
    slide3.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide3[0, 0].text(
        "Footer with blue separator, larger height (36px),\n"
        "custom font, center text, and a logo in the left cell.",
        size=11,
    )
    doc.add_slide(slide3)

    # ---- Slide 4: Custom title formatting ----
    slide4 = Slide()
    slide4.title = "Custom Title Panel"
    slide4.subtitle = "TitleText + SubtitleText"
    slide4.title_panel.enabled = True
    slide4.grid_layout(rows=1, cols=1, padding=Edges.all(30))
    slide4[0, 0].text(
        "Title uses Times-Bold 28pt (not actually bold),\n"
        "subtitle appears beside on the right (35% width),\n"
        "separator hidden, panel height 70px.",
        size=11,
    )
    doc.add_slide(slide4)

    # ---- Slide 5: Subtitle below with separator ----
    slide5 = Slide()
    slide5.title = "Title with Separator"
    slide5.subtitle = "Subtitle placed below with a visible separator"
    slide5.title_panel.enabled = True
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
