"""Tests for layout/grid.py — pure layout engine."""

from __future__ import annotations

from reporting.layout.grid import Grid
from reporting.layout.geometry import Rect, Size
from reporting.layout.sizing import Px, Fill, Percent


class TestGridLayout:
    def test_simple_grid(self):
        g = Grid(rows=2, cols=3, row_sizes=[Px(50), Px(50)], col_sizes=[Px(100), Px(100), Px(100)])
        total_size, cell_rects = g.layout(Size(400, 200))
        assert total_size.width == 300
        assert total_size.height == 100

    def test_fill_sizes(self):
        g = Grid(rows=2, cols=2, gap=10)
        total_size, cell_rects = g.layout(Size(400, 300))
        assert total_size.width == 400
        assert total_size.height == 300
        assert cell_rects[0][0].width == 195
        assert cell_rects[0][0].height == 145

    def test_mixed_sizes(self):
        g = Grid(
            rows=2, cols=2,
            row_sizes=[Px(100), Fill],
            col_sizes=[Percent(50), Percent(50)],
            gap=0,
        )
        avail = Size(400, 300)
        total_size, cell_rects = g.layout(avail)
        assert total_size.width == 400
        assert total_size.height == 100 + (300 - 100)

    def test_padding(self):
        from reporting.layout.geometry import Edges
        g = Grid(rows=1, cols=1, row_sizes=[Fill], col_sizes=[Fill], padding=Edges.all(20))
        total_size, cell_rects = g.layout(Size(200, 100))
        assert total_size.width == 200
        assert total_size.height == 100
        assert cell_rects[0][0].width == 200 - 40

    def test_grid_getitem_single(self):
        g = Grid(rows=3, cols=4)
        cell = g[0, 1]
        assert cell.panel.row == 0
        assert cell.panel.col == 1
        assert cell.panel.rowspan == 1
        assert cell.panel.colspan == 1

    def test_grid_getitem_row_slice(self):
        g = Grid(rows=3, cols=4)
        cell = g[0, :]
        assert cell.panel.rowspan == 1
        assert cell.panel.colspan == 4

    def test_grid_getitem_col_slice(self):
        g = Grid(rows=3, cols=4)
        cell = g[:, 0]
        assert cell.panel.rowspan == 3
        assert cell.panel.colspan == 1

    def test_grid_getitem_subgrid(self):
        g = Grid(rows=4, cols=5)
        cell = g[1:, 2:]
        assert cell.panel.rowspan == 3
        assert cell.panel.colspan == 3

    def test_negative_index(self):
        g = Grid(rows=3, cols=4)
        cell = g[-1, -1]
        assert cell.panel.row == 2
        assert cell.panel.col == 3
