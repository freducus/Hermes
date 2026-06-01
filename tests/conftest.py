"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_slide():
    from reporting.slide import Slide
    slide = Slide("Test Slide")
    slide.grid_layout(rows=3, cols=4)
    return slide
