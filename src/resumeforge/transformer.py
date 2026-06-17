"""Transforms a Lark parse tree into domain models (Stylesheet)."""

from lark import Transformer, Token, Tree
from resumeforge.models import Declaration, LayoutRule, SectionRule, Stylesheet

STYLESHEET_RULE_VALIDATORS = [
    {
        "check": lambda layout, _: layout is not None,
        "message": "RCSS must contain a layout { ... } rule",
    },
   {
        "check": lambda _, sections: len(sections) > 0,
        "message": "RCSS must contain at least one section[name=\"...\"] rule",
    },
]

class RcssTransformer(Transformer):
    """Walks the parse tree bottom-up, converting nodes into domain models."""

    def __init__(self, options: dict | None = None):
        super().__init__()
        self._debug = options.get("debug") is True if options else False

    def _log(self, rule_name: str, items):
        if self._debug:
            print(f"[{rule_name}] {items}")

    def _validate_stylesheet(self, layout: LayoutRule | None, sections: list[SectionRule]):
        for validator in STYLESHEET_RULE_VALIDATORS:
            if not validator['check'](layout, sections):
                raise ValueError(validator['message'])

    def value(self, items) -> list[str]:
        """Extract values from TOKEN array. 

        e.g. Token('VALUE', '8mm') → str(token) → "8mm"
        """
        self._log("value", items)
        return [str(token) for token in items]

    def declaration(self, items) -> Declaration:
        """Extract property and values[] from TOKEN.
        
        e.g. Token('PROPERTY', 'padding'), ['8mm'] -> Declaration('padding', ['8mm'])
        """
        self._log("declaration", items)
        return Declaration(property=str(items[0]), values=items[1])

    def layout_selector(self, items) -> str:
        """layout is a dsl selector it doesn't have any tokens"""
        self._log("layout_selector", items)
        return "layout"

    def section_selector(self, items) -> str:
        """Extract the section name, stripping quotes from the STRING token.

        e.g. Token('STRING', '"HEADER"') → "HEADER"
        """
        self._log("section_selector", items)
        return str(items[0]).strip('"')

    def rule(self, items) -> LayoutRule | SectionRule:
        """Map a selector + declarations into a LayoutRule or SectionRule.

        items[0] is the selector return value ("layout" or a section name).
        items[1:] are Declaration objects from each declaration in the block.
        """
        self._log("rule", items)
        selector = items[0]
        declarations = items[1:]
        if selector == "layout":
            return LayoutRule(declarations=declarations)
        return SectionRule(name=selector, declarations=declarations)

    def start(self, items) -> Stylesheet:
        """Map the rules to layout and section[] Stylesheet.
        
        e.g.
        [
            LayoutRule(
                declarations=Declaration(property='mode', values=['grid'])
            ), 
            SectionRule(name='"HEADER"', 
                declarations=Declaration(property='grid-column', values=['1'])
            )
        ] -> StyleSheet(LayoutRule, SectionRule[])
        """
        self._log("start", items)
        layout = None
        sections = []
        for rule in items:
            if isinstance(rule, LayoutRule):
                layout = rule
            else:
                sections.append(rule)
        
        self._validate_stylesheet(layout, sections)
        return Stylesheet(layout=layout, sections=sections)


def transform(tree: Tree, options: dict | None = None) -> Stylesheet:
    """Entry point: transform a Lark tree into a Stylesheet domain model."""
    return RcssTransformer(options).transform(tree)
