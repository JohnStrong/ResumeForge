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
            props[key] = decl.values[0]
    return HeadingConfig(**props)
