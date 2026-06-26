"""Named layout configurations stored in themes.

A ``LayoutConfig`` is a pure-data description of a grid layout
(rows, columns, sizing, gap, padding).  Themes hold a dict of
named layouts, and ``SlideTypeConfig`` references one by name.
"""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.layout.geometry import Edges
from reporting.layout.sizing import Sizing


@dataclasses.dataclass
class LayoutConfig:
    """A named grid layout configuration.

    Stored in ``Theme.layouts`` and referenced by
    ``SlideTypeConfig.layout``.

    Args:
        name: Layout name used as key in ``Theme.layouts``.
        rows: Number of rows (default ``1``).
        cols: Number of columns (default ``1``).
        row_sizes: Per-row sizing.  Each element can be
            ``Px(v)``, ``Percent(v)``, ``Fill``, or a plain
            float (treated as ``Px(v)``).  When ``None``,
            all rows use ``Fill`` (default ``None``).
        col_sizes: Per-column sizing, same rules as
            ``row_sizes`` (default ``None``).
        gap: Spacing between cells in pixels (default ``0.0``).
        padding: Outer padding around the grid as an
            ``Edges``.  ``Edges.all(v)`` sets uniform
            padding (default ``None`` = no padding).

    Example::

        from reporting.layout_config import LayoutConfig
        from reporting.layout.sizing import Px, Fill

        cfg = LayoutConfig(
            name="two_by_two",
            rows=2, cols=2, gap=8,
            row_sizes=[Px(100), Fill],
            col_sizes=[Fill, Fill],
        )
    """

    name: str
    rows: int = 1
    cols: int = 1
    row_sizes: Optional[list[Sizing]] = None
    col_sizes: Optional[list[Sizing]] = None
    gap: float = 0.0
    padding: Optional[Edges] = None


__all__ = ["LayoutConfig"]
