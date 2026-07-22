"""Typography system — defines font configurations for themes."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.styles.colors import ColorValue, normalize_color


@dataclasses.dataclass(frozen=True)
class FontSpec:
    """A single font specification (family, size, style, colour).

    Used within a ``Typography`` to define the visual style for
    each text level (heading, body, caption, etc.).

    Args:
        family: Font family name (default ``"Helvetica"``).
        size: Font size in points (default ``12.0``).
        bold: Whether the font is bold (default ``False``).
        italic: Whether the font is italic (default ``False``).
        color: Text colour as a ``ColorValue``
            (default ``None`` = inherit).
        underline: Whether the text is underlined
            (default ``False``).

    Example::

        from reporting.styles.typography import FontSpec

        spec = FontSpec(family="Arial", size=11, color="#333333")
    """
    family: str = "Helvetica"
    size: float = 12.0
    bold: bool = False
    italic: bool = False
    color: Optional[ColorValue] = None
    underline: bool = False

    def __post_init__(self) -> None:
        if self.color is not None:
            object.__setattr__(self, 'color', normalize_color(self.color))


@dataclasses.dataclass
class Typography:
    """A complete typography set for a report theme.

    Defines font specifications for headings (three levels),
    body text, captions, code blocks, and monospace.

    Args:
        heading_1: Top-level heading font
            (default: ``Helvetica 28pt bold``).
        heading_2: Second-level heading font
            (default: ``Helvetica 22pt bold``).
        heading_3: Third-level heading font
            (default: ``Helvetica 18pt bold``).
        body: Body text font
            (default: ``Helvetica 12pt``).
        caption: Caption / figure label font
            (default: ``Helvetica 10pt``).
        code: Inline code font
            (default: ``Courier 10pt``).
        mono: Code block / monospace font
            (default: ``Courier 11pt``).
        extras: Additional named font specs defined by the user.
            Accessed as attributes via ``typo.my_style``, and
            automatically resolved when passed as ``style="my_style"``
            to ``slide[r, c].text()``.

    Example::

        from reporting.styles.typography import Typography, FontSpec

        typo = Typography(
            heading_1=FontSpec(family="Arial", size=28, bold=True,
                               color="#1F4E79"),
            body=FontSpec(family="Arial", size=11, color="#333333"),
            extras={
                "callout": FontSpec(family="Arial", size=10,
                                    italic=True, color="#666666"),
            },
        )
    """
    heading_1: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=28.0, bold=True)
    )
    heading_2: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=22.0, bold=True)
    )
    heading_3: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=18.0, bold=True)
    )
    body: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=12.0)
    )
    caption: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=10.0)
    )
    code: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Courier", size=10.0)
    )
    mono: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Courier", size=11.0)
    )
    extras: dict[str, FontSpec] = dataclasses.field(default_factory=dict)

    def __getattr__(self, name: str) -> FontSpec:
        try:
            return self.extras[name]
        except KeyError:
            raise AttributeError(f"Typography has no style {name!r}")


_STYLE_ALIASES: dict[str, str] = {
    "h1": "heading_1",
    "h2": "heading_2",
    "h3": "heading_3",
}


def resolve_style_name(
    style_name: str,
    typography: Typography,
) -> Optional[FontSpec]:
    """Resolve a style name against a ``Typography``.

    Supports aliases (``"h1"`` → ``"heading_1"``, etc.) and
    falls back to ``getattr``, which includes any user-defined
    extras.

    Args:
        style_name: The style name (e.g. ``"heading_1"``, ``"h1"``,
            ``"callout"``).
        typography: A ``Typography`` instance to resolve against.

    Returns:
        The resolved ``FontSpec``, or ``None`` if not found.
    """
    name = _STYLE_ALIASES.get(style_name, style_name)
    return getattr(typography, name, None)
