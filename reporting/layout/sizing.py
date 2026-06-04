"""Sizing primitives for layout — pure math, no renderer imports."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Union


class SizingType(Enum):
    """The strategy used to resolve a length value.

    Members:

        AUTO
            Dimension determined by content size (not yet
            resolved at layout time).
        FILL
            Dimension takes a fraction of the available
            space proportional to its weight (flex-grow).
        FIXED
            Dimension is an exact value in points / pixels.
        PERCENT
            Dimension is a percentage of the available space.
    """
    AUTO = "auto"
    FILL = "fill"
    FIXED = "fixed"
    PERCENT = "percent"


@dataclasses.dataclass(frozen=True)
class LengthValue:
    """A length specification with a value and sizing strategy.

    Create instances via the factory functions ``Px()``,
    ``Percent()``, or by using the module-level constants
    ``Auto`` / ``Fill``.

    Args:
        value: Numeric value (units depend on ``sizing_type``).
        sizing_type: The strategy that interprets ``value``.

    Example::

        from reporting.layout.sizing import LengthValue, Px, Percent, Fill

        fixed = Px(120)            # exactly 120 pt
        pct = Percent(50)          # 50 % of available space
        grow = Fill                # flex-grow with weight 1
    """
    value: float
    sizing_type: SizingType

    def resolve(self, available: float, total_fill_weight: float, own_fill_weight: float) -> float:
        """Compute the resolved length for a given available space.

        Args:
            available: Total available space along this axis.
            total_fill_weight: Sum of ``value`` across all
                ``FILL`` entries on this axis.
            own_fill_weight: This entry's ``value`` (used as
                a flex ratio).

        Returns:
            Resolved length in points / pixels.
        """
        if self.sizing_type is SizingType.FIXED:
            return self.value
        if self.sizing_type is SizingType.PERCENT:
            return available * self.value / 100.0
        if self.sizing_type is SizingType.FILL:
            if total_fill_weight == 0:
                return 0.0
            return available * own_fill_weight / total_fill_weight
        return 0.0


Auto = LengthValue(0.0, SizingType.AUTO)
"""LengthValue sized by content (not resolved at layout time)."""

Fill = LengthValue(1.0, SizingType.FILL)
"""LengthValue that fills remaining space (flex-grow weight = 1)."""


def Px(value: float) -> LengthValue:
    """Create a fixed-size length in points / pixels.

    Args:
        value: Exact length.

    Returns:
        ``LengthValue(value, SizingType.FIXED)``.
    """
    return LengthValue(value, SizingType.FIXED)


def Percent(value: float) -> LengthValue:
    """Create a percentage-based length.

    Args:
        value: Percentage (0–100) of the available space.

    Returns:
        ``LengthValue(value, SizingType.PERCENT)``.
    """
    return LengthValue(value, SizingType.PERCENT)


Sizing = Union[LengthValue, float]
"""A length that can be expressed as a ``LengthValue`` or a raw
float (treated as ``Px(value)``)."""


def normalize(value: Sizing) -> LengthValue:
    """Convert a ``Sizing`` to a ``LengthValue``.

    Floats and ints are wrapped in ``Px()``.

    Args:
        value: A ``LengthValue`` or a plain number.

    Returns:
        A ``LengthValue`` instance.
    """
    if isinstance(value, (int, float)):
        return Px(float(value))
    return value
