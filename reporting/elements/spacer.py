"""Spacer element — occupies empty space in a layout."""

from __future__ import annotations

import dataclasses

from reporting.elements.base import BaseElement, ElementType


@dataclasses.dataclass
class SpacerElement(BaseElement):
    width: float = 0.0
    height: float = 0.0

    def __init__(self, width: float = 0.0, height: float = 0.0, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.SPACER, properties=kwargs)
        self.width = width
        self.height = height
