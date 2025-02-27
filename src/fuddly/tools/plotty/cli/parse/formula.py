
from typing import Optional


def parse_formula(formula: str) -> Optional[tuple[str, str]]:
    parts = formula.split('~')
    if len(parts) != 2:
        return None

    return (parts[0], parts[1])
