"""Panel — a rectangular region within a grid layout.

No renderer dependencies. Pure layout geometry.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional

from reporting.layout.geometry import Edges, Size
from reporting.layout.constraints import Constraints
from reporting.styles.colors import ColorValue, normalize_color


class HAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    STRETCH = "stretch"


class VAlign(Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"
    STRETCH = "stretch"


@dataclasses.dataclass
class Panel:
    row: int = 0
    col: int = 0
    rowspan: int = 1
    colspan: int = 1
    padding: Edges = dataclasses.field(default_factory=Edges)
    margin: Edges = dataclasses.field(default_factory=Edges)
    background_color: Optional[ColorValue] = None
    border: Optional[str] = None
    border_radius: float = 0.0
    h_align: HAlign = HAlign.STRETCH
    v_align: VAlign = VAlign.STRETCH
    constraints: Constraints = dataclasses.field(default_factory=Constraints)
    min_size: Size = dataclasses.field(default_factory=lambda: Size(0, 0))
    fixed_size: Optional[Size] = None

    def __post_init__(self) -> None:
        if self.background_color is not None:
            self.background_color = normalize_color(self.background_color)

    @property
    def content_area(self) -> str:
        return "panel" if self.fixed_size else "dynamic"
