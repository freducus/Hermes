"""Spacer element — occupies empty space in a layout."""

from __future__ import annotations

import dataclasses

from reporting.elements.base import BaseElement, ElementType


@dataclasses.dataclass
class SpacerElement(BaseElement):
    """An invisible element that reserves space in a layout.

    Useful for creating blank rows / columns or fine-tuning
    alignment without padding.

    Args:
        width: Horizontal space in points (default ``0.0``).
        height: Vertical space in points (default ``0.0``).

    Example::

        from reporting.elements.spacer import SpacerElement

        el = SpacerElement(width=20, height=10)
    """
    width: float = 0.0
    height: float = 0.0

    def __init__(self, width: float = 0.0, height: float = 0.0, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.SPACER, properties=kwargs)
        self.width = width
        self.height = height
