"""Tests for fpdf_adapter.adapt_declarations."""

import pytest
from unittest.mock import MagicMock

from resumeforge.models import Declaration
from resumeforge.adapters.fpdf_adapter import adapt_declarations, SectionRenderStyle, DisplayMode


class TestAdaptDeclarationsPositive:
    """POSITIVE: declarations are correctly classified into AdaptedStyle."""

    def test_empty_declarations(self):
        """POSITIVE: empty list returns default AdaptedStyle."""
        style = adapt_declarations([])
        assert style.state_setters == []
        assert style.write_params == {}
        assert style.display == DisplayMode.BLOCK

    def test_font_size_becomes_state_setter(self):
        """POSITIVE: font-size produces a state setter that calls set_font_size."""
        decls = [Declaration(property="font-size", values=["12pt"])]
        style = adapt_declarations(decls)
        assert len(style.state_setters) == 1
        pdf = MagicMock()
        style.state_setters[0](pdf)
        pdf.set_font_size.assert_called_once_with(12.0)

    def test_color_becomes_state_setter(self):
        """POSITIVE: color produces a state setter that calls set_text_color with RGB."""
        decls = [Declaration(property="color", values=["#ff8800"])]
        style = adapt_declarations(decls)
        pdf = MagicMock()
        style.state_setters[0](pdf)
        pdf.set_text_color.assert_called_once_with(255, 136, 0)

    def test_background_color_becomes_state_setter(self):
        """POSITIVE: background-color produces a state setter that calls set_fill_color."""
        decls = [Declaration(property="background-color", values=["#003366"])]
        style = adapt_declarations(decls)
        pdf = MagicMock()
        style.state_setters[0](pdf)
        pdf.set_fill_color.assert_called_once_with(0, 51, 102)

    def test_align_becomes_write_param(self):
        """POSITIVE: align is stored as a write param with uppercased first char."""
        decls = [Declaration(property="align", values=["center"])]
        style = adapt_declarations(decls)
        assert style.write_params == {"align": "C"}

    def test_line_height_becomes_write_param(self):
        """POSITIVE: line-height is stored as write param 'h'."""
        decls = [Declaration(property="line-height", values=["7"])]
        style = adapt_declarations(decls)
        assert style.write_params == {"h": 7.0}

    def test_display_inline_sets_mode(self):
        """POSITIVE: display: inline sets DisplayMode.INLINE."""
        decls = [Declaration(property="display", values=["inline"])]
        style = adapt_declarations(decls)
        assert style.display == DisplayMode.INLINE

    def test_display_block_sets_mode(self):
        """POSITIVE: display: block sets DisplayMode.BLOCK."""
        decls = [Declaration(property="display", values=["block"])]
        style = adapt_declarations(decls)
        assert style.display == DisplayMode.BLOCK

    def test_mixed_declarations(self):
        """POSITIVE: multiple declarations are classified into correct buckets."""
        decls = [
            Declaration(property="font-size", values=["14pt"]),
            Declaration(property="align", values=["left"]),
            Declaration(property="color", values=["#000000"]),
            Declaration(property="display", values=["inline"]),
        ]
        style = adapt_declarations(decls)
        assert len(style.state_setters) == 2
        assert style.write_params == {"align": "L"}
        assert style.display == DisplayMode.INLINE


class TestAdaptDeclarationsNegative:
    """NEGATIVE: unknown or unsupported declarations are silently skipped."""

    def test_unknown_property_ignored(self):
        """NEGATIVE: properties not in any handler are skipped without error."""
        decls = [Declaration(property="unknown-prop", values=["foo"])]
        style = adapt_declarations(decls)
        assert style.state_setters == []
        assert style.write_params == {}

    def test_layout_properties_ignored(self):
        """NEGATIVE: layout-level properties (grid-column, width, etc.) are not handled."""
        decls = [
            Declaration(property="grid-column", values=["1"]),
            Declaration(property="width", values=["1fr"]),
            Declaration(property="padding", values=["8mm"]),
        ]
        style = adapt_declarations(decls)
        assert style.state_setters == []
        assert style.write_params == {}
