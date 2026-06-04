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
    """Horizontal alignment options for content within a cell.

    Members:
        LEFT: Align content to the left edge of the cell.
        CENTER: Centre content horizontally within the cell.
        RIGHT: Align content to the right edge of the cell.
        STRETCH: Scale/stretch content to fill the full cell
            width (default).
    """
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    STRETCH = "stretch"


class VAlign(Enum):
    """Vertical alignment options for content within a cell.

    Members:
        TOP: Align content to the top edge of the cell.
        MIDDLE: Centre content vertically within the cell.
        BOTTOM: Align content to the bottom edge of the cell.
        STRETCH: Scale/stretch content to fill the full cell
            height (default).
    """
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"
    STRETCH = "stretch"


@dataclasses.dataclass
class Panel:
    """A cell (or merged cell group) within the grid layout.

    ``Panel`` stores layout metadata: position, span, padding,
    margin, background, border, alignment, and size constraints.
    It is created automatically when constructing a ``Grid``.

    Args:
        row: Row index (default ``0``).
        col: Column index (default ``0``).
        rowspan: Number of rows this panel spans (default ``1``).
        colspan: Number of columns this panel spans (default ``1``).
        padding: Inner padding as an ``Edges`` instance
            (default ``Edges()`` = zero).
        margin: Outer margin as an ``Edges`` instance
            (default ``Edges()`` = zero).
        background_color: Background colour (any ``ColorValue``)
            (default ``None`` = transparent).
        border: CSS-style border shorthand or ``None``
            (default ``None``).
        border_radius: Corner radius in points (default ``0.0``).
        h_align: Horizontal alignment of child content
            (default ``HAlign.STRETCH``).
        v_align: Vertical alignment of child content
            (default ``VAlign.STRETCH``).
        constraints: Min/max size constraints
            (default ``Constraints()`` = unbounded).
        min_size: Minimum size as ``Size(w, h)`` (default
            ``Size(0, 0)``).
        fixed_size: Fixed size override; when set, the panel
            ignores grid-computed sizing
            (default ``None``).

    Example::

        from reporting.layout.panel import Panel, HAlign, VAlign
        from reporting.layout.geometry import Edges

        panel = Panel(
            row=0, col=0,
            padding=Edges.all(8),
            h_align=HAlign.CENTER,
            v_align=VAlign.MIDDLE,
        )
    """
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
        """Return ``"panel"`` if a ``fixed_size`` is set, otherwise ``"dynamic"``."""
        return "panel" if self.fixed_size else "dynamic"
