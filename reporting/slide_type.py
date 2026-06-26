"""Slide type configuration — pre-defined slide templates within a theme.

A ``SlideTypeConfig`` bundles default text content (title, subtitle,
cell texts), a named layout reference, and panel configuration.
Every field is optional — the resolution chain (base_slide → theme →
slide_type → explicit) fills in what is missing.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from reporting.background import Background
    from reporting.footer_config import FooterPanel
    from reporting.title_config import TitlePanel, TitleText, SubtitleText


@dataclasses.dataclass
class SlideTypeConfig:
    """Pre-defined slide template bundled in a theme.

    Args:
        name: Type name used as key in ``Theme.slide_types``.
        title_text: Default title text (plain ``str`` or
            ``TitleText``).  Falls back to theme typography
            when ``None`` (default ``None``).
        subtitle_text: Default subtitle text (plain ``str`` or
            ``SubtitleText``).  Falls back to theme typography
            when ``None`` (default ``None``).
        layout: Name of a ``LayoutConfig`` in the parent theme's
            ``layouts`` dict.  When set, the slide automatically
            gets a grid with those dimensions (default ``None``).
        title_panel: Title panel layout (height, padding,
            separator, subtitle placement).  Falls back to
            ``TitlePanel.from_theme()`` when ``None``
            (default ``None``).
        footer_panel: Footer panel styling and content.
            Falls back to ``theme.footer_panel`` when ``None``
            (default ``None``).
        background: Optional default slide background
            (default ``None``).
        cells: Default text content for grid cells, keyed by
            ``(row, col)``.  When the slide is created, each
            matching cell gets a ``TextElement`` with the
            given string (default ``{}``).

    Example::

        from reporting.slide_type import SlideTypeConfig
        from reporting.title_config import TitlePanel
        from reporting.footer_config import FooterPanel

        st = SlideTypeConfig(
            name="results",
            title_text="Results",
            subtitle_text="Experimental data",
            layout="two_by_two",
            title_panel=TitlePanel(height=60),
            footer_panel=FooterPanel(center_text="Results Report"),
            cells={(0, 0): "Metric A", (0, 1): "Metric B"},
        )
    """

    name: str = "default"
    title_text: Optional[Union[str, "TitleText"]] = None
    subtitle_text: Optional[Union[str, "SubtitleText"]] = None
    layout: Optional[str] = None
    title_panel: Optional["TitlePanel"] = None
    footer_panel: Optional["FooterPanel"] = None
    background: Optional["Background"] = None
    cells: dict[tuple[int, int], str] = dataclasses.field(default_factory=dict)


__all__ = ["SlideTypeConfig"]
