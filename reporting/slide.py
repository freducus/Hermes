"""Slide — a single page in a report with grid layout and NumPy-style cell access."""

from __future__ import annotations

from typing import Any, Optional, Union

from reporting.layout.geometry import Edges, Rect, Size
from reporting.layout.grid import Grid, GridCell
from reporting.layout.panel import HAlign, VAlign
from reporting.layout.sizing import Sizing, Px
from reporting.elements.text import TextElement
from reporting.elements.image import ImageElement
from reporting.elements.figure import FigureElement
from reporting.elements.table import TableElement
from reporting.elements.tablespec_element import TableSpecElement
from reporting.styles.theme import Theme, CorporateTheme
from reporting.background import Background, BackgroundType, SolidBackground, GradientBackground, ImageBackground
from reporting.title_config import TitleConfig, SubtitleConfig, TitlePanelConfig, SubtitlePlacement


class Slide:
    """A single slide (page) in a report.

    Every ``Slide`` has a built-in **title panel** rendered
    automatically at the top.  The remaining area below it is
    divided into a grid via ``grid_layout()``.

    Cell access uses NumPy-style indexing::

        slide[row, col]          # single cell
        slide[0, :]              # entire first row
        slide[:, 0]              # entire first column
        slide[0:2, 1:3]          # sub-grid

    Args:
        title: Slide title displayed in the title panel.
        subtitle: Optional subtitle (default ``None``).
        theme: Visual theme. Falls back to ``CorporateTheme()``
            when ``None`` (default ``None``).
        width: Slide width in pixels (default ``960.0``).
        height: Slide height in pixels (default ``540.0``).
        title_panel_height: Height of the title panel in pixels
            (default ``60.0``).
        background: Slide background.  Accepts a hex string
            ``"#RRGGBB"``, a named CSS color, or a
            ``SolidBackground`` / ``GradientBackground`` /
            ``ImageBackground`` instance (default ``None``).
        title_config: Configure title font, size, colour, and
            separator (default ``TitleConfig()``).
        subtitle_config: Configure subtitle font and colour
            (default ``SubtitleConfig()``).
        title_panel_config: Configure subtitle placement and
            padding (default ``TitlePanelConfig()``).

    Example::

        from reporting.slide import Slide

        slide = Slide("Results", subtitle="Test data")
        slide.grid_layout(rows=2, cols=2, gap=8)
        slide[0, 0].text("Top-left", bold=True)
        slide[1, :].text("Spanning bottom row")
    """

    def __init__(
        self,
        title: str,
        subtitle: Optional[str] = None,
        theme: Optional[Theme] = None,
        width: float = 960.0,
        height: float = 540.0,
        title_panel_height: float = 60.0,
        background: Optional[Union[str, SolidBackground, GradientBackground, ImageBackground]] = None,
        title_config: Optional[TitleConfig] = None,
        subtitle_config: Optional[SubtitleConfig] = None,
        title_panel_config: Optional[TitlePanelConfig] = None,
    ):
        self.title = title
        self.subtitle = subtitle
        self.theme = theme or CorporateTheme()
        self.width = width
        self.height = height
        self.title_panel_height = title_panel_height
        if isinstance(background, str):
            self.background: Optional[Background] = SolidBackground(background)
        else:
            self.background: Optional[Background] = background
        self.title_config = title_config or TitleConfig()
        self.subtitle_config = subtitle_config or SubtitleConfig()
        self.title_panel_config = title_panel_config or TitlePanelConfig()
        self._grid: Optional[Grid] = None
        self._elements: dict[tuple[int, int], Any] = {}

    @property
    def size(self) -> Size:
        """Return the full slide dimensions as a ``Size``.

        Returns:
            ``Size(width, height)`` in pixels.
        """
        return Size(self.width, self.height)

    @property
    def content_size(self) -> Size:
        """Return the available area below the title panel.

        The content area is the full slide minus the title panel.

        Returns:
            ``Size(width, height - title_panel_height)`` in pixels.
        """
        return Size(self.width, self.height - self.title_panel_height)

    def get_cell_rects(self) -> list[list[Rect]]:
        """Compute the pixel rectangles of every grid cell.

        Raises:
            RuntimeError: If ``grid_layout()`` has not been called.

        Returns:
            A 2-D list of ``Rect``, one per cell in the grid.
        """
        if self._grid is None:
            raise RuntimeError("Call grid_layout() before accessing cells.")
        _, rects = self._grid.layout(self.content_size)
        return [[Rect(r.x, r.y, r.width, r.height) for r in row] for row in rects]

    def grid_layout(
        self,
        rows: int = 1,
        cols: int = 1,
        row_sizes: Optional[list[Sizing]] = None,
        col_sizes: Optional[list[Sizing]] = None,
        gap: float = 0.0,
        padding: Optional[Edges] = None,
    ) -> None:
        """Divide the content area into a grid of cells.

        Must be called before accessing cells with ``slide[r, c]``.

        Args:
            rows: Number of rows (default ``1``).
            cols: Number of columns (default ``1``).
            row_sizes: Per-row sizing. Each element can be
                ``Px(v)`` for fixed, ``Percent(v)`` for
                percentage, ``Fill`` for remaining space, or
                a plain float treated as ``Px(v)``
                (default ``None`` = all rows use ``Fill``).
            col_sizes: Per-column sizing, same rules as
                ``row_sizes`` (default ``None`` = all
                columns use ``Fill``).
            gap: Spacing between cells in pixels
                (default ``0.0``).
            padding: Outer padding around the grid as an
                ``Edges``.  ``Edges.all(v)`` sets uniform
                padding (default ``None`` = no padding).

        Example::

            slide.grid_layout(rows=3, cols=2, gap=8,
                              padding=Edges.all(12))
            slide[0, 0].text("Cell (0, 0)")
        """
        self._grid = Grid(
            rows=rows,
            cols=cols,
            row_sizes=row_sizes,
            col_sizes=col_sizes,
            gap=gap,
            padding=padding,
        )

    def __getitem__(self, pos: tuple[Union[int, slice], Union[int, slice]]) -> _CellProxy:
        """Access a grid cell by row and column (NumPy-style indexing).

        Args:
            pos: A ``(row, col)`` tuple.  Each coordinate can be an
                ``int`` or a ``slice``.  Slices span multiple cells
                (auto ``rowspan`` / ``colspan``).

        Returns:
            A ``_CellProxy`` that provides chained methods
            (``.text()``, ``.image()``, etc.).

        Raises:
            RuntimeError: If ``grid_layout()`` has not been called.

        Example::

            slide[0, 0]          # single cell
            slide[0, :]          # whole first row
            slide[:, 1]          # whole second column
            slide[1:, 2:]        # bottom-right sub-grid
        """
        if self._grid is None:
            raise RuntimeError("Call grid_layout() before accessing cells.")
        cell = self._grid[pos]
        return _CellProxy(self, cell)

    def _set_cell_element(self, cell: GridCell, element: Any) -> None:
        cell.element = element
        self._elements[(cell.panel.row, cell.panel.col)] = element


class _CellProxy:
    """Intermediate object returned by ``slide[r, c]``.

    Do **not** instantiate directly.  Every cell-access method
    returns ``self`` or an element, enabling chaining.
    """

    def __init__(self, slide: Slide, cell: GridCell) -> None:
        self._slide = slide
        self._cell = cell

    def align(
        self,
        h_align: HAlign = HAlign.STRETCH,
        v_align: VAlign = VAlign.STRETCH,
    ) -> _CellProxy:
        """Set content alignment inside the cell.

        Call before the element-creating method (``.text()``,
        ``.image()``, etc.) so alignment affects the rendered
        content.

        Args:
            h_align: Horizontal alignment.

                - ``HAlign.LEFT`` — left-align content
                - ``HAlign.CENTER`` — centre horizontally
                - ``HAlign.RIGHT`` — right-align content
                - ``HAlign.STRETCH`` — stretch content to fill
                  cell width (default)

            v_align: Vertical alignment.

                - ``VAlign.TOP`` — top-align content
                - ``VAlign.MIDDLE`` — centre vertically
                - ``VAlign.BOTTOM`` — bottom-align content
                - ``VAlign.STRETCH`` — stretch content to fill
                  cell height (default)

        Returns:
            ``self`` for chaining.

        Example::

            slide[0, 0].align(HAlign.CENTER, VAlign.MIDDLE).text("Hi")
            slide[1, 0].align(HAlign.LEFT, VAlign.TOP).image("img.png")
        """
        self._cell.panel.h_align = h_align
        self._cell.panel.v_align = v_align
        return self

    def text(self, content: str = "", **kwargs: object) -> TextElement:
        """Add a text element to this cell.

        Text content is plain text.  Rich formatting (bold, italic,
        colour, font) is passed as keyword arguments and applied to
        the entire string.  Use ``TextElement`` directly for
        multi-run (mixed-format) text.

        Args:
            content: The text to display.  May contain ``\\n`` for
                line breaks.

        Keyword Args:
            bold: Whether the text is bold (default ``False``).
            italic: Whether the text is italic (default ``False``).
            size: Font size in points (default ``None`` = theme
                default, typically ``10``).
            color: Text colour as a hex string ``"#RRGGBB"``, a
                named CSS colour, or an ``(r, g, b)`` tuple
                (default ``None``).
            font_name: Font family such as ``"Helvetica"``,
                ``"Times-Roman"``, ``"Courier"`` (default
                ``None`` = theme default).
            alignment: One of ``TextAlignment.LEFT``,
                ``TextAlignment.CENTER``,
                ``TextAlignment.RIGHT``,
                ``TextAlignment.JUSTIFY`` (default
                ``TextAlignment.LEFT``).

        Returns:
            The created ``TextElement``.

        Example::

            slide[0, 0].text("Hello", bold=True, size=14,
                              color="#1F4E79")
            slide[1, 0].text("Line 1\\nLine 2",
                              alignment=TextAlignment.CENTER)
        """
        el = TextElement(content, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def image(self, source: str = "", **kwargs: object) -> ImageElement:
        """Add an image from a file to this cell.

        Supported formats: PNG, JPG.

        Args:
            source: Path to the image file.

        Keyword Args:
            scale: Uniform scale factor (default ``1.0``).
            fit_mode: How to fit the image in the cell.

                - ``ImageFitMode.ORIGINAL`` — native size, scaled
                  down only if larger than the cell (default)
                - ``ImageFitMode.FIT_VERTICAL`` — fill cell height
                - ``ImageFitMode.FIT_HORIZONTAL`` — fill cell width
            width: Explicit width in points.  Overrides ``scale``
                and ``fit_mode`` for the width axis
                (default ``None``).
            height: Explicit height in points.  Overrides
                ``scale`` and ``fit_mode`` for the height axis
                (default ``None``).
            rotation: Rotation angle in degrees clockwise
                (default ``0.0``).
            opacity: Opacity from ``0.0`` (transparent) to
                ``1.0`` (opaque) (default ``1.0``).
            alt_text: Alternative text for accessibility
                (default ``""``).

        Returns:
            The created ``ImageElement``.

        Example::

            slide[0, 0].image("chart.png", scale=0.8)
            slide[0, 1].image("photo.jpg",
                              fit_mode=ImageFitMode.FIT_VERTICAL)
            slide[1, 0].image("logo.png", width=120, opacity=0.9)
        """
        el = ImageElement(source, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def plot(self, figure: object = None, **kwargs: object) -> FigureElement:
        """Embed a matplotlib figure in this cell.

        Args:
            figure: A ``matplotlib.figure.Figure`` instance.

        Keyword Args:
            format: Output format — ``"png"`` (raster, default),
                ``"pdf"`` (vector, requires ``pdfrw``), or
                ``"svg"`` (requires ``svgwrite``).
            dpi: Resolution for raster output (default ``150``).
            preserve_aspect: Whether to preserve the figure's
                aspect ratio (default ``False``).
            container_width_pct: Width as a percentage of the
                cell width (default ``None`` = use native size).
            container_height_pct: Height as a percentage of the
                cell width (default ``None`` = use native size).

        Returns:
            The created ``FigureElement``.

        Example::

            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([1, 2, 3], [4, 5, 6])
            slide[0, 0].plot(fig, format="pdf", preserve_aspect=True)
        """
        el = FigureElement(figure, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def table(self, data: object = None, **kwargs: object) -> TableElement:
        """Add a table to this cell.

        Accepts either a pandas ``DataFrame`` (rendered as a
        basic table) or a ``TableSpec`` (rendered with full
        TableSpec styling).  Passing a ``TableSpec``
        automatically delegates to ``table_spec()``.

        Args:
            data: A pandas ``DataFrame``, a ``TableSpec``, or
                anything ``TableSpec`` can convert.

        Keyword Args:
            header: Whether to show a header row
                (default ``True``, DataFrame only).
            include_index: Whether to show the DataFrame index
                (default ``False``, DataFrame only).
            zebra: Enable alternating row colours
                (default ``False``).
            numeric_format: Format string for numeric values
                (e.g. ``"{:.2f}"``) (default ``None``).

        Returns:
            A ``TableElement`` (DataFrame input) or
            ``TableSpecElement`` (TableSpec input).

        Example::

            import pandas as pd
            df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
            slide[0, 0].table(df, zebra=True)

            from reporting.tablespec import TableSpec, Column
            ts = TableSpec(columns=[Column("x"), Column("y")])
            ts.row(1, 2).row(3, 4)
            slide[0, 0].table(ts)
        """
        from reporting.tablespec.spec import TableSpec
        if isinstance(data, TableSpec):
            return self.table_spec(data, **kwargs)  # type: ignore[return-value]
        el = TableElement(data, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def table_spec(self, spec: object = None, **kwargs: object) -> TableSpecElement:
        """Add a ``TableSpec`` to this cell (explicit method).

        Prefer calling ``.table(ts)`` which auto-detects
        ``TableSpec``; this method exists for cases where
        the type detection needs to be bypassed.

        Args:
            spec: A ``TableSpec`` instance.
            **kwargs: Ignored (reserved for future use).

        Returns:
            The created ``TableSpecElement``.

        Example::

            ts = TableSpec(columns=[Column("A"), Column("B")])
            ts.row(10, 20)
            slide[0, 0].table_spec(ts)
        """
        el = TableSpecElement(spec, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el
