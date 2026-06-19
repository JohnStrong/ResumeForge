"""Tests for the RCSS transformer."""

import pytest
from lark import Token

from resumeforge.transformer import RcssTransformer, transform
from resumeforge.models import Declaration, LayoutRule, SectionRule, Stylesheet
from resumeforge.parser import RcssParser


@pytest.fixture
def transformer():
    return RcssTransformer()


@pytest.fixture
def parser():
    return RcssParser()


class TestValue:
    """Tests for value() method."""

    def test_single_value(self, transformer):
        """POSITIVE: single VALUE token returns list with one string"""
        items = [Token("VALUE", "8mm")]
        result = transformer.value(items)
        assert result == ["8mm"]

    def test_multiple_values(self, transformer):
        """POSITIVE: multiple VALUE tokens return list of strings"""
        items = [Token("VALUE", "20mm"), Token("VALUE", "18mm"), Token("VALUE", "20mm"), Token("VALUE", "18mm")]
        result = transformer.value(items)
        assert result == ["20mm", "18mm", "20mm", "18mm"]


class TestDeclaration:
    """Tests for declaration() method."""

    def test_simple_declaration(self, transformer):
        """POSITIVE: PROPERTY token + values list returns Declaration"""
        items = [Token("PROPERTY", "padding"), ["8mm"]]
        result = transformer.declaration(items)
        assert result.property == "padding"
        assert result.values == ["8mm"]

    def test_multi_value_declaration(self, transformer):
        """POSITIVE: declaration with multiple values"""
        items = [Token("PROPERTY", "margins"), ["20mm", "18mm", "20mm", "18mm"]]
        result = transformer.declaration(items)
        assert result.property == "margins"
        assert result.values == ["20mm", "18mm", "20mm", "18mm"]

    def test_hyphenated_property(self, transformer):
        """POSITIVE: hyphenated property name preserved"""
        items = [Token("PROPERTY", "grid-column"), ["1"]]
        result = transformer.declaration(items)
        assert result.property == "grid-column"


class TestLayoutSelector:
    """Tests for layout_selector() method."""

    def test_returns_layout_string(self, transformer):
        """POSITIVE: always returns the string 'layout'"""
        result = transformer.layout_selector([])
        assert result == "layout"


class TestSectionSelector:
    """Tests for section_selector() method."""

    def test_strips_quotes(self, transformer):
        """POSITIVE: strips quotes from STRING token"""
        items = [Token("STRING", '"HEADER"')]
        result = transformer.section_selector(items)
        assert result == "HEADER"

    def test_multi_word_name(self, transformer):
        """POSITIVE: multi-word section names preserved"""
        items = [Token("STRING", '"WORK EXPERIENCE"')]
        result = transformer.section_selector(items)
        assert result == "WORK EXPERIENCE"


class TestRule:
    """Tests for rule() method."""

    def test_layout_rule(self, transformer):
        """POSITIVE: selector 'layout' produces a LayoutRule"""
        items = ["layout", Declaration(property="mode", values=["grid"])]
        result = transformer.rule(items)
        assert isinstance(result, LayoutRule)
        assert len(result.declarations) == 1
        assert result.declarations[0].property == "mode"

    def test_section_rule(self, transformer):
        """POSITIVE: section name produces a SectionRule"""
        items = ["HEADER", Declaration(property="padding", values=["8mm"])]
        result = transformer.rule(items)
        assert isinstance(result, SectionRule)
        assert result.name == "HEADER"
        assert result.declarations[0].property == "padding"

    def test_multiple_declarations(self, transformer):
        """POSITIVE: all declarations are captured in the rule"""
        items = [
            "SIDEBAR",
            Declaration(property="grid-column", values=["1"]),
            Declaration(property="padding", values=["6mm"]),
            Declaration(property="width", values=["1fr"]),
        ]
        result = transformer.rule(items)
        assert len(result.declarations) == 3


class TestStart:
    """Tests for start() method."""

    def test_valid_stylesheet(self, transformer):
        """POSITIVE: layout + sections produce a valid Stylesheet"""
        items = [
            LayoutRule(declarations=[Declaration(property="mode", values=["grid"])]),
            SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])]),
        ]
        result = transformer.start(items)
        assert isinstance(result, Stylesheet)
        assert result.layout is not None
        assert len(result.sections) == 1

    def test_missing_layout(self, transformer):
        """NEGATIVE: no layout rule raises ValueError"""
        items = [
            SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])]),
        ]
        with pytest.raises(ValueError, match="layout"):
            transformer.start(items)

    def test_no_sections(self, transformer):
        """NEGATIVE: no section rules raises ValueError"""
        items = [
            LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
        ]
        with pytest.raises(ValueError, match="section"):
            transformer.start(items)


class TestTransformIntegration:
    """Integration tests for the transform() entry point."""

    def test_full_transform(self, parser):
        """POSITIVE: full RCSS string transforms into a valid Stylesheet"""
        rcss = """\
layout { mode: grid; columns: 2; }
section[name="HEADER"] { grid-column: 1; padding: 8mm; }
section[name="MAIN"] { grid-column: 2; padding: 6mm; }
"""
        result = parser.parse(rcss)
        stylesheet = transform(result.tree)
        assert stylesheet.layout.declarations[0].property == "mode"
        assert stylesheet.layout.declarations[0].values == ["grid"]
        assert len(stylesheet.sections) == 2
        assert stylesheet.sections[0].name == "HEADER"
        assert stylesheet.sections[1].name == "MAIN"

    def test_transform_invalid_no_layout(self, parser):
        """NEGATIVE: RCSS with no layout raises VisitError (wrapping ValueError) during transform"""
        from lark.exceptions import VisitError
        rcss = 'section[name="HEADER"] { padding: 8mm; }'
        result = parser.parse(rcss)
        with pytest.raises(VisitError, match="layout"):
            transform(result.tree)


class TestFontFaceSelector:
    """Tests for fontface_selector() method."""

    def test_returns_font_face_string(self, transformer):
        """POSITIVE: fontface_selector returns 'font-face' identifier"""
        result = transformer.fontface_selector([])
        assert result == "font-face"


class TestFontFaceRule:
    """Tests for rule() handling @font-face."""

    def test_font_face_rule_created(self, transformer):
        """POSITIVE: selector 'font-face' with declarations produces FontFaceRule"""
        from resumeforge.models import FontFaceRule
        items = [
            "font-face",
            Declaration(property="font-family", values=['"Consolas"']),
            Declaration(property="src", values=['"./fonts/Consolas.ttf"']),
        ]
        result = transformer.rule(items)
        assert isinstance(result, FontFaceRule)
        assert len(result.declarations) == 2

    def test_font_face_rule_with_weight(self, transformer):
        """POSITIVE: @font-face with font-weight captures all declarations"""
        from resumeforge.models import FontFaceRule
        items = [
            "font-face",
            Declaration(property="font-family", values=['"Consolas"']),
            Declaration(property="src", values=['"./fonts/Consolas-Bold.ttf"']),
            Declaration(property="font-weight", values=["bold"]),
        ]
        result = transformer.rule(items)
        assert isinstance(result, FontFaceRule)
        assert len(result.declarations) == 3


class TestStartWithFontFace:
    """Tests for start() with @font-face rules."""

    def test_font_face_set_in_stylesheet(self, transformer):
        """POSITIVE: @font-face rule is set as font_face on Stylesheet"""
        from resumeforge.models import FontFaceRule
        items = [
            FontFaceRule(declarations=[Declaration(property="font-family", values=['"Consolas"'])]),
            LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
            SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])]),
        ]
        result = transformer.start(items)
        assert result.font_face is not None
        assert isinstance(result.font_face, FontFaceRule)
        assert result.font_face.declarations[0].values == ['"Consolas"']

    def test_no_font_face_defaults_to_none(self, transformer):
        """POSITIVE: stylesheet without @font-face has font_face=None"""
        items = [
            LayoutRule(declarations=[Declaration(property="mode", values=["single"])]),
            SectionRule(name="HEADER", declarations=[Declaration(property="padding", values=["8mm"])]),
        ]
        result = transformer.start(items)
        assert result.font_face is None


class TestFontFaceIntegration:
    """Integration tests for @font-face parsing and transformation."""

    def test_full_transform_with_font_face(self, parser):
        """POSITIVE: RCSS with @font-face transforms into Stylesheet with font_face set"""
        rcss = '''\
@font-face { font-family: "Consolas"; src: "./fonts/Consolas.ttf"; font-weight: bold; }
layout { mode: single; }
section[name="HEADER"] { font-size: 12pt; }
'''
        result = parser.parse(rcss)
        stylesheet = transform(result.tree)
        assert stylesheet.font_face is not None
        decls = {d.property: d.values[0] for d in stylesheet.font_face.declarations}
        assert decls["font-family"] == '"Consolas"'
        assert decls["src"] == '"./fonts/Consolas.ttf"'
        assert decls["font-weight"] == "bold"

    def test_full_transform_without_font_face(self, parser):
        """POSITIVE: RCSS without @font-face has font_face=None"""
        rcss = '''\
layout { mode: single; }
section[name="HEADER"] { font-size: 12pt; }
'''
        result = parser.parse(rcss)
        stylesheet = transform(result.tree)
        assert stylesheet.font_face is None
