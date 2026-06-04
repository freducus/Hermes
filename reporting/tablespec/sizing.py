"""Table sizing modes — TableFitMode, ColumnDistrib, and TableSizing.

Controls how a table occupies its allocated space:

- ``STRETCH``: fill available space, keep font size unchanged.
- ``SHRINK_FONT``: reduce font size (down to *min_font_size*) if content
  overflows the available height or width.
- ``PERCENT``: occupy *percent_width* of the available width; the
  container (Panel with ``HAlign``) handles alignment.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional


class TableFitMode(Enum):
    """How a table sizes itself within its allocated rectangle.

    Members:
        STRETCH: Fill available space. Column widths are
            content-aware (proportional to text width). Font
            size stays at ``TableStyle.font_size``.
            This is the default.
        SHRINK_FONT: Start at ``TableStyle.font_size`` but
            shrink the font proportionally if the natural
            content width or height exceeds the available
            space. Never goes below ``min_font_size``.
        PERCENT: Use ``percent_width`` of the available
            width for column distribution. The container
            (Panel) handles alignment.
    """
    STRETCH = "stretch"
    SHRINK_FONT = "shrink_font"
    PERCENT = "percent"


class ColumnDistrib(Enum):
    """How columns are distributed within the table's width.

    Members:

        CONTENT
            Proportional to measured text width (default).
        EQUAL
            All columns get equal width.
        FIXED
            Use ``Column.width`` where set; remaining space
            split equally.
    """
    CONTENT = "content"
    EQUAL = "equal"
    FIXED = "fixed"


@dataclasses.dataclass(frozen=True)
class TableSizing:
    """Per-table sizing configuration for a ``TableSpec``.

    ``min_font_size`` here overrides ``TableStyle.min_font_size``.
    ``percent_width`` is only meaningful when ``fit_mode == PERCENT``.

    Args:
        fit_mode: The sizing strategy
            (default ``TableFitMode.STRETCH``).
        min_font_size: Override ``TableStyle.min_font_size``
            for this table (default ``None``).
        percent_width: Fraction of available width to use when
            ``fit_mode == PERCENT`` (default ``1.0``).
        column_distrib: How columns are distributed within the
            table width (default ``ColumnDistrib.CONTENT``).

    Example::

        from reporting.tablespec.sizing import (
            TableSizing, TableFitMode, ColumnDistrib,
        )

        sizing = TableSizing(
            fit_mode=TableFitMode.SHRINK_FONT,
            min_font_size=5.0,
            column_distrib=ColumnDistrib.FIXED,
        )
    """
    fit_mode: TableFitMode = TableFitMode.STRETCH
    min_font_size: Optional[float] = None
    percent_width: float = 1.0
    column_distrib: ColumnDistrib = ColumnDistrib.CONTENT
