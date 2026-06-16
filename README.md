# ResumeForge — README

## Table of Contents
- [About](#about)
- [Setup](#setup)
- [Usage](#usage)
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
# Render a resume
resumeforge render --input resume.txt --style resume-single.rcss --output resume.pdf

# Show version
resumeforge version
```

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
- Supported properties: padding, margin, background-color, color, align, width (fr or fixed), gap, column-gap, font-size, line-height, display (block/inline), grid-column (1 or 2).
- Grid mode supports exactly 2 columns. grid-column must be 1 or 2 for each section in grid mode.

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
resumeforge render --input resume.txt --style resume-single.rcss --layout single --output resume-single.pdf
```

Two-column grid:
```bash
resumeforge render --input resume.txt --style resume-grid.rcss --layout grid --output resume-grid.pdf
```

Validate style file:
```bash
resumeforge validate-style --style resume-grid.rcss
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