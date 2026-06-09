Themes (Built-in & Custom)
==========================

Este ejemplo cubre los temas incorporados (``CorporateTheme``,
``DarkTheme``, ``LightTheme``) y cómo crear un tema personalizado.

Código completo
---------------

.. literalinclude:: ../../examples/docs_themes.py
   :language: python
   :caption: ``examples/docs_themes.py``

Explicación
-----------

**1. Temas incorporados**

El framework incluye tres temas listos para usar:

.. code-block:: python

   from reporting.styles.theme import CorporateTheme, DarkTheme, LightTheme

   slide = Slide("Title", theme=CorporateTheme())
   slide = Slide("Title", theme=DarkTheme())
   slide = Slide("Title", theme=LightTheme())

.. list-table:: Temas incorporados
   :header-rows: 1
   :widths: 18 20 20 42

   * - Tema
     - Fondo
     - Tipografía
     - Paleta
   * - ``CorporateTheme``
     - Blanco
     - Arial
     - Azul/gris corporativo
   * - ``DarkTheme``
     - ``#1E1E1E``
     - Helvetica
     - Azul claro sobre oscuro
   * - ``LightTheme``
     - ``#FAFAFA``
     - Helvetica
     - Azul sobre gris claro

---

**2. Tema personalizado**

Se puede crear un tema desde cero con :class:`~reporting.styles.theme.Theme`:

.. code-block:: python

   from reporting.styles.theme import Theme
   from reporting.styles.colors import ColorPalette, Color
   from reporting.styles.typography import Typography, FontSpec
   from reporting.tablespec.style import TableStyle

   custom_theme = Theme(
       name="GreenFields",
       palette=ColorPalette(
           primary=Color.from_hex("#2E7D32"),
           secondary=Color.from_hex("#43A047"),
           background=Color.from_hex("#F1F8E9"),
           text_primary=Color.from_hex("#1B5E20"),
           # ... más colores
       ),
       typography=Typography(
           heading_1=FontSpec(family="Times-Bold", size=30, bold=False,
                              color="#1B5E20"),
           body=FontSpec(family="Times-Roman", size=11, color="#333333"),
       ),
       table_style=TableStyle(),
       footer=FooterConfig(center_text="GreenFields Report"),
   )

   slide = Slide("Title", theme=custom_theme)

.. list-table:: Componentes de ``Theme``
   :header-rows: 1
   :widths: 18 16 66

   * - Componente
     - Tipo
     - Descripción
   * - ``name``
     - ``str``
     - Nombre identificativo del tema.
   * - ``palette``
     - ``ColorPalette``
     - Colores primario, secundario, acento, fondo,
       texto, borde, error, warning, success.
   * - ``typography``
     - ``Typography``
     - Fuentes para headings (3 niveles), body,
       caption, code, mono.
   * - ``table_style``
     - ``TableStyle``
     - Estilos por defecto de tablas.
   * - ``footer``
     - ``FooterConfig``
     - Configuración del pie de página.

---

**3. ColorPalette**

:class:`~reporting.styles.colors.ColorPalette` agrupa los colores del tema:

.. list-table:: Campos de ``ColorPalette``
   :header-rows: 1
   :widths: 18 12 70

   * - Campo
     - Uso
     - Ejemplo
   * - ``primary``
     - Títulos, acentos principales
     - ``#1F4E79``
   * - ``secondary``
     - Subtítulos, elementos secundarios
     - ``#2E75B6``
   * - ``accent``
     - Destacar elementos
     - ``#ED7D31``
   * - ``background``
     - Fondo de diapositiva
     - ``#FFFFFF``
   * - ``text_primary``
     - Texto principal
     - ``#333333``
   * - ``text_secondary``
     - Texto secundario / pies
     - ``#666666``
   * - ``border``
     - Bordes y separadores
     - ``#D9D9D9``
   * - ``error``
     - Valores de error
     - ``#C00000``
   * - ``warning``
     - Valores de advertencia
     - ``#FFC000``
   * - ``success``
     - Valores correctos
     - ``#70AD47``

Los colores se crean con ``Color.from_hex("#RRGGBB")`` o se
obtienen del diccionario ``NAMED_COLORS`` (``from
reporting.styles.colors import NAMED_COLORS``).

---

**4. Tema desde Document**

Se puede asignar un tema al documento para que todas las
diapositivas lo hereden automáticamente:

.. code-block:: python

   doc = Document("Title", theme=DarkTheme())
   slide = doc.new_slide("Slide")  # hereda DarkTheme

Cada ``Slide`` también acepta un ``theme`` explícito que
sobrescribe el del documento.

---

**5. Slide types en el tema**

Cada tema define tres :class:`~reporting.slide_type.SlideTypeConfig`:

.. list-table:: Slide types incorporados
   :header-rows: 1
   :widths: 14 18 20 48

   * - Tipo
     - ``title_panel_height``
     - Footer
     - Uso
   * - ``"default"``
     - 60 px
     - Activado
     - Diapositiva normal.
   * - ``"title"``
     - 80 px
     - Desactivado
     - Diapositiva de portada / sección.
   * - ``"blank"``
     - 0 px
     - Desactivado
     - Sin panel de título ni pie.

Se seleccionan con el parámetro ``slide_type``:

.. code-block:: python

   slide = Slide("Cover", slide_type="title")

Salida del ejemplo
------------------

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
   :alt: Custom GreenFields theme — page 4

.. image:: _images/docs_themes_p5.png
   :width: 640px
   :alt: Theme via document — page 5
