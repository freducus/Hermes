"""Slide type configuration — pre-defined slide templates within a theme.

A ``SlideTypeConfig`` bundles all defaults for a slide: title panel
height, title/subtitle font config, footer config, optional background,
and optional pre-defined grid layout.

Slide types live inside a ``Theme.slide_types`` dict.  Users pick one
via ``Slide(..., slide_type="default")`` and can still override any
individual parameter.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Optional

from reporting.layout.geometry import Edges

if TYPE_CHECKING:
    from reporting.background import Background
    from reporting.elements.text import TextAlignment
    from reporting.footer_config import FooterConfig
    from reporting.styles.theme import Theme
    from reporting.title_config import TitleConfig, SubtitleConfig, TitlePanelConfig


@dataclasses.dataclass
class SlideTypeConfig:
    """Pre-defined slide template bundled in a theme.

    Args:
        name: Type name used as key in ``Theme.slide_types``.
        title_panel_height: Height of the title panel in pixels
            (default ``60.0``).
        title_config: Title font and separator config
            (default ``None`` = derive from theme typography).
        subtitle_config: Subtitle font config
            (default ``None`` = derive from theme typography).
        title_panel_config: Title/subtitle layout arrangement
            (default ``TitlePanelConfig()``).
        footer_config: Footer styling and content
            (default ``None`` = ``FooterConfig(enabled=False)``).
        footer_logo: Optional path to a logo image placed in
            the left footer cell (default ``None``).
        background: Optional default slide background
            (default ``None``).
        grid_rows: Pre-defined grid rows (default ``None``).
        grid_cols: Pre-defined grid columns (default ``None``).
        grid_kwargs: Extra keyword arguments passed to
            ``grid_layout()`` (default ``{}``).
    """

    name: str = "default"
    title_panel_height: float = 60.0
    title_config: Optional[TitleConfig] = None
    subtitle_config: Optional[SubtitleConfig] = None
    title_panel_config: Optional[TitlePanelConfig] = None
    footer_config: Optional["FooterConfig"] = None
    footer_logo: Optional[str] = None
    background: Optional["Background"] = None
    grid_rows: Optional[int] = None
    grid_cols: Optional[int] = None
    grid_kwargs: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_theme(
        cls,
        theme: "Theme",
        name: str = "default",
        title_panel_height: float = 60.0,
        footer_enabled: bool = True,
    ) -> "SlideTypeConfig":
        """Create a ``SlideTypeConfig`` deriving defaults from a ``Theme``.

        Args:
            theme: Theme to derive typography and palette from.
            name: Type name.
            title_panel_height: Default title panel height.
            footer_enabled: Whether the footer is enabled by default.

        Returns:
            A fully-populated ``SlideTypeConfig``.
        """
        from reporting.elements.text import TextAlignment
        from reporting.footer_config import FooterConfig
        from reporting.title_config import TitleConfig, SubtitleConfig, TitlePanelConfig

        title_config = TitleConfig(
            font_name=theme.typography.heading_1.family,
            font_size=theme.typography.heading_1.size,
            bold=theme.typography.heading_1.bold,
            italic=theme.typography.heading_1.italic,
            color=theme.typography.heading_1.color or theme.palette.primary.css,
            alignment=TextAlignment.LEFT,
            show_separator=True,
            separator_color=theme.palette.border.css,
            separator_width=1.0,
            separator_margin=8.0,
        )
        subtitle_config = SubtitleConfig(
            font_name=theme.typography.body.family,
            font_size=theme.typography.body.size,
            bold=theme.typography.body.bold,
            italic=theme.typography.body.italic,
            color=theme.typography.body.color or theme.palette.text_secondary.css,
            alignment=TextAlignment.LEFT,
        )
        footer_config = FooterConfig(
            enabled=footer_enabled,
            separator_color=theme.palette.border.css,
            font_name=theme.typography.caption.family,
            font_size=theme.typography.caption.size,
            color=theme.palette.text_secondary.css,
        )

        return cls(
            name=name,
            title_panel_height=title_panel_height,
            title_config=title_config,
            subtitle_config=subtitle_config,
            title_panel_config=TitlePanelConfig(),
            footer_config=footer_config,
        )


__all__ = ["SlideTypeConfig"]
