"""Tests for layout/panel.py — pure layout, no renderer deps."""

from __future__ import annotations

from reporting.layout.panel import Panel, HAlign, VAlign
from reporting.layout.geometry import Edges, Size
from reporting.layout.constraints import Constraints


class TestPanel:
    def test_default_panel(self):
        p = Panel()
        assert p.row == 0
        assert p.col == 0
        assert p.rowspan == 1
        assert p.colspan == 1
        assert p.h_align == HAlign.STRETCH
        assert p.v_align == VAlign.STRETCH

    def test_custom_panel(self):
        p = Panel(
            row=2, col=3,
            rowspan=2, colspan=3,
            padding=Edges.all(5),
            h_align=HAlign.CENTER,
            v_align=VAlign.MIDDLE,
        )
        assert p.row == 2
        assert p.col == 3
        assert p.rowspan == 2
        assert p.colspan == 3
        assert p.padding == Edges.all(5)

    def test_content_area(self):
        p1 = Panel()
        assert p1.content_area == "dynamic"
        p2 = Panel(fixed_size=Size(100, 100))
        assert p2.content_area == "panel"
