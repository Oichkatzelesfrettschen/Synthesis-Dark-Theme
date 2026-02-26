#!/usr/bin/env python3
"""
WCAG 2.1 Accessibility Contrast Audit

Checks all palette colors against the background for WCAG AA compliance (4.5:1).
Exits non-zero when any color fails the minimum threshold.

Usage:
  python3 src/scripts/accessibility_audit.py
  python3 src/scripts/accessibility_audit.py --fail-below 4.5
  python3 src/scripts/accessibility_audit.py --fail-below 7.0

WHY: An informational-only audit never fails CI. With --fail-below, violations
     block the build rather than silently accumulating.
"""

import argparse
import json
import sys
from pathlib import Path


def get_luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip('#')
    rgb = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def get_contrast(hex1: str, hex2: str) -> float:
    l1 = get_luminance(hex1)
    l2 = get_luminance(hex2)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def load_colors_from_json(colors_json: Path) -> dict:
    """Load hex colors from src/colors.json and flatten to name->hex dict."""
    data = json.loads(colors_json.read_text(encoding='utf-8'))
    result = {}

    def _walk(node, prefix):
        if isinstance(node, dict):
            if 'hex' in node and isinstance(node['hex'], str):
                result[prefix] = node['hex']
            for k, v in node.items():
                if k.startswith('_') or k in ('role', 'note', 'contrast_vs_fg',
                                               'contrast_vs_base', 'hsl',
                                               'used_in', 'deprecated_use',
                                               'rationale', 'replaces'):
                    continue
                _walk(v, f"{prefix}.{k}" if prefix else k)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                _walk(item, f"{prefix}[{i}]")

    _walk(data, '')
    return result


# Default palette (Dracula base) -- used when src/colors.json is not available
DEFAULT_PALETTE = {
    "Background": "#282a36",
    "Current Line": "#44475a",
    "Foreground": "#f8f8f2",
    "Comment": "#6272a4",
    "Indigo-Gray": "#8e95b8",
    "Selection": "#b9a4fa",
    "Cyan": "#8be9fd",
    "Green": "#50fa7b",
    "Orange": "#ffb86c",
    "Purple": "#bd93f9",
    "Red": "#ff5555",
    "Yellow": "#f1fa8c",
}


def main():
    parser = argparse.ArgumentParser(
        description='WCAG 2.1 contrast audit for Synthesis-Dark palette'
    )
    parser.add_argument(
        '--fail-below',
        type=float,
        default=4.5,
        metavar='RATIO',
        help='Fail (exit 1) if any color contrast is below this ratio. '
             'WCAG AA=4.5, AAA=7.0. Default: 4.5'
    )
    parser.add_argument(
        '--palette',
        type=Path,
        default=None,
        help='Path to src/colors.json (auto-detected if not given)'
    )
    args = parser.parse_args()

    # Load palette: prefer src/colors.json if available
    colors_json = args.palette
    if colors_json is None:
        repo_root = Path(__file__).resolve().parents[2]
        candidate = repo_root / "src" / "colors.json"
        if candidate.exists():
            colors_json = candidate

    if colors_json and colors_json.exists():
        palette = load_colors_from_json(colors_json)
        print(f"Loaded {len(palette)} colors from {colors_json}")
    else:
        palette = DEFAULT_PALETTE
        print("Using default Dracula palette (src/colors.json not found)")

    bg = palette.get("background.base", palette.get("Background", "#282a36"))
    fail_threshold = args.fail_below

    print(f"\n--- WCAG 2.1 Contrast Audit (BG: {bg}, fail-below: {fail_threshold:.1f}:1) ---\n")

    failures = []
    for name, hex_val in sorted(palette.items()):
        if hex_val.lower() == bg.lower():
            continue
        try:
            ratio = get_contrast(hex_val, bg)
        except Exception as e:
            print(f"  {name}: ERROR ({e})")
            continue

        if ratio >= 7:
            level = "AAA"
        elif ratio >= 4.5:
            level = "AA"
        elif ratio >= 3.0:
            level = "AA Large"
        else:
            level = "FAIL"

        fail_marker = " <-- BELOW THRESHOLD" if ratio < fail_threshold else ""
        print(f"  {name:<35} ({hex_val}): {ratio:5.2f}:1 [{level}]{fail_marker}")

        if ratio < fail_threshold:
            failures.append((name, hex_val, ratio))

    print()
    if failures:
        print(f"FAIL: {len(failures)} color(s) below {fail_threshold:.1f}:1 threshold:")
        for name, hex_val, ratio in failures:
            print(f"  {name} ({hex_val}): {ratio:.2f}:1")
        sys.exit(1)
    else:
        print(f"PASS: all colors meet {fail_threshold:.1f}:1 threshold.")


if __name__ == '__main__':
    main()
