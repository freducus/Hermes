"""Typography system — defines font configurations for themes."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.styles.colors import ColorValue, normalize_color


@dataclasses.dataclass(frozen=True)
class FontSpec:
    family: str = "Helvetica"
    size: float = 12.0
    bold: bool = False
    italic: bool = False
    color: Optional[ColorValue] = None
    underline: bool = False

    def __post_init__(self) -> None:
        if self.color is not None:
            object.__setattr__(self, 'color', normalize_color(self.color))


@dataclasses.dataclass(frozen=True)
class Typography:
    heading_1: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=28.0, bold=True)
    )
    heading_2: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=22.0, bold=True)
    )
    heading_3: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=18.0, bold=True)
    )
    body: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=12.0)
    )
    caption: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Helvetica", size=10.0)
    )
    code: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Courier", size=10.0)
    )
    mono: FontSpec = dataclasses.field(
        default_factory=lambda: FontSpec(family="Courier", size=11.0)
    )
