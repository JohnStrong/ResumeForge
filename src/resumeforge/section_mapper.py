"""Maps raw CV text sections to their corresponding RCSS style rules."""

from resumeforge.models import Stylesheet, StyledSection, RawSection
from resumeforge.validator import run_validators

SECTION_MAPPER_VALIDATORS = [
    {
        "check": lambda raw_sections, section_names: len(raw_sections) > 0,
        "message": "No sections found in CV text matching the stylesheet. "
                    "Ensure headings match section[name=\"...\"] values exactly.",
    },
    {
        "check": lambda raw_sections, section_names: {s.name for s in raw_sections} == section_names,
        "message": "CV text is missing one or more sections defined in the stylesheet.",
    },
]

class SectionMapper:
    """Splits a plain-text CV into sections and pairs each with its RCSS style rule.

    A section is identified by a heading line that exactly matches a section name
    defined in the Stylesheet (e.g. 'EXPERIENCE', 'EDUCATION', or 'John Joseph Strong').
    Content is everything between that heading and the next heading or EOF.
    """

    def __init__(self, options: dict | None = None):
        self._debug = options.get("debug") is True if options else False

    def _log_section(self, section: tuple[str, str]):
        """Print section heading and body when debug mode is enabled."""
        if self._debug:
            print(f"heading: {section[0]}\nbody: {section[1]}")

    def _split_sections(self, text: str, section_names: set[str]) -> list[RawSection]:
        """Split raw CV text into (name, content) pairs.

        Walks line by line. A line whose stripped value matches a known section name
        starts a new section. All subsequent lines (including blank lines) are captured
        as content until the next heading or EOF.

        Returns a list of (section_name, content) tuples in document order.
        Text before the first matching heading is silently ignored.
        """
        sections = []
        current_name = None
        current_lines = []
        current_order = 0

        for line in text.splitlines():
            # Strip only for heading comparison — raw line preserved for content
            stripped = line.strip()
            if stripped in section_names:
                # New heading found — save the previous section if one was open
                if current_name:
                    sections.append(RawSection.fromText(current_name, current_lines, current_order))
                    current_order += 1
                # Start collecting for this new section
                current_name = stripped
                current_lines = []
            elif current_name:
                # Inside a section — append raw line (preserves whitespace/blank lines)
                current_lines.append(line)
            # else: before any heading (preamble) — silently skipped

        # EOF reached — flush the last open section
        if current_name:
            sections.append(RawSection.fromText(current_name, current_lines, current_order))

        return sections

    def _apply_rules(self, raw_sections: list[tuple[str, str]], stylesheet: Stylesheet) -> list[StyledSection]:
        """Match each (name, content) pair to its SectionRule from the stylesheet.

        Returns a list of StyledSection objects ready for rendering.
        """
        pass
        
    def map(self, text: str, stylesheet: Stylesheet) -> list[StyledSection]:
        """Map raw CV text to a list of StyledSection objects.

        Splits the text into sections by heading, then pairs each section
        with its matching SectionRule from the stylesheet.
        """
        section_names = {s.name for s in stylesheet.sections}
        raw_sections = self._split_sections(text=text, section_names=section_names)
        run_validators(SECTION_MAPPER_VALIDATORS, raw_sections, section_names)
        return self._apply_rules(raw_sections=raw_sections, stylesheet=stylesheet)