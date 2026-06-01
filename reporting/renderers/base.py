"""Abstract base renderer — defines the renderer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from reporting.document import Document


class BaseRenderer(ABC):
    @abstractmethod
    def render_document(self, document: "Document", output_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def render_slide(self, slide: object) -> object:
        raise NotImplementedError

    @abstractmethod
    def render_panel(self, panel: object, rect: object) -> object:
        raise NotImplementedError
