"""TableCell — a single cell within a TableSpec."""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

from reporting.elements.text import TextAlignment
from reporting.styles.colors import ColorValue, normalize_color
from reporting.tablespec.style import CellStyle


@dataclasses.dataclass
class TableCell:
    """A single cell in a ``TableSpec`` table.

    Cells are created automatically by ``TableSpec.add_row()``.
    For merged cells, set ``rowspan`` / ``colspan`` after
    creation.

    Args:
        value: The raw cell value (any type; default ``None``).
        text: Display text.  If ``None``, the ``TableSpec``
            computes it from ``value`` and the column's
            format / formatter (default ``None``).
        rowspan: Number of rows this cell spans (>= 1;
            default ``1``).
        colspan: Number of columns this cell spans (>= 1;
            default ``1``).
        alignment: Per-cell alignment override
            (default ``None``).
        background_color: Per-cell background colour override
            (default ``None``).
        text_color: Per-cell text colour override
            (default ``None``).
        style: Per-cell ``CellStyle`` override
            (default ``None``).

    Example::

        from reporting.tablespec.cell import TableCell

        cell = TableCell(value=42, text="42.0")
        merged = TableCell(value="Header", colspan=3)
    """
    value: Any = None
    text: Optional[str] = None
    rowspan: int = 1
    colspan: int = 1
    alignment: Optional[TextAlignment] = None
    background_color: Optional[ColorValue] = None
    text_color: Optional[ColorValue] = None
    style: Optional[CellStyle] = None

    def __post_init__(self) -> None:
        self.background_color = normalize_color(self.background_color) if self.background_color is not None else None
        self.text_color = normalize_color(self.text_color) if self.text_color is not None else None

    def __repr__(self) -> str:
        if self.text is not None:
            return f"TableCell({self.text!r})"
        return f"TableCell(value={self.value!r})"

    @property
    def display_text(self) -> str:
        """Return the display text or stringified value.

        Returns:
            The explicit ``text`` if set, otherwise
            ``str(value)``, otherwise ``""``.
        """
        if self.text is not None:
            return self.text
        if self.value is not None:
            return str(self.value)
        return ""


# Backward-compatible alias
Cell = TableCell
