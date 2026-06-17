"""Shared validation runner for declarative rule lists."""

def run_validators(validators: list[dict], *args):
    """Run a list of validation rules. Raises ValueError on first failure.

    Each validator is a dict with:
      - check: callable that receives *args and returns True/False
      - message: error string to surface if check fails
    """
    for rule in validators:
        if not rule["check"](*args):
            raise ValueError(rule["message"])
