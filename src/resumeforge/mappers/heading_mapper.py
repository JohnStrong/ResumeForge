from resumeforge.models import HeadingRule, Stylesheet, StyledHeading

def map(text: str, stylesheet: Stylesheet) -> StyledHeading:
    """Extract all text content until the first 'section' is found according to the user rcss selectors.
    
    This is our heading
    """
    
    heading_rule: HeadingRule = stylesheet.heading
    section_names = [s.name for s in stylesheet.sections]
    lines = text.splitlines()
    content_lines = []
    for line in lines:
        if line.strip() in section_names:
            # we hit a section as defined in the users rcss, everything before is presumed to be the heading
            break
        content_lines.append(line)

    content = "\n".join(content_lines).strip()
    if not content:
        raise ValueError("CV text must have heading content (name/contact) before the first section")

    return StyledHeading(content=content, rule=heading_rule)
