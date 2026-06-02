"""Title/Subtitle configuration — formatting for the slide title panel.

Pure data model with zero renderer dependencies.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional

from reporting.layout.geometry import Edges
from reporting.elements.text import TextAlignment

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
    color: str = "#1F4E79"
    alignment: TextAlignment = TextAlignment.LEFT
    show_separator: bool = True
    separator_color: str = "#CCCCCC"
    separator_width: float = 1.0
    separator_margin: float = 8.0


@dataclasses.dataclass
class SubtitleConfig:
    font_name: str = "Helvetica"
    font_size: float = 11.0
    bold: bool = False
    italic: bool = False
    color: str = "#666666"
    alignment: TextAlignment = TextAlignment.LEFT


@dataclasses.dataclass
class TitlePanelConfig:
    subtitle_placement: SubtitlePlacement = SubtitlePlacement.BELOW
    subtitle_width_ratio: float = 0.35
    padding: Edges = dataclasses.field(
        default_factory=lambda: Edges(left=20, right=20, top=8, bottom=8),
    )
