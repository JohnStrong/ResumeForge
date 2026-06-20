"""Tests for fpdf_engine."""

import os
import pytest
from unittest.mock import patch, MagicMock

from fpdf import FPDF

from resumeforge.models import Declaration, LayoutRule
from resumeforge.renderer import RenderSection
from resumeforge.adapters.fpdf_adapter import SectionRenderStyle, DisplayMode
from resumeforge.adapters.layout_adapter import LayoutConfig
from resumeforge.engines.fpdf_engine import fpdf_engine


@pytest.fixture
def layout():
    return LayoutConfig(
        mode="single",
        columns=1,
        column_widths=[100],
        column_gap=0.0,
        margins=(20.0, 18.0, 20.0, 18.0),
    )


def _section(name, content, style=None, order=0, grid_column=None):
    return RenderSection(
        name=name,
        content=content,
        style=style or SectionRenderStyle(),
        order=order,
        grid_column=grid_column,
    )


class TestFpdfEnginePositive:
    """POSITIVE: fpdf_engine renders sections correctly."""

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_adds_page_and_sets_font(self, MockFPDF, layout):
        """POSITIVE: engine initializes PDF with a page and default font."""
        pdf = MockFPDF.return_value
        fpdf_engine([], layout, "out.pdf")
        pdf.add_page.assert_called_once()
        pdf.set_font.assert_any_call("Helvetica", size=11)

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_block_section_uses_multi_cell(self, MockFPDF, layout):
        """POSITIVE: block display sections write heading then content via multi_cell."""
        pdf = MockFPDF.return_value
        pdf.font_size_pt = 10
        style = SectionRenderStyle(display=DisplayMode.BLOCK)
        sections = [_section("HEADER", "John Smith", style)]
        fpdf_engine(sections, layout, "out.pdf")
        calls = pdf.multi_cell.call_args_list
        # First call: heading in bold
        assert calls[0][1]["text"] == "HEADER"
        # Second call: content
        assert calls[1][1]["text"] == "John Smith"

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_inline_section_uses_cell(self, MockFPDF, layout):
        """POSITIVE: inline display sections use cell to write content."""
        pdf = MockFPDF.return_value
        pdf.font_size_pt = 10
        style = SectionRenderStyle(display=DisplayMode.INLINE)
        sections = [_section("LINKS", "github.com/jsmith", style)]
        fpdf_engine(sections, layout, "out.pdf")
        pdf.cell.assert_called_once_with(w=0, text="github.com/jsmith", h=5)

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_state_setters_applied_before_write(self, MockFPDF, layout):
        """POSITIVE: state setters are called before content is written."""
        pdf = MockFPDF.return_value
        pdf.font_size_pt = 10
        call_order = []
        pdf.set_font_size.side_effect = lambda s: call_order.append("font_size")
        pdf.multi_cell.side_effect = lambda **kw: call_order.append(f"multi_cell:{kw.get('text', '')}")

        setter = lambda p: p.set_font_size(14)
        style = SectionRenderStyle(state_setters=[setter])
        sections = [_section("HEADER", "text", style)]
        fpdf_engine(sections, layout, "out.pdf")
        # font_size set before heading and content writes
        assert call_order[0] == "font_size"

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_write_params_passed_to_multi_cell(self, MockFPDF, layout):
        """POSITIVE: write_params are spread into the content multi_cell call."""
        pdf = MockFPDF.return_value
        pdf.font_size_pt = 10
        style = SectionRenderStyle(write_params={"align": "C", "h": 7.0})
        sections = [_section("HEADER", "centered", style)]
        fpdf_engine(sections, layout, "out.pdf")
        content_call = pdf.multi_cell.call_args_list[1]
        assert content_call[1]["text"] == "centered"
        assert content_call[1]["align"] == "C"
        assert content_call[1]["h"] == 7.0

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_output_called_with_path(self, MockFPDF, layout):
        """POSITIVE: pdf.output is called with the specified output path."""
        pdf = MockFPDF.return_value
        fpdf_engine([], layout, "resume.pdf")
        pdf.output.assert_called_once_with("resume.pdf")

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_multiple_sections_rendered_in_order(self, MockFPDF, layout):
        """POSITIVE: sections are written in the order they are received."""
        pdf = MockFPDF.return_value
        pdf.font_size_pt = 10
        texts = []
        pdf.multi_cell.side_effect = lambda **kw: texts.append(kw["text"])

        sections = [
            _section("HEADER", "John", order=0),
            _section("EXP", "Engineer", order=1),
        ]
        fpdf_engine(sections, layout, "out.pdf")
        # Heading then content for each section in order
        assert texts == ["HEADER", "John", "EXP", "Engineer"]


class TestFpdfEngineE2E:
    """E2E: write a real PDF and verify content."""

    def test_pdf_contains_section_content(self, layout, tmp_path):
        """POSITIVE: generated PDF contains headings and text from all sections."""
        from pypdf import PdfReader

        output = str(tmp_path / "test_output.pdf")
        sections = [
            _section("HEADER", "Jane Doe", order=0),
            _section("EXPERIENCE", "Software Engineer at ACME", order=1),
        ]
        fpdf_engine(sections, layout, output)

        assert os.path.exists(output)
        reader = PdfReader(output)
        page_text = reader.pages[0].extract_text()
        # Verify headings are rendered
        assert "HEADER" in page_text
        assert "EXPERIENCE" in page_text
        # Verify content is rendered
        assert "Jane Doe" in page_text
        assert "Software Engineer at ACME" in page_text

    def test_grid_layout_renders_both_columns(self, tmp_path):
        """POSITIVE: grid mode renders sections in separate columns."""
        from pypdf import PdfReader

        grid_layout = LayoutConfig(
            mode="grid",
            columns=2,
            column_widths=[50, 50],
            column_gap=6.0,
            margins=(20.0, 18.0, 20.0, 18.0),
        )
        output = str(tmp_path / "grid_output.pdf")
        sections = [
            _section("SKILLS", "Python\nTypeScript", order=0, grid_column=1),
            _section("EXPERIENCE", "Engineer at Acme", order=1, grid_column=2),
        ]
        fpdf_engine(sections, grid_layout, output)

        assert os.path.exists(output)
        reader = PdfReader(output)
        page_text = reader.pages[0].extract_text()
        assert "SKILLS" in page_text
        assert "Python" in page_text
        assert "EXPERIENCE" in page_text
        assert "Engineer at Acme" in page_text


class TestFpdfEngineFonts:
    """Tests for font registration and usage in fpdf_engine."""

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_no_font_face_uses_default_helvetica(self, MockFPDF, layout):
        """POSITIVE: without @font-face, engine uses Helvetica as default."""
        pdf = MockFPDF.return_value
        fpdf_engine([], layout, "out.pdf", font_face=None)
        pdf.add_font.assert_not_called()
        pdf.set_font.assert_any_call("Helvetica", size=11)

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_font_face_registers_regular(self, MockFPDF, layout):
        """POSITIVE: @font-face with src registers the regular variant."""
        from resumeforge.models import FontFaceRule
        pdf = MockFPDF.return_value
        font_face = FontFaceRule(declarations=[
            Declaration(property="font-family", values=['"Carlito"']),
            Declaration(property="src", values=['"fonts/Carlito-Regular.ttf"']),
        ])
        fpdf_engine([], layout, "out.pdf", font_face=font_face)
        pdf.add_font.assert_any_call("Carlito", "", "fonts/Carlito-Regular.ttf")

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_font_face_registers_bold(self, MockFPDF, layout):
        """POSITIVE: @font-face with src-bold registers the bold variant."""
        from resumeforge.models import FontFaceRule
        pdf = MockFPDF.return_value
        font_face = FontFaceRule(declarations=[
            Declaration(property="font-family", values=['"Carlito"']),
            Declaration(property="src", values=['"fonts/Carlito-Regular.ttf"']),
            Declaration(property="src-bold", values=['"fonts/Carlito-Bold.ttf"']),
        ])
        fpdf_engine([], layout, "out.pdf", font_face=font_face)
        pdf.add_font.assert_any_call("Carlito", "", "fonts/Carlito-Regular.ttf")
        pdf.add_font.assert_any_call("Carlito", "B", "fonts/Carlito-Bold.ttf")

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_font_face_sets_registered_font(self, MockFPDF, layout):
        """POSITIVE: engine uses the registered font family for set_font."""
        from resumeforge.models import FontFaceRule
        pdf = MockFPDF.return_value
        font_face = FontFaceRule(declarations=[
            Declaration(property="font-family", values=['"Carlito"']),
            Declaration(property="src", values=['"fonts/Carlito-Regular.ttf"']),
        ])
        fpdf_engine([], layout, "out.pdf", font_face=font_face)
        pdf.set_font.assert_any_call("Carlito", size=11)

    @patch("resumeforge.engines.fpdf_engine.FPDF")
    def test_heading_uses_bold_of_registered_font(self, MockFPDF, layout):
        """POSITIVE: section headings use bold style of the registered font."""
        from resumeforge.models import FontFaceRule
        pdf = MockFPDF.return_value
        pdf.font_size_pt = 11
        font_face = FontFaceRule(declarations=[
            Declaration(property="font-family", values=['"Carlito"']),
            Declaration(property="src", values=['"fonts/Carlito-Regular.ttf"']),
            Declaration(property="src-bold", values=['"fonts/Carlito-Bold.ttf"']),
        ])
        sections = [_section("HEADER", "Jane Doe", order=0)]
        fpdf_engine(sections, layout, "out.pdf", font_face=font_face)
        pdf.set_font.assert_any_call("Carlito", style="B", size=11)
        pdf.set_font.assert_any_call("Carlito", style="", size=11)
