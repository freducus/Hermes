"""Tests for the advanced table engine — range parser, TableSpec API, styles, conditionals."""

from __future__ import annotations

import pytest

from reporting.tablespec import (
    Column,
    TableSpec,
    TableCell,
    TableRow,
    cell,
    parse_coord,
    parse_range,
)
from reporting.tablespec.style import TableStyle
from reporting.tablespec.exceptions import (
    ColumnNotFoundError,
    InvalidRowError,
    InvalidSpanError,
    TableSpecError,
)
from reporting.tablespec.range_parser import RangeError, col_to_index, index_to_col
from reporting.tablespec.style import CellStyle, ColumnStyle, RowStyle, TableStyle


# ---------------------------------------------------------------------------
# Range parser
# ---------------------------------------------------------------------------

class TestParseCoord:
    def test_a1(self) -> None:
        assert parse_coord("A1") == (0, 0)

    def test_b2(self) -> None:
        assert parse_coord("B2") == (1, 1)

    def test_z1(self) -> None:
        assert parse_coord("Z1") == (0, 25)

    def test_aa1(self) -> None:
        assert parse_coord("AA1") == (0, 26)

    def test_az1(self) -> None:
        assert parse_coord("AZ1") == (0, 51)

    def test_big_coord(self) -> None:
        assert parse_coord("AB123") == (122, 27)

    def test_lowercase(self) -> None:
        assert parse_coord("a1") == (0, 0)

    def test_invalid_raises(self) -> None:
        with pytest.raises(RangeError):
            parse_coord("")
        with pytest.raises(RangeError):
            parse_coord("1")
        with pytest.raises(RangeError):
            parse_coord("A")
        with pytest.raises(RangeError):
            parse_coord("123")


class TestParseRange:
    def test_a1_d4(self) -> None:
        assert parse_range("A1:D4") == (0, 0, 3, 3)

    def test_reversed(self) -> None:
        assert parse_range("D4:A1") == (0, 0, 3, 3)

    def test_single_cell(self) -> None:
        assert parse_range("B2:B2") == (1, 1, 1, 1)

    def test_full_column(self) -> None:
        r1, c1, r2, c2 = parse_range("A:A")
        assert c1 == 0 and c2 == 0
        assert r1 <= r2

    def test_full_row(self) -> None:
        r1, c1, r2, c2 = parse_range("1:1")
        assert r1 == 0 and r2 == 0
        assert c1 <= c2

    def test_col_range(self) -> None:
        r1, c1, r2, c2 = parse_range("A:C")
        assert c1 == 0 and c2 == 2
        assert r1 <= r2

    def test_invalid_raises(self) -> None:
        with pytest.raises(RangeError):
            parse_range("")


class TestColToIndex:
    def test_a(self) -> None:
        assert col_to_index("A") == 0

    def test_z(self) -> None:
        assert col_to_index("Z") == 25

    def test_aa(self) -> None:
        assert col_to_index("AA") == 26

    def test_az(self) -> None:
        assert col_to_index("AZ") == 51

    def test_ba(self) -> None:
        assert col_to_index("BA") == 52


class TestIndexToCol:
    def test_0(self) -> None:
        assert index_to_col(0) == "A"

    def test_25(self) -> None:
        assert index_to_col(25) == "Z"

    def test_26(self) -> None:
        assert index_to_col(26) == "AA"

    def test_51(self) -> None:
        assert index_to_col(51) == "AZ"


# ---------------------------------------------------------------------------
# Fluent row() API
# ---------------------------------------------------------------------------

class TestFluentRow:
    def test_plain_values(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.row(1, 2)
        assert len(t.rows) == 1
        assert t.rows[0].cells[0].value == 1
        assert t.rows[0].cells[1].value == 2

    def test_mixed_cell_and_plain(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.row(cell("Header", colspan=2))
        assert len(t.rows) == 1
        assert t.rows[0].cells[0].value == "Header"
        assert t.rows[0].cells[0].colspan == 2

    def test_cell_with_style_via_kwargs(self) -> None:
        t = TableSpec(columns=[Column("a")])
        t.row(cell("Alert", style=CellStyle(bold=True, text_color="red")))
        cs = t.rows[0].cells[0].style
        assert cs is not None
        assert cs.bold is True
        assert cs.text_color == "#FF0000"


# ---------------------------------------------------------------------------
# Excel-style API
# ---------------------------------------------------------------------------

class TestExcelAPI:
    def test_setitem_str(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.row(0, 0)
        t["A1"] = 99
        assert t.rows[0].cells[0].value == 99

    def test_setitem_tuple(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.row(0, 0)
        t[0, 1] = 42
        assert t.rows[0].cells[1].value == 42

    def test_getitem_str(self) -> None:
        t = TableSpec(columns=[Column("a")])
        t.row("hello")
        assert t["A1"] == "hello"

    def test_getitem_tuple(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.row(10, 20)
        assert t[0, 1] == 20


class TestMerge:
    def test_merge_cols(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b"), Column("c")])
        t.row("X", "Y", "Z")
        t.merge("A1:C1")
        assert t.rows[0].cells[0].colspan == 3

    def test_merge_rows(self) -> None:
        t = TableSpec(columns=[Column("a")])
        t.row("A").row("B").row("C")
        t.merge("A1:A3")
        assert t.rows[0].cells[0].rowspan == 3


class TestRangeStyle:
    def test_style_range(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b")])
        t.row("x", "y")
        t.apply_style("A1:B1", background_color="red", bold=True)
        c0 = t.rows[0].cells[0]
        c1 = t.rows[0].cells[1]
        assert c0.style is not None
        assert c0.style.background_color == "#FF0000"
        assert c0.style.bold is True
        assert c1.style is not None
        assert c1.style.background_color == "#FF0000"

    def test_range_selector(self) -> None:
        t = TableSpec(columns=[Column("a"), Column("b"), Column("c")])
        t.row("a1", "b1", "c1")
        t.row("a2", "b2", "c2")
        t.range("A1:C1").style(background_color="#003366").merge()
        assert t.rows[0].cells[0].colspan == 3
        assert t.rows[0].cells[0].style is not None
        assert t.rows[0].cells[0].style.background_color == "#003366"


# ---------------------------------------------------------------------------
# resolve_cell_style — style cascade
# ---------------------------------------------------------------------------

class TestStyleCascade:
    def test_table_defaults(self) -> None:
        ts = TableStyle(font_name="Courier", font_size=8.0)
        t = TableSpec(columns=[Column("x")], style=ts)
        t.row(42)
        resolved = t.resolve_cell_style(0, 0)
        assert resolved.font_name == "Courier"
        assert resolved.font_size == 8.0

    def test_cell_style_overrides(self) -> None:
        t = TableSpec(columns=[Column("x")])
        t.row(cell(42, style=CellStyle(bold=True, background_color="yellow")))
        resolved = t.resolve_cell_style(0, 0)
        assert resolved.bold is True
        assert resolved.background_color == "#FFFF00"

    def test_column_style_applied(self) -> None:
        col = Column("x", style=ColumnStyle(align_h="right", font_size=14.0))
        t = TableSpec(columns=[col])
        t.row(42)
        resolved = t.resolve_cell_style(0, 0)
        assert resolved.align_h == "right"
        assert resolved.font_size == 14.0

    def test_row_style_applied(self) -> None:
        row_style = RowStyle(background_color="#EEE")
        t = TableSpec(columns=[Column("x")])
        t.rows.append(TableRow(
            cells=[TableCell(value=42)],
            style=row_style,
        ))
        resolved = t.resolve_cell_style(0, 0)
        assert resolved.background_color == "#EEE"


# ---------------------------------------------------------------------------
# Conditional formatting (deferred)
# ---------------------------------------------------------------------------

class TestDeferredConditional:
    def test_add_condition_matches(self) -> None:
        t = TableSpec(columns=[Column("temp")])
        t.row(100).row(200).row(300)
        t.add_condition("temp", lambda v: v > 250, background_color="red")
        resolved = t.resolve_cell_style(2, 0)
        assert resolved.background_color == "#FF0000"

    def test_add_condition_no_match(self) -> None:
        t = TableSpec(columns=[Column("temp")])
        t.row(100).row(200)
        t.add_condition("temp", lambda v: v > 500, background_color="red")
        resolved = t.resolve_cell_style(0, 0)
        assert resolved.background_color is None or resolved.background_color == t.style.border_color

    def test_add_heatmap(self) -> None:
        t = TableSpec(columns=[Column("val")], style=TableStyle(header_rows=0))
        t.row(0.0).row(0.5).row(1.0)
        t.add_heatmap("val", min_color="#FFFFCC", max_color="#FF0000")
        r0 = t.resolve_cell_style(0, 0)
        r2 = t.resolve_cell_style(2, 0)
        assert r0.background_color is not None
        assert r2.background_color is not None

    def test_add_highlight_max(self) -> None:
        t = TableSpec(columns=[Column("val")])
        t.row(10).row(20).row(30)
        t.add_highlight_max("val", color="#C6EFCE")
        resolved = t.resolve_cell_style(2, 0)
        assert resolved.background_color == "#C6EFCE"

    def test_add_highlight_min(self) -> None:
        t = TableSpec(columns=[Column("val")], style=TableStyle(header_rows=0))
        t.row(10).row(20).row(30)
        t.add_highlight_min("val", color="#FFC7CE")
        resolved = t.resolve_cell_style(0, 0)
        assert resolved.background_color == "#FFC7CE"


# ---------------------------------------------------------------------------
# Multilevel headers via header_rows
# ---------------------------------------------------------------------------

class TestMultilevelHeaders:
    def test_header_rows_field(self) -> None:
        t = TableSpec(columns=[Column("x")])
        assert t.style.header_rows == 1

    def test_header_rows_configurable(self) -> None:
        ts = TableStyle(header_rows=2)
        t = TableSpec(columns=[Column("x")], style=ts)
        assert t.style.header_rows == 2


# ---------------------------------------------------------------------------
# Dataframe roundtrip
# ---------------------------------------------------------------------------

class TestDataframeRoundtrip:
    def test_roundtrip(self) -> None:
        import pandas as pd

        df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        t = TableSpec.from_dataframe(df1)
        df2 = t.to_dataframe()
        assert df1.equals(df2)


# ---------------------------------------------------------------------------
# Misc / edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_table_no_crash(self) -> None:
        t = TableSpec()
        assert t.columns == []
        assert t.rows == []

    def test_single_cell_table(self) -> None:
        t = TableSpec(columns=[Column("x")])
        t.row(42)
        assert t.rows[0].cells[0].value == 42

    def test_cell_helper_defaults(self) -> None:
        c = cell("hello")
        assert c.value == "hello"
        assert c.colspan == 1
        assert c.rowspan == 1
        assert c.style is None

    def test_cell_helper_with_style_kwargs(self) -> None:
        c = cell("bold one", bold=True, background_color="blue")
        assert c.value == "bold one"
        assert c.style is not None
        assert c.style.bold is True
        assert c.style.background_color == "#0000FF"

    def test_display_text_property(self) -> None:
        c = TableCell(value=3.14, text="π")
        assert c.display_text == "π"
        c2 = TableCell(value=42)
        assert c2.display_text == "42"
        c3 = TableCell()
        assert c3.display_text == ""

    def test_repr(self) -> None:
        c = TableCell(text="hello")
        assert "hello" in repr(c)
