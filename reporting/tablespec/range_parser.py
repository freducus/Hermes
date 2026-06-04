"""Excel-style range and coordinate parser.

Converts string references like ``"A1"``, ``"B2"``, ``"A1:D4"``,
``"A:A"``, ``"1:1"`` into zero-based (row, col) integer tuples.

Public functions:

* ``parse_coord(ref: str) -> tuple[int, int]`` — ``"A1" → (0, 0)``
* ``parse_range(ref: str) -> tuple[int, int, int, int]`` — ``"A1:D4" → (0, 0, 3, 3)``
* ``col_to_index(col: str) -> int`` — ``"A" → 0, "Z" → 25, "AA" → 26``
* ``index_to_col(index: int) -> str`` — ``0 → "A", 25 → "Z", 26 → "AA"``
"""

from __future__ import annotations

import re
from typing import Optional

_COORD_RE = re.compile(r"^([A-Za-z]+)(\d+)$")
_RANGE_RE = re.compile(
    r"^([A-Za-z]+)(\d+)?:([A-Za-z]+)(\d+)?$"
)
_COL_ONLY_RE = re.compile(r"^([A-Za-z]+):([A-Za-z]+)$")
_ROW_ONLY_RE = re.compile(r"^(\d+):(\d+)$")


class RangeError(ValueError):
    """Raised when a range or coordinate string cannot be parsed."""


def col_to_index(col: str) -> int:
    """Convert Excel column letter(s) to zero-based index.

    Examples:
        ``"A" → 0``, ``"Z" → 25``, ``"AA" → 26``, ``"AZ" → 51``
    """
    result = 0
    for ch in col.upper():
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result - 1


def index_to_col(index: int) -> str:
    """Convert zero-based column index to Excel column letter(s).

    Examples:
        ``0 → "A"``, ``25 → "Z"``, ``26 → "AA"``
    """
    result: list[str] = []
    while index >= 0:
        result.append(chr(ord("A") + index % 26))
        index = index // 26 - 1
    return "".join(reversed(result))


def parse_coord(ref: str) -> tuple[int, int]:
    """Parse an Excel-style cell reference into zero-based (row, col).

    Examples:
        ``"A1" → (0, 0)``
        ``"B2" → (1, 1)``
        ``"AA12" → (11, 26)``

    Raises:
        RangeError: if the reference is malformed.
    """
    ref = ref.strip()
    m = _COORD_RE.match(ref)
    if not m:
        raise RangeError(f"Invalid cell reference: {ref!r}")
    col = col_to_index(m.group(1))
    row = int(m.group(2)) - 1
    return row, col


def parse_range(ref: str) -> tuple[int, int, int, int]:
    r"""Parse an Excel-style range into zero-based (r1, c1, r2, c2).

    The result is normalised so that r1 <= r2 and c1 <= c2.

    Examples:
        ``"A1:D4" → (0, 0, 3, 3)``
        ``"D4:A1" → (0, 0, 3, 3)`` (reversed — always normalised)
        ``"A:A" → (0, 0, MAX_ROW, 0)`` — full column A
        ``"1:1" → (0, 0, 0, MAX_COL)`` — full row 1

    Raises:
        RangeError: if the range string is malformed.
    """
    ref = ref.strip().upper()

    # "A:A" — full column
    cm = _COL_ONLY_RE.match(ref)
    if cm:
        c1 = col_to_index(cm.group(1))
        c2 = col_to_index(cm.group(2))
        if c1 > c2:
            c1, c2 = c2, c1
        return 0, c1, 0, c2

    # "1:1" — full row
    rm = _ROW_ONLY_RE.match(ref)
    if rm:
        r1 = int(rm.group(1)) - 1
        r2 = int(rm.group(2)) - 1
        if r1 > r2:
            r1, r2 = r2, r1
        return r1, 0, r2, 0

    m = _RANGE_RE.match(ref)
    if not m:
        raise RangeError(f"Invalid range reference: {ref!r}")

    c1 = col_to_index(m.group(1))
    r1 = int(m.group(2)) - 1 if m.group(2) else 0
    c2 = col_to_index(m.group(3))
    r2 = int(m.group(4)) - 1 if m.group(4) else 0

    if r1 > r2:
        r1, r2 = r2, r1
    if c1 > c2:
        c1, c2 = c2, c1
    return r1, c1, r2, c2
