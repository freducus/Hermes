"""Background model — slide background (solid, gradient, or image).

All classes are pure data models with zero renderer dependencies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


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

    def __init__(self, color: str) -> None:
        if not color.startswith("#"):
            raise ValueError(f"Color must be a hex string starting with '#', got {color!r}")
        self.color = color

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

    def __init__(self, start_color: str, end_color: str, angle: float = 0.0) -> None:
        if not start_color.startswith("#"):
            raise ValueError(f"start_color must be a hex string starting with '#', got {start_color!r}")
        if not end_color.startswith("#"):
            raise ValueError(f"end_color must be a hex string starting with '#', got {end_color!r}")
        self.start_color = start_color
        self.end_color = end_color
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