"""Run with: python scripts/debug_renderer.py"""

from pathlib import Path
from resumeforge.parser import RcssParser
from resumeforge.transformer import transform
from resumeforge.mappers.section_mapper import SectionMapper
from resumeforge.mappers.heading_mapper import map as map_heading
from resumeforge.renderer import Renderer
from resumeforge.adapters.fpdf_adapter import adapt_declarations
from resumeforge.adapters.layout_adapter import adapt_layout
from resumeforge.engines.fpdf_engine import fpdf_engine

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

# Parse and transform RCSS
raw_rcss = (EXAMPLES_DIR / "valid.rcss").read_text()
result = RcssParser().parse(raw_rcss)
stylesheet = transform(result.tree)

# Map CV heading and sections
cv_text = (EXAMPLES_DIR / "resume.txt").read_text()
styled_heading = map_heading(cv_text, stylesheet)
styled_sections = SectionMapper().map(cv_text, stylesheet)

# Render with adapter
renderer = Renderer(adapter=adapt_declarations, engine=fpdf_engine, layout_adapter=adapt_layout, options={"debug": True})
renderer.render(sections=styled_sections, layout=stylesheet.layout, output_path="output.pdf", font_face=stylesheet.font_face, heading=styled_heading)
