"""Footer panel configuration — styling for the slide footer panel.

Pure data model with zero renderer dependencies.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Optional

from reporting.layout.geometry import Edges
from reporting.styles.colors import ColorValue, normalize_color

if TYPE_CHECKING:
    from reporting.styles.theme import Theme

__all__ = ["FooterPanel"]


@dataclasses.dataclass
class FooterPanel:
    """Styling and layout for the slide footer panel.

    Args:
        height: Footer height in pixels (default ``28.0``).
        show_separator: Whether to draw a line above the footer
            (default ``True``).
        separator_color: Colour of the separator line
            (default ``"#CCCCCC"``).
        separator_width: Thickness of the separator line in points
            (default ``1.0``).
        separator_margin: Gap between separator and the top of the
            footer panel in pixels (default ``4.0``).
        font_name: Default font family for footer text
            (default ``"Helvetica"``).
        font_size: Default font size in points
            (default ``8.0``).
        color: Default text colour (default ``"#999999"``).
        padding: Inner padding around the footer content as an
            ``Edges``.  Default: ``Edges(left=20, right=20,
            top=4, bottom=4)``.
        enabled: Whether the footer is rendered
            (default ``True``).
        center_text: Text to display in the centre footer cell;
            ``{page}`` and ``{total}`` are replaced automatically
            (default ``""``).
        logo: Optional path to a logo image placed in the left
            footer cell (default ``None``).

    Example::

        from reporting.footer_config import FooterPanel
        from reporting.layout.geometry import Edges

        panel = FooterPanel(
            height=32,
            separator_color="#C00000",
            separator_width=2,
            font_size=9,
            padding=Edges(left=24, right=24, top=6, bottom=6),
        )
        slide = Slide("Title", footer_panel=panel)
    """

    height: float = 28.0
    show_separator: bool = True
    separator_color: ColorValue = "#CCCCCC"
    separator_width: float = 1.0
    separator_margin: float = 4.0
    font_name: str = "Helvetica"
    font_size: float = 8.0
    color: ColorValue = "#999999"
    padding: Edges = dataclasses.field(
        default_factory=lambda: Edges(left=20, right=20, top=4, bottom=4),
    )
    enabled: bool = False
    center_text: str = ""
    logo: Optional[str] = None

    def __post_init__(self) -> None:
        self.separator_color = normalize_color(self.separator_color)
        self.color = normalize_color(self.color)

    @classmethod
    def from_theme(cls, theme: Theme) -> FooterPanel:
        """Create a ``FooterPanel`` from a ``Theme``.

        Derives font family, size, and separator colour from
        the theme's caption typography and palette.

        Args:
            theme: The theme to use as a source.

        Returns:
            A fully-populated ``FooterPanel``.
        """
        cap = theme.typography.caption
        return cls(
            separator_color=theme.palette.border.css,
            font_name=cap.family,
            font_size=cap.size,
            color=theme.palette.text_secondary.css,
        )
