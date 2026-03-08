#!/usr/bin/env python3
"""
Shared helpers for preferred SVG authority overrides.
"""

from __future__ import annotations

import json
from pathlib import Path


PREFERRED_AUTHORITIES_PATH = Path('src/raster_wrappers/preferred-authorities.json')


def load_preferred_authorities(repo_root: Path) -> dict[str, str]:
    """Load the preferred authority override map if it exists."""
    path = repo_root / PREFERRED_AUTHORITIES_PATH
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def preferred_authority_for(repo_root: Path, relative_png: Path) -> Path | None:
    """Return an override authority path for a PNG when one is recorded."""
    overrides = load_preferred_authorities(repo_root)
    preferred = overrides.get(relative_png.as_posix())
    if not preferred:
        return None
    candidate = repo_root / preferred
    if candidate.exists():
        return candidate
    return None
