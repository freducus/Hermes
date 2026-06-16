"""Theme system — defines visual themes for reports.

Themes define the complete visual identity: colours, typography,
page size, named layouts, and slide types.

Predefined themes
-----------------
* ``CorporateTheme`` — blue/grey, Arial (default)
* ``DarkTheme`` — dark background, light text, blue accents
* ``LightTheme`` — light background, soft palette

Custom themes
-------------
Subclass ``Theme`` directly::

    from reporting.styles.theme import Theme
    from reporting.styles.colors import ColorPalette, Color
    from reporting.styles.typography import Typography, FontSpec
    from reporting.tablespec.style import TableStyle
    from reporting.layout_config import LayoutConfig
    from reporting.slide_type import SlideTypeConfig

    class MyTheme(Theme):
        def __init__(self) -> None:
            super().__init__(
                name="MyTheme",
                page_size=(960, 540),
                palette=ColorPalette(...),
                typography=Typography(...),
                table_style=TableStyle(),
                layouts={
                    "default": LayoutConfig(name="default", rows=1, cols=1),
                },
                slide_types={
                    "default": SlideTypeConfig(name="default", layout="default"),
                },
            )

Register for auto-discovery with ``load_themes()``::

    @Theme.register("my_theme")
    class MyTheme(Theme):
        ...
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional, TypeVar

from reporting.layout_config import LayoutConfig
from reporting.slide_type import SlideTypeConfig
from reporting.styles.colors import Color, ColorPalette
from reporting.styles.typography import Typography, FontSpec
from reporting.footer_config import FooterPanel

if TYPE_CHECKING:
    from reporting.tablespec.style import TableStyle

ThemeT = TypeVar("ThemeT", bound="Theme")


@dataclasses.dataclass
class Theme:
    """Base report theme combining colours, typography, layout configs,
    and slide type presets.

    Subclasses (``CorporateTheme``, ``DarkTheme``, ``LightTheme``)
    provide pre-built presets.  Create a custom theme by subclassing
    ``Theme`` and calling ``super().__init__()`` with your values.

    Args:
        name: Theme name for identification.
        page_size: ``(width, height)`` in pixels (default ``(960, 540)``).
        palette: The colour palette.
        typography: Font specifications for all text levels.
        table_style: Table style rules (column widths, zebra, etc.).
        layouts: Named ``LayoutConfig`` objects keyed by name.
        slide_types: Named ``SlideTypeConfig`` objects keyed by name.
        footer_panel: Footer panel configuration.

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
                ...
            ),
            typography=Typography(),
            table_style=TableStyle(),
        )
    """

    name: str = ""
    page_size: tuple[float, float] = (960.0, 540.0)
    palette: ColorPalette = dataclasses.field(
        default_factory=lambda: ColorPalette(
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
    )
    typography: Typography = dataclasses.field(default_factory=Typography)
    table_style: Any = None
    layouts: dict[str, LayoutConfig] = dataclasses.field(default_factory=dict)
    slide_types: dict[str, SlideTypeConfig] = dataclasses.field(default_factory=dict)
    footer_panel: FooterPanel = dataclasses.field(default_factory=FooterPanel)

    _registry: ClassVar[dict[str, type[Theme]]] = {}

    def __post_init__(self) -> None:
        if self.table_style is None:
            from reporting.tablespec.style import TableStyle
            object.__setattr__(self, "table_style", TableStyle())
        if not self.layouts:
            object.__setattr__(
                self,
                "layouts",
                {"default": LayoutConfig(name="default", rows=1, cols=1)},
            )
        if not self.slide_types:
            object.__setattr__(
                self,
                "slide_types",
                {"default": SlideTypeConfig(name="default", layout="default")},
            )

    def get_slide_type(self, name: str = "default") -> SlideTypeConfig:
        """Look up a slide type by name, falling back to a default if missing.

        Args:
            name: The slide type name.

        Returns:
            The matching ``SlideTypeConfig`` or a fresh default.
        """
        return self.slide_types.get(
            name,
            SlideTypeConfig(name=name, layout="default"),
        )

    def get_layout(self, name: str = "default") -> LayoutConfig:
        """Look up a layout by name, falling back to a default.

        Args:
            name: The layout name.

        Returns:
            The matching ``LayoutConfig`` or ``LayoutConfig(name=name)``.
        """
        return self.layouts.get(name, LayoutConfig(name=name))

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

    @classmethod
    def register(cls, name: str = "") -> Callable[[type[ThemeT]], type[ThemeT]]:
        """Class decorator that registers a ``Theme`` subclass for auto-discovery.

        Usage::

            @Theme.register("corporate")
            class CorporateTheme(Theme):
                ...

        Args:
            name: Registration key (defaults to the class name).

        Returns:
            A decorator that registers the class and returns it.
        """
        def decorator(subclass: type[ThemeT]) -> type[ThemeT]:
            key = name or subclass.__name__
            cls._registry[key] = subclass
            return subclass
        return decorator

    @staticmethod
    def load_themes(directory: str) -> dict[str, type[Theme]]:
        """Scan *directory* for ``.py`` files and import them,
        collecting any ``Theme`` subclasses decorated with
        ``@Theme.register()``.

        Args:
            directory: Path to a directory containing theme ``.py`` files.

        Returns:
            A dict mapping registration keys to ``Theme`` classes.
        """
        p = Path(directory)
        if not p.is_dir():
            return dict(Theme._registry)

        for f in sorted(p.glob("*.py")):
            if f.name.startswith("_"):
                continue
            mod_name = f"_theme_{f.stem}"
            spec = importlib.util.spec_from_file_location(mod_name, str(f))
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            try:
                spec.loader.exec_module(mod)
            except Exception:
                pass

        return dict(Theme._registry)


@Theme.register("corporate")
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
        from reporting.title_config import TitlePanel
        from reporting.background import SolidBackground

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

        default_tp = TitlePanel(
            height=60.0, show_separator=True,
            separator_color=palette.border.css, separator_width=1.0,
            separator_margin=8.0,
        )
        title_tp = TitlePanel(
            height=80.0, show_separator=False,
        )
        blank_tp = TitlePanel(
            height=0.0, show_separator=False,
        )

        footer = FooterPanel(
            enabled=True, separator_color=palette.border.css,
            font_name=typography.caption.family,
            font_size=typography.caption.size,
            color=palette.text_secondary.css,
            center_text="Corporate Report",
        )
        no_footer = FooterPanel(enabled=False)

        layouts = {
            "default": LayoutConfig(name="default", rows=1, cols=1),
        }
        bg = SolidBackground(palette.background.css)

        slide_types = {
            "default": SlideTypeConfig(
                name="default",
                title_panel=default_tp,
                footer_panel=footer,
                layout="default",
                background=bg,
            ),
            "title": SlideTypeConfig(
                name="title",
                title_panel=title_tp,
                footer_panel=no_footer,
                layout="default",
                background=bg,
            ),
            "blank": SlideTypeConfig(
                name="blank",
                title_panel=blank_tp,
                footer_panel=no_footer,
                background=bg,
            ),
        }
        super().__init__(
            name="Corporate",
            palette=palette,
            typography=typography,
            table_style=table_style,
            layouts=layouts,
            slide_types=slide_types,
            footer_panel=footer,
        )


@Theme.register("dark")
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
        from reporting.title_config import TitlePanel

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

        default_tp = TitlePanel(
            height=60.0, show_separator=True,
            separator_color=palette.border.css, separator_width=1.0,
            separator_margin=8.0,
        )
        title_tp = TitlePanel(
            height=80.0, show_separator=False,
        )
        blank_tp = TitlePanel(
            height=0.0, show_separator=False,
        )

        from reporting.background import SolidBackground

        footer = FooterPanel(
            enabled=True, separator_color=palette.border.css,
            font_name=typography.caption.family,
            font_size=typography.caption.size,
            color=palette.text_secondary.css,
            center_text="Dark Report",
        )
        no_footer = FooterPanel(enabled=False)

        layouts = {
            "default": LayoutConfig(name="default", rows=1, cols=1),
        }
        bg = SolidBackground(palette.background.css)
        slide_types = {
            "default": SlideTypeConfig(
                name="default",
                title_panel=default_tp,
                footer_panel=footer,
                layout="default",
                background=bg,
            ),
            "title": SlideTypeConfig(
                name="title",
                title_panel=title_tp,
                footer_panel=no_footer,
                layout="default",
                background=bg,
            ),
            "blank": SlideTypeConfig(
                name="blank",
                title_panel=blank_tp,
                footer_panel=no_footer,
                background=bg,
            ),
        }
        super().__init__(
            name="Dark",
            palette=palette,
            typography=typography,
            table_style=table_style,
            layouts=layouts,
            slide_types=slide_types,
            footer_panel=footer,
        )


@Theme.register("light")
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
        from reporting.title_config import TitlePanel
        from reporting.background import SolidBackground

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

        default_tp = TitlePanel(
            height=60.0, show_separator=True,
            separator_color=palette.border.css, separator_width=1.0,
            separator_margin=8.0,
        )
        title_tp = TitlePanel(
            height=80.0, show_separator=False,
        )
        blank_tp = TitlePanel(
            height=0.0, show_separator=False,
        )

        footer = FooterPanel(
            enabled=True, separator_color=palette.border.css,
            font_name=typography.caption.family,
            font_size=typography.caption.size,
            color=palette.text_secondary.css,
            center_text="Light Report",
        )
        no_footer = FooterPanel(enabled=False)

        layouts = {
            "default": LayoutConfig(name="default", rows=1, cols=1),
        }
        bg = SolidBackground(palette.background.css)
        slide_types = {
            "default": SlideTypeConfig(
                name="default",
                title_panel=default_tp,
                footer_panel=footer,
                layout="default",
                background=bg,
            ),
            "title": SlideTypeConfig(
                name="title",
                title_panel=title_tp,
                footer_panel=no_footer,
                layout="default",
                background=bg,
            ),
            "blank": SlideTypeConfig(
                name="blank",
                title_panel=blank_tp,
                footer_panel=no_footer,
                background=bg,
            ),
        }
        super().__init__(
            name="Light",
            palette=palette,
            typography=typography,
            table_style=table_style,
            layouts=layouts,
            slide_types=slide_types,
            footer_panel=footer,
        )
