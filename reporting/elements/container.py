"""Container element — allows nesting a Grid inside another Grid."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.elements.base import BaseElement, ElementType
from reporting.layout.grid import Grid


@dataclasses.dataclass
class ContainerElement(BaseElement):
    """A container that holds a sub-grid within a single cell.

    Used to place mixed content (text, image, plot, table) inside
    one grid cell by nesting another ``Grid`` inside it.

    Args:
        grid: A ``Grid`` instance defining the sub-layout
            (default ``None``).

    Example::

        from reporting.layout.grid import Grid
        from reporting.layout.sizing import Fill, Px
        from reporting.elements.container import ContainerElement

        inner = Grid(rows=2, cols=1,
                     row_sizes=[Fill, Px(50)])
        inner[0, 0].text("Top")
        inner[1, 0].text("Bottom")

        el = ContainerElement(inner)
    """
    grid: Optional[Grid] = None

    def __init__(self, grid: Optional[Grid] = None, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.CONTAINER, properties=kwargs)
        self.grid = grid

    def set_grid(self, grid: Grid) -> None:
        """Set or replace the sub-grid.

        Args:
            grid: A ``Grid`` instance.
        """
        self.grid = grid
