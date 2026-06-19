"""Run with: python scripts/debug_transform.py

Expected output:

[layout_selector] []
[value] [Token('VALUE', 'grid')]
[declaration] [Token('PROPERTY', 'mode'), None]
[value] [Token('VALUE', '2')]
[declaration] [Token('PROPERTY', 'columns'), None]
[value] [Token('VALUE', '6mm')]
[declaration] [Token('PROPERTY', 'column-gap'), None]
[value] [Token('VALUE', '20mm'), Token('VALUE', '18mm'), Token('VALUE', '20mm'), Token('VALUE', '18mm')]
[declaration] [Token('PROPERTY', 'margins'), None]
[rule] [None, None, None, None, None]
[section_selector] [Token('STRING', '"HEADER"')]
[value] [Token('VALUE', '1')]
[declaration] [Token('PROPERTY', 'grid-column'), None]
[value] [Token('VALUE', '8mm')]
[declaration] [Token('PROPERTY', 'padding'), None]
[value] [Token('VALUE', 'center')]
[declaration] [Token('PROPERTY', 'align'), None]
[rule] [None, None, None, None]
[section_selector] [Token('STRING', '"EXPERIENCE"')]
[value] [Token('VALUE', '2')]
[declaration] [Token('PROPERTY', 'grid-column'), None]
[value] [Token('VALUE', '6mm')]
[declaration] [Token('PROPERTY', 'padding'), None]
[value] [Token('VALUE', '12pt')]
[declaration] [Token('PROPERTY', 'font-size'), None]
[rule] [None, None, None, None]
[start] [None, None, None]
"""

from resumeforge.parser import RcssParser
from resumeforge.transformer import transform

MOCK_RCSS = """\
@font-face { font-family: "Consolas"; src: "./fonts/Consolas.ttf"; font-weight: bold; }
layout { mode: grid; columns: 2; column-gap: 6mm; margins: 20mm 18mm 20mm 18mm; }
section[name="HEADER"] { grid-column: 1; padding: 8mm; align: center; }
section[name="EXPERIENCE"] { grid-column: 2; padding: 6mm; font-size: 12pt; }
"""

result = RcssParser().parse(MOCK_RCSS)
stylesheet = transform(result.tree, {"debug": True})
print(f"\nResult: {stylesheet}")
print(f"\nFont face: {stylesheet.font_face}")
