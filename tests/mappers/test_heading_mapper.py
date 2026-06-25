"""Tests for the heading mapper."""

import pytest
from resumeforge.models import (
    Declaration, HeadingRule, LayoutRule, SectionRule, Stylesheet, StyledHeading,
)
from resumeforge.mappers.heading_mapper import map as map_heading


def _make_stylesheet(heading_rule=None):
    return Stylesheet(
        layout=LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
        heading=heading_rule,
        sections=[
            SectionRule(name="Skills", declarations=[Declaration(property="font-size", values=["12pt"])]),
            SectionRule(name="Experience", declarations=[Declaration(property="font-size", values=["12pt"])]),
        ],
    )


class TestHeadingMapperPositive:
    """POSITIVE: heading mapper extracts content before first section."""

    def test_extracts_name_and_contact(self):
        """POSITIVE: extracts all lines before the first section heading"""
        text = "John Doe\nSoftware Engineer\njohn@email.com\n\nSkills\nPython, Go"
        result = map_heading(text, _make_stylesheet())
        assert result.content == "John Doe\nSoftware Engineer\njohn@email.com"

    def test_single_line_heading(self):
        """POSITIVE: a single name line before a section is valid"""
        text = "Jane Smith\nSkills\nPython"
        result = map_heading(text, _make_stylesheet())
        assert result.content == "Jane Smith"

    def test_multiline_heading_with_blank_lines(self):
        """POSITIVE: blank lines within heading are preserved"""
        text = "John Doe\n\nSenior Engineer\njohn@test.com\nSkills\nPython"
        result = map_heading(text, _make_stylesheet())
        assert "John Doe" in result.content
        assert "john@test.com" in result.content

    def test_returns_styled_heading_instance(self):
        """POSITIVE: returns a StyledHeading dataclass"""
        text = "John Doe\nSkills\nPython"
        result = map_heading(text, _make_stylesheet())
        assert isinstance(result, StyledHeading)

    def test_rule_is_none_when_no_heading_rule(self):
        """POSITIVE: rule is None when stylesheet has no heading rule"""
        text = "John Doe\nSkills\nPython"
        result = map_heading(text, _make_stylesheet(heading_rule=None))
        assert result.rule is None

    def test_rule_is_set_when_heading_rule_provided(self):
        """POSITIVE: rule is the HeadingRule from stylesheet when present"""
        heading_rule = HeadingRule(declarations=[Declaration(property="font-size", values=["22pt"])])
        text = "John Doe\nSkills\nPython"
        result = map_heading(text, _make_stylesheet(heading_rule=heading_rule))
        assert result.rule is heading_rule

    def test_stops_at_first_section_only(self):
        """POSITIVE: only stops at the first matching section, not later ones"""
        text = "John Doe\nContact info\nSkills\nPython\nExperience\nEngineer"
        result = map_heading(text, _make_stylesheet())
        assert "Experience" not in result.content
        assert "Skills" not in result.content


class TestHeadingMapperNegative:
    """NEGATIVE: heading mapper raises when no heading content exists."""

    def test_raises_when_first_line_is_section(self):
        """NEGATIVE: raises ValueError when CV starts with a section heading"""
        text = "Skills\nPython, Go"
        with pytest.raises(ValueError, match="heading content"):
            map_heading(text, _make_stylesheet())

    def test_raises_when_text_is_empty(self):
        """NEGATIVE: raises ValueError on empty text"""
        with pytest.raises(ValueError, match="heading content"):
            map_heading("", _make_stylesheet())

    def test_raises_when_text_is_whitespace_only(self):
        """NEGATIVE: raises ValueError on whitespace-only text"""
        with pytest.raises(ValueError, match="heading content"):
            map_heading("   \n\n  ", _make_stylesheet())

    def test_raises_when_only_whitespace_before_section(self):
        """NEGATIVE: raises ValueError when only whitespace precedes first section"""
        text = "  \n\nSkills\nPython"
        with pytest.raises(ValueError, match="heading content"):
            map_heading(text, _make_stylesheet())
