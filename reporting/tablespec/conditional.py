"""Conditional formatting engine for TableSpec.

Provides first-class conditional rules, heatmaps, and highlight
definitions that are resolved at render time (not at definition time).

Public classes:

* ``CellCondition`` — a rule + style applied when the rule matches
* ``HeatmapDef`` — interpolates a colour gradient across values
* ``HighlightExtremeDef`` — highlights max or min value in a column
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Optional

from reporting.styles.colors import ColorValue, normalize_color
from reporting.tablespec.style import CellStyle


@dataclass(frozen=True)
class CellCondition:
    """A conditional rule that applies *style* when *rule(value)* is True.

    Attributes:
        column: Column name (string) or zero-based index (int).
        rule: Callable that receives the cell value and returns bool.
        style: CellStyle to apply when the rule matches.
    """

    column: str | int
    rule: Callable[[Any], bool]
    style: CellStyle


@dataclass(frozen=True)
class HeatmapDef:
    """Defines a heatmap gradient over numeric values in a column.

    Attributes:
        column: Column name or zero-based index.
        min_color: Colour for the minimum value (default pale yellow).
        max_color: Colour for the maximum value (default red).
    """

    column: str | int
    min_color: ColorValue = "#FFFFCC"
    max_color: ColorValue = "#FF0000"

    def __post_init__(self) -> None:
        object.__setattr__(self, "min_color", normalize_color(self.min_color))
        object.__setattr__(self, "max_color", normalize_color(self.max_color))


@dataclass(frozen=True)
class HighlightExtremeDef:
    """Highlights the maximum or minimum value in a column.

    Attributes:
        column: Column name or zero-based index.
        mode: ``"max"`` or ``"min"``.
        color: Background colour to apply (default green for max, red for min).
    """

    column: str | int
    mode: str  # "max" or "min"
    color: ColorValue = "#C6EFCE"

    def __post_init__(self) -> None:
        object.__setattr__(self, "color", normalize_color(self.color))


# ---------------------------------------------------------------------------
# Resolution helpers (used by renderers)
# ---------------------------------------------------------------------------


def _interpolate_hex(c1: str, c2: str, ratio: float) -> str:
    """Linearly interpolate between two hex colours."""
    r1 = int(c1[1:3], 16)
    g1 = int(c1[3:5], 16)
    b1 = int(c1[5:7], 16)
    r2 = int(c2[1:3], 16)
    g2 = int(c2[3:5], 16)
    b2 = int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f"#{r:02X}{g:02X}{b:02X}"


def resolve_conditional_styles(
    col_idx: int,
    cell_value: Any,
    *,
    conditions: list[CellCondition],
    heatmaps: list[HeatmapDef],
    highlights: list[HighlightExtremeDef],
    column_values: Optional[list[Any]] = None,
) -> list[CellStyle]:
    """Resolve which conditional styles apply to *cell_value* in *col_idx*.

    Returns a list of CellStyle overrides (may be empty).  The caller
    merges them in order (last wins for conflicting fields).
    """
    results: list[CellStyle] = []

    for cond in conditions:
        col = cond.column
        if (isinstance(col, int) and col == col_idx) or col == col_idx:
            if cond.rule(cell_value):
                results.append(cond.style)

    for hf in heatmaps:
        col = hf.column
        if (isinstance(col, int) and col == col_idx) or col == col_idx:
            if column_values and cell_value is not None:
                vals = [float(v) for v in column_values if v is not None]
                if vals:
                    mn, mx = min(vals), max(vals)
                    span = mx - mn or 1.0
                    ratio = (float(cell_value) - mn) / span
                    bg = _interpolate_hex(hf.min_color, hf.max_color, ratio)
                    results.append(CellStyle(background_color=bg))

    return results


def resolve_extreme_styles(
    col_idx: int,
    cell_value: Any,
    *,
    highlights: list[HighlightExtremeDef],
    column_values: Optional[list[Any]] = None,
) -> list[CellStyle]:
    """Resolve highlight-max / highlight-min styles."""
    results: list[CellStyle] = []
    for he in highlights:
        col = he.column
        if (isinstance(col, int) and col == col_idx) or col == col_idx:
            if column_values and cell_value is not None:
                vals = [v for v in column_values if v is not None]
                if not vals:
                    continue
                if he.mode == "max" and cell_value == max(vals):
                    results.append(CellStyle(background_color=he.color))
                elif he.mode == "min" and cell_value == min(vals):
                    results.append(CellStyle(background_color=he.color))
    return results
