"""Cell entity — a single cell within a TableSpec row."""

from __future__ import annotations

from typing import Any, Optional

from reporting.elements.text import TextAlignment
from reporting.tablespec.style import CellStyle


class Cell:
    """A single cell in a TableSpec table.

    Attributes:
        value: The raw cell value (any type).
        text: Display text. If None, it will be computed by TableSpec
            from *value* and the column's format/formatter at row-insertion time.
        rowspan: Number of rows this cell spans (>= 1).
        colspan: Number of columns this cell spans (>= 1).
        alignment: Per-cell alignment override.
        background_color: Per-cell background override.
        text_color: Per-cell text color override.
        style: Optional per-cell style override.
    """

    def __init__(
        self,
        value: Any = None,
        text: Optional[str] = None,
        rowspan: int = 1,
        colspan: int = 1,
        alignment: Optional[TextAlignment] = None,
        background_color: Optional[str] = None,
        text_color: Optional[str] = None,
        style: Optional[CellStyle] = None,
    ) -> None:
        self.value = value
        self.text = text
        self.rowspan = rowspan
        self.colspan = colspan
        self.alignment = alignment
        self.background_color = background_color
        self.text_color = text_color
        self.style = style

    def __repr__(self) -> str:
        if self.text is not None:
            return f"Cell({self.text!r})"
        return f"Cell(value={self.value!r})"
