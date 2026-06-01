"""Document — a complete report container holding multiple slides."""

from __future__ import annotations

import dataclasses
from typing import Optional

from reporting.slide import Slide
from reporting.styles.theme import Theme, CorporateTheme
from reporting.renderers.base import BaseRenderer


@dataclasses.dataclass
class Document:
    title: str
    author: str = ""
    theme: Theme = dataclasses.field(default_factory=CorporateTheme)
    slides: list[Slide] = dataclasses.field(default_factory=list)

    def add_slide(self, slide: Slide) -> Slide:
        self.slides.append(slide)
        return slide

    def new_slide(
        self,
        title: str,
        subtitle: Optional[str] = None,
        theme: Optional[Theme] = None,
        width: float = 960.0,
        height: float = 540.0,
    ) -> Slide:
        slide = Slide(
            title=title,
            subtitle=subtitle,
            theme=theme or self.theme,
            width=width,
            height=height,
        )
        self.slides.append(slide)
        return slide

    def render(self, renderer: BaseRenderer, output_path: str) -> None:
        renderer.render_document(self, output_path)
