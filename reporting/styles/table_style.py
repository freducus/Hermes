"""Table styling system — defines zebra, heatmap, and conditional formats."""

from __future__ import annotations

import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class ZebraStyle:
    even_row_color: str = "#F3F3F3"
    odd_row_color: str = "#FFFFFF"
    header_color: str = "#4472C4"
    header_text_color: str = "#FFFFFF"
    border_color: str = "#D9D9D9"


@dataclasses.dataclass(frozen=True)
class HeatmapStyle:
    color_map: str = "YlOrRd"
    min_color: str = "#FFFFCC"
    max_color: str = "#FF0000"


@dataclasses.dataclass(frozen=True)
class TableStyle:
    zebra: Optional[ZebraStyle] = None
    heatmap: Optional[HeatmapStyle] = None
    highlight_max_color: str = "#C6EFCE"
    highlight_min_color: str = "#FFC7CE"
    font_size: float = 10.0
    header_font_size: float = 11.0
    font_family: str = "Helvetica"
    padding: float = 4.0
