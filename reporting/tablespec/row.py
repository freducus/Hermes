"""Row entity — a single row within a TableSpec."""

from __future__ import annotations

from typing import Any, Optional

from reporting.tablespec.cell import Cell
from reporting.tablespec.style import RowStyle


class Row:
    """A row in a TableSpec table.

    Attributes:
        cells: Ordered list of Cell objects, one per visible column.
        style: Optional per-row style defaults.
        group: Name of the group this row belongs to (for hierarchical tables).
        metadata: Arbitrary key-value metadata attached to this row.
    """

    def __init__(
        self,
        cells: Optional[list[Cell]] = None,
        style: Optional[RowStyle] = None,
        group: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        self.cells = cells or []
        self.style = style
        self.group = group
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"Row(cells={len(self.cells)}, group={self.group!r})"
