#!/usr/bin/env python3
"""
MATE-Synthesis-Dark Icon Color Transformer
Applies COLOR-STRATEGY.md v2.0.0 semantic color mapping to MATE icons.

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
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Tuple, Optional

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: PIL not available. PNG processing disabled.")

# =============================================================================
# COLOR MAPPING TABLES (from COLOR-STRATEGY.md v2.0.0)
# =============================================================================

# Target colors from Synthesis Dark palette
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


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to HSL (H: 0-360, S: 0-1, L: 0-1)."""
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    return h * 360, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convert HSL (H: 0-360, S: 0-1, L: 0-1) to RGB (0-255)."""
    h_norm = h / 360.0
    r, g, b = colorsys.hls_to_rgb(h_norm, l, s)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def get_hue_family(hue: float) -> str:
    """Determine which hue family a color belongs to (0-360 scale)."""
    # Normalize hue to 0-360
    hue = hue % 360

    # Red: 0-20 and 340-360
    if hue <= 20 or hue >= 340:
        return 'red'
    # Orange: 20-45
    elif 20 < hue <= 45:
        return 'orange'
    # Yellow: 45-80
    elif 45 < hue <= 80:
        return 'yellow'
    # Green: 80-150
    elif 80 < hue <= 150:
        return 'green'
    # Cyan: 150-200
    elif 150 < hue <= 200:
        return 'cyan'
    # Blue: 200-260
    elif 200 < hue <= 260:
        return 'blue'
    # Purple: 260-300
    elif 260 < hue <= 300:
        return 'purple'
    # Magenta/Pink: 300-340
    else:
        return 'magenta'


def is_folder_color(r: int, g: int, b: int) -> bool:
    """
    Detect if this is a MATE folder color (ultra-desaturated yellow-green).
    MATE folders are typically around H:65, S:0.15, pale olive/khaki tones.
    """
    h, s, l = rgb_to_hsl(r, g, b)
    # Folder colors: hue 40-90 (yellow-green), low saturation, high luminance
    return (40 <= h <= 90 and s < 0.3 and l > 0.6)


def transform_color(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """
    Transform a color according to COLOR-STRATEGY.md v2.0.0 rules.
    Returns the transformed RGB tuple.
    """
    # Skip near-black and near-white (preserve outlines, shadows, highlights)
    if r < 20 and g < 20 and b < 20:
        return (r, g, b)
    if r > 235 and g > 235 and b > 235:
        return (r, g, b)

    h, s, l = rgb_to_hsl(r, g, b)

    # Special case: folder colors (desaturated yellow-green)
    if is_folder_color(r, g, b):
        # Shift to indigo-gray, reduce luminance for dark mode
        # Target: #8e95b8 (H:228, S:0.22, L:0.64)
        new_h = 228  # Indigo hue
        new_s = max(0.15, min(0.25, s + 0.05))  # Subtle color
        new_l = max(0.45, min(0.60, l * 0.75))  # Dark mode appropriate
        return hsl_to_rgb(new_h, new_s, new_l)

    # For desaturated colors (S < 0.3), shift toward indigo
    if s < 0.3:
        new_h = 240  # Indigo hue
        new_s = max(0.15, min(0.25, s + 0.10))
        new_l = max(0.45, min(0.60, l * 0.80))
        return hsl_to_rgb(new_h, new_s, new_l)

    # For saturated colors (S >= 0.3), map by hue family
    family = get_hue_family(h)

    if family == 'blue':
        # Blue -> Indigo/Lavender (primary accent)
        # Map to ~250 (indigo/violet range)
        new_h = 240 + (h - 230) * 0.5  # Compress range toward indigo
        new_h = max(235, min(260, new_h))
        new_s = min(1.0, s * 1.15)  # Boost saturation slightly
        new_l = max(0.35, min(0.75, l))  # Keep in dark mode range

    elif family == 'green':
        # Green -> Teal (CachyOS identity)
        # Map to ~160 (teal range)
        new_h = 155 + (h - 120) * 0.3
        new_h = max(150, min(170, new_h))
        new_s = min(1.0, s * 1.10)
        new_l = max(0.30, min(0.65, l))

    elif family == 'cyan':
        # Cyan stays cyan-ish but shifts slightly toward teal
        new_h = 175 + (h - 175) * 0.8
        new_h = max(170, min(195, new_h))
        new_s = min(1.0, s * 1.05)
        new_l = max(0.35, min(0.70, l))

    elif family == 'yellow':
        # Yellow -> Warm yellow (Catppuccin)
        new_h = 45 + (h - 62) * 0.5
        new_h = max(40, min(55, new_h))
        new_s = min(1.0, s * 1.10)
        new_l = max(0.55, min(0.80, l))  # Keep high luminance for visibility

    elif family == 'orange':
        # Orange -> Peach
        new_h = 25 + (h - 32) * 0.8
        new_h = max(20, min(35, new_h))
        new_s = min(1.0, s * 1.05)
        new_l = max(0.45, min(0.75, l))

    elif family == 'red':
        # Red -> Soft red (WCAG safe)
        new_h = h  # Keep red hue
        if h > 340:
            new_h = 350 + (h - 350) * 0.5
        else:
            new_h = 5 + (h - 10) * 0.5
        new_h = max(350, new_h) if new_h > 180 else min(15, new_h)
        new_s = min(0.85, s * 0.95)  # Slightly desaturate for softness
        new_l = max(0.45, min(0.65, l))

    elif family == 'purple':
        # Purple -> Mauve
        new_h = 270 + (h - 280) * 0.6
        new_h = max(265, min(285, new_h))
        new_s = min(1.0, s * 1.10)
        new_l = max(0.40, min(0.70, l))

    elif family == 'magenta':
        # Magenta/Pink -> Soft pink or shift toward mauve
        new_h = 310 + (h - 320) * 0.7
        new_h = max(300, min(330, new_h))
        new_s = min(0.90, s * 0.95)
        new_l = max(0.50, min(0.75, l))

    else:
        # Fallback: minor adjustments
        new_h = h
        new_s = s
        new_l = l

    return hsl_to_rgb(new_h, new_s, new_l)


# =============================================================================
# PNG PROCESSING
# =============================================================================

def process_png(filepath: Path) -> Tuple[str, bool, str]:
    """
    Process a single PNG file, transforming colors.
    Returns (filepath, success, message).
    """
    if not HAS_PIL:
        return (str(filepath), False, "PIL not available")

    try:
        img = Image.open(filepath)

        # Handle different modes
        if img.mode == 'P':
            # Palette mode - convert to RGBA
            img = img.convert('RGBA')
        elif img.mode == 'L':
            # Grayscale - skip
            return (str(filepath), True, "skipped (grayscale)")
        elif img.mode == '1':
            # 1-bit - skip
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
                    if a == 0:  # Fully transparent
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


# Regex patterns for SVG color attributes
SVG_HEX_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*[:=]\s*["\']?(#[0-9a-fA-F]{3,6})["\']?',
    re.IGNORECASE
)

SVG_RGB_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*[:=]\s*["\']?rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)["\']?',
    re.IGNORECASE
)

# Pattern for style attributes containing colors
SVG_STYLE_HEX_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*:\s*(#[0-9a-fA-F]{3,6})',
    re.IGNORECASE
)

SVG_STYLE_RGB_PATTERN = re.compile(
    r'(fill|stroke|stop-color|flood-color|lighting-color)\s*:\s*rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
    re.IGNORECASE
)


def transform_svg_hex_match(match) -> str:
    """Transform a hex color match in SVG."""
    attr = match.group(1)
    hex_color = match.group(2)
    rgb = hex_to_rgb(hex_color)
    if rgb is None:
        return match.group(0)
    new_rgb = transform_color(*rgb)
    new_hex = rgb_to_hex(*new_rgb)
    # Preserve original quote style
    original = match.group(0)
    if '="' in original or "='" in original:
        return f'{attr}="{new_hex}"'
    elif ':' in original:
        return f'{attr}:{new_hex}'
    return original.replace(hex_color, new_hex)


def transform_svg_rgb_match(match) -> str:
    """Transform an rgb() color match in SVG."""
    attr = match.group(1)
    r, g, b = int(match.group(2)), int(match.group(3)), int(match.group(4))
    new_r, new_g, new_b = transform_color(r, g, b)
    original = match.group(0)
    if '="' in original or "='" in original:
        return f'{attr}="rgb({new_r},{new_g},{new_b})"'
    elif ':' in original:
        return f'{attr}:rgb({new_r},{new_g},{new_b})'
    return f'{attr}:rgb({new_r},{new_g},{new_b})'


def transform_svg_style_hex_match(match) -> str:
    """Transform a hex color in style attribute."""
    attr = match.group(1)
    hex_color = match.group(2)
    rgb = hex_to_rgb(hex_color)
    if rgb is None:
        return match.group(0)
    new_rgb = transform_color(*rgb)
    new_hex = rgb_to_hex(*new_rgb)
    return f'{attr}:{new_hex}'


def transform_svg_style_rgb_match(match) -> str:
    """Transform an rgb() color in style attribute."""
    attr = match.group(1)
    r, g, b = int(match.group(2)), int(match.group(3)), int(match.group(4))
    new_r, new_g, new_b = transform_color(r, g, b)
    return f'{attr}:rgb({new_r},{new_g},{new_b})'


def process_svg(filepath: Path) -> Tuple[str, bool, str]:
    """
    Process a single SVG file, transforming colors.
    Returns (filepath, success, message).
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        original_content = content

        # Transform hex colors in attributes
        content = SVG_HEX_PATTERN.sub(transform_svg_hex_match, content)

        # Transform rgb() colors in attributes
        content = SVG_RGB_PATTERN.sub(transform_svg_rgb_match, content)

        # Transform hex colors in style attributes
        content = SVG_STYLE_HEX_PATTERN.sub(transform_svg_style_hex_match, content)

        # Transform rgb() colors in style attributes
        content = SVG_STYLE_RGB_PATTERN.sub(transform_svg_style_rgb_match, content)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return (str(filepath), True, "transformed")
        else:
            return (str(filepath), True, "unchanged")

    except Exception as e:
        return (str(filepath), False, str(e))


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def find_icons(base_dir: Path) -> Tuple[list, list]:
    """Find all PNG and SVG files in the icon directory."""
    pngs = []
    svgs = []

    for root, dirs, files in os.walk(base_dir):
        # Skip cursors directory
        if 'cursors' in root:
            continue
        for filename in files:
            filepath = Path(root) / filename
            if filename.lower().endswith('.png'):
                pngs.append(filepath)
            elif filename.lower().endswith('.svg'):
                svgs.append(filepath)

    return pngs, svgs


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Transform MATE icon colors to Synthesis Dark palette'
    )
    parser.add_argument(
        'icon_dir',
        nargs='?',
        default=os.path.expanduser('~/.local/share/icons/MATE-Synthesis-Dark'),
        help='Path to icon theme directory'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress'
    )

    args = parser.parse_args()
    icon_dir = Path(args.icon_dir)

    if not icon_dir.exists():
        print(f"ERROR: Icon directory not found: {icon_dir}")
        sys.exit(1)

    print(f"Scanning {icon_dir} for icons...")
    pngs, svgs = find_icons(icon_dir)
    print(f"Found {len(pngs)} PNG files and {len(svgs)} SVG files")

    if args.dry_run:
        print("\n[DRY RUN] Would process:")
        print(f"  - {len(pngs)} PNG files")
        print(f"  - {len(svgs)} SVG files")
        return

    # Process SVGs (single-threaded for simplicity)
    print(f"\nProcessing {len(svgs)} SVG files...")
    svg_transformed = 0
    svg_unchanged = 0
    svg_errors = 0

    for i, svg_path in enumerate(svgs, 1):
        filepath, success, message = process_svg(svg_path)
        if args.verbose:
            print(f"  [{i}/{len(svgs)}] {filepath}: {message}")
        if success:
            if message == "transformed":
                svg_transformed += 1
            else:
                svg_unchanged += 1
        else:
            svg_errors += 1
            if not args.verbose:
                print(f"  ERROR: {filepath}: {message}")

    print(f"SVG: {svg_transformed} transformed, {svg_unchanged} unchanged, {svg_errors} errors")

    # Process PNGs (parallel)
    if HAS_PIL and pngs:
        print(f"\nProcessing {len(pngs)} PNG files with {args.workers} workers...")
        png_transformed = 0
        png_unchanged = 0
        png_errors = 0

        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_png, p): p for p in pngs}

            for i, future in enumerate(as_completed(futures), 1):
                filepath, success, message = future.result()
                if args.verbose:
                    print(f"  [{i}/{len(pngs)}] {filepath}: {message}")
                elif i % 100 == 0:
                    print(f"  Processed {i}/{len(pngs)} PNG files...")

                if success:
                    if message == "transformed":
                        png_transformed += 1
                    else:
                        png_unchanged += 1
                else:
                    png_errors += 1
                    if not args.verbose:
                        print(f"  ERROR: {filepath}: {message}")

        print(f"PNG: {png_transformed} transformed, {png_unchanged} unchanged, {png_errors} errors")
    elif not HAS_PIL:
        print("\nSkipping PNG processing (PIL not available)")
        print("Install with: pip install Pillow")

    print("\nDone!")
    print("\nNext steps:")
    print("  1. Regenerate icon cache:")
    print(f"     gtk-update-icon-cache -f {icon_dir}")
    print("  2. Apply theme:")
    print("     gsettings set org.mate.interface icon-theme 'MATE-Synthesis-Dark'")


if __name__ == '__main__':
    main()
