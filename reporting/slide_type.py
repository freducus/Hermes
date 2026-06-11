"""Slide type configuration — pre-defined slide templates within a theme.

A ``SlideTypeConfig`` bundles panel defaults for a slide: title panel
layout, footer panel config, optional background, and optional pre-defined
grid layout.

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
    from reporting.footer_config import FooterPanel
    from reporting.styles.theme import Theme
    from reporting.title_config import TitlePanel


@dataclasses.dataclass
class SlideTypeConfig:
    """Pre-defined slide template bundled in a theme.

    Args:
        name: Type name used as key in ``Theme.slide_types``.
        title_panel: Title panel layout (height, padding, separator,
            subtitle placement).  Falls back to ``TitlePanel()``
            when ``None`` (default ``None``).
        footer_panel: Footer panel styling and content.
            Falls back to ``FooterPanel(enabled=False)`` when
            ``None`` (default ``None``).
        background: Optional default slide background
            (default ``None``).
        grid_rows: Pre-defined grid rows (default ``None``).
        grid_cols: Pre-defined grid columns (default ``None``).
        grid_kwargs: Extra keyword arguments passed to
            ``grid_layout()`` (default ``{}``).
    """

    name: str = "default"
    title_panel: Optional[TitlePanel] = None
    footer_panel: Optional[FooterPanel] = None
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
        from reporting.footer_config import FooterPanel
        from reporting.title_config import TitlePanel

        return cls(
            name=name,
            title_panel=TitlePanel(
                height=title_panel_height,
                show_separator=True,
                separator_color=theme.palette.border.css,
                separator_width=1.0,
                separator_margin=8.0,
            ),
            footer_panel=FooterPanel(
                enabled=footer_enabled,
                separator_color=theme.palette.border.css,
                font_name=theme.typography.caption.family,
                font_size=theme.typography.caption.size,
                color=theme.palette.text_secondary.css,
            ),
        )


__all__ = ["SlideTypeConfig"]
