"""Layout constraints — pure math, no renderer imports."""

from __future__ import annotations

import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class AxisConstraints:
    min_size: float = 0.0
    max_size: float = float("inf")

    def clamp(self, value: float) -> float:
        if value < self.min_size:
            return self.min_size
        if value > self.max_size:
            return self.max_size
        return value


@dataclasses.dataclass(frozen=True)
class Constraints:
    width: AxisConstraints = dataclasses.field(default_factory=AxisConstraints)
    height: AxisConstraints = dataclasses.field(default_factory=AxisConstraints)
    min_aspect_ratio: Optional[float] = None
    max_aspect_ratio: Optional[float] = None

    def clamp(self, w: float, h: float) -> tuple[float, float]:
        w = self.width.clamp(w)
        h = self.height.clamp(h)
        if self.min_aspect_ratio is not None and h > 0 and w / h < self.min_aspect_ratio:
            w = h * self.min_aspect_ratio
        if self.max_aspect_ratio is not None and h > 0 and w / h > self.max_aspect_ratio:
            w = h * self.max_aspect_ratio
        return w, h
