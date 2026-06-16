"""Transforms a Lark parse tree into domain models (Stylesheet)."""

from lark import Transformer, Token, Tree
from resumeforge.models import Declaration, LayoutRule, SectionRule, Stylesheet


class RcssTransformer(Transformer):
    """Walks the parse tree bottom-up, converting nodes into domain models."""

    def __init__(self, options: dict | None = None):
        super().__init__()
        self._debug = options.get("debug") is True if options else False

    def _log(self, rule_name: str, items):
        if self._debug:
            print(f"[{rule_name}] {items}")

    def value(self, items):
        self._log("value", items)
        pass

    def declaration(self, items):
        self._log("declaration", items)
        pass

    def layout_selector(self, items):
        self._log("layout_selector", items)
        pass

    def section_selector(self, items):
        self._log("section_selector", items)
        pass

    def rule(self, items):
        self._log("rule", items)
        pass

    def start(self, items):
        self._log("start", items)
        pass


def transform(tree: Tree, options: dict | None = None) -> Stylesheet:
    """Entry point: transform a Lark tree into a Stylesheet domain model."""
    return RcssTransformer(options).transform(tree)
