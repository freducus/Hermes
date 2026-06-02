"""Tests for TableSpec style classes."""

from __future__ import annotations

from reporting.elements.text import TextAlignment
from reporting.layout.geometry import Edges
from reporting.tablespec.style import CellStyle, ColumnStyle, RowStyle, TableStyle


class TestCellStyle:
    def test_defaults(self):
        s = CellStyle()
        assert s.background_color is None
        assert s.text_color is None
        assert s.alignment is None

    def test_custom_values(self):
        s = CellStyle(
            background_color="#FF0000",
            text_color="#FFFFFF",
            font_size=12.0,
            alignment=TextAlignment.CENTER,
        )
        assert s.background_color == "#FF0000"
        assert s.text_color == "#FFFFFF"
        assert s.font_size == 12.0
        assert s.alignment == TextAlignment.CENTER

    def test_immutable(self):
        s = CellStyle(background_color="#000")
        try:
            s.background_color = "#FFF"
            assert False, "should be frozen"
        except AttributeError:
            pass


class TestColumnStyle:
    def test_defaults(self):
        s = ColumnStyle()
        assert s.background_color is None


class TestRowStyle:
    def test_defaults(self):
        s = RowStyle()
        assert s.background_color is None


class TestTableStyle:
    def test_defaults(self):
        s = TableStyle()
        assert s.zebra is False
        assert s.font_name == "Helvetica"
        assert s.font_size == 10.0
        assert isinstance(s.padding, Edges)

    def test_custom(self):
        s = TableStyle(zebra=True, header_background="#000000")
        assert s.zebra is True
        assert s.header_background == "#000000"

    def test_padding_default_4(self):
        s = TableStyle()
        assert s.padding.left == 4.0
        assert s.padding.right == 4.0
