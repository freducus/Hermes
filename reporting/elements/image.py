"""Image element — backend-agnostic image reference."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional

from reporting.elements.base import BaseElement, ElementType


class ImageFormat(Enum):
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"


@dataclasses.dataclass
class ImageElement(BaseElement):
    source: str = ""
    image_format: ImageFormat = ImageFormat.PNG
    alt_text: str = ""
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    width: Optional[float] = None
    height: Optional[float] = None

    def __init__(self, source: str = "", **kwargs: object) -> None:
        super().__init__(element_type=ElementType.IMAGE, properties=kwargs)
        self.source = source
        self.image_format = ImageFormat.PNG
        self.alt_text = ""
        self.scale = 1.0
        self.rotation = 0.0
        self.opacity = 1.0
        self.width = None
        self.height = None

        if source.lower().endswith(".jpg") or source.lower().endswith(".jpeg"):
            self.image_format = ImageFormat.JPG
        elif source.lower().endswith(".svg"):
            self.image_format = ImageFormat.SVG
