"""Adapter that converts RCSS declarations into fpdf2 rendering instructions."""

from dataclasses import dataclass, field
from enum import Enum

from resumeforge.models import Declaration


class DisplayMode(Enum):
    """Determines which fpdf2 write method to use for section content."""
    BLOCK = "block"    # → multi_cell
    INLINE = "inline"  # → cell


@dataclass
class SectionRenderStyle:
    """Adapted RCSS declarations for PDF rendering.

    Separates declarations into state mutations applied before writing
    content, parameters passed to the write call, and the display mode
    that determines which write method to use.
    """
    state_setters: list[callable] = field(default_factory=list)
    write_params: dict = field(default_factory=dict)
    display: DisplayMode = DisplayMode.BLOCK


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string like '#333333' to an (r, g, b) tuple."""
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# State setters — mutate pdf state before writing content
STATE_HANDLERS = {
    "font-size": lambda values: lambda pdf: pdf.set_font_size(float(values[0].replace("pt", ""))),
    "color": lambda values: lambda pdf: pdf.set_text_color(*_hex_to_rgb(values[0])),
    "background-color": lambda values: lambda pdf: pdf.set_fill_color(*_hex_to_rgb(values[0])),
}

# Write params — passed to multi_cell/cell at write time
WRITE_PARAM_HANDLERS = {
    "align": lambda values: ("align", values[0][0].upper()),
    "line-height": lambda values: ("h", float(values[0])),
}


def adapt_declarations(declarations: list[Declaration]) -> SectionRenderStyle:
    """Convert RCSS declarations into a SectionRenderStyle for rendering.

    Classifies each declaration as a state setter, a write parameter,
    or a display mode directive.
    """
    style = SectionRenderStyle()
    for decl in declarations:
        if decl.property == "display":
            style.display = DisplayMode(decl.values[0])
        elif decl.property in STATE_HANDLERS:
            style.state_setters.append(STATE_HANDLERS[decl.property](decl.values))
        elif decl.property in WRITE_PARAM_HANDLERS:
            key, value = WRITE_PARAM_HANDLERS[decl.property](decl.values)
            style.write_params[key] = value
    return style
