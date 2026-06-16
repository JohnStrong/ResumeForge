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