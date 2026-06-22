Title Panel
===========

The slide title panel is controlled via the ``title_panel`` attribute
on each :class:`~reporting.slide.Slide`. When enabled, the renderer
draws the title and subtitle at the top of the slide.

Full example
------------

.. literalinclude:: ../../examples/docs_header_footer.py
   :language: python
   :caption: ``examples/docs_header_footer.py``

Explanation
-----------

**Title and subtitle properties**

Set the title and subtitle after creating the slide:

.. code-block:: python

   from reporting.slide import Slide

   slide = Slide()
   slide.title = "My Title"
   slide.subtitle = "Optional subtitle"

Both ``title`` and ``subtitle`` accept either a plain ``str`` or a
:class:`~reporting.title_config.TitleText` /
:class:`~reporting.title_config.SubtitleText` with custom styling:

.. code-block:: python

   from reporting.title_config import TitleText, SubtitleText

   slide.title = TitleText("Custom", font_size=24, bold=True, color="#C00000")
   slide.subtitle = SubtitleText("Styled subtitle", italic=True)

**TitlePanel**

:class:`~reporting.title_config.TitlePanel` has a single field:

.. list-table:: ``TitlePanel`` fields
   :header-rows: 1
   :widths: 24 14 62

   * - Field
     - Type
     - Description
   * - ``enabled``
     - ``bool``
     - Render the title+subtitle at the top of the slide
       (default ``False``).

Enable the title panel:

.. code-block:: python

   slide.title_panel.enabled = True

When enabled, the title and subtitle are drawn as inline text at the
top of the slide. The grid uses the full slide area.

**Footer (removed)**

Previous versions included a ``FooterPanel`` with automatic footer
grid, page numbers, and logo. This has been removed in favour of
placing footer content directly in the slide grid when needed.
