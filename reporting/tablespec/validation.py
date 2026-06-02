"""Validation helpers for TableSpec integrity checks."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from reporting.tablespec.column import Column
from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    DuplicateColumnError,
    InvalidRowError,
    InvalidSpanError,
)


def validate_columns(columns: Sequence[Column]) -> None:
    """Check for duplicate column names.

    Raises:
        DuplicateColumnError: if any two columns share the same name.
    """
    seen: set[str] = set()
    for col in columns:
        if col.name in seen:
            raise DuplicateColumnError(f"Duplicate column name: {col.name!r}")
        seen.add(col.name)


def validate_row_values(values: tuple[Any, ...], num_columns: int) -> None:
    """Check that the number of values matches the number of columns.

    Raises:
        InvalidRowError: on mismatch.
    """
    if len(values) != num_columns:
        raise InvalidRowError(
            f"Expected {num_columns} values, got {len(values)}"
        )


def validate_span(
    row: int,
    col: int,
    rowspan: int,
    colspan: int,
    num_rows: int,
    num_cols: int,
) -> None:
    """Check that a span does not exceed table bounds.

    Raises:
        InvalidSpanError: if the span overflows.
    """
    if row < 0 or col < 0:
        raise InvalidSpanError(f"Negative indices not allowed: row={row}, col={col}")
    if rowspan < 1 or colspan < 1:
        raise InvalidSpanError(
            f"Span dimensions must be >= 1, got rowspan={rowspan}, colspan={colspan}"
        )
    if row + rowspan > num_rows:
        raise InvalidSpanError(
            f"Row range [{row}, {row + rowspan}) exceeds row count {num_rows}"
        )
    if col + colspan > num_cols:
        raise InvalidSpanError(
            f"Column range [{col}, {col + colspan}) exceeds column count {num_cols}"
        )


def resolve_column_index(
    columns: Sequence[Column], key: str | int
) -> int:
    """Resolve a column name or index to a 0-based index.

    Raises:
        ColumnNotFoundError: if *key* is a string name not found.
        IndexError: if *key* is an int outside bounds.
    """
    if isinstance(key, str):
        for i, col in enumerate(columns):
            if col.name == key:
                return i
        raise ColumnNotFoundError(f"Column {key!r} not found")
    idx = int(key)
    if not (0 <= idx < len(columns)):
        raise ColumnNotFoundError(
            f"Column index {idx} out of range (0..{len(columns) - 1})"
        )
    return idx
