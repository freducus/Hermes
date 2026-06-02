"""TableSpec exception hierarchy."""

from __future__ import annotations


class TableSpecError(Exception):
    """Base exception for all TableSpec errors."""


class InvalidColumnError(TableSpecError):
    """Raised when a column operation fails."""


class InvalidRowError(TableSpecError):
    """Raised when a row operation fails."""


class InvalidSpanError(TableSpecError):
    """Raised when a rowspan/colspan is out of bounds."""


class InvalidFormatError(TableSpecError):
    """Raised when a format string or formatter is invalid."""


class DuplicateColumnError(InvalidColumnError):
    """Raised when a column with the same name already exists."""


class ColumnNotFoundError(InvalidColumnError):
    """Raised when a named column does not exist."""
