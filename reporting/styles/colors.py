"""Color system — defines colors and palettes for themes."""

from __future__ import annotations

import dataclasses
from typing import Union

NAMED_COLORS: dict[str, str] = {
    "aliceblue": "#F0F8FF",
    "antiquewhite": "#FAEBD7",
    "aqua": "#00FFFF",
    "aquamarine": "#7FFFD4",
    "azure": "#F0FFFF",
    "beige": "#F5F5DC",
    "bisque": "#FFE4C4",
    "black": "#000000",
    "blanchedalmond": "#FFEBCD",
    "blue": "#0000FF",
    "blueviolet": "#8A2BE2",
    "brown": "#A52A2A",
    "burlywood": "#DEB887",
    "cadetblue": "#5F9EA0",
    "chartreuse": "#7FFF00",
    "chocolate": "#D2691E",
    "coral": "#FF7F50",
    "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC",
    "crimson": "#DC143C",
    "cyan": "#00FFFF",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9",
    "darkgreen": "#006400",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00",
    "darkorchid": "#9932CC",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deepskyblue": "#00BFFF",
    "dimgray": "#696969",
    "dodgerblue": "#1E90FF",
    "firebrick": "#B22222",
    "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22",
    "fuchsia": "#FF00FF",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "gold": "#FFD700",
    "goldenrod": "#DAA520",
    "gray": "#808080",
    "green": "#008000",
    "greenyellow": "#ADFF2F",
    "honeydew": "#F0FFF0",
    "hotpink": "#FF69B4",
    "indianred": "#CD5C5C",
    "indigo": "#4B0082",
    "ivory": "#FFFFF0",
    "khaki": "#F0E68C",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lightblue": "#ADD8E6",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0",
    "lime": "#00FF00",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "magenta": "#FF00FF",
    "maroon": "#800000",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "navy": "#000080",
    "oldlace": "#FDF5E6",
    "olive": "#808000",
    "olivedrab": "#6B8E23",
    "orange": "#FFA500",
    "orangered": "#FF4500",
    "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "pink": "#FFC0CB",
    "plum": "#DDA0DD",
    "powderblue": "#B0E0E6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "red": "#FF0000",
    "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seashell": "#FFF5EE",
    "sienna": "#A0522D",
    "silver": "#C0C0C0",
    "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD",
    "slategray": "#708090",
    "snow": "#FFFAFA",
    "springgreen": "#00FF7F",
    "steelblue": "#4682B4",
    "tan": "#D2B48C",
    "teal": "#008080",
    "thistle": "#D8BFD8",
    "tomato": "#FF6347",
    "turquoise": "#40E0D0",
    "violet": "#EE82EE",
    "wheat": "#F5DEB3",
    "white": "#FFFFFF",
    "whitesmoke": "#F5F5F5",
    "yellow": "#FFFF00",
    "yellowgreen": "#9ACD32",
}

ColorValue = Union[str, tuple[int, int, int], "Color"]


@dataclasses.dataclass(frozen=True)
class Color:
    """Immutable color stored as hex string + int r/g/b + alpha.

    Use ``Color.parse()`` to auto-detect hex, named, or rgb() strings.
    """

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

    @staticmethod
    def parse(value: ColorValue, alpha: float = 1.0) -> Color:
        """Auto-detect color format and return a ``Color``.

        Accepts:
            * ``Color`` instance — returned as-is (alpha updated if given)
            * hex string ``"#FF0000"`` or ``"FF0000"``
            * named color ``"red"``, ``"light blue"`` (case/space insensitive)
            * ``"rgb(r, g, b)"``
            * ``tuple[int, int, int]`` like ``(255, 0, 0)``
        """
        if isinstance(value, Color):
            return value if alpha == 1.0 else value.with_alpha(alpha)
        if isinstance(value, (tuple, list)):
            r, g, b = int(value[0]), int(value[1]), int(value[2])
            return Color.from_rgb(r, g, b, alpha=alpha)
        if not isinstance(value, str):
            raise TypeError(f"Cannot parse color from {type(value).__name__}")

        s = value.strip()
        if s.startswith("#"):
            return Color.from_hex(s, alpha=alpha)
        if s.startswith("rgb("):
            inner = s[4:].rstrip(")").strip()
            parts = [int(x.strip()) for x in inner.split(",")]
            return Color.from_rgb(*parts[:3], alpha=alpha)

        name = s.lower().replace(" ", "").replace("-", "")
        if name in NAMED_COLORS:
            return Color.from_hex(NAMED_COLORS[name], alpha=alpha)

        if all(c in "0123456789abcdefABCDEF" for c in s):
            return Color.from_hex(s, alpha=alpha)

        raise ValueError(f"Unknown color: {s!r}")

    @property
    def float_rgb(self) -> tuple[float, float, float]:
        """RGB components as floats in [0, 1] (for ReportLab et al.)."""
        return (self.r / 255, self.g / 255, self.b / 255)

    @property
    def css(self) -> str:
        """CSS-compatible hex string starting with ``#``."""
        return self.hex if self.hex.startswith("#") else f"#{self.hex}"

    @property
    def reportlab_color(self):
        """Return a ``reportlab.lib.colors.Color`` object."""
        from reportlab.lib import colors

        return colors.Color(*self.float_rgb, alpha=self.alpha)

    @property
    def rgba(self) -> str:
        return f"rgba({self.r},{self.g},{self.b},{self.alpha})"

    def with_alpha(self, alpha: float) -> Color:
        return Color(hex=self.hex, r=self.r, g=self.g, b=self.b, alpha=alpha)

    @property
    def hue(self) -> float:
        r, g, b = self.float_rgb
        mx = max(r, g, b)
        mn = min(r, g, b)
        delta = mx - mn
        if delta == 0:
            return 0.0
        if mx == r:
            h = ((g - b) / delta) % 6
        elif mx == g:
            h = ((b - r) / delta) + 2
        else:
            h = ((r - g) / delta) + 4
        return h * 60

    @property
    def lightness(self) -> float:
        r, g, b = self.float_rgb
        return (max(r, g, b) + min(r, g, b)) / 2

    @property
    def saturation(self) -> float:
        r, g, b = self.float_rgb
        mx = max(r, g, b)
        mn = min(r, g, b)
        delta = mx - mn
        if delta == 0:
            return 0.0
        l = (mx + mn) / 2
        return delta / (1 - abs(2 * l - 1))

    @staticmethod
    def sort_by_hue(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Sort (name, hex) pairs by hue, then lightness, then saturation."""
        def _key(item: tuple[str, str]) -> tuple[float, float, float, str]:
            c = Color.parse(item[1])
            return (c.hue, c.lightness, c.saturation, item[0])
        return sorted(items, key=_key)


def normalize_color(value: ColorValue) -> str:
    """Normalize any color input to a canonical hex string (with ``#``)."""
    return Color.parse(value).css


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
