"""Tests for Cell entity."""

from __future__ import annotations

from reporting.elements.text import TextAlignment
from reporting.tablespec.cell import Cell
from reporting.tablespec.style import CellStyle


class TestCell:
    def test_defaults(self):
        c = Cell()
        assert c.value is None
        assert c.text is None
        assert c.rowspan == 1
        assert c.colspan == 1

    def test_value_and_text(self):
        c = Cell(value=42, text="forty-two")
        assert c.value == 42
        assert c.text == "forty-two"

    def test_spans(self):
        c = Cell(rowspan=3, colspan=2)
        assert c.rowspan == 3
        assert c.colspan == 2

    def test_alignment(self):
        c = Cell(alignment=TextAlignment.CENTER)
        assert c.alignment == TextAlignment.CENTER

    def test_background_color(self):
        c = Cell(background_color="#F00")
        assert c.background_color == "#F00"

    def test_style(self):
        style = CellStyle(font_size=14.0)
        c = Cell(style=style)
        assert c.style is style

    def test_repr_with_text(self):
        c = Cell(text="hello")
        assert "hello" in repr(c)

    def test_repr_without_text(self):
        c = Cell(value=99)
        assert "99" in repr(c)
