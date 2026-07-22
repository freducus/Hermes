"""HTML renderer — generates HTML/CSS output."""

from __future__ import annotations

import base64
import io
import mimetypes
import os
import re
import tempfile
from typing import TYPE_CHECKING, Any, Optional

from reporting.elements.base import ElementType
from reporting.elements.figure import FigureElement
from reporting.elements.text import TextElement, TextAlignment
from reporting.elements.image import ImageElement
from reporting.elements.table import TableElement
from reporting.elements.tablespec_element import TableSpecElement
from reporting.layout.geometry import Edges, Rect, Size
from reporting.layout.panel import HAlign, VAlign
from reporting.renderers.base import BaseRenderer
from reporting.styles.colors import Color
from reporting.tablespec.sizing import TableFitMode
from reporting.footer_config import FooterPanel
from reporting.background import Background, BackgroundType

if TYPE_CHECKING:
    from reporting.document import Document
    from reporting.slide import Slide


class HTMLRenderer(BaseRenderer):
    """Render a report to a standalone HTML file with CSS styling.

    Each ``Slide`` becomes a ``<div class="slide">`` with absolute-
    positioned cells.  Images and figure PNGs are embedded as
    base64 data URIs for portability.

    Args:
        standalone: If ``True`` (default), generates a complete
            HTML document with ``<!DOCTYPE html>``, ``<head>``,
            and inline CSS.  If ``False``, returns only the
            slide ``<div>`` fragments for embedding.

    Example::

        from reporting.document import Document
        from reporting.renderers.html.renderer import HTMLRenderer

        doc = Document()
        slide = doc.new_slide("Hello")
        slide.grid_layout(1, 1)
        slide[0, 0].text("Hello, HTML!")

        renderer = HTMLRenderer()
        renderer.render_document(doc, "output.html")
    """
    def __init__(self, standalone: bool = True) -> None:
        self.standalone = standalone
        self._body_parts: list[str] = []
        self._page_num: int = 1
        self._total_pages: int = 1

    def render_document(self, document: "Document", output_path: str) -> None:
        slides_html: list[str] = []
        total = len(document.slides)
        for i, slide in enumerate(document.slides):
            self._page_num = i + 1
            self._total_pages = total
            slides_html.append(self._render_slide_html(slide))

        slides_content = "\n".join(slides_html)

        # Derive theme from first slide or document default
        theme = document.slides[0].theme if document.slides else document.theme
        pal = theme.palette

        if self.standalone:
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{document.title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: {pal.background.css}; font-family: {theme.typography.body.family}, sans-serif; }}
.slide {{ width: 960px; height: 540px; margin: 20px auto; background: {pal.background.css};
         box-shadow: 0 4px 12px rgba(0,0,0,0.3); position: relative; overflow: hidden; }}
.title-panel {{ position: absolute; top: 0; left: 0; width: 100%;
                border-bottom: 1px solid {pal.border.css}; overflow: hidden; }}
.title-panel.beside {{ display: flex; justify-content: space-between; align-items: center; }}
.title-panel h1 {{ font-size: 20px; color: {pal.primary.css}; margin: 0; }}
.title-panel p {{ font-size: 11px; color: {pal.text_secondary.css}; margin: 2px 0 0 0; }}
.title-panel.beside p {{ margin: 0; text-align: right; }}
.slide-content {{ position: absolute; left: 0; width: 100%; bottom: 0; }}
.cell {{ position: absolute; overflow: hidden; padding: 4px; }}
</style>
</head>
<body>
{slides_content}
</body>
</html>"""
        else:
            html = slides_content

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def _render_slide_html(self, slide: Slide) -> str:
        self._current_slide = slide
        slide_bg_style = self._background_css(slide)
        slide_extra = f'style="{slide_bg_style}"' if slide_bg_style else ""

        tp = slide.title_panel

        if tp.enabled:
            t = slide.title
            s = slide.subtitle
            th = slide.title_panel.height

            h1_weight = "bold" if t.bold else "normal"
            h1_style = (f"font-size:{t.font_size}px;color:{Color.parse(t.color).css};"
                        f"font-weight:{h1_weight};font-family:{t.font_name};"
                        f"text-align:{t.alignment.value}")

            is_beside = (
                s
                and tp.subtitle_placement.value == "beside"
            )

            panel_cls = "title-panel beside" if is_beside else "title-panel"
            panel_style = f"height:{th}px;padding:{tp.padding.top}px {tp.padding.right}px {tp.padding.bottom}px {tp.padding.left}px;"

            if is_beside:
                sub_w = tp.subtitle_width_ratio
                sub_weight = "bold" if s.bold else "normal"
                sub_style = (f"font-size:{s.font_size}px;color:{Color.parse(s.color).css};"
                             f"font-weight:{sub_weight};font-family:{s.font_name};"
                             f"text-align:{s.alignment.value};width:{sub_w*100}%")
                title_html = (
                    f"""<div class="{panel_cls}" style="{panel_style}">"""
                    f"""<h1 style="{h1_style}">{t}</h1>"""
                    f"""<p style="{sub_style}">{s}</p>"""
                    f"""</div>"""
                )
            else:
                title_html = f"""<div class="{panel_cls}" style="{panel_style}"><h1 style="{h1_style}">{t}</h1>"""
                if s:
                    sub_weight = "bold" if s.bold else "normal"
                    sub_style = (f"font-size:{s.font_size}px;color:{Color.parse(s.color).css};"
                                 f"font-weight:{sub_weight};font-family:{s.font_name};"
                                 f"text-align:{s.alignment.value}")
                    title_html += f"<p style=\"{sub_style}\">{s}</p>"
                if tp.show_separator:
                    title_html += (f"<hr style=\"border:none;border-top:{tp.separator_width}px solid "
                                   f"{Color.parse(tp.separator_color).css};margin-top:{tp.separator_margin}px;margin-bottom:0\">")
                title_html += "</div>"
        else:
            title_html = ""
            th = 0

        content_parts: list[str] = []

        if slide._grid:
            cell_rects = slide.get_cell_rects()
            for r in range(slide._grid.rows):
                for c in range(slide._grid.cols):
                    cell = slide._grid.cells[r][c]
                    rect = cell_rects[r][c]
                    bg = cell.panel.background_color
                    element = cell.element
                    if element is None:
                        style = self._cell_style(rect, bg)
                        content_parts.append(f"""<div class="cell" style="{style}"></div>""")
                        continue
                    element_html = self._render_element_html(element, rect, bg, panel=cell.panel)
                    content_parts.append(element_html)

        cells_content = "\n".join(content_parts)

        # Footer rendering
        footer_html = ""
        fh = slide.footer_panel.height
        if fh > 0 and slide.footer_panel.enabled:
            slide._populate_footer_grid()
            fp = slide.footer_panel
            pad = fp.padding
            offset_y_px = slide.height - fh + pad.top
            footer_parts: list[str] = []
            cell_rects = slide.get_footer_cell_rects()
            for r in range(slide._footer_grid.rows):
                for c2 in range(slide._footer_grid.cols):
                    cell = slide._footer_grid.cells[r][c2]
                    rect = cell_rects[r][c2]
                    element = cell.element
                    if element is None:
                        continue
                    # Replace auto placeholders
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
                            for block in element.blocks:
                                for run in block.runs:
                                    run.text = run.text.replace("{page}", str(self._page_num))
                                    run.text = run.text.replace("{total}", str(self._total_pages))
                    adj = Rect(
                        rect.x + pad.left,
                        rect.y + offset_y_px,
                        rect.width,
                        rect.height,
                    )
                    el_html = self._render_element_html(element, adj, panel=cell.panel)
                    footer_parts.append(el_html)
            if footer_parts:
                sep_html = ""
                if fp.show_separator:
                    sep_color = Color.parse(fp.separator_color).css
                    sep_x = pad.left
                    sep_w = f"calc(100% - {pad.left + pad.right}px)"
                    sep_y = offset_y_px - pad.top  # just above footer content
                    sep_html = f'<hr style="border:none;border-top:{fp.separator_width}px solid {sep_color};position:absolute;left:{sep_x}px;top:{sep_y}px;width:{sep_w};margin:0">'
                footer_html = sep_html + "".join(footer_parts)

        return f"""<div class="slide" {slide_extra}>
  {title_html}
  <div class="slide-content" style="top:{th}px;bottom:{fh}px">
    {cells_content}
  </div>
  {footer_html if fh > 0 else ""}
</div>"""

    def _background_css(self, slide: Slide) -> str:
        bg = getattr(slide, "background", None)
        if bg is None:
            return ""
        if bg.type == BackgroundType.SOLID:
            return f"background:{Color.parse(bg.color).css};"
        elif bg.type == BackgroundType.GRADIENT:
            return (f"background:linear-gradient({bg.angle}deg,"
                    f"{Color.parse(bg.start_color).css},{Color.parse(bg.end_color).css});")
        elif bg.type == BackgroundType.IMAGE:
            url = self._background_image_url(bg.source)
            if bg.opacity < 1.0 and url.startswith("data:"):
                return f"background:linear-gradient(rgba(255,255,255,{1-bg.opacity:.2f}),rgba(255,255,255,{1-bg.opacity:.2f})),{url} center/cover no-repeat;"
            return f"background:{url} center/cover no-repeat;"
        return ""

    @staticmethod
    def _background_image_url(source: str) -> str:
        if not os.path.exists(source):
            return ""
        try:
            with open(source, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("ascii")
            mime = mimetypes.guess_type(source)[0] or "image/png"
            return f"url('data:{mime};base64,{b64}')"
        except Exception:
            return ""

    def _cell_style(self, rect: Any, bg_color: Optional[str] = None) -> str:
        parts = [
            f"left:{rect.x:.1f}px; top:{rect.y:.1f}px;",
            f"width:{rect.width:.1f}px; height:{rect.height:.1f}px;",
        ]
        if bg_color:
            parts.append(f"background-color:{Color.parse(bg_color).css};")
        return " ".join(parts)

    def _render_element_html(self, element: Any, rect: Any, bg_color: Optional[str] = None,
                             panel: Optional[Any] = None) -> str:
        style = self._cell_style(rect, bg_color)
        if panel and (panel.h_align != HAlign.STRETCH or panel.v_align != VAlign.STRETCH):
            style = self._align_style(style, panel)

        if element.element_type == ElementType.TEXT:
            return self._render_text_html(element, style)
        elif element.element_type == ElementType.IMAGE:
            return self._render_image_html(element, style)
        elif element.element_type == ElementType.FIGURE:
            return self._render_figure_html(element, style)
        elif element.element_type == ElementType.TABLE:
            return self._render_table_html(element, style)
        elif element.element_type == ElementType.TABLESPEC:
            return self._render_tablespec_html(element, style)
        elif element.element_type == ElementType.CONTAINER:
            return self._render_container_html(element, rect, panel=panel)
        return f"""<div class="cell" style="{style}"></div>"""

    @staticmethod
    def _align_style(style: str, panel: Any) -> str:
        """Inject CSS flexbox alignment into the cell style."""
        align_items = ""
        justify = ""
        if panel.h_align == HAlign.CENTER:
            justify = "justify-content:center;"
        elif panel.h_align == HAlign.LEFT:
            justify = "justify-content:flex-start;"
        elif panel.h_align == HAlign.RIGHT:
            justify = "justify-content:flex-end;"
        if panel.v_align == VAlign.MIDDLE:
            align_items = "align-items:center;"
        elif panel.v_align == VAlign.TOP:
            align_items = "align-items:flex-start;"
        elif panel.v_align == VAlign.BOTTOM:
            align_items = "align-items:flex-end;"
        if justify or align_items:
            return f"display:flex;{align_items}{justify}{style}"
        return style

    def _render_text_html(self, element: TextElement, style: str) -> str:
        from reporting.styles.typography import resolve_style_name
        theme = getattr(self, '_current_slide', None)
        resolved = None
        if "style" in element.properties and theme is not None:
            resolved = resolve_style_name(element.properties["style"], theme.theme.typography)

        parts: list[str] = []
        for block in element.blocks:
            text_parts: list[str] = []
            for run in block.runs:
                span_style = ""
                if run.bold:
                    span_style += "font-weight:bold;"
                if run.italic:
                    span_style += "font-style:italic;"
                if run.color:
                    span_style += f"color:{Color.parse(run.color).css};"
                fs = run.size or (resolved.size if resolved else None)
                if fs:
                    span_style += f"font-size:{fs}px;"
                fn = run.font_name or (resolved.family if resolved else None)
                if fn:
                    span_style += f"font-family:{fn};"
                text = run.text.replace("\n", "<br/>")
                text_parts.append(f'<span style="{span_style}">{text}</span>')
            text_html = "".join(text_parts)
            align_class = f"text-{block.alignment.value}"
            parts.append(f'<div class="text-block {align_class}" style="text-align:{block.alignment.value}">{text_html}</div>')
        content = "".join(parts)
        return f"""<div class="cell" style="{style}">{content}</div>"""

    def _render_image_html(self, element: ImageElement, style: str) -> str:
        if not element.source or not os.path.exists(element.source):
            return f"""<div class="cell" style="{style}"><p>Image not found: {element.source}</p></div>"""
        obj_fit = "contain" if element.preserve_aspect else "fill"
        return f"""<div class="cell" style="{style}"><img src="{element.source}" style="width:100%;height:100%;object-fit:{obj_fit}" alt="{element.alt_text}"></div>"""

    def _render_figure_html(self, element: FigureElement, style: str) -> str:
        if element.figure is None:
            return f"""<div class="cell" style="{style}"></div>"""
        try:
            fig = element.figure
            match = re.search(r"width:([\d.]+)px", style)
            cell_w = float(match.group(1)) if match else 400
            match = re.search(r"height:([\d.]+)px", style)
            cell_h = float(match.group(1)) if match else 300

            old_size = fig.get_size_inches()
            fig.set_size_inches(cell_w / element.dpi, cell_h / element.dpi)

            if element.format == "svg":
                buf = io.BytesIO()
                fig.savefig(buf, dpi=element.dpi, bbox_inches=element.bbox_inches, format="svg")
                fig.set_size_inches(old_size)
                buf.seek(0)
                svg_raw = buf.read().decode("utf-8")
                return f"""<div class="cell" style="{style}">{svg_raw}</div>"""
            else:
                buf = io.BytesIO()
                fig.savefig(buf, dpi=element.dpi, bbox_inches=element.bbox_inches, format="png")
                fig.set_size_inches(old_size)
                buf.seek(0)
                b64 = base64.b64encode(buf.read()).decode("utf-8")
                return f"""<div class="cell" style="{style}"><img src="data:image/png;base64,{b64}" style="width:100%;height:100%;object-fit:contain"></div>"""
        except Exception:
            return f"""<div class="cell" style="{style}"></div>"""

    def _render_table_html(self, element: TableElement, style: str) -> str:
        if element.data is None:
            return f"""<div class="cell" style="{style}"></div>"""

        theme = getattr(self, '_current_slide', None)
        ts = None

        header_bg = Color.parse(ts.header_background).css if ts else "#4472C4"
        header_fg = Color.parse(ts.header_text_color).css if ts else "#ffffff"
        border_c = Color.parse(ts.border_color).css if ts else "#d9d9d9"
        body_fs = f"{ts.font_size}pt" if ts else "10px"

        df = element.data
        if element.include_index:
            df = df.reset_index()

        zebra_style = ""
        if element.zebra:
            even_bg = Color.parse(ts.even_row_color).css if ts else "#f3f3f3"
            odd_bg = Color.parse(ts.odd_row_color).css if ts else "#ffffff"
            zebra_style = f"""<style>
tr:nth-child(even) {{ background-color: {even_bg}; }}
tr:nth-child(odd) {{ background-color: {odd_bg}; }}
thead th {{ background-color: {header_bg}; color: {header_fg}; }}
</style>"""

        cell_style = f"padding:4px;border:1px solid {border_c};text-align:center"
        html = f"""<div class="cell" style="{style};overflow:auto">{zebra_style}
<table style="width:100%;border-collapse:collapse;font-size:{body_fs}">
<thead><tr>"""
        for col in df.columns:
            html += f"<th style='{cell_style}'>{col}</th>"
        html += "</tr></thead><tbody>"
        for _, row in df.iterrows():
            html += "<tr>"
            for val in row:
                html += f"<td style='{cell_style}'>{val}</td>"
            html += "</tr>"
        html += "</tbody></table></div>"
        return html

    def _render_tablespec_html(self, element: Any, style: str) -> str:
        spec = element.tablespec
        if spec is None or not spec.columns or not spec.rows:
            return f"""<div class="cell" style="{style}"></div>"""

        num_cols = len(spec.columns)
        num_rows = len(spec.rows)
        ts = spec.style
        hr = ts.header_rows

        occupied = [[False] * num_cols for _ in range(num_rows)]

        sizing = spec.sizing
        table_width_css = "100%"
        if sizing.fit_mode == TableFitMode.PERCENT:
            table_width_css = f"{sizing.percent_width * 100:.0f}%"
        fs_css = f"{ts.font_size}pt"
        table_css = f"width:{table_width_css};border-collapse:collapse;font-size:{fs_css}"
        if ts.zebra:
            table_css += ";background-color:#FFFFFF"

        parts: list[str] = []
        parts.append(f"""<div class="cell" style="{style};overflow:auto"><table style="{table_css}">""")

        parts.append("<thead>")
        for hr_idx in range(min(hr, num_rows)):
            row = spec.rows[hr_idx]
            parts.append("<tr>")
            grid_c = 0
            for cell_idx in range(len(row.cells)):
                if grid_c >= num_cols:
                    break
                while grid_c < num_cols and occupied[hr_idx][grid_c]:
                    grid_c += 1
                if grid_c >= num_cols:
                    break

                cell = row.cells[cell_idx]
                colspan = max(cell.colspan, 1)
                rowspan = max(cell.rowspan, 1)
                c_end = min(grid_c + colspan - 1, num_cols - 1)

                resolved = spec.resolve_cell_style(hr_idx, grid_c, cell_idx=cell_idx) if cell else None

                display = ""
                if cell:
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

                td_s = self._cell_css(resolved, is_header=True, default_bg=ts.header_background, default_color=ts.header_text_color, border_color=ts.border_color) if resolved else f"padding:4px;border:1px solid {ts.border_color};text-align:center;background-color:" + ts.header_background + ";color:" + ts.header_text_color

                cs = f' colspan="{colspan}"' if colspan > 1 else ""
                rs = f' rowspan="{rowspan}"' if rowspan > 1 else ""
                parts.append(f'<th{cs}{rs} style="{td_s}">{display}</th>')

                if colspan > 1 or rowspan > 1:
                    r2 = min(hr_idx + rowspan - 1, num_rows - 1)
                    for span_r in range(hr_idx, r2 + 1):
                        for span_c in range(grid_c, c_end + 1):
                            occupied[span_r][span_c] = True
                    occupied[hr_idx][grid_c] = False

                grid_c += colspan
            parts.append("</tr>")
        parts.append("</thead><tbody>")

        for r in range(hr, num_rows):
            row = spec.rows[r]
            parts.append("<tr>")
            grid_c = 0
            for cell_idx in range(len(row.cells)):
                if grid_c >= num_cols:
                    break
                while grid_c < num_cols and occupied[r][grid_c]:
                    grid_c += 1
                if grid_c >= num_cols:
                    break

                cell = row.cells[cell_idx]
                colspan = max(cell.colspan, 1)
                rowspan = max(cell.rowspan, 1)
                c_end = min(grid_c + colspan - 1, num_cols - 1)

                resolved = spec.resolve_cell_style(r, grid_c, cell_idx=cell_idx) if cell else None

                display = ""
                if cell:
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

                td_s = self._cell_css(resolved, is_header=False, zebra=ts.zebra, row_idx=r, even_color=ts.even_row_color, odd_color=ts.odd_row_color, border_color=ts.border_color) if resolved else f"padding:4px;border:1px solid {ts.border_color};text-align:center"

                cs = f' colspan="{colspan}"' if colspan > 1 else ""
                rs = f' rowspan="{rowspan}"' if rowspan > 1 else ""
                parts.append(f'<td{cs}{rs} style="{td_s}">{display}</td>')

                if colspan > 1 or rowspan > 1:
                    r2 = min(r + rowspan - 1, num_rows - 1)
                    for span_r in range(r, r2 + 1):
                        for span_c in range(grid_c, c_end + 1):
                            occupied[span_r][span_c] = True
                    occupied[r][grid_c] = False

                grid_c += colspan
            parts.append("</tr>")
        parts.append("</tbody></table></div>")
        return "".join(parts)

    def _cell_css(
        self,
        resolved: Any,
        is_header: bool = False,
        default_bg: str = "#4472C4",
        default_color: str = "#FFFFFF",
        zebra: bool = False,
        row_idx: int = 0,
        even_color: str = "#F3F3F3",
        odd_color: str = "#FFFFFF",
        border_color: str = "#d9d9d9",
    ) -> str:
        """Build inline CSS for a single cell from its resolved CellStyle."""
        css_parts: list[str] = []

        padding_val = resolved.padding
        if padding_val is not None:
            css_parts.append(f"padding:{_css_padding(padding_val)}")
        else:
            css_parts.append("padding:4px")

        bc = resolved.border_color or border_color
        bw = resolved.border_width or 1
        css_parts.append(f"border:{bw}px solid {Color.parse(bc).css}")

        if is_header:
            bg = resolved.background_color or default_bg
            tc = resolved.text_color or default_color
            css_parts.append(f"background-color:{Color.parse(bg).css}")
            css_parts.append(f"color:{Color.parse(tc).css}")
        else:
            if resolved.background_color:
                css_parts.append(f"background-color:{Color.parse(resolved.background_color).css}")
            elif zebra:
                bg = even_color if row_idx % 2 == 0 else odd_color
                css_parts.append(f"background-color:{Color.parse(bg).css}")
            if resolved.text_color:
                css_parts.append(f"color:{Color.parse(resolved.text_color).css}")

        ah = resolved.align_h or ""
        if ah:
            css_parts.append(f"text-align:{ah}")
        else:
            css_parts.append("text-align:center")

        av = resolved.align_v or ""
        if av:
            css_parts.append(f"vertical-align:{av}")
        else:
            css_parts.append("vertical-align:middle")

        if resolved.bold:
            css_parts.append("font-weight:bold")
        if resolved.italic:
            css_parts.append("font-style:italic")
        if resolved.underline:
            css_parts.append("text-decoration:underline")
        if resolved.font_size:
            css_parts.append(f"font-size:{resolved.font_size}pt")

        return ";".join(css_parts)

    def _render_container_html(self, element: Any, parent_rect: Any,
                               panel: Optional[Any] = None) -> str:
        inner = element.grid
        if inner is None:
            return ""
        parts: list[str] = []
        inner_size, inner_rects = inner.layout(Size(parent_rect.width, parent_rect.height))
        for r in range(inner.rows):
            for c in range(inner.cols):
                cell = inner.cells[r][c]
                cell_rect = inner_rects[r][c]
                abs_rect = Rect(
                    x=parent_rect.x + cell_rect.x,
                    y=parent_rect.y + cell_rect.y,
                    width=cell_rect.width,
                    height=cell_rect.height,
                )
                bg = cell.panel.background_color
                inner_el = cell.element
                if inner_el is None:
                    style = self._cell_style(abs_rect, bg)
                    parts.append(f"""<div class="cell" style="{style}"></div>""")
                else:
                    parts.append(self._render_element_html(inner_el, abs_rect, bg, panel=cell.panel))
        return "\n".join(parts)

    def render_slide(self, slide: object) -> object:
        """Render a single slide as HTML.

        Args:
            slide: A ``Slide`` instance.

        Returns:
            The HTML string for the slide.
        """
        return self._render_slide_html(slide)

    def render_panel(self, panel: object, rect: object) -> object:
        """Render a panel (no-op in HTML renderer).

        Args:
            panel: A ``Panel`` instance.
            rect: A ``Rect`` bounding box.

        Returns:
            ``None``.
        """
        return None


def _css_padding(padding: Any) -> str:
    if padding is None:
        return "4px"
    if isinstance(padding, (int, float)):
        return f"{padding}px"
    top = getattr(padding, "top", 4) or 4
    right = getattr(padding, "right", 4) or 4
    bottom = getattr(padding, "bottom", 4) or 4
    left = getattr(padding, "left", 4) or 4
    return f"{top}px {right}px {bottom}px {left}px"
