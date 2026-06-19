"""Run with: python scripts/debug_parse.py

Example output:

  start
    rule
      layout_selector
      declaration
        mode
        value     grid
      declaration
        columns
        value     2
      declaration
        column-gap
        value     6mm
      declaration
        margins
        value
          20mm
          18mm
          20mm
          18mm
    rule
      section_selector    "HEADER"
      declaration
        grid-column
        value     1
      declaration
        padding
        value     8mm
      declaration
        align
        value     center
    rule
      section_selector    "WORK EXPERIENCE"
      declaration
        grid-column
        value     2
      declaration
        font-size
        value     12pt
      declaration
        line-height
        value     1.4
"""

from resumeforge.parser import RcssParser

MOCK_RCSS = """\
@font-face { font-family: "Consolas"; src: "./fonts/Consolas.ttf"; font-weight: bold; }

layout {
    mode: grid;
    columns: 2;
    column-gap: 6mm;
    margins: 20mm 18mm 20mm 18mm;
}

section[name="HEADER"] {
    grid-column: 1;
    padding: 8mm;
    align: center;
}

section[name="WORK EXPERIENCE"] {
    grid-column: 2;
    font-size: 12pt;
    line-height: 1.4;
}
"""

parser = RcssParser()
parser.parse(MOCK_RCSS, {"debug": True})
