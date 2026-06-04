"""TableSpec — professional table data model.

Export public API for convenient imports::

    from reporting.tablespec import (
        TableSpec, Column, TableCell, TableRow, Cell, Row, TableBuilder,
        cell, parse_coord, parse_range,
    )
"""

from __future__ import annotations

from reporting.tablespec.builder import TableBuilder
from reporting.tablespec.cell import Cell, TableCell
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
from reporting.tablespec.helpers import cell
from reporting.tablespec.range_parser import parse_coord, parse_range
from reporting.tablespec.row import Row, TableRow
from reporting.tablespec.sizing import ColumnDistrib, TableFitMode, TableSizing
from reporting.tablespec.spec import TableSpec
from reporting.tablespec.style import CellStyle, ColumnStyle, RowStyle, TableStyle

__all__ = [
    "TableSpec",
    "Column",
    "TableCell",
    "TableRow",
    "Cell",
    "Row",
    "TableBuilder",
    "cell",
    "parse_coord",
    "parse_range",
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
    "ColumnDistrib",
    "TableFitMode",
    "TableSizing",
]
