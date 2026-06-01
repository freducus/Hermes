"""PPTX renderer — generates PowerPoint output using python-pptx."""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING, Any, Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

from reporting.elements.base import ElementType
from reporting.elements.figure import FigureElement
from reporting.elements.text import TextElement, TextAlignment
from reporting.elements.image import ImageElement
from reporting.elements.table import TableElement
from reporting.layout.geometry import Rect, Size
from reporting.renderers.base import BaseRenderer

if TYPE_CHECKING:
    from reporting.document import Document
    from reporting.slide import Slide


def _px_to_emu(v: float, slide_dim: float, target_emu: float) -> int:
    return int(v * target_emu / slide_dim)


class PPTXRenderer(BaseRenderer):
    def __init__(self) -> None:
        self._prs: Optional[Presentation] = None
        self._slide_w_emu: int = 0
        self._slide_h_emu: int = 0
        self._slide_w: float = 960.0
        self._slide_h: float = 540.0

    def render_document(self, document: "Document", output_path: str) -> None:
        s = document.slides[0] if document.slides else None
        self._slide_w = s.width if s else 960.0
        self._slide_h = s.height if s else 540.0
        self._slide_w_emu = int(self._slide_w * 914400 / 960)
        self._slide_h_emu = int(self._slide_h * 914400 / 540)

        self._prs = Presentation()
        self._prs.slide_width = self._slide_w_emu
        self._prs.slide_height = self._slide_h_emu

        for slide in document.slides:
            self._render_slide(slide)

        self._prs.save(output_path)

    def render_slide(self, slide: object) -> object:
        return self._render_slide(slide)

    def _render_slide(self, slide: Slide) -> None:
        if self._prs is None:
            return
        slide_layout = self._prs.slide_layouts[6]
        pptx_slide = self._prs.slides.add_slide(slide_layout)

        self._render_pptx_title(pptx_slide, slide)

        if slide._grid is None:
            return

        cell_rects = slide.get_cell_rects()
        for r in range(slide._grid.rows):
            for c in range(slide._grid.cols):
                cell = slide._grid.cells[r][c]
                element = cell.element
                if element is None:
                    continue
                self._render_element(pptx_slide, element, cell_rects[r][c])

    def _render_pptx_title(self, pptx_slide: Any, slide: Slide) -> None:
        left = _px_to_emu(10, self._slide_w, self._slide_w_emu)
        top = _px_to_emu(5, self._slide_h, self._slide_h_emu)
        width = _px_to_emu(self._slide_w - 20, self._slide_w, self._slide_w_emu)
        height = _px_to_emu(slide.title_panel_height - 10, self._slide_h, self._slide_h_emu)

        txBox = pptx_slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = slide.title
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

        if slide.subtitle:
            p2 = tf.add_paragraph()
            p2.text = slide.subtitle
            p2.font.size = Pt(11)
            p2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    def _render_element(self, pptx_slide: Any, element: Any, rect: Any) -> None:
        left = _px_to_emu(rect.x, self._slide_w, self._slide_w_emu)
        top = _px_to_emu(rect.y, self._slide_h, self._slide_h_emu)
        width = _px_to_emu(rect.width, self._slide_w, self._slide_w_emu)
        height = _px_to_emu(rect.height, self._slide_h, self._slide_h_emu)

        if element.element_type == ElementType.TEXT:
            self._render_text(pptx_slide, element, left, top, width, height)
        elif element.element_type == ElementType.IMAGE:
            self._render_image_in_cell(pptx_slide, element, left, top, width, height)
        elif element.element_type == ElementType.FIGURE:
            self._render_figure_in_cell(pptx_slide, element, left, top, width, height)
        elif element.element_type == ElementType.TABLE:
            self._render_table_in_cell(pptx_slide, element, left, top, width, height)
        elif element.element_type == ElementType.CONTAINER:
            self._render_pptx_container(pptx_slide, element, rect)

    def _render_text(self, pptx_slide: Any, element: TextElement, left: int, top: int, width: int, height: int) -> None:
        txBox = pptx_slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True

        for i, block in enumerate(element.blocks):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()

            align_map = {
                TextAlignment.LEFT: PP_ALIGN.LEFT,
                TextAlignment.CENTER: PP_ALIGN.CENTER,
                TextAlignment.RIGHT: PP_ALIGN.RIGHT,
                TextAlignment.JUSTIFY: PP_ALIGN.JUSTIFY,
            }
            p.alignment = align_map.get(block.alignment, PP_ALIGN.LEFT)

            for run in block.runs:
                run_obj = p.add_run()
                run_obj.text = run.text
                if run.font_name:
                    run_obj.font.name = run.font_name
                if run.bold:
                    run_obj.font.bold = True
                if run.italic:
                    run_obj.font.italic = True
                if run.size:
                    run_obj.font.size = Pt(run.size)
                if run.color:
                    try:
                        h = run.color.lstrip("#")
                        run_obj.font.color.rgb = RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
                    except Exception:
                        pass

    def _render_image_in_cell(self, pptx_slide: Any, element: ImageElement, left: int, top: int, width: int, height: int) -> None:
        if not element.source or not os.path.exists(element.source):
            return
        pptx_slide.shapes.add_picture(element.source, left, top, width, height)

    def _render_figure_in_cell(self, pptx_slide: Any, element: FigureElement, left: int, top: int, width: int, height: int) -> None:
        if element.figure is None:
            return
        try:
            fig = element.figure
            old_size = fig.get_size_inches()
            fig.set_size_inches(width / 96, height / 96)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            fig.savefig(tmp_path, dpi=element.dpi, bbox_inches=element.bbox_inches, format="png")
            fig.set_size_inches(old_size)
            pptx_slide.shapes.add_picture(tmp_path, left, top, width, height)
            os.unlink(tmp_path)
        except Exception:
            pass

    def _render_table_in_cell(self, pptx_slide: Any, element: TableElement, left: int, top: int, width: int, height: int) -> None:
        if element.data is None:
            return
        try:
            df = element.data
            if element.include_index:
                df = df.reset_index()
            rows_count = len(df) + 1
            cols_count = len(df.columns)
            table_shape = pptx_slide.shapes.add_table(rows_count, cols_count, left, top, width, height)
            table = table_shape.table

            for j, col_name in enumerate(df.columns):
                cell = table.cell(0, j)
                cell.text = str(col_name)

            for i, (_, row) in enumerate(df.iterrows()):
                for j, val in enumerate(row):
                    cell = table.cell(i + 1, j)
                    cell.text = str(val)

            if element.zebra:
                for i in range(1, rows_count):
                    if i % 2 == 0:
                        for j in range(cols_count):
                            table.cell(i, j).fill.solid()
                            table.cell(i, j).fill.fore_color.rgb = RGBColor(0xF3, 0xF3, 0xF3)
        except Exception:
            pass

    def _render_pptx_container(self, pptx_slide: Any, element: Any, parent_rect: Any) -> None:
        inner = element.grid
        if inner is None:
            return
        inner_size, inner_rects = inner.layout(Size(parent_rect.width, parent_rect.height))
        for r in range(inner.rows):
            for c2 in range(inner.cols):
                cell = inner.cells[r][c2]
                cell_rect = inner_rects[r][c2]
                abs_rect = Rect(
                    x=parent_rect.x + cell_rect.x,
                    y=parent_rect.y + cell_rect.y,
                    width=cell_rect.width,
                    height=cell_rect.height,
                )
                inner_el = cell.element
                if inner_el is None:
                    continue
                self._render_element(pptx_slide, inner_el, abs_rect)

    def render_panel(self, panel: object, rect: object) -> object:
        return None
