"""Tests for TableSpec validation helpers."""

from __future__ import annotations

import pytest

from reporting.tablespec.column import Column
from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    DuplicateColumnError,
    InvalidRowError,
    InvalidSpanError,
)
from reporting.tablespec.validation import (
    resolve_column_index,
    validate_columns,
    validate_row_values,
    validate_span,
)


class TestValidateColumns:
    def test_unique_passes(self):
        validate_columns([Column("a"), Column("b")])

    def test_duplicate_raises(self):
        with pytest.raises(DuplicateColumnError):
            validate_columns([Column("x"), Column("x")])

    def test_empty_passes(self):
        validate_columns([])


class TestValidateRowValues:
    def test_correct_count_passes(self):
        validate_row_values((1, 2, 3), 3)

    def test_wrong_count_raises(self):
        with pytest.raises(InvalidRowError):
            validate_row_values((1, 2), 3)


class TestValidateSpan:
    def test_valid_passes(self):
        validate_span(0, 0, 1, 1, 10, 10)

    def test_negative_row_raises(self):
        with pytest.raises(InvalidSpanError):
            validate_span(-1, 0, 1, 1, 10, 10)

    def test_rowspan_overflow_raises(self):
        with pytest.raises(InvalidSpanError):
            validate_span(8, 0, 5, 1, 10, 10)

    def test_colspan_overflow_raises(self):
        with pytest.raises(InvalidSpanError):
            validate_span(0, 8, 1, 5, 10, 10)

    def test_zero_rowspan_raises(self):
        with pytest.raises(InvalidSpanError):
            validate_span(0, 0, 0, 1, 10, 10)


class TestResolveColumnIndex:
    def test_by_name(self):
        cols = [Column("a"), Column("b")]
        assert resolve_column_index(cols, "a") == 0
        assert resolve_column_index(cols, "b") == 1

    def test_by_index(self):
        cols = [Column("a"), Column("b")]
        assert resolve_column_index(cols, 0) == 0
        assert resolve_column_index(cols, 1) == 1

    def test_name_not_found_raises(self):
        with pytest.raises(ColumnNotFoundError):
            resolve_column_index([Column("a")], "x")
