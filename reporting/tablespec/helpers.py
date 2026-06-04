"""Standalone builder helpers for constructing TableSpec tables.

Public helpers:

* ``cell(value, *, colspan=1, rowspan=1, style=None, **overrides)``
  — shorthand for ``TableCell(value=..., colspan=...)``
"""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

from reporting.tablespec.cell import TableCell
from reporting.tablespec.style import CellStyle


def cell(
    value: Any,
    *,
    colspan: int = 1,
    rowspan: int = 1,
    style: Optional[CellStyle] = None,
    **overrides: Any,
) -> TableCell:
    """Create a single TableCell with optional span and style overrides.

    Examples::

        cell("Header", colspan=4, style=header_style)
        cell(0.95, style=CellStyle(bold=True, text_color="#006100"))
        cell("Label", rowspan=2)
    """
    style_kwargs: dict[str, Any] = {}
    valid_fields = {
        "bold", "italic", "underline",
        "text_color", "background_color", "border_color", "border_width",
        "font_name", "font_size", "alignment",
        "align_h", "align_v", "padding",
    }
    for k in list(overrides.keys()):
        if k in valid_fields:
            style_kwargs[k] = overrides.pop(k)

    merged_style = style
    if style_kwargs:
        base = dataclasses.asdict(style) if style else {}
        base.update(style_kwargs)
        merged_style = CellStyle(**base)

    return TableCell(
        value=value,
        colspan=colspan,
        rowspan=rowspan,
        style=merged_style,
        **overrides,
    )
