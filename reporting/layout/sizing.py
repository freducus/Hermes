"""Sizing primitives for layout — pure math, no renderer imports."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Union


class SizingType(Enum):
    AUTO = "auto"
    FILL = "fill"
    FIXED = "fixed"
    PERCENT = "percent"


@dataclasses.dataclass(frozen=True)
class LengthValue:
    value: float
    sizing_type: SizingType

    def resolve(self, available: float, total_fill_weight: float, own_fill_weight: float) -> float:
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
Fill = LengthValue(1.0, SizingType.FILL)


def Px(value: float) -> LengthValue:
    return LengthValue(value, SizingType.FIXED)


def Percent(value: float) -> LengthValue:
    return LengthValue(value, SizingType.PERCENT)


Sizing = Union[LengthValue, float]


def normalize(value: Sizing) -> LengthValue:
    if isinstance(value, (int, float)):
        return Px(float(value))
    return value
