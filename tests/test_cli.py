"""Tests for the ResumeForge CLI."""

from unittest.mock import patch, MagicMock
from resumeforge.cli import main


def test_version(capsys):
    assert main(["version"]) == 0
    assert "0.1.0" in capsys.readouterr().out


@patch("resumeforge.cli.fpdf_engine")
@patch("resumeforge.cli.adapt_declarations")
def test_render_valid(mock_adapter, mock_engine, capsys):
    """POSITIVE: render command parses, transforms, maps, and calls renderer."""
    from resumeforge.adapters.fpdf_adapter import SectionRenderStyle
    mock_adapter.return_value = SectionRenderStyle()

    assert main(["render", "--input", "examples/resume.txt", "--style", "examples/valid.rcss", "--output", "o.pdf"]) == 0
    mock_adapter.assert_called()
    mock_engine.assert_called_once()


@patch("resumeforge.cli.fpdf_engine")
@patch("resumeforge.cli.adapt_declarations")
def test_render_invalid_rcss(mock_adapter, mock_engine, capsys):
    """NEGATIVE: render with invalid RCSS returns 1 without calling renderer."""
    assert main(["render", "--input", "examples/resume.txt", "--style", "examples/invalid.rcss", "--output", "o.pdf"]) == 1
    out = capsys.readouterr().out
    assert "Invalid RCSS" in out
    mock_engine.assert_not_called()


def test_no_command():
    assert main([]) == 1


@patch("resumeforge.cli.fpdf_engine")
@patch("resumeforge.cli.adapt_declarations")
@patch("resumeforge.cli.map_heading")
def test_render_calls_heading_mapper(mock_map_heading, mock_adapter, mock_engine, capsys):
    """POSITIVE: render command calls heading mapper with CV text and stylesheet."""
    from resumeforge.adapters.fpdf_adapter import SectionRenderStyle
    from resumeforge.models import StyledHeading
    mock_adapter.return_value = SectionRenderStyle()
    mock_map_heading.return_value = StyledHeading(content="Lorem Ipsum\nSenior Software Engineer", rule=None)

    assert main(["render", "--input", "examples/resume.txt", "--style", "examples/valid.rcss", "--output", "o.pdf"]) == 0
    mock_map_heading.assert_called_once()


@patch("resumeforge.cli.fpdf_engine")
@patch("resumeforge.cli.adapt_declarations")
@patch("resumeforge.cli.map_heading")
def test_render_passes_heading_to_renderer(mock_map_heading, mock_adapter, mock_engine, capsys):
    """POSITIVE: render command passes styled heading to renderer."""
    from resumeforge.adapters.fpdf_adapter import SectionRenderStyle
    from resumeforge.models import StyledHeading
    mock_adapter.return_value = SectionRenderStyle()
    styled_heading = StyledHeading(content="Lorem Ipsum\nEngineer", rule=None)
    mock_map_heading.return_value = styled_heading

    assert main(["render", "--input", "examples/resume.txt", "--style", "examples/valid.rcss", "--output", "o.pdf"]) == 0
    _, kwargs = mock_engine.call_args
    assert kwargs["heading_config"] is not None
    assert kwargs["heading_config"].content == "Lorem Ipsum\nEngineer"
