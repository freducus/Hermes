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
    BELOW = "below"
    BESIDE = "beside"


@dataclasses.dataclass
class TitleConfig:
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
    subtitle_placement: SubtitlePlacement = SubtitlePlacement.BELOW
    subtitle_width_ratio: float = 0.35
    padding: Edges = dataclasses.field(
        default_factory=lambda: Edges(left=20, right=20, top=8, bottom=8),
    )
