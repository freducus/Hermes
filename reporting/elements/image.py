"""Image element — backend-agnostic image reference."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from reporting.elements.base import BaseElement, ElementType


class ImageFormat(Enum):
    """Supported raster image formats.

    Members:
        PNG: Portable Network Graphics (lossless).
        JPG: JPEG (lossy, smaller file size).
        SVG: Scalable Vector Graphics (vector).
    """
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"


class ImageFitMode(Enum):
    """How an image is fitted into its container cell.

    Members:
        ORIGINAL: Keep native size; scale down (maintaining
            aspect ratio) only if larger than the container
            in any dimension.
        FIT_VERTICAL: Scale to fill the container's height;
            width follows aspect ratio.
        FIT_HORIZONTAL: Scale to fill the container's width;
            height follows aspect ratio.
    """
    ORIGINAL = "original"
    FIT_VERTICAL = "fit_vertical"
    FIT_HORIZONTAL = "fit_horizontal"


class ImageElement(BaseElement):
    """An image content element a raster or vector image file.

    The image is loaded from a file path.  Supported formats:
    PNG, JPG, and SVG (SVG requires HTML renderer).

    Sizing priority (highest first):
    1. Explicit ``width`` / ``height`` (points)
    2. ``fit_mode`` (``FIT_VERTICAL`` / ``FIT_HORIZONTAL``)
    3. ``scale`` multiplier applied to the native size
    4. ``ORIGINAL`` — native size, scaled down only if
       larger than the container
    5. When ``preserve_aspect`` is ``True``, the image is
       scaled uniformly to fit within the content rect,
       anchored per cell alignment (default ``False`` =
       stretch to fill).

    Args:
        source: Path to the image file.  Extension is used
            to auto-detect ``image_format``.
        **kwargs: Property overrides:

            - ``alt_text``: ``str`` accessiblity text
              (default ``""``)
            - ``scale``: ``float`` uniform scale factor
              (default ``1.0``)
            - ``rotation``: ``float`` clockwise rotation
              in degrees (default ``0.0``)
            - ``opacity``: ``float`` from 0.0 (transparent)
              to 1.0 (opaque) (default ``1.0``)
            - ``width``: ``float`` explicit width in points
              (default ``None``)
            - ``height``: ``float`` explicit height in points
              (default ``None``)
            - ``fit_mode``: ``ImageFitMode`` or ``str``
              (default ``"original"``)
            - ``preserve_aspect``: ``bool`` maintain aspect
              ratio when scaling (default ``False``)

    Example::

        from reporting.elements.image import ImageElement, ImageFitMode

        el = ImageElement("chart.png", scale=0.8)
        el2 = ImageElement("photo.jpg",
                          fit_mode=ImageFitMode.FIT_VERTICAL)
        el3 = ImageElement("logo.png", width=120, height=60)
        el4 = ImageElement("logo.png", preserve_aspect=True)
    """
    source: str = ""
    image_format: ImageFormat = ImageFormat.PNG
    alt_text: str = ""
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    width: Optional[float] = None
    height: Optional[float] = None
    fit_mode: ImageFitMode = ImageFitMode.ORIGINAL
    preserve_aspect: bool = False

    def __init__(self, source: str = "", **kwargs: object) -> None:
        super().__init__(element_type=ElementType.IMAGE, properties=kwargs)
        self.source = source
        self.image_format = ImageFormat.PNG
        self.alt_text = kwargs.get("alt_text", "")
        self.scale = float(kwargs.get("scale", 1.0))
        self.rotation = float(kwargs.get("rotation", 0.0))
        self.opacity = float(kwargs.get("opacity", 1.0))
        self.width = kwargs.get("width", None)
        self.height = kwargs.get("height", None)
        self.fit_mode = ImageFitMode(kwargs.get("fit_mode", "original"))
        self.preserve_aspect = bool(kwargs.get("preserve_aspect", False))

        if source.lower().endswith(".jpg") or source.lower().endswith(".jpeg"):
            self.image_format = ImageFormat.JPG
        elif source.lower().endswith(".svg"):
            self.image_format = ImageFormat.SVG
