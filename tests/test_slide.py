"""Tests for slide.py — the page abstraction."""

from __future__ import annotations

import pytest

from reporting.slide import Slide
from reporting.title_config import TitleText, SubtitleText, TitlePanel
from reporting.elements.text import TextElement
from reporting.elements.image import ImageElement
from reporting.elements.figure import FigureElement
from reporting.elements.table import TableElement
from reporting.elements.base import ElementType
from reporting.layout.geometry import Rect


class TestSlide:
    def test_create_slide(self):
        slide = Slide(title="Test", subtitle="Sub", width=800, height=600)
        assert slide.title == "Test"
        assert slide.subtitle == "Sub"
        assert slide.width == 800
        assert slide.height == 600
        assert slide.size.width == 800
        assert slide.size.height == 600

    def test_title_is_titletext(self):
        slide = Slide("Test", subtitle="Sub")
        assert isinstance(slide.title, TitleText)
        assert isinstance(slide.subtitle, SubtitleText)

    def test_title_text_str_duck(self):
        slide = Slide("Hello")
        assert isinstance(slide.title, TitleText)
        assert str(slide.title) == "Hello"
        assert f"{slide.title}" == "Hello"
        assert slide.title.text == "Hello"

    def test_title_properties(self):
        slide = Slide("Test")
        assert hasattr(slide.title, "font_name")
        assert hasattr(slide.title, "font_size")
        assert hasattr(slide.title, "bold")
        assert hasattr(slide.title, "color")
        assert hasattr(slide.title, "alignment")

    def test_mutate_title_text(self):
        slide = Slide("Test")
        slide.title.text = "Updated"
        assert slide.title.text == "Updated"
        assert str(slide.title) == "Updated"
        assert f"{slide.title}" == "Updated"

    def test_mutate_subtitle_text(self):
        slide = Slide("Test", subtitle="Sub")
        slide.subtitle.text = "Changed"
        assert slide.subtitle.text == "Changed"
        assert str(slide.subtitle) == "Changed"

    def test_mutate_title_property(self):
        slide = Slide("Test")
        slide.title.font_size = 32
        assert slide.title.font_size == 32
        slide.title.bold = False
        assert slide.title.bold is False

    def test_mutate_subtitle_property(self):
        slide = Slide("Test", subtitle="Sub")
        slide.subtitle.color = "#FF0000"
        assert slide.subtitle.color == "#FF0000"
        slide.subtitle.font_size = 14
        assert slide.subtitle.font_size == 14

    def test_titletext_directly(self):
        title = TitleText("Custom", font_size=28, bold=False, font_name="Times-Roman")
        slide = Slide(title, subtitle="Sub")
        assert slide.title == "Custom"
        assert slide.title.font_size == 28
        assert slide.title.bold is False
        assert slide.title.font_name == "Times-Roman"

    def test_subtitletext_directly(self):
        sub = SubtitleText("Notes", font_size=12, italic=True, color="#00AA00")
        slide = Slide("Title", subtitle=sub)
        assert slide.subtitle == "Notes"
        assert slide.subtitle.font_size == 12
        assert slide.subtitle.italic is True
        assert slide.subtitle.color == "#00AA00"

    def test_title_panel_height(self):
        slide = Slide("Test", title_panel=TitlePanel(height=80))
        assert slide.title_panel.height == 80
        assert slide.content_size == (960, 428)

    def test_content_size(self):
        slide = Slide("Test", width=800, height=600)
        assert slide.content_size.width == 800
        assert slide.content_size.height == 508

    def test_get_cell_rects_grid_relative(self):
        slide = Slide("Test", width=800, height=600, title_panel=TitlePanel(height=60))
        slide.grid_layout(rows=1, cols=1)
        rects = slide.get_cell_rects()
        assert len(rects) == 1
        assert len(rects[0]) == 1
        r = rects[0][0]
        assert r.y == 0
        assert r.width == 800
        assert r.height == 508

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
