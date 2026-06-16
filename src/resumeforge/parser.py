"""Parser for RCSS DSL. Parse or Validate RCSS text"""

# Lark is the parsing library that reads grammar/rcss.lark and builds a parse tree
from lark import Lark
from lark.exceptions import UnexpectedToken, UnexpectedCharacters
from pathlib import Path

from resumeforge.models import ValidationResult, ParseResult

GRAMMAR_PATH = Path(__file__).parent / "grammar" / "rcss.lark"

class RcssParser:
    def __init__(self):
        """Read the grammar and compile it"""
        grammer_text = GRAMMAR_PATH.read_text()
        self._parser = Lark(grammer_text, parser="lalr")

    def validate(self, text: str):
        "Validate a raw string against the rcss grammar."
        try:
            self._parser.parse(text)
            return ValidationResult(valid = True)
        except (UnexpectedToken, UnexpectedCharacters) as e:
            return ValidationResult(
                valid = False,
                message = f"Line {e.line}, Col {e.column}: {e}"
            )
    
    def parse(self, text: str, options: dict | None = None):
        """Parse RCSS text. Validates first, returns ParseResult with tree on success."""
        result = self.validate(text)
        if not result.valid:
            return ParseResult(valid=False, message=result.message)
        tree = self._parser.parse(text)
        if options and options.get("debug") is True:
            # Pretty print the AST when debug mode is enabled
            print(tree.pretty())
        
        return ParseResult(valid=True, tree=tree)
