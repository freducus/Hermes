Padding & Margin example
========================

``examples/padding_margin.py`` is a visual demonstration of the layout
spacing system. It generates a 5-slide PDF that compares:

1. **Grid padding** — ``Edges.all(5)`` vs ``Edges.all(30)``
2. **Grid gap** — ``gap=2`` vs ``gap=20``
3. **Panel padding** — ``Edges()`` (no padding) vs ``Edges.all(20)``
4. **Panel margin** — each cell has ``margin=Edges.all(8)``
5. **Combined** — mixing padding, margin, and gap on the same slide

Run it:

.. code-block:: bash

   python examples/padding_margin.py

Visual diagram of the spacing concepts
---------------------------------------

::

   ┌── grid.padding ────────────────────────────┐
   │  ┌── cell ───┐  gap  ┌── cell ───┐         │
   │  │ ┌padding──┤       │ ┌padding──┤         │
   │  │ │ content │       │ │ content │         │
   │  │ └─────────┤       │ └─────────┤         │
   │  │ ← margin→ │       │ ← margin→ │         │
   │  └───────────┘       └───────────┘         │
   └────────────────────────────────────────────┘

- ``grid.padding`` — outermost space around all cells
- ``gap`` — uniform space between adjacent cells
- ``panel.margin`` — extra space added around a specific cell
- ``panel.padding`` — space inside the cell around its content

Code excerpt
------------

.. code-block:: python

   from reporting.layout.geometry import Edges

   # Grid-level spacing
   slide.grid_layout(rows=2, cols=2, gap=12, padding=Edges.all(20))

   # Cell-level spacing
   slide[0, 0]._cell.panel.padding = Edges.all(10)
   slide[0, 0]._cell.panel.margin  = Edges.all(5)

Panel padding and margin are ``Edges`` objects — you can set each side
individually:

.. code-block:: python

   # Different padding on each side
   slide[0, 0]._cell.panel.padding = Edges(left=5, top=10, right=5, bottom=15)

   # Symmetric (horizontal vs vertical)
   slide[0, 0]._cell.panel.margin = Edges.symmetric(horizontal=10, vertical=20)

Output slides
-------------

Slide 1 — Grid padding (5 vs 30):

.. image:: ../_images/padding_margin_p1.png
   :width: 480px
   :alt: Grid padding comparison

Slide 2 — Narrow gap (2px):

.. image:: ../_images/padding_margin_p2.png
   :width: 480px
   :alt: Grid gap narrow

Slide 3 — Wide gap (20px):

.. image:: ../_images/padding_margin_p3.png
   :width: 480px
   :alt: Grid gap wide

Slide 4 — Panel padding (0 vs 20):

.. image:: ../_images/padding_margin_p4.png
   :width: 480px
   :alt: Panel padding comparison

Slide 5 — Combined layout:

.. image:: ../_images/padding_margin_p5.png
   :width: 480px
   :alt: Combined padding margin and gap
