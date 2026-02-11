import re
from typing import List, Pattern

import bpy


def find_materials_by_regex(pattern: str, *, flags: int = 0, use_fullmatch: bool = False) -> List[bpy.types.Material]:
    """
    Return all bpy.data.materials whose names match a regex.

    Args:
        pattern: Regex pattern as a string.
        flags: re flags, e.g. re.IGNORECASE | re.MULTILINE
        use_fullmatch: If True, uses fullmatch() (entire name must match).
                       If False, uses search() (pattern can match anywhere).

    Returns:
        List of bpy.types.Material that match.
    """
    try:
        rx: Pattern[str] = re.compile(pattern, flags)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {pattern!r}. re.error: {e}") from e

    matches: List[bpy.types.Material] = []
    for mat in bpy.data.materials:
        name = mat.name or ""
        ok = rx.fullmatch(name) is not None if use_fullmatch else rx.search(name) is not None
        if ok:
            matches.append(mat)

    return matches
