# ResumeForge — README

![version](https://img.shields.io/badge/version-0.1.0-blue)
![build](https://img.shields.io/badge/build-passing-brightgreen)
![coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![python](https://img.shields.io/badge/python-3.12+-yellow)
![license](https://img.shields.io/badge/license-MIT-green)

## Table of Contents
- [About](#about)
- [Setup](#setup)
- [Usage](#usage)
  - [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [RCSS DSL](#rcss-dsl)
  - [Section identification](#section-identification)
  - [.rcss basics (MVP)](#rcss-basics-mvp)
  - [Example .rcss snippets](#example-rcss-snippets)
- [CLI: example POC commands (WIP)](#cli-example-poc-commands-wip)
  - [Expected file formats](#expected-file-formats)
  - [Project scope (MVP)](#project-scope-mvp)
  - [Example project layout](#example-project-layout)

## About
ResumeForge converts a plain UTF-8 text CV into a styled multi-page A4 PDF using a small CSS-like DSL (.rcss). Supports two layout modes: standard (single-column) and grid (2-column). MVP excludes font-face loading and decorative assets.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# Render a plain-text CV to styled PDF
resumeforge render --input resume.txt --style resume-single.rcss --output resume.pdf

# Validate an RCSS style file for syntax errors
resumeforge validate --style resume-single.rcss

# Print CLI version
resumeforge version
```

### Troubleshooting

**"Unexpected token ... Expected one of: LAYOUT, SECTION"**
Your `.rcss` file has an invalid selector. Only `layout { ... }` and `section[name="..."] { ... }` are valid. Check for typos in the selector keyword.

**"Unexpected token ... Expected one of: SEMICOLON"**
A property declaration is missing its trailing semicolon. Every declaration must end with `;`.

**"RCSS must contain a layout { ... } rule"**
The transformer could not find a `layout` block in your `.rcss` file. Every stylesheet requires one.

**"RCSS must contain at least one section[name=...] rule"**
Your `.rcss` defines a layout but no section rules. Add at least one `section[name="..."] { ... }` block.

**"No sections found in CV text matching the stylesheet"**
The headings in your `.txt` file don't match any `section[name="..."]` values in the stylesheet. Headings must match exactly (case-sensitive, full line).

**"CV text is missing one or more sections defined in the stylesheet"**
Your `.txt` file is missing a heading that the stylesheet expects. Ensure every `section[name="..."]` in the `.rcss` has a corresponding heading line in the CV text.

**"No raw sections to apply rules to"**
The section mapper received no parsed sections to style. This typically means your CV text was empty or contained no lines matching any stylesheet section names.

**"No matching stylesheet rule for one or more sections"**
A section was parsed from the CV text but has no corresponding `section[name="..."]` rule in the stylesheet. Ensure every heading in your `.txt` file has a matching rule in the `.rcss`.

## Testing

```bash
pip install pytest
pytest
```

## RCSS DSL

> Grammar definition: [`src/resumeforge/grammar/rcss.lark`](src/resumeforge/grammar/rcss.lark)

### Section identification
- A section begins at a heading line that matches the pattern ^{HEADING} (a full-line header like: LINKS, WORK EXPERIENCE, EDUCATION).
- A section contains all text from that heading line up to the next heading line or EOF.
- Section selectors in .rcss match the heading text exactly (e.g., section[name="WORK EXPERIENCE"]).

### .rcss basics (MVP)
- File extension: .rcss
- Grid mode supports exactly 2 columns. grid-column must be 1 or 2 for each section in grid mode.

#### Layout properties (in `layout { ... }`)
| Property | Values | Description |
|---|---|---|
| `mode` | `single`, `grid` | Page layout mode |
| `columns` | `2` | Number of columns (grid mode) |
| `column-gap` | e.g. `6mm` | Gap between columns |
| `margins` | e.g. `20mm 18mm 20mm 18mm` | Page margins (top right bottom left) |

#### Section properties (in `section[name="..."] { ... }`)

**Style properties** (PDF render mode — applied as PDF state before writing):
| Property | Values | Description |
|---|---|---|
| `font-size` | e.g. `12pt` | Text size |
| `color` | e.g. `#333333` | Text color (hex) |
| `background-color` | e.g. `#f0f0f0` | Section fill color (hex) |

**Write properties** (PDF render mode — control how content is rendered):
| Property | Values | Description |
|---|---|---|
| `align` | `left`, `center`, `right` | Text alignment |
| `line-height` | e.g. `7` | Line height in mm |
| `display` | `block`, `inline` | Block wraps text (multi-line), inline flows horizontally |

**Layout positioning** (grid mode only):
| Property | Values | Description |
|---|---|---|
| `grid-column` | `1`, `2` | Which column to place the section in |
| `padding` | e.g. `8mm` | Inner spacing |
| `width` | e.g. `1fr` | Proportional column width |

### Example .rcss snippets
Single-column (resume-single.rcss)
```css
layout { mode: single; margins: 20mm 18mm 20mm 18mm; }

section[name="HEADER"] {
  padding: 8mm;
  align: center;
}
```

Two-column grid (resume-grid.rcss)
```css
layout { mode: grid; columns: 2; column-gap: 6mm; margins: 20mm 18mm 20mm 18mm; }

/* Place by heading text and explicit column (1 or 2) */
section[name="SIDEBAR"] {
  grid-column: 1;
  padding: 6mm;
  width: 1fr;
}

section[name="MAIN"] {
  grid-column: 2;
  padding: 6mm;
  width: 1fr;
}

section[name="HEADER"] {
  grid-column: 1;
  padding: 8mm;
  align: center;
}
```

## CLI: example POC commands (WIP)
Assume binary: resumeforge

Single-column:
```bash
resumeforge render --input resume.txt --style resume-single.rcss --output resume-single.pdf
```

Two-column grid:
```bash
resumeforge render --input resume.txt --style examples/valid.rcss --output resume-grid.pdf
```

Validate style file:
```bash
resumeforge validate --style examples/valid.rcss
```

### Expected file formats
- resume.txt — plain UTF-8 text with headings on their own lines (e.g., WORK EXPERIENCE).
- *.rcss — style file using rules above.
- Output: multi-page PDF sized to A4.

### Project scope (MVP)
- Parse sections by heading lines, map .rcss styles, layout single or 2-column grid, paginate and render PDF.
- No font-face loading or external assets. Only 2 columns supported in grid mode.

### Example project layout
- bin/resumeforge
- src/{parser,layout,renderer,cli}
- examples/{resume.txt,resume-single.rcss,resume-grid.rcss}
- tests/{unit,visual}

## Tech stack evaluation

- DSL parsing
  - Lark — easy grammar-based parser (Earley/LALR), quick AST output.
  - ANTLR (Python target) — grammar-first, good if DSL will grow complex.
  - parsy / parsimonious — lightweight parser-combinator options for small grammars.
  - dataclasses / pydantic — represent and validate parsed AST/style objects.

- Layout & styling engine (apply .rcss to section content)
  - Build a layout tree (blocks, columns, paddings, margins, flow, pagination).
  - Implement simple box model and a 2-column flow engine that respects grid-column: 1|2 and paginates to A4.

- Direct PDF libraries (no HTML)
  - ReportLab — mature, full-featured programmatic PDF generation (draw text, shapes, images, pages).
  - fpdf2 — lightweight, Pythonic, easier API for PDFs and text layout.
  - PyPDF2 / pikepdf — post-processing, merging, metadata, or encryption (not for layout).

- Typography & measurements
  - HarfBuzz/pyharfbuzz or use ReportLab text-wrap primitives for advanced shaping if needed later.
  - Use mm/mm-to-point helpers and a consistent unit system for A4.

- CLI & tooling
  - Typer or Click for CLI.
  - pytest for tests, black/isort for formatting.
  - packaging: poetry or setuptools.

- Testing & visual verification
  - Generate small PDFs and compare rendering output (visual tests) or use heuristics on text positions.

Suggested minimal stack for MVP
- Parsing: Lark + dataclasses
- Layout: custom box-model + simple paginator (A4 points)
- PDF output: ReportLab (or fpdf2 if you prefer smaller lib)
- CLI: Typer