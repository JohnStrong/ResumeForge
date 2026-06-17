from dataclasses import dataclass

from lark import Tree

@dataclass
class ValidationResult:
    """A validation result used by parser.py. 
    
    Encapsulates the status of lark prasing of a provided RCSS text with optional user friendly message to display
    """
    valid: bool
    message: str | None = None

@dataclass
class ParseResult:
    """Result of parsing RCSS text.
    
    valid: whether the RCSS is syntactically correct
    message: error description if valid is False
    tree: the Lark parse tree if valid is True, None otherwise
    """
    valid: bool
    message: str | None = None
    tree: Tree | None = None

@dataclass
class Declaration:
    """A single property: value pair like 'padding: 8mm'"""
    property: str
    values: list[str]  # list because margins has 4 values: 20mm 18mm 20mm 18mm
  
@dataclass
class LayoutRule:
    """The layout { ... } block — page-level settings"""
    declarations: list[Declaration]
    # Convenience: pull out mode, columns, margins etc. later via helper methods
  
@dataclass
class SectionRule:
    """A section[name="..."] { ... } block — per-section styles"""
    name: str  # the heading text, e.g. "HEADER", "WORK EXPERIENCE"
    declarations: list[Declaration]
  
@dataclass
class Stylesheet:
    """The complete parsed .rcss file as domain objects"""
    layout: LayoutRule # required — every .rcss must have a layout block
    sections: list[SectionRule]

@dataclass
class StyledSection:
    """Encapsulated str content with its section rule from a Stylesheet"""
    name: str
    content: str
    rule: SectionRule
