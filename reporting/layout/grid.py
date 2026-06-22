"""Grid layout engine — pure math, no renderer dependencies."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.layout.geometry import Point, Size, Rect, Edges
from reporting.layout.sizing import Sizing, LengthValue, SizingType, normalize
from reporting.layout.panel import Panel, HAlign, VAlign


@dataclasses.dataclass
class GridPosition:
    """Row / column coordinate within a ``Grid``.

    Not typically instantiated directly; used internally for
    cell look-up.

    Args:
        row: Row index.
        col: Column index.
    """
    row: int
    col: int


@dataclasses.dataclass
class GridCell:
    """A single cell in a ``Grid``, combining a ``Panel`` and an optional element.

    Args:
        panel: The cell's ``Panel`` (layout metadata).
        element: Content element (``TextElement``,
            ``ImageElement``, etc.), set when a cell is
            populated (default ``None``).
    """
    panel: Panel
    element: Optional[object] = None


class GridCellProxy:
    """Fluent proxy returned by ``Grid.__getitem__`` for adding content to a cell.

    Provides the same chained API as ``Slide`` cells::

        inner = Grid(rows=2, cols=1)
        inner[0, 0].text("Title", bold=True)
        inner[1, 0].plot(fig)
        slide[0, 0].grid_layout(inner)

    When you need the underlying ``GridCell``, use ``.cell``.
    """

    def __init__(self, cell: GridCell, typography: object = None) -> None:
        self._cell = cell
        self._typography = typography

    @property
    def cell(self) -> GridCell:
        """Return the underlying ``GridCell`` for direct access."""
        return self._cell

    @property
    def panel(self) -> Panel:
        """Return the cell's ``Panel``."""
        return self._cell.panel

    @property
    def element(self) -> Optional[object]:
        """Return the element assigned to this cell (or ``None``)."""
        return self._cell.element

    @element.setter
    def element(self, value: Optional[object]) -> None:
        self._cell.element = value

    @property
    def background_color(self) -> Optional[object]:
        """Background colour of the cell's panel."""
        return self._cell.panel.background_color

    @background_color.setter
    def background_color(self, value: object) -> None:
        from reporting.styles.colors import normalize_color
        self._cell.panel.background_color = normalize_color(value)

    @property
    def padding(self) -> Edges:
        """Padding of the cell's panel."""
        return self._cell.panel.padding

    @padding.setter
    def padding(self, value: Edges) -> None:
        self._cell.panel.padding = value

    def align(
        self,
        h_align: HAlign = HAlign.STRETCH,
        v_align: VAlign = VAlign.STRETCH,
    ) -> GridCellProxy:
        """Set content alignment inside the cell.

        Call before the element-creating method so alignment
        affects the rendered content.

        Args:
            h_align: Horizontal alignment.
            v_align: Vertical alignment.

        Returns:
            ``self`` for chaining.
        """
        self._cell.panel.h_align = h_align
        self._cell.panel.v_align = v_align
        return self

    def text(self, content: str = "", **kwargs: object) -> object:
        """Add a text element to this cell.

        When ``style`` is given (e.g. ``"heading_1"``, ``"body"``,
        ``"caption"``), font properties are resolved from the
        grid's typography (if available).  Explicit kwargs override
        the resolved values.

        Args:
            content: The text to display.

        Keyword Args:
            style: A typography style name — ``"heading_1"``
                (or ``"h1"``), ``"heading_2"`` (or ``"h2"``),
                ``"heading_3"`` (or ``"h3"``), ``"body"``,
                ``"caption"``, ``"code"``, ``"mono"``.
            bold: Whether the text is bold.
            italic: Whether the text is italic.
            size: Font size in points.
            color: Text colour.
            font_name: Font family name.
            alignment: Text alignment.

        Returns:
            The created ``TextElement``.
        """
        style_name = kwargs.pop("style", None)
        if style_name is not None:
            if self._typography is not None:
                from reporting.styles.typography import STYLE_ALIASES, FontSpec
                name = STYLE_ALIASES.get(style_name, style_name)
                spec = getattr(self._typography, name, None)
                if isinstance(spec, FontSpec):
                    kwargs.setdefault("font_name", spec.family)
                    kwargs.setdefault("size", spec.size)
                    kwargs.setdefault("bold", spec.bold)
                    kwargs.setdefault("italic", spec.italic)
                    if spec.color is not None and "color" not in kwargs:
                        kwargs["color"] = spec.color
            else:
                kwargs["style"] = style_name
        from reporting.elements.text import TextElement
        el: object = TextElement(content, **kwargs)
        self._cell.element = el
        return el

    def image(self, source: str = "", **kwargs: object) -> object:
        """Add an image from a file to this cell.

        Args:
            source: Path to the image file.

        Keyword Args:
            scale: Uniform scale factor (default ``1.0``).
            fit_mode: How to fit the image.
            width: Explicit width in points.
            height: Explicit height in points.
            rotation: Rotation angle in degrees.
            opacity: Opacity from ``0.0`` to ``1.0``.

        Returns:
            The created ``ImageElement``.
        """
        from reporting.elements.image import ImageElement
        el: object = ImageElement(source, **kwargs)
        self._cell.element = el
        return el

    def plot(self, figure: object = None, **kwargs: object) -> object:
        """Embed a matplotlib figure in this cell.

        Args:
            figure: A ``matplotlib.figure.Figure`` instance.

        Keyword Args:
            format: Output format (``"png"``, ``"pdf"``, ``"svg"``).
            dpi: Resolution for raster output (default ``150``).
            preserve_aspect: Whether to preserve aspect ratio.
            container_width_pct: Width as percentage of cell.
            container_height_pct: Height as percentage of cell.

        Returns:
            The created ``FigureElement``.
        """
        from reporting.elements.figure import FigureElement
        el: object = FigureElement(figure, **kwargs)
        self._cell.element = el
        return el

    def table(self, data: object = None, **kwargs: object) -> object:
        """Add a table to this cell.

        Accepts either a pandas ``DataFrame`` (rendered as a
        basic table) or a ``TableSpec`` (rendered with full
        TableSpec styling).

        Args:
            data: A pandas ``DataFrame`` or a ``TableSpec``.

        Keyword Args:
            header: Whether to show a header row.
            include_index: Whether to show the DataFrame index.
            zebra: Enable alternating row colours.
            numeric_format: Format string for numeric values.

        Returns:
            A ``TableElement`` or ``TableSpecElement``.
        """
        from reporting.tablespec.spec import TableSpec
        if isinstance(data, TableSpec):
            return self.table_spec(data, **kwargs)
        from reporting.elements.table import TableElement
        el: object = TableElement(data, **kwargs)
        self._cell.element = el
        return el

    def table_spec(self, spec: object = None, **kwargs: object) -> object:
        """Add a ``TableSpec`` to this cell (explicit method).

        Args:
            spec: A ``TableSpec`` instance.

        Returns:
            The created ``TableSpecElement``.
        """
        from reporting.elements.tablespec_element import TableSpecElement
        el: object = TableSpecElement(spec, **kwargs)
        self._cell.element = el
        return el

    def grid_layout(self, grid: Grid) -> object:
        """Add a nested sub-grid inside this cell.

        Wraps a ``Grid`` in a ``ContainerElement``.

        Args:
            grid: A ``Grid`` instance defining the sub-layout.

        Returns:
            The created ``ContainerElement``.
        """
        from reporting.elements.container import ContainerElement
        el: object = ContainerElement(grid=grid)
        self._cell.element = el
        return el


@dataclasses.dataclass
class Grid:
    """Rectangular grid that resolves row / column sizes and computes cell rectangles.

    Created automatically by ``Slide.grid_layout()``.
    Supports NumPy-style cell access via ``__getitem__``,
    automatic span merging, and flexible sizing (fixed,
    percentage, fill).

    Args:
        rows: Number of rows.
        cols: Number of columns.
        row_sizes: Per-row sizing.  Each element can be
            ``Px(v)``, ``Percent(v)``, ``Fill``, or a plain
            float (treated as ``Px(v)``).  When ``None``, all
            rows get ``Fill`` (equal height).
        col_sizes: Per-column sizing (same rules as
            ``row_sizes``).  When ``None``, all columns
            get ``Fill`` (equal width).
        gap: Spacing between rows and columns in pixels
            (default ``0.0``).
        padding: Outer padding around the grid
            (default ``Edges()`` = zero).

    Example::

        from reporting.layout.grid import Grid
        from reporting.layout.geometry import Size
        from reporting.layout.sizing import Px, Percent, Fill

        grid = Grid(rows=3, cols=2,
                    row_sizes=[Px(50), Fill, Percent(30)],
                    col_sizes=[Percent(60), Fill],
                    gap=8)
        total, rects = grid.layout(Size(800, 400))
        # rects[r][c] → Rect with resolved pixel positions
    """

    rows: int
    cols: int
    row_sizes: list[Sizing]
    col_sizes: list[Sizing]
    cells: list[list[GridCell]]
    gap: float = 0.0
    padding: Edges = dataclasses.field(default_factory=Edges)

    def __init__(
        self,
        rows: int,
        cols: int,
        row_sizes: Optional[list[Sizing]] = None,
        col_sizes: Optional[list[Sizing]] = None,
        gap: float = 0.0,
        padding: Optional[Edges] = None,
        typography: object = None,
    ):
        self.rows = rows
        self.cols = cols
        self.gap = gap
        self.padding = padding or Edges()
        self._typography = typography

        self.row_sizes = row_sizes or [LengthValue(1.0, SizingType.FILL)] * rows
        self.col_sizes = col_sizes or [LengthValue(1.0, SizingType.FILL)] * cols

        self.cells = [
            [GridCell(panel=Panel(row=r, col=c)) for c in range(cols)]
            for r in range(rows)
        ]

    @property
    def typography(self) -> object:
        """Typography used for ``style`` resolution in ``text()``."""
        return self._typography

    @typography.setter
    def typography(self, value: object) -> None:
        self._typography = value
        self._resolve_pending_styles()

    def _resolve_pending_styles(self) -> None:
        """Resolve ``style`` on any ``TextElement`` created before typography was set."""
        if self._typography is None:
            return
        from reporting.styles.typography import STYLE_ALIASES, FontSpec
        from reporting.elements.base import ElementType
        from reporting.elements.container import ContainerElement

        for row in self.cells:
            for cell in row:
                if cell.element is None:
                    continue
                el = cell.element
                if hasattr(el, 'element_type') and el.element_type == ElementType.TEXT:
                    props = getattr(el, 'properties', {}) or {}
                    style_name = props.get('style')
                    if style_name is not None:
                        name = STYLE_ALIASES.get(style_name, style_name)
                        spec = getattr(self._typography, name, None)
                        if isinstance(spec, FontSpec):
                            for block in el.blocks:
                                for run in block.runs:
                                    if not run.bold and spec.bold:
                                        run.bold = True
                                    if not run.italic and spec.italic:
                                        run.italic = True
                                    if run.size is None:
                                        run.size = spec.size
                                    if run.font_name is None:
                                        run.font_name = spec.family
                                    if run.color is None and spec.color is not None:
                                        run.color = spec.color
                elif isinstance(el, ContainerElement) and el.grid is not None:
                    el.grid.typography = self._typography

    def copy_structure(self) -> Grid:
        """Create a new ``Grid`` with the same dimensions, sizing,
        gap, and padding, but with fresh empty cells.

        Returns:
            A new ``Grid`` sharing the structural properties
            of this one.
        """
        return Grid(
            rows=self.rows,
            cols=self.cols,
            row_sizes=list(self.row_sizes),
            col_sizes=list(self.col_sizes),
            gap=self.gap,
            padding=self.padding,
            typography=self._typography,
        )

    def __getitem__(self, pos: tuple[int | slice, int | slice]) -> GridCellProxy:
        """Access a cell by row and column (NumPy-style indexing).

        Slices set ``rowspan`` / ``colspan`` on the
        cell's ``Panel``.

        Args:
            pos: ``(row, col)`` where each coordinate is
                an ``int`` or a ``slice``.

        Returns:
            A ``GridCellProxy`` wrapping the cell at
            ``(row, col)``, with ``rowspan`` and ``colspan``
            updated if slices were used.
        """
        row_key, col_key = pos
        rows_range = self._resolve_range(row_key, self.rows)
        cols_range = self._resolve_range(col_key, self.cols)
        r, c = rows_range.start, cols_range.start
        cell = self.cells[r][c]
        cell.panel.rowspan = rows_range.stop - rows_range.start
        cell.panel.colspan = cols_range.stop - cols_range.start
        return GridCellProxy(cell, typography=self._typography)

    @staticmethod
    def _resolve_range(key: int | slice, limit: int) -> range:
        if isinstance(key, int):
            if key < 0:
                key += limit
            return range(key, key + 1)
        start = key.start if key.start is not None else 0
        stop = key.stop if key.stop is not None else limit
        if start < 0:
            start += limit
        if stop < 0:
            stop += limit
        return range(start, stop)

    def layout(self, available: Size) -> tuple[Size, list[list[Rect]]]:
        """Compute final cell positions for a given available area.

        The algorithm:

        #. Subtracts padding and gaps from the available space.
        #. Resolves row heights and column widths from sizing
           specs (fixed → exact, percent → % of available,
           fill → proportional flex).
        #. Computes pixel rectangles for each cell.
        #. Merges rectangles for cells with ``rowspan > 1`` or
           ``colspan > 1`` (zeroes out covered cells).

        Args:
            available: The total ``Size`` available for the grid.

        Returns:
            A tuple ``(total_size, cell_rects)`` where
            ``cell_rects`` is a 2-D ``list[list[Rect]]``
            (same shape as the grid).  Merged cells have
            zero ``Rect(0, 0, 0, 0)`` at covered positions.
        """
        avail_w = available.width - self.padding.horizontal - max(0, (self.cols - 1) * self.gap)
        avail_h = available.height - self.padding.vertical - max(0, (self.rows - 1) * self.gap)
        col_widths = self._resolve_sizes(self.col_sizes, avail_w, self.cols)
        row_heights = self._resolve_sizes(self.row_sizes, avail_h, self.rows)

        total_w = self.padding.horizontal + (self.cols - 1) * self.gap + sum(col_widths)
        total_h = self.padding.vertical + (self.rows - 1) * self.gap + sum(row_heights)

        origin_x = self.padding.left
        origin_y = self.padding.top

        cell_rects: list[list[Rect]] = []
        y = origin_y
        for r in range(self.rows):
            row_rects: list[Rect] = []
            x = origin_x
            for c in range(self.cols):
                row_rects.append(Rect(x, y, col_widths[c], row_heights[r]))
                x += col_widths[c] + self.gap
            cell_rects.append(row_rects)
            y += row_heights[r] + self.gap

        merged = self._merge_spans(cell_rects)
        return Size(total_w, total_h), merged

    def _merge_spans(self, cell_rects: list[list[Rect]]) -> list[list[Rect]]:
        merged = [[r for r in row] for row in cell_rects]
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                if cell.panel.rowspan > 1 or cell.panel.colspan > 1:
                    rr = min(r + cell.panel.rowspan, self.rows)
                    rc = min(c + cell.panel.colspan, self.cols)
                    first = cell_rects[r][c]
                    last = cell_rects[rr - 1][rc - 1]
                    merged_w = last.x + last.width - first.x
                    merged_h = last.y + last.height - first.y
                    merged[r][c] = Rect(first.x, first.y, merged_w, merged_h)
                    for sr in range(r, rr):
                        for sc in range(c, rc):
                            if sr != r or sc != c:
                                merged[sr][sc] = Rect(0, 0, 0, 0)
        return merged

    @staticmethod
    def _resolve_sizes(sizes: list[Sizing], available: float, count: int) -> list[float]:
        resolved = [0.0] * count
        fill_total = 0.0
        used_space = 0.0

        for i, raw in enumerate(sizes):
            lv = normalize(raw)
            if lv.sizing_type is SizingType.FIXED:
                resolved[i] = lv.value
                used_space += lv.value
            elif lv.sizing_type is SizingType.PERCENT:
                resolved[i] = available * lv.value / 100.0
                used_space += resolved[i]
            elif lv.sizing_type in (SizingType.FILL, SizingType.AUTO):
                fill_total += lv.value if lv.value > 0 else 1.0

        remaining = available - used_space
        if fill_total > 0:
            for i, raw in enumerate(sizes):
                lv = normalize(raw)
                if lv.sizing_type in (SizingType.FILL, SizingType.AUTO):
                    wgt = lv.value if lv.value > 0 else 1.0
                    resolved[i] = remaining * wgt / fill_total

        return resolved
