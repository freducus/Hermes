"""Document — a complete report container holding multiple slides."""

from __future__ import annotations

import dataclasses
from typing import Optional, Union

from reporting.slide import Slide
from reporting.styles.theme import Theme, CorporateTheme
from reporting.renderers.base import BaseRenderer


@dataclasses.dataclass
class Document:
    """A report document that holds slides and coordinates rendering.

    ``Document`` is the top-level container.  Add slides to it and then
    call ``render()`` with a renderer backend.

    Args:
        title: Report title (displayed in metadata, not on slides).
        author: Author name for metadata (default ``""``).
        theme: Visual theme applied to all slides by default.
            Built-in choices: ``CorporateTheme()``, ``DarkTheme()``,
            ``LightTheme()`` (default ``CorporateTheme()``).
        slides: Initial list of slides.  Prefer ``add_slide()`` or
            ``new_slide()`` instead of setting this directly.

    Example::

        from reporting.document import Document
        from reporting.slide import Slide
        from reporting.renderers.pdf.renderer import PDFRenderer

        doc = Document("My Report", author="Engineer")
        slide = Slide("Introduction")
        slide.grid_layout(rows=1, cols=1)
        slide[0, 0].text("Hello, world!")
        doc.add_slide(slide)
        doc.render(PDFRenderer(), "output.pdf")
    """

    title: str
    author: str = ""
    theme: Theme = dataclasses.field(default_factory=CorporateTheme)
    slides: list[Slide] = dataclasses.field(default_factory=list)

    def add_slide(self, slide: Slide) -> Slide:
        """Append an already-built ``Slide`` to the document.

        Args:
            slide: A fully configured ``Slide`` instance (grid layout
                and content already set).

        Returns:
            The same ``slide`` instance (useful for chaining).

        Example::

            doc = Document("Report")
            s = Slide("Page 1")
            s.grid_layout(rows=1, cols=1)
            s[0, 0].text("Content")
            doc.add_slide(s)
        """
        self.slides.append(slide)
        return slide

    def new_slide(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        theme: Optional[Theme] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        slide_type: str = "default",
        base_slide: Optional[Slide] = None,
    ) -> Slide:
        """Create a ``Slide``, add it to the document, and return it.

        Shorthand for ``Slide(...)`` + ``add_slide(...)``.

        Args:
            title: Slide title (shown in the title panel).
                Falls back to the slide type default when ``None``
                (default ``None``).
            subtitle: Optional subtitle shown below the title
                (default ``None``).
            theme: Visual theme for this slide.  Falls back to the
                document-level theme if ``None`` (default ``None``).
            width: Slide width in pixels.  Falls back to
                ``theme.page_size[0]`` when ``None``
                (default ``None``).
            height: Slide height in pixels.  Falls back to
                ``theme.page_size[1]`` when ``None``
                (default ``None``).
            slide_type: Name of a pre-defined slide type in the
                theme (default ``"default"``).
            base_slide: Another ``Slide`` whose config and grid
                layout are used as a starting point
                (default ``None``).

        Returns:
            The newly created ``Slide``, already appended to the
            document.

        Example::

            doc = Document("Report")
            slide = doc.new_slide("Results", subtitle="Test data")
            slide.grid_layout(rows=2, cols=2)
            slide[0, 0].text("Cell A")
        """
        slide = Slide(
            title=title,
            subtitle=subtitle,
            theme=theme or self.theme,
            width=width,
            height=height,
            slide_type=slide_type,
            base_slide=base_slide,
        )
        self.slides.append(slide)
        return slide

    def render(self, renderer: BaseRenderer, output_path: str) -> None:
        """Render the document to a file using the given backend.

        Args:
            renderer: A renderer instance such as ``PDFRenderer()``
                or ``HTMLRenderer()``.
            output_path: Destination file path (e.g. ``"report.pdf"``
                or ``"report.html"``).  The renderer creates or
                overwrites this file.

        Example::

            from reportlab.renderers.pdf.renderer import PDFRenderer
            doc.render(PDFRenderer(), "final_report.pdf")
        """
        renderer.render_document(self, output_path)
