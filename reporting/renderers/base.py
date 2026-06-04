"""Abstract base renderer — defines the renderer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from reporting.document import Document


class BaseRenderer(ABC):
    """Abstract base class for all output renderers.

    Subclasses must implement ``render_document``, ``render_slide``,
    and ``render_panel``.  A renderer converts the report model
    (``Document`` → ``Slide`` → ``Panel`` → ``BaseElement``) into
    an output format (PDF, HTML, etc.).

    Example::

        from reporting.renderers.base import BaseRenderer

        class MyRenderer(BaseRenderer):
            def render_document(self, document, output_path):
                ...
            def render_slide(self, slide):
                ...
            def render_panel(self, panel, rect):
                ...
    """

    @abstractmethod
    def render_document(self, document: "Document", output_path: str) -> None:
        """Render an entire ``Document`` to an output file.

        Args:
            document: The report document to render.
            output_path: File path for the output (e.g. ``"report.pdf"``).
        """
        raise NotImplementedError

    @abstractmethod
    def render_slide(self, slide: object) -> object:
        """Render a single ``Slide``.

        Args:
            slide: A ``Slide`` instance.

        Returns:
            The slide object (or a renderer-specific handle).
        """
        raise NotImplementedError

    @abstractmethod
    def render_panel(self, panel: object, rect: object) -> object:
        """Render a single panel (cell) within a slide.

        Args:
            panel: A ``Panel`` instance.
            rect: The ``Rect`` bounding the panel in pixels.

        Returns:
            The panel object (or ``None``).
        """
        raise NotImplementedError
