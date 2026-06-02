"""Tests for TableSpec formatter utilities."""

from __future__ import annotations

import pytest

from reporting.tablespec.exceptions import InvalidFormatError
from reporting.tablespec.formatters import apply_custom_formatter, apply_format


class TestApplyFormat:
    def test_format_float(self):
        assert apply_format(3.14159, "{:.2f}") == "3.14"

    def test_format_percent(self):
        assert apply_format(0.856, "{:.1%}") == "85.6%"

    def test_format_integer(self):
        assert apply_format(42, "{:04d}") == "0042"

    def test_invalid_format_raises(self):
        with pytest.raises(InvalidFormatError):
            apply_format(42, "{:invalid}")


class TestApplyCustomFormatter:
    def test_lambda(self):
        fn = lambda v: f"{v * 100:.0f}%"
        assert apply_custom_formatter(0.95, fn) == "95%"

    def test_exception_raised(self):
        def broken(v):
            raise ValueError("oops")

        with pytest.raises(InvalidFormatError):
            apply_custom_formatter(1, broken)
