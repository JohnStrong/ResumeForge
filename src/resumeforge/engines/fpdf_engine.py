"""fpdf2 render engine — writes RenderSections to a PDF file."""

from fpdf import FPDF

from resumeforge.models import FontFaceRule
from resumeforge.renderer import RenderSection
from resumeforge.adapters.fpdf_adapter import DisplayMode
from resumeforge.adapters.layout_adapter import LayoutConfig
from resumeforge.adapters.heading_adapter import HeadingConfig
from resumeforge.constants import DEFAULTS


def _get_font_face_value(font_face: FontFaceRule | None, prop: str, default=None):
    """Extract a value from font_face declarations."""
    if font_face is None:
        return default
    for d in font_face.declarations:
        if d.property == prop:
            return d.values[0].strip('"')
    return default


def _register_fonts(pdf: FPDF, font_face: FontFaceRule | None) -> str:
    """Register custom fonts from @font-face and return the font family name."""
    if font_face is None:
        return DEFAULTS["font-family"]

    family = _get_font_face_value(font_face, "font-family", DEFAULTS["font-family"])
    src = _get_font_face_value(font_face, "src")
    src_bold = _get_font_face_value(font_face, "src-bold")

    if src:
        pdf.add_font(family, "", src)
    if src_bold:
        pdf.add_font(family, "B", src_bold)

    return family

def _render_heading(pdf: FPDF, heading_config: HeadingConfig | None, font_family: str) -> None:
    """Render heading with Applicant name, contact info and role/title information."""
    if heading_config is None:
        return

    lines = heading_config.content.splitlines()
    if not lines:
        return

    font_size = int(heading_config.font_size) if isinstance(heading_config.font_size, str) else heading_config.font_size
    line_height = int(heading_config.line_height) if isinstance(heading_config.line_height, str) else heading_config.line_height
    align = heading_config.align[0].upper()  # "center" -> "C", "left" -> "L", "right" -> "R"

    # First line: name — bold, always black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(font_family, style="B", size=font_size)
    pdf.multi_cell(w=0, h=line_height, text=lines[0], align=align, new_x="LMARGIN", new_y="NEXT")

    # Remaining lines: contact/title — regular, scaled down, with color if set
    if len(lines) > 1:
        if heading_config.color:
            # TODO: extract hex-to-rgb conversion to a shared adapter utility
            r, g, b = int(heading_config.color[1:3], 16), int(heading_config.color[3:5], 16), int(heading_config.color[5:7], 16)
            pdf.set_text_color(r, g, b)
        contact_size = round(font_size * 0.55)
        pdf.set_font(font_family, style="", size=contact_size)
        for line in lines[1:]:
            if line.strip():
                pdf.multi_cell(w=0, h=line_height, text=line, align=align, new_x="LMARGIN", new_y="NEXT")

    # Reset for subsequent sections
    pdf.set_text_color(0, 0, 0)
    pdf.ln(line_height)


def _render_single(pdf: FPDF, sections: list[RenderSection], font_family: str) -> None:
    """Render sections sequentially in a single column."""
    for section in sections:
        _apply_and_write(pdf, section, w=0, font_family=font_family)


def _render_grid(pdf: FPDF, sections: list[RenderSection], layout_config: LayoutConfig, font_family: str) -> None:
    """Render sections into a 2-column grid layout."""
    gap = layout_config.column_gap
    page_w = pdf.epw
    usable_w = page_w - gap
    col_widths = [usable_w * w / 100 for w in layout_config.column_widths]
    col_x = [pdf.l_margin, pdf.l_margin + col_widths[0] + gap]
    col_y = [pdf.get_y(), pdf.get_y()]

    for section in sections:
        col = (section.grid_column or 1) - 1
        pdf.set_xy(col_x[col], col_y[col])
        _apply_and_write(pdf, section, w=col_widths[col], x_after=col_x[col], font_family=font_family)
        col_y[col] = pdf.get_y()


def _apply_and_write(pdf: FPDF, section: RenderSection, w: float, font_family: str, x_after: float | None = None) -> None:
    """Apply state setters, write heading in bold, then write section content."""
    new_x = "LEFT" if x_after is not None else "LMARGIN"

    # Reset state to defaults before applying section overrides
    pdf.set_text_color(0, 0, 0)
    pdf.set_font_size(DEFAULTS["body-font-size"])

    # Apply section-level style overrides (font-size, color, etc.)
    for setter in section.style.state_setters:
        setter(pdf)

    # Resolve sizes: use section style if set, otherwise defaults
    heading_size = pdf.font_size_pt or DEFAULTS["heading-font-size"]
    body_size = pdf.font_size_pt or DEFAULTS["body-font-size"]
    line_h = section.style.write_params.get("h", DEFAULTS["line-height"])

    # Write section heading — bold, always black
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(font_family, style="B", size=heading_size)
    pdf.multi_cell(w=w, h=line_h, text=section.name, new_x=new_x, new_y="NEXT")

    # Re-apply style setters (list of callables from SectionRenderStyle) to restore
    # section color for body content — each setter is a lambda that mutates pdf state
    for setter in section.style.state_setters:
        setter(pdf)

    # Write section content — regular
    pdf.set_font(font_family, style="", size=body_size)
    write_params = {**section.style.write_params, "h": line_h}
    if section.style.display == DisplayMode.BLOCK:
        pdf.multi_cell(w=w, text=section.content, new_x=new_x, new_y="NEXT", **write_params)
    else:
        pdf.cell(w=w, text=section.content, **write_params)

def fpdf_engine(
    sections: list[RenderSection], 
    layout_config: LayoutConfig,
    output_path: str, 
    font_face: FontFaceRule | None = None,
    heading_config: HeadingConfig | None = None
) -> None:
    """Render sections to a PDF file using fpdf2."""
    pdf = FPDF()
    pdf.add_page()

    # Register custom font or use default
    font_family = _register_fonts(pdf, font_face)
    pdf.set_font(font_family, size=DEFAULTS["body-font-size"])

    _render_heading(pdf, heading_config, font_family)
    if layout_config.mode == "grid":
        _render_grid(pdf, sections, layout_config, font_family)
    else:
        _render_single(pdf, sections, font_family)

    pdf.output(output_path)
