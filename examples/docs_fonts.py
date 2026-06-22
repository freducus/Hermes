"""Font usage, style keyword, and standard font families — used by docs 06_fonts.rst."""

from pathlib import Path

from reporting.document import Document
from reporting.slide import Slide
from reporting.layout.geometry import Edges
from reporting.renderers.pdf.renderer import PDFRenderer
from reporting.renderers.html.renderer import HTMLRenderer

OUT_DIR = Path(__file__).parent


def main() -> None:
    doc = Document("Fonts Demo", author="Docs")

    # ---- Slide 1: Style keyword ----
    slide1 = Slide()
    slide1.title = "The ``style`` Keyword"
    slide1.subtitle = "Inherit font properties from the theme typography"
    slide1.grid_layout(rows=3, cols=1, gap=8, padding=Edges.all(20))

    slide1[0, 0].text("This is style=\"h1\"", style="h1")
    slide1[1, 0].text("This is style=\"body\"", style="body")
    slide1[2, 0].text(
        "style=\"body\" with explicit color override",
        style="body", color="#C62828",
    )
    doc.add_slide(slide1)

    # ---- Slide 2: Named fonts ----
    slide2 = Slide()
    slide2.title = "Standard Font Families"
    slide2.subtitle = "font_name accepts any PostScript font name"
    slide2.grid_layout(rows=3, cols=2, gap=10, padding=Edges.all(20))

    slide2[0, 0].text("Helvetica 14pt", font_name="Helvetica", size=14)
    slide2[0, 1].text("Helvetica-Bold 14pt", font_name="Helvetica-Bold", size=14)
    slide2[1, 0].text("Times-Roman 12pt", font_name="Times-Roman", size=12)
    slide2[1, 1].text("Times-Italic 12pt", font_name="Times-Italic", size=12)
    slide2[2, 0].text("Courier 10pt", font_name="Courier", size=10)
    slide2[2, 1].text("Courier-Bold 10pt", font_name="Courier-Bold", size=10)
    doc.add_slide(slide2)

    # ---- Slide 3: bold/italic/color kwargs ----
    slide3 = Slide()
    slide3.title = "Inline Formatting"
    slide3.subtitle = "Bold, italic, color, alignment in .text()"
    slide3.grid_layout(rows=4, cols=2, gap=8, padding=Edges.all(20))

    slide3[0, 0].text("Bold text", bold=True, size=14)
    slide3[0, 1].text("Italic text", italic=True, size=14)
    slide3[1, 0].text("Bold + Italic", bold=True, italic=True, size=14)
    slide3[1, 1].text("Colored text", color="#1565C0", size=14)
    slide3[2, 0].text("Custom size 18", size=18)
    slide3[2, 1].text("Right-aligned", alignment="right", size=14)
    slide3[3, 0].text("Center-aligned blue", alignment="center",
                       color="#C62828", size=14)
    slide3[3, 1].text("Mixed via add_run:", size=12)
    te = slide3[3, 1].text("", size=12)
    te.add_run("bold ", bold=True)
    te.add_run("italic ", italic=True)
    te.add_run("colored", color="#C62828")
    doc.add_slide(slide3)

    # ---- Slide 4: FontSpec and Typography ----
    slide4 = Slide()
    slide4.title = "FontSpec & Typography"
    slide4.subtitle = "Define custom font configs for the theme"
    slide4.grid_layout(rows=1, cols=1, padding=Edges.all(20))
    slide4[0, 0].text(
        "from reporting.styles.typography import FontSpec, Typography\n"
        "\n"
        "typo = Typography(\n"
        "    heading_1=FontSpec(family=\"Arial\", size=28, bold=True,\n"
        "                       color=\"#1F4E79\"),\n"
        "    body=FontSpec(family=\"Arial\", size=11, color=\"#333333\"),\n"
        "    caption=FontSpec(family=\"Arial\", size=9, italic=True,\n"
        "                     color=\"#666666\"),\n"
        ")",
        style="body",
    )
    doc.add_slide(slide4)

    out = OUT_DIR / "docs_fonts"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    HTMLRenderer().render_document(doc, str(out) + ".html")
    print("Generated docs_fonts.pdf and docs_fonts.html")


if __name__ == "__main__":
    main()


