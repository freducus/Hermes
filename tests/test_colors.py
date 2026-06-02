"""Tests for styles/colors.py — Color parsing and normalization."""

from __future__ import annotations

import pytest

from reporting.styles.colors import Color, ColorValue, NAMED_COLORS, normalize_color


class TestColorParse:
    def test_hex_with_hash(self):
        c = Color.parse("#FF0000")
        assert c.r == 255 and c.g == 0 and c.b == 0

    def test_hex_without_hash(self):
        c = Color.parse("FF0000")
        assert c.r == 255 and c.g == 0 and c.b == 0

    def test_short_hex(self):
        c = Color.parse("#F00")
        assert c.r == 255 and c.g == 0 and c.b == 0

    def test_named_color(self):
        c = Color.parse("red")
        assert c.r == 255 and c.g == 0 and c.b == 0

    def test_named_color_case_insensitive(self):
        c = Color.parse("RED")
        assert c.r == 255 and c.g == 0 and c.b == 0

    def test_named_color_with_spaces(self):
        c = Color.parse("light blue")
        assert c.css.upper() == "#ADD8E6"

    def test_named_color_with_hyphen(self):
        c = Color.parse("light-blue")
        assert c.css.upper() == "#ADD8E6"

    def test_named_green(self):
        c = Color.parse("green")
        assert c.r == 0 and c.g == 128 and c.b == 0

    def test_named_dark_green(self):
        c = Color.parse("dark green")
        assert c.css.upper() == "#006400"

    def test_rgb_string(self):
        c = Color.parse("rgb(255, 0, 0)")
        assert c.r == 255 and c.g == 0 and c.b == 0

    def test_rgb_string_with_spaces(self):
        c = Color.parse("rgb( 255 , 128 , 0 )")
        assert c.r == 255 and c.g == 128 and c.b == 0

    def test_tuple_rgb(self):
        c = Color.parse((255, 0, 0))
        assert c.r == 255 and c.g == 0 and c.b == 0
        assert c.css == "#ff0000"

    def test_color_instance(self):
        c1 = Color.from_hex("#FF0000")
        c2 = Color.parse(c1)
        assert c2 is c1

    def test_color_instance_with_alpha(self):
        c1 = Color.from_hex("#FF0000")
        c2 = Color.parse(c1, alpha=0.5)
        assert c2 is not c1
        assert c2.alpha == 0.5

    def test_alpha_preserved(self):
        c = Color.parse("red", alpha=0.5)
        assert c.alpha == 0.5
        assert c.r == 255

    def test_named_gray(self):
        assert Color.parse("gray").css.upper() == "#808080"

    def test_named_navy(self):
        assert Color.parse("navy").css.upper() == "#000080"

    def test_unknown_color_raises(self):
        with pytest.raises(ValueError, match="Unknown color"):
            Color.parse("notacolor")

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError):
            Color.parse(123)


class TestColorProperties:
    def test_float_rgb(self):
        c = Color.from_rgb(255, 128, 0)
        r, g, b = c.float_rgb
        assert r == 1.0
        assert g == 0.5019607843137255
        assert b == 0.0

    def test_css_property(self):
        c = Color.parse("red")
        assert c.css == "#FF0000"

    def test_css_without_hash(self):
        c = Color.parse("ff0000")
        assert c.css == "#ff0000"

    def test_rgba_property(self):
        c = Color.parse("red", alpha=0.5)
        assert c.rgba == "rgba(255,0,0,0.5)"

    def test_reportlab_color(self):
        c = Color.parse("red")
        rl = c.reportlab_color
        assert abs(rl.red - 1.0) < 0.001
        assert abs(rl.green - 0.0) < 0.001
        assert abs(rl.blue - 0.0) < 0.001

    def test_with_alpha(self):
        c = Color.parse("red")
        c2 = c.with_alpha(0.3)
        assert c2.alpha == 0.3
        assert c2.css == "#FF0000"


class TestNormalizeColor:
    def test_hex_string(self):
        assert normalize_color("#FF0000") == "#FF0000"

    def test_named_color(self):
        assert normalize_color("red") == "#FF0000"

    def test_tuple(self):
        assert normalize_color((255, 0, 0)) == "#ff0000"

    def test_color_instance(self):
        c = Color.parse("blue")
        assert normalize_color(c) == "#0000FF"

    def test_none_not_allowed(self):
        with pytest.raises(TypeError):
            normalize_color(None)  # type: ignore


class TestNamedColors:
    def test_all_entries_parseable(self):
        for name, hex_str in NAMED_COLORS.items():
            c = Color.parse(name)
            assert c.css.lower() == hex_str.lower(), f"{name} -> {c.css} != {hex_str}"

    def test_common_colors(self):
        assert Color.parse("white") == Color.from_hex("#FFFFFF")
        assert Color.parse("black") == Color.from_hex("#000000")
        assert Color.parse("blue") == Color.from_hex("#0000FF")
