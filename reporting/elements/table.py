"""Table element — wraps a pandas DataFrame, backend-agnostic."""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

from reporting.elements.base import BaseElement, ElementType


@dataclasses.dataclass
class ConditionalFormat:
    column: str = ""
    highlight_max: bool = False
    highlight_min: bool = False
    color_map: Optional[str] = None
    threshold: Optional[float] = None


@dataclasses.dataclass
class TableElement(BaseElement):
    data: Any = None
    include_index: bool = False
    header: bool = True
    zebra: bool = False
    numeric_format: Optional[str] = None
    column_widths: Optional[list[float]] = None
    conditional_formats: list[ConditionalFormat] = dataclasses.field(default_factory=list)

    def __init__(self, data: object = None, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.TABLE, properties=kwargs)
        self.data = data
        self.include_index = kwargs.pop("include_index", False)
        self.header = kwargs.pop("header", True)
        self.zebra = kwargs.pop("zebra", False)
        self.numeric_format = kwargs.pop("numeric_format", None)
        self.column_widths = kwargs.pop("column_widths", None)
        self.conditional_formats = []

    def highlight_max(self, column: str) -> TableElement:
        self.conditional_formats.append(ConditionalFormat(column=column, highlight_max=True))
        return self

    def highlight_min(self, column: str) -> TableElement:
        self.conditional_formats.append(ConditionalFormat(column=column, highlight_min=True))
        return self

    def heatmap(self, column: str, color_map: str = "YlOrRd") -> TableElement:
        self.conditional_formats.append(ConditionalFormat(column=column, color_map=color_map))
        return self
