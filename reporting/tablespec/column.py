"""Column entity — defines a single column's schema and style."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from reporting.elements.text import TextAlignment
from reporting.tablespec.style import ColumnStyle


class Column:
    """A column definition within a ``TableSpec``.

    Args:
        name: Column identifier (must be unique within a table).
        label: Visual header text; defaults to ``name`` if
            not provided (default ``None``).
        width: Fixed width in points (default ``None``).
        width_ratio: Relative width factor (e.g. ``2.0`` =
            twice the default; default ``None``).
        format: Python format string for display, e.g.
            ``"{:.2%}"`` (default ``None``).
        formatter: Custom callable ``(value) -> display_text``
            (default ``None``).
        alignment: Default ``TextAlignment`` for cells
            (default ``None``).
        visible: Whether the column appears in rendered output
            (default ``True``).
        style: Per-column ``ColumnStyle`` overrides
            (default ``None``).

    Example::

        from reporting.tablespec.column import Column

        col = Column("Efficiency",
                     label="Eff. (%)",
                     format="{:.1%}",
                     width=80)
        col2 = Column("Temperature",
                      formatter=lambda v: f"{v:.0f}°C")
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
        """Set the format string and return ``self`` for chaining.

        Args:
            fmt: Python format string (e.g. ``"{:.3f}"``).

        Returns:
            ``self`` for chaining.
        """
        self.format = fmt
        return self

    def set_formatter(self, func: Callable[[Any], str]) -> Column:
        """Set a custom formatter callable and return ``self`` for chaining.

        Args:
            func: A callable ``(value) -> display_text``.

        Returns:
            ``self`` for chaining.
        """
        self.formatter = func
        return self
