"""Tests for Row entity."""

from __future__ import annotations

from reporting.tablespec.cell import Cell
from reporting.tablespec.row import Row
from reporting.tablespec.style import RowStyle


class TestRow:
    def test_defaults(self):
        r = Row()
        assert r.cells == []
        assert r.group is None
        assert r.metadata == {}

    def test_with_cells(self):
        cells = [Cell(value=1), Cell(value=2)]
        r = Row(cells=cells)
        assert len(r.cells) == 2
        assert r.cells[0].value == 1

    def test_group(self):
        r = Row(group="Compressor")
        assert r.group == "Compressor"

    def test_style(self):
        style = RowStyle(background_color="#EEE")
        r = Row(style=style)
        assert r.style is style

    def test_metadata(self):
        r = Row(metadata={"source": "simulation"})
        assert r.metadata["source"] == "simulation"
