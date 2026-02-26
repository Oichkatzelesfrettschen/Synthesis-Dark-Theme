"""
SVG well-formedness tests.

XML-parses all .svg files in the repository to detect malformed documents.
Skips binary (cursor) directories.
"""

from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

REPO_ROOT = Path(__file__).parent.parent

# Directories containing SVG files to validate
SVG_DIRS = [
    "gtk-2.0",
    "gtk-3.0",
    "gtk-3.20",
    "gtk-4.0",
    "gnome-shell",
    "cinnamon",
    "metacity-1",
    "xfwm4",
    "src/assets",
]


def collect_svg_files():
    files = []
    for directory in SVG_DIRS:
        dir_path = REPO_ROOT / directory
        if dir_path.exists():
            for svg in dir_path.rglob("*.svg"):
                # Skip cursor directories (not standard SVG)
                if 'cursor' in str(svg).lower():
                    continue
                files.append(svg)
    return files


SVG_FILES = collect_svg_files()


@pytest.mark.parametrize("svg_file", SVG_FILES, ids=lambda f: str(f.relative_to(REPO_ROOT)))
def test_svg_well_formed(svg_file):
    """Each SVG must be parseable as XML."""
    try:
        ET.parse(svg_file)
    except ET.ParseError as e:
        pytest.fail(f"Malformed SVG {svg_file}: {e}")


@pytest.mark.parametrize("svg_file", SVG_FILES, ids=lambda f: str(f.relative_to(REPO_ROOT)))
def test_svg_no_null_bytes(svg_file):
    content = svg_file.read_bytes()
    assert b'\x00' not in content, f"Null bytes found in {svg_file}"
