"""PDF renderer — generates PDF output using ReportLab with absolute positioning."""

from __future__ import annotations

import math
import os
import tempfile
import warnings

from typing import TYPE_CHECKING, Any, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph, Table, TableStyle

from reporting.elements.base import ElementType
from reporting.elements.figure import FigureElement
from reporting.elements.text import TextElement, TextAlignment
from reporting.elements.image import ImageElement
from reporting.elements.table import TableElement
from reporting.elements.tablespec_element import TableSpecElement
from reporting.layout.geometry import Edges, Rect, Size
from reporting.layout.panel import HAlign, VAlign, Panel
from reporting.renderers.base import BaseRenderer
from reporting.background import BackgroundType, SolidBackground, GradientBackground, ImageBackground
from reporting.styles.colors import Color
from reporting.tablespec.sizing import ColumnDistrib, TableFitMode
from reporting.tablespec.style import CellStyle

if TYPE_CHECKING:
    from reporting.document import Document


_PX_TO_PT = 72 / 96

_FONT_MAP: dict[str, str] = {
    "Arial": "Helvetica",
    "Arial Black": "Helvetica",
    "Times New Roman": "Times-Roman",
    "Courier New": "Courier",
    "Courier New Bold": "Courier-Bold",
    "Verdana": "Helvetica",
    "Tahoma": "Helvetica",
    "Calibri": "Helvetica",
    "Segoe UI": "Helvetica",
}


def _ps_font_name(family: str) -> str:
    """Map CSS font-family to a ReportLab PostScript base name."""
    return _FONT_MAP.get(family.strip(), family.strip())


def _align_to_reportlab(align: TextAlignment) -> int:
    return {
        TextAlignment.LEFT: TA_LEFT,
        TextAlignment.CENTER: TA_CENTER,
        TextAlignment.RIGHT: TA_RIGHT,
        TextAlignment.JUSTIFY: TA_JUSTIFY,
    }.get(align, TA_LEFT)


def _h_align_to_str(align_h: Optional[str]) -> str:
    return {"left": "LEFT", "center": "CENTER", "right": "RIGHT"}.get(align_h or "", "LEFT")


def _v_align_to_str(align_v: Optional[str]) -> str:
    return {"top": "TOP", "middle": "MIDDLE", "bottom": "BOTTOM"}.get(align_v or "", "MIDDLE")


def _resolve_font_name(base: str, bold: Optional[bool], italic: Optional[bool]) -> str:
    b = bold or False
    i = italic or False
    ps_base = _ps_font_name(base)
    if b and i:
        return ps_base + "-BoldOblique"
    elif b:
        return ps_base + "-Bold"
    elif i:
        return ps_base + "-Oblique"
    return ps_base


def _cell_padding(padding: Any) -> tuple[float, float, float, float]:
    """Return (top, bottom, left, right) padding in pt."""
    if padding is None:
        return 1.0, 1.0, 2.0, 2.0
    if isinstance(padding, (int, float)):
        return padding, padding, padding, padding
    return padding.top or 1, padding.bottom or 1, padding.left or 2, padding.right or 2


def _px_to_pt(v: float) -> float:
    return v * _PX_TO_PT


def _pt_to_px(v: float) -> float:
    """Convert points → pixels at 96 dpi."""
    return v / _PX_TO_PT  # = v * 96/72


def _rect_to_canvas(slide_pt_h: float, rx: float, ry: float, rw: float, rh: float) -> tuple[float, float, float, float]:
    x = _px_to_pt(rx)
    y = slide_pt_h - _px_to_pt(ry + rh)
    w = _px_to_pt(rw)
    h = _px_to_pt(rh)
    return x, y, w, h


class PDFRenderer(BaseRenderer):
    """Render a report to PDF using ReportLab with absolute positioning.

    Each ``Slide`` becomes a PDF page.  The title panel is rendered
    at the top, followed by the grid layout with all elements
    positioned absolutely.

    Supported element types: ``TextElement``, ``ImageElement``,
    ``FigureElement``, ``TableElement``, ``TableSpecElement``,
    ``ContainerElement``.

    Example::

        from reporting.document import Document
        from reporting.renderers.pdf.renderer import PDFRenderer

        doc = Document()
        slide = doc.new_slide("Results")
        slide.grid_layout(rows=1, cols=1)
        slide[0, 0].text("Hello, PDF!")

        renderer = PDFRenderer()
        renderer.render_document(doc, "output.pdf")
    """
    def __init__(self) -> None:
        self._canvas: Optional[canvas.Canvas] = None
        self._slide_pt_h: float = 0
        self._temp_files: list[str] = []
        self._page_num: int = 1
        self._total_pages: int = 1

    def render_document(self, document: "Document", output_path: str) -> None:
        """Render all slides of a document to a single PDF file.

        Each slide becomes one page.  Temporary figure images
        are cleaned up after rendering.

        Args:
            document: The report document.
            output_path: Output PDF file path
                (e.g. ``"report.pdf"``).
        """
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
            total = len(document.slides)
            for i, slide in enumerate(document.slides):
                self._page_num = i + 1
                self._total_pages = total
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
        """Render a single slide (add to current PDF page, then ``showPage``).

        Args:
            slide: A ``Slide`` instance.

        Returns:
            The slide object.
        """
        if self._canvas is not None:
            self._render_slide(slide)
        return slide

    def _render_slide(self, slide: Any) -> None:
        c = self._canvas
        if c is None:
            return

        self._current_slide = slide
        self._render_background(slide)
        self._render_title_panel(slide)

        if slide._grid is not None:
            cell_rects = slide.get_cell_rects()
            offset_y = slide.title_panel.height
            for r in range(slide._grid.rows):
                for c2 in range(slide._grid.cols):
                    cell = slide._grid.cells[r][c2]
                    rect = cell_rects[r][c2]
                    adj = Rect(rect.x, rect.y + offset_y, rect.width, rect.height)
                    self._render_panel_background(adj, cell.panel.background_color)
                    element = cell.element
                    if element is None:
                        continue
                    self._render_element(element, adj, panel=cell.panel)

        self._render_footer(slide)

    def _render_background(self, slide: Any) -> None:
        bg = getattr(slide, "background", None)
        if bg is None:
            return
        c = self._canvas
        if c is None:
            return
        pw = _px_to_pt(slide.width)
        ph = _px_to_pt(slide.height)

        if bg.type == BackgroundType.SOLID:
            try:
                _c = Color.parse(bg.color).reportlab_color
                c.setFillColor(_c)
                c.rect(0, 0, pw, ph, fill=1, stroke=0)
            except Exception:
                pass

        elif bg.type == BackgroundType.GRADIENT:
            try:
                c1 = Color.parse(bg.start_color)
                c2 = Color.parse(bg.end_color)
                r1, g1, b1 = c1.float_rgb
                r2, g2, b2 = c2.float_rgb

                bands = 80
                angle_rad = math.radians(bg.angle)
                cos_a = abs(math.cos(angle_rad))
                sin_a = abs(math.sin(angle_rad))

                for i in range(bands):
                    t = i / bands
                    r = r1 + (r2 - r1) * t
                    g = g1 + (g2 - g1) * t
                    b = b1 + (b2 - b1) * t

                    band_h = ph / bands
                    band_w = pw / bands
                    c.setFillColorRGB(r, g, b)
                    if cos_a >= sin_a:
                        y0 = ph - (i + 1) * band_h
                        c.rect(0, y0, pw, band_h + 1, fill=1, stroke=0)
                    else:
                        x0 = i * band_w
                        c.rect(x0, 0, band_w + 1, ph, fill=1, stroke=0)
            except Exception:
                pass

        elif bg.type == BackgroundType.IMAGE:
            try:
                if os.path.exists(bg.source):
                    if bg.opacity < 1.0:
                        c.saveState()
                    c.drawImage(bg.source, 0, 0, width=pw, height=ph, preserveAspectRatio=True, anchor='c')
                    if bg.opacity < 1.0:
                        c.setFillColorRGB(1, 1, 1, alpha=1.0 - bg.opacity)
                        c.rect(0, 0, pw, ph, fill=1, stroke=0)
                        c.restoreState()
            except Exception:
                pass

    def _render_title_panel(self, slide: Any) -> None:
        c = self._canvas
        if c is None:
            return

        t = slide.title
        s = slide.subtitle
        panel = slide.title_panel
        th_pt = _px_to_pt(slide.title_panel.height)
        y0 = self._slide_pt_h - th_pt
        margin = _px_to_pt(20)
        text_w = _px_to_pt(slide.width) - margin * 2

        title_style = ParagraphStyle(
            "SlideTitle",
            fontName=_resolve_font_name(t.font_name, t.bold, None),
            fontSize=t.font_size,
            leading=t.font_size * 1.2,
            alignment=_align_to_reportlab(t.alignment),
            textColor=Color.parse(t.color).reportlab_color,
        )
        tp = Paragraph(t.text, title_style)

        is_beside = (
            s
            and panel.subtitle_placement.value == "beside"
        )

        if is_beside:
            sub_w = text_w * panel.subtitle_width_ratio
            title_w = text_w - sub_w

            title_frame = Frame(
                margin, y0, title_w, th_pt,
                leftPadding=0, rightPadding=0, topPadding=6, bottomPadding=0,
                id="title",
            )
            title_frame.addFromList([tp], c)

            sub_font = _resolve_font_name(s.font_name, s.bold, None)
            sub_x = margin + title_w
            sub_align = _align_to_reportlab(s.alignment)
            sub_color = Color.parse(s.color).reportlab_color

            c.saveState()
            c.setFont(sub_font, s.font_size)
            c.setFillColor(sub_color)
            sub_leading = s.font_size * 1.3
            sub_baseline = y0 + (th_pt - sub_leading) / 2 + s.font_size * 0.35
            if sub_align == TA_RIGHT:
                c.drawRightString(sub_x + sub_w, sub_baseline, s.text)
            elif sub_align == TA_CENTER:
                c.drawCentredString(sub_x + sub_w / 2, sub_baseline, s.text)
            else:
                c.drawString(sub_x, sub_baseline, s.text)
            c.restoreState()
        else:
            flowables = [tp]
            if s:
                sub_font = _resolve_font_name(s.font_name, s.bold, None)
                sub_style = ParagraphStyle(
                    "SlideSubtitle",
                    fontName=sub_font,
                    fontSize=s.font_size,
                    leading=s.font_size * 1.3,
                    alignment=_align_to_reportlab(s.alignment),
                    textColor=Color.parse(s.color).reportlab_color,
                )
                from reportlab.platypus import Spacer
                flowables.append(Spacer(1, 4))
                flowables.append(Paragraph(s.text, sub_style))

            main_frame = Frame(
                margin, y0, text_w, th_pt,
                leftPadding=0, rightPadding=0, topPadding=6, bottomPadding=2,
                id="title_panel",
            )
            main_frame.addFromList(flowables, c)

        if panel.show_separator:
            sep_y = y0 + _px_to_pt(panel.separator_margin)
            c.setStrokeColor(Color.parse(panel.separator_color).reportlab_color)
            c.setLineWidth(panel.separator_width)
            c.line(margin, sep_y, margin + text_w, sep_y)

    def _render_footer(self, slide: Any) -> None:
        c = self._canvas
        if c is None:
            return

        # Skip entirely when no footer grid has been set up
        if slide._footer_grid is None:
            return

        fp = slide.footer_panel
        fh = slide.footer_panel.height
        pad = fp.padding

        # Footer background area (top of page in canvas coordinates)
        footer_y_pt = 0  # bottom of slide
        footer_h_pt = _px_to_pt(fh)

        # Separator line (above the footer)
        if fp.show_separator:
            sep_y = footer_y_pt + footer_h_pt + _px_to_pt(fp.separator_margin)
            slide_w_pt = _px_to_pt(slide.width)
            sep_x = _px_to_pt(pad.left)
            sep_w = slide_w_pt - _px_to_pt(pad.left + pad.right)
            c.setStrokeColor(Color.parse(fp.separator_color).reportlab_color)
            c.setLineWidth(fp.separator_width)
            c.line(sep_x, sep_y, sep_x + sep_w, sep_y)

        cell_rects = slide.get_footer_cell_rects()
        # Offset from top of slide (pixels) → top-left corner of footer content area
        offset_y_px = slide.height - fh + pad.top

        for r in range(slide._footer_grid.rows):
            for c2 in range(slide._footer_grid.cols):
                cell = slide._footer_grid.cells[r][c2]
                rect = cell_rects[r][c2]
                # Position in slide-relative pixels
                adj = Rect(
                    rect.x + pad.left,
                    rect.y + offset_y_px,
                    rect.width,
                    rect.height,
                )
                element = cell.element
                if element is None:
                    continue
                self._render_footer_element(element, adj)

    def _render_footer_element(self, element: Any, rect: Rect) -> None:
        """Render a single footer element, replacing ``{page}`` / ``{total}`` placeholders."""
        from reporting.elements.text import TextElement

        if isinstance(element, TextElement):
            auto_type = element.properties.get("_auto")
            if auto_type == "page_number":
                for block in element.blocks:
                    for run in block.runs:
                        run.text = str(self._page_num)
            elif auto_type == "total_pages":
                for block in element.blocks:
                    for run in block.runs:
                        run.text = str(self._total_pages)
            else:
                # Replace placeholders in plain text elements
                for block in element.blocks:
                    for run in block.runs:
                        run.text = run.text.replace("{page}", str(self._page_num))
                        run.text = run.text.replace("{total}", str(self._total_pages))
        self._render_element(element, rect, frame_padding=0)

    def _render_panel_background(self, rect: Rect, bg_color: Optional[str] = None) -> None:
        """Fill the panel rectangle with the given background colour."""
        if bg_color is None:
            return
        c = self._canvas
        if c is None:
            return
        try:
            cc = Color.parse(bg_color)
            x = _px_to_pt(rect.x)
            y = self._slide_pt_h - _px_to_pt(rect.y + rect.height)
            w = _px_to_pt(rect.width)
            h_pt = _px_to_pt(rect.height)
            c.setFillColor(cc.reportlab_color)
            c.rect(x, y, w, h_pt, fill=1, stroke=0)
        except Exception:
            pass

    def _render_element(self, element: Any, rect: Any, panel: Optional[Any] = None, frame_padding: float = 4.0) -> None:
        if panel:
            rect = self._compute_content_rect(rect, element, panel)
        if element.element_type == ElementType.TEXT:
            self._render_text(element, rect, frame_padding=frame_padding)
        elif element.element_type == ElementType.IMAGE:
            self._render_image(element, rect)
        elif element.element_type == ElementType.FIGURE:
            self._render_figure(element, rect)
        elif element.element_type == ElementType.TABLE:
            self._render_table(element, rect)
        elif element.element_type == ElementType.TABLESPEC:
            self._render_tablespec(element, rect, panel)
        elif element.element_type == ElementType.CONTAINER:
            self._render_container(element, rect)

    def _estimate_content_size(
        self,
        element: Any,
        rect: Rect,
    ) -> Size:
        """Return the natural (unscaled) content size of *element* in **points**.

        ``rect`` is the panel rect (pixels) — used for percentage-of-container
        computations.
        """
        if element.element_type == ElementType.TEXT:
            blocks = element.blocks
            if not blocks or not blocks[0].runs:
                return Size(rect.width, rect.height)
            run = blocks[0].runs[0]
            theme = getattr(self, '_current_slide', None)
            body = theme.theme.typography.body if theme is not None else None
            fallback_family = body.family if body is not None else "Helvetica"
            fallback_size = body.size if body is not None else 10.0
            font_name = _ps_font_name(run.font_name or fallback_family)
            font_size = run.size or fallback_size
            try:
                text_w = stringWidth(run.text, font_name, font_size)
            except Exception:
                text_w = font_size * len(run.text) * 0.4
            text_h = font_size * 1.4
            return Size(text_w + 8, text_h + 8)

        if element.element_type == ElementType.TABLESPEC:
            spec = element.tablespec
            pad = spec.style.padding
            font_name = spec.style.font_name
            body_fs = spec.style.font_size
            header_fs = spec.style.header_font_size
            try:
                nat_widths = self._measure_column_widths(
                    spec, font_name, body_fs, header_fs, pad,
                )
                table_w = sum(nat_widths)
            except Exception:
                table_w = 80.0
            pad_h = sum(_cell_padding(pad)[:2])
            hr = spec.style.header_rows
            row_h = spec.style.font_size * spec.style.line_height + pad_h
            header_row_h = spec.style.header_font_size * spec.style.line_height + pad_h
            table_h = len(spec.rows) * row_h + hr * header_row_h
            return Size(table_w, table_h)

        if element.element_type == ElementType.TABLE:
            df = element.data
            if df is None:
                return Size(_px_to_pt(rect.width), _px_to_pt(rect.height))
            n_cols = len(df.columns)
            n_rows = len(df) + 1
            font_size = 10
            col_w = 40 * n_cols
            row_h = font_size * 1.4 + 6
            return Size(col_w, n_rows * row_h)

        if element.element_type == ElementType.FIGURE:
            fig = element.figure
            if fig is None:
                return Size(_px_to_pt(rect.width), _px_to_pt(rect.height))

            fig_w = fig.get_figwidth() * 72
            fig_h = fig.get_figheight() * 72

            if element.container_width_pct is not None:
                fig_w = _px_to_pt(rect.width) * element.container_width_pct / 100.0
            if element.container_height_pct is not None:
                fig_h = _px_to_pt(rect.height) * element.container_height_pct / 100.0

            return Size(fig_w, fig_h)

        if element.element_type == ElementType.IMAGE:
            img_w_pt = _px_to_pt(rect.width)
            img_h_pt = _px_to_pt(rect.height)
            try:
                from PIL import Image as PILImage
                if os.path.exists(element.source):
                    with PILImage.open(element.source) as img:
                        img_w_px, img_h_px = img.size
                    img_w_pt = img_w_px
                    img_h_pt = img_h_px
            except Exception:
                pass

            img_w_pt *= element.scale
            img_h_pt *= element.scale

            if element.width is not None:
                img_w_pt = element.width
            if element.height is not None:
                img_h_pt = element.height

            panel_w_pt = _px_to_pt(rect.width)
            panel_h_pt = _px_to_pt(rect.height)

            if element.fit_mode.value == "original":
                if img_w_pt > panel_w_pt or img_h_pt > panel_h_pt:
                    aspect = img_w_pt / max(img_h_pt, 1)
                    if img_w_pt / panel_w_pt > img_h_pt / panel_h_pt:
                        img_w_pt = panel_w_pt
                        img_h_pt = img_w_pt / aspect
                    else:
                        img_h_pt = panel_h_pt
                        img_w_pt = img_h_pt * aspect
            elif element.fit_mode.value == "fit_vertical":
                aspect = img_w_pt / max(img_h_pt, 1)
                img_h_pt = panel_h_pt
                img_w_pt = img_h_pt * aspect
            elif element.fit_mode.value == "fit_horizontal":
                aspect = img_w_pt / max(img_h_pt, 1)
                img_w_pt = panel_w_pt
                img_h_pt = img_w_pt / aspect

            return Size(max(img_w_pt, 1), max(img_h_pt, 1))

        return Size(_px_to_pt(rect.width), _px_to_pt(rect.height))

    def _compute_content_rect(
        self,
        rect: Rect,
        element: Any,
        panel: Any,
    ) -> Rect:
        """Compute the rendering rect from element sizing + panel alignment + margin.

        Flow:
          1. Subtract ``panel.margin`` from the cell rect.
          2. Compute the element's natural size (via ``_estimate_content_size``).
          3. Per-axis sizing: if alignment is STRETCH, use the full container
             dimension; otherwise clamp natural size to the container.
          4. Position according to ``panel.h_align`` / ``panel.v_align``.

        ``_estimate_content_size`` returns **points**;  the rect
        dimensions are in pixels, so convert before comparing.
        """
        # 1 — margin
        if panel.margin and any(getattr(panel.margin, a) for a in ("top", "bottom", "left", "right")):
            m = panel.margin
            rect = Rect(
                rect.x + (m.left or 0),
                rect.y + (m.top or 0),
                rect.width - (m.left or 0) - (m.right or 0),
                rect.height - (m.top or 0) - (m.bottom or 0),
            )

        if rect.width <= 0 or rect.height <= 0:
            return Rect(rect.x, rect.y, max(rect.width, 1), max(rect.height, 1))

        nat = self._estimate_content_size(element, rect)
        cw = rect.width if panel.h_align == HAlign.STRETCH else min(_pt_to_px(nat.width), rect.width)
        ch = rect.height if panel.v_align == VAlign.STRETCH else min(_pt_to_px(nat.height), rect.height)

        x = rect.x
        if panel.h_align == HAlign.CENTER:
            x = rect.x + (rect.width - cw) / 2
        elif panel.h_align == HAlign.RIGHT:
            x = rect.x + rect.width - cw

        y = rect.y
        if panel.v_align == VAlign.MIDDLE:
            y = rect.y + (rect.height - ch) / 2
        elif panel.v_align == VAlign.BOTTOM:
            y = rect.y + rect.height - ch

        return Rect(x, y, cw, ch)

    def _render_text(self, element: TextElement, rect: Any, frame_padding: float = 4.0) -> None:
        c = self._canvas
        if c is None:
            return

        theme = getattr(self, '_current_slide', None)
        body = theme.theme.typography.body if theme is not None else None

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
                    tag += f'<font face="{_ps_font_name(run.font_name)}">'
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

            fallback_family = body.family if body is not None else "Helvetica"
            fallback_size = body.size if body is not None else 12.0
            fs = block_size or max(h * 0.12, 6)
            style = ParagraphStyle(
                "CellText",
                fontName=_ps_font_name(block_font or fallback_family),
                fontSize=fs,
                leading=max(fs * 1.2, 8),
                alignment=_align_to_reportlab(block.alignment),
                spaceBefore=1,
                spaceAfter=1,
            )
            p = Paragraph(html, style)
            c.saveState()
            c.translate(x, y)
            fp = frame_padding
            frame = Frame(0, 0, w, h, leftPadding=fp, rightPadding=fp, topPadding=fp, bottomPadding=fp, id="cell")
            frame.addFromList([p], c)
            c.restoreState()

    def _render_image(self, element: ImageElement, rect: Any) -> None:
        c = self._canvas
        if c is None or not element.source or not os.path.exists(element.source):
            return
        x, y, w, h = _rect_to_canvas(self._slide_pt_h, rect.x, rect.y, rect.width, rect.height)
        try:
            c.drawImage(element.source, x, y, width=w, height=h, preserveAspectRatio=True, anchor='sw')
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
                self._render_figure_vector(fig, c, x, y, w, h, element.preserve_aspect)
            else:
                self._render_figure_raster(fig, element, c, x, y, w, h, element.preserve_aspect)
        except Exception:
            pass

    @staticmethod
    def _fitted_size(fig: Any, w: float, h: float) -> tuple[float, float]:
        fig_w_in, fig_h_in = fig.get_size_inches()
        aspect = fig_w_in / max(fig_h_in, 1e-6)
        container_aspect = w / max(h, 1e-6)
        if aspect > container_aspect:
            fw = w
            fh = w / aspect
        else:
            fh = h
            fw = h * aspect
        return fw, fh

    def _render_figure_vector(self, fig: Any, c: Any, x: float, y: float, w: float, h: float,
                               preserve_aspect: bool = False) -> None:
        try:
            import io
            from pdfrw import PdfReader
            from pdfrw.buildxobj import pagexobj
            from pdfrw.toreportlab import makerl
        except ImportError:
            self._render_figure_raster(fig, None, c, x, y, w, h, preserve_aspect)
            return

        old_size = fig.get_size_inches()
        try:
            buf = io.BytesIO()
            if preserve_aspect:
                fw_pt, fh_pt = self._fitted_size(fig, w, h)
                fig.set_size_inches(fw_pt / 72, fh_pt / 72)
                fig.savefig(buf, format="pdf", bbox_inches="tight")
                buf.seek(0)
                reader = PdfReader(buf)
                xobj = pagexobj(reader.pages[0])
                name = makerl(c, xobj)
                bbox = xobj.BBox
                bw_pt = bbox[2] - bbox[0]
                bh_pt = bbox[3] - bbox[1]
                if bw_pt > w or bh_pt > h:
                    scale = min(w / max(bw_pt, 1), h / max(bh_pt, 1))
                    bw_pt *= scale
                    bh_pt *= scale
                dx = x + (w - bw_pt) / 2
                dy = y + (h - bh_pt) / 2
                c.saveState()
                c.translate(dx, dy)
                c.doForm(name)
                c.restoreState()
            else:
                fig.set_size_inches(w / 72, h / 72)
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        fig.tight_layout(pad=0.3)
                except Exception:
                    pass
                fig.savefig(buf, format="pdf")
                buf.seek(0)
                reader = PdfReader(buf)
                xobj = pagexobj(reader.pages[0])
                name = makerl(c, xobj)
                c.saveState()
                c.translate(x, y)
                c.doForm(name)
                c.restoreState()
        except Exception:
            self._render_figure_raster(fig, None, c, x, y, w, h, preserve_aspect)
        finally:
            fig.set_size_inches(old_size)

    def _render_figure_raster(self, fig: Any, element: Any, c: Any, x: float, y: float,
                               w: float, h: float, preserve_aspect: bool = False) -> None:
        dpi = element.dpi if element else 150
        old_size = fig.get_size_inches()
        fd, tmp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            if preserve_aspect:
                fw_pt, fh_pt = self._fitted_size(fig, w, h)
                fig.set_size_inches(fw_pt / 72, fh_pt / 72)
                fig.savefig(tmp_path, dpi=dpi, bbox_inches="tight", format="png")
                try:
                    from PIL import Image as PILImage
                    with PILImage.open(tmp_path) as img:
                        tw_px, th_px = img.size
                    tw_pt = tw_px * 72.0 / dpi
                    th_pt = th_px * 72.0 / dpi
                except Exception:
                    tw_pt, th_pt = fw_pt, fh_pt
                if tw_pt > w or th_pt > h:
                    scale = min(w / max(tw_pt, 1), h / max(th_pt, 1))
                    tw_pt *= scale
                    th_pt *= scale
                dx = x + (w - tw_pt) / 2
                dy = y + (h - th_pt) / 2
                c.drawImage(tmp_path, dx, dy, width=tw_pt, height=th_pt, anchor='sw')
            else:
                fig.set_size_inches(w / 72, h / 72)
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        fig.tight_layout(pad=0.3)
                except Exception:
                    pass
                fig.savefig(tmp_path, dpi=dpi, format="png")
                c.drawImage(tmp_path, x, y, width=w, height=h, anchor='sw')
        finally:
            fig.set_size_inches(old_size)
            self._temp_files.append(tmp_path)

    def _render_table(self, element: TableElement, rect: Any) -> None:
        c = self._canvas
        if c is None or element.data is None:
            return

        ts = self._current_slide.theme.table_style if hasattr(self, '_current_slide') else None

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

            if element.column_widths and len(element.column_widths) == n_cols:
                col_widths = element.column_widths
            else:
                col_w = max(avail_w / max(n_cols, 1), 10)
                col_widths = [col_w] * n_cols

            row_h_pt = max(h / max(n_rows_t, 1), 10)
            body_size = max(min(row_h_pt * 0.3, 8), 3)
            header_size = max(min(row_h_pt * 0.35, 9), 4)

            border_c = colors.Color(0.85, 0.85, 0.85)
            header_bg = colors.Color(0.27, 0.45, 0.77)
            header_text = colors.white
            border_w = 0.5
            if ts is not None:
                border_c = Color.parse(ts.border_color).reportlab_color
                header_bg = Color.parse(ts.header_background).reportlab_color
                header_text = Color.parse(ts.header_text_color).reportlab_color
                border_w = ts.border_width

            cmds: list[tuple] = [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), header_size),
                ("FONTSIZE", (0, 1), (-1, -1), body_size),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), border_w, border_c),
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), header_text),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]

            if element.zebra:
                even_color = colors.Color(0.95, 0.95, 0.95)
                if ts is not None:
                    even_color = Color.parse(ts.even_row_color).reportlab_color
                for i in range(2, len(rows_data), 2):
                    cmds.append(("BACKGROUND", (0, i), (-1, i), even_color))

            t = Table(rows_data, colWidths=col_widths)
            t.setStyle(TableStyle(cmds))
            frame = Frame(x, y, w, h, leftPadding=pad, rightPadding=pad, topPadding=4, bottomPadding=4, id="table_cell")
            frame.addFromList([t], c)
        except Exception:
            import traceback
            traceback.print_exc()

    def _render_tablespec(self, element: Any, rect: Any, panel: Any = None) -> None:
        c = self._canvas
        if c is None:
            return

        spec = element.tablespec
        if spec is None or not spec.columns or not spec.rows:
            return

        try:
            x, y, w, h = _rect_to_canvas(self._slide_pt_h, rect.x, rect.y, rect.width, rect.height)

            panel = panel or Panel()

            ts = spec.style
            sizing = spec.sizing
            num_cols = len(spec.columns)
            num_rows = len(spec.rows)
            hr = ts.header_rows

            pad = 4
            content_w = max(w - 2 * pad, 10)
            avail_h = max(h, 10)

            if sizing.fit_mode == TableFitMode.PERCENT:
                pct_w = max(content_w * sizing.percent_width, 10)
                col_widths, body_fs, header_fs = self._compute_table_layout(
                    spec, pct_w, avail_h,
                )
                frame_w = pct_w + 2 * pad
                if panel.h_align == HAlign.CENTER:
                    frame_x = x + (w - frame_w) / 2
                elif panel.h_align == HAlign.RIGHT:
                    frame_x = x + w - frame_w
                else:
                    frame_x = x
            else:
                col_widths, body_fs, header_fs = self._compute_table_layout(
                    spec, content_w, avail_h,
                )
                frame_w = w
                frame_x = x

            add_header = 1 if ts.header_rows > 0 else 0
            row_offset = add_header
            total_rows = num_rows + row_offset

            data_rows: list[list[str]] = [
                [""] * num_cols for _ in range(total_rows)
            ]

            cmds: list[tuple] = []

            if add_header:
                for ci in range(num_cols):
                    data_rows[0][ci] = spec.columns[ci].label or spec.columns[ci].name

            self._build_tablespec_cells(
                spec, data_rows, cmds, num_cols, num_rows, hr,
                body_fs, header_fs, ts, row_offset=row_offset,
            )

            if add_header:
                hl_font = _resolve_font_name(
                    ts.font_name or "Helvetica", True, False,
                )
                hl_leading = max(header_fs * ts.line_height, 8)
                cmds.append(("FONTNAME", (0, 0), (num_cols - 1, 0), hl_font))
                cmds.append(("FONTSIZE", (0, 0), (num_cols - 1, 0), header_fs))
                cmds.append(("LEADING", (0, 0), (num_cols - 1, 0), hl_leading))
                cmds.append(("ALIGN", (0, 0), (num_cols - 1, 0), "CENTER"))
                cmds.append(("VALIGN", (0, 0), (num_cols - 1, 0), "MIDDLE"))
                top_pad, bot_pad, left_pad, right_pad = _cell_padding(ts.padding)
                cmds.append(("TOPPADDING", (0, 0), (num_cols - 1, 0), top_pad))
                cmds.append(("BOTTOMPADDING", (0, 0), (num_cols - 1, 0), bot_pad))
                cmds.append(("LEFTPADDING", (0, 0), (num_cols - 1, 0), left_pad))
                cmds.append(("RIGHTPADDING", (0, 0), (num_cols - 1, 0), right_pad))

            t = Table(data_rows, colWidths=col_widths)
            t.setStyle(TableStyle(cmds))

            # Wrap the table to get its actual rendered height
            table_w, table_h = t.wrap(content_w, h)

            # Natural content height for vertical alignment
            if panel.v_align == VAlign.BOTTOM:
                top_padding = max(h - table_h, 0)
                bottom_padding = 0
            elif panel.v_align == VAlign.MIDDLE:
                excess = max(h - table_h, 0)
                top_padding = excess / 2
                bottom_padding = excess / 2
            else:
                top_padding = 0
                bottom_padding = max(h - table_h, 0)

            frame = Frame(
                frame_x, y, frame_w, h,
                leftPadding=pad, rightPadding=pad,
                topPadding=top_padding, bottomPadding=bottom_padding,
                id="tablespec_cell",
            )
            frame.addFromList([t], c)
        except Exception:
            import traceback
            traceback.print_exc()

    def _compute_table_layout(
        self,
        spec: Any,
        avail_w: float,
        avail_h: float,
    ) -> tuple[list[float], float, float]:
        """Compute column widths and font sizes from the sizing mode.

        Returns:
            Tuple of (col_widths, body_font_size, header_font_size).
        """
        ts = spec.style
        sizing = spec.sizing
        num_rows = len(spec.rows)
        distrib = sizing.column_distrib

        body_fs = ts.font_size
        header_fs = ts.header_font_size
        min_fs = sizing.min_font_size if sizing.min_font_size is not None else ts.min_font_size
        line_h = ts.line_height

        pad = ts.padding
        pad_top = pad if isinstance(pad, (int, float)) else (pad.top if pad else 4)
        pad_bot = pad if isinstance(pad, (int, float)) else (pad.bottom if pad else 4)
        pad_h = pad_top + pad_bot

        if sizing.fit_mode == TableFitMode.SHRINK_FONT:
            if distrib == ColumnDistrib.EQUAL:
                raise ValueError("ColumnDistrib.EQUAL is not supported with SHRINK_FONT mode")

            body_fs, header_fs = self._shrink_font(
                spec, body_fs, header_fs, min_fs, line_h, pad_h,
                avail_w, avail_h, pad,
            )

        # Build column widths according to distribution mode
        if distrib == ColumnDistrib.EQUAL:
            col_w = max(avail_w / max(len(spec.columns), 1), 8)
            col_widths = [col_w] * len(spec.columns)
        elif distrib == ColumnDistrib.FIXED:
            col_widths = []
            fixed_total = 0.0
            flexible = 0
            for col in spec.columns:
                if col.width:
                    cw = max(_px_to_pt(col.width) if col.width < 100 else col.width, 8)
                    col_widths.append(cw)
                    fixed_total += cw
                else:
                    col_widths.append(None)
                    flexible += 1
            remaining = max(avail_w - fixed_total, 0)
            flex_w = remaining / max(flexible, 1) if flexible else 0
            col_widths = [w if w is not None else flex_w for w in col_widths]
        else:
            # CONTENT — content-aware proportional distribution
            font_name = ts.font_name
            nat_widths = self._measure_column_widths(
                spec, font_name, body_fs, header_fs, pad,
            )
            total_nat = sum(nat_widths)
            if total_nat > 0:
                scale = avail_w / total_nat
                col_widths = [max(w * scale, 8) for w in nat_widths]
            else:
                col_widths = [max(avail_w / max(len(spec.columns), 1), 8)] * len(spec.columns)

        return col_widths, body_fs, header_fs

    def _shrink_font(
        self,
        spec: Any,
        body_fs: float,
        header_fs: float,
        min_fs: float,
        line_h: float,
        pad_h: float,
        avail_w: float,
        avail_h: float,
        pad: Any,
    ) -> tuple[float, float]:
        """Reduce font sizes if content overflows available space."""
        font_name = spec.style.font_name
        num_rows = len(spec.rows)

        nat_widths = self._measure_column_widths(
            spec, font_name, body_fs, header_fs, pad,
        )
        total_nat = sum(nat_widths)
        row_h = body_fs * line_h + pad_h
        total_h = row_h * num_rows

        if total_nat > avail_w or total_h > avail_h:
            w_ratio = avail_w / total_nat if total_nat > 0 else 1
            h_ratio = avail_h / total_h if total_h > 0 else 1
            ratio = min(w_ratio, h_ratio)
            body_fs = max(body_fs * ratio, min_fs)
            header_fs = max(header_fs * ratio, min_fs)

        return body_fs, header_fs

    def _measure_column_widths(
        self,
        spec: Any,
        font_name: str,
        body_fs: float,
        header_fs: float,
        pad: Any,
    ) -> list[float]:
        """Measure the widest text per column at the given font sizes.

        Returns unscaled natural widths (points).
        """
        pad_left = pad if isinstance(pad, (int, float)) else (pad.left if pad else 4)
        pad_right = pad if isinstance(pad, (int, float)) else (pad.right if pad else 4)
        pad_w = pad_left + pad_right

        col_widths: list[float] = []
        for col_idx, col in enumerate(spec.columns):
            max_w = 0.0
            for r_idx, row in enumerate(spec.rows):
                if col_idx >= len(row.cells):
                    continue
                is_header = r_idx < spec.style.header_rows
                fs = header_fs if is_header else body_fs

                cell = row.cells[col_idx]
                display = cell.text if cell.text is not None else str(cell.value or "")
                try:
                    tw = stringWidth(display, font_name, fs)
                except Exception:
                    tw = 0
                max_w = max(max_w, tw)

            base = max_w + pad_w

            if col.width:
                base = _px_to_pt(col.width) if col.width < 100 else col.width
            elif col.width_ratio:
                base *= col.width_ratio

            col_widths.append(max(base, 10))

        return col_widths

    def _build_tablespec_cells(
        self,
        spec: Any,
        data_rows: list[list[str]],
        cmds: list[tuple],
        num_cols: int,
        num_rows: int,
        header_rows: int,
        body_size: float,
        header_size: float,
        ts: Any,
        row_offset: int = 0,
    ) -> None:
        """Fill data_rows and cmds from the TableSpec style cascade."""
        from reportlab.lib import colors as rl_colors

        total_rows = num_rows + row_offset
        occupied = [[False] * num_cols for _ in range(total_rows)]

        has_auto_header = row_offset > 0
        for r in range(num_rows):
            tr = r + row_offset
            row = spec.rows[r]
            is_header = False if has_auto_header else (r < header_rows)
            font_size = header_size if is_header else body_size
            grid_c = 0
            cell_idx = 0

            while grid_c < num_cols and cell_idx < len(row.cells):
                if occupied[tr][grid_c]:
                    grid_c += 1
                    cell_idx += 1
                    continue

                cell = row.cells[cell_idx]
                colspan = max(cell.colspan, 1)
                rowspan = max(cell.rowspan, 1)
                c_end = min(grid_c + colspan - 1, num_cols - 1)

                resolved = spec.resolve_cell_style(r, grid_c, cell_idx=cell_idx)

                display = cell.text
                if display is None:
                    col = spec.columns[grid_c] if grid_c < len(spec.columns) else None
                    if col and col.formatter:
                        display = col.formatter(cell.value)
                    elif col and col.format:
                        from reporting.tablespec.formatters import apply_format
                        try:
                            display = apply_format(cell.value, col.format)
                        except Exception:
                            display = str(cell.value) if cell.value is not None else ""
                    else:
                        display = str(cell.value) if cell.value is not None else ""
                data_rows[tr][grid_c] = display

                rl_font_name = _resolve_font_name(
                    resolved.font_name or "Helvetica",
                    resolved.bold,
                    resolved.italic,
                )
                rl_font_size = resolved.font_size if resolved.font_size is not None else font_size
                rl_font_size = max(rl_font_size, 3)

                rl_leading = max(rl_font_size * ts.line_height, 8)
                cmds.append(("FONTNAME", (grid_c, tr), (c_end, tr), rl_font_name))
                cmds.append(("FONTSIZE", (grid_c, tr), (c_end, tr), rl_font_size))
                cmds.append(("LEADING", (grid_c, tr), (c_end, tr), rl_leading))
                cmds.append(("ALIGN", (grid_c, tr), (c_end, tr), _h_align_to_str(resolved.align_h)))
                cmds.append(("VALIGN", (grid_c, tr), (c_end, tr), _v_align_to_str(resolved.align_v)))

                top_pad, bot_pad, left_pad, right_pad = _cell_padding(resolved.padding)
                cmds.append(("TOPPADDING", (grid_c, tr), (c_end, tr), top_pad))
                cmds.append(("BOTTOMPADDING", (grid_c, tr), (c_end, tr), bot_pad))
                cmds.append(("LEFTPADDING", (grid_c, tr), (c_end, tr), left_pad))
                cmds.append(("RIGHTPADDING", (grid_c, tr), (c_end, tr), right_pad))

                if resolved.background_color:
                    try:
                        bg = Color.parse(resolved.background_color).reportlab_color
                        cmds.append(("BACKGROUND", (grid_c, tr), (c_end, tr), bg))
                    except Exception:
                        pass

                if resolved.text_color:
                    try:
                        tc = Color.parse(resolved.text_color).reportlab_color
                        cmds.append(("TEXTCOLOR", (grid_c, tr), (c_end, tr), tc))
                    except Exception:
                        pass

                if colspan > 1 or rowspan > 1:
                    r2 = min(tr + rowspan - 1, total_rows - 1)
                    cmds.append(("SPAN", (grid_c, tr), (c_end, r2)))
                    for span_r in range(tr, r2 + 1):
                        for span_c in range(grid_c, c_end + 1):
                            occupied[span_r][span_c] = True
                    occupied[tr][grid_c] = False

                grid_c += colspan
                cell_idx += 1

            if not is_header and ts.zebra:
                try:
                    row_bg = ts.even_row_color if r % 2 == 0 else ts.odd_row_color
                    if row_bg:
                        zc = Color.parse(row_bg).reportlab_color
                        cmds.append(("BACKGROUND", (0, tr), (num_cols - 1, tr), zc))
                except Exception:
                    pass

        bc = Color.parse(ts.border_color).reportlab_color
        bw = max(ts.border_width, 0.1)
        cmds.insert(0, ("GRID", (0, 0), (num_cols - 1, total_rows - 1), bw, bc))

        if has_auto_header:
            hr_indices = range(row_offset)
        else:
            hr_indices = range(header_rows)

        for thr in hr_indices:
            hb = Color.parse(ts.header_background).reportlab_color
            ht = Color.parse(ts.header_text_color).reportlab_color
            cmds.append(("BACKGROUND", (0, thr), (num_cols - 1, thr), hb))
            cmds.append(("TEXTCOLOR", (0, thr), (num_cols - 1, thr), ht))



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
                self._render_element(inner_el, abs_rect, panel=cell.panel)

    def render_panel(self, panel: object, rect: object) -> object:
        """Render a single panel (no-op in PDF renderer).

        Panels are rendered as part of slide rendering via
        ``_render_element``.  This method exists for interface
        conformance.

        Args:
            panel: A ``Panel`` instance.
            rect: A ``Rect`` bounding box.

        Returns:
            ``None``.
        """
        return None
