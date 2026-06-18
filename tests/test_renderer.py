"""Tests for Renderer."""

import pytest
from unittest.mock import MagicMock, call

from resumeforge.models import (
    Declaration, LayoutRule, SectionRule, StyledSection,
)
from resumeforge.adapters.fpdf_adapter import SectionRenderStyle, DisplayMode
from resumeforge.renderer import Renderer


@pytest.fixture
def layout():
    return LayoutRule(declarations=[
        Declaration(property="mode", values=["grid"]),
        Declaration(property="columns", values=["2"]),
    ])


def _make_section(name, declarations, order=0):
    return StyledSection(
        name=name,
        content=f"{name} content",
        rule=SectionRule(name=name, declarations=declarations),
        order=order,
    )


class TestRendererPositive:
    """POSITIVE: renderer invokes adapter correctly for each section."""

    def test_adapter_called_per_section(self, layout):
        """POSITIVE: adapter is called once per styled section."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        sections = [
            _make_section("HEADER", [Declaration(property="align", values=["center"])], order=0),
            _make_section("EXPERIENCE", [Declaration(property="font-size", values=["12pt"])], order=1),
        ]
        renderer = Renderer(adapter=adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        assert adapter.call_count == 2

    def test_adapter_receives_correct_declarations(self, layout):
        """POSITIVE: adapter receives the declarations from each section's rule."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        decls_header = [Declaration(property="align", values=["center"])]
        decls_exp = [Declaration(property="font-size", values=["12pt"])]
        sections = [
            _make_section("HEADER", decls_header, order=0),
            _make_section("EXPERIENCE", decls_exp, order=1),
        ]
        renderer = Renderer(adapter=adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        adapter.assert_any_call(decls_header)
        adapter.assert_any_call(decls_exp)

    def test_adapter_called_in_section_order(self, layout):
        """POSITIVE: adapter processes sections sorted by order field, not list position."""
        calls = []
        def tracking_adapter(decls):
            calls.append(decls)
            return SectionRenderStyle()

        decls_a = [Declaration(property="align", values=["center"])]
        decls_b = [Declaration(property="font-size", values=["14pt"])]
        sections = [
            _make_section("EXPERIENCE", decls_b, order=1),
            _make_section("HEADER", decls_a, order=0),
        ]
        renderer = Renderer(adapter=tracking_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        assert calls == [decls_a, decls_b]

    def test_empty_sections_no_adapter_call(self, layout):
        """POSITIVE: no adapter calls when sections list is empty."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        renderer = Renderer(adapter=adapter)
        renderer.render(sections=[], layout=layout, output_path="out.pdf")
        adapter.assert_not_called()


class TestRendererNegative:
    """NEGATIVE: renderer handles adapter errors."""

    def test_adapter_exception_propagates(self, layout):
        """NEGATIVE: if adapter raises, renderer does not swallow the error."""
        def failing_adapter(decls):
            raise ValueError("unsupported property")

        sections = [_make_section("HEADER", [Declaration(property="bad", values=["x"])])]
        renderer = Renderer(adapter=failing_adapter)
        with pytest.raises(ValueError, match="unsupported property"):
            renderer.render(sections=sections, layout=layout, output_path="out.pdf")
