"""Tests for the RCSS DSL parser.

NOTE: The following semantic rules are NOT yet enforced by the grammar but will be:
  - If layout mode is "grid", every section MUST have a grid-column property.
  - Grid mode supports a maximum of 2 columns (grid-column: 1 or 2 only).
These will be validated at a higher level (semantic pass) once implemented.
"""

import pytest
from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from resumeforge.parser import RcssParser


@pytest.fixture
def parser():
    return RcssParser()


class TestValidRcss:
    """Positive test cases — valid RCSS that must parse successfully."""

    FULL_COVERAGE_RCSS = """\
/* POSITIVE: layout selector with multiple properties including multi-value */
layout {
    mode: grid;
    columns: 2;
    column-gap: 6mm;
    margins: 20mm 18mm 20mm 18mm;
}

/* POSITIVE: section selector with name identifier and single property */
section[name="HEADER"] {
    padding: 8mm;
    align: center;
    grid-column: 1;
}

/* POSITIVE: section selector with multi-word name */
section[name="WORK EXPERIENCE"] {
    padding: 6mm;
    font-size: 12pt;
    line-height: 1.4;
    grid-column: 2;
}

/* POSITIVE: section with grid-column and width using fr unit */
section[name="SIDEBAR"] {
    grid-column: 1;
    width: 1fr;
    padding: 6mm;
    background-color: #f0f0f0;
    color: #333333;
}

/* POSITIVE: section with display and margin properties */
section[name="EDUCATION"] {
    grid-column: 2;
    display: block;
    margin: 4mm;
}
"""

    def test_full_grammar_coverage(self, parser):
        """All grammar rules are exercised in one cohesive RCSS string."""
        tree = parser.parse(self.FULL_COVERAGE_RCSS)
        assert tree is not None

    def test_layout_selector(self, parser):
        rcss = """\
/* POSITIVE: minimal layout rule */
layout { mode: single; }
"""
        tree = parser.parse(rcss)
        assert tree is not None

    def test_section_selector(self, parser):
        rcss = """\
/* POSITIVE: minimal section rule */
section[name="LINKS"] { padding: 4mm; }
"""
        tree = parser.parse(rcss)
        assert tree is not None

    def test_multi_value_property(self, parser):
        rcss = """\
/* POSITIVE: property with multiple space-separated values */
layout { margins: 20mm 18mm 20mm 18mm; }
"""
        tree = parser.parse(rcss)
        assert tree is not None

    def test_hyphenated_property_names(self, parser):
        rcss = """\
/* POSITIVE: hyphenated property names like grid-column, font-size */
section[name="MAIN"] { grid-column: 2; font-size: 14pt; }
"""
        tree = parser.parse(rcss)
        assert tree is not None

    def test_comments_ignored(self, parser):
        rcss = """\
/* POSITIVE: comments should not affect parsing */
layout { /* inline comment */ mode: single; }
"""
        tree = parser.parse(rcss)
        assert tree is not None


class TestInvalidRcss:
    """Negative test cases — invalid RCSS that must raise parse errors."""

    def test_invalid_selector(self, parser):
        rcss = """\
/* NEGATIVE: unknown selector — only layout and section are valid */
header { padding: 8mm; }
"""
        with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
            parser.parse(rcss)

    def test_section_missing_bracket_identifier(self, parser):
        rcss = """\
/* NEGATIVE: section without [name="..."] identifier */
section { padding: 8mm; }
"""
        with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
            parser.parse(rcss)

    def test_property_missing_colon(self, parser):
        rcss = """\
/* NEGATIVE: property without colon separator */
layout { mode single; }
"""
        with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
            parser.parse(rcss)

    def test_property_missing_semicolon(self, parser):
        rcss = """\
/* NEGATIVE: property without semicolon terminator */
layout { mode: single }
"""
        with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
            parser.parse(rcss)

    def test_property_missing_value(self, parser):
        rcss = """\
/* NEGATIVE: property with colon but no value before semicolon */
layout { mode: ; }
"""
        with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
            parser.parse(rcss)

    def test_empty_block(self, parser):
        rcss = """\
/* NEGATIVE: rule with no declarations — grammar requires declaration+ */
layout { }
"""
        with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
            parser.parse(rcss)

    def test_section_name_not_quoted(self, parser):
        rcss = """\
/* NEGATIVE: section name without quotes */
section[name=HEADER] { padding: 8mm; }
"""
        with pytest.raises((UnexpectedCharacters, UnexpectedToken)):
            parser.parse(rcss)
