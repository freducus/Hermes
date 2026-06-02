"""Table styling system — defines zebra, heatmap, and conditional formats."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.styles.colors import ColorValue, normalize_color


@dataclasses.dataclass(frozen=True)
class ZebraStyle:
    even_row_color: ColorValue = "#F3F3F3"
    odd_row_color: ColorValue = "#FFFFFF"
    header_color: ColorValue = "#4472C4"
    header_text_color: ColorValue = "#FFFFFF"
    border_color: ColorValue = "#D9D9D9"

    def __post_init__(self) -> None:
        object.__setattr__(self, 'even_row_color', normalize_color(self.even_row_color))
        object.__setattr__(self, 'odd_row_color', normalize_color(self.odd_row_color))
        object.__setattr__(self, 'header_color', normalize_color(self.header_color))
        object.__setattr__(self, 'header_text_color', normalize_color(self.header_text_color))
        object.__setattr__(self, 'border_color', normalize_color(self.border_color))


@dataclasses.dataclass(frozen=True)
class HeatmapStyle:
    color_map: str = "YlOrRd"
    min_color: ColorValue = "#FFFFCC"
    max_color: ColorValue = "#FF0000"

    def __post_init__(self) -> None:
        object.__setattr__(self, 'min_color', normalize_color(self.min_color))
        object.__setattr__(self, 'max_color', normalize_color(self.max_color))


@dataclasses.dataclass(frozen=True)
class TableStyle:
    zebra: Optional[ZebraStyle] = None
    heatmap: Optional[HeatmapStyle] = None
    highlight_max_color: ColorValue = "#C6EFCE"
    highlight_min_color: ColorValue = "#FFC7CE"
    font_size: float = 10.0
    header_font_size: float = 11.0
    font_family: str = "Helvetica"
    padding: float = 4.0

    def __post_init__(self) -> None:
        object.__setattr__(self, 'highlight_max_color', normalize_color(self.highlight_max_color))
        object.__setattr__(self, 'highlight_min_color', normalize_color(self.highlight_min_color))
