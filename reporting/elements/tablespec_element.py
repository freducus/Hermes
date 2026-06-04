"""TableSpec element — wraps a TableSpec table model, backend-agnostic."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Optional

from reporting.elements.base import BaseElement, ElementType

if TYPE_CHECKING:
    from reporting.tablespec.spec import TableSpec


@dataclasses.dataclass
class TableSpecElement(BaseElement):
    """A table created from a ``TableSpec`` (advanced table model).

    ``TableSpec`` supports merged cells, per-cell styling, nested
    content, multi-row headers, and more.  Use ``TableElement``
    for simple pandas ``DataFrame`` tables.

    Args:
        tablespec: A ``TableSpec`` instance.

    Example::

        from reporting.tablespec import TableSpec, Column
        from reporting.elements.tablespec_element import TableSpecElement

        ts = TableSpec(columns=[Column("A"), Column("B")])
        ts.row(1, 2).row(3, 4)
        el = TableSpecElement(ts)
    """
    tablespec: Optional[Any] = None

    def __init__(self, tablespec: object = None, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.TABLESPEC, properties=kwargs)
        self.tablespec = tablespec