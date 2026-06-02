"""Style primitives for TableSpec — CellStyle, ColumnStyle, RowStyle, TableStyle.

All style dataclasses are frozen (immutable) to prevent accidental sharing
of mutable style references across cells, columns, or rows.
"""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.elements.text import TextAlignment
from reporting.layout.geometry import Edges
from reporting.styles.colors import ColorValue, normalize_color


@dataclasses.dataclass(frozen=True)
class CellStyle:
    """Per-cell styling overrides. None means "use parent/default"."""

    background_color: Optional[ColorValue] = None
    text_color: Optional[ColorValue] = None
    border_color: Optional[ColorValue] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'background_color', normalize_color(self.background_color) if self.background_color is not None else None)
        object.__setattr__(self, 'text_color', normalize_color(self.text_color) if self.text_color is not None else None)
        object.__setattr__(self, 'border_color', normalize_color(self.border_color) if self.border_color is not None else None)


@dataclasses.dataclass(frozen=True)
class ColumnStyle:
    """Per-column styling defaults. Applied to each cell in the column."""

    background_color: Optional[ColorValue] = None
    text_color: Optional[ColorValue] = None
    border_color: Optional[ColorValue] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'background_color', normalize_color(self.background_color) if self.background_color is not None else None)
        object.__setattr__(self, 'text_color', normalize_color(self.text_color) if self.text_color is not None else None)
        object.__setattr__(self, 'border_color', normalize_color(self.border_color) if self.border_color is not None else None)


@dataclasses.dataclass(frozen=True)
class RowStyle:
    """Per-column styling defaults. Applied to each cell in the row."""

    background_color: Optional[ColorValue] = None
    text_color: Optional[ColorValue] = None
    border_color: Optional[ColorValue] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'background_color', normalize_color(self.background_color) if self.background_color is not None else None)
        object.__setattr__(self, 'text_color', normalize_color(self.text_color) if self.text_color is not None else None)
        object.__setattr__(self, 'border_color', normalize_color(self.border_color) if self.border_color is not None else None)


@dataclasses.dataclass(frozen=True)
class TableStyle:
    """Top-level table-wide style defaults."""

    zebra: bool = False
    even_row_color: ColorValue = "#F3F3F3"
    odd_row_color: ColorValue = "#FFFFFF"
    header_background: ColorValue = "#4472C4"
    header_text_color: ColorValue = "#FFFFFF"
    border_color: ColorValue = "#D9D9D9"
    border_width: float = 0.5
    font_name: str = "Helvetica"
    font_size: float = 10.0
    header_font_size: float = 11.0
    padding: Edges = dataclasses.field(default_factory=lambda: Edges.all(4.0))
    highlight_max_color: ColorValue = "#C6EFCE"
    highlight_min_color: ColorValue = "#FFC7CE"

    def __post_init__(self) -> None:
        object.__setattr__(self, 'even_row_color', normalize_color(self.even_row_color))
        object.__setattr__(self, 'odd_row_color', normalize_color(self.odd_row_color))
        object.__setattr__(self, 'header_background', normalize_color(self.header_background))
        object.__setattr__(self, 'header_text_color', normalize_color(self.header_text_color))
        object.__setattr__(self, 'border_color', normalize_color(self.border_color))
        object.__setattr__(self, 'highlight_max_color', normalize_color(self.highlight_max_color))
        object.__setattr__(self, 'highlight_min_color', normalize_color(self.highlight_min_color))
