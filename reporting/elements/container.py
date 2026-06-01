"""Container element — allows nesting a Grid inside another Grid."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.elements.base import BaseElement, ElementType
from reporting.layout.grid import Grid


@dataclasses.dataclass
class ContainerElement(BaseElement):
    grid: Optional[Grid] = None

    def __init__(self, grid: Optional[Grid] = None, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.CONTAINER, properties=kwargs)
        self.grid = grid

    def set_grid(self, grid: Grid) -> None:
        self.grid = grid
