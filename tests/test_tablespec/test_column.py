"""Tests for Column entity."""

from __future__ import annotations

from reporting.elements.text import TextAlignment
from reporting.tablespec.column import Column
from reporting.tablespec.style import ColumnStyle


class TestColumn:
    def test_name_required(self):
        c = Column("mach")
        assert c.name == "mach"

    def test_label_defaults_to_name(self):
        c = Column("pressure_ratio")
        assert c.label == "pressure_ratio"

    def test_explicit_label(self):
        c = Column("pr", label="Pressure Ratio")
        assert c.label == "Pressure Ratio"

    def test_format_setter_chaining(self):
        c = Column("x")
        result = c.set_format("{:.2f}")
        assert result is c
        assert c.format == "{:.2f}"

    def test_formatter_setter_chaining(self):
        c = Column("x")
        fn = lambda v: str(v)
        result = c.set_formatter(fn)
        assert result is c
        assert c.formatter is fn

    def test_visible_default(self):
        c = Column("x")
        assert c.visible is True

    def test_style_assignment(self):
        style = ColumnStyle(background_color="#EEE")
        c = Column("x", style=style)
        assert c.style is style
