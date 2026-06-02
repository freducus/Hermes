"""Tests for TableSpec core functionality."""

from __future__ import annotations

import pytest

from reporting.tablespec import (
    Cell,
    Column,
    Row,
    TableBuilder,
    TableSpec,
)
from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    DuplicateColumnError,
    InvalidColumnError,
    InvalidRowError,
    InvalidSpanError,
    TableSpecError,
)
from reporting.tablespec.style import TableStyle


class TestTableSpecCreation:
    def test_empty_table(self):
        t = TableSpec()
        assert t.columns == []
        assert t.rows == []

    def test_columns_from_constructor(self):
        t = TableSpec(columns=[Column("a"), Column("b")])
        assert len(t.columns) == 2
        assert t.columns[0].name == "a"

    def test_duplicate_columns_raises(self):
        with pytest.raises(DuplicateColumnError):
            TableSpec(columns=[Column("x"), Column("x")])

    def test_add_column_chaining(self):
        t = TableSpec().add_column("a").add_column("b")
        assert len(t.columns) == 2


class TestTableSpecAddRow:
    def test_positional_values(self):
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.add_row(1, 2)
        assert len(t.rows) == 1
        assert t.rows[0].cells[0].value == 1
        assert t.rows[0].cells[1].value == 2

    def test_wrong_value_count_raises(self):
        t = TableSpec(columns=[Column("a"), Column("b")])
        with pytest.raises(InvalidRowError):
            t.add_row(1, 2, 3)

    def test_keyword_values(self):
        t = TableSpec(columns=[Column("mach"), Column("efficiency")])
        t.add_row(mach=0.8, efficiency=0.92)
        assert t.rows[0].cells[0].value == 0.8
        assert t.rows[0].cells[1].value == 0.92

    def test_keyword_unknown_column_raises(self):
        t = TableSpec(columns=[Column("a")])
        with pytest.raises(ColumnNotFoundError):
            t.add_row(x=1)

    def test_mixed_positional_and_keyword_raises(self):
        t = TableSpec(columns=[Column("a")])
        with pytest.raises(InvalidRowError):
            t.add_row(1, a=2)

    def test_auto_text_from_format(self):
        t = TableSpec(columns=[Column("x", format="{:.2f}")])
        t.add_row(3.14159)
        assert t.rows[0].cells[0].text == "3.14"

    def test_auto_text_from_formatter(self):
        t = TableSpec(columns=[Column("x", formatter=lambda v: f"{v*100:.0f}%")])
        t.add_row(0.95)
        assert t.rows[0].cells[0].text == "95%"


class TestTableSpecCellAccess:
    def test_modify_existing_cell(self):
        t = TableSpec(columns=[Column("a")])
        t.add_row(1)
        t.cell(row=0, col=0, value=99, colspan=1)
        assert t.rows[0].cells[0].value == 99

    def test_cell_out_of_range_raises(self):
        t = TableSpec(columns=[Column("a")])
        with pytest.raises(InvalidRowError):
            t.cell(row=5, col=0)

    def test_invalid_span_raises(self):
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.add_row(1, 2)
        with pytest.raises(InvalidSpanError):
            t.cell(row=0, col=0, colspan=5)

    def test_cell_with_style(self):
        from reporting.tablespec.style import CellStyle

        t = TableSpec(columns=[Column("a")])
        t.add_row(1)
        style = CellStyle(background_color="#FF0000")
        t.cell(row=0, col=0, style=style)
        assert t.rows[0].cells[0].style is style


class TestTableSpecColumnAccess:
    def test_column_by_name(self):
        t = TableSpec(columns=[Column("mach")])
        col = t.column("mach")
        assert col.name == "mach"

    def test_column_not_found_raises(self):
        t = TableSpec()
        with pytest.raises(ColumnNotFoundError):
            t.column("nonexistent")

    def test_column_format_chaining(self):
        t = TableSpec(columns=[Column("x")])
        t.column("x").set_format("{:.1%}")
        assert t.columns[0].format == "{:.1%}"


class TestTableSpecGrouping:
    def test_group_stamps_rows(self):
        t = TableSpec(columns=[Column("x")])
        t.group("Group A").add_row(1).add_row(2)
        t.group("Group B").add_row(3)
        assert t.rows[0].group == "Group A"
        assert t.rows[1].group == "Group A"
        assert t.rows[2].group == "Group B"

    def test_no_group_is_none(self):
        t = TableSpec(columns=[Column("x")])
        t.add_row(1)
        assert t.rows[0].group is None


class TestTableSpecConditionalFormatting:
    def test_highlight_max(self):
        t = TableSpec(columns=[Column("val")])
        t.add_row(10).add_row(20).add_row(30)
        t.highlight_max("val")
        assert t.rows[2].cells[0].background_color == t.style.highlight_max_color

    def test_highlight_min(self):
        t = TableSpec(columns=[Column("val")])
        t.add_row(10).add_row(20).add_row(30)
        t.highlight_min("val")
        assert t.rows[0].cells[0].background_color == t.style.highlight_min_color

    def test_heatmap(self):
        t = TableSpec(columns=[Column("val")])
        t.add_row(0.0).add_row(0.5).add_row(1.0)
        t.heatmap("val")
        colors = [r.cells[0].background_color for r in t.rows]
        assert colors[0] == "#00FF00"  # min = pure green
        assert colors[2] == "#FF0000"  # max = pure red
        assert colors[1] == "#7F7F00"  # mid = yellow-ish

    def test_zebra_enables_style(self):
        t = TableSpec(columns=[Column("x")])
        t.zebra()
        assert t.style.zebra is True

    def test_highlight_unknown_column(self):
        t = TableSpec(columns=[Column("x")])
        with pytest.raises(ColumnNotFoundError):
            t.highlight_max("y")


class TestTableSpecExport:
    def test_to_dict_returns_columns_and_rows(self):
        t = TableSpec(columns=[Column("a")])
        t.add_row(42)
        d = t.to_dict()
        assert "columns" in d
        assert "rows" in d
        assert len(d["columns"]) == 1
        assert len(d["rows"]) == 1

    def test_to_json_returns_string(self):
        t = TableSpec(columns=[Column("a")])
        t.add_row(1)
        s = t.to_json()
        assert isinstance(s, str)
        assert '"a"' in s

    def test_to_records(self):
        t = TableSpec(columns=[Column("name"), Column("val")])
        t.add_row("foo", 99)
        recs = t.to_records()
        assert recs == [{"name": "foo", "val": 99}]

    def test_to_records_uses_display_text(self):
        t = TableSpec(columns=[Column("pct", format="{:.1%}")])
        t.add_row(0.856)
        recs = t.to_records()
        assert recs[0]["pct"] == "85.6%"


class TestTableSpecFromDataframe:
    def test_basic(self):
        import pandas as pd

        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        t = TableSpec.from_dataframe(df)
        assert len(t.columns) == 2
        assert len(t.rows) == 2
        assert t.rows[0].cells[0].value == 1

    def test_accepts_kwargs(self):
        import pandas as pd

        df = pd.DataFrame({"a": [10]})
        t = TableSpec.from_dataframe(df, style=TableStyle(zebra=True))
        assert t.style.zebra is True


class TestTableSpecFromRecords:
    def test_basic(self):
        recs = [{"name": "A", "val": 1}, {"name": "B", "val": 2}]
        t = TableSpec.from_records(recs)
        assert len(t.columns) == 2
        assert len(t.rows) == 2

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            TableSpec.from_records([])


class TestTableSpecFromDataclasses:
    def test_basic(self):
        import dataclasses

        @dataclasses.dataclass
        class Point:
            x: float
            y: float

        pts = [Point(1.0, 2.0), Point(3.0, 4.0)]
        t = TableSpec.from_dataclasses(pts)
        assert len(t.columns) == 2
        assert len(t.rows) == 2
        assert t.columns[0].label == "X"  # _ replaced, title cased

    def test_empty_raises(self):
        import dataclasses

        @dataclasses.dataclass
        class Point:
            x: float

        with pytest.raises(ValueError):
            TableSpec.from_dataclasses([])


class TestTableSpecToDataframe:
    def test_roundtrip(self):
        import pandas as pd

        df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        t = TableSpec.from_dataframe(df1)
        df2 = t.to_dataframe()
        assert df1.equals(df2)


class TestTableBuilder:
    def test_basic_build(self):
        t = (
            TableBuilder()
            .column("x")
            .column("y")
            .row(1, 2)
            .row(3, 4)
            .build()
        )
        assert len(t.columns) == 2
        assert len(t.rows) == 2

    def test_zebra(self):
        t = TableBuilder().column("x").row(1).zebra().build()
        assert t.style.zebra is True

    def test_highlights(self):
        t = (
            TableBuilder()
            .column("val")
            .row(10)
            .row(20)
            .highlight_max("val")
            .build()
        )
        assert t.rows[1].cells[0].background_color == t.style.highlight_max_color

    def test_no_columns_raises(self):
        with pytest.raises(TableSpecError):
            TableBuilder().build()

    def test_chaining_returns_builder(self):
        b = TableBuilder().column("x").column("y")
        assert isinstance(b, TableBuilder)
