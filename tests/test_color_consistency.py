"""
Color consistency tests.

Verifies that all named hex colors in SCSS _colors.scss files have a
corresponding entry in src/colors.json. This catches colors added to SCSS
without being recorded in the canonical palette.
"""

import json
import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent
COLORS_JSON = REPO_ROOT / "src" / "colors.json"

SCSS_COLOR_FILES = [
    "gtk-3.20/_colors.scss",
    "gtk-4.0/_colors.scss",
    "gnome-shell/_colors.scss",
    "cinnamon/_colors.scss",
]

HEX_PATTERN = re.compile(r'#([0-9a-fA-F]{3,6})\b')

# Colors that are intentionally not in the canonical palette.
# These include upstream Cinnamon/GNOME colors that we inherit without modifying,
# computed helpers (near-black, near-white), and legacy colors with no semantic role.
EXEMPT_COLORS = {
    # Near-blacks / near-whites used for contrast math
    '#000', '#fff', '#000000', '#ffffff', '#fefefe', '#f8f8f8',
    '#14171a', '#191a22',
    # Upstream Cinnamon inherited colors (not our design choices)
    '#50fa7a',   # Cinnamon lime (minor variant of #50fa7b)
    '#13b1d5',   # Cinnamon blue link
    '#4dadd4',   # Cinnamon suggested-action
    '#73d216',   # Cinnamon success (upstream)
    '#f27835',   # Cinnamon warning
    '#fc4138',   # Cinnamon error
    '#f04a50',   # Cinnamon destructive
    '#f08437',   # Cinnamon drop-target
    '#f46067',   # Cinnamon WM close light
    '#cc575d',   # Cinnamon WM close dark
    '#d7787d',   # Cinnamon WM close hover dark
    '#f68086',   # Cinnamon WM close hover light
    '#f13039',   # Cinnamon WM close active light
    '#be3841',   # Cinnamon WM close active dark
    '#454c5c',   # Cinnamon WM button hover dark
    '#262932',   # Cinnamon WM button hover border dark
    '#d1d3da',   # Cinnamon WM button hover border light
    '#90949e',   # Cinnamon WM icon light
    '#90939b',   # Cinnamon WM icon dark
    '#b6b8c0',   # Cinnamon WM icon unfocused light
    '#666a74',   # Cinnamon WM icon unfocused dark
    '#7a7f8b',   # Cinnamon WM icon hover light
    '#c4c7cc',   # Cinnamon WM icon hover dark
    '#2f343f',   # Cinnamon WM close icon dark
    '#f8f8f9',   # Cinnamon WM close icon light
    '#bac3cf',   # Cinnamon dark sidebar fg
    '#d3dae3',   # Cinnamon header fg (darker variant)
    '#cfd6e6',   # Cinnamon entry border light
    '#fdfdfd',   # Cinnamon button bg light
}


def load_canonical_hex_values():
    """Extract all hex values from src/colors.json."""
    if not COLORS_JSON.exists():
        return set()
    data = json.loads(COLORS_JSON.read_text(encoding='utf-8'))
    hexes = set()

    def _walk(node):
        if isinstance(node, dict):
            if 'hex' in node and isinstance(node['hex'], str):
                hexes.add(node['hex'].lower())
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)
    return hexes


CANONICAL_HEXES = load_canonical_hex_values()


def test_colors_json_exists():
    assert COLORS_JSON.exists(), "src/colors.json must exist"


def test_colors_json_valid():
    data = json.loads(COLORS_JSON.read_text(encoding='utf-8'))
    assert isinstance(data, dict), "src/colors.json must be a JSON object"


@pytest.mark.parametrize("scss_path", SCSS_COLOR_FILES)
def test_scss_colors_in_canonical_palette(scss_path):
    """All non-exempt hex colors in SCSS must appear in src/colors.json."""
    if not CANONICAL_HEXES:
        pytest.skip("src/colors.json not loaded (empty)")

    full_path = REPO_ROOT / scss_path
    if not full_path.exists():
        pytest.skip(f"{scss_path} not found")

    text = full_path.read_text(encoding='utf-8')
    found_hexes = {f"#{m.lower()}" for m in HEX_PATTERN.findall(text)}

    # Normalize 3-char hex to 6-char for comparison
    def normalize(h):
        h = h.lower()
        if len(h) == 4:  # #rgb
            return '#' + ''.join(c * 2 for c in h[1:])
        return h

    missing = set()
    for h in found_hexes:
        norm = normalize(h)
        if norm in EXEMPT_COLORS or h in EXEMPT_COLORS:
            continue
        if norm not in CANONICAL_HEXES and h not in CANONICAL_HEXES:
            missing.add(h)

    assert not missing, (
        f"Colors in {scss_path} not in src/colors.json:\n"
        + "\n".join(f"  {h}" for h in sorted(missing))
        + "\nAdd them to src/colors.json or to EXEMPT_COLORS in this test."
    )
