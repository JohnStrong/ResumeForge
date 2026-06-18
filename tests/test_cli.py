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
