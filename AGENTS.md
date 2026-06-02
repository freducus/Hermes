# pyreportengine — AGENTS.md

## Project

Python reporting framework (`pyreportengine`) for generating technical engineering reports (CFD, FEM, modal analysis, etc.). A "programmable PowerPoint" with fully decoupled render backends.

## Architecture constraints (strict — will not be obvious from imports)

- **Layout logic** (`layout/`) MUST NOT import or depend on any renderer (ReportLab, python-pptx, etc.).
- **Elements** (`elements/`) MUST NOT know which render backend is in use.
- **Geometry** (`layout/geometry.py`, `sizing.py`, `constraints.py`) is pure math — no visual representation concepts.
- Follow SOLID, Clean Architecture, composition over inheritance, dependency inversion.
- All public APIs fully type-hinted. Prefer `dataclasses`, `typing`, `enum`. No `Any` unless unavoidable.

## Directory layout

```
reporting/
  document.py          # Report container
  slide.py             # Page abstraction (accepts slide[row,col] indexing)
  layout/              # Pure layout engine (zero renderer imports)
    geometry.py, panel.py, grid.py, sizing.py, constraints.py
  elements/            # Content types (backend-agnostic)
    base.py, text.py, image.py, figure.py, table.py, container.py, spacer.py
  styles/              # Theming system
    theme.py, colors.py, typography.py, table_style.py
  renderers/           # Output backends
    base.py            # Abstract renderer interface
    pdf/               # ReportLab implementation
    html/              # HTML/CSS implementation
  utils/
  examples/
tests/
```

## Slide anatomy

Every `Slide` has a built-in **title panel** (default height 60px) rendered automatically. The grid occupies the remaining content area below it.

```python
slide = Slide("Title", subtitle="Optional", title_panel_height=60)
slide.grid_layout(rows=3, cols=4)
# Grid is laid out in the area below the title panel
slide[0, 0].text("content")  # placed at y=60+
```

Use `slide.content_size` to get the available (width, height) for the grid.

## API convention

NumPy-style cell access via `__getitem__`:

```python
slide[row, col]            # single cell
slide[0, :]                # whole row → colspan=num_cols
slide[:, 0]                # whole column
slide[1:, 2:]              # sub-grid
slide[0, 0].text("...", bold=True, size=14)   # chained element creation
slide[1, 0].plot(fig)                          # matplotlib figure
slide[2, :].table(df, zebra=True)
```

Slices auto-compute `colspan`/`rowspan`. Text kwargs (`bold`, `italic`, `color`, `size`, `alignment`) are extracted from `**kwargs` and applied to the auto-created `TextRun`.

## Tech stack

| Layer | Technology |
|-------|-----------|
| Language | Python >= 3.11 (current: 3.12.10, Windows) |
| Testing | pytest |
| PDF | reportlab |
| HTML | — (pure HTML/CSS) |
| Plots | matplotlib (`matplotlib.figure.Figure`) |
| Tables | pandas (`DataFrame` as input) |

## Development commands

```
pip install -e ".[dev]"      # editable install with dev deps
pip install -e ".[docs]"     # with docs deps (sphinx, pypdfium2)
make test                     # run all tests (pytest -v)
make docs                     # build HTML docs (cd docs; sphinx)
make docs-clean               # rm -rf docs/build/
cd docs && make.bat html      # build docs on Windows cmd
cd docs && python -m sphinx -b html source build   # build docs (any shell)
```

## Commits

Commit after every meaningful change. Stage only intended files; never commit secrets.

## Code style

- Google-style docstrings.
- Module-level docstring explaining responsibility.
- No empty methods, no pseudocode, no `pass` stubs — raise `NotImplementedError` in abstract methods.
- Everything must be executable.

## Platform

- **Windows** (PowerShell). `.venv` already created with virtualenv 20.31.2.
- PyCharm project configured for Python 3.12. Use `.venv\Scripts\activate` to activate.

## Documentation policy

Every new feature or public API change MUST include:
1. An executable example (in `examples/` or as a code block in the RST page).
2. A corresponding update to the Sphinx docs under `docs/source/` — either a new `.rst` page or a new section in an existing page.
3. If the feature affects layout (padding, margin, sizing), add a visual example to `docs/source/layout.rst` or `examples/padding_margin.py`.

Regenerate the HTML docs after changes with:

```
cd docs
.\make.bat html
```

Regenerate example page images:

```
python examples/basic_report.py
python docs\gen_doc_images.py
```

Or all at once:

```
make docs
```
