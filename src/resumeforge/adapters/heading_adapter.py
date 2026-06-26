from dataclasses import dataclass

from resumeforge.models import StyledHeading

@dataclass
class HeadingConfig:
    content: str
    font_size: int
    align: str
    line_height: int
    color: str | None = None


def adapt_heading(heading: StyledHeading | None) -> HeadingConfig | None:
    """Convert a StyledHeading into a typed HeadingConfig for the render engine.

    Applies ATS-friendly defaults (font_size=20, align=center, line_height=7)
    and overrides with any user-specified declarations from the heading rule.
    Returns None if heading is None (no heading content in CV).

    TODO: Refactor to use _DECLARATION_ADAPTERS map and produce state_setters
    (pdf-mutating callables) like fpdf_adapter does for SectionRenderStyle.
    This would remove manual type conversion here and hex-to-rgb in the engine.
    """
    if heading is None:
        return None

    props = {
        "content": heading.content,
        "font_size": 20,
        "align": "center",
        "line_height": 7,
    }

    if heading.rule:
        for decl in heading.rule.declarations:
            key = decl.property.replace("-", "_")
            value = decl.values[0]
            if key == "font_size":
                value = int(value.rstrip("pt"))
            elif key == "line_height":
                value = int(value)
            props[key] = value
    return HeadingConfig(**props)
