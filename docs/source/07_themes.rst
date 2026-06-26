Themes (Built-in & Custom)
==========================

This page covers the built-in themes (``CorporateTheme``,
``DarkTheme``, ``LightTheme``), how to create a custom theme,
and how to register them for auto-discovery.

Full example
------------

.. literalinclude:: ../../examples/docs_themes.py
   :language: python
   :caption: ``examples/docs_themes.py``

Explanation
-----------

**1. Built-in themes**

The framework ships with three ready-to-use themes:

.. code-block:: python

   from reporting.styles.theme import CorporateTheme, DarkTheme, LightTheme

   slide = Slide("Title", theme=CorporateTheme())
   slide = Slide("Title", theme=DarkTheme())
   slide = Slide("Title", theme=LightTheme())

.. list-table:: Built-in themes
   :header-rows: 1
   :widths: 18 20 20 42

   * - Theme
     - Background
     - Typography
     - Palette
   * - ``CorporateTheme``
     - White
     - Arial
     - Corporate blue/grey
   * - ``DarkTheme``
     - ``#1E1E1E``
     - Helvetica
     - Light blue on dark
   * - ``LightTheme``
     - ``#FAFAFA``
     - Helvetica
     - Blue on light grey

---

**2. Theme components**

A :class:`~reporting.styles.theme.Theme` bundles the full visual identity:

.. list-table:: ``Theme`` fields
   :header-rows: 1
   :widths: 18 18 64

   * - Field
     - Type
     - Description
   * - ``name``
     - ``str``
     - Theme identifier.
   * - ``page_size``
     - ``tuple[float, float]``
     - Default slide size ``(width, height)`` in px
       (default ``(960, 540)``).
   * - ``palette``
     - ``ColorPalette``
     - Primary, secondary, accent, background,
       text, border, error, warning, success.
   * - ``typography``
     - ``Typography``
     - Font specs for headings (3 levels), body,
       caption, code, mono.
   * - ``table_style``
     - ``TableStyle``
     - Default table styling.
   * - ``footer_panel``
     - ``FooterPanel``
     - Default footer configuration.

---

**3. Creating a custom theme**

A theme is created by subclassing ``Theme`` and calling
``super().__init__()`` with the desired configuration:

.. code-block:: python

   from reporting.styles.theme import Theme
   from reporting.styles.colors import ColorPalette, Color
   from reporting.styles.typography import Typography, FontSpec
   from reporting.tablespec.style import TableStyle

   class OceanTheme(Theme):
       def __init__(self) -> None:
           palette = ColorPalette(
               primary=Color.from_hex("#006994"),
               secondary=Color.from_hex("#00B4D8"),
               accent=Color.from_hex("#FF6B35"),
               background=Color.from_hex("#E0F7FA"),
               text_primary=Color.from_hex("#003B5C"),
               text_secondary=Color.from_hex("#0077B6"),
               border=Color.from_hex("#90E0EF"),
               error=Color.from_hex("#C00000"),
               warning=Color.from_hex("#FFC000"),
               success=Color.from_hex("#2E7D32"),
           )
           typography = Typography(
               heading_1=FontSpec("Helvetica", 28, bold=True, color="#006994"),
               heading_2=FontSpec("Helvetica", 22, bold=True, color="#00B4D8"),
               body=FontSpec("Helvetica", 11, color="#003B5C"),
               caption=FontSpec("Helvetica", 9, italic=True, color="#0077B6"),
           )
           super().__init__(
               name="Ocean",
               page_size=(960, 540),
               palette=palette,
               typography=typography,
               table_style=TableStyle(),
               footer_panel=FooterPanel(center_text="Ocean Report"),
           )

Using the custom theme:

.. code-block:: python

   slide = Slide("Marine Life", theme=OceanTheme())
   # or by name (if registered):
   slide = Slide("Marine Life", theme="ocean")

---

**4. Theme registration and auto-discovery**

Use the ``@Theme.register()`` decorator to make a theme
discoverable by name:

.. code-block:: python

   @Theme.register("ocean")
   class OceanTheme(Theme):
       ...

Themes can then be loaded from a Python file:

.. code-block:: python

   Theme.load_themes("path/to/themes.py")
   theme = Theme.get_registered("ocean")  # returns the class

Without registration, instantiate the class directly:

.. code-block:: python

   slide = Slide("Title", theme=OceanTheme())

---

**5. Theme applied via Document**

A theme can be set on the ``Document`` so all slides inherit it:

.. code-block:: python

   doc = Document("Report", theme=DarkTheme())
   slide = doc.new_slide("Slide")  # inherits DarkTheme

Per-slide overrides are always respected:

.. code-block:: python

   slide = Slide("Custom", theme=CustomTheme())  # overrides doc theme

---

Example output
--------------

.. image:: _images/docs_themes_p1.png
   :width: 640px
   :alt: Corporate theme — page 1

.. image:: _images/docs_themes_p2.png
   :width: 640px
   :alt: Dark theme — page 2

.. image:: _images/docs_themes_p3.png
   :width: 640px
   :alt: Light theme — page 3

.. image:: _images/docs_themes_p4.png
   :width: 640px
   :alt: Ocean theme — page 4

.. image:: _images/docs_themes_p6.png
   :width: 640px
   :alt: Registered theme via name — page 6

.. image:: _images/docs_themes_p7.png
   :width: 640px
   :alt: Theme via document — page 7
