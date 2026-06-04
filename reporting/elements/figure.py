"""Figure element — wraps a matplotlib figure, backend-agnostic."""

from __future__ import annotations

from typing import Any, Optional

from reporting.elements.base import BaseElement, ElementType


class FigureElement(BaseElement):
    """A matplotlib figure embedded as a content element.

    The figure is rendered to raster (PNG) or vector format
    (PDF for ReportLab, SVG for HTML) at render time.

    Output format:
        - ``"png"`` (default) — raster image at ``dpi``
          resolution (works with all renderers)
        - ``"pdf"`` — vector PDF via ``pdfrw`` (PDF renderer
          only; requires ``pip install pdfrw``)
        - ``"svg"`` — vector SVG (HTML renderer only)

    Container-relative sizing:
        When ``container_width_pct`` or ``container_height_pct``
        is set, the figure's size is computed as a percentage of
        the container (panel) dimensions instead of the
        matplotlib ``figsize``.

        When ``preserve_aspect`` is ``True``, the figure is
        scaled uniformly to fit within the content rect,
        anchored per cell alignment (default ``False`` =
        stretch to fill).

    Args:
        figure: A ``matplotlib.figure.Figure`` instance.
        **kwargs: Property overrides:

            - ``dpi``: ``int`` output resolution for raster
              formats (default ``150``)
            - ``bbox_inches``: ``Optional[str]`` bbox setting
              for the save operation (default ``"tight"``)
            - ``format``: ``str`` — ``"png"``, ``"pdf"``,
              or ``"svg"`` (default ``"png"``)
            - ``container_width_pct``: ``Optional[float]``
              width as a % of the container (default ``None``)
            - ``container_height_pct``: ``Optional[float]``
              height as a % of the container (default ``None``)
            - ``preserve_aspect``: ``bool`` maintain aspect
              ratio when scaling (default ``False``)

    Example::

        import matplotlib.pyplot as plt
        from reporting.elements.figure import FigureElement

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [4, 5, 6])

        el = FigureElement(fig, format="pdf", preserve_aspect=True)
        el2 = FigureElement(fig, container_width_pct=80)
    """
    figure: Any = None
    dpi: int = 150
    bbox_inches: Optional[str] = "tight"
    format: str = "png"
    container_width_pct: Optional[float] = None
    container_height_pct: Optional[float] = None
    preserve_aspect: bool = False

    def __init__(self, figure: object = None, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.FIGURE, properties=kwargs)
        self.figure = figure
        self.dpi = int(kwargs.get("dpi", 150))
        self.bbox_inches = kwargs.get("bbox_inches", "tight")
        self.format = str(kwargs.get("format", "png"))
        self.container_width_pct = kwargs.get("container_width_pct", None)
        self.container_height_pct = kwargs.get("container_height_pct", None)
        self.preserve_aspect = bool(kwargs.get("preserve_aspect", False))
