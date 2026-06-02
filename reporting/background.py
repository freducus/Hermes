"""Background model — slide background (solid, gradient, or image).

All classes are pure data models with zero renderer dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union

from reporting.styles.colors import Color, ColorValue, normalize_color


class BackgroundType(Enum):
    SOLID = "solid"
    GRADIENT = "gradient"
    IMAGE = "image"


class Background(ABC):
    """Base class for slide background definitions."""

    @property
    @abstractmethod
    def type(self) -> BackgroundType:
        ...


class SolidBackground(Background):
    """A solid-color slide background."""

    color: str

    def __init__(self, color: ColorValue) -> None:
        self.color = normalize_color(color)

    @property
    def type(self) -> BackgroundType:
        return BackgroundType.SOLID


class GradientBackground(Background):
    """A linear gradient slide background.

    Args:
        start_color: Hex color at the start (e.g. "#1F4E79").
        end_color: Hex color at the end.
        angle: Direction in degrees (0 = top→bottom, 90 = left→right).
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
    """An image slide background.

    Args:
        source: Path to the image file.
        opacity: Opacity from 0.0 to 1.0.
        fit: How the image fits the slide — "cover", "contain", or "stretch".
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