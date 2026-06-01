"""Tests for layout/sizing.py — pure math, no renderer deps."""

from __future__ import annotations

from reporting.layout.sizing import LengthValue, SizingType, Auto, Fill, Px, Percent, normalize


class TestLengthValue:
    def test_fixed_resolve(self):
        lv = Px(100)
        assert lv.resolve(1000, 0, 0) == 100

    def test_percent_resolve(self):
        lv = Percent(50)
        assert lv.resolve(1000, 0, 0) == 500

    def test_fill_resolve(self):
        lv = Fill
        result = lv.resolve(1000, 4, 1)
        assert result == 250

    def test_fill_zero_weight(self):
        lv = Fill
        assert lv.resolve(1000, 0, 1) == 0

    def test_auto_zero(self):
        lv = Auto
        assert lv.resolve(1000, 0, 0) == 0


class TestNormalize:
    def test_float(self):
        lv = normalize(50.0)
        assert lv.sizing_type == SizingType.FIXED
        assert lv.value == 50.0

    def test_int(self):
        lv = normalize(30)
        assert lv.sizing_type == SizingType.FIXED
        assert lv.value == 30.0

    def test_length_value(self):
        lv = normalize(Px(20))
        assert lv.sizing_type == SizingType.FIXED
        assert lv.value == 20.0
