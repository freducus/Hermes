"""Title/Subtitle configuration — formatting for the slide title panel.

Pure data model with zero renderer dependencies.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional

from reporting.layout.geometry import Edges
from reporting.elements.text import TextAlignment
from reporting.styles.colors import Color, ColorValue, normalize_color

__all__ = [
    "TitleConfig", "SubtitleConfig",
    "SubtitlePlacement", "TitlePanelConfig",
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
class TitleConfig:
    """Formatting configuration for the slide title text.

    Applies to the title rendered in the built-in title panel
    at the top of every ``Slide``.

    Args:
        font_name: Font family (default ``"Helvetica"``).
        font_size: Font size in points (default ``20.0``).
        bold: Whether the title is bold (default ``True``).
        italic: Whether the title is italic (default ``False``).
        color: Text colour as a ``ColorValue`` (default
            ``"#1F4E79"``).
        alignment: Horizontal alignment (default
            ``TextAlignment.LEFT``).
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

        from reporting.title_config import TitleConfig
        from reporting.elements.text import TextAlignment

        config = TitleConfig(
            font_name="Times-Roman",
            font_size=24,
            color="#003366",
            alignment=TextAlignment.CENTER,
            show_separator=False,
        )
        slide = Slide("Title", title_config=config)
    """

    font_name: str = "Helvetica"
    font_size: float = 20.0
    bold: bool = True
    italic: bool = False
    color: ColorValue = "#1F4E79"
    alignment: TextAlignment = TextAlignment.LEFT
    show_separator: bool = True
    separator_color: ColorValue = "#CCCCCC"
    separator_width: float = 1.0
    separator_margin: float = 8.0

    def __post_init__(self) -> None:
        self.color = normalize_color(self.color)
        self.separator_color = normalize_color(self.separator_color)


@dataclasses.dataclass
class SubtitleConfig:
    """Formatting configuration for the slide subtitle text.

    Args:
        font_name: Font family (default ``"Helvetica"``).
        font_size: Font size in points (default ``11.0``).
        bold: Whether the subtitle is bold (default ``False``).
        italic: Whether the subtitle is italic (default ``False``).
        color: Text colour as a ``ColorValue``
            (default ``"#666666"``).
        alignment: Horizontal alignment (default
            ``TextAlignment.LEFT``).

    Example::

        from reporting.title_config import SubtitleConfig

        config = SubtitleConfig(
            font_size=12,
            color="#999999",
            italic=True,
        )
        slide = Slide("Results", subtitle="Test data",
                      subtitle_config=config)
    """

    font_name: str = "Helvetica"
    font_size: float = 11.0
    bold: bool = False
    italic: bool = False
    color: ColorValue = "#666666"
    alignment: TextAlignment = TextAlignment.LEFT

    def __post_init__(self) -> None:
        self.color = normalize_color(self.color)


@dataclasses.dataclass
class TitlePanelConfig:
    """Layout configuration for the slide title panel area.

    Controls how the title and subtitle are arranged within the
    title panel at the top of every ``Slide``.

    Args:
        subtitle_placement: Whether the subtitle appears
            ``BELOW`` the title or ``BESIDE`` it
            (default ``SubtitlePlacement.BELOW``).
        subtitle_width_ratio: Fraction of the panel width
            allocated to the subtitle when placed ``BESIDE``
            (default ``0.35``).
        padding: Inner padding around the panel content as
            an ``Edges``.  Default::

                Edges(left=20, right=20, top=8, bottom=8)

    Example::

        from reporting.title_config import (
            TitlePanelConfig, SubtitlePlacement,
        )

        config = TitlePanelConfig(
            subtitle_placement=SubtitlePlacement.BESIDE,
            subtitle_width_ratio=0.4,
        )
        slide = Slide("Results", subtitle="Test data",
                      title_panel_config=config)
    """

    subtitle_placement: SubtitlePlacement = SubtitlePlacement.BELOW
    subtitle_width_ratio: float = 0.35
    padding: Edges = dataclasses.field(
        default_factory=lambda: Edges(left=20, right=20, top=8, bottom=8),
    )
