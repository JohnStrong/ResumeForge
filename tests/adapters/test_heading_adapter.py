"""Tests for the heading adapter."""

import pytest
from resumeforge.models import Declaration, HeadingRule, StyledHeading
from resumeforge.adapters.heading_adapter import adapt_heading, HeadingConfig


class TestHeadingAdapterPositive:
    """POSITIVE: heading adapter resolves defaults and overrides."""

    def test_returns_defaults_when_rule_is_none(self):
        """POSITIVE: returns ATS defaults when heading has no rule"""
        heading = StyledHeading(content="John Doe\njohn@email.com", rule=None)
        config = adapt_heading(heading)
        assert config.content == "John Doe\njohn@email.com"
        assert config.font_size == 20
        assert config.align == "center"
        assert config.line_height == 7

    def test_returns_defaults_for_unset_properties(self):
        """POSITIVE: properties not overridden in rule retain defaults"""
        rule = HeadingRule(declarations=[
            Declaration(property="font-size", values=["24"]),
        ])
        heading = StyledHeading(content="Jane Smith", rule=rule)
        config = adapt_heading(heading)
        assert config.font_size == 24
        assert config.align == "center"
        assert config.line_height == 7

    def test_overrides_font_size(self):
        """POSITIVE: font-size declaration overrides default"""
        rule = HeadingRule(declarations=[
            Declaration(property="font-size", values=["24"]),
        ])
        heading = StyledHeading(content="John Doe", rule=rule)
        config = adapt_heading(heading)
        assert config.font_size == 24

    def test_overrides_align(self):
        """POSITIVE: align declaration overrides default center"""
        rule = HeadingRule(declarations=[
            Declaration(property="align", values=["left"]),
        ])
        heading = StyledHeading(content="John Doe", rule=rule)
        config = adapt_heading(heading)
        assert config.align == "left"

    def test_overrides_line_height(self):
        """POSITIVE: line-height declaration overrides default"""
        rule = HeadingRule(declarations=[
            Declaration(property="line-height", values=["9"]),
        ])
        heading = StyledHeading(content="John Doe", rule=rule)
        config = adapt_heading(heading)
        assert config.line_height == 9

    def test_multiple_overrides(self):
        """POSITIVE: multiple declarations override their respective defaults"""
        rule = HeadingRule(declarations=[
            Declaration(property="font-size", values=["22"]),
            Declaration(property="align", values=["right"]),
            Declaration(property="line-height", values=["8"]),
        ])
        heading = StyledHeading(content="John Doe\nEngineer", rule=rule)
        config = adapt_heading(heading)
        assert config.font_size == 22
        assert config.align == "right"
        assert config.line_height == 8
        assert config.content == "John Doe\nEngineer"

    def test_returns_heading_config_instance(self):
        """POSITIVE: returns a HeadingConfig dataclass"""
        heading = StyledHeading(content="John Doe", rule=None)
        config = adapt_heading(heading)
        assert isinstance(config, HeadingConfig)

    def test_content_preserved(self):
        """POSITIVE: heading content is passed through unchanged"""
        heading = StyledHeading(content="Jane Doe\nSenior Engineer\njane@test.com", rule=None)
        config = adapt_heading(heading)
        assert config.content == "Jane Doe\nSenior Engineer\njane@test.com"


class TestHeadingAdapterNegative:
    """NEGATIVE: heading adapter handles None input."""

    def test_returns_none_when_heading_is_none(self):
        """NEGATIVE: returns None when heading is None"""
        config = adapt_heading(None)
        assert config is None
