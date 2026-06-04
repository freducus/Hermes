"""TableBuilder — fluent builder API for TableSpec.

Usage::

    table = (
        TableBuilder()
        .column("Case")
        .column("Mach")
        .column("Efficiency")
        .row("A", 0.8, 0.92)
        .row("B", 0.9, 0.94)
        .zebra()
        .build()
    )
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from reporting.tablespec.column import Column
from reporting.tablespec.exceptions import TableSpecError
from reporting.tablespec.sizing import ColumnDistrib, TableFitMode, TableSizing
from reporting.tablespec.spec import TableSpec
from reporting.tablespec.style import TableStyle


class TableBuilder:
    """Fluent builder that constructs a TableSpec via chained calls.

    Call ``.build()`` at the end to produce the final ``TableSpec``.
    """

    def __init__(self) -> None:
        self._columns: list[Column] = []
        self._rows: list[tuple[Any, ...]] = []
        self._style: TableStyle = TableStyle()
        self._sizing: TableSizing = TableSizing()
        self._highlights: list[tuple[str, str]] = []  # (method, column)
        self._heatmaps: list[str] = []
        self._zebra: bool = False

    def column(
        self,
        name: str,
        label: Optional[str] = None,
        width: Optional[float] = None,
        width_ratio: Optional[float] = None,
        format: Optional[str] = None,
        formatter: Optional[Callable[[Any], str]] = None,
        alignment: Optional[object] = None,
        visible: bool = True,
    ) -> TableBuilder:
        """Define a column."""
        col = Column(
            name=name,
            label=label,
            width=width,
            width_ratio=width_ratio,
            format=format,
            formatter=formatter,
            alignment=alignment,
            visible=visible,
        )
        self._columns.append(col)
        return self

    def row(self, *values: Any, **kwargs: Any) -> TableBuilder:
        """Add a row of values."""
        self._rows.append((values, kwargs))
        return self

    def sizing(
        self,
        mode: TableFitMode = TableFitMode.STRETCH,
        min_font_size: Optional[float] = None,
        percent_width: float = 1.0,
        column_distrib: ColumnDistrib = ColumnDistrib.CONTENT,
    ) -> TableBuilder:
        """Set the table sizing configuration.

        Args:
            mode: Sizing strategy (default: ``TableFitMode.STRETCH``).
            min_font_size: Override ``TableStyle.min_font_size``.
            percent_width: Fraction of available width to use in PERCENT mode.
            column_distrib: How columns are distributed.
        """
        self._sizing = TableSizing(
            fit_mode=mode,
            min_font_size=min_font_size,
            percent_width=percent_width,
            column_distrib=column_distrib,
        )
        return self

    def highlight_max(self, column: str) -> TableBuilder:
        """Mark *column* for max-highlighting."""
        self._highlights.append(("max", column))
        return self

    def highlight_min(self, column: str) -> TableBuilder:
        """Mark *column* for min-highlighting."""
        self._highlights.append(("min", column))
        return self

    def heatmap(self, column: str) -> TableBuilder:
        """Mark *column* for heatmap formatting."""
        self._heatmaps.append(column)
        return self

    def zebra(self) -> TableBuilder:
        """Enable zebra striping."""
        self._zebra = True
        return self

    def build(self) -> TableSpec:
        """Construct and return the final TableSpec.

        Raises:
            TableSpecError: if there are no columns defined.
        """
        if not self._columns:
            raise TableSpecError("TableBuilder needs at least one column")

        table = TableSpec(columns=self._columns, style=self._style, sizing=self._sizing)

        for values, kwargs in self._rows:
            if kwargs:
                table.add_row(**kwargs)
            else:
                table.add_row(*values)

        if self._zebra:
            table.zebra()

        for method, col_name in self._highlights:
            if method == "max":
                table.highlight_max(col_name)
            elif method == "min":
                table.highlight_min(col_name)

        for col_name in self._heatmaps:
            table.heatmap(col_name)

        return table
