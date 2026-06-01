"""HTML renderer — generates HTML/CSS output."""

from __future__ import annotations

import base64
import io
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
from reporting.layout.geometry import Rect, Size
from reporting.renderers.base import BaseRenderer

if TYPE_CHECKING:
    from reporting.document import Document
    from reporting.slide import Slide


class HTMLRenderer(BaseRenderer):
    def __init__(self, standalone: bool = True) -> None:
        self.standalone = standalone
        self._body_parts: list[str] = []

    def render_document(self, document: "Document", output_path: str) -> None:
        slides_html: list[str] = []
        for slide in document.slides:
            slides_html.append(self._render_slide_html(slide))

        slides_content = "\n".join(slides_html)

        if self.standalone:
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{document.title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #333; font-family: Arial, sans-serif; }}
.slide {{ width: 960px; height: 540px; margin: 20px auto; background: #fff;
         box-shadow: 0 4px 12px rgba(0,0,0,0.3); position: relative; overflow: hidden; }}
.title-panel {{ position: absolute; top: 0; left: 0; width: 100%; height: 60px;
                padding: 8px 20px; border-bottom: 1px solid #ccc; }}
.title-panel h1 {{ font-size: 20px; color: #1F4E79; margin: 0; }}
.title-panel p {{ font-size: 11px; color: #666; margin: 2px 0 0 0; }}
.slide-content {{ position: absolute; top: 60px; left: 0; width: 100%; bottom: 0; }}
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
        title_html = f"""<div class="title-panel"><h1>{slide.title}</h1>"""
        if slide.subtitle:
            title_html += f"<p>{slide.subtitle}</p>"
        title_html += "</div>"

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
                    element_html = self._render_element_html(element, rect, bg)
                    content_parts.append(element_html)

        cells_content = "\n".join(content_parts)

        return f"""<div class="slide">
  {title_html}
  <div class="slide-content">
    {cells_content}
  </div>
</div>"""

    def _cell_style(self, rect: Any, bg_color: Optional[str] = None) -> str:
        parts = [
            f"left:{rect.x:.1f}px; top:{rect.y:.1f}px;",
            f"width:{rect.width:.1f}px; height:{rect.height:.1f}px;",
        ]
        if bg_color:
            parts.append(f"background-color:{bg_color};")
        return " ".join(parts)

    def _render_element_html(self, element: Any, rect: Any, bg_color: Optional[str] = None) -> str:
        style = self._cell_style(rect, bg_color)

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
            return self._render_container_html(element, rect)
        return f"""<div class="cell" style="{style}"></div>"""

    def _render_text_html(self, element: TextElement, style: str) -> str:
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
                    span_style += f"color:{run.color};"
                if run.size:
                    span_style += f"font-size:{run.size}px;"
                if run.font_name:
                    span_style += f"font-family:{run.font_name};"
                text_parts.append(f'<span style="{span_style}">{run.text}</span>')
            text_html = "".join(text_parts)
            align_class = f"text-{block.alignment.value}"
            parts.append(f'<div class="text-block {align_class}" style="text-align:{block.alignment.value}">{text_html}</div>')
        content = "".join(parts)
        return f"""<div class="cell" style="{style}">{content}</div>"""

    def _render_image_html(self, element: ImageElement, style: str) -> str:
        if not element.source or not os.path.exists(element.source):
            return f"""<div class="cell" style="{style}"><p>Image not found: {element.source}</p></div>"""
        return f"""<div class="cell" style="{style}"><img src="{element.source}" style="width:100%;height:100%;object-fit:contain" alt="{element.alt_text}"></div>"""

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

        df = element.data
        if element.include_index:
            df = df.reset_index()

        zebra_style = ""
        if element.zebra:
            zebra_style = """<style>
tr:nth-child(even) { background-color: #f3f3f3; }
tr:nth-child(odd) { background-color: #ffffff; }
thead th { background-color: #4472C4; color: #ffffff; }
</style>"""

        html = f"""<div class="cell" style="{style};overflow:auto">{zebra_style}
<table style="width:100%;border-collapse:collapse;font-size:10px">
<thead><tr>"""
        for col in df.columns:
            html += f"<th style='padding:4px;border:1px solid #d9d9d9;text-align:center'>{col}</th>"
        html += "</tr></thead><tbody>"
        for _, row in df.iterrows():
            html += "<tr>"
            for val in row:
                html += f"<td style='padding:4px;border:1px solid #d9d9d9;text-align:center'>{val}</td>"
            html += "</tr>"
        html += "</tbody></table></div>"
        return html

    def _render_tablespec_html(self, element: Any, style: str) -> str:
        spec = element.tablespec
        if spec is None or not spec.columns or not spec.rows:
            return f"""<div class="cell" style="{style}"></div>"""

        num_cols = len(spec.columns)
        num_rows = len(spec.rows) + 1

        occupied = [[False] * num_cols for _ in range(num_rows)]

        table_style = "width:100%;border-collapse:collapse;font-size:10px"
        if spec.style.zebra:
            table_style += ";background-color:#FFFFFF"

        html = f"""<div class="cell" style="{style};overflow:auto"><table style="{table_style}">
<thead><tr>"""
        for col in spec.columns:
            html += f"<th style='padding:4px;border:1px solid #d9d9d9;text-align:center;background-color:#4472C4;color:#FFFFFF'>{col.label}</th>"
        html += "</tr></thead><tbody>"

        for r in range(len(spec.rows)):
            row = spec.rows[r]
            rr = r + 1
            if rr % 2 == 0 and spec.style.zebra:
                bg_base = "#f3f3f3"
            else:
                bg_base = "#ffffff"

            html += "<tr>"
            for c_idx in range(num_cols):
                if occupied[rr][c_idx]:
                    continue
                if c_idx >= len(row.cells):
                    html += "<td></td>"
                    continue
                cell = row.cells[c_idx]
                txt = cell.text if cell.text is not None else (str(cell.value) if cell.value is not None else "")

                td_style = f"padding:4px;border:1px solid #d9d9d9;text-align:center"
                if cell.background_color:
                    td_style += f";background-color:{cell.background_color}"
                else:
                    td_style += f";background-color:{bg_base}"
                if cell.text_color:
                    td_style += f";color:{cell.text_color}"

                colspan = cell.colspan if cell.colspan > 1 else ""
                rowspan = cell.rowspan if cell.rowspan > 1 else ""
                cs = f' colspan="{colspan}"' if colspan else ""
                rs = f' rowspan="{rowspan}"' if rowspan else ""

                html += f'<td{cs}{rs} style="{td_style}">{txt}</td>'

                if cell.colspan > 1 or cell.rowspan > 1:
                    c2 = min(c_idx + cell.colspan - 1, num_cols - 1)
                    r2 = min(rr + cell.rowspan - 1, num_rows - 1)
                    for span_r in range(rr, r2 + 1):
                        for span_c in range(c_idx, c2 + 1):
                            occupied[span_r][span_c] = True
                    occupied[rr][c_idx] = False
            html += "</tr>"
        html += "</tbody></table></div>"
        return html

    def _render_container_html(self, element: Any, parent_rect: Any) -> str:
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
                    parts.append(self._render_element_html(inner_el, abs_rect, bg))
        return "\n".join(parts)

    def render_slide(self, slide: object) -> object:
        return self._render_slide_html(slide)

    def render_panel(self, panel: object, rect: object) -> object:
        return None
