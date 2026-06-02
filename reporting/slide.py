"""Slide — a single page in a report with grid layout and NumPy-style cell access."""

from __future__ import annotations

from typing import Any, Optional, Union

from reporting.layout.geometry import Edges, Rect, Size
from reporting.layout.grid import Grid, GridCell
from reporting.layout.sizing import Sizing, Px
from reporting.elements.text import TextElement
from reporting.elements.image import ImageElement
from reporting.elements.figure import FigureElement
from reporting.elements.table import TableElement
from reporting.elements.tablespec_element import TableSpecElement
from reporting.styles.theme import Theme, CorporateTheme
from reporting.background import Background, BackgroundType, SolidBackground, GradientBackground, ImageBackground
from reporting.title_config import TitleConfig, SubtitleConfig, TitlePanelConfig, SubtitlePlacement


class Slide:
    def __init__(
        self,
        title: str,
        subtitle: Optional[str] = None,
        theme: Optional[Theme] = None,
        width: float = 960.0,
        height: float = 540.0,
        title_panel_height: float = 60.0,
        background: Optional[Union[str, SolidBackground, GradientBackground, ImageBackground]] = None,
        title_config: Optional[TitleConfig] = None,
        subtitle_config: Optional[SubtitleConfig] = None,
        title_panel_config: Optional[TitlePanelConfig] = None,
    ):
        self.title = title
        self.subtitle = subtitle
        self.theme = theme or CorporateTheme()
        self.width = width
        self.height = height
        self.title_panel_height = title_panel_height
        if isinstance(background, str):
            self.background: Optional[Background] = SolidBackground(background)
        else:
            self.background: Optional[Background] = background
        self.title_config = title_config or TitleConfig()
        self.subtitle_config = subtitle_config or SubtitleConfig()
        self.title_panel_config = title_panel_config or TitlePanelConfig()
        self._grid: Optional[Grid] = None
        self._elements: dict[tuple[int, int], Any] = {}

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    @property
    def content_size(self) -> Size:
        return Size(self.width, self.height - self.title_panel_height)

    def get_cell_rects(self) -> list[list[Rect]]:
        if self._grid is None:
            raise RuntimeError("Call grid_layout() before accessing cells.")
        _, rects = self._grid.layout(self.content_size)
        return [[Rect(r.x, r.y, r.width, r.height) for r in row] for row in rects]

    def grid_layout(
        self,
        rows: int = 1,
        cols: int = 1,
        row_sizes: Optional[list[Sizing]] = None,
        col_sizes: Optional[list[Sizing]] = None,
        gap: float = 0.0,
        padding: Optional[Edges] = None,
    ) -> None:
        self._grid = Grid(
            rows=rows,
            cols=cols,
            row_sizes=row_sizes,
            col_sizes=col_sizes,
            gap=gap,
            padding=padding,
        )

    def __getitem__(self, pos: tuple[Union[int, slice], Union[int, slice]]) -> _CellProxy:
        if self._grid is None:
            raise RuntimeError("Call grid_layout() before accessing cells.")
        cell = self._grid[pos]
        return _CellProxy(self, cell)

    def _set_cell_element(self, cell: GridCell, element: Any) -> None:
        cell.element = element
        self._elements[(cell.panel.row, cell.panel.col)] = element


class _CellProxy:
    def __init__(self, slide: Slide, cell: GridCell) -> None:
        self._slide = slide
        self._cell = cell

    def text(self, content: str = "", **kwargs: object) -> TextElement:
        el = TextElement(content, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def image(self, source: str = "", **kwargs: object) -> ImageElement:
        el = ImageElement(source, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def plot(self, figure: object = None, **kwargs: object) -> FigureElement:
        el = FigureElement(figure, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def table(self, data: object = None, **kwargs: object) -> TableElement:
        el = TableElement(data, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el

    def table_spec(self, spec: object = None, **kwargs: object) -> TableSpecElement:
        el = TableSpecElement(spec, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el
