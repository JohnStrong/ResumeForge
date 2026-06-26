"""Tests for Renderer."""

import pytest
from unittest.mock import MagicMock, call

from resumeforge.models import (
    Declaration, LayoutRule, SectionRule, StyledSection, StyledHeading,
)
from resumeforge.adapters.fpdf_adapter import SectionRenderStyle, DisplayMode
from resumeforge.adapters.layout_adapter import LayoutConfig, adapt_layout
from resumeforge.renderer import Renderer, RenderSection


@pytest.fixture
def layout():
    return LayoutRule(declarations=[
        Declaration(property="mode", values=["grid"]),
        Declaration(property="columns", values=["2"]),
        Declaration(property="column-widths", values=["50%", "50%"]),
        Declaration(property="column-gap", values=["6mm"]),
        Declaration(property="margins", values=["20mm", "18mm", "20mm", "18mm"]),
    ])


@pytest.fixture
def noop_engine():
    return MagicMock()


@pytest.fixture
def mock_layout_adapter():
    return MagicMock(return_value=LayoutConfig(
        mode="grid", columns=2, column_widths=[50, 50],
        column_gap=6.0, margins=(20.0, 18.0, 20.0, 18.0),
    ))


def _make_section(name, declarations, order=0):
    return StyledSection(
        name=name,
        content=f"{name} content",
        rule=SectionRule(name=name, declarations=declarations),
        order=order,
    )


class TestRendererPositive:
    """POSITIVE: renderer invokes adapter correctly for each section."""

    def test_adapter_called_per_section(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: adapter is called once per styled section."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        sections = [
            _make_section("HEADER", [Declaration(property="align", values=["center"])], order=0),
            _make_section("EXPERIENCE", [Declaration(property="font-size", values=["12pt"])], order=1),
        ]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        assert adapter.call_count == 2

    def test_adapter_receives_correct_declarations(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: adapter receives the declarations from each section's rule."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        decls_header = [Declaration(property="align", values=["center"])]
        decls_exp = [Declaration(property="font-size", values=["12pt"])]
        sections = [
            _make_section("HEADER", decls_header, order=0),
            _make_section("EXPERIENCE", decls_exp, order=1),
        ]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        adapter.assert_any_call(decls_header)
        adapter.assert_any_call(decls_exp)

    def test_adapter_called_in_section_order(self, layout, noop_engine, mock_layout_adapter):
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
        renderer = Renderer(adapter=tracking_adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        assert calls == [decls_a, decls_b]

    def test_empty_sections_no_adapter_call(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: no adapter calls when sections list is empty."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=[], layout=layout, output_path="out.pdf")
        adapter.assert_not_called()

    def test_engine_is_called(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: engine is invoked once per render call."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        sections = [_make_section("HEADER", [Declaration(property="align", values=["center"])], order=0)]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        noop_engine.assert_called_once()

    def test_font_face_passed_to_engine(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: font_face is forwarded to the engine."""
        from resumeforge.models import FontFaceRule
        adapter = MagicMock(return_value=SectionRenderStyle())
        font_face = FontFaceRule(declarations=[Declaration(property="font-family", values=['"Carlito"'])])
        sections = [_make_section("HEADER", [Declaration(property="align", values=["center"])], order=0)]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf", font_face=font_face)
        _, kwargs = noop_engine.call_args
        assert kwargs["font_face"] == font_face


class TestRendererNegative:
    """NEGATIVE: renderer handles adapter errors."""

    def test_engine_not_called_when_adapter_fails(self, layout, noop_engine, mock_layout_adapter):
        """NEGATIVE: engine is not invoked if the adapter raises an error."""
        def failing_adapter(decls):
            raise ValueError("unsupported property")

        sections = [_make_section("HEADER", [Declaration(property="bad", values=["x"])])]
        renderer = Renderer(adapter=failing_adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        with pytest.raises(ValueError):
            renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        noop_engine.assert_not_called()


class TestRendererLayoutAdapter:
    """Tests for layout_adapter integration in Renderer."""

    def test_layout_adapter_called_during_render(self, layout, noop_engine):
        """POSITIVE: layout_adapter is invoked with layout during render."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        layout_adapter = MagicMock(return_value=LayoutConfig(
            mode="grid", columns=2, column_widths=[35, 65],
            column_gap=6.0, margins=(20.0, 18.0, 20.0, 18.0),
        ))
        sections = [_make_section("HEADER", [Declaration(property="align", values=["center"])], order=0)]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        layout_adapter.assert_called_once_with(layout)

    def test_layout_config_passed_to_engine(self, layout, noop_engine):
        """POSITIVE: engine receives LayoutConfig from layout_adapter."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        expected_config = LayoutConfig(
            mode="grid", columns=2, column_widths=[35, 65],
            column_gap=6.0, margins=(20.0, 18.0, 20.0, 18.0),
        )
        layout_adapter = MagicMock(return_value=expected_config)
        sections = [_make_section("HEADER", [Declaration(property="align", values=["center"])], order=0)]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        args, _ = noop_engine.call_args
        assert args[1] == expected_config


class TestRendererHeading:
    """Tests for heading parameter passed to engine."""

    def test_heading_passed_to_engine_when_set(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: heading_config is forwarded to the engine when heading provided."""
        from resumeforge.models import HeadingRule
        from resumeforge.adapters.heading_adapter import HeadingConfig
        adapter = MagicMock(return_value=SectionRenderStyle())
        heading = StyledHeading(
            content="John Doe\njohn@email.com",
            rule=HeadingRule(declarations=[Declaration(property="font-size", values=["22pt"])]),
        )
        sections = [_make_section("HEADER", [Declaration(property="align", values=["center"])], order=0)]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf", heading=heading)
        _, kwargs = noop_engine.call_args
        assert kwargs["heading_config"] is not None
        assert isinstance(kwargs["heading_config"], HeadingConfig)
        assert kwargs["heading_config"].content == "John Doe\njohn@email.com"

    def test_heading_none_passed_to_engine_when_not_set(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: heading_config is None when heading not provided."""
        adapter = MagicMock(return_value=SectionRenderStyle())
        sections = [_make_section("HEADER", [Declaration(property="align", values=["center"])], order=0)]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf")
        _, kwargs = noop_engine.call_args
        assert kwargs["heading_config"] is None

    def test_heading_with_none_rule_uses_defaults(self, layout, noop_engine, mock_layout_adapter):
        """POSITIVE: heading with rule=None produces HeadingConfig with defaults."""
        from resumeforge.adapters.heading_adapter import HeadingConfig
        adapter = MagicMock(return_value=SectionRenderStyle())
        heading = StyledHeading(content="Jane Smith\nEngineer", rule=None)
        sections = [_make_section("HEADER", [Declaration(property="align", values=["center"])], order=0)]
        renderer = Renderer(adapter=adapter, engine=noop_engine, layout_adapter=mock_layout_adapter)
        renderer.render(sections=sections, layout=layout, output_path="out.pdf", heading=heading)
        _, kwargs = noop_engine.call_args
        assert kwargs["heading_config"].font_size == 20
        assert kwargs["heading_config"].align == "center"
        assert kwargs["heading_config"].line_height == 7
