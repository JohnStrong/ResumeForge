"""ResumeForge CLI entry point."""

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resumeforge",
        description="Convert plain-text CVs into styled A4 PDFs using RCSS.",
    )
    subparsers = parser.add_subparsers(dest="command")

    render = subparsers.add_parser("render", help="Render a resume to PDF")
    render.add_argument("--input", required=True, help="Path to input .txt file")
    render.add_argument("--style", required=True, help="Path to .rcss style file")
    render.add_argument("--output", default="output.pdf", help="Output PDF path")

    subparsers.add_parser("version", help="Show version")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "render":
        print(f"Rendering {args.input} with style {args.style} -> {args.output}")
        return 0

    if args.command == "version":
        print("resumeforge 0.1.0")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
