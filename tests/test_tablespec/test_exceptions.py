"""Tests for TableSpec exception hierarchy."""

from __future__ import annotations

from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    DuplicateColumnError,
    InvalidColumnError,
    InvalidFormatError,
    InvalidRowError,
    InvalidSpanError,
    TableSpecError,
)


class TestExceptionHierarchy:
    def test_table_spec_error_is_base(self):
        assert issubclass(InvalidColumnError, TableSpecError)
        assert issubclass(InvalidRowError, TableSpecError)
        assert issubclass(InvalidSpanError, TableSpecError)
        assert issubclass(InvalidFormatError, TableSpecError)
        assert issubclass(DuplicateColumnError, InvalidColumnError)
        assert issubclass(ColumnNotFoundError, InvalidColumnError)

    def test_error_message(self):
        exc = InvalidColumnError("test message")
        assert str(exc) == "test message"
