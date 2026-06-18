"""Run with: python scripts/debug_renderer.py"""

from pathlib import Path
from resumeforge.parser import RcssParser
from resumeforge.transformer import transform
from resumeforge.section_mapper import SectionMapper
from resumeforge.renderer import Renderer
from resumeforge.adapters.fpdf_adapter import adapt_declarations
from resumeforge.engines.fpdf_engine import fpdf_engine

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

# Parse and transform RCSS
raw_rcss = (EXAMPLES_DIR / "valid.rcss").read_text()
result = RcssParser().parse(raw_rcss)
stylesheet = transform(result.tree)

# Map CV sections to style rules
cv_text = (EXAMPLES_DIR / "resume.txt").read_text()
styled_sections = SectionMapper().map(cv_text, stylesheet)

# Render with adapter
renderer = Renderer(adapter=adapt_declarations, engine=fpdf_engine, options={"debug": True})
renderer.render(sections=styled_sections, layout=stylesheet.layout, output_path="output.pdf")
