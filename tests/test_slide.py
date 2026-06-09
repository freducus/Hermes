"""Tests for slide.py — the page abstraction."""

from __future__ import annotations

import pytest

from reporting.slide import Slide
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

    def test_title_panel_height(self):
        slide = Slide("Test", title_panel_height=80)
        assert slide.title_panel_height == 80
        assert slide.content_size == (960, 432)

    def test_content_size(self):
        slide = Slide("Test", width=800, height=600)
        assert slide.content_size.width == 800
        assert slide.content_size.height == 512

    def test_get_cell_rects_grid_relative(self):
        slide = Slide("Test", width=800, height=600, title_panel_height=60)
        slide.grid_layout(rows=1, cols=1)
        rects = slide.get_cell_rects()
        assert len(rects) == 1
        assert len(rects[0]) == 1
        r = rects[0][0]
        assert r.y == 0
        assert r.width == 800
        assert r.height == 512

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
