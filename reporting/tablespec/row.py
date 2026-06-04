"""TableRow — a single row within a TableSpec."""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

from reporting.tablespec.cell import TableCell
from reporting.tablespec.style import RowStyle


@dataclasses.dataclass
class TableRow:
    """A single row in a ``TableSpec`` table.

    Rows are created automatically by ``TableSpec.add_row()``
    and ``TableSpec.row()``.

    Args:
        cells: List of ``TableCell`` objects, one per visible
            column (default empty list).
        style: Per-row ``RowStyle`` overrides
            (default ``None``).
        group: Group name for hierarchical / grouped tables
            (default ``None``).
        metadata: Arbitrary key-value metadata attached to
            this row (default empty dict).

    Example::

        from reporting.tablespec.row import TableRow
        from reporting.tablespec.cell import TableCell

        row = TableRow(cells=[
            TableCell(value="Case A"),
            TableCell(value=0.85),
        ])
    """
    cells: list[TableCell] = dataclasses.field(default_factory=list)
    style: Optional[RowStyle] = None
    group: Optional[str] = None
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __repr__(self) -> str:
        return f"TableRow(cells={len(self.cells)}, group={self.group!r})"


# Backward-compatible alias
Row = TableRow
