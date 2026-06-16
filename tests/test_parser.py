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
        result = parser.parse(self.FULL_COVERAGE_RCSS)
        assert result.valid is True
        assert result.tree is not None

    def test_layout_selector(self, parser):
        rcss = """\
/* POSITIVE: minimal layout rule */
layout { mode: single; }
"""
        result = parser.parse(rcss)
        assert result.valid is True
        assert result.tree is not None

    def test_section_selector(self, parser):
        rcss = """\
/* POSITIVE: minimal section rule */
section[name="LINKS"] { padding: 4mm; }
"""
        result = parser.parse(rcss)
        assert result.valid is True
        assert result.tree is not None

    def test_multi_value_property(self, parser):
        rcss = """\
/* POSITIVE: property with multiple space-separated values */
layout { margins: 20mm 18mm 20mm 18mm; }
"""
        result = parser.parse(rcss)
        assert result.valid is True
        assert result.tree is not None

    def test_hyphenated_property_names(self, parser):
        rcss = """\
/* POSITIVE: hyphenated property names like grid-column, font-size */
section[name="MAIN"] { grid-column: 2; font-size: 14pt; }
"""
        result = parser.parse(rcss)
        assert result.valid is True
        assert result.tree is not None

    def test_comments_ignored(self, parser):
        rcss = """\
/* POSITIVE: comments should not affect parsing */
layout { /* inline comment */ mode: single; }
"""
        result = parser.parse(rcss)
        assert result.valid is True
        assert result.tree is not None


class TestInvalidRcss:
    """Negative test cases — invalid RCSS that must raise parse errors."""

    def test_invalid_selector(self, parser):
        rcss = """\
/* NEGATIVE: unknown selector — only layout and section are valid */
header { padding: 8mm; }
"""
        result = parser.parse(rcss)
        assert result.valid is False
        assert result.message is not None

    def test_section_missing_bracket_identifier(self, parser):
        rcss = """\
/* NEGATIVE: section without [name="..."] identifier */
section { padding: 8mm; }
"""
        result = parser.parse(rcss)
        assert result.valid is False
        assert result.message is not None

    def test_property_missing_colon(self, parser):
        rcss = """\
/* NEGATIVE: property without colon separator */
layout { mode single; }
"""
        result = parser.parse(rcss)
        assert result.valid is False
        assert result.message is not None

    def test_property_missing_semicolon(self, parser):
        rcss = """\
/* NEGATIVE: property without semicolon terminator */
layout { mode: single }
"""
        result = parser.parse(rcss)
        assert result.valid is False
        assert result.message is not None

    def test_property_missing_value(self, parser):
        rcss = """\
/* NEGATIVE: property with colon but no value before semicolon */
layout { mode: ; }
"""
        result = parser.parse(rcss)
        assert result.valid is False
        assert result.message is not None

    def test_empty_block(self, parser):
        rcss = """\
/* NEGATIVE: rule with no declarations — grammar requires declaration+ */
layout { }
"""
        result = parser.parse(rcss)
        assert result.valid is False
        assert result.message is not None

    def test_section_name_not_quoted(self, parser):
        rcss = """\
/* NEGATIVE: section name without quotes */
section[name=HEADER] { padding: 8mm; }
"""
        result = parser.parse(rcss)
        assert result.valid is False
        assert result.message is not None


class TestValidatePositive:
    """Validate returns valid=True for correct RCSS."""

    def test_valid_layout(self, parser):
        result = parser.validate('layout { mode: single; }')
        assert result.valid is True
        assert result.message is None

    def test_valid_section(self, parser):
        result = parser.validate('section[name="HEADER"] { padding: 8mm; }')
        assert result.valid is True
        assert result.message is None

    def test_valid_full(self, parser):
        rcss = """\
layout { mode: grid; columns: 2; }
section[name="SIDEBAR"] { grid-column: 1; padding: 6mm; }
section[name="MAIN"] { grid-column: 2; padding: 6mm; }
"""
        result = parser.validate(rcss)
        assert result.valid is True
        assert result.message is None


class TestValidateNegative:
    """Validate returns valid=False with a message for invalid RCSS."""

    def test_invalid_selector(self, parser):
        result = parser.validate('header { padding: 8mm; }')
        assert result.valid is False
        assert "Line 1, Col 1" in result.message
        assert "LAYOUT" in result.message
        assert "SECTION" in result.message

    def test_missing_semicolon(self, parser):
        result = parser.validate('layout { mode: single }')
        assert result.valid is False
        assert "SEMICOLON" in result.message
        assert "RBRACE" in result.message

    def test_missing_colon(self, parser):
        result = parser.validate('layout { mode single; }')
        assert result.valid is False
        assert "COLON" in result.message

    def test_empty_block(self, parser):
        result = parser.validate('layout { }')
        assert result.valid is False
        assert "RBRACE" in result.message

    def test_section_without_name(self, parser):
        result = parser.validate('section { padding: 8mm; }')
        assert result.valid is False
        assert "LSQB" in result.message


class TestParseResultPositive:
    """parse() returns ParseResult with valid=True and a tree on success."""

    def test_returns_parse_result(self, parser):
        from resumeforge.models import ParseResult
        result = parser.parse('layout { mode: single; }')
        assert isinstance(result, ParseResult)

    def test_valid_is_true(self, parser):
        result = parser.parse('layout { mode: single; }')
        assert result.valid is True

    def test_message_is_none(self, parser):
        result = parser.parse('layout { mode: single; }')
        assert result.message is None

    def test_tree_is_not_none(self, parser):
        result = parser.parse('layout { mode: grid; columns: 2; }')
        assert result.tree is not None

    def test_tree_has_start_root(self, parser):
        result = parser.parse('section[name="HEADER"] { padding: 8mm; }')
        assert result.tree.data == "start"

    def test_tree_contains_rules(self, parser):
        rcss = """\
layout { mode: grid; columns: 2; }
section[name="MAIN"] { grid-column: 2; padding: 6mm; }
"""
        result = parser.parse(rcss)
        assert len(result.tree.children) == 2


class TestParseResultNegative:
    """parse() returns ParseResult with valid=False and no tree on failure."""

    def test_invalid_returns_parse_result(self, parser):
        from resumeforge.models import ParseResult
        result = parser.parse('header { padding: 8mm; }')
        assert isinstance(result, ParseResult)

    def test_valid_is_false(self, parser):
        result = parser.parse('header { padding: 8mm; }')
        assert result.valid is False

    def test_tree_is_none(self, parser):
        result = parser.parse('layout { mode: single }')
        assert result.tree is None

    def test_message_present(self, parser):
        result = parser.parse('layout { mode: single }')
        assert result.message is not None
        assert "SEMICOLON" in result.message

    def test_message_has_location(self, parser):
        result = parser.parse('header { padding: 8mm; }')
        assert "Line 1" in result.message
        assert "Col 1" in result.message
