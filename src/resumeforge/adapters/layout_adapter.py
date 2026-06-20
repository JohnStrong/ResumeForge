from dataclasses import dataclass
from typing import Any, Callable
from resumeforge.models import LayoutRule, Declaration

@dataclass
class LayoutConfig:
    """renderer friendly layout configs from Layout Stylesheet (rcss)"""
    mode: str
    columns: int
    column_widths: list[int]
    column_gap: float
    margins: tuple[float, float, float, float]
    font_family: str | None = None

_DECLARATION_ADAPTERS: dict[str, Callable[[Declaration], Any]] = {
    "mode": lambda d: d.values[0],
    "columns": lambda d: int(d.values[0]),
    "column-widths": lambda d: [int(v.rstrip("%")) for v in d.values],
    "column-gap": lambda d: float(d.values[0].rstrip("mm")),
    "margins": lambda d: tuple(float(v.rstrip("mm")) for v in d.values),
    "font-family": lambda d: d.values[0].strip('"'),
}

def adapt_layout(layout: LayoutRule) -> LayoutConfig:
    props = {}
    for decl in layout.declarations:
        decl_adatper = _DECLARATION_ADAPTERS.get(decl.property)
        if decl_adatper:
            key = decl.property.replace("-", "_")
            props[key] = decl_adatper(decl)
        else:
            raise ValueError(f"layout property '{decl.property}' is not valid")
    return LayoutConfig(**props)
