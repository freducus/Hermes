"""Color system — defines colors and palettes for themes."""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class Color:
    hex: str
    r: int
    g: int
    b: int
    alpha: float = 1.0

    @staticmethod
    def from_hex(hex_str: str, alpha: float = 1.0) -> Color:
        h = hex_str.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return Color(hex=hex_str, r=r, g=g, b=b, alpha=alpha)

    @staticmethod
    def from_rgb(r: int, g: int, b: int, alpha: float = 1.0) -> Color:
        hex_str = f"#{r:02x}{g:02x}{b:02x}"
        return Color(hex=hex_str, r=r, g=g, b=b, alpha=alpha)

    @property
    def rgba(self) -> str:
        return f"rgba({self.r},{self.g},{self.b},{self.alpha})"

    def with_alpha(self, alpha: float) -> Color:
        return Color(hex=self.hex, r=self.r, g=self.g, b=self.b, alpha=alpha)


@dataclasses.dataclass(frozen=True)
class ColorPalette:
    primary: Color
    secondary: Color
    accent: Color
    background: Color
    text_primary: Color
    text_secondary: Color
    border: Color
    error: Color
    warning: Color
    success: Color
