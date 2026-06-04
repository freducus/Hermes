"""TableSpec — professional table data model.

Zero pandas/polars dependency; those are optional data sources
loaded via classmethods with ``try/except ImportError``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Optional, Union

from reporting.tablespec.cell import TableCell
from reporting.tablespec.column import Column
from reporting.tablespec.conditional import (
    CellCondition,
    HeatmapDef,
    HighlightExtremeDef,
    resolve_conditional_styles,
    resolve_extreme_styles,
)
from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    InvalidRowError,
    InvalidSpanError,
)
from reporting.tablespec.formatters import apply_custom_formatter, apply_format
from reporting.tablespec.range_parser import parse_coord, parse_range
from reporting.tablespec.row import TableRow
from reporting.tablespec.sizing import TableFitMode, TableSizing
from reporting.tablespec.style import CellStyle, TableStyle
from reporting.tablespec.validation import (
    resolve_column_index,
    validate_columns,
    validate_row_values,
    validate_span,
)

# backward compat imports
from reporting.tablespec.cell import Cell  # noqa: F401
from reporting.tablespec.row import Row    # noqa: F401


class RangeSelector:
    """A selected cell range returned by ``TableSpec.range()``.

    Supports chained ``.style(**kwargs)`` and ``.merge()`` calls.

    Do not instantiate directly; obtain via ``table.range("A1:C4")``.

    Example::

        table.range("A1:D4").style(background_color="#D9EAF7", bold=True)
        table.range("A1:D1").merge()
    """

    def __init__(self, spec: TableSpec, r1: int, c1: int, r2: int, c2: int) -> None:
        self._spec = spec
        self._r1 = r1
        self._c1 = c1
        self._r2 = r2
        self._c2 = c2

    def style(self, **kwargs: Any) -> RangeSelector:
        """Apply a ``CellStyle`` built from *kwargs* to every cell in the range.

        Args:
            **kwargs: ``CellStyle`` field values (background_color, bold, etc.).

        Returns:
            ``self`` for chaining.
        """
        cs = CellStyle(**kwargs)
        for r in range(self._r1, self._r2 + 1):
            for c in range(self._c1, self._c2 + 1):
                if r < len(self._spec.rows) and c < len(self._spec.columns):
                    self._spec.rows[r].cells[c].style = cs
        return self

    def merge(self) -> RangeSelector:
        """Merge the range: set colspan/rowspan on the top-left cell.

        Returns:
            ``self`` for chaining.
        """
        if self._r1 < len(self._spec.rows) and self._c1 < len(self._spec.columns):
            cell = self._spec.rows[self._r1].cells[self._c1]
            cell.colspan = self._c2 - self._c1 + 1
            cell.rowspan = self._r2 - self._r1 + 1
        return self


class TableSpec:
    """A flexible, backend-agnostic table data model.

    ``TableSpec`` supports merged cells, per-cell styling,
    deferred conditional formatting, Excel-style cell access,
    and multiple data-source constructors (DataFrame, Polars,
    dataclasses, records).

    Sizing modes: ``STRETCH`` (default), ``SHRINK_FONT``
    (shrink font to fit), ``PERCENT`` (occupy a percentage
    of the available width).

    Args:
        columns: List of ``Column`` definitions.
        rows: List of ``TableRow`` instances
            (default ``None``).
        style: ``TableStyle`` instance (default
            ``TableStyle()``).
        sizing: ``TableSizing`` instance (default
            ``TableSizing()``).

    Example::

        from reporting.tablespec import TableSpec, Column

        table = TableSpec(
            columns=[
                Column("Case"),
                Column("Mach"),
                Column("Efficiency"),
            ]
        )
        table.add_row("Case A", 0.80, 0.92)
        table.add_row("Case B", 0.90, 0.94)

        # Excel-style access
        table["A1"] = "Results"
        table.merge("A1:D1")
    """

    def __init__(
        self,
        columns: Optional[list[Column]] = None,
        rows: Optional[list[TableRow]] = None,
        style: Optional[TableStyle] = None,
        sizing: Optional[TableSizing] = None,
    ) -> None:
        self.columns: list[Column] = list(columns) if columns else []
        self.rows: list[TableRow] = list(rows) if rows else []
        self.style: TableStyle = style or TableStyle()
        self.sizing: TableSizing = sizing or TableSizing()
        self._current_group: Optional[str] = None
        self._conditions: list[CellCondition] = []
        self._heatmaps: list[HeatmapDef] = []
        self._highlights: list[HighlightExtremeDef] = []
        validate_columns(self.columns)

    @classmethod
    def build(cls) -> "TableBuilder":
        """Return a ``TableBuilder`` for chained construction.

        Example::

            table = TableSpec.build().columns("a","b").add_row(1,2).build()
        """
        from reporting.tablespec.builder import TableBuilder
        return TableBuilder()

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
        """Append a column definition and return ``self`` for chaining.

        Args:
            name: Column identifier (must be unique).
            label: Header display text (defaults to ``name``).
            width: Fixed width in points (default ``None``).
            width_ratio: Relative width factor (default ``None``).
            format: Python format string e.g. ``"{:.2f}"``
                (default ``None``).
            formatter: Custom callable ``(value) -> str``
                (default ``None``).
            alignment: Default text alignment (default ``None``).
            visible: Whether the column appears in output
                (default ``True``).
            style: ``ColumnStyle`` or ``None`` (default ``None``).

        Returns:
            ``self`` for chaining.
        """
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
        """Add a row and return ``self`` for chaining.

        Accepts positional values (one per column) or keyword
        arguments mapping column names to values (not both).

        Args:
            *values: One value per column, in order.
            **kwargs: Column-name → value mappings.

        Returns:
            ``self`` for chaining.

        Raises:
            InvalidRowError: if both positional and keyword
                arguments are provided.
        """
        if values and kwargs:
            raise InvalidRowError("Provide positional values OR keyword arguments, not both")

        if kwargs:
            values = tuple(self._resolve_kwargs(kwargs))
        else:
            validate_row_values(values, len(self.columns))

        cells: list[TableCell] = []
        for col, val in zip(self.columns, values):
            text: Optional[str] = None
            if col.format is not None:
                text = apply_format(val, col.format)
            elif col.formatter is not None:
                text = apply_custom_formatter(val, col.formatter)
            cells.append(TableCell(value=val, text=text))

        self.rows.append(TableRow(cells=cells, group=self._current_group))
        return self

    def row(self, *items: Any) -> TableSpec:
        """Fluent row builder. Accepts a mix of TableCell and plain values.

        Examples::

            table.row("Case A", 0.80, 0.92)
            table.row(cell("Header", colspan=3))
        """
        cells: list[TableCell] = []
        for item in items:
            if isinstance(item, TableCell):
                cells.append(item)
            else:
                cells.append(TableCell(value=item))
        self.rows.append(TableRow(cells=cells, group=self._current_group))
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

    # ------------------------------------------------------------------
    # Excel-style API
    # ------------------------------------------------------------------

    def __getitem__(self, key: Union[str, tuple[int, int]]) -> Any:
        """Access a cell by Excel-style reference ``"A1"`` or ``(row, col)``.

        Examples::

            value = table["B2"]       # Excel-style
            value = table[1, 1]        # zero-based tuple
        """
        if isinstance(key, str):
            r, c = parse_coord(key)
        elif isinstance(key, tuple):
            r, c = key
        else:
            raise TypeError(f"Expected str or tuple, got {type(key).__name__}")
        return self.rows[r].cells[c].value

    def __setitem__(self, key: Union[str, tuple[int, int]], value: Any) -> None:
        """Set a cell value by Excel-style reference ``"A1"`` or ``(row, col)``.

        Examples::

            table["A1"] = "Results"    # Excel-style
            table[0, 0] = "Results"    # zero-based tuple
        """
        if isinstance(key, str):
            r, c = parse_coord(key)
        elif isinstance(key, tuple):
            r, c = key
        else:
            raise TypeError(f"Expected str or tuple, got {type(key).__name__}")
        self.rows[r].cells[c].value = value

    def merge(self, range_ref: str) -> TableSpec:
        """Merge cells in an Excel-style range.

        Sets colspan/rowspan on the top-left cell of the range.

        Examples::

            table.merge("A1:D1")     # merge header across 4 columns
            table.merge("A1:A4")     # merge label across 4 rows
        """
        r1, c1, r2, c2 = parse_range(range_ref)
        if r1 < len(self.rows) and c1 < len(self.columns):
            cell = self.rows[r1].cells[c1]
            cell.colspan = c2 - c1 + 1
            cell.rowspan = r2 - r1 + 1
        return self

    def apply_style(self, range_ref: str, **kwargs: Any) -> TableSpec:
        """Apply a CellStyle built from *kwargs* to every cell in the range.

        Examples::

            table.apply_style("A1:D1", background_color="#003366",
                              text_color="white", bold=True)
            table.apply_style("B2:C5", background_color="#D9EAF7")
        """
        r1, c1, r2, c2 = parse_range(range_ref)
        cs = CellStyle(**kwargs)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if r < len(self.rows) and c < len(self.columns):
                    self.rows[r].cells[c].style = cs
        return self

    def range(self, range_ref: str) -> RangeSelector:
        """Return a ``RangeSelector`` for chained operations on a range.

        Examples::

            table.range("A1:D4").style(background_color="#D9EAF7", bold=True)
            table.range("A1:D1").merge()
        """
        r1, c1, r2, c2 = parse_range(range_ref)
        return RangeSelector(self, r1, c1, r2, c2)

    # ------------------------------------------------------------------
    # Legacy cell / column helpers
    # ------------------------------------------------------------------

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
    # Conditional formatting (immediate — mutates cells)
    # ------------------------------------------------------------------

    def highlight_max(self, column: str) -> TableSpec:
        """Highlight the maximum value in *column* with a green background."""
        col_idx = resolve_column_index(self.columns, column)
        col_vals: list[tuple[int, Any]] = []
        for r, row in enumerate(self.rows):
            if r < self.style.header_rows:
                continue
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    try:
                        float(val)
                        col_vals.append((r, val))
                    except (TypeError, ValueError):
                        pass
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
            if r < self.style.header_rows:
                continue
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    try:
                        float(val)
                        col_vals.append((r, val))
                    except (TypeError, ValueError):
                        pass
        if not col_vals:
            return self
        min_row = min(col_vals, key=lambda x: x[1])[0]
        self.rows[min_row].cells[col_idx].background_color = self.style.highlight_min_color
        return self

    def heatmap(self, column: str) -> TableSpec:
        """Apply a green-to-red heatmap to *column*."""
        col_idx = resolve_column_index(self.columns, column)
        col_vals: list[float] = []
        for row in self.rows[self.style.header_rows:]:
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    try:
                        col_vals.append(float(val))
                    except (TypeError, ValueError):
                        pass
        if not col_vals:
            return self
        mn, mx = min(col_vals), max(col_vals)
        span = mx - mn or 1.0

        for row in self.rows[self.style.header_rows:]:
            if col_idx < len(row.cells):
                val = row.cells[col_idx].value
                if val is not None:
                    try:
                        ratio = (float(val) - mn) / span
                    except (TypeError, ValueError):
                        continue
                    r_ = int(255 * ratio)
                    g_ = int(255 * (1 - ratio))
                    row.cells[col_idx].background_color = f"#{r_:02X}{g_:02X}00"

        return self

    def zebra(self) -> TableSpec:
        """Enable alternating row colors."""
        kwargs: dict[str, Any] = {k: getattr(self.style, k) for k in _dataclass_fields(TableStyle)}
        kwargs["zebra"] = True
        self.style = TableStyle(**kwargs)
        return self

    # ------------------------------------------------------------------
    # Deferred conditional formatting (resolved at render time)
    # ------------------------------------------------------------------

    def add_condition(
        self,
        column: str | int,
        rule: Callable[[Any], bool],
        **style_kwargs: Any,
    ) -> TableSpec:
        """Add a conditional format rule for *column*.

        The *rule* callable receives the cell value; when it returns True,
        the *style_kwargs* are applied as a CellStyle.

        Examples::

            table.add_condition("Temperature", lambda v: v > 1200,
                                background_color="red")
            table.add_condition("Efficiency", lambda v: v > 0.90,
                                background_color="green")
        """
        col_idx: int = resolve_column_index(self.columns, column) if isinstance(column, str) else column
        self._conditions.append(
            CellCondition(column=col_idx, rule=rule, style=CellStyle(**style_kwargs))
        )
        return self

    def add_heatmap(
        self,
        column: str | int,
        min_color: str = "#FFFFCC",
        max_color: str = "#FF0000",
    ) -> TableSpec:
        """Add a heatmap for *column* (deferred — resolved at render time)."""
        col_idx: int = resolve_column_index(self.columns, column) if isinstance(column, str) else column
        self._heatmaps.append(HeatmapDef(column=col_idx, min_color=min_color, max_color=max_color))
        return self

    def add_highlight_max(
        self,
        column: str | int,
        color: str = "#C6EFCE",
    ) -> TableSpec:
        """Add a highlight-max rule for *column* (deferred — resolved at render time)."""
        col_idx: int = resolve_column_index(self.columns, column) if isinstance(column, str) else column
        self._highlights.append(HighlightExtremeDef(column=col_idx, mode="max", color=color))
        return self

    def add_highlight_min(
        self,
        column: str | int,
        color: str = "#FFC7CE",
    ) -> TableSpec:
        """Add a highlight-min rule for *column* (deferred — resolved at render time)."""
        col_idx: int = resolve_column_index(self.columns, column) if isinstance(column, str) else column
        self._highlights.append(HighlightExtremeDef(column=col_idx, mode="min", color=color))
        return self

    # ------------------------------------------------------------------
    # Style resolution for renderers
    # ------------------------------------------------------------------

    def resolve_cell_style(
        self,
        row_idx: int,
        col_idx: int,
        cell_idx: Optional[int] = None,
    ) -> CellStyle:
        """Resolve the effective CellStyle for a cell by merging all layers.

        Merge order (last wins): TableStyle → RowStyle → ColumnStyle → CellStyle.
        Then applies deferred conditionals/heatmaps/highlights.
        Finally applies inline background_color/text_color overrides.

        Args:
            row_idx: Row index.
            col_idx: Visual column index (for column lookups).
            cell_idx: Cell index in the row (defaults to *col_idx*). Use this
                when rowspan/colspan causes visual and cell indices to differ.
        """
        ts = self.style
        row = self.rows[row_idx] if row_idx < len(self.rows) else None
        col = self.columns[col_idx] if col_idx < len(self.columns) else None
        ci = cell_idx if cell_idx is not None else col_idx
        cell = row.cells[ci] if row and ci < len(row.cells) else None

        resolved = CellStyle(
            font_name=ts.font_name,
            font_size=ts.font_size,
            border_color=ts.border_color,
            border_width=ts.border_width,
            padding=ts.padding,
        )

        row_style = row.style if row else None
        col_style = col.style if col else None
        cell_style = cell.style if cell else None

        for override in [row_style, col_style, cell_style]:
            if override is not None:
                resolved = _merge_styles(resolved, override)

        cell_value = cell.value if cell else None

        col_values: list[Any] = []
        if col_idx >= 0:
            col_values = [
                r.cells[col_idx].value
                for r in self.rows[self.style.header_rows:]
                if col_idx < len(r.cells)
            ]

        is_header = row_idx < self.style.header_rows
        if not is_header:
            cond_styles = resolve_conditional_styles(
                col_idx, cell_value,
                conditions=self._conditions,
                heatmaps=self._heatmaps,
                highlights=self._highlights,
                column_values=col_values,
            )
            extreme_styles = resolve_extreme_styles(
                col_idx, cell_value,
                highlights=self._highlights,
                column_values=col_values,
            )
            for cs in cond_styles + extreme_styles:
                if cs is not None:
                    resolved = _merge_styles(resolved, cs)

        if cell and cell.background_color is not None:
            resolved = _rebuild_style(resolved, background_color=cell.background_color)
        if cell and cell.text_color is not None:
            resolved = _rebuild_style(resolved, text_color=cell.text_color)
        if cell and cell.alignment is not None:
            resolved = _rebuild_style(resolved, alignment=cell.alignment)

        return resolved

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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _merge_styles(base: CellStyle, override: CellStyle) -> CellStyle:
    """Merge two CellStyles: override wins for non-None fields."""
    from dataclasses import fields
    kwargs: dict[str, Any] = {}
    for f in fields(CellStyle):
        if f.name == "id":
            continue
        val = getattr(override, f.name)
        if val is not None:
            kwargs[f.name] = val
        else:
            kwargs[f.name] = getattr(base, f.name)
    return CellStyle(**kwargs)


def _rebuild_style(style: CellStyle, **overrides: Any) -> CellStyle:
    """Rebuild a CellStyle with some fields overridden."""
    from dataclasses import fields
    kwargs: dict[str, Any] = {}
    for f in fields(CellStyle):
        if f.name == "id":
            continue
        kwargs[f.name] = getattr(style, f.name)
    kwargs.update(overrides)
    return CellStyle(**kwargs)


def _dataclass_fields(cls: type) -> list[str]:
    """Return list of field names for a dataclass."""
    from dataclasses import fields
    return [f.name for f in fields(cls)]
