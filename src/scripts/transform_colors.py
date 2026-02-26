#!/usr/bin/env python3
"""
Synthesis-Dark Color Transformer
Applies COLOR-STRATEGY.md v2.0.0 semantic color mapping to theme assets.

Modes:
  --repo-scan   Process all asset directories in the repository (default when
                no positional argument given and running from within the repo).
  <icon_dir>    Process a single directory (icon-only mode).

Design Philosophy:
- Hue families stay together (blue->indigo, green->teal, etc.)
- Luminance hierarchy for colorblind safety
- Saturated vs desaturated colors handled differently
- Folder colors shift to indigo-gray, not teal
"""

import os
import re
import sys
import colorsys
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Tuple, Optional

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: PIL not available. PNG processing disabled.", file=sys.stderr)

# =============================================================================
# REPO SCAN TARGETS
# Directories processed in --repo-scan mode (relative to repo root)
# =============================================================================
REPO_SCAN_TARGETS = [
    'icons',
    'metacity-1',
    'gtk-2.0',
    'gtk-3.0',
    'gtk-3.20',
    'gtk-4.0',
    'xfwm4',
    'cinnamon',
]

# =============================================================================
# COLOR MAPPING TABLES (from COLOR-STRATEGY.md v2.0.0)
# =============================================================================

TARGETS = {
    'indigo_primary': (180, 190, 254),    # #b4befe - lavender, primary accent
    'indigo_dark': (69, 71, 90),          # #45475a - bg-selection, muted
    'indigo_medium': (127, 132, 156),     # #7f849c - overlay
    'sky_blue': (137, 180, 250),          # #89b4fa - sky blue
    'surface': (49, 50, 68),              # #313244 - surface

    'teal_dark': (13, 110, 67),           # #0d6e43 - dark teal
    'teal_primary': (23, 177, 105),       # #17b169 - CachyOS teal
    'teal_soft': (166, 227, 161),         # #a6e3a1 - soft green
    'teal_variant': (64, 160, 126),       # #40a07e - teal variant

    'peach': (250, 179, 135),             # #fab387 - peach
    'yellow': (249, 226, 175),            # #f9e2af - yellow
    'peach_muted': (224, 122, 78),        # #e07a4e - muted peach
    'brown_muted': (161, 128, 114),       # #a18072 - muted brown

    'red_soft': (229, 101, 122),          # #e5657a - soft crimson
    'red_primary': (243, 139, 168),       # #f38ba8 - Catppuccin red
    'red_muted': (197, 74, 92),           # #c54a5c - muted red

    'mauve_dark': (89, 78, 117),          # #594e75 - dark mauve
    'mauve': (203, 166, 247),             # #cba6f7 - lavender/mauve

    'folder_slate': (142, 149, 184),      # #8e95b8 - slate/indigo gray
    'folder_gray': (127, 132, 156),       # #7f849c - gray-violet
    'folder_muted': (108, 112, 134),      # #6c7086 - muted slate
}


# =============================================================================
# COLOR MATH
# =============================================================================

def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to HSL (H: 0-360, S: 0-1, L: 0-1)."""
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return h * 360, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convert HSL (H: 0-360, S: 0-1, L: 0-1) to RGB (0-255)."""
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def get_hue_family(hue: float) -> str:
    """Determine which hue family a color belongs to (0-360 scale)."""
    hue = hue % 360
    if hue <= 20 or hue >= 340:
        return 'red'
    elif 20 < hue <= 45:
        return 'orange'
    elif 45 < hue <= 80:
        return 'yellow'
    elif 80 < hue <= 150:
        return 'green'
    elif 150 < hue <= 200:
        return 'cyan'
    elif 200 < hue <= 260:
        return 'blue'
    elif 260 < hue <= 300:
        return 'purple'
    else:
        return 'magenta'


def is_folder_color(r: int, g: int, b: int) -> bool:
    """
    Detect if this is a MATE folder color (ultra-desaturated yellow-green).
    MATE folders are typically around H:65, S:0.15, pale olive/khaki tones.
    """
    h, s, l = rgb_to_hsl(r, g, b)
    return 40 <= h <= 90 and s < 0.3 and l > 0.6


def transform_color(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """
    Transform a color according to COLOR-STRATEGY.md v2.0.0 rules.
    Returns the transformed RGB tuple.
    """
    # Preserve near-black and near-white (outlines, shadows, highlights)
    if r < 20 and g < 20 and b < 20:
        return (r, g, b)
    if r > 235 and g > 235 and b > 235:
        return (r, g, b)

    h, s, l = rgb_to_hsl(r, g, b)

    # Folder colors (desaturated yellow-green) -> indigo-gray
    if is_folder_color(r, g, b):
        new_h = 228  # Indigo hue; target #8e95b8
        new_s = max(0.15, min(0.25, s + 0.05))
        new_l = max(0.45, min(0.60, l * 0.75))
        return hsl_to_rgb(new_h, new_s, new_l)

    # Desaturated colors -> shift toward indigo
    if s < 0.3:
        new_h = 240
        new_s = max(0.15, min(0.25, s + 0.10))
        new_l = max(0.45, min(0.60, l * 0.80))
        return hsl_to_rgb(new_h, new_s, new_l)

    # Saturated colors: map by hue family
    family = get_hue_family(h)

    if family == 'blue':
        new_h = max(235, min(260, 240 + (h - 230) * 0.5))
        new_s = min(1.0, s * 1.15)
        new_l = max(0.35, min(0.75, l))

    elif family == 'green':
        new_h = max(150, min(170, 155 + (h - 120) * 0.3))
        new_s = min(1.0, s * 1.10)
        new_l = max(0.30, min(0.65, l))

    elif family == 'cyan':
        new_h = max(170, min(195, 175 + (h - 175) * 0.8))
        new_s = min(1.0, s * 1.05)
        new_l = max(0.35, min(0.70, l))

    elif family == 'yellow':
        new_h = max(40, min(55, 45 + (h - 62) * 0.5))
        new_s = min(1.0, s * 1.10)
        new_l = max(0.55, min(0.80, l))

    elif family == 'orange':
        new_h = max(20, min(35, 25 + (h - 32) * 0.8))
        new_s = min(1.0, s * 1.05)
        new_l = max(0.45, min(0.75, l))

    elif family == 'red':
        if h > 340:
            new_h = max(350, 350 + (h - 350) * 0.5)
        else:
            new_h = min(15, 5 + (h - 10) * 0.5)
        new_s = min(0.85, s * 0.95)
        new_l = max(0.45, min(0.65, l))

    elif family == 'purple':
        new_h = max(265, min(285, 270 + (h - 280) * 0.6))
        new_s = min(1.0, s * 1.10)
        new_l = max(0.40, min(0.70, l))

    elif family == 'magenta':
        new_h = max(300, min(330, 310 + (h - 320) * 0.7))
        new_s = min(0.90, s * 0.95)
        new_l = max(0.50, min(0.75, l))

    else:
        new_h, new_s, new_l = h, s, l

    return hsl_to_rgb(new_h, new_s, new_l)


# =============================================================================
# PNG PROCESSING
# =============================================================================

def process_png(filepath: Path) -> Tuple[str, bool, str]:
    """
    Process a single PNG file, transforming colors.
    Returns (filepath_str, success, message).
    """
    if not HAS_PIL:
        return (str(filepath), False, "PIL not available")

    try:
        img = Image.open(filepath)

        if img.mode == 'P':
            img = img.convert('RGBA')
        elif img.mode == 'L':
            return (str(filepath), True, "skipped (grayscale)")
        elif img.mode == '1':
            return (str(filepath), True, "skipped (1-bit)")
        elif img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')

        has_alpha = img.mode == 'RGBA'
        pixels = img.load()
        width, height = img.size
        modified = False

        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                if has_alpha:
                    r, g, b, a = pixel
                    if a == 0:
                        continue
                else:
                    r, g, b = pixel
                    a = 255

                new_r, new_g, new_b = transform_color(r, g, b)

                if (new_r, new_g, new_b) != (r, g, b):
                    modified = True
                    if has_alpha:
                        pixels[x, y] = (new_r, new_g, new_b, a)
                    else:
                        pixels[x, y] = (new_r, new_g, new_b)

        if modified:
            img.save(filepath)
            return (str(filepath), True, "transformed")
        else:
            return (str(filepath), True, "unchanged")

    except Exception as e:
        return (str(filepath), False, str(e))


# =============================================================================
# SVG PROCESSING
# =============================================================================

def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.strip().lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return None
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color string."""
    return f"#{r:02x}{g:02x}{b:02x}"


SVG_HEX_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*[:=]\s*["\']?(#[0-9a-fA-F]{3,6})["\']?',
    re.IGNORECASE
)
SVG_RGB_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*[:=]\s*["\']?rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)["\']?',
    re.IGNORECASE
)
SVG_STYLE_HEX_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*:\s*(#[0-9a-fA-F]{3,6})',
    re.IGNORECASE
)
SVG_STYLE_RGB_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*:\s*rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
    re.IGNORECASE
)


def _make_hex_replacer():
    def replacer(match):
        attr = match.group(1)
        hex_color = match.group(2)
        rgb = hex_to_rgb(hex_color)
        if rgb is None:
            return match.group(0)
        new_rgb = transform_color(*rgb)
        new_hex = rgb_to_hex(*new_rgb)
        original = match.group(0)
        if '="' in original or "='" in original:
            return f'{attr}="{new_hex}"'
        return f'{attr}:{new_hex}'
    return replacer


def _make_rgb_replacer():
    def replacer(match):
        attr = match.group(1)
        r, g, b = int(match.group(2)), int(match.group(3)), int(match.group(4))
        new_r, new_g, new_b = transform_color(r, g, b)
        original = match.group(0)
        if '="' in original or "='" in original:
            return f'{attr}="rgb({new_r},{new_g},{new_b})"'
        return f'{attr}:rgb({new_r},{new_g},{new_b})'
    return replacer


def process_svg(filepath: Path) -> Tuple[str, bool, str]:
    """
    Process a single SVG file, transforming colors.
    Returns (filepath_str, success, message).
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        original_content = content
        content = SVG_HEX_PATTERN.sub(_make_hex_replacer(), content)
        content = SVG_RGB_PATTERN.sub(_make_rgb_replacer(), content)
        content = SVG_STYLE_HEX_PATTERN.sub(
            lambda m: f'{m.group(1)}:{rgb_to_hex(*transform_color(*hex_to_rgb(m.group(2)) or (0,0,0)))}',
            content
        )
        content = SVG_STYLE_RGB_PATTERN.sub(
            lambda m: f'{m.group(1)}:rgb({",".join(str(v) for v in transform_color(int(m.group(2)), int(m.group(3)), int(m.group(4))))})',
            content
        )

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return (str(filepath), True, "transformed")
        return (str(filepath), True, "unchanged")

    except Exception as e:
        return (str(filepath), False, str(e))


# =============================================================================
# FILE DISCOVERY
# =============================================================================

def collect_files(directories: list) -> Tuple[list, list]:
    """
    Collect all PNG and SVG files from a list of directories.
    Skips cursor sub-directories (binary cursor format).
    """
    pngs = []
    svgs = []
    for directory in directories:
        directory = Path(directory)
        if not directory.exists():
            continue
        for root, dirs, files in os.walk(directory):
            if 'cursors' in root:
                continue
            for filename in files:
                filepath = Path(root) / filename
                if filename.lower().endswith('.png'):
                    pngs.append(filepath)
                elif filename.lower().endswith('.svg'):
                    svgs.append(filepath)
    return pngs, svgs


# =============================================================================
# PROCESSING PIPELINE
# =============================================================================

def run_pipeline(pngs: list, svgs: list, workers: int, verbose: bool, dry_run: bool):
    """Run the full color-transform pipeline on collected files."""
    if dry_run:
        print(f"[DRY RUN] Would process {len(pngs)} PNG and {len(svgs)} SVG files.")
        return

    # SVG (single-threaded -- fast and avoids GIL issues with regex)
    print(f"Processing {len(svgs)} SVG files...")
    svg_transformed = svg_unchanged = svg_errors = 0
    for i, svg_path in enumerate(svgs, 1):
        filepath, success, message = process_svg(svg_path)
        if verbose:
            print(f"  [{i}/{len(svgs)}] {filepath}: {message}")
        if success:
            svg_transformed += (message == "transformed")
            svg_unchanged += (message != "transformed")
        else:
            svg_errors += 1
            if not verbose:
                print(f"  ERROR: {filepath}: {message}", file=sys.stderr)
    print(f"SVG: {svg_transformed} transformed, {svg_unchanged} unchanged, {svg_errors} errors")

    # PNG (parallel)
    if HAS_PIL and pngs:
        print(f"Processing {len(pngs)} PNG files with {workers} workers...")
        png_transformed = png_unchanged = png_errors = 0
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_png, p): p for p in pngs}
            for i, future in enumerate(as_completed(futures), 1):
                filepath, success, message = future.result()
                if verbose:
                    print(f"  [{i}/{len(pngs)}] {filepath}: {message}")
                elif i % 100 == 0:
                    print(f"  Processed {i}/{len(pngs)} PNG files...")
                if success:
                    png_transformed += (message == "transformed")
                    png_unchanged += (message != "transformed")
                else:
                    png_errors += 1
                    if not verbose:
                        print(f"  ERROR: {filepath}: {message}", file=sys.stderr)
        print(f"PNG: {png_transformed} transformed, {png_unchanged} unchanged, {png_errors} errors")
    elif not HAS_PIL:
        print("Skipping PNG processing (PIL not available). Install: pip install Pillow")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Transform theme asset colors to Synthesis Dark palette'
    )
    parser.add_argument(
        'icon_dir',
        nargs='?',
        help='Path to a single directory to process. Omit to use --repo-scan mode.'
    )
    parser.add_argument(
        '--repo-scan',
        action='store_true',
        default=False,
        help='Scan all asset directories in the repository (icons, gtk-*, xfwm4, etc.)'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='Number of parallel PNG workers (default: 4)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show per-file progress'
    )

    args = parser.parse_args()

    # Determine what to process
    if args.icon_dir:
        # Single directory mode
        target_dirs = [Path(args.icon_dir)]
        if not target_dirs[0].exists():
            print(f"ERROR: Directory not found: {args.icon_dir}", file=sys.stderr)
            sys.exit(1)
        print(f"Processing single directory: {target_dirs[0]}")
    else:
        # Repo-scan mode: resolve repo root from script location
        repo_root = Path(__file__).resolve().parents[2]
        target_dirs = [repo_root / t for t in REPO_SCAN_TARGETS]
        print(f"Repo-scan mode: {repo_root}")
        print(f"Targets: {', '.join(REPO_SCAN_TARGETS)}")

    pngs, svgs = collect_files(target_dirs)
    print(f"Found {len(pngs)} PNG and {len(svgs)} SVG files.")

    run_pipeline(pngs, svgs, args.workers, args.verbose, args.dry_run)
    print("Done.")


if __name__ == '__main__':
    main()
