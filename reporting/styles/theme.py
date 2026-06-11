"""Theme system — defines visual themes for reports."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from reporting.styles.colors import Color, ColorPalette
from reporting.styles.typography import Typography, FontSpec
from reporting.footer_config import FooterPanel
from reporting.slide_type import SlideTypeConfig

if TYPE_CHECKING:
    from reporting.tablespec.style import TableStyle


@dataclasses.dataclass(frozen=True)
class Theme:
    """Base report theme combining colours, typography, and table styling.

    Subclasses (``CorporateTheme``, ``DarkTheme``, ``LightTheme``)
    provide pre-built palettes.  A custom theme can be created by
    instantiating ``Theme`` directly with any ``ColorPalette``,
    ``Typography``, and ``TableStyle``.

    Args:
        name: Theme name for identification.
        palette: The colour palette.
        typography: Font specifications for all text levels.
        table_style: Table style rules (column widths, zebra, etc.).
        footer_panel: Footer panel configuration (height, separator, font).

    Example::

        from reporting.styles.theme import Theme
        from reporting.styles.colors import ColorPalette, Color
        from reporting.styles.typography import Typography, FontSpec
        from reporting.tablespec.style import TableStyle

        theme = Theme(
            name="Custom",
            palette=ColorPalette(
                primary=Color.from_hex("#333"),
                secondary=Color.from_hex("#666"),
                # ... other colours
            ),
            typography=Typography(),
            table_style=TableStyle(),
        )
    """
    name: str
    palette: ColorPalette
    typography: Typography
    table_style: "TableStyle"
    footer_panel: FooterPanel = dataclasses.field(default_factory=FooterPanel)
    slide_types: dict[str, SlideTypeConfig] = dataclasses.field(default_factory=dict)

    def get_slide_type(self, name: str = "default") -> SlideTypeConfig:
        """Look up a slide type by name, falling back to a default if missing.

        Args:
            name: The slide type name.

        Returns:
            The matching ``SlideTypeConfig`` or a fresh default.
        """
        return self.slide_types.get(
            name,
            SlideTypeConfig.from_theme(self, name=name),
        )

    def get_heading_style(self, level: int) -> FontSpec:
        """Get the font specification for a heading level.

        Args:
            level: 1, 2, or 3 for the corresponding heading.

        Returns:
            The ``FontSpec`` for that level, or ``body``
            if the level is outside 1..3.
        """
        return {
            1: self.typography.heading_1,
            2: self.typography.heading_2,
            3: self.typography.heading_3,
        }.get(level, self.typography.body)


@dataclasses.dataclass(frozen=True)
class CorporateTheme(Theme):
    """Default corporate theme (blue/grey palette, Arial fonts).

    Uses the corporate colour scheme and Arial/Calibri fonts
    with a white background.

    Example::

        from reporting.styles.theme import CorporateTheme

        theme = CorporateTheme()
    """
    def __init__(self) -> None:
        from reporting.tablespec.style import TableStyle

        palette = ColorPalette(
            primary=Color.from_hex("#1F4E79"),
            secondary=Color.from_hex("#2E75B6"),
            accent=Color.from_hex("#ED7D31"),
            background=Color.from_hex("#FFFFFF"),
            text_primary=Color.from_hex("#333333"),
            text_secondary=Color.from_hex("#666666"),
            border=Color.from_hex("#D9D9D9"),
            error=Color.from_hex("#C00000"),
            warning=Color.from_hex("#FFC000"),
            success=Color.from_hex("#70AD47"),
        )
        typography = Typography(
            heading_1=FontSpec(family="Arial", size=28.0, bold=True, color="#1F4E79"),
            heading_2=FontSpec(family="Arial", size=22.0, bold=True, color="#1F4E79"),
            heading_3=FontSpec(family="Arial", size=16.0, bold=True, color="#2E75B6"),
            body=FontSpec(family="Arial", size=11.0, color="#333333"),
            caption=FontSpec(family="Arial", size=9.0, color="#666666"),
            code=FontSpec(family="Courier New", size=10.0, color="#333333"),
            mono=FontSpec(family="Courier New", size=10.0, color="#333333"),
        )
        table_style = TableStyle()
        super().__init__(name="Corporate", palette=palette, typography=typography, table_style=table_style,
                         footer_panel=FooterPanel(center_text="Corporate Report"),
                         slide_types=_builtin_slide_types(
                             theme_palette=palette,
                             theme_typography=typography,
                             center_text="Corporate Report",
                         ))


def _builtin_slide_types(
    theme_palette: ColorPalette,
    theme_typography: Typography,
    center_text: str = "",
) -> dict[str, SlideTypeConfig]:
    """Create the standard set of slide types for a built-in theme."""
    from reporting.title_config import TitlePanel

    default_title_panel = TitlePanel(
        height=60.0,
        show_separator=True,
        separator_color=theme_palette.border.css,
        separator_width=1.0,
        separator_margin=8.0,
    )
    title_slide_panel = TitlePanel(
        height=80.0,
        show_separator=False,
        separator_color=theme_palette.border.css,
        separator_width=1.0,
        separator_margin=8.0,
    )
    blank_panel = TitlePanel(
        height=0.0,
        show_separator=False,
    )

    # Build footer panels
    default_footer = FooterPanel(
        enabled=True,
        separator_color=theme_palette.border.css,
        font_name=theme_typography.caption.family,
        font_size=theme_typography.caption.size,
        color=theme_palette.text_secondary.css,
        center_text=center_text,
    )
    no_footer = FooterPanel(enabled=False)

    return {
        "default": SlideTypeConfig(
            name="default",
            title_panel=default_title_panel,
            footer_panel=default_footer,
        ),
        "title": SlideTypeConfig(
            name="title",
            title_panel=title_slide_panel,
            footer_panel=no_footer,
        ),
        "blank": SlideTypeConfig(
            name="blank",
            title_panel=blank_panel,
            footer_panel=no_footer,
        ),
    }


@dataclasses.dataclass(frozen=True)
class DarkTheme(Theme):
    """Dark theme (blue accent on dark background).

    Uses Helvetica fonts with light text on a near-black
    background.  Suited for presentations in dim environments.

    Example::

        from reporting.styles.theme import DarkTheme

        theme = DarkTheme()
    """
    def __init__(self) -> None:
        from reporting.tablespec.style import TableStyle

        palette = ColorPalette(
            primary=Color.from_hex("#4FC3F7"),
            secondary=Color.from_hex("#29B6F6"),
            accent=Color.from_hex("#FFB74D"),
            background=Color.from_hex("#1E1E1E"),
            text_primary=Color.from_hex("#E0E0E0"),
            text_secondary=Color.from_hex("#9E9E9E"),
            border=Color.from_hex("#424242"),
            error=Color.from_hex("#EF5350"),
            warning=Color.from_hex("#FFA726"),
            success=Color.from_hex("#66BB6A"),
        )
        typography = Typography(
            heading_1=FontSpec(family="Helvetica", size=28.0, bold=True, color="#4FC3F7"),
            heading_2=FontSpec(family="Helvetica", size=22.0, bold=True, color="#4FC3F7"),
            heading_3=FontSpec(family="Helvetica", size=16.0, bold=True, color="#29B6F6"),
            body=FontSpec(family="Helvetica", size=11.0, color="#E0E0E0"),
            caption=FontSpec(family="Helvetica", size=9.0, color="#9E9E9E"),
            code=FontSpec(family="Courier", size=10.0, color="#E0E0E0"),
            mono=FontSpec(family="Courier", size=10.0, color="#E0E0E0"),
        )
        table_style = TableStyle()
        super().__init__(name="Dark", palette=palette, typography=typography, table_style=table_style,
                         footer_panel=FooterPanel(center_text="Dark Report"),
                         slide_types=_builtin_slide_types(
                             theme_palette=palette,
                             theme_typography=typography,
                             center_text="Dark Report",
                         ))


@dataclasses.dataclass(frozen=True)
class LightTheme(Theme):
    """Light theme (blue on near-white background).

    Similar to the corporate theme but with a slightly softer
    palette and a light grey background.

    Example::

        from reporting.styles.theme import LightTheme

        theme = LightTheme()
    """
    def __init__(self) -> None:
        from reporting.tablespec.style import TableStyle

        palette = ColorPalette(
            primary=Color.from_hex("#1565C0"),
            secondary=Color.from_hex("#42A5F5"),
            accent=Color.from_hex("#FF7043"),
            background=Color.from_hex("#FAFAFA"),
            text_primary=Color.from_hex("#212121"),
            text_secondary=Color.from_hex("#757575"),
            border=Color.from_hex("#E0E0E0"),
            error=Color.from_hex("#E53935"),
            warning=Color.from_hex("#FB8C00"),
            success=Color.from_hex("#43A047"),
        )
        typography = Typography(
            heading_1=FontSpec(family="Helvetica", size=28.0, bold=True, color="#1565C0"),
            heading_2=FontSpec(family="Helvetica", size=22.0, bold=True, color="#1565C0"),
            heading_3=FontSpec(family="Helvetica", size=16.0, bold=True, color="#42A5F5"),
            body=FontSpec(family="Helvetica", size=11.0, color="#212121"),
            caption=FontSpec(family="Helvetica", size=9.0, color="#757575"),
            code=FontSpec(family="Courier", size=10.0, color="#212121"),
            mono=FontSpec(family="Courier", size=10.0, color="#212121"),
        )
        table_style = TableStyle()
        super().__init__(name="Light", palette=palette, typography=typography, table_style=table_style,
                         footer_panel=FooterPanel(center_text="Light Report"),
                         slide_types=_builtin_slide_types(
                             theme_palette=palette,
                             theme_typography=typography,
                             center_text="Light Report",
                         ))
