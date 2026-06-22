"""Reporting framework — a programmable PowerPoint for engineering reports.

Top-level imports: ``Document``, ``Slide``.

Example::

    from reporting import Document, Slide

    doc = Document("Cover")
    slide = doc.new_slide()
    slide.title = "Hello, world!"
    slide.grid_layout(rows=1, cols=1)
    slide[0, 0].text("Hello, world!")
"""

from reporting.document import Document
from reporting.slide import Slide

__all__ = ["Document", "Slide"]
