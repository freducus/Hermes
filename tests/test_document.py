"""Tests for document.py — the report container."""

from __future__ import annotations

from reporting.document import Document
from reporting.slide import Slide


class TestDocument:
    def test_create_document(self):
        doc = Document(title="Test Report", author="Engineer")
        assert doc.title == "Test Report"
        assert doc.author == "Engineer"
        assert len(doc.slides) == 0

    def test_add_slide(self):
        doc = Document(title="Test")
        slide = Slide()
        slide.title = "Page 1"
        returned = doc.add_slide(slide)
        assert returned is slide
        assert len(doc.slides) == 1

    def test_new_slide(self):
        doc = Document(title="Test")
        slide = doc.new_slide()
        slide.title = "Page 1"
        slide.subtitle = "Sub"
        assert isinstance(slide, Slide)
        assert slide.title == "Page 1"
        assert slide.subtitle == "Sub"
        assert len(doc.slides) == 1

    def test_render_calls_renderer(self):
        doc = Document(title="Test")
        doc.new_slide()

        class FakeRenderer:
            def render_document(self, doc, path):
                self.called_with = (doc, path)

        r = FakeRenderer()
        doc.render(r, "out.pdf")  # type: ignore
        assert r.called_with == (doc, "out.pdf")
