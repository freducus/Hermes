"""Style primitives for TableSpec — CellStyle, ColumnStyle, RowStyle, TableStyle.

All style dataclasses are frozen (immutable) to prevent accidental sharing
of mutable style references across cells, columns, or rows.
"""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.elements.text import TextAlignment
from reporting.layout.geometry import Edges


@dataclasses.dataclass(frozen=True)
class CellStyle:
    """Per-cell styling overrides. None means "use parent/default"."""

    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None


@dataclasses.dataclass(frozen=True)
class ColumnStyle:
    """Per-column styling defaults. Applied to each cell in the column."""

    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None


@dataclasses.dataclass(frozen=True)
class RowStyle:
    """Per-row styling defaults. Applied to each cell in the row."""

    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None


@dataclasses.dataclass(frozen=True)
class TableStyle:
    """Top-level table-wide style defaults."""

    zebra: bool = False
    even_row_color: str = "#F3F3F3"
    odd_row_color: str = "#FFFFFF"
    header_background: str = "#4472C4"
    header_text_color: str = "#FFFFFF"
    border_color: str = "#D9D9D9"
    border_width: float = 0.5
    font_name: str = "Helvetica"
    font_size: float = 10.0
    header_font_size: float = 11.0
    padding: Edges = dataclasses.field(default_factory=lambda: Edges.all(4.0))
    highlight_max_color: str = "#C6EFCE"
    highlight_min_color: str = "#FFC7CE"
