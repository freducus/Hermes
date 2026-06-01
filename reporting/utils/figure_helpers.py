"""Helper utilities for matplotlib figure handling."""

from __future__ import annotations

import io
import tempfile
from typing import Optional


def figure_to_bytes(fig: object, dpi: int = 150, fmt: str = "png") -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, format=fmt, bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def figure_to_tempfile(fig: object, dpi: int = 150, suffix: str = ".png") -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        fig.savefig(tmp, dpi=dpi, bbox_inches="tight")
        return tmp.name
