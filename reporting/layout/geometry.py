"""Pure geometry primitives — no visual representation concepts, no renderer imports."""

from __future__ import annotations

import dataclasses
from typing import NamedTuple


class Point(NamedTuple):
    """A 2-D point in layout coordinates.

    Args:
        x: X-coordinate (horizontal, left-to-right).
        y: Y-coordinate (vertical, top-to-bottom).

    Example::

        from reporting.layout.geometry import Point

        p = Point(100.0, 200.0)
    """
    x: float
    y: float


class Size(NamedTuple):
    """A 2-D extent (width and height).

    Args:
        width: Horizontal dimension in points / pixels.
        height: Vertical dimension in points / pixels.

    Example::

        from reporting.layout.geometry import Size

        sz = Size(960.0, 540.0)
    """
    width: float
    height: float


@dataclasses.dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangle defined by origin and extent.

    The coordinate system is top-left origin (y increases downward).

    Args:
        x: Left edge X-coordinate.
        y: Top edge Y-coordinate.
        width: Horizontal extent.
        height: Vertical extent.

    Example::

        from reporting.layout.geometry import Rect, Point

        r = Rect(10, 20, 100, 50)
        r.inset(5, 5, 5, 5)          # shrink uniformly
        r.contains_point(Point(30, 40))  # True
    """
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        """Left edge X-coordinate (same as ``x``)."""
        return self.x

    @property
    def right(self) -> float:
        """Right edge X-coordinate (``x + width``)."""
        return self.x + self.width

    @property
    def top(self) -> float:
        """Top edge Y-coordinate (same as ``y``)."""
        return self.y

    @property
    def bottom(self) -> float:
        """Bottom edge Y-coordinate (``y + height``)."""
        return self.y + self.height

    @property
    def top_left(self) -> Point:
        """Return the top-left corner as a ``Point``."""
        return Point(self.x, self.y)

    @property
    def bottom_right(self) -> Point:
        """Return the bottom-right corner as a ``Point``."""
        return Point(self.right, self.bottom)

    @property
    def size(self) -> Size:
        """Return the rectangle extent as a ``Size``."""
        return Size(self.width, self.height)

    def inset(self, left: float, top: float, right: float, bottom: float) -> Rect:
        """Shrink the rectangle by offsets on each side.

        Args:
            left: Amount to subtract from ``x`` and ``width``.
            top: Amount to subtract from ``y`` and ``height``.
            right: Amount to subtract from ``width`` (right side).
            bottom: Amount to subtract from ``height`` (bottom side).

        Returns:
            A new ``Rect`` with the inset applied.
        """
        return Rect(
            x=self.x + left,
            y=self.y + top,
            width=self.width - left - right,
            height=self.height - top - bottom,
        )

    def contains_point(self, p: Point) -> bool:
        """Test whether a point lies within (or on the boundary of) the rectangle.

        Args:
            p: The point to test.

        Returns:
            ``True`` if ``p`` is inside the rectangle.
        """
        return self.left <= p.x <= self.right and self.top <= p.y <= self.bottom


@dataclasses.dataclass(frozen=True)
class Edges:
    """Four-sided offset (padding, margin, or border widths).

    Each side can be set independently.  Factory methods
    ``all()`` and ``symmetric()`` provide common shortcuts.

    Args:
        left: Left edge offset (default ``0.0``).
        top: Top edge offset (default ``0.0``).
        right: Right edge offset (default ``0.0``).
        bottom: Bottom edge offset (default ``0.0``).

    Example::

        from reporting.layout.geometry import Edges

        uniform = Edges.all(8)
        symmetric = Edges.symmetric(horizontal=12, vertical=6)
        custom = Edges(left=20, top=10, right=20, bottom=10)
    """
    left: float = 0.0
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0

    @staticmethod
    def all(value: float) -> Edges:
        """Create an instance with the same value on all four sides.

        Args:
            value: Offset applied to ``left``, ``top``,
                ``right``, and ``bottom``.

        Returns:
            ``Edges(value, value, value, value)``.
        """
        return Edges(left=value, top=value, right=value, bottom=value)

    @staticmethod
    def symmetric(horizontal: float = 0.0, vertical: float = 0.0) -> Edges:
        """Create an instance with mirrored horizontal/vertical values.

        Args:
            horizontal: Value for ``left`` and ``right``
                (default ``0.0``).
            vertical: Value for ``top`` and ``bottom``
                (default ``0.0``).

        Returns:
            ``Edges(horizontal, vertical, horizontal, vertical)``.
        """
        return Edges(left=horizontal, top=vertical, right=horizontal, bottom=vertical)

    @property
    def horizontal(self) -> float:
        """Sum of left and right offsets."""
        return self.left + self.right

    @property
    def vertical(self) -> float:
        """Sum of top and bottom offsets."""
        return self.top + self.bottom
