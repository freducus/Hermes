"""Table element — wraps a pandas DataFrame, backend-agnostic."""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

from reporting.elements.base import BaseElement, ElementType


@dataclasses.dataclass
class ConditionalFormat:
    """A single conditional formatting rule for a table column.

    Args:
        column: Column name to apply the rule to.
        highlight_max: Highlight the maximum value
            (default ``False``).
        highlight_min: Highlight the minimum value
            (default ``False``).
        color_map: Matplotlib colour map name for heatmap
            styling (e.g. ``"YlOrRd"``) (default ``None``).
        threshold: Numeric threshold for the rule
            (default ``None``).
    """
    column: str = ""
    highlight_max: bool = False
    highlight_min: bool = False
    color_map: Optional[str] = None
    threshold: Optional[float] = None


@dataclasses.dataclass
class TableElement(BaseElement):
    """A table created from a pandas ``DataFrame``.

    Args:
        data: A pandas ``DataFrame``.
        **kwargs: Property overrides:

            - ``include_index``: ``bool`` show the DataFrame
              index column (default ``False``)
            - ``header``: ``bool`` show a header row
              (default ``True``)
            - ``zebra``: ``bool`` alternate row background
              colours (default ``False``)
            - ``numeric_format``: ``Optional[str]`` format
              string for numeric values, e.g. ``"{:.2f}"``
              (default ``None``)
            - ``column_widths``: ``Optional[list[float]]``
              per-column widths in points
              (default ``None``)

    Example::

        import pandas as pd
        from reporting.elements.table import TableElement

        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        el = TableElement(df, zebra=True, numeric_format="{:.2f}")
        el.highlight_max("A")
    """
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
        """Highlight the maximum value in a column.

        Args:
            column: Column name.

        Returns:
            ``self`` for chaining.
        """
        self.conditional_formats.append(ConditionalFormat(column=column, highlight_max=True))
        return self

    def highlight_min(self, column: str) -> TableElement:
        """Highlight the minimum value in a column.

        Args:
            column: Column name.

        Returns:
            ``self`` for chaining.
        """
        self.conditional_formats.append(ConditionalFormat(column=column, highlight_min=True))
        return self

    def heatmap(self, column: str, color_map: str = "YlOrRd") -> TableElement:
        """Apply a heatmap colour gradient to a column.

        Args:
            column: Column name.
            color_map: Matplotlib colour map name
                (default ``"YlOrRd"``).

        Returns:
            ``self`` for chaining.
        """
        self.conditional_formats.append(ConditionalFormat(column=column, color_map=color_map))
        return self
