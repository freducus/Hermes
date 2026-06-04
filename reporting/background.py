"""Background model — slide background (solid, gradient, or image).

All classes are pure data models with zero renderer dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union

from reporting.styles.colors import Color, ColorValue, normalize_color


class BackgroundType(Enum):
    """Supported slide background types.

    Members:
        SOLID: Single-colour fill.
        GRADIENT: Linear gradient between two colours.
        IMAGE: Raster image file (PNG, JPG).
    """
    SOLID = "solid"
    GRADIENT = "gradient"
    IMAGE = "image"


class Background(ABC):
    """Abstract base for slide background definitions.

    Subclasses: ``SolidBackground``, ``GradientBackground``,
    ``ImageBackground``.

    .. rubric:: Type dispatch

    ``BackgroundType`` members correspond to each subclass and
    can be used for discriminated unions::

        if bg.type == BackgroundType.GRADIENT:
            bg = cast(GradientBackground, bg)
    """

    @property
    @abstractmethod
    def type(self) -> BackgroundType:
        ...


class SolidBackground(Background):
    """A solid-colour slide background.

    Args:
        color: Any value accepted by ``normalize_color()``:
            a hex string ``"#RRGGBB"``, a named CSS colour
            (``"navy"``, ``"red"``), or an ``(r, g, b)`` tuple
            of integers in ``0..255``.

    Example::

        from reporting.background import SolidBackground

        bg = SolidBackground("#1F4E79")
        bg2 = SolidBackground("steelblue")
        bg3 = SolidBackground((31, 78, 121))
    """

    color: str

    def __init__(self, color: ColorValue) -> None:
        self.color = normalize_color(color)

    @property
    def type(self) -> BackgroundType:
        return BackgroundType.SOLID


class GradientBackground(Background):
    """A linear-gradient slide background.

    The gradient is rendered from ``start_color`` to ``end_color``
    at the given ``angle``.

    Args:
        start_color: Starting colour (any ``ColorValue``).
        end_color: Ending colour (any ``ColorValue``).
        angle: Gradient direction in degrees.

            - ``0`` — top to bottom
            - ``90`` — left to right
            - ``180`` — bottom to top
            - ``270`` — right to left

    Example::

        from reporting.background import GradientBackground

        bg = GradientBackground("#1F4E79", "#87CEEB", angle=90)
        slide = Slide("Title", background=bg)
    """

    start_color: str
    end_color: str
    angle: float

    def __init__(self, start_color: ColorValue, end_color: ColorValue, angle: float = 0.0) -> None:
        self.start_color = normalize_color(start_color)
        self.end_color = normalize_color(end_color)
        self.angle = angle

    @property
    def type(self) -> BackgroundType:
        return BackgroundType.GRADIENT


class ImageBackground(Background):
    """An image-based slide background.

    Args:
        source: Path to the image file (PNG or JPG).
        opacity: Opacity from ``0.0`` (transparent) to
            ``1.0`` (opaque) (default ``1.0``).
        fit: How the image fits the slide.

            - ``"cover"`` — scale uniformly to cover the
              entire slide; parts may be cropped (default)
            - ``"contain"`` — scale uniformly so the whole
              image is visible; may leave empty margins
            - ``"stretch"`` — stretch non-uniformly to
              fill the slide exactly

    Example::

        from reporting.background import ImageBackground

        bg = ImageBackground("slide_bg.png", opacity=0.5,
                              fit="cover")
        slide = Slide("Title", background=bg)
    """

    source: str
    opacity: float
    fit: str

    def __init__(self, source: str, opacity: float = 1.0, fit: str = "cover") -> None:
        self.source = source
        self.opacity = opacity
        self.fit = fit

    @property
    def type(self) -> BackgroundType:
        return BackgroundType.IMAGE