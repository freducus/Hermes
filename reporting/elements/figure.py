"""Figure element — wraps a matplotlib figure, backend-agnostic.

The ``format`` attribute controls output:
  - ``"png"`` (default) — raster image at ``dpi`` resolution
  - ``"pdf"`` — vector PDF via pdfrw (PDF renderer only; requires ``pip install pdfrw``)
  - ``"svg"`` — vector SVG (HTML renderer only)
"""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

from reporting.elements.base import BaseElement, ElementType


@dataclasses.dataclass
class FigureElement(BaseElement):
    figure: Any = None
    dpi: int = 150
    bbox_inches: Optional[str] = "tight"
    format: str = "png"

    def __init__(self, figure: object = None, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.FIGURE, properties=kwargs)
        self.figure = figure
        self.dpi = int(kwargs.get("dpi", 150))
        self.bbox_inches = kwargs.get("bbox_inches", "tight")
        self.format = str(kwargs.get("format", "png"))
