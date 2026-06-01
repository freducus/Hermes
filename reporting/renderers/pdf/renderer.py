"""PDF renderer — generates PDF output using ReportLab with absolute positioning."""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING, Any, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph, Table, TableStyle

from reporting.elements.base import ElementType
from reporting.elements.figure import FigureElement
from reporting.elements.text import TextElement, TextAlignment
from reporting.elements.image import ImageElement
from reporting.elements.table import TableElement
from reporting.elements.tablespec_element import TableSpecElement
from reporting.layout.geometry import Rect, Size
from reporting.renderers.base import BaseRenderer

if TYPE_CHECKING:
    from reporting.document import Document


_PX_TO_PT = 72 / 96


def _align_to_reportlab(align: TextAlignment) -> int:
    return {
        TextAlignment.LEFT: TA_LEFT,
        TextAlignment.CENTER: TA_CENTER,
        TextAlignment.RIGHT: TA_RIGHT,
        TextAlignment.JUSTIFY: TA_JUSTIFY,
    }.get(align, TA_LEFT)


def _px_to_pt(v: float) -> float:
    return v * _PX_TO_PT


def _rect_to_canvas(slide_pt_h: float, rx: float, ry: float, rw: float, rh: float) -> tuple[float, float, float, float]:
    x = _px_to_pt(rx)
    y = slide_pt_h - _px_to_pt(ry + rh)
    w = _px_to_pt(rw)
    h = _px_to_pt(rh)
    return x, y, w, h


class PDFRenderer(BaseRenderer):
    def __init__(self) -> None:
        self._canvas: Optional[canvas.Canvas] = None
        self._slide_pt_h: float = 0
        self._temp_files: list[str] = []

    def render_document(self, document: "Document", output_path: str) -> None:
        slide = document.slides[0] if document.slides else None
        slide_w = slide.width if slide else 960.0
        slide_h = slide.height if slide else 540.0

        pw = _px_to_pt(slide_w)
        ph = _px_to_pt(slide_h)
        self._slide_pt_h = ph

        c = canvas.Canvas(output_path, pagesize=(pw, ph))
        self._canvas = c
        self._temp_files = []

        try:
            for slide in document.slides:
                self._render_slide(slide)
                c.showPage()
            c.save()
        finally:
            for tmp in self._temp_files:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
            self._canvas = None

    def render_slide(self, slide: object) -> object:
        if self._canvas is not None:
            self._render_slide(slide)
        return slide

    def _render_slide(self, slide: Any) -> None:
        c = self._canvas
        if c is None:
            return

        self._render_title_panel(slide)

        if slide._grid is None:
            return

        cell_rects = slide.get_cell_rects()
        for r in range(slide._grid.rows):
            for c2 in range(slide._grid.cols):
                cell = slide._grid.cells[r][c2]
                self._render_panel_background(cell_rects[r][c2], cell.panel.background_color)
                element = cell.element
                if element is None:
                    continue
                self._render_element(element, cell_rects[r][c2])

    def _render_title_panel(self, slide: Any) -> None:
        c = self._canvas
        if c is None:
            return

        th_pt = _px_to_pt(slide.title_panel_height)
        y0 = self._slide_pt_h - th_pt

        if slide.subtitle:
            sub_style = ParagraphStyle(
                "SlideSubtitle",
                fontName="Helvetica",
                fontSize=10,
                leading=13,
                alignment=TA_LEFT,
                textColor=colors.Color(0.4, 0.4, 0.4),
            )
            sp = Paragraph(slide.subtitle, sub_style)
            sub_frame = Frame(
                _px_to_pt(20), y0, self._slide_pt_h - _px_to_pt(40), th_pt,
                leftPadding=0, rightPadding=0, topPadding=20, bottomPadding=0,
                id="subtitle",
            )
            sub_frame.addFromList([sp], c)

        c.setStrokeColor(colors.Color(0.8, 0.8, 0.8))
        c.line(_px_to_pt(20), y0, self._slide_pt_h - _px_to_pt(20), y0)

    def _render_panel_background(self, rect: Any, bg_color: Optional[str]) -> None:
        if bg_color is None:
            return
        c = self._canvas
        if c is None:
            return
        try:
            h = bg_color.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            x = _px_to_pt(rect.x)
            y = self._slide_pt_h - _px_to_pt(rect.y + rect.height)
            w = _px_to_pt(rect.width)
            h_pt = _px_to_pt(rect.height)
            c.setFillColorRGB(r / 255, g / 255, b / 255)
            c.rect(x, y, w, h_pt, fill=1, stroke=0)
        except Exception:
            pass

    def _render_element(self, element: Any, rect: Any) -> None:
        if element.element_type == ElementType.TEXT:
            self._render_text(element, rect)
        elif element.element_type == ElementType.IMAGE:
            self._render_image(element, rect)
        elif element.element_type == ElementType.FIGURE:
            self._render_figure(element, rect)
        elif element.element_type == ElementType.TABLE:
            self._render_table(element, rect)
        elif element.element_type == ElementType.TABLESPEC:
            self._render_tablespec(element, rect)
        elif element.element_type == ElementType.CONTAINER:
            self._render_container(element, rect)

    def _render_text(self, element: TextElement, rect: Any) -> None:
        c = self._canvas
        if c is None:
            return

        x, y, w, h = _rect_to_canvas(self._slide_pt_h, rect.x, rect.y, rect.width, rect.height)

        for block in element.blocks:
            parts: list[str] = []
            block_font: Optional[str] = None
            block_size: Optional[float] = None
            for run in block.runs:
                tag = ""
                close = ""
                if run.bold:
                    tag += "<b>"
                    close = "</b>" + close
                if run.italic:
                    tag += "<i>"
                    close = "</i>" + close
                if run.font_name:
                    tag += f'<font face="{run.font_name}">'
                    close = "</font>" + close
                    if block_font is None:
                        block_font = run.font_name
                if run.color:
                    tag += f'<font color="{run.color}">'
                    close = "</font>" + close
                if run.size:
                    tag += f'<font size="{run.size}">'
                    close = "</font>" + close
                    if block_size is None:
                        block_size = run.size
                parts.append(f"{tag}{run.text}{close}")
            html = "".join(parts)

            fs = block_size or max(h * 0.12, 6)
            style = ParagraphStyle(
                "CellText",
                fontName=block_font or "Helvetica",
                fontSize=fs,
                leading=max(fs * 1.2, 8),
                alignment=_align_to_reportlab(block.alignment),
                spaceBefore=1,
                spaceAfter=1,
            )
            p = Paragraph(html, style)
            frame = Frame(x, y, w, h, leftPadding=4, rightPadding=4, topPadding=4, bottomPadding=4, id="cell")
            frame.addFromList([p], c)

    def _render_image(self, element: ImageElement, rect: Any) -> None:
        c = self._canvas
        if c is None or not element.source or not os.path.exists(element.source):
            return
        x, y, w, h = _rect_to_canvas(self._slide_pt_h, rect.x, rect.y, rect.width, rect.height)
        try:
            c.drawImage(element.source, x + 2, y + 2, width=w - 4, height=h - 4, preserveAspectRatio=True, anchor='c')
        except Exception:
            pass

    def _render_figure(self, element: FigureElement, rect: Any) -> None:
        c = self._canvas
        if c is None or element.figure is None:
            return
        try:
            fig = element.figure
            x, y, w, h = _rect_to_canvas(self._slide_pt_h, rect.x, rect.y, rect.width, rect.height)

            if element.format == "pdf":
                self._render_figure_vector(fig, c, x, y, w, h)
            else:
                self._render_figure_raster(fig, element, c, x, y, w, h)
        except Exception:
            pass

    def _render_figure_vector(self, fig: Any, c: Any, x: float, y: float, w: float, h: float) -> None:
        try:
            import io
            from pdfrw import PdfReader
            from pdfrw.buildxobj import pagexobj
            from pdfrw.toreportlab import makerl
        except ImportError:
            self._render_figure_raster(fig, None, c, x, y, w, h)
            return

        old_size = fig.get_size_inches()
        try:
            fig.set_size_inches(w / 72, h / 72)
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf", bbox_inches="tight")
            buf.seek(0)
            reader = PdfReader(buf)
            xobj = pagexobj(reader.pages[0])
            name = makerl(c, xobj)
            bbox = xobj.BBox
            scale_x = w / bbox[2]
            scale_y = h / bbox[3]
            scale = min(scale_x, scale_y)
            c.saveState()
            c.translate(x + (w - bbox[2] * scale) / 2, y + (h - bbox[3] * scale) / 2)
            c.scale(scale, scale)
            c.doForm(name)
            c.restoreState()
        except Exception:
            self._render_figure_raster(fig, None, c, x, y, w, h)
        finally:
            fig.set_size_inches(old_size)

    def _render_figure_raster(self, fig: Any, element: Any, c: Any, x: float, y: float, w: float, h: float) -> None:
        dpi = element.dpi if element else 150
        old_size = fig.get_size_inches()
        fig.set_size_inches(w / 72, h / 72)
        fd, tmp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        fig.savefig(tmp_path, dpi=dpi, bbox_inches="tight", format="png")
        fig.set_size_inches(old_size)
        self._temp_files.append(tmp_path)
        c.drawImage(tmp_path, x + 2, y + 2, width=w - 4, height=h - 4, preserveAspectRatio=True, anchor='c')

    def _render_table(self, element: TableElement, rect: Any) -> None:
        c = self._canvas
        if c is None or element.data is None:
            return

        try:
            df = element.data
            if element.include_index:
                df = df.reset_index()

            headers = [str(col) for col in df.columns]
            rows_data: list[list[str]] = [headers]
            for _, row in df.iterrows():
                rows_data.append([str(v) for v in row])

            x, y, w, h = _rect_to_canvas(self._slide_pt_h, rect.x, rect.y, rect.width, rect.height)
            n_cols = len(headers)
            n_rows_t = len(rows_data)
            pad = 8
            avail_w = max(w - 2 * pad, 10)
            col_w = max(avail_w / max(n_cols, 1), 10)

            row_h_pt = max(h / max(n_rows_t, 1), 10)
            body_size = max(min(row_h_pt * 0.3, 8), 3)
            header_size = max(min(row_h_pt * 0.35, 9), 4)

            cmds: list[tuple] = [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), header_size),
                ("FONTSIZE", (0, 1), (-1, -1), body_size),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.Color(0.85, 0.85, 0.85)),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.27, 0.45, 0.77)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]

            if element.zebra:
                for i in range(2, len(rows_data), 2):
                    cmds.append(("BACKGROUND", (0, i), (-1, i), colors.Color(0.95, 0.95, 0.95)))

            t = Table(rows_data, colWidths=[col_w] * n_cols)
            t.setStyle(TableStyle(cmds))
            frame = Frame(x, y, w, h, leftPadding=pad, rightPadding=pad, topPadding=4, bottomPadding=4, id="table_cell")
            frame.addFromList([t], c)
        except Exception:
            pass

    def _render_tablespec(self, element: Any, rect: Any) -> None:
        c = self._canvas
        if c is None:
            return

        spec = element.tablespec
        if spec is None or not spec.columns or not spec.rows:
            return

        try:
            x, y, w, h = _rect_to_canvas(self._slide_pt_h, rect.x, rect.y, rect.width, rect.height)

            headers = [col.label for col in spec.columns]
            num_cols = len(headers)
            num_rows = len(spec.rows) + 1

            pad = 4
            avail_w = max(w - 2 * pad, 10)
            col_w = max(avail_w / max(num_cols, 1), 8)

            row_height = max(h / max(num_rows, 1), 10)
            body_size = max(min(row_height * 0.3, 8), 3)
            header_size = max(min(row_height * 0.35, 9), 4)

            data_rows: list[list[str]] = [list(headers)]
            data_rows.extend(
                [""] * num_cols for _ in range(len(spec.rows))
            )

            cmds: list[tuple] = [
                ("FONTNAME", (0, 0), (num_cols - 1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (num_cols - 1, 0), header_size),
                ("FONTSIZE", (0, 1), (num_cols - 1, num_rows - 1), body_size),
                ("ALIGN", (0, 0), (num_cols - 1, num_rows - 1), "CENTER"),
                ("VALIGN", (0, 0), (num_cols - 1, num_rows - 1), "MIDDLE"),
                ("GRID", (0, 0), (num_cols - 1, num_rows - 1), 0.5, colors.Color(0.85, 0.85, 0.85)),
                ("BACKGROUND", (0, 0), (num_cols - 1, 0), colors.Color(0.27, 0.45, 0.77)),
                ("TEXTCOLOR", (0, 0), (num_cols - 1, 0), colors.white),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]

            if spec.style.zebra:
                for i in range(2, num_rows, 2):
                    cmds.append(("BACKGROUND", (0, i), (num_cols - 1, i),
                                 colors.Color(0.95, 0.95, 0.95)))

            occupied = [[False] * num_cols for _ in range(num_rows)]
            for r in range(len(spec.rows)):
                row = spec.rows[r]
                rr = r + 1
                for c_idx in range(min(len(row.cells), num_cols)):
                    if occupied[rr][c_idx]:
                        continue
                    cell = row.cells[c_idx]

                    txt = cell.text if cell.text is not None else (str(cell.value) if cell.value is not None else "")
                    data_rows[rr][c_idx] = txt

                    if cell.colspan > 1 or cell.rowspan > 1:
                        c2 = min(c_idx + cell.colspan - 1, num_cols - 1)
                        r2 = min(rr + cell.rowspan - 1, num_rows - 1)
                        cmds.append(("SPAN", (c_idx, rr), (c2, r2)))
                        for span_r in range(rr, r2 + 1):
                            for span_c in range(c_idx, c2 + 1):
                                occupied[span_r][span_c] = True
                        occupied[rr][c_idx] = False

                    if cell.background_color:
                        try:
                            hex_bg = cell.background_color.lstrip("#")
                            bg = colors.Color(int(hex_bg[0:2], 16) / 255, int(hex_bg[2:4], 16) / 255, int(hex_bg[4:6], 16) / 255)
                            cmds.append(("BACKGROUND", (c_idx, rr), (c_idx, rr), bg))
                        except Exception:
                            pass

                    if cell.text_color:
                        try:
                            hex_tc = cell.text_color.lstrip("#")
                            tc = colors.Color(int(hex_tc[0:2], 16) / 255, int(hex_tc[2:4], 16) / 255, int(hex_tc[4:6], 16) / 255)
                            cmds.append(("TEXTCOLOR", (c_idx, rr), (c_idx, rr), tc))
                        except Exception:
                            pass

            t = Table(data_rows, colWidths=[col_w] * num_cols)
            t.setStyle(TableStyle(cmds))
            frame = Frame(x, y, w, h, leftPadding=pad, rightPadding=pad, topPadding=2, bottomPadding=2, id="tablespec_cell")
            frame.addFromList([t], c)
        except Exception:
            pass

    def _render_container(self, element: Any, rect: Any) -> None:
        inner = element.grid
        if inner is None:
            return
        inner_size, inner_rects = inner.layout(Size(rect.width, rect.height))
        for r in range(inner.rows):
            for c2 in range(inner.cols):
                cell = inner.cells[r][c2]
                cell_rect = inner_rects[r][c2]
                abs_rect = Rect(
                    x=rect.x + cell_rect.x,
                    y=rect.y + cell_rect.y,
                    width=cell_rect.width,
                    height=cell_rect.height,
                )
                self._render_panel_background(abs_rect, cell.panel.background_color)
                inner_el = cell.element
                if inner_el is None:
                    continue
                self._render_element(inner_el, abs_rect)

    def render_panel(self, panel: object, rect: object) -> object:
        return None
