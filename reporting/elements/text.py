"""Text element — rich text content, backend-agnostic."""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Optional

from reporting.styles.colors import ColorValue, normalize_color
from reporting.elements.base import BaseElement, ElementType


class TextAlignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclasses.dataclass
class TextRun:
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[ColorValue] = None
    size: Optional[float] = None
    font_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.color is not None:
            self.color = normalize_color(self.color)


@dataclasses.dataclass
class TextBlock:
    runs: list[TextRun]
    alignment: TextAlignment = TextAlignment.LEFT
    spacing_before: float = 0.0
    spacing_after: float = 0.0


@dataclasses.dataclass
class TextElement(BaseElement):
    blocks: list[TextBlock] = dataclasses.field(default_factory=list)

    def __init__(self, text: str = "", **kwargs: object) -> None:
        super().__init__(element_type=ElementType.TEXT, properties=kwargs)
        bold = kwargs.pop("bold", False)
        italic = kwargs.pop("italic", False)
        color = kwargs.pop("color", None)
        size = kwargs.pop("size", None)
        font_name = kwargs.pop("font_name", None)
        alignment = kwargs.pop("alignment", TextAlignment.LEFT)
        if isinstance(alignment, str):
            alignment = TextAlignment(alignment)
        self.blocks = []
        if text:
            run = TextRun(text=text, bold=bold, italic=italic, color=color, size=size, font_name=font_name)
            self.blocks.append(TextBlock(runs=[run], alignment=alignment))

    def add_run(
        self,
        text: str,
        bold: bool = False,
        italic: bool = False,
        color: Optional[str] = None,
        size: Optional[float] = None,
        font_name: Optional[str] = None,
    ) -> TextRun:
        run = TextRun(text=text, bold=bold, italic=italic, color=color, size=size, font_name=font_name)
        if not self.blocks:
            self.blocks.append(TextBlock(runs=[]))
        self.blocks[-1].runs.append(run)
        return run

    def add_block(
        self,
        alignment: TextAlignment = TextAlignment.LEFT,
        spacing_before: float = 0.0,
        spacing_after: float = 0.0,
    ) -> TextBlock:
        if isinstance(alignment, str):
            alignment = TextAlignment(alignment)
        block = TextBlock(runs=[], alignment=alignment, spacing_before=spacing_before, spacing_after=spacing_after)
        self.blocks.append(block)
        return block
