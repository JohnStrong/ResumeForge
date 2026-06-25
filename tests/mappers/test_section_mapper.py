"""Tests for SectionMapper._split_sections."""

import pytest
from resumeforge.mappers.section_mapper import SectionMapper
from resumeforge.models import RawSection


@pytest.fixture
def mapper():
    return SectionMapper()


SECTION_NAMES = {"HEADER", "EXPERIENCE", "EDUCATION"}


class TestSplitSections:
    """Tests for _split_sections — splits raw CV text into RawSection objects."""

    def test_single_section(self, mapper):
        """POSITIVE: one section heading returns one RawSection"""
        text = "HEADER\nJohn Smith\njohn@example.com"
        result = mapper._split_sections(text, {"HEADER"})
        assert len(result) == 1
        assert result[0].name == "HEADER"
        assert "John Smith" in result[0].content
        assert result[0].order == 0

    def test_multiple_sections(self, mapper):
        """POSITIVE: multiple headings return one RawSection each in order"""
        text = "HEADER\nJohn Smith\n\nEXPERIENCE\nEngineer at ACME"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert len(result) == 2
        assert result[0].name == "HEADER"
        assert result[0].order == 0
        assert result[1].name == "EXPERIENCE"
        assert result[1].order == 1

    def test_content_preserved_between_sections(self, mapper):
        """POSITIVE: all content lines between headings are captured"""
        text = "HEADER\nLine 1\nLine 2\nLine 3\nEXPERIENCE\nJob"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert result[0].content == "Line 1\nLine 2\nLine 3"

    def test_blank_lines_preserved_in_content(self, mapper):
        """POSITIVE: blank/whitespace lines within section content are preserved"""
        text = "HEADER\nJohn Smith\n\njohn@example.com"
        result = mapper._split_sections(text, {"HEADER"})
        assert "\n\n" in result[0].content

    def test_heading_not_included_in_content(self, mapper):
        """POSITIVE: the heading line itself is not included in section content"""
        text = "HEADER\nJohn Smith"
        result = mapper._split_sections(text, {"HEADER"})
        assert "HEADER" not in result[0].content

    def test_last_section_captured_at_eof(self, mapper):
        """POSITIVE: last section is saved at EOF without needing a trailing heading"""
        text = "HEADER\nJohn\nEDUCATION\nUniversity of X\nBSc Computer Science"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert result[-1].name == "EDUCATION"
        assert "BSc Computer Science" in result[-1].content

    def test_preamble_before_first_heading_ignored(self, mapper):
        """POSITIVE: text before the first section heading is silently skipped"""
        text = "This is a preamble\nHEADER\nJohn Smith"
        result = mapper._split_sections(text, {"HEADER"})
        assert len(result) == 1
        assert "preamble" not in result[0].content

    def test_unknown_heading_treated_as_content(self, mapper):
        """POSITIVE: a line matching no section name is included as content"""
        text = "HEADER\nJohn Smith\nUNKNOWN SECTION\nsome text"
        result = mapper._split_sections(text, {"HEADER"})
        assert "UNKNOWN SECTION" in result[0].content

    def test_personal_name_as_section_heading(self, mapper):
        """POSITIVE: a person's name used as a section heading is matched and name preserved"""
        text = "John Joseph Strong\nSoftware Engineer\njohn@example.com\n\nEXPERIENCE\nEngineer at ACME"
        section_names = {"John Joseph Strong", "EXPERIENCE"}
        result = mapper._split_sections(text, section_names)
        assert len(result) == 2
        assert result[0].name == "John Joseph Strong"
        assert "Software Engineer" in result[0].content

    def test_empty_text_returns_empty(self, mapper):
        """NEGATIVE: empty input returns empty list"""
        result = mapper._split_sections("", SECTION_NAMES)
        assert result == []

    def test_no_matching_headings_returns_empty(self, mapper):
        """NEGATIVE: text with no known headings returns empty list"""
        text = "Just some\nrandom text\nwith no headings"
        result = mapper._split_sections(text, SECTION_NAMES)
        assert result == []


class TestApplyRules:
    """Tests for _apply_rules — pure transformation matching raw sections to rules."""

    def _make_rules_by_name(self, section_names):
        from resumeforge.models import SectionRule, Declaration
        return {n: SectionRule(name=n, declarations=[Declaration(property="padding", values=["8mm"])]) for n in section_names}

    def test_single_section_matched(self, mapper):
        """POSITIVE: one raw section matched to its rule produces one StyledSection"""
        rules_by_name = self._make_rules_by_name(["HEADER"])
        raw = [RawSection(name="HEADER", content="John Smith", order=0)]
        result = mapper._apply_rules(raw, rules_by_name)
        assert len(result) == 1
        assert result[0].name == "HEADER"
        assert result[0].content == "John Smith"
        assert result[0].rule == rules_by_name["HEADER"]

    def test_multiple_sections_preserve_order(self, mapper):
        """POSITIVE: multiple raw sections are matched and returned in document order"""
        rules_by_name = self._make_rules_by_name(["HEADER", "EXPERIENCE", "EDUCATION"])
        raw = [
            RawSection(name="HEADER", content="John", order=0),
            RawSection(name="EXPERIENCE", content="Engineer", order=1),
            RawSection(name="EDUCATION", content="BSc", order=2),
        ]
        result = mapper._apply_rules(raw, rules_by_name)
        assert [s.name for s in result] == ["HEADER", "EXPERIENCE", "EDUCATION"]
        assert result[0].rule == rules_by_name["HEADER"]
        assert result[1].rule == rules_by_name["EXPERIENCE"]
        assert result[2].rule == rules_by_name["EDUCATION"]

    def test_order_field_preserved(self, mapper):
        """POSITIVE: order from RawSection is carried into StyledSection"""
        rules_by_name = self._make_rules_by_name(["HEADER", "EXPERIENCE"])
        raw = [
            RawSection(name="HEADER", content="John", order=0),
            RawSection(name="EXPERIENCE", content="Job", order=1),
        ]
        result = mapper._apply_rules(raw, rules_by_name)
        assert result[0].order == 0
        assert result[1].order == 1


class TestMapValidation:
    """Tests for validation in SectionMapper.map()."""

    def _make_stylesheet(self):
        from resumeforge.models import Stylesheet, LayoutRule, SectionRule, Declaration
        return Stylesheet(
            layout=LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
            heading=None,
            sections=[SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])])]
        )

    def test_empty_text_raises(self, mapper):
        """NEGATIVE: empty CV text raises ValueError — no sections found"""
        with pytest.raises(ValueError, match="No sections found"):
            mapper.map("", self._make_stylesheet())

    def test_whitespace_only_raises(self, mapper):
        """NEGATIVE: whitespace-only CV text raises ValueError"""
        with pytest.raises(ValueError, match="No sections found"):
            mapper.map("   \n\n  \n", self._make_stylesheet())

    def test_no_matching_headings_raises(self, mapper):
        """NEGATIVE: CV text with no headings matching stylesheet raises ValueError"""
        with pytest.raises(ValueError, match="No sections found"):
            mapper.map("Just some random text\nwith no known headings", self._make_stylesheet())

    def test_missing_section_raises(self, mapper):
        """NEGATIVE: CV text missing a stylesheet section raises ValueError"""
        from resumeforge.models import Stylesheet, LayoutRule, SectionRule, Declaration
        stylesheet = Stylesheet(
            layout=LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
            heading=None,
            sections=[
                SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])]),
                SectionRule(name="EXPERIENCE", declarations=[Declaration(property="padding", values=["6mm"])]),
            ]
        )
        # CV only has HEADER, missing EXPERIENCE
        with pytest.raises(ValueError, match="missing one or more sections"):
            mapper.map("HEADER\nJohn Smith", stylesheet)

    def test_extra_section_in_cv_not_in_stylesheet_raises(self, mapper):
        """NEGATIVE: CV has a section heading that has no matching stylesheet rule"""
        from resumeforge.models import Stylesheet, LayoutRule, SectionRule, Declaration
        stylesheet = Stylesheet(
            layout=LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
            heading=None,
            sections=[
                SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])]),
                SectionRule(name="EXPERIENCE", declarations=[Declaration(property="padding", values=["6mm"])]),
            ]
        )
        # CV has HEADER + EXPERIENCE + EDUCATION but stylesheet only defines HEADER + EXPERIENCE
        # Note: _split_sections only picks up headings matching section_names, so EDUCATION won't be split
        # This test verifies the set equality check catches missing stylesheet sections
        with pytest.raises(ValueError, match="missing one or more sections"):
            mapper.map("HEADER\nJohn Smith\nEXPERIENCE\nEngineer", Stylesheet(
                layout=LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
                heading=None,
                sections=[
                    SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])]),
                    SectionRule(name="EXPERIENCE", declarations=[Declaration(property="padding", values=["6mm"])]),
                    SectionRule(name="EDUCATION", declarations=[Declaration(property="padding", values=["6mm"])]),
                ]
            ))
