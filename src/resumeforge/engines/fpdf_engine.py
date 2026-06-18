"""fpdf2 render engine — writes RenderSections to a PDF file."""

from fpdf import FPDF

from resumeforge.models import LayoutRule
from resumeforge.renderer import RenderSection
from resumeforge.adapters.fpdf_adapter import DisplayMode


def fpdf_engine(sections: list[RenderSection], layout: LayoutRule, output_path: str) -> None:
    """Render sections to a PDF file using fpdf2."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    for section in sections:
        # Apply state setters (font-size, color, background-color)
        for setter in section.style.state_setters:
            setter(pdf)

        # Write content using appropriate method based on display mode
        if section.style.display == DisplayMode.BLOCK:
            pdf.multi_cell(w=0, text=section.content, new_x="LMARGIN", new_y="NEXT", **section.style.write_params)
        else:
            pdf.cell(w=0, text=section.content, **section.style.write_params)

    pdf.output(output_path)
