"""
CSS validation tests.

Checks all gtk.css and gtk-dark.css files for obvious syntax errors:
- Balanced braces
- No unclosed comments
- No null bytes
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent
CSS_GLOBS = [
    "gtk-3.0/**/*.css",
    "gtk-3.20/**/*.css",
    "gtk-4.0/**/*.css",
    "gnome-shell/**/*.css",
    "cinnamon/**/*.css",
]


def collect_css_files():
    files = []
    for pattern in CSS_GLOBS:
        files.extend(REPO_ROOT.glob(pattern))
    return [f for f in files if f.is_file()]


CSS_FILES = collect_css_files()


@pytest.mark.parametrize("css_file", CSS_FILES, ids=lambda f: str(f.relative_to(REPO_ROOT)))
def test_css_no_null_bytes(css_file):
    content = css_file.read_bytes()
    assert b'\x00' not in content, f"Null bytes found in {css_file}"


@pytest.mark.parametrize("css_file", CSS_FILES, ids=lambda f: str(f.relative_to(REPO_ROOT)))
def test_css_balanced_braces(css_file):
    text = css_file.read_text(encoding='utf-8', errors='replace')
    # Strip string literals to avoid counting braces inside them
    inside_comment = False
    depth = 0
    i = 0
    while i < len(text):
        if not inside_comment and text[i:i+2] == '/*':
            inside_comment = True
            i += 2
            continue
        if inside_comment and text[i:i+2] == '*/':
            inside_comment = False
            i += 2
            continue
        if not inside_comment:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
        i += 1
    assert depth == 0, f"Unbalanced braces (depth={depth}) in {css_file}"


@pytest.mark.parametrize("css_file", CSS_FILES, ids=lambda f: str(f.relative_to(REPO_ROOT)))
def test_css_no_unclosed_comments(css_file):
    text = css_file.read_text(encoding='utf-8', errors='replace')
    opens = text.count('/*')
    closes = text.count('*/')
    assert opens == closes, (
        f"Unclosed comment in {css_file}: {opens} opens vs {closes} closes"
    )
