from resumeforge.models import Stylesheet, StyledSection

class SectionMapper:
    def __init__(self, options: dict | None = None):
        super().__init__()
        self._debug = options.get("debug") is True if options else False

    def _log_section(self, section: tuple[str, str]):
        if self._debug:
            print(f"heading: {section[0]} \\n body: {section[1]}")

    def map(self, text: str, stylesheet: Stylesheet) -> list[StyledSection]:
        """Maps a raw txt str content to the stylesheet sections."""
        section_names = {s.name for s in stylesheet.sections}
        raw_sections = self._split_sections(text=text, section_names=section_names)
        return self._apply_rules(raw_sections=raw_sections, stylesheet=stylesheet)

    def _split_sections(self, text: str, section_names: set[str]) -> list[tuple[str, str]]:
        """Split text into (name, content) pairs by heading lines."""
        sections = []
        current_name = None
        current_lines = []

        for line in text.splitlines():
            stripped = line.strip()
            if stripped in section_names:
                # New heading found — save the previous section if one was open
                if current_name:
                    sections.append((current_name, "\n".join(current_lines)))
                # Start collecting for this new section
                current_name = stripped
                current_lines = []
            elif current_name:
                    current_lines.append(line)
        
        # EOF reached — flush the last open section
        if current_name:
            sections.append((current_name, "\n".join(current_lines)))
        
        return sections

    def _apply_rules(self, raw_sections: list[tuple[str, str]], stylesheet: Stylesheet) -> list[StyledSection]:
        """Match each raw section to its SectionRule from the stylesheet."""
        pass
    