"""Slide — a single page in a report with grid layout and NumPy-style cell access."""

from __future__ import annotations

from typing import Any, Optional, Union

from reporting.layout.geometry import Edges, Rect, Size
from reporting.layout.grid import Grid, GridCell, GridCellProxy
from reporting.layout.panel import HAlign, VAlign
from reporting.layout.sizing import Sizing
from reporting.elements.text import TextElement
from reporting.elements.image import ImageElement
from reporting.elements.figure import FigureElement
from reporting.elements.table import TableElement
from reporting.elements.tablespec_element import TableSpecElement
from reporting.elements.container import ContainerElement
from reporting.styles.theme import Theme, CorporateTheme
from reporting.background import Background, BackgroundType, SolidBackground, GradientBackground, ImageBackground
from reporting.title_config import TitleText, SubtitleText, TitlePanel
from reporting.styles.typography import STYLE_ALIASES


class Slide:
    """A single slide (page) in a report.

    Create a ``Slide``, then set its title, subtitle, background,
    and grid layout::

        from reporting.slide import Slide

        slide = Slide()
        slide.title = "Results"
        slide.subtitle = "Test data"
        slide.grid_layout(rows=2, cols=2, gap=8)
        slide[0, 0].text("Top-left", bold=True)
        slide[1, :].text("Spanning bottom row")

    Args:
        theme: Visual theme.  Falls back to ``CorporateTheme()``
            when ``None`` (default ``None``).
        base: Another ``Slide`` whose theme and grid structure
            are used as a starting point.  Content cells are
            **not** copied (default ``None``).
    """

    def __init__(
        self,
        theme: Optional[Union[str, Theme]] = None,
        base: Optional[Slide] = None,
    ):
        self._grid = None
        self._elements = {}
        self.theme = CorporateTheme() if theme is None else theme
        self.width: float = 960.0
        self.height: float = 540.0
        self._title: TitleText = TitleText.from_theme(self.theme)
        self._subtitle: Optional[SubtitleText] = None
        self._background: Optional[Background] = None
        self.title_panel: TitlePanel = TitlePanel()

        if base is not None:
            self.theme = base.theme
            self.width = base.width
            self.height = base.height
            if base._grid is not None:
                self._grid = base._grid.copy_structure()

    # --- Title property ---

    @property
    def title(self) -> TitleText:
        return self._title

    @title.setter
    def title(self, value: Union[str, TitleText]) -> None:
        if isinstance(value, TitleText):
            self._title = value
        else:
            self._title = TitleText.from_theme(self.theme, text=str(value))

    # --- Subtitle property ---

    @property
    def subtitle(self) -> Optional[SubtitleText]:
        return self._subtitle

    @subtitle.setter
    def subtitle(self, value: Optional[Union[str, SubtitleText]]) -> None:
        if value is None:
            self._subtitle = None
        elif isinstance(value, SubtitleText):
            self._subtitle = value
        else:
            self._subtitle = SubtitleText.from_theme(self.theme, text=str(value))

    # --- Background property ---

    @property
    def background(self) -> Optional[Background]:
        return self._background

    @background.setter
    def background(self, value: Optional[Union[str, SolidBackground, GradientBackground, ImageBackground]]) -> None:
        if value is None:
            self._background = None
        elif isinstance(value, Background):
            self._background = value
        elif isinstance(value, str):
            self._background = SolidBackground(value)
        else:
            raise TypeError(f"Expected str or Background, got {type(value).__name__}")

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

        Returns:
            ``Size(width, height)`` in pixels.
        """
        return Size(self.width, self.height)

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
            typography=self.theme.typography,
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
        cell_proxy = self._grid[pos]
        return _CellProxy(self, cell_proxy)

    def _set_cell_element(self, cell: GridCell, element: Any) -> None:
        cell.element = element
        self._elements[(cell.panel.row, cell.panel.col)] = element


class _CellProxy:
    """Intermediate object returned by ``slide[r, c]``.

    Do **not** instantiate directly.  Every cell-access method
    returns ``self`` or an element, enabling chaining.
    """

    def __init__(self, slide: Slide, proxy: GridCellProxy) -> None:
        self._slide = slide
        self._proxy = proxy
        self._cell = proxy.cell

    @property
    def background_color(self) -> object:
        """Background colour of the cell's panel (property)."""
        return self._proxy.background_color

    @background_color.setter
    def background_color(self, value: object) -> None:
        self._proxy.background_color = value

    @property
    def padding(self) -> object:
        """Padding of the cell's panel (property)."""
        return self._proxy.padding

    @padding.setter
    def padding(self, value: object) -> None:
        self._proxy.padding = value

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
            v_align: Vertical alignment.

        Returns:
            ``self`` for chaining.

        Example::

            slide[0, 0].align(HAlign.CENTER, VAlign.MIDDLE).text("Hi")
        """
        self._proxy.align(h_align, v_align)
        return self

    def text(self, content: str = "", **kwargs: object) -> TextElement:
        """Add a text element to this cell.

        Text content is plain text.  Rich formatting (bold, italic,
        colour, font) is passed as keyword arguments and applied to
        the entire string.

        When ``style`` is given (e.g. ``"heading_1"``, ``"body"``,
        ``"caption"``), font properties are resolved from the
        slide's theme.  Explicit kwargs override the resolved
        values.

        Args:
            content: The text to display.  May contain ``\\n`` for
                line breaks.

        Keyword Args:
            style: A theme typography style name — ``"heading_1"``
                (or ``"h1"``), ``"heading_2"`` (or ``"h2"``),
                ``"heading_3"`` (or ``"h3"``), ``"body"``,
                ``"caption"``, ``"code"``, ``"mono"``.
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
                ``TextAlignment.CENTER``, ``TextAlignment.RIGHT``,
                ``TextAlignment.JUSTIFY``.

        Returns:
            The created ``TextElement``.

        Example::

            slide[0, 0].text("Hello", style="heading_1")
            slide[1, 0].text("Line 1\\nLine 2",
                              alignment=TextAlignment.CENTER)
        """
        style_name = kwargs.pop("style", None)
        if style_name is not None:
            typo = self._slide.theme.typography
            name = STYLE_ALIASES.get(style_name, style_name)
            spec = getattr(typo, name, None)
            if spec is not None:
                kwargs.setdefault("font_name", spec.family)
                kwargs.setdefault("size", spec.size)
                kwargs.setdefault("bold", spec.bold)
                kwargs.setdefault("italic", spec.italic)
                if spec.color is not None and "color" not in kwargs:
                    kwargs["color"] = spec.color
        el = self._proxy.text(content, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def image(self, source: str = "", **kwargs: object) -> ImageElement:
        """Add an image from a file to this cell.

        Args:
            source: Path to the image file.

        Keyword Args:
            scale: Uniform scale factor (default ``1.0``).
            fit_mode: How to fit the image in the cell.
            width: Explicit width in points.
            height: Explicit height in points.
            rotation: Rotation angle in degrees clockwise.
            opacity: Opacity from ``0.0`` to ``1.0``.
            alt_text: Alternative text for accessibility.

        Returns:
            The created ``ImageElement``.
        """
        el = self._proxy.image(source, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def plot(self, figure: object = None, **kwargs: object) -> FigureElement:
        """Embed a matplotlib figure in this cell.

        Args:
            figure: A ``matplotlib.figure.Figure`` instance.

        Keyword Args:
            format: Output format — ``"png"``, ``"pdf"``, or ``"svg"``.
            dpi: Resolution for raster output (default ``150``).
            preserve_aspect: Whether to preserve the figure's
                aspect ratio (default ``False``).
            container_width_pct: Width as a percentage of the
                cell width (default ``None``).
            container_height_pct: Height as a percentage of the
                cell width (default ``None``).

        Returns:
            The created ``FigureElement``.

        Example::

            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([1, 2, 3], [4, 5, 6])
            slide[0, 0].plot(fig)
        """
        el = self._proxy.plot(figure, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

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
            header: Whether to show a header row (default ``True``).
            include_index: Whether to show the DataFrame index
                (default ``False``).
            zebra: Enable alternating row colours (default ``False``).
            numeric_format: Format string for numeric values.

        Returns:
            A ``TableElement`` (DataFrame input) or
            ``TableSpecElement`` (TableSpec input).
        """
        from reporting.tablespec.spec import TableSpec
        if isinstance(data, TableSpec):
            return self.table_spec(data, **kwargs)  # type: ignore[return-value]
        el = self._proxy.table(data, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

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
        """
        el = self._proxy.table_spec(spec, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def grid_layout(self, grid: object) -> ContainerElement:
        """Add a nested sub-grid inside this cell.

        Wraps a ``Grid`` in a ``ContainerElement`` so you can
        place multiple items inside one cell.

        Args:
            grid: A ``Grid`` instance defining the sub-layout.

        Returns:
            The created ``ContainerElement``.

        Example::

            from reporting.layout.grid import Grid

            inner = Grid(rows=2, cols=1, gap=6)
            inner[0, 0].text("Top")
            inner[1, 0].text("Bottom")
            slide[2, :].grid_layout(inner)
        """
        el = self._proxy.grid_layout(grid)
        if hasattr(grid, 'typography'):
            grid.typography = self._slide.theme.typography
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]
