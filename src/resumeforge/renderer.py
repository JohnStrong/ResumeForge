"""Renders StyledSections into a paginated A4 PDF."""

from resumeforge.models import LayoutRule, StyledSection


class Renderer:
    """Takes styled sections and a layout rule, renders to PDF."""

    def __init__(self, options: dict | None = None):
        self._debug = options.get("debug") is True if options else False

    def _log(self, step: str, detail: str):
        if self._debug:
            print(f"[renderer:{step}] {detail}")

    def render(self, sections: list[StyledSection], layout: LayoutRule, output_path: str) -> None:
        """Render styled sections to a PDF file at output_path."""
        self._log("start", f"rendering {len(sections)} sections to {output_path}")
        self._log("layout", f"{layout.declarations}")

        for section in sections:
            self._log("section", f"[{section.order}] {section.name}")

        # TODO: implement layout engine + PDF generation
        self._log("done", output_path)
