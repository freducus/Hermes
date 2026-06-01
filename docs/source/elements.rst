Elements Reference
==================

All content types inherit from ``BaseElement`` and are backend-agnostic —
they do not know which renderer produces the final output.

TextElement
-----------

A rich-text block made of one or more ``TextBlock``\ s, each containing
one or more ``TextRun``\ s.

.. code-block:: python

   slide[0, 0].text("Hello")                     # simple text
   slide[0, 1].text("Bold red", bold=True,       # formatted in one call
                     color="#C62828", size=14)
   slide[1, 0].text("Times-Roman title",         # custom font
                     font_name="Times-Roman",
                     size=16, italic=True)

**Keyword arguments** (all extracted from ``**kwargs``):

``bold``
   ``bool`` — applies bold face (default ``False``)
``italic``
   ``bool`` — applies italic (default ``False``)
``color``
   ``str`` — hex color like ``"#C62828"`` (default ``None``)
``size``
   ``float`` — font size in points (default ``None``, renderer picks)
``font_name``
   ``str`` — PostScript font name, e.g. ``"Times-Roman"``, ``"Courier-Bold"``,
   ``"Helvetica-Oblique"`` (default ``None`` → renderer default)
``alignment``
   ``str`` or ``TextAlignment`` — ``"left"``, ``"center"``, ``"right"``,
   ``"justify"`` (default ``"left"``)

**Multi-run text:**

.. code-block:: python

   el = slide[0, 0].text("Base text", size=12)
   el.add_run(" bold part", bold=True)
   el.add_run(" red part", color="#C62828")
   el.add_block(alignment="center")
   el.add_run("Centered line", font_name="Times-Roman", size=14)

.. image:: _images/comprehensive_report_p1.png
   :width: 320px
   :alt: Text elements with various formatting

----

FigureElement
-------------

Wraps a ``matplotlib.figure.Figure``.

.. code-block:: python

   import matplotlib.pyplot as plt
   import numpy as np

   fig, ax = plt.subplots()
   ax.plot(np.linspace(0, 10, 50), np.sin(np.linspace(0, 10, 50)))
   slide[0, 0].plot(fig)                    # default dpi=150, bbox="tight"

   slide[0, 1].plot(fig, dpi=200)           # higher resolution
   slide[0, 2].plot(fig, format="jpg")      # JPEG output

**Keyword arguments:**

``dpi``
   ``int`` — resolution (default ``150``)
``bbox_inches``
   ``str`` or ``None`` — bounding box (default ``"tight"``)
``format``
   ``str`` — image format (default ``"png"``)

.. image:: _images/engineering_report_p1.png
   :width: 320px
   :alt: Matplotlib figure in report

----

TableElement
------------

Wraps a ``pandas.DataFrame``.

.. code-block:: python

   import pandas as pd

   df = pd.DataFrame({
       "Parameter": ["A", "B", "C"],
       "Value": [1.0, 2.5, 3.2],
       "Status": ["Pass", "Pass", "Fail"],
   })
   slide[0, :].table(df)                    # basic table
   slide[1, :].table(df, zebra=True)        # alternating row colors
   slide[2, 0].table(df, include_index=True) # show index column

**Keyword arguments:**

``zebra``
   ``bool`` — alternating row colors (default ``False``)
``include_index``
   ``bool`` — reset index as first column (default ``False``)
``header``
   ``bool`` — show header row (default ``True``)
``numeric_format``
   ``str`` — format string for numbers, e.g. ``"{:.2f}"``
``column_widths``
   ``list[float]`` — explicit column widths in px

**Conditional formatting:**

.. code-block:: python

   slide[0, :].table(df).highlight_max("Value")
   slide[1, :].table(df).heatmap("Value", color_map="Blues")
   slide[2, :].table(df).highlight_min("Status")

.. image:: _images/dashboard_report_p1.png
   :width: 320px
   :alt: Table with zebra styling and plots

----

ImageElement
------------

References an external image file.

.. code-block:: python

   slide[0, 0].image("chart.png")
   slide[0, 0].image("diagram.svg", scale=0.8)

**Keyword arguments:**

``alt_text``
   ``str`` — alternate text (default ``""``)
``scale``
   ``float`` — scale factor (default ``1.0``)
``rotation``
   ``float`` — rotation degrees (default ``0.0``)
``opacity``
   ``float`` — opacity 0–1 (default ``1.0``)
``width``
   ``float`` — explicit width in px (default ``None``)
``height``
   ``float`` — explicit height in px (default ``None``)

----

ContainerElement
----------------

Nests a ``Grid`` inside a single cell. Useful for complex sub-layouts.

.. code-block:: python

   from reporting.layout.grid import Grid
   from reporting.layout.sizing import Fill
   from reporting.elements.container import ContainerElement
   from reporting.elements.text import TextElement

   inner = Grid(rows=2, cols=1, row_sizes=[Fill, Fill], gap=5)
   inner[0, 0].panel.background_color = "#E8F0FE"
   inner[0, 0].element = TextElement("Top", bold=True, size=12)
   inner[1, 0].panel.background_color = "#FFF3E0"
   inner[1, 0].element = TextElement("Bottom", size=10)

   container = ContainerElement(grid=inner)
   slide._set_cell_element(slide._grid[0, 0], container)

.. image:: _images/nested_layouts_p1.png
   :width: 320px
   :alt: Nested container layout

----

SpacerElement
-------------

Occupies empty space in a layout. Typically unused — empty cells render as
blank space automatically.

.. code-block:: python

   from reporting.elements.spacer import SpacerElement

   slide._grid.cells[0][1].element = SpacerElement(width=50, height=20)
