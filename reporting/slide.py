"""Slide — a single page in a report with grid layout and NumPy-style cell access."""

from __future__ import annotations

from typing import Any, Optional, Union

from reporting.layout.geometry import Edges, Rect, Size
from reporting.layout.grid import Grid, GridCell, GridCellProxy
from reporting.layout.panel import HAlign, VAlign
from reporting.layout.sizing import Sizing, Px
from reporting.elements.text import TextElement
from reporting.elements.image import ImageElement
from reporting.elements.figure import FigureElement
from reporting.elements.table import TableElement
from reporting.elements.tablespec_element import TableSpecElement
from reporting.elements.container import ContainerElement
from reporting.styles.theme import Theme, CorporateTheme
from reporting.background import Background, BackgroundType, SolidBackground, GradientBackground, ImageBackground
from reporting.title_config import TitleText, SubtitleText, TitlePanel, SubtitlePlacement
from reporting.footer_config import FooterPanel


class Slide:
    """A single slide (page) in a report.

    Every ``Slide`` has a built-in **title panel** rendered
    automatically at the top.  The remaining area below it is
    divided into a grid via ``grid_layout()``.

    Cell access uses NumPy-style indexing::

        slide[row, col]          # single cell
        slide[0, :]              # entire first row
        slide[:, 0]              # entire first column
        slide[0:2, 1:3]          # sub-grid

    Args:
        title: Slide title displayed in the title panel.  Can be a
            plain ``str`` or a ``TitleText`` with embedded styling.
            Falls back to the slide type default when ``None``
            (default ``None``).
        subtitle: Optional subtitle (default ``None``).  Can be a
            plain ``str`` or a ``SubtitleText`` with embedded styling.
        theme: Visual theme.  Falls back to ``CorporateTheme()``
            when ``None`` (default ``None``).
        width: Slide width in pixels.  Falls back to
            ``theme.page_size[0]`` when ``None`` (default ``None``).
        height: Slide height in pixels.  Falls back to
            ``theme.page_size[1]`` when ``None`` (default ``None``).
        title_panel: Title panel configuration (height, padding,
            separator, subtitle placement).  Falls back to the
            slide type default when ``None`` (default ``None``).
        background: Slide background.  Accepts a hex string
            ``"#RRGGBB"``, a named CSS color, or a
            ``SolidBackground`` / ``GradientBackground`` /
            ``ImageBackground`` instance (default ``None``).
        footer_panel: Footer panel configuration (height, styling,
            logo).  Falls back to the slide type default when
            ``None`` (default ``None``).
        slide_type: Name of a pre-defined slide type in the
            theme (default ``"default"``).
        base_slide: Another ``Slide`` whose config and grid
            layout are used as a starting point.  Content cells
            are **not** copied (default ``None``).

    When a slide type specifies a ``layout``, the grid is
    created automatically.  Slide type default cells are
    populated as ``TextElement`` objects.

    Resolution order (later wins)::

        base_slide → theme → slide_type → explicit kwargs

    Example::

        from reporting.slide import Slide

        slide = Slide("Results", subtitle="Test data")
        slide.grid_layout(rows=2, cols=2, gap=8)
        slide[0, 0].text("Top-left", bold=True)
        slide[1, :].text("Spanning bottom row")

    Text can also inherit all font properties from the slide's theme::

        slide[0, 0].text("Heading", style="h1")
        slide[0, 1].text("Body text", style="body",
                          color=palette.primary.css)

    Use a pre-defined slide type from the theme::

        slide = Slide("Cover", slide_type="title")

    Or base a slide on another slide to reuse its layout::

        base = Slide("Master")
        base.grid_layout(rows=2, cols=3, gap=10)

        child = Slide("Child", base_slide=base)
        # child has the same theme, header/footer config,
        # background, and 2x3 grid layout
    """

    def __init__(
        self,
        title: Optional[Union[str, TitleText]] = None,
        subtitle: Optional[Union[str, SubtitleText]] = None,
        theme: Optional[Union[str, Theme]] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        title_panel: Optional[TitlePanel] = None,
        background: Optional[Union[str, SolidBackground, GradientBackground, ImageBackground]] = None,
        footer_panel: Optional[FooterPanel] = None,
        slide_type: str = "default",
        base_slide: Optional[Slide] = None,
    ):
        self._grid = None
        self._elements = {}
        self._footer_grid = None
        self._footer_elements = {}

        # --- Resolution chain: base_slide → theme → slide_type → explicit kwargs ---
        resolved_theme: Theme
        resolved_title_panel: Optional[TitlePanel] = None
        resolved_footer_panel: Optional[FooterPanel] = None
        resolved_background: Optional[Background] = None
        resolved_width: float
        resolved_height: float
        resolved_title: Optional[Union[str, TitleText]] = None
        resolved_subtitle: Optional[Union[str, SubtitleText]] = None

        # ── Helper: resolve theme (instance, string name, or default) ──
        def _resolve_theme(t: Optional[Union[str, Theme]]) -> Theme:
            if t is None:
                return CorporateTheme()
            if isinstance(t, str):
                return Theme.get_registered(t)()
            return t

        # ── Step 1: base_slide ──────────────────────────────────────
        if base_slide is not None:
            resolved_theme = base_slide.theme
            resolved_title_panel = base_slide.title_panel
            resolved_footer_panel = base_slide.footer_panel
            resolved_width = base_slide.width
            resolved_height = base_slide.height
            resolved_title = base_slide.title
            resolved_subtitle = base_slide.subtitle
            if base_slide.background is not None:
                resolved_background = base_slide.background
            if base_slide._grid is not None:
                self._grid = base_slide._grid.copy_structure()
        else:
            resolved_theme = _resolve_theme(theme)
            resolved_width = width or resolved_theme.page_size[0]
            resolved_height = height or resolved_theme.page_size[1]

        # ── Step 2: explicit theme override ─────────────────────────
        if theme is not None:
            resolved_theme = _resolve_theme(theme)

        # ── Step 3: slide type from theme ────────────────────────────
        st = resolved_theme.get_slide_type(slide_type)
        if resolved_title is None and st.title_text is not None:
            resolved_title = st.title_text
        if resolved_subtitle is None and st.subtitle_text is not None:
            resolved_subtitle = st.subtitle_text
        resolved_title_panel = resolved_title_panel or st.title_panel
        resolved_footer_panel = resolved_footer_panel or st.footer_panel
        if resolved_background is None and st.background is not None:
            resolved_background = st.background

        # ── Step 4: explicit kwargs override ─────────────────────────
        self.theme = resolved_theme
        self.width = width or resolved_width
        self.height = height or resolved_height
        self.title_panel = title_panel or resolved_title_panel or TitlePanel.from_theme(self.theme)
        if isinstance(background, str):
            self.background = SolidBackground(background)
        else:
            self.background = background if background is not None else resolved_background
        self.footer_panel = footer_panel or resolved_footer_panel or self.theme.footer_panel

        # ── Step 5: build title/subtitle text objects ────────────────
        raw_title: Union[str, TitleText] = resolved_title if title is None else title
        raw_subtitle: Optional[Union[str, SubtitleText]] = resolved_subtitle if subtitle is None else subtitle

        if isinstance(raw_title, TitleText):
            self.title = TitleText(
                raw_title.text,
                font_name=raw_title.font_name,
                font_size=raw_title.font_size,
                bold=raw_title.bold,
                italic=raw_title.italic,
                color=raw_title.color,
                alignment=raw_title.alignment,
            )
        else:
            self.title = TitleText.from_theme(self.theme, text=raw_title or "")

        if raw_subtitle is not None:
            if isinstance(raw_subtitle, SubtitleText):
                self.subtitle = SubtitleText(
                    raw_subtitle.text,
                    font_name=raw_subtitle.font_name,
                    font_size=raw_subtitle.font_size,
                    bold=raw_subtitle.bold,
                    italic=raw_subtitle.italic,
                    color=raw_subtitle.color,
                    alignment=raw_subtitle.alignment,
                )
            else:
                self.subtitle = SubtitleText.from_theme(self.theme, text=raw_subtitle)
        else:
            self.subtitle = None

        # ── Step 6: auto-apply layout from slide type ────────────────
        if self._grid is None and st.layout is not None and base_slide is None:
            lc = resolved_theme.get_layout(st.layout)
            self.grid_layout(
                rows=lc.rows,
                cols=lc.cols,
                row_sizes=lc.row_sizes,
                col_sizes=lc.col_sizes,
                gap=lc.gap,
                padding=lc.padding,
            )

        # ── Step 7: populate default cells from slide type ───────────
        if self._grid is not None and base_slide is None:
            for (r, c), text_content in st.cells.items():
                if 0 <= r < self._grid.rows and 0 <= c < self._grid.cols:
                    if self._grid.cells[r][c].element is None:
                        self[r, c].text(text_content)

        # ── Step 8: footer ──────────────────────────────────────────
        if self.footer_panel.enabled:
            self.footer_layout(rows=1, cols=3)
            if self.footer_panel.logo:
                self.footer[0, 0].image(self.footer_panel.logo)
            else:
                self.footer[0, 0].text("")
            if self.footer_panel.center_text:
                self.footer[0, 1].text(
                    self.footer_panel.center_text,
                    size=self.footer_panel.font_size,
                    color=self.footer_panel.color,
                    font_name=self.footer_panel.font_name,
                    alignment="center",
                )
            self.footer[0, 2].text(
                "{page} / {total}",
                size=self.footer_panel.font_size,
                color=self.footer_panel.color,
                font_name=self.footer_panel.font_name,
                alignment="right",
            )

    @property
    def size(self) -> Size:
        """Return the full slide dimensions as a ``Size``.

        Returns:
            ``Size(width, height)`` in pixels.
        """
        return Size(self.width, self.height)

    @property
    def content_size(self) -> Size:
        """Return the available area below the title panel.

        When a footer grid has been set up via ``footer_layout()``,
        the footer height (and separator margin, if shown) is
        also subtracted.

        Returns:
            ``Size(width, height - title_panel.height[- footer_panel.height
            [- separator_margin]])`` in pixels.
        """
        if self._footer_grid is not None:
            fp = self.footer_panel
            extra = fp.separator_margin if fp.show_separator else 0
            footer_h = fp.height + extra
        else:
            footer_h = 0
        title_h = self.title_panel.height if self.title_panel.enabled else 0
        return Size(self.width, self.height - title_h - footer_h)

    def get_cell_rects(self) -> list[list[Rect]]:
        """Compute the pixel rectangles of every grid cell.

        Raises:
            RuntimeError: If ``grid_layout()`` has not been called.

        Returns:
            A 2-D list of ``Rect``, one per cell in the grid.
        """
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
        """Divide the content area into a grid of cells.

        Must be called before accessing cells with ``slide[r, c]``.

        Args:
            rows: Number of rows (default ``1``).
            cols: Number of columns (default ``1``).
            row_sizes: Per-row sizing. Each element can be
                ``Px(v)`` for fixed, ``Percent(v)`` for
                percentage, ``Fill`` for remaining space, or
                a plain float treated as ``Px(v)``
                (default ``None`` = all rows use ``Fill``).
            col_sizes: Per-column sizing, same rules as
                ``row_sizes`` (default ``None`` = all
                columns use ``Fill``).
            gap: Spacing between cells in pixels
                (default ``0.0``).
            padding: Outer padding around the grid as an
                ``Edges``.  ``Edges.all(v)`` sets uniform
                padding (default ``None`` = no padding).

        Example::

            slide.grid_layout(rows=3, cols=2, gap=8,
                              padding=Edges.all(12))
            slide[0, 0].text("Cell (0, 0)")
        """
        self._grid = Grid(
            rows=rows,
            cols=cols,
            row_sizes=row_sizes,
            col_sizes=col_sizes,
            gap=gap,
            padding=padding,
        )

    def __getitem__(self, pos: tuple[Union[int, slice], Union[int, slice]]) -> _CellProxy:
        """Access a grid cell by row and column (NumPy-style indexing).

        Args:
            pos: A ``(row, col)`` tuple.  Each coordinate can be an
                ``int`` or a ``slice``.  Slices span multiple cells
                (auto ``rowspan`` / ``colspan``).

        Returns:
            A ``_CellProxy`` that provides chained methods
            (``.text()``, ``.image()``, etc.).

        Raises:
            RuntimeError: If ``grid_layout()`` has not been called.

        Example::

            slide[0, 0]          # single cell
            slide[0, :]          # whole first row
            slide[:, 1]          # whole second column
            slide[1:, 2:]        # bottom-right sub-grid
        """
        if self._grid is None:
            raise RuntimeError("Call grid_layout() before accessing cells.")
        cell_proxy = self._grid[pos]
        return _CellProxy(self, cell_proxy)

    def _set_cell_element(self, cell: GridCell, element: Any) -> None:
        cell.element = element
        self._elements[(cell.panel.row, cell.panel.col)] = element

    # --- Footer ---

    def footer_layout(
        self,
        rows: int = 1,
        cols: int = 4,
        row_sizes: Optional[list[Sizing]] = None,
        col_sizes: Optional[list[Sizing]] = None,
        gap: float = 0.0,
        padding: Optional[Edges] = None,
    ) -> None:
        """Divide the footer area into a grid of cells.

        Must be called before accessing footer cells with
        ``slide.footer[r, c]``.

        Args:
            rows: Number of rows (default ``1``).
            cols: Number of columns (default ``4``).
            row_sizes: Per-row sizing (default ``None`` =
                all rows use ``Fill``).
            col_sizes: Per-column sizing (default ``None`` =
                all columns use ``Fill``).
            gap: Spacing between cells in pixels
                (default ``0.0``).
            padding: Outer padding around the footer grid
                (default ``None`` = no extra padding; the
                footer's own ``FooterConfig.padding`` is
                applied by the renderer).

        Example::

            slide.footer_layout(rows=1, cols=4, gap=4)
            slide.footer[0, 0].page_number(style="caption")
            slide.footer[0, 1].text(" | ", style="caption")
            slide.footer[0, 2].total_pages(style="caption")
        """
        self._footer_grid = Grid(
            rows=rows,
            cols=cols,
            row_sizes=row_sizes,
            col_sizes=col_sizes,
            gap=gap,
            padding=padding,
        )

    def get_footer_cell_rects(self) -> list[list[Rect]]:
        """Compute the pixel rectangles of every footer grid cell.

        Rectangles are relative to the top-left of the footer
        content area (inside ``FooterConfig.padding``).

        Returns:
            A 2-D list of ``Rect``, one per cell in the footer grid.
        """
        if self._footer_grid is None:
            raise RuntimeError("Call footer_layout() before accessing footer cells.")
        _, rects = self._footer_grid.layout(self._footer_content_size)
        return [[Rect(r.x, r.y, r.width, r.height) for r in row] for row in rects]

    @property
    def _footer_content_size(self) -> Size:
        """Available area inside the footer panel (after padding)."""
        pad = self.footer_panel.padding
        return Size(
            self.width - pad.left - pad.right,
            self.footer_panel.height - pad.top - pad.bottom,
        )

    @property
    def footer(self) -> _FooterProxy:
        """Access the footer grid.

        Returns:
            A ``_FooterProxy`` for NumPy-style indexing into
            footer cells.

        Raises:
            RuntimeError: If ``footer_layout()`` has not been
                called first.
        """
        if self._footer_grid is None:
            raise RuntimeError("Call footer_layout() before accessing footer cells.")
        return _FooterProxy(self)

    def _set_footer_element(self, cell: GridCell, element: Any) -> None:
        cell.element = element
        self._footer_elements[(cell.panel.row, cell.panel.col)] = element


_STYLE_ALIASES: dict[str, str] = {
    "h1": "heading_1",
    "h2": "heading_2",
    "h3": "heading_3",
}


class _CellProxy:
    """Intermediate object returned by ``slide[r, c]``.

    Do **not** instantiate directly.  Every cell-access method
    returns ``self`` or an element, enabling chaining.
    """

    def __init__(self, slide: Slide, proxy: GridCellProxy) -> None:
        self._slide = slide
        self._proxy = proxy
        self._cell = proxy.cell

    @property
    def background_color(self) -> object:
        """Background colour of the cell's panel (property).

        Setting this is equivalent to
        ``slide[r, c]._cell.panel.background_color = value``.

        Example::

            slide[0, 0].background_color = "#E3F2FD"
            slide[1, 0].background_color = (33, 150, 243)
        """
        return self._proxy.background_color

    @background_color.setter
    def background_color(self, value: object) -> None:
        self._proxy.background_color = value

    @property
    def padding(self) -> object:
        """Padding of the cell's panel (property).

        Setting this is equivalent to
        ``slide[r, c]._cell.panel.padding = value``.
        """
        return self._proxy.padding

    @padding.setter
    def padding(self, value: object) -> None:
        self._proxy.padding = value

    def align(
        self,
        h_align: HAlign = HAlign.STRETCH,
        v_align: VAlign = VAlign.STRETCH,
    ) -> _CellProxy:
        """Set content alignment inside the cell.

        Call before the element-creating method (``.text()``,
        ``.image()``, etc.) so alignment affects the rendered
        content.

        Args:
            h_align: Horizontal alignment.

                - ``HAlign.LEFT`` — left-align content
                - ``HAlign.CENTER`` — centre horizontally
                - ``HAlign.RIGHT`` — right-align content
                - ``HAlign.STRETCH`` — stretch content to fill
                  cell width (default)

            v_align: Vertical alignment.

                - ``VAlign.TOP`` — top-align content
                - ``VAlign.MIDDLE`` — centre vertically
                - ``VAlign.BOTTOM`` — bottom-align content
                - ``VAlign.STRETCH`` — stretch content to fill
                  cell height (default)

        Returns:
            ``self`` for chaining.

        Example::

            slide[0, 0].align(HAlign.CENTER, VAlign.MIDDLE).text("Hi")
            slide[1, 0].align(HAlign.LEFT, VAlign.TOP).image("img.png")
        """
        self._proxy.align(h_align, v_align)
        return self

    def text(self, content: str = "", **kwargs: object) -> TextElement:
        """Add a text element to this cell.

        Text content is plain text.  Rich formatting (bold, italic,
        colour, font) is passed as keyword arguments and applied to
        the entire string.  Use ``TextElement`` directly for
        multi-run (mixed-format) text.

        When ``style`` is given (e.g. ``"heading_1"``, ``"body"``,
        ``"caption"``), font properties are resolved from the
        slide's theme.  Explicit kwargs override the resolved
        values.

        Args:
            content: The text to display.  May contain ``\\n`` for
                line breaks.

        Keyword Args:
            style: A theme typography style name —
                ``"heading_1"`` (or ``"h1"``), ``"heading_2"``
                (or ``"h2"``), ``"heading_3"`` (or ``"h3"``),
                ``"body"``, ``"caption"``, ``"code"``, ``"mono"``.
                Resolves family, size, bold, italic, and colour
                from the slide's theme (default ``None``).
            bold: Whether the text is bold (default ``False``).
            italic: Whether the text is italic (default ``False``).
            size: Font size in points (default ``None`` = theme
                default, typically ``10``).
            color: Text colour as a hex string ``"#RRGGBB"``, a
                named CSS colour, or an ``(r, g, b)`` tuple
                (default ``None``).
            font_name: Font family such as ``"Helvetica"``,
                ``"Times-Roman"``, ``"Courier"`` (default
                ``None`` = theme default).
            alignment: One of ``TextAlignment.LEFT``,
                ``TextAlignment.CENTER``,
                ``TextAlignment.RIGHT``,
                ``TextAlignment.JUSTIFY`` (default
                ``TextAlignment.LEFT``).

        Returns:
            The created ``TextElement``.

        Example::

            slide[0, 0].text("Hello", style="heading_1")
            slide[0, 0].text("Bold text", style="h2",
                              color=pal.primary.css)
            slide[1, 0].text("Line 1\\nLine 2",
                              alignment=TextAlignment.CENTER)
        """
        style_name = kwargs.pop("style", None)
        if style_name is not None:
            typo = self._slide.theme.typography
            name = _STYLE_ALIASES.get(style_name, style_name)
            spec = getattr(typo, name, None)
            if spec is not None:
                kwargs.setdefault("font_name", spec.family)
                kwargs.setdefault("size", spec.size)
                kwargs.setdefault("bold", spec.bold)
                kwargs.setdefault("italic", spec.italic)
                if spec.color is not None and "color" not in kwargs:
                    kwargs["color"] = spec.color
        el = self._proxy.text(content, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def image(self, source: str = "", **kwargs: object) -> ImageElement:
        """Add an image from a file to this cell.

        Supported formats: PNG, JPG.

        Args:
            source: Path to the image file.

        Keyword Args:
            scale: Uniform scale factor (default ``1.0``).
            fit_mode: How to fit the image in the cell.

                - ``ImageFitMode.ORIGINAL`` — native size, scaled
                  down only if larger than the cell (default)
                - ``ImageFitMode.FIT_VERTICAL`` — fill cell height
                - ``ImageFitMode.FIT_HORIZONTAL`` — fill cell width
            width: Explicit width in points.  Overrides ``scale``
                and ``fit_mode`` for the width axis
                (default ``None``).
            height: Explicit height in points.  Overrides
                ``scale`` and ``fit_mode`` for the height axis
                (default ``None``).
            rotation: Rotation angle in degrees clockwise
                (default ``0.0``).
            opacity: Opacity from ``0.0`` (transparent) to
                ``1.0`` (opaque) (default ``1.0``).
            alt_text: Alternative text for accessibility
                (default ``""``).

        Returns:
            The created ``ImageElement``.

        Example::

            slide[0, 0].image("chart.png", scale=0.8)
            slide[0, 1].image("photo.jpg",
                              fit_mode=ImageFitMode.FIT_VERTICAL)
            slide[1, 0].image("logo.png", width=120, opacity=0.9)
        """
        el = self._proxy.image(source, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def plot(self, figure: object = None, **kwargs: object) -> FigureElement:
        """Embed a matplotlib figure in this cell.

        Args:
            figure: A ``matplotlib.figure.Figure`` instance.

        Keyword Args:
            format: Output format — ``"png"`` (raster, default),
                ``"pdf"`` (vector, requires ``pdfrw``), or
                ``"svg"`` (requires ``svgwrite``).
            dpi: Resolution for raster output (default ``150``).
            preserve_aspect: Whether to preserve the figure's
                aspect ratio (default ``False``).
            container_width_pct: Width as a percentage of the
                cell width (default ``None`` = use native size).
            container_height_pct: Height as a percentage of the
                cell width (default ``None`` = use native size).

        Returns:
            The created ``FigureElement``.

        Example::

            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([1, 2, 3], [4, 5, 6])
            slide[0, 0].plot(fig, format="pdf", preserve_aspect=True)
        """
        el = self._proxy.plot(figure, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def table(self, data: object = None, **kwargs: object) -> TableElement:
        """Add a table to this cell.

        Accepts either a pandas ``DataFrame`` (rendered as a
        basic table) or a ``TableSpec`` (rendered with full
        TableSpec styling).  Passing a ``TableSpec``
        automatically delegates to ``table_spec()``.

        Args:
            data: A pandas ``DataFrame``, a ``TableSpec``, or
                anything ``TableSpec`` can convert.

        Keyword Args:
            header: Whether to show a header row
                (default ``True``, DataFrame only).
            include_index: Whether to show the DataFrame index
                (default ``False``, DataFrame only).
            zebra: Enable alternating row colours
                (default ``False``).
            numeric_format: Format string for numeric values
                (e.g. ``"{:.2f}"``) (default ``None``).

        Returns:
            A ``TableElement`` (DataFrame input) or
            ``TableSpecElement`` (TableSpec input).

        Example::

            import pandas as pd
            df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
            slide[0, 0].table(df, zebra=True)

            from reporting.tablespec import TableSpec, Column
            ts = TableSpec(columns=[Column("x"), Column("y")])
            ts.row(1, 2).row(3, 4)
            slide[0, 0].table(ts)
        """
        from reporting.tablespec.spec import TableSpec
        if isinstance(data, TableSpec):
            return self.table_spec(data, **kwargs)  # type: ignore[return-value]
        el = self._proxy.table(data, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def table_spec(self, spec: object = None, **kwargs: object) -> TableSpecElement:
        """Add a ``TableSpec`` to this cell (explicit method).

        Prefer calling ``.table(ts)`` which auto-detects
        ``TableSpec``; this method exists for cases where
        the type detection needs to be bypassed.

        Args:
            spec: A ``TableSpec`` instance.
            **kwargs: Ignored (reserved for future use).

        Returns:
            The created ``TableSpecElement``.

        Example::

            ts = TableSpec(columns=[Column("A"), Column("B")])
            ts.row(10, 20)
            slide[0, 0].table_spec(ts)
        """
        from reporting.tablespec.spec import TableSpec as _TableSpec
        from reporting.tablespec.style import TableStyle as _TableStyle
        if isinstance(spec, _TableSpec) and spec.style == _TableStyle():
            import dataclasses
            theme_ts = self._slide.theme.table_style
            spec.style = _TableStyle(**{f.name: getattr(theme_ts, f.name) for f in dataclasses.fields(_TableStyle)})
        el = self._proxy.table_spec(spec, **kwargs)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]

    def grid_layout(self, grid: object) -> ContainerElement:
        """Add a nested sub-grid inside this cell.

        Wraps a ``Grid`` in a ``ContainerElement`` so you can
        place multiple items inside one cell.

        Args:
            grid: A ``Grid`` instance defining the sub-layout.

        Returns:
            The created ``ContainerElement``.

        Example::

            from reporting.layout.grid import Grid

            inner = Grid(rows=2, cols=1, gap=6)
            inner[0, 0].text("Top")
            inner[1, 0].text("Bottom")
            slide[2, :].grid_layout(inner)
        """
        el = self._proxy.grid_layout(grid)
        self._slide._set_cell_element(self._cell, el)
        return el  # type: ignore[return-value]


class _FooterProxy:
    """Intermediate object returned by ``slide.footer``.

    Do **not** instantiate directly.  Use ``slide.footer_layout()``
    first, then ``slide.footer[r, c]``.
    """

    def __init__(self, slide: Slide) -> None:
        self._slide = slide

    def __getitem__(self, pos: tuple[Union[int, slice], Union[int, slice]]) -> _FooterCellProxy:
        """Access a footer grid cell by row and column.

        Args:
            pos: A ``(row, col)`` tuple.  Each coordinate can be an
                ``int`` or a ``slice``.

        Returns:
            A ``_FooterCellProxy`` for placing content.
        """
        proxy = self._slide._footer_grid[pos]
        return _FooterCellProxy(self._slide, proxy)


class _FooterCellProxy:
    """Proxy for individual footer cells returned by ``slide.footer[r, c]``.

    Do **not** instantiate directly.
    """

    def __init__(self, slide: Slide, proxy: GridCellProxy) -> None:
        self._slide = slide
        self._proxy = proxy
        self._cell = proxy.cell

    def text(self, content: str = "", **kwargs: object) -> TextElement:
        """Add a text element to this footer cell.

        Args:
            content: The text to display.

        Keyword Args:
            Same as ``_CellProxy.text()`` — ``bold``, ``italic``,
            ``size``, ``color``, ``font_name``, ``alignment``,
            ``style``.

        Returns:
            The created ``TextElement``.
        """
        style_name = kwargs.pop("style", None)
        if style_name is not None:
            typo = self._slide.theme.typography
            name = _STYLE_ALIASES.get(style_name, style_name)
            spec = getattr(typo, name, None)
            if spec is not None:
                kwargs.setdefault("font_name", spec.family)
                kwargs.setdefault("size", spec.size)
                kwargs.setdefault("bold", spec.bold)
                kwargs.setdefault("italic", spec.italic)
                if spec.color is not None and "color" not in kwargs:
                    kwargs["color"] = spec.color
        el = self._proxy.text(content, **kwargs)
        self._slide._set_footer_element(self._cell, el)
        return el  # type: ignore[return-value]

    def image(
        self,
        source: str = "",
        scale: float = 1.0,
        fit_mode: str = "fit_vertical",
        **kwargs: object,
    ) -> ImageElement:
        """Add an image to this footer cell.

        Args:
            source: Path to the image file.
            scale: Uniform scale factor (default ``1.0``).
            fit_mode: How to fit the image in the cell
                (default ``"fit_vertical"``).

        Returns:
            The created ``ImageElement``.
        """
        from reporting.elements.image import ImageFitMode

        mode = ImageFitMode(fit_mode)
        el = self._proxy.image(source=source, scale=scale, fit_mode=mode, **kwargs)
        self._slide._set_footer_element(self._cell, el)
        return el  # type: ignore[return-value]

    def page_number(self, **kwargs: object) -> TextElement:
        """Add a page-number placeholder in this footer cell.

        The renderer replaces this with the current page number
        (e.g. ``"1"``, ``"2"``, …).

        Keyword Args:
            Same as ``text()`` — ``bold``, ``italic``, ``size``,
            ``color``, ``font_name``, ``alignment``, ``style``.

        Returns:
            The created ``TextElement`` with an auto placeholder.
        """
        el = self.text("{page}", **kwargs)
        el.properties["_auto"] = "page_number"
        return el

    def total_pages(self, **kwargs: object) -> TextElement:
        """Add a total-pages placeholder in this footer cell.

        The renderer replaces this with the total number of pages
        (e.g. ``"5"``, ``"12"``, …).

        Keyword Args:
            Same as ``text()`` — ``bold``, ``italic``, ``size``,
            ``color``, ``font_name``, ``alignment``, ``style``.

        Returns:
            The created ``TextElement`` with an auto placeholder.
        """
        el = self.text("{total}", **kwargs)
        el.properties["_auto"] = "total_pages"
        return el
