from reporting.styles.colors import Color, ColorPalette
from reporting.styles.typography import Typography, FontSpec
from reporting.styles.theme import Theme, CorporateTheme, DarkTheme, LightTheme

__all__ = [
    "Color", "ColorPalette",
    "Typography", "FontSpec",
    "TableStyle",
    "Theme", "CorporateTheme", "DarkTheme", "LightTheme",
]


def __getattr__(name: str) -> object:
    """Lazy import of ``TableStyle`` to avoid circular imports."""
    if name == "TableStyle":
        from reporting.tablespec.style import TableStyle as _ts
        return _ts
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

