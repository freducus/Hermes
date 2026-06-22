"""Tests for slide.py — the page abstraction."""

from __future__ import annotations

import pytest

from reporting.slide import Slide
from reporting.layout.geometry import Rect
from reporting.styles.theme import Theme, CorporateTheme, DarkTheme, LightTheme
from reporting.title_config import TitleText, SubtitleText, TitlePanel
from reporting.elements.text import TextElement
from reporting.elements.image import ImageElement
from reporting.elements.figure import FigureElement
from reporting.elements.table import TableElement
from reporting.elements.base import ElementType


class TestSlide:
    def test_create_slide(self):
        slide = Slide()
        slide.title = "Test"
        slide.subtitle = "Sub"
        slide.width = 800
        slide.height = 600
        assert slide.title == "Test"
        assert slide.subtitle == "Sub"
        assert slide.width == 800
        assert slide.height == 600
        assert slide.size.width == 800
        assert slide.size.height == 600

    def test_title_is_titletext(self):
        slide = Slide()
        slide.title = "Test"
        slide.subtitle = "Sub"
        assert isinstance(slide.title, TitleText)
        assert isinstance(slide.subtitle, SubtitleText)

    def test_title_text_str_duck(self):
        slide = Slide()
        slide.title = "Hello"
        assert isinstance(slide.title, TitleText)
        assert str(slide.title) == "Hello"
        assert f"{slide.title}" == "Hello"
        assert slide.title.text == "Hello"

    def test_title_properties(self):
        slide = Slide()
        slide.title = "Test"
        assert hasattr(slide.title, "font_name")
        assert hasattr(slide.title, "font_size")
        assert hasattr(slide.title, "bold")
        assert hasattr(slide.title, "color")
        assert hasattr(slide.title, "alignment")

    def test_mutate_title_text(self):
        slide = Slide()
        slide.title = "Test"
        slide.title.text = "Updated"
        assert slide.title.text == "Updated"
        assert str(slide.title) == "Updated"
        assert f"{slide.title}" == "Updated"

    def test_mutate_subtitle_text(self):
        slide = Slide()
        slide.title = "Test"
        slide.subtitle = "Sub"
        slide.subtitle.text = "Changed"
        assert slide.subtitle.text == "Changed"
        assert str(slide.subtitle) == "Changed"

    def test_mutate_title_property(self):
        slide = Slide()
        slide.title = "Test"
        slide.title.font_size = 32
        assert slide.title.font_size == 32
        slide.title.bold = False
        assert slide.title.bold is False

    def test_mutate_subtitle_property(self):
        slide = Slide()
        slide.title = "Test"
        slide.subtitle = "Sub"
        slide.subtitle.color = "#FF0000"
        assert slide.subtitle.color == "#FF0000"
        slide.subtitle.font_size = 14
        assert slide.subtitle.font_size == 14

    def test_titletext_directly(self):
        title = TitleText("Custom", font_size=28, bold=False, font_name="Times-Roman")
        slide = Slide()
        slide.title = title
        slide.subtitle = "Sub"
        assert slide.title == "Custom"
        assert slide.title.font_size == 28
        assert slide.title.bold is False
        assert slide.title.font_name == "Times-Roman"

    def test_subtitletext_directly(self):
        sub = SubtitleText("Notes", font_size=12, italic=True, color="#00AA00")
        slide = Slide()
        slide.title = "Title"
        slide.subtitle = sub
        assert slide.subtitle == "Notes"
        assert slide.subtitle.font_size == 12
        assert slide.subtitle.italic is True
        assert slide.subtitle.color == "#00AA00"

    def test_content_size(self):
        slide = Slide()
        slide.width = 800
        slide.height = 600
        assert slide.content_size.width == 800
        assert slide.content_size.height == 600

    def test_get_cell_rects(self):
        slide = Slide()
        slide.width = 800
        slide.height = 600
        slide.grid_layout(rows=1, cols=1)
        rects = slide.get_cell_rects()
        assert len(rects) == 1
        assert len(rects[0]) == 1
        r = rects[0][0]
        assert r.y == 0
        assert r.width == 800
        assert r.height == 600

    def test_text_element(self, sample_slide):
        el = sample_slide[0, :].text("Hello")
        assert isinstance(el, TextElement)
        assert el.element_type == ElementType.TEXT

    def test_image_element(self, sample_slide):
        el = sample_slide[1, 0].image("test.png")
        assert isinstance(el, ImageElement)
        assert el.element_type == ElementType.IMAGE

    def test_plot_element(self, sample_slide):
        el = sample_slide[1, 1].plot(None)
        assert isinstance(el, FigureElement)
        assert el.element_type == ElementType.FIGURE

    def test_table_element(self, sample_slide):
        el = sample_slide[2, :].table(None, zebra=True)
        assert isinstance(el, TableElement)
        assert el.element_type == ElementType.TABLE
        assert el.zebra is True

    def test_cell_elements_stored(self, sample_slide):
        sample_slide[0, 0].text("A")
        sample_slide[1, 1].text("B")
        assert sample_slide._elements[(0, 0)] is not None
        assert sample_slide._elements[(1, 1)] is not None

    # ── Base slide inheritance ──────────────────────────────────────

    def test_base_slide_resolution(self):
        """base provides theme, dimensions, and grid."""
        base = Slide()
        base.title = "Base"
        base.grid_layout(rows=2, cols=3, gap=5)
        child = Slide(base=base)
        assert child.width == base.width
        assert child.height == base.height
        assert child.theme is base.theme
        assert child._grid is not None
        assert child._grid.rows == 2
        assert child._grid.cols == 3
        assert child._grid.gap == 5

    def test_base_slide_content_not_copied(self):
        """base copies grid structure but not cell content."""
        base = Slide()
        base.title = "Base"
        base.grid_layout(rows=1, cols=1)
        base[0, 0].text("Base content")
        child = Slide(base=base)
        assert child._grid.cells[0][0].element is None

    # ── Theme tests ─────────────────────────────────────────────────

    def test_dark_theme_works(self):
        """DarkTheme creates slides with correct defaults."""
        slide = Slide(theme=DarkTheme())
        slide.title = "Dark"
        assert slide.theme.name == "Dark"
        assert slide.width == 960.0

    def test_light_theme_works(self):
        """LightTheme creates slides with correct defaults."""
        slide = Slide(theme=LightTheme())
        slide.title = "Light"
        assert slide.theme.name == "Light"

    def test_empty_slide_defaults_to_corporate(self):
        """Slide() with no args uses CorporateTheme."""
        slide = Slide()
        assert slide.theme.name == "Corporate"
        assert slide.width == 960.0
        assert slide.height == 540.0

    def test_title_panel_default_disabled(self):
        """TitlePanel.enabled defaults to False."""
        tp = TitlePanel()
        assert tp.enabled is False
        slide = Slide()
        slide.title = "Test"
        assert slide.title_panel.enabled is False
