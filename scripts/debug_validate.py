"""Run with: python scripts/debug_validate.py"""

from resumeforge.parser import RcssParser

parser = RcssParser()

# --- Positive case: valid RCSS ---
valid_rcss = """\
layout { mode: single; margins: 20mm 18mm 20mm 18mm; }
section[name="HEADER"] { padding: 8mm; align: center; }
"""

result = parser.validate(valid_rcss)
print(f"[VALID RCSS]   valid={result.valid}, message={result.message}")

# --- Negative case: invalid selector ---
bad_selector = """\
header { padding: 8mm; }
"""

result = parser.validate(bad_selector)
print(f"[BAD SELECTOR] valid={result.valid}, message={result.message}")

# --- Negative case: invalid declaration (missing semicolon) ---
bad_declaration = """\
layout { mode: single }
"""

result = parser.validate(bad_declaration)
print(f"[BAD DECL]     valid={result.valid}, message={result.message}")
