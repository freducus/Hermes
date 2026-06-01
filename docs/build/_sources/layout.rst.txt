Layout System
=============

The layout engine is pure math — zero renderer dependencies. It computes
rectangles (``Rect``) for every cell in the grid using sizing constraints,
padding, margins, and gaps.

Geometry primitives
-------------------

``Rect(x, y, width, height)``
   A rectangular region with properties ``left``, ``right``, ``top``,
   ``bottom``, ``top_left``, ``bottom_right``, ``size``, and method
   ``inset(left, top, right, bottom)``.

``Size(width, height)``
   Two-dimensional size. Read via ``rect.size``.

``Point(x, y)``
   Two-dimensional point.

``Edges(left=0, top=0, right=0, bottom=0)``
   Four-sided boundary specification. Created via:

   .. code-block:: python

      from reporting.layout.geometry import Edges

      Edges.all(15)                          # 15 on all four sides
      Edges.symmetric(horizontal=10, vertical=20)   # left=right=10, top=bottom=20
      Edges(left=5, top=10, right=5, bottom=15)     # individual sides

   Properties: ``horizontal`` (= left + right), ``vertical`` (= top + bottom).

Grid layout
-----------

.. code-block:: python

   slide.grid_layout(
       rows=3,
       cols=4,
       row_sizes=None,        # list[Sizing] — defaults to [Fill] * rows
       col_sizes=None,        # list[Sizing] — defaults to [Fill] * cols
       gap=0.0,               # spacing between rows and columns (px)
       padding=None,          # Edges — spacing around the grid content area
   )

Grid padding
~~~~~~~~~~~~

``padding`` is an ``Edges`` value that defines the space between the grid's
bounding box and the outermost cells. This is the outermost margin of the
grid content area.

.. code-block:: python

   slide.grid_layout(rows=2, cols=2, padding=Edges.all(20))
   # Each edge of the grid content is inset 20px from the slide content area.

Grid gap
~~~~~~~~

``gap`` is the uniform spacing between adjacent rows and between adjacent
columns. Gaps are not part of any cell — they are empty space.

.. code-block:: python

   slide.grid_layout(rows=2, cols=2, gap=10)
   # 10px between row 0 and row 1, 10px between col 0 and col 1.

----

Sizing
------

Each row and column can have its size specified individually.

``Fill``
   Takes a share of the remaining space. The default for all rows/columns.
   Multiple ``Fill`` rows divide the space proportionally by their weight.

   .. code-block:: python

      from reporting.layout.sizing import Fill, Px, Percent

      slide.grid_layout(
          rows=2,
          cols=3,
          row_sizes=[Fill(2), Fill(1)],  # first row gets 2/3, second gets 1/3
          col_sizes=[Px(100), Fill, Fill],   # first col fixed 100px, rest fill
      )

``Px(value)``
   Fixed pixel size.

   .. code-block:: python

      from reporting.layout.sizing import Px

      slide.grid_layout(rows=3, cols=1, row_sizes=[Px(60), Fill, Px(40)])

``Percent(value)``
   Percentage of available space.

   .. code-block:: python

      from reporting.layout.sizing import Percent

      slide.grid_layout(rows=1, cols=2, col_sizes=[Percent(30), Percent(70)])

----

Panel
-----

Every ``GridCell`` has a ``Panel`` that controls the cell's appearance and
behavior. Access it via the cell proxy:

.. code-block:: python

   slide[0, 0]._cell.panel     # access the underlying Panel object

Panel padding (internal)
~~~~~~~~~~~~~~~~~~~~~~~~

``panel.padding`` is an ``Edges`` value that defines space **inside** the
cell, between the cell's border and the content (text, image, etc.).

.. code-block:: python

   slide[0, 0]._cell.panel.padding = Edges.all(10)
   # Content is inset 10px from the cell's edges.

Panel margin (external)
~~~~~~~~~~~~~~~~~~~~~~~

``panel.margin`` is an ``Edges`` value that defines space **outside** the
cell, between the cell's border and adjacent cells or the grid boundary.

.. code-block:: python

   slide[0, 0]._cell.panel.margin = Edges.all(5)
   # 5px of empty space around this cell.

**Important:** Panel margin and panel padding work independently. Margin
pushes the cell away from neighbours; padding pushes the content inward
inside the cell.

Panel background color
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   slide[0, 0]._cell.panel.background_color = "#E8F0FE"

Panel alignment
~~~~~~~~~~~~~~~

.. code-block:: python

   from reporting.layout.panel import HAlign, VAlign

   slide[0, 0]._cell.panel.h_align = HAlign.CENTER
   slide[0, 0]._cell.panel.v_align = VAlign.MIDDLE

``HAlign`` values: ``LEFT``, ``CENTER``, ``RIGHT``, ``STRETCH`` (default)\
``VAlign`` values: ``TOP``, ``MIDDLE``, ``BOTTOM``, ``STRETCH`` (default)

----

Padding vs margin — visual diagram
----------------------------------

::

   ┌───────────────────────────────────────────────┐  ← slide content area
   │  ┌─ grid.padding ──────────────────────────┐  │
   │  │                                          │  │
   │  │  ┌── cell ───┐      ┌── cell ───┐       │  │
   │  │  │ ┌padding──┤ gap  │ ┌padding──┤       │  │
   │  │  │ │ content │      │ │ content │       │  │
   │  │  │ └─────────┤      │ └─────────┤       │  │
   │  │  │  ↑ margin │      │  ↑ margin │       │  │
   │  │  └───────────┘      └───────────┘       │  │
   │  │                                          │  │
   │  └──────────────────────────────────────────┘  │
   └───────────────────────────────────────────────┘

   grid.padding  → space between grid edge and cells
   gap           → space between adjacent cells
   panel.margin  → extra space around a specific cell
   panel.padding → space inside a cell around its content

----

Constraints
-----------

Each ``Panel`` has an optional ``Constraints`` object that clamps the
cell's final size.

.. code-block:: python

   from reporting.layout.constraints import Constraints, AxisConstraints

   slide[0, 0]._cell.panel.constraints = Constraints(
       width=AxisConstraints(min_size=50, max_size=300),
       height=AxisConstraints(min_size=20, max_size=200),
   )
