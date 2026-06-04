"""Grid layout engine — pure math, no renderer dependencies."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.layout.geometry import Point, Size, Rect, Edges
from reporting.layout.sizing import Sizing, LengthValue, SizingType, normalize
from reporting.layout.panel import Panel


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
    ):
        self.rows = rows
        self.cols = cols
        self.gap = gap
        self.padding = padding or Edges()

        self.row_sizes = row_sizes or [LengthValue(1.0, SizingType.FILL)] * rows
        self.col_sizes = col_sizes or [LengthValue(1.0, SizingType.FILL)] * cols

        self.cells = [
            [GridCell(panel=Panel(row=r, col=c)) for c in range(cols)]
            for r in range(rows)
        ]

    def __getitem__(self, pos: tuple[int | slice, int | slice]) -> GridCell:
        """Access a cell by row and column (NumPy-style indexing).

        Slices set ``rowspan`` / ``colspan`` on the
        cell's ``Panel``.

        Args:
            pos: ``(row, col)`` where each coordinate is
                an ``int`` or a ``slice``.

        Returns:
            The ``GridCell`` at ``(row, col)``, with
            ``rowspan`` and ``colspan`` updated if slices
            were used.
        """
        row_key, col_key = pos
        rows_range = self._resolve_range(row_key, self.rows)
        cols_range = self._resolve_range(col_key, self.cols)
        r, c = rows_range.start, cols_range.start
        cell = self.cells[r][c]
        cell.panel.rowspan = rows_range.stop - rows_range.start
        cell.panel.colspan = cols_range.stop - cols_range.start
        return cell

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
