"""fpdf2 render engine — writes RenderSections to a PDF file."""

from fpdf import FPDF

from resumeforge.models import LayoutRule
from resumeforge.renderer import RenderSection
from resumeforge.adapters.fpdf_adapter import DisplayMode


def _get_layout_value(layout: LayoutRule, prop: str, default=None):
    """Extract a single value from layout declarations."""
    for d in layout.declarations:
        if d.property == prop:
            return d.values[0]
    return default


def _parse_mm(value: str) -> float:
    """Parse a mm value string like '6mm' to float."""
    return float(value.replace("mm", ""))


def fpdf_engine(sections: list[RenderSection], layout: LayoutRule, output_path: str) -> None:
    """Render sections to a PDF file using fpdf2."""
    mode = _get_layout_value(layout, "mode", "single")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    if mode == "grid":
        _render_grid(pdf, sections, layout)
    else:
        _render_single(pdf, sections)

    pdf.output(output_path)


def _render_single(pdf: FPDF, sections: list[RenderSection]) -> None:
    """Render sections sequentially in a single column."""
    for section in sections:
        _apply_and_write(pdf, section, w=0)


def _render_grid(pdf: FPDF, sections: list[RenderSection], layout: LayoutRule) -> None:
    """Render sections into a 2-column grid layout."""
    gap = _parse_mm(_get_layout_value(layout, "column-gap", "6mm"))
    page_w = pdf.epw  # effective page width (minus margins)
    col_w = (page_w - gap) / 2
    col_x = [pdf.l_margin, pdf.l_margin + col_w + gap]
    col_y = [pdf.get_y(), pdf.get_y()]  # track y per column

    for section in sections:
        col = (section.grid_column or 1) - 1  # 0-indexed
        pdf.set_xy(col_x[col], col_y[col])
        _apply_and_write(pdf, section, w=col_w)
        col_y[col] = pdf.get_y()


def _apply_and_write(pdf: FPDF, section: RenderSection, w: float) -> None:
    """Apply state setters and write section content."""
    for setter in section.style.state_setters:
        setter(pdf)

    if section.style.display == DisplayMode.BLOCK:
        pdf.multi_cell(w=w, text=section.content, new_x="LMARGIN", new_y="NEXT", **section.style.write_params)
    else:
        pdf.cell(w=w, text=section.content, **section.style.write_params)
