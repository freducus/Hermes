"""Base element type — backend-agnostic content representation."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any


class ElementType(Enum):
    TEXT = "text"
    IMAGE = "image"
    FIGURE = "figure"
    TABLE = "table"
    CONTAINER = "container"
    SPACER = "spacer"


@dataclasses.dataclass
class BaseElement:
    element_type: ElementType
    properties: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        self.properties.setdefault("id", None)
        self.properties.setdefault("css_class", None)
