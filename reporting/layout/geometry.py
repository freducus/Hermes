"""Pure geometry primitives — no visual representation concepts, no renderer imports."""

from __future__ import annotations

import dataclasses
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float


class Size(NamedTuple):
    width: float
    height: float


@dataclasses.dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def top_left(self) -> Point:
        return Point(self.x, self.y)

    @property
    def bottom_right(self) -> Point:
        return Point(self.right, self.bottom)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    def inset(self, left: float, top: float, right: float, bottom: float) -> Rect:
        return Rect(
            x=self.x + left,
            y=self.y + top,
            width=self.width - left - right,
            height=self.height - top - bottom,
        )

    def contains_point(self, p: Point) -> bool:
        return self.left <= p.x <= self.right and self.top <= p.y <= self.bottom


@dataclasses.dataclass(frozen=True)
class Edges:
    left: float = 0.0
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0

    @staticmethod
    def all(value: float) -> Edges:
        return Edges(left=value, top=value, right=value, bottom=value)

    @staticmethod
    def symmetric(horizontal: float = 0.0, vertical: float = 0.0) -> Edges:
        return Edges(left=horizontal, top=vertical, right=horizontal, bottom=vertical)

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom
