"""Tests for the layout adapter."""

import pytest
from resumeforge.models import Declaration, LayoutRule
from resumeforge.adapters.layout_adapter import adapt_layout, LayoutConfig


@pytest.fixture
def grid_layout():
    """A valid grid layout with all properties."""
    return LayoutRule(declarations=[
        Declaration(property="mode", values=["grid"]),
        Declaration(property="columns", values=["2"]),
        Declaration(property="column-widths", values=["35%", "65%"]),
        Declaration(property="column-gap", values=["6mm"]),
        Declaration(property="margins", values=["20mm", "18mm", "20mm", "18mm"]),
        Declaration(property="font-family", values=['"Carlito"']),
    ])


class TestAdaptLayout:
    """Tests for adapt_layout field adapters."""

    def test_mode_adapted(self, grid_layout):
        """POSITIVE: mode returns raw string value"""
        config = adapt_layout(grid_layout)
        assert config.mode == "grid"

    def test_columns_adapted(self, grid_layout):
        """POSITIVE: columns returns integer"""
        config = adapt_layout(grid_layout)
        assert config.columns == 2
        assert isinstance(config.columns, int)

    def test_column_widths_adapted(self, grid_layout):
        """POSITIVE: column-widths returns list of integers without %"""
        config = adapt_layout(grid_layout)
        assert config.column_widths == [35, 65]
        assert all(isinstance(v, int) for v in config.column_widths)

    def test_column_gap_adapted(self, grid_layout):
        """POSITIVE: column-gap returns float without mm suffix"""
        config = adapt_layout(grid_layout)
        assert config.column_gap == 6.0
        assert isinstance(config.column_gap, float)

    def test_margins_adapted(self, grid_layout):
        """POSITIVE: margins returns tuple of floats without mm suffix"""
        config = adapt_layout(grid_layout)
        assert config.margins == (20.0, 18.0, 20.0, 18.0)
        assert isinstance(config.margins, tuple)

    def test_font_family_adapted(self, grid_layout):
        """POSITIVE: font-family returns string with quotes stripped"""
        config = adapt_layout(grid_layout)
        assert config.font_family == "Carlito"

    def test_font_family_optional(self):
        """POSITIVE: font-family defaults to None when not set"""
        layout = LayoutRule(declarations=[
            Declaration(property="mode", values=["single"]),
            Declaration(property="columns", values=["1"]),
            Declaration(property="column-widths", values=["100%"]),
            Declaration(property="column-gap", values=["0mm"]),
            Declaration(property="margins", values=["20mm", "18mm", "20mm", "18mm"]),
        ])
        config = adapt_layout(layout)
        assert config.font_family is None

    def test_returns_layout_config_instance(self, grid_layout):
        """POSITIVE: adapt_layout returns a LayoutConfig dataclass"""
        config = adapt_layout(grid_layout)
        assert isinstance(config, LayoutConfig)

    def test_unknown_property_raises(self):
        """NEGATIVE: unrecognised layout property raises ValueError"""
        layout = LayoutRule(declarations=[
            Declaration(property="mode", values=["grid"]),
            Declaration(property="columns", values=["2"]),
            Declaration(property="column-widths", values=["35%", "65%"]),
            Declaration(property="column-gap", values=["6mm"]),
            Declaration(property="margins", values=["20mm", "18mm", "20mm", "18mm"]),
            Declaration(property="banana", values=["yellow"]),
        ])
        with pytest.raises(ValueError, match="banana"):
            adapt_layout(layout)
