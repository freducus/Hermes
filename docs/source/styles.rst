Styles & Theming
================

The styling system provides colors, typography, table styles, and complete
themes.

Colors
------

.. code-block:: python

   from reporting.styles.colors import Color, ColorPalette

   c = Color.from_hex("#1F4E79")          # from hex string
   c = Color.from_rgb(31, 78, 121)        # from RGB integers
   c.rgba                                  # → "rgba(31,78,121,1.0)"

   palette = ColorPalette(
       primary=Color.from_hex("#1F4E79"),
       secondary=Color.from_hex("#2E75B6"),
       accent=Color.from_hex("#ED7D31"),
       background=Color.from_hex("#FFFFFF"),
       text_primary=Color.from_hex("#333333"),
       text_secondary=Color.from_hex("#666666"),
       border=Color.from_hex("#D9D9D9"),
       error=Color.from_hex("#C00000"),
       warning=Color.from_hex("#FFC000"),
       success=Color.from_hex("#70AD47"),
   )

Typography
----------

.. code-block:: python

   from reporting.styles.typography import Typography, FontSpec

   typography = Typography(
       heading_1=FontSpec(family="Arial", size=28.0, bold=True, color="#1F4E79"),
       heading_2=FontSpec(family="Arial", size=22.0, bold=True, color="#1F4E79"),
       heading_3=FontSpec(family="Arial", size=16.0, bold=True, color="#2E75B6"),
       body=FontSpec(family="Arial", size=11.0, color="#333333"),
       caption=FontSpec(family="Arial", size=9.0, color="#666666"),
       code=FontSpec(family="Courier New", size=10.0, color="#333333"),
       mono=FontSpec(family="Courier New", size=10.0, color="#333333"),
   )

TableStyle
----------

.. code-block:: python

   from reporting.tablespec.style import TableStyle

   table_style = TableStyle(
       zebra=True,
       even_row_color="#F3F3F3",
       odd_row_color="#FFFFFF",
       header_background="#4472C4",
       header_text_color="#FFFFFF",
       border_color="#D9D9D9",
       font_size=10.0,
       header_font_size=11.0,
       font_family="Helvetica",
       padding=4.0,
   )

Themes
------

Three built-in themes are provided:

``CorporateTheme``
   Blue/orange palette, Arial typography. Professional look.

   .. image:: _images/theme_demo_p1.png
      :width: 320px
      :alt: Corporate theme

``DarkTheme``
   Cyan/amber on dark gray, Helvetica typography. Presentation style.

   .. image:: _images/theme_demo_p2.png
      :width: 320px
      :alt: Dark theme

``LightTheme``
   Blue/teal on light gray, Helvetica typography. Clean minimal look.

   .. image:: _images/theme_demo_p3.png
      :width: 320px
      :alt: Light theme

Using a theme:

.. code-block:: python

   from reporting.styles.theme import CorporateTheme, DarkTheme, LightTheme
   from reporting.document import Document
   from reporting.slide import Slide

   doc = Document(title="My Report", theme=CorporateTheme())
   slide = Slide("Title", theme=DarkTheme())

   # Query theme properties
   heading = slide.theme.get_heading_style(1)
   # → FontSpec(family="Helvetica", size=28.0, bold=True, color="#...")

Note: themes define the visual defaults, but elements do not automatically
consume them yet — theme integration with auto-styling of text/table
elements is planned.
