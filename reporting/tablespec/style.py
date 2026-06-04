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
    """Per-cell styling overrides within a ``TableSpec``.

    Every field defaults to ``None``, meaning "use parent/default"
    (inherits from ``RowStyle`` → ``ColumnStyle`` → ``TableStyle``).

    Args:
        background_color: Cell background colour
            (default ``None``).
        text_color: Cell text colour (default ``None``).
        border_color: Cell border colour (default ``None``).
        border_width: Cell border width in points
            (default ``None``).
        font_name: Font family (default ``None``).
        font_size: Font size in points (default ``None``).
        alignment: ``TextAlignment`` (default ``None``).
        padding: ``Edges`` padding (default ``None``).
        bold: Bold override (default ``None``).
        italic: Italic override (default ``None``).
        underline: Underline override (default ``None``).
        align_h: Horizontal alignment string — ``"left"``,
            ``"center"``, ``"right"`` (default ``None``).
        align_v: Vertical alignment string — ``"top"``,
            ``"middle"``, ``"bottom"`` (default ``None``).
    """
    background_color: Optional[ColorValue] = None
    text_color: Optional[ColorValue] = None
    border_color: Optional[ColorValue] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    align_h: Optional[str] = None  # "left", "center", "right"
    align_v: Optional[str] = None  # "top", "middle", "bottom"

    def __post_init__(self) -> None:
        object.__setattr__(self, "background_color", normalize_color(self.background_color) if self.background_color is not None else None)
        object.__setattr__(self, "text_color", normalize_color(self.text_color) if self.text_color is not None else None)
        object.__setattr__(self, "border_color", normalize_color(self.border_color) if self.border_color is not None else None)


@dataclasses.dataclass(frozen=True)
class ColumnStyle:
    """Per-column styling defaults applied to each cell in the column.

    Fields match ``CellStyle``; all default to ``None``.

    Args:
        background_color: Column background colour
            (default ``None``).
        text_color: Column text colour (default ``None``).
        border_color: Column border colour (default ``None``).
        border_width: Border width in points (default ``None``).
        font_name: Font family (default ``None``).
        font_size: Font size (default ``None``).
        alignment: ``TextAlignment`` (default ``None``).
        padding: ``Edges`` padding (default ``None``).
        bold: Bold override (default ``None``).
        italic: Italic override (default ``None``).
        underline: Underline override (default ``None``).
        align_h: Horizontal alignment string (default ``None``).
        align_v: Vertical alignment string (default ``None``).
    """
    background_color: Optional[ColorValue] = None
    text_color: Optional[ColorValue] = None
    border_color: Optional[ColorValue] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    align_h: Optional[str] = None
    align_v: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "background_color", normalize_color(self.background_color) if self.background_color is not None else None)
        object.__setattr__(self, "text_color", normalize_color(self.text_color) if self.text_color is not None else None)
        object.__setattr__(self, "border_color", normalize_color(self.border_color) if self.border_color is not None else None)


@dataclasses.dataclass(frozen=True)
class RowStyle:
    """Per-row styling defaults applied to each cell in the row.

    Fields match ``CellStyle``; all default to ``None``.

    Args:
        background_color: Row background colour
            (default ``None``).
        text_color: Row text colour (default ``None``).
        border_color: Row border colour (default ``None``).
        border_width: Border width in points (default ``None``).
        font_name: Font family (default ``None``).
        font_size: Font size (default ``None``).
        alignment: ``TextAlignment`` (default ``None``).
        padding: ``Edges`` padding (default ``None``).
        bold: Bold override (default ``None``).
        italic: Italic override (default ``None``).
        underline: Underline override (default ``None``).
        align_h: Horizontal alignment string (default ``None``).
        align_v: Vertical alignment string (default ``None``).
    """
    background_color: Optional[ColorValue] = None
    text_color: Optional[ColorValue] = None
    border_color: Optional[ColorValue] = None
    border_width: Optional[float] = None
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    alignment: Optional[TextAlignment] = None
    padding: Optional[Edges] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    align_h: Optional[str] = None
    align_v: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "background_color", normalize_color(self.background_color) if self.background_color is not None else None)
        object.__setattr__(self, "text_color", normalize_color(self.text_color) if self.text_color is not None else None)
        object.__setattr__(self, "border_color", normalize_color(self.border_color) if self.border_color is not None else None)


@dataclasses.dataclass(frozen=True)
class TableStyle:
    """Top-level table-wide style defaults for a ``TableSpec``.

    These values apply to the entire table unless overridden
    by a ``RowStyle``, ``ColumnStyle``, or ``CellStyle``.

    Args:
        zebra: Enable alternating row colours
            (default ``False``).
        even_row_color: Even-row background colour
            (default ``"#E8E8E8"``).
        odd_row_color: Odd-row background colour
            (default ``"#FFFFFF"``).
        header_background: Header row background colour
            (default ``"#4472C4"``).
        header_text_color: Header row text colour
            (default ``"#FFFFFF"``).
        border_color: Grid border colour
            (default ``"#D9D9D9"``).
        border_width: Grid border width in points
            (default ``0.5``).
        font_name: Base font family (default ``"Helvetica"``).
        font_size: Base font size in points (default ``10.0``).
        header_font_size: Header font size in points
            (default ``11.0``).
        padding: Cell padding as ``Edges``
            (default ``Edges.all(4.0)``).
        highlight_max_color: Colour for ``highlight_max``
            (default ``"#C6EFCE"``).
        highlight_min_color: Colour for ``highlight_min``
            (default ``"#FFC7CE"``).
        header_rows: Number of header rows at the top
            (default ``1``).
        min_font_size: Minimum font size for
            ``SHRINK_FONT`` mode (default ``4.0``).
        line_height: Multiplier for row height estimation
            (default ``1.2``).

    Example::

        from reporting.tablespec.style import TableStyle

        style = TableStyle(
            zebra=True,
            font_name="Arial",
            font_size=9.0,
            header_background="#1F4E79",
        )
    """
    zebra: bool = False
    even_row_color: ColorValue = "#E8E8E8"
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
    header_rows: int = 1
    min_font_size: float = 4.0
    """Minimum font size in points for ``SHRINK_FONT`` mode."""
    line_height: float = 1.2
    """Multiplier applied to font size to estimate row height."""

    def __post_init__(self) -> None:
        object.__setattr__(self, "even_row_color", normalize_color(self.even_row_color))
        object.__setattr__(self, "odd_row_color", normalize_color(self.odd_row_color))
        object.__setattr__(self, "header_background", normalize_color(self.header_background))
        object.__setattr__(self, "header_text_color", normalize_color(self.header_text_color))
        object.__setattr__(self, "border_color", normalize_color(self.border_color))
        object.__setattr__(self, "highlight_max_color", normalize_color(self.highlight_max_color))
        object.__setattr__(self, "highlight_min_color", normalize_color(self.highlight_min_color))
