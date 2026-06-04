"""Text element — rich text content, backend-agnostic."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional

from reporting.styles.colors import ColorValue, normalize_color
from reporting.elements.base import BaseElement, ElementType


class TextAlignment(Enum):
    """Horizontal alignment for a text block.

    Members:
        LEFT: Align text to the left edge.
        CENTER: Centre text horizontally.
        RIGHT: Align text to the right edge.
        JUSTIFY: Stretch text to fill the full width.
    """
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclasses.dataclass
class TextRun:
    """A single run of text with uniform formatting.

    Multiple runs within a ``TextBlock`` create mixed-format
    content (e.g. "Hello **bold** world").

    Args:
        text: The text content.
        bold: Whether the run is bold (default ``False``).
        italic: Whether the run is italic (default ``False``).
        underline: Whether the run is underlined
            (default ``False``).
        color: Text colour as a ``ColorValue``
            (default ``None`` = inherit).
        size: Font size in points (default ``None`` = inherit).
        font_name: Font family (default ``None`` = inherit).

    Example::

        from reporting.elements.text import TextRun

        run = TextRun("Hello", bold=True, size=14)
    """
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[ColorValue] = None
    size: Optional[float] = None
    font_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.color is not None:
            self.color = normalize_color(self.color)


@dataclasses.dataclass
class TextBlock:
    """A paragraph consisting of one or more ``TextRun`` instances.

    Args:
        runs: The runs that make up this paragraph.
        alignment: Horizontal alignment
            (default ``TextAlignment.LEFT``).
        spacing_before: Extra space before the paragraph
            in points (default ``0.0``).
        spacing_after: Extra space after the paragraph
            in points (default ``0.0``).
    """
    runs: list[TextRun]
    alignment: TextAlignment = TextAlignment.LEFT
    spacing_before: float = 0.0
    spacing_after: float = 0.0


@dataclasses.dataclass
class TextElement(BaseElement):
    """A text content element consisting of one or more ``TextBlock`` instances.

    When created via ``_CellProxy.text()``, a single block with
    one run is constructed automatically from convenience kwargs
    (``bold``, ``italic``, ``color``, ``size``, ``font_name``,
    ``alignment``).  For mixed-format text, build runs and blocks
    manually after construction.

    Args:
        text: Initial plain text content (default ``""``).
        **kwargs: Formatting kwargs extracted at construction:

            - ``bold``: ``bool``
            - ``italic``: ``bool``
            - ``color``: ``ColorValue``
            - ``size``: ``float`` (points)
            - ``font_name``: ``str``
            - ``alignment``: ``TextAlignment`` or ``str``

    Example::

        from reporting.elements.text import TextElement, TextRun, TextAlignment

        # Simple — one style for the whole string
        el = TextElement("Hello", bold=True, size=14)

        # Mixed-format
        el = TextElement()
        el.add_run("Hello ", bold=True)
        el.add_run("world", italic=True)
        el.add_block(alignment=TextAlignment.CENTER)
        el.add_run("Centered line")
    """
    blocks: list[TextBlock] = dataclasses.field(default_factory=list)

    def __init__(self, text: str = "", **kwargs: object) -> None:
        super().__init__(element_type=ElementType.TEXT, properties=kwargs)
        bold = kwargs.pop("bold", False)
        italic = kwargs.pop("italic", False)
        color = kwargs.pop("color", None)
        size = kwargs.pop("size", None)
        font_name = kwargs.pop("font_name", None)
        alignment = kwargs.pop("alignment", TextAlignment.LEFT)
        if isinstance(alignment, str):
            alignment = TextAlignment(alignment)
        self.blocks = []
        if text:
            run = TextRun(text=text, bold=bold, italic=italic, color=color, size=size, font_name=font_name)
            self.blocks.append(TextBlock(runs=[run], alignment=alignment))

    def add_run(
        self,
        text: str,
        bold: bool = False,
        italic: bool = False,
        color: Optional[str] = None,
        size: Optional[float] = None,
        font_name: Optional[str] = None,
    ) -> TextRun:
        """Append a ``TextRun`` to the last block.

        If no blocks exist yet, creates a ``TextBlock`` first.

        Args:
            text: Run text.
            bold: Bold flag (default ``False``).
            italic: Italic flag (default ``False``).
            color: Colour (default ``None``).
            size: Font size in points (default ``None``).
            font_name: Font family (default ``None``).

        Returns:
            The created ``TextRun``.
        """
        run = TextRun(text=text, bold=bold, italic=italic, color=color, size=size, font_name=font_name)
        if not self.blocks:
            self.blocks.append(TextBlock(runs=[]))
        self.blocks[-1].runs.append(run)
        return run

    def add_block(
        self,
        alignment: TextAlignment = TextAlignment.LEFT,
        spacing_before: float = 0.0,
        spacing_after: float = 0.0,
    ) -> TextBlock:
        """Start a new paragraph block.

        Args:
            alignment: Horizontal alignment
                (default ``TextAlignment.LEFT``).
            spacing_before: Space before in points
                (default ``0.0``).
            spacing_after: Space after in points
                (default ``0.0``).

        Returns:
            The created (empty) ``TextBlock``.
        """
        if isinstance(alignment, str):
            alignment = TextAlignment(alignment)
        block = TextBlock(runs=[], alignment=alignment, spacing_before=spacing_before, spacing_after=spacing_after)
        self.blocks.append(block)
        return block
