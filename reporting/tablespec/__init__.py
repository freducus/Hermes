"""TableSpec — professional table data model.

Export public API for convenient imports::

    from reporting.tablespec import TableSpec, Column, Row, Cell, TableBuilder
"""

from __future__ import annotations

from reporting.tablespec.builder import TableBuilder
from reporting.tablespec.cell import Cell
from reporting.tablespec.column import Column
from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    DuplicateColumnError,
    InvalidColumnError,
    InvalidFormatError,
    InvalidRowError,
    InvalidSpanError,
    TableSpecError,
)
from reporting.tablespec.row import Row
from reporting.tablespec.spec import TableSpec
from reporting.tablespec.style import CellStyle, ColumnStyle, RowStyle, TableStyle

__all__ = [
    "TableSpec",
    "Column",
    "Row",
    "Cell",
    "TableBuilder",
    "TableStyle",
    "CellStyle",
    "ColumnStyle",
    "RowStyle",
    "TableSpecError",
    "InvalidColumnError",
    "InvalidRowError",
    "InvalidSpanError",
    "InvalidFormatError",
    "DuplicateColumnError",
    "ColumnNotFoundError",
]
