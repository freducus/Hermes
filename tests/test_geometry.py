"""Tests for layout/geometry.py — pure math, no renderer deps."""

from __future__ import annotations

from reporting.layout.geometry import Point, Size, Rect, Edges


class TestPoint:
    def test_construction(self):
        p = Point(10, 20)
        assert p.x == 10
        assert p.y == 20

    def test_unpacking(self):
        x, y = Point(3, 4)
        assert x == 3
        assert y == 4


class TestSize:
    def test_construction(self):
        s = Size(100, 200)
        assert s.width == 100
        assert s.height == 200


class TestRect:
    def test_properties(self):
        r = Rect(10, 20, 100, 200)
        assert r.left == 10
        assert r.right == 110
        assert r.top == 20
        assert r.bottom == 220
        assert r.top_left == Point(10, 20)
        assert r.bottom_right == Point(110, 220)
        assert r.size == Size(100, 200)

    def test_inset(self):
        r = Rect(10, 20, 100, 200)
        inset = r.inset(5, 10, 5, 10)
        assert inset == Rect(15, 30, 90, 180)

    def test_contains_point(self):
        r = Rect(0, 0, 100, 100)
        assert r.contains_point(Point(50, 50))
        assert not r.contains_point(Point(150, 150))
        assert r.contains_point(Point(0, 0))
        assert r.contains_point(Point(100, 100))


class TestEdges:
    def test_all(self):
        e = Edges.all(10)
        assert e == Edges(10, 10, 10, 10)

    def test_symmetric(self):
        e = Edges.symmetric(horizontal=5, vertical=10)
        assert e == Edges(5, 10, 5, 10)

    def test_horizontal_vertical(self):
        e = Edges(10, 20, 5, 15)
        assert e.horizontal == 15
        assert e.vertical == 35
