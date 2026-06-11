"""Title/Subtitle configuration — formatting for the slide title panel.

Pure data model with zero renderer dependencies.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import TYPE_CHECKING, Optional

from reporting.layout.geometry import Edges
from reporting.elements.text import TextAlignment
from reporting.styles.colors import Color, ColorValue, normalize_color

if TYPE_CHECKING:
    from reporting.styles.theme import Theme

__all__ = [
    "TitleText", "SubtitleText",
    "SubtitlePlacement", "TitlePanel",
]


class SubtitlePlacement(Enum):
    """Where to place the subtitle relative to the title.

    Members:
        BELOW: Subtitle appears on a new line beneath the title.
        BESIDE: Subtitle appears to the right of the title,
            sharing the same row in the title panel.
    """
    BELOW = "below"
    BESIDE = "beside"


@dataclasses.dataclass
class TitleText:
    """Slide title with its own styling properties.

    Use ``.text`` to read or write the title string.  All styling
    properties (``font_name``, ``font_size``, ``bold``, etc.) are
    mutable attributes on the instance.

    ``TitleText`` provides ``__str__``, ``__eq__`` and ``__bool__``
    so it can be used transparently wherever a plain title string
    was expected (f-strings, comparisons, truth checks).

    Example::

        title = TitleText("Results", font_size=28, bold=True)
        slide = Slide(title)
        slide.title.text = "Updated"        # change the text
        slide.title.font_size = 24          # change styling
        print(f"{slide.title}")             # "Updated"
    """

    text: str = ""
    font_name: str = "Helvetica"
    font_size: float = 20.0
    bold: bool = True
    italic: bool = False
    color: ColorValue = "#1F4E79"
    alignment: TextAlignment = TextAlignment.LEFT

    def __post_init__(self) -> None:
        self.color = normalize_color(self.color)

    def __str__(self) -> str:
        return self.text

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.text == other
        if isinstance(other, TitleText):
            return self.text == other.text
        return NotImplemented

    def __bool__(self) -> bool:
        return bool(self.text)

    def __repr__(self) -> str:
        return f"TitleText({self.text!r}, font_size={self.font_size})"

    @classmethod
    def from_theme(
        cls,
        theme: Theme,
        text: str = "",
    ) -> TitleText:
        """Create a ``TitleText`` deriving font defaults from a ``Theme``.

        Args:
            theme: Theme to derive font and colour from.
            text: Title text (default ``""``).

        Returns:
            A fully-populated ``TitleText``.
        """
        h1 = theme.typography.heading_1
        return cls(
            text=text,
            font_name=h1.family,
            font_size=h1.size,
            bold=h1.bold,
            italic=h1.italic,
            color=h1.color or theme.palette.primary.css,
            alignment=TextAlignment.LEFT,
        )


@dataclasses.dataclass
class SubtitleText:
    """Slide subtitle with its own styling properties.

    Use ``.text`` to read or write the subtitle string.  All styling
    properties are mutable attributes.

    ``SubtitleText`` provides ``__str__``, ``__eq__`` and ``__bool__``
    so it works transparently in f-strings, comparisons and truth checks.

    Example::

        sub = SubtitleText("Test data", font_size=12, italic=True)
        slide = Slide("Title", subtitle=sub)
        slide.subtitle.text = "Updated"
        slide.subtitle.color = "#999999"
    """

    text: str = ""
    font_name: str = "Helvetica"
    font_size: float = 11.0
    bold: bool = False
    italic: bool = False
    color: ColorValue = "#666666"
    alignment: TextAlignment = TextAlignment.LEFT

    def __post_init__(self) -> None:
        self.color = normalize_color(self.color)

    def __str__(self) -> str:
        return self.text

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.text == other
        if isinstance(other, SubtitleText):
            return self.text == other.text
        return NotImplemented

    def __bool__(self) -> bool:
        return bool(self.text)

    def __repr__(self) -> str:
        return f"SubtitleText({self.text!r}, font_size={self.font_size})"

    @classmethod
    def from_theme(
        cls,
        theme: Theme,
        text: str = "",
    ) -> SubtitleText:
        """Create a ``SubtitleText`` deriving font defaults from a ``Theme``.

        Args:
            theme: Theme to derive font and colour from.
            text: Subtitle text (default ``""``).

        Returns:
            A fully-populated ``SubtitleText``.
        """
        body = theme.typography.body
        return cls(
            text=text,
            font_name=body.family,
            font_size=body.size,
            bold=body.bold,
            italic=body.italic,
            color=body.color or theme.palette.text_secondary.css,
            alignment=TextAlignment.LEFT,
        )


@dataclasses.dataclass
class TitlePanel:
    """Layout configuration for the slide title panel area.

    Controls the panel height, how the title and subtitle are
    arranged, padding, and the optional separator line below
    the title.

    Args:
        height: Title panel height in pixels (default ``60.0``).
        subtitle_placement: Whether the subtitle appears
            ``BELOW`` the title or ``BESIDE`` it
            (default ``SubtitlePlacement.BELOW``).
        subtitle_width_ratio: Fraction of the panel width
            allocated to the subtitle when placed ``BESIDE``
            (default ``0.35``).
        padding: Inner padding around the panel content as
            an ``Edges``.  Default::

                Edges(left=20, right=20, top=8, bottom=8)

        show_separator: Whether to draw a horizontal rule
            below the title (default ``True``).
        separator_color: Colour of the separator line
            (default ``"#CCCCCC"``).
        separator_width: Thickness of the separator line
            in points (default ``1.0``).
        separator_margin: Vertical gap between the title
            baseline and the separator in points
            (default ``8.0``).

    Example::

        from reporting.title_config import (
            TitlePanel, SubtitlePlacement,
        )

        panel = TitlePanel(
            height=80,
            subtitle_placement=SubtitlePlacement.BESIDE,
            subtitle_width_ratio=0.4,
        )
        slide = Slide("Results", subtitle="Test data",
                      title_panel=panel)
    """

    height: float = 60.0
    subtitle_placement: SubtitlePlacement = SubtitlePlacement.BELOW
    subtitle_width_ratio: float = 0.35
    padding: Edges = dataclasses.field(
        default_factory=lambda: Edges(left=20, right=20, top=8, bottom=8),
    )
    show_separator: bool = True
    separator_color: ColorValue = "#CCCCCC"
    separator_width: float = 1.0
    separator_margin: float = 8.0

    def __post_init__(self) -> None:
        self.separator_color = normalize_color(self.separator_color)

    @classmethod
    def from_theme(cls, theme: Theme) -> TitlePanel:
        """Create a ``TitlePanel`` from a ``Theme``.

        Derives separator colour from the theme's colour palette.

        Args:
            theme: The theme to use as a source.

        Returns:
            A fully-populated ``TitlePanel``.
        """
        return cls(
            height=60.0,
            show_separator=True,
            separator_color=theme.palette.border.css,
            separator_width=1.0,
            separator_margin=8.0,
        )
