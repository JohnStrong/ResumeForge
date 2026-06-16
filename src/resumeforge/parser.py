# Lark is the parsing library that reads grammar/rcss.lark and builds a parse tree
from lark import Lark
from pathlib import Path

GRAMMAR_PATH = Path(__file__).parent / "grammar" / "rcss.lark"

class RcssParser:
    def __init__(self):
        """Read the grammar and compile it"""
        grammer_text = GRAMMAR_PATH.read_text()
        self._parser = Lark(grammer_text, parser="lalr")
    
    def parse(self, text: str):
        """Parse a raw string using the rcss grammer"""
        tree = self._parser.parse(text)
        return tree
