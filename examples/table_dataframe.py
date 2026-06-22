"""Example 6: DataFrame roundtrip — from_dataframe() and to_dataframe()."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from reporting.document import Document
from reporting.slide import Slide
from reporting.tablespec import Column, TableSpec, TableCell, TableRow
from reporting.renderers.pdf.renderer import PDFRenderer


def main() -> None:
    doc = Document(title="DataFrame Tables", author="Engineer")

    slide = Slide()
    slide.title = "From DataFrame"
    slide.grid_layout(rows=1, cols=1)

    df = pd.DataFrame({
        "City": ["New York", "Los Angeles", "Chicago", "Houston"],
        "Population (M)": [8.4, 3.8, 2.7, 2.3],
        "Area (km²)": [783.8, 1299.0, 589.0, 1707.0],
    })
    t = TableSpec.from_dataframe(df)
    header = TableRow(cells=[TableCell(value=c, text=c) for c in df.columns])
    t.rows.insert(0, header)
    t.zebra()
    slide[0, 0].table(t)
    doc.add_slide(slide)

    out = Path(__file__).parent / "table_dataframe"
    PDFRenderer().render_document(doc, str(out) + ".pdf")
    print("Generated table_dataframe.pdf")


if __name__ == "__main__":
    main()
