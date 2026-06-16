"""Tests for the ResumeForge CLI."""

from resumeforge.cli import main


def test_version(capsys):
    assert main(["version"]) == 0
    assert "0.1.0" in capsys.readouterr().out


def test_render_valid(capsys):
    assert main(["render", "--input", "resume.txt", "--style", "examples/valid.rcss", "--output", "o.pdf"]) == 0
    out = capsys.readouterr().out
    assert "start" in out

def test_render_invalid(capsys):
    assert main(["render", "--input", "resume.txt", "--style", "examples/invalid.rcss", "--output", "o.pdf"]) == 1
    out = capsys.readouterr().out
    assert "Invalid RCSS" in out


def test_no_command():
    assert main([]) == 1
