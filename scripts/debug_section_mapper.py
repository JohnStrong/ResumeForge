"""Run with: python scripts/debug_section_mapper.py"""

from pathlib import Path
from resumeforge.parser import RcssParser
from resumeforge.transformer import transform
from resumeforge.section_mapper import SectionMapper

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

MOCK_CV = """\
HEADER
John Smith
john@example.com | github.com/jsmith

EXPERIENCE
Senior Engineer at ACME Corp
- Built scalable microservices
- Led team of 5 engineers
"""

INVALID_CV_EMPTY = ""
INVALID_CV_MISSING_SECTION = """\
HEADER
John Smith
"""

# --- Valid case ---
print("=== VALID: map CV with examples/valid.rcss ===\n")
rcss_text = (EXAMPLES_DIR / "valid.rcss").read_text()
result = RcssParser().parse(rcss_text)
stylesheet = transform(result.tree)
mapper = SectionMapper({"debug": True})
styled_sections = mapper.map(MOCK_CV, stylesheet)

for s in styled_sections:
    print(f"[{s.order}] {s.name}")
    print(f"    content: {s.content[:60]}...")
    print(f"    rule: {s.rule.declarations}")
    print()

# --- Invalid cases ---
print("=== INVALID: empty CV text ===\n")
try:
    mapper.map(INVALID_CV_EMPTY, stylesheet)
except ValueError as e:
    print(f"  ERROR: {e}\n")

print("=== INVALID: CV missing EXPERIENCE section ===\n")
try:
    mapper.map(INVALID_CV_MISSING_SECTION, stylesheet)
except ValueError as e:
    print(f"  ERROR: {e}\n")

print("=== INVALID: invalid .rcss file (examples/invalid.rcss) ===\n")
invalid_rcss = (EXAMPLES_DIR / "invalid.rcss").read_text()
invalid_result = RcssParser().parse(invalid_rcss)
if not invalid_result.valid:
    print(f"  PARSE ERROR: {invalid_result.message}\n")
else:
    try:
        invalid_stylesheet = transform(invalid_result.tree)
        mapper.map(MOCK_CV, invalid_stylesheet)
    except ValueError as e:
        print(f"  TRANSFORM ERROR: {e}\n")
