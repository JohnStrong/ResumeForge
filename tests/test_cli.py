"""Tests for the ResumeForge CLI."""

from resumeforge.cli import main


def test_version(capsys):
    assert main(["version"]) == 0
    assert "0.1.0" in capsys.readouterr().out


def test_render_echo(capsys):
    assert main(["render", "--input", "cv.txt", "--style", "s.rcss", "--output", "o.pdf"]) == 0
    out = capsys.readouterr().out
    assert "cv.txt" in out
    assert "s.rcss" in out
    assert "o.pdf" in out


def test_no_command():
    assert main([]) == 1
