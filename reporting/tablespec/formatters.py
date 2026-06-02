"""Value formatting utilities for TableSpec.

These helpers are used by TableSpec.add_row to compute display text
from raw cell values and column-level format specifications.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from reporting.tablespec.exceptions import InvalidFormatError


def apply_format(value: Any, fmt: str) -> str:
    """Apply a Python format string to *value*.

    Args:
        value: The raw cell value.
        fmt: A ``str.format``-style template, e.g. ``"{:.2%}"``.

    Returns:
        The formatted string.

    Raises:
        InvalidFormatError: if the format string is invalid.
    """
    try:
        return fmt.format(value)
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise InvalidFormatError(
            f"Format string {fmt!r} failed for value {value!r}: {exc}"
        ) from exc


def apply_custom_formatter(value: Any, func: Callable[[Any], str]) -> str:
    """Apply a callable formatter to *value*.

    Args:
        value: The raw cell value.
        func: A callable that takes a value and returns a string.

    Returns:
        The formatted string.

    Raises:
        InvalidFormatError: if the callable raises.
    """
    try:
        return func(value)
    except Exception as exc:
        raise InvalidFormatError(
            f"Custom formatter {func!r} failed for value {value!r}: {exc}"
        ) from exc
