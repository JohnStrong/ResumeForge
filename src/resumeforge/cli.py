"""ResumeForge CLI entry point."""

import argparse
import sys
from pathlib import Path

from resumeforge.parser import RcssParser
from resumeforge.transformer import transform
from resumeforge.section_mapper import SectionMapper


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resumeforge",
        description="Convert plain-text CVs into styled A4 PDFs using RCSS.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # render cv txt to pdf command using rcss style file (formatting, style rules)
    render = subparsers.add_parser("render", help="Render a resume to PDF")
    render.add_argument("--input", required=True, help="Path to input .txt file")
    render.add_argument("--style", required=True, help="Path to .rcss style file")
    render.add_argument("--output", default="output.pdf", help="Output PDF path")

    # validate your rcss style file
    validate = subparsers.add_parser("validate", help="Validate RCSS syntax")                                                                                                      
    validate.add_argument("--style", required=True, help="Path to .rcss file to validate") 

    # check the cli version
    subparsers.add_parser("version", help="Show version")

    return parser

def cmd_render(args) -> int:
    """Render a resume for .txt + .rcss to PDF."""

    # TODO - align the 'logging' pattern between all components

    # 1. Parse the RCSS style file into a tree
    print("[1/4] ✓ Parsing RCSS style file")
    raw_rcss = Path(args.style).read_text()
    result = RcssParser().parse(text=raw_rcss, options={"debug": True})
    if not result.valid:
        print(f"[1/4] ✗ Invalid RCSS: {result.message}")
        return 1

    # 2. Transform tree into domain models (layout, sections, declarations)
    print("[2/4] ✓ Transforming parse tree to stylesheet")
    stylesheet = transform(tree=result.tree, options={"debug": True})
   
    # 3. Map raw text sections to their style sheet rules
    print("[3/4] ✓ Mapping CV sections to style rules")
    cv_text = Path(args.input).read_text()
    styled_sections = SectionMapper(options={"debug":True}).map(text=cv_text, stylesheet=stylesheet)
    
    # 4. Render PDF from input .txt using transformed style models
    print("[4/4] ✓ Rendering PDF")
    return 0

def cmd_validate(args) -> int:
    """Validate RCSS syntax and reports errors to stdout"""
    text = Path(args.style).read_text()
    validtion_result = RcssParser().validate(text)

    if validtion_result.valid:
        print("Valid RCSS")
        return 0
    else:
        print(f"Invalid RCSS: {validtion_result.message}")
        return 1

def cmd_version(args) -> int:
    """Print the current version."""
    print("resumeforge 0.1.0")
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    commands = {
        "validate": cmd_validate,
        "version": cmd_version,
        "render": cmd_render
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
  
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
