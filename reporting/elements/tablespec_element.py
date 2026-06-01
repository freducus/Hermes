"""TableSpec element — wraps a TableSpec table model, backend-agnostic."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Optional

from reporting.elements.base import BaseElement, ElementType

if TYPE_CHECKING:
    from reporting.tablespec.spec import TableSpec


@dataclasses.dataclass
class TableSpecElement(BaseElement):
    tablespec: Optional[Any] = None

    def __init__(self, tablespec: object = None, **kwargs: object) -> None:
        super().__init__(element_type=ElementType.TABLESPEC, properties=kwargs)
        self.tablespec = tablespec