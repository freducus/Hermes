"""Base element type — backend-agnostic content representation."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any


class ElementType(Enum):
    """Discriminated union tag for all element subclasses.

    Members:
        TEXT: ``TextElement``
        IMAGE: ``ImageElement``
        FIGURE: ``FigureElement``
        TABLE: ``TableElement``
        TABLESPEC: ``TableSpecElement``
        CONTAINER: ``ContainerElement``
        SPACER: ``SpacerElement``
    """
    TEXT = "text"
    IMAGE = "image"
    FIGURE = "figure"
    TABLE = "table"
    TABLESPEC = "tablespec"
    CONTAINER = "container"
    SPACER = "spacer"


@dataclasses.dataclass
class BaseElement:
    """Abstract base for all content elements in a report.

    Subclasses must set ``element_type`` to the corresponding
    ``ElementType`` member.

    The ``properties`` dictionary stores arbitrary metadata
    (``id``, ``css_class``, and any keyword arguments passed
    to the constructor).

    Args:
        element_type: The type tag for this element.
        properties: User-supplied keyword arguments stored
            as a dict (default empty dict).

    Example::

        from reporting.elements.base import BaseElement, ElementType

        el = BaseElement(ElementType.TEXT, {"bold": True})
    """
    element_type: ElementType
    properties: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        self.properties.setdefault("id", None)
        self.properties.setdefault("css_class", None)
