from dataclasses import dataclass

@dataclass
class ValidationResult:
    """A validation result used by parser.py. 
    
    Encapsulates the status of lark prasing of a provided RCSS text with optional user friendly message to display
    """
    valid: bool
    message: str | None = None