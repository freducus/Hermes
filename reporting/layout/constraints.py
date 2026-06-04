"""Layout constraints — pure math, no renderer imports."""

from __future__ import annotations

import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class AxisConstraints:
    """Min / max constraints for a single axis.

    Args:
        min_size: Minimum allowed size (default ``0.0``).
        max_size: Maximum allowed size
            (default ``float("inf")``).

    Example::

        from reporting.layout.constraints import AxisConstraints

        ax = AxisConstraints(min_size=20, max_size=200)
        ax.clamp(10)    # → 20
        ax.clamp(300)   # → 200
        ax.clamp(100)   # → 100
    """
    min_size: float = 0.0
    max_size: float = float("inf")

    def clamp(self, value: float) -> float:
        """Clamp a value to the allowed range.

        Args:
            value: The value to clamp.

        Returns:
            ``value`` if within ``[min_size, max_size]``,
            otherwise the nearest bound.
        """
        if value < self.min_size:
            return self.min_size
        if value > self.max_size:
            return self.max_size
        return value


@dataclasses.dataclass(frozen=True)
class Constraints:
    """2-D constraints with optional aspect-ratio bounds.

    Args:
        width: Width axis constraints
            (default ``AxisConstraints()`` = unbounded).
        height: Height axis constraints
            (default ``AxisConstraints()`` = unbounded).
        min_aspect_ratio: Minimum ``width / height`` ratio
            (default ``None`` = no minimum).
        max_aspect_ratio: Maximum ``width / height`` ratio
            (default ``None`` = no maximum).

    Example::

        from reporting.layout.constraints import Constraints, AxisConstraints

        c = Constraints(
            width=AxisConstraints(min_size=50, max_size=400),
            height=AxisConstraints(min_size=30, max_size=300),
            min_aspect_ratio=0.5,
            max_aspect_ratio=2.0,
        )
        c.clamp(500, 100)  # → (400, 200) — width clamped, aspect ratio enforced
    """
    width: AxisConstraints = dataclasses.field(default_factory=AxisConstraints)
    height: AxisConstraints = dataclasses.field(default_factory=AxisConstraints)
    min_aspect_ratio: Optional[float] = None
    max_aspect_ratio: Optional[float] = None

    def clamp(self, w: float, h: float) -> tuple[float, float]:
        """Clamp width and height and enforce aspect-ratio bounds.

        Aspect-ratio enforcement may adjust the width further
        after the independent axis clamps.

        Args:
            w: Proposed width.
            h: Proposed height.

        Returns:
            ``(w, h)`` clamped and aspect-ratio adjusted.
        """
        w = self.width.clamp(w)
        h = self.height.clamp(h)
        if self.min_aspect_ratio is not None and h > 0 and w / h < self.min_aspect_ratio:
            w = h * self.min_aspect_ratio
        if self.max_aspect_ratio is not None and h > 0 and w / h > self.max_aspect_ratio:
            w = h * self.max_aspect_ratio
        return w, h
