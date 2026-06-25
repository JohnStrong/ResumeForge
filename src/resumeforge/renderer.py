"""Renders StyledSections into a paginated A4 PDF."""

from dataclasses import dataclass
from typing import Callable

from resumeforge.models import FontFaceRule, LayoutRule, StyledSection, Declaration, StyledHeading
from resumeforge.adapters.fpdf_adapter import SectionRenderStyle
from resumeforge.adapters.layout_adapter import LayoutConfig

# Type alias for any adapter function
StyleAdapter = Callable[[list[Declaration]], SectionRenderStyle]
LayoutAdapter = Callable[[LayoutRule], LayoutConfig]

@dataclass
class RenderSection:
    """A section prepared for the engine: content paired with its adapted style."""
    name: str
    content: str
    style: SectionRenderStyle
    order: int
    grid_column: int | None = None


# Type alias for any render engine function
RenderEngine = Callable[[list["RenderSection"], LayoutConfig, str, FontFaceRule | None, StyledHeading | None], None]

class Renderer:
    """Takes styled sections and a layout rule, renders to PDF.

    Adapter converts RCSS declarations into rendering instructions.
    Engine writes the adapted sections to a specific output format.
    """

    def __init__(self, adapter: StyleAdapter, engine: RenderEngine, layout_adapter: LayoutAdapter, options: dict | None = None):
        self._debug = options.get("debug") is True if options else False
        self._adapter = adapter
        self._engine = engine
        self._layout_adapter = layout_adapter

    def _log(self, step: str, detail: str):
        if self._debug:
            print(f"[renderer:{step}] {detail}")

    def render(self, 
            sections: list[StyledSection],
            layout: LayoutRule, 
            output_path: str, 
            font_face: FontFaceRule | None = None,
            heading: StyledHeading | None = None
        ) -> None:
        """Render styled sections to a PDF file at output_path."""
        self._log("start", f"rendering {len(sections)} sections to {output_path}")
        self._log("layout", f"{layout.declarations}")
        if heading is not None:
            self._log("heading", f"{heading.rule.declarations if heading.rule else 'defaults'}")

        layout_config = self._layout_adapter(layout)
        self._log("layout_config", f"{layout_config}")

        render_sections = []
        for section in sorted(sections, key=lambda s: s.order):
            self._log("section", f"[{section.order}] {section.name}")
            style = self._adapter(section.rule.declarations)
            self._log("adapted", f"{style}")
            grid_column = next(
                (int(d.values[0]) for d in section.rule.declarations if d.property == "grid-column"),
                None,
            )
            render_sections.append(RenderSection(
                name=section.name,
                content=section.content,
                style=style,
                order=section.order,
                grid_column=grid_column,
            ))

        self._engine(render_sections, layout_config, output_path, font_face=font_face, heading=heading)
        self._log("done", output_path)
