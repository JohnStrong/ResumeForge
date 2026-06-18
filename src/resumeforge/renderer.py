"""Renders StyledSections into a paginated A4 PDF."""

from typing import Callable
from resumeforge.models import LayoutRule, StyledSection, Declaration
from resumeforge.adapters.fpdf_adapter import adapt_declarations, SectionRenderStyle

 # Type alias for any adapter function
StyleAdapter = Callable[[list[Declaration]], SectionRenderStyle]

class Renderer:
    """Takes styled sections and a layout rule, renders to PDF."""

    def __init__(self, adapter: StyleAdapter, options: dict | None = None):
        self._debug = options.get("debug") is True if options else False
        self.adapter = adapter

    def _log(self, step: str, detail: str):
        if self._debug:
            print(f"[renderer:{step}] {detail}")

    def render(self, sections: list[StyledSection], layout: LayoutRule, output_path: str) -> None:
        """Render styled sections to a PDF file at output_path."""
        self._log("start", f"rendering {len(sections)} sections to {output_path}")
        self._log("layout", f"{layout.declarations}")

        for section in sorted(sections, key=lambda s: s.order):
            self._log("section", f"[{section.order}] {section.name}")
            adatped_section = self.adapter(section.rule.declarations)
            self._log("adapted_section", f"[{adatped_section}]")

        # TODO: implement layout engine + PDF generation
        self._log("done", output_path)
