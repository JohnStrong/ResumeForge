"""Tests for SectionMapper._split_sections."""

import pytest
from resumeforge.section_mapper import SectionMapper


@pytest.fixture
def mapper():
    return SectionMapper()


SECTION_NAMES = {"HEADER", "EXPERIENCE", "EDUCATION"}


class TestSplitSections:
    """Tests for _split_sections — splits raw CV text into (name, content) pairs."""

    def test_single_section(self, mapper):
        """POSITIVE: one section heading returns one (name, content) pair"""
        text = "HEADER\nJohn Smith\njohn@example.com"
        result = mapper._split_sections(text, {"HEADER"})
        assert len(result) == 1
        assert result[0][0] == "HEADER"
        assert "John Smith" in result[0][1]

    def test_multiple_sections(self, mapper):
        """POSITIVE: multiple headings return one pair each"""
        text = "HEADER\nJohn Smith\n\nEXPERIENCE\nEngineer at ACME"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert len(result) == 2
        assert result[0][0] == "HEADER"
        assert result[1][0] == "EXPERIENCE"

    def test_content_preserved_between_sections(self, mapper):
        """POSITIVE: all content lines between headings are captured"""
        text = "HEADER\nLine 1\nLine 2\nLine 3\nEXPERIENCE\nJob"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert result[0][1] == "Line 1\nLine 2\nLine 3"

    def test_blank_lines_preserved_in_content(self, mapper):
        """POSITIVE: blank/whitespace lines within section content are preserved"""
        text = "HEADER\nJohn Smith\n\njohn@example.com"
        result = mapper._split_sections(text, {"HEADER"})
        assert "\n\n" in result[0][1]

    def test_heading_not_included_in_content(self, mapper):
        """POSITIVE: the heading line itself is not included in section content"""
        text = "HEADER\nJohn Smith"
        result = mapper._split_sections(text, {"HEADER"})
        assert "HEADER" not in result[0][1]

    def test_last_section_captured_at_eof(self, mapper):
        """POSITIVE: last section is saved at EOF without needing a trailing heading"""
        text = "HEADER\nJohn\nEDUCATION\nUniversity of X\nBSc Computer Science"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert result[-1][0] == "EDUCATION"
        assert "BSc Computer Science" in result[-1][1]

    def test_preamble_before_first_heading_ignored(self, mapper):
        """POSITIVE: text before the first section heading is silently skipped"""
        text = "This is a preamble\nHEADER\nJohn Smith"
        result = mapper._split_sections(text, {"HEADER"})
        assert len(result) == 1
        assert "preamble" not in result[0][1]

    def test_unknown_heading_treated_as_content(self, mapper):
        """POSITIVE: a line matching no section name is included as content"""
        text = "HEADER\nJohn Smith\nUNKNOWN SECTION\nsome text"
        result = mapper._split_sections(text, {"HEADER"})
        assert "UNKNOWN SECTION" in result[0][1]

    def test_personal_name_as_section_heading(self, mapper):
        """POSITIVE: a person's name or 'C.V.' used as a section heading is matched and name preserved"""
        text = "John Joseph Strong\nSoftware Engineer\njohn@example.com\n\nEXPERIENCE\nEngineer at ACME"
        section_names = {"John Joseph Strong", "EXPERIENCE"}
        result = mapper._split_sections(text, section_names)
        assert len(result) == 2
        assert result[0][0] == "John Joseph Strong"
        assert "Software Engineer" in result[0][1]
        """NEGATIVE: empty input returns empty list"""
        result = mapper._split_sections("", SECTION_NAMES)
        assert result == []

    def test_no_matching_headings_returns_empty(self, mapper):
        """NEGATIVE: text with no known headings returns empty list"""
        text = "Just some\nrandom text\nwith no headings"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert result == []
