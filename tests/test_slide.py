"""Tests for slide.py — the page abstraction."""

from __future__ import annotations

import pytest

from reporting.slide import Slide
from reporting.slide_type import SlideTypeConfig
from reporting.layout_config import LayoutConfig
from reporting.layout.sizing import Px, Fill
from reporting.layout.geometry import Edges, Rect
from reporting.styles.theme import Theme, CorporateTheme, DarkTheme, LightTheme
from reporting.styles.colors import Color, ColorPalette
from reporting.styles.typography import Typography, FontSpec
from reporting.title_config import TitleText, SubtitleText, TitlePanel
from reporting.footer_config import FooterPanel
from reporting.elements.text import TextElement
from reporting.elements.image import ImageElement
from reporting.elements.figure import FigureElement
from reporting.elements.table import TableElement
from reporting.elements.base import ElementType


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

    # ── New theme system tests ──────────────────────────────────────

    def test_auto_layout_from_slide_type(self):
        """SlideType with layout name auto-creates grid."""
        slide = Slide("Auto", slide_type="title")
        assert slide._grid is not None
        assert slide._grid.rows == 1
        assert slide._grid.cols == 1

    def test_slide_type_blank_no_layout(self):
        """blank slide type has no layout, so no auto-grid."""
        slide = Slide("Blank", slide_type="blank")
        assert slide._grid is None

    def test_slide_type_default_cells(self):
        """SlideType cells dict auto-populates grid cells."""
        st = SlideTypeConfig(
            name="test",
            layout="default",
            cells={(0, 0): "Cell A", (0, 1): "Cell B"},
        )
        theme = Theme(
            name="TestTheme",
            layouts={"default": LayoutConfig(name="default", rows=1, cols=2)},
            slide_types={"test": st},
        )
        slide = Slide("Cells", theme=theme, slide_type="test")
        assert slide._grid is not None
        assert slide._grid.rows == 1
        assert slide._grid.cols == 2
        assert slide._grid.cells[0][0].element is not None
        assert slide._grid.cells[0][1].element is not None
        el = slide._grid.cells[0][0].element
        assert isinstance(el, TextElement)
        assert el.blocks[0].runs[0].text == "Cell A"

    def test_theme_page_size_defaults(self):
        """Theme.page_size controls slide width/height when not explicit."""
        theme = Theme(
            name="Wide",
            page_size=(1280.0, 720.0),
        )
        slide = Slide("Wide", theme=theme)
        assert slide.width == 1280.0
        assert slide.height == 720.0

    def test_explicit_size_overrides_theme(self):
        """Explicit width/height must override theme.page_size."""
        theme = Theme(name="Small", page_size=(640.0, 480.0))
        slide = Slide("Big", theme=theme, width=1920.0, height=1080.0)
        assert slide.width == 1920.0
        assert slide.height == 1080.0

    def test_title_from_slide_type(self):
        """SlideType title_text appears as default title."""
        st = SlideTypeConfig(name="cover", title_text="Cover Title")
        theme = Theme(slide_types={"cover": st})
        slide = Slide(theme=theme, slide_type="cover")
        assert str(slide.title) == "Cover Title"

    def test_explicit_title_overrides_slide_type(self):
        """Explicit title kwarg must override slide type title_text."""
        st = SlideTypeConfig(name="cover", title_text="Default")
        theme = Theme(slide_types={"cover": st})
        slide = Slide("Explicit", theme=theme, slide_type="cover")
        assert str(slide.title) == "Explicit"

    def test_subtitle_from_slide_type(self):
        """SlideType subtitle_text appears as default subtitle."""
        st = SlideTypeConfig(name="cover", subtitle_text="Default Sub")
        theme = Theme(slide_types={"cover": st})
        slide = Slide("Title", theme=theme, slide_type="cover")
        assert slide.subtitle is not None
        assert str(slide.subtitle) == "Default Sub"

    def test_explicit_subtitle_overrides_slide_type(self):
        """Explicit subtitle must override slide type subtitle_text."""
        st = SlideTypeConfig(name="cover", subtitle_text="Default")
        theme = Theme(slide_types={"cover": st})
        slide = Slide("Title", subtitle="Explicit", theme=theme, slide_type="cover")
        assert str(slide.subtitle) == "Explicit"

    def test_base_slide_resolution(self):
        """base_slide provides theme, panels, dimensions, and grid."""
        base = Slide("Base")
        base.grid_layout(rows=2, cols=3, gap=5)
        child = Slide(base_slide=base)
        assert child.width == base.width
        assert child.height == base.height
        assert child.theme is base.theme
        assert child.title_panel.height == base.title_panel.height
        assert child._grid is not None
        assert child._grid.rows == 2
        assert child._grid.cols == 3
        assert child._grid.gap == 5

    def test_base_slide_content_not_copied(self):
        """base_slide copies grid structure but not cell content."""
        base = Slide("Base")
        base.grid_layout(rows=1, cols=1)
        base[0, 0].text("Base content")
        child = Slide("Child", base_slide=base)
        assert child._grid.cells[0][0].element is None

    def test_dark_theme_works(self):
        """DarkTheme creates slides with correct page_size."""
        slide = Slide("Dark", theme=DarkTheme())
        assert slide.theme.name == "Dark"
        assert slide.width == 960.0

    def test_light_theme_works(self):
        """LightTheme creates slides with correct page_size."""
        slide = Slide("Light", theme=LightTheme())
        assert slide.theme.name == "Light"

    def test_custom_theme_with_layouts(self):
        """Custom Theme with named layouts and slide types."""
        theme = Theme(
            name="Custom",
            layouts={
                "two_by_one": LayoutConfig(
                    name="two_by_one", rows=2, cols=1, gap=4,
                    row_sizes=[Px(100), Fill],
                ),
            },
            slide_types={
                "slim": SlideTypeConfig(
                    name="slim", layout="two_by_one",
                    title_text="Slim Slide",
                ),
            },
        )
        slide = Slide(theme=theme, slide_type="slim")
        assert slide._grid is not None
        assert slide._grid.rows == 2
        assert slide._grid.cols == 1
        assert slide._grid.gap == 4
        assert str(slide.title) == "Slim Slide"

    def test_layout_config_creation(self):
        """LayoutConfig basic creation."""
        lc = LayoutConfig(name="test", rows=3, cols=4, gap=8, padding=Edges.all(10))
        assert lc.name == "test"
        assert lc.rows == 3
        assert lc.cols == 4
        assert lc.gap == 8
        assert lc.padding is not None
        assert lc.padding.left == 10

    def test_slide_type_config_creation(self):
        """SlideTypeConfig basic creation with optional fields."""
        st = SlideTypeConfig(
            name="results",
            title_text="Results",
            subtitle_text="Data",
            layout="default",
            title_panel=TitlePanel(height=70),
            footer_panel=FooterPanel(enabled=False),
            cells={(0, 0): "Hello"},
        )
        assert st.name == "results"
        assert st.title_text == "Results"
        assert st.subtitle_text == "Data"
        assert st.layout == "default"
        assert st.title_panel is not None
        assert st.title_panel.height == 70
        assert st.footer_panel is not None
        assert st.footer_panel.enabled is False
        assert st.cells == {(0, 0): "Hello"}

    def test_theme_register_and_load(self):
        """Theme.register() and Theme.load_themes()."""
        @Theme.register("test_theme")
        class TestRegTheme(Theme):
            def __init__(self) -> None:
                super().__init__(name="TestRegistered")

        assert "test_theme" in Theme._registry
        assert Theme._registry["test_theme"] is TestRegTheme

    def test_theme_get_layout_default(self):
        """Theme.get_layout() returns LayoutConfig or default."""
        theme = Theme()
        lc = theme.get_layout("nonexistent")
        assert lc.name == "nonexistent"
        assert lc.rows == 1

    def test_theme_get_slide_type_default(self):
        """Theme.get_slide_type() returns SlideTypeConfig or default."""
        theme = Theme()
        st = theme.get_slide_type("nonexistent")
        assert st.name == "nonexistent"
        assert st.layout == "default"

    def test_empty_slide_defaults_to_corporate(self):
        """Slide() with no args uses CorporateTheme."""
        slide = Slide()
        assert slide.theme.name == "Corporate"
        assert slide.width == 960.0
        assert slide.height == 540.0

    def test_title_panel_enabled_by_default(self):
        """TitlePanel.enabled defaults to True."""
        tp = TitlePanel()
        assert tp.enabled is True
        slide = Slide("Test")
        assert slide.title_panel.enabled is True

    def test_title_panel_disabled_content_size_full(self):
        """When title_panel is disabled, content_size covers full height."""
        slide = Slide(
            "Test",
            title_panel=TitlePanel(enabled=False),
            footer_panel=FooterPanel(enabled=False),
        )
        slide.grid_layout(rows=1, cols=1)
        cs = slide.content_size
        assert cs.width == 960.0
        assert cs.height == 540.0

    def test_title_panel_enabled_content_size_subtracts_height(self):
        """When title_panel is enabled, content_size subtracts panel height."""
        slide = Slide(
            "Test",
            title_panel=TitlePanel(enabled=True, height=80),
            footer_panel=FooterPanel(enabled=False),
        )
        slide.grid_layout(rows=1, cols=1)
        cs = slide.content_size
        assert cs.width == 960.0
        assert cs.height == 460.0  # 540 - 80

    def test_title_panel_disabled_blank_slide_type(self):
        """blank slide type sets enabled=False on TitlePanel."""
        slide = Slide(
            slide_type="blank",
            footer_panel=FooterPanel(enabled=False),
        )
        assert slide.title_panel.enabled is False
        cs = slide.content_size
        assert cs.height == 540.0
