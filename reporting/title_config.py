"""Title/Subtitle configuration — formatting for the slide title.

Pure data model with zero renderer dependencies.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from reporting.elements.text import TextAlignment
from reporting.styles.colors import ColorValue, normalize_color

if TYPE_CHECKING:
    from reporting.styles.theme import Theme

__all__ = [
    "TitleText", "SubtitleText", "TitlePanel",
]


@dataclasses.dataclass
class TitleText:
    """Slide title with its own styling properties.

    Use ``.text`` to read or write the title string.  All styling
    properties (``font_name``, ``font_size``, ``bold``, etc.) are
    mutable attributes on the instance.
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
        """Create a ``TitleText`` deriving font defaults from a ``Theme``."""
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
        """Create a ``SubtitleText`` deriving font defaults from a ``Theme``."""
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
    """Controls whether the slide title panel is rendered.

    When ``enabled`` is ``True``, the renderer draws the title and
    subtitle (if set) at the top of the slide.  When ``False``
    (the default), no title panel is shown and the grid uses the
    full slide area.

    Args:
        enabled: Whether to render the title panel
            (default ``False``).
    """

    enabled: bool = False
