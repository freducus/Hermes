"""Helper utilities for matplotlib figure handling."""

from __future__ import annotations

import io
import tempfile
from typing import Optional


def figure_to_bytes(fig: object, dpi: int = 150, fmt: str = "png") -> bytes:
    """Render a matplotlib figure to bytes.

    Args:
        fig: A ``matplotlib.figure.Figure``.
        dpi: Output resolution (default ``150``).
        fmt: Output format — ``"png"``, ``"pdf"``, ``"svg"``
            (default ``"png"``).

    Returns:
        The rendered image as ``bytes``.
    """
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, format=fmt, bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def figure_to_tempfile(fig: object, dpi: int = 150, suffix: str = ".png") -> str:
    """Render a matplotlib figure to a temporary file.

    The caller is responsible for deleting the file.

    Args:
        fig: A ``matplotlib.figure.Figure``.
        dpi: Output resolution (default ``150``).
        suffix: File suffix (default ``".png"``).

    Returns:
        Path to the temporary file.
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        fig.savefig(tmp, dpi=dpi, bbox_inches="tight")
        return tmp.name


def figure_to_pdf_bytes(fig: object) -> bytes:
    """Render a matplotlib figure to PDF bytes.

    Args:
        fig: A ``matplotlib.figure.Figure``.

    Returns:
        The PDF as ``bytes``.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf", bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def figure_to_svg_bytes(fig: object) -> bytes:
    """Render a matplotlib figure to SVG bytes.

    Args:
        fig: A ``matplotlib.figure.Figure``.

    Returns:
        The SVG as ``bytes``.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    buf.seek(0)
    return buf.read()
