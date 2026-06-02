"""TableSpec — professional table data model.

Zero pandas/polars dependency; those are optional data sources
loaded via classmethods with ``try/except ImportError``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Optional, Union

from reporting.tablespec.cell import Cell
from reporting.tablespec.column import Column
from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    InvalidRowError,
    InvalidSpanError,
)
from reporting.tablespec.formatters import apply_custom_formatter, apply_format
from reporting.tablespec.row import Row
from reporting.tablespec.style import TableStyle
from reporting.tablespec.validation import (
    resolve_column_index,
    validate_columns,
    validate_row_values,
    validate_span,
)


class TableSpec:
    """A flexible, backend-agnostic table data model.

    Usage::

        table = TableSpec(
            columns=[
                Column("Case"),
                Column("Mach"),
                Column("Efficiency"),
            ]
        )
        table.add_row("Case A", 0.80, 0.92)
        table.add_row("Case B", 0.90, 0.94)
    """

    def __init__(
        self,
        columns: Optional[list[Column]] = None,
        rows: Optional[list[Row]] = None,
        style: Optional[TableStyle] = None,
    ) -> None:
        self.columns: list[Column] = list(columns) if columns else []
        self.rows: list[Row] = list(rows) if rows else []
        self.style: TableStyle = style or TableStyle()
        self._current_group: Optional[str] = None
        validate_columns(self.columns)

    # ------------------------------------------------------------------
    # Fluent builder helpers
    # ------------------------------------------------------------------

    def add_column(
        self,
        name: str,
        label: Optional[str] = None,
        width: Optional[float] = None,
        width_ratio: Optional[float] = None,
        format: Optional[str] = None,
        formatter: Optional[Callable[[Any], str]] = None,
        alignment: Optional[object] = None,
        visible: bool = True,
        style: Optional[object] = None,
    ) -> TableSpec:
        """Add a column and return self for chaining."""
        from reporting.tablespec.style import ColumnStyle

        col = Column(
            name=name,
            label=label,
            width=width,
            width_ratio=width_ratio,
            format=format,
            formatter=formatter,
            alignment=alignment,
            visible=visible,
            style=style,
        )
        validate_columns(self.columns + [col])
        self.columns.append(col)
        return self

    def add_row(self, *values: Any, **kwargs: Any) -> TableSpec:
        """Add a row and return self for chaining.

        Accepts positional values (one per column) or keyword arguments
        mapping column names to values.
        """
        if values and kwargs:
            raise InvalidRowError("Provide positional values OR keyword arguments, not both")

        if kwargs:
            values = tuple(self._resolve_kwargs(kwargs))
        else:
            validate_row_values(values, len(self.columns))

        cells: list[Cell] = []
        for col, val in zip(self.columns, values):
            text: Optional[str] = None
            if col.format is not None:
                text = apply_format(val, col.format)
            elif col.formatter is not None:
                text = apply_custom_formatter(val, col.formatter)
            cells.append(Cell(value=val, text=text))

        self.rows.append(Row(cells=cells, group=self._current_group))
        return self

    def _resolve_kwargs(self, kwargs: dict[str, Any]) -> list[Any]:
        """Map keyword argument names to column order."""
        resolved: list[Any] = [None] * len(self.columns)
        used = set(kwargs.keys())
        col_names = {c.name for c in self.columns}
        unknown = used - col_names
        if unknown:
            raise ColumnNotFoundError(
                f"Unknown column(s): {', '.join(sorted(unknown))}"
            )
        for col in self.columns:
            if col.name in kwargs:
                resolved[self.columns.index(col)] = kwargs[col.name]
            else:
                resolved[self.columns.index(col)] = None
        return resolved

    def cell(
        self,
        row: int,
        col: int,
        value: Any = None,
        text: Optional[str] = None,
        rowspan: int = 1,
        colspan: int = 1,
        alignment: Optional[object] = None,
        background_color: Optional[str] = None,
        text_color: Optional[str] = None,
        style: Optional[object] = None,
    ) -> TableSpec:
        """Modify a specific cell in the table.

        Useful for setting spans or per-cell overrides after row insertion.
        """
        if row < 0 or row >= len(self.rows):
            raise InvalidRowError(f"Row index {row} out of range (0..{len(self.rows) - 1})")
        if col < 0 or col >= len(self.columns):
            raise InvalidRowError(f"Column index {col} out of range (0..{len(self.columns) - 1})")

        validate_span(row, col, rowspan, colspan, len(self.rows), len(self.columns))

        from reporting.tablespec.style import CellStyle

        existing = self.rows[row].cells[col]
        existing.value = value
        existing.text = text
        existing.rowspan = rowspan
        existing.colspan = colspan
        existing.alignment = alignment
        existing.background_color = background_color
        existing.text_color = text_color
        if style is not None:
            existing.style = style
        return self

    def column(self, name: str) -> Column:
        """Return the Column with the given name (for chained configuration).

        Usage::

            table.column("Mach").set_format("{:.3f}")
            table.column("Efficiency").set_formatter(lambda x: f"{x*100:.1f}%")
        """
        for col in self.columns:
            if col.name == name:
                return col
        raise ColumnNotFoundError(f"Column {name!r} not found")

    def group(self, name: str) -> TableSpec:
        """Set the current group name.

        All subsequent ``add_row()`` calls will belong to this group
        until ``group()`` is called again with a different name.
        """
        self._current_group = name
        return self

    # ------------------------------------------------------------------
    # Conditional formatting
    # ------------------------------------------------------------------

    def highlight_max(self, column: str) -> TableSpec:
        """Highlight the maximum value in *column* with a green background."""
        col_idx = resolve_column_index(self.columns, column)
        col_vals: list[tuple[int, Any]] = []
        for r, row in enumerate(self.rows):
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    col_vals.append((r, val))
        if not col_vals:
            return self
        max_row = max(col_vals, key=lambda x: x[1])[0]
        self.rows[max_row].cells[col_idx].background_color = self.style.highlight_max_color
        return self

    def highlight_min(self, column: str) -> TableSpec:
        """Highlight the minimum value in *column* with a red background."""
        col_idx = resolve_column_index(self.columns, column)
        col_vals: list[tuple[int, Any]] = []
        for r, row in enumerate(self.rows):
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    col_vals.append((r, val))
        if not col_vals:
            return self
        min_row = min(col_vals, key=lambda x: x[1])[0]
        self.rows[min_row].cells[col_idx].background_color = self.style.highlight_min_color
        return self

    def heatmap(self, column: str) -> TableSpec:
        """Apply a green-to-red heatmap to *column*."""
        col_idx = resolve_column_index(self.columns, column)
        col_vals: list[float] = []
        for row in self.rows:
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    col_vals.append(float(val))
        if not col_vals:
            return self
        mn, mx = min(col_vals), max(col_vals)
        span = mx - mn or 1.0

        for row in self.rows:
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    ratio = (float(val) - mn) / span
                    r_ = int(255 * ratio)
                    g_ = int(255 * (1 - ratio))
                    row.cells[col_idx].background_color = f"#{r_:02X}{g_:02X}00"

        return self

    def zebra(self) -> TableSpec:
        """Enable alternating row colors."""
        self.style = TableStyle(zebra=True)
        return self

    # ------------------------------------------------------------------
    # Classmethod constructors (optional dependencies)
    # ------------------------------------------------------------------

    @classmethod
    def from_dataframe(cls, df: Any, **kwargs: Any) -> TableSpec:
        """Build a TableSpec from a pandas DataFrame.

        Args:
            df: A ``pandas.DataFrame``.
            **kwargs: Passed through to ``TableSpec()``.

        Raises:
            ImportError: if pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for from_dataframe()") from None

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas.DataFrame, got {type(df).__name__}")

        columns = [Column(name=str(c)) for c in df.columns]
        table = cls(columns=columns, **kwargs)

        for _, row in df.iterrows():
            values = tuple(row[c] for c in df.columns)
            table.add_row(*values)

        return table

    @classmethod
    def from_polars(cls, df: Any, **kwargs: Any) -> TableSpec:
        """Build a TableSpec from a Polars DataFrame.

        Args:
            df: A ``polars.DataFrame`` or ``polars.LazyFrame``.
            **kwargs: Passed through to ``TableSpec()``.

        Raises:
            ImportError: if polars is not installed.
        """
        try:
            import polars as pl
        except ImportError:
            raise ImportError("polars is required for from_polars()") from None

        if not isinstance(df, (pl.DataFrame, pl.LazyFrame)):
            raise TypeError(f"Expected polars DataFrame/LazyFrame, got {type(df).__name__}")

        if isinstance(df, pl.LazyFrame):
            df = df.collect()

        columns = [Column(name=str(c)) for c in df.columns]
        table = cls(columns=columns, **kwargs)

        for row in df.iter_rows():
            table.add_row(*row)

        return table

    @classmethod
    def from_records(
        cls,
        records: list[dict[str, Any]],
        **kwargs: Any,
    ) -> TableSpec:
        """Build a TableSpec from a list of dicts (records).

        Column order is inferred from the first record's keys.
        """
        if not records:
            raise ValueError("from_records() requires at least one record")

        columns = [Column(name=str(k)) for k in records[0]]
        table = cls(columns=columns, **kwargs)

        for rec in records:
            values = tuple(rec.get(c.name) for c in columns)
            table.add_row(*values)

        return table

    @classmethod
    def from_dataclasses(
        cls,
        instances: list[Any],
        **kwargs: Any,
    ) -> TableSpec:
        """Build a TableSpec from a list of dataclass instances.

        Field names become column names.
        """
        import dataclasses

        if not instances:
            raise ValueError("from_dataclasses() requires at least one instance")

        fields = dataclasses.fields(instances[0])
        columns = [Column(name=f.name, label=f.name.replace("_", " ").title()) for f in fields]
        table = cls(columns=columns, **kwargs)

        for inst in instances:
            values = tuple(getattr(inst, f.name) for f in fields)
            table.add_row(*values)

        return table

    # ------------------------------------------------------------------
    # Serialization / export
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict.

        Returns:
            Dictionary with keys ``"columns"``, ``"rows"``, and ``"style"``.
        """
        return {
            "columns": [
                {
                    "name": c.name,
                    "label": c.label,
                    "width": c.width,
                    "width_ratio": c.width_ratio,
                    "format": c.format,
                    "alignment": c.alignment.name if c.alignment else None,
                    "visible": c.visible,
                }
                for c in self.columns
            ],
            "rows": [
                {
                    "group": r.group,
                    "cells": [
                        {
                            "value": cell.value,
                            "text": cell.text,
                            "rowspan": cell.rowspan,
                            "colspan": cell.colspan,
                        }
                        for cell in r.cells
                    ],
                }
                for r in self.rows
            ],
            "style": {
                "zebra": self.style.zebra,
                "font_name": self.style.font_name,
                "font_size": self.style.font_size,
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def to_records(self) -> list[dict[str, Any]]:
        """Export rows as a list of dicts (column name -> display text)."""
        records: list[dict[str, Any]] = []
        for row in self.rows:
            rec: dict[str, Any] = {}
            for col, cell in zip(self.columns, row.cells):
                rec[col.name] = cell.text if cell.text is not None else cell.value
            records.append(rec)
        return records

    def to_dataframe(self) -> Any:
        """Export to a pandas DataFrame.

        Raises:
            ImportError: if pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for to_dataframe()") from None

        return pd.DataFrame(self.to_records())
