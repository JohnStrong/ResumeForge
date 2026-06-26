"""Default CV typography constants.

Used as fallbacks when no overrides are specified in @font-face or section rules.
Based on professional tech CV recommendations: clear, conservative, ATS-friendly.
"""

DEFAULTS = {
    "font-family": "Helvetica",
    "heading-font-size": 12,       # section headings: 11-14pt bold
    "body-font-size": 11,          # body content: 10.5-12pt regular
    "title-font-size": 22,         # name/title: 20-26pt bold
    "line-height": 5,              # ~1.1 spacing in mm
}