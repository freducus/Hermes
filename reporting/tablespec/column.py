"""Column entity — defines a single column's schema and style."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from reporting.elements.text import TextAlignment
from reporting.tablespec.style import ColumnStyle


class Column:
    """A column definition within a TableSpec.

    Attributes:
        name: Internal identifier (must be unique within a table).
        label: Visual header text; defaults to *name* if not provided.
        width: Fixed width in points (px-equivalent units).
        width_ratio: Relative width (e.g. 2.0 = twice the default).
        format: Python format string, e.g. ``"{:.2%}"``.
        formatter: Custom callable ``(value) -> str``.
        alignment: Default text alignment for cells in this column.
        visible: Whether this column appears in output.
        style: Optional per-column style defaults.
    """

    def __init__(
        self,
        name: str,
        label: Optional[str] = None,
        width: Optional[float] = None,
        width_ratio: Optional[float] = None,
        format: Optional[str] = None,
        formatter: Optional[Callable[[Any], str]] = None,
        alignment: Optional[TextAlignment] = None,
        visible: bool = True,
        style: Optional[ColumnStyle] = None,
    ) -> None:
        self.name = name
        self.label = label or name
        self.width = width
        self.width_ratio = width_ratio
        self.format = format
        self.formatter = formatter
        self.alignment = alignment
        self.visible = visible
        self.style = style

    def __repr__(self) -> str:
        return f"Column({self.name!r})"

    def set_format(self, fmt: str) -> Column:
        """Set the format string and return self for chaining."""
        self.format = fmt
        return self

    def set_formatter(self, func: Callable[[Any], str]) -> Column:
        """Set a custom formatter callable and return self for chaining."""
        self.formatter = func
        return self
