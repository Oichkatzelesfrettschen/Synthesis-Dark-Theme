"""
Unit tests for src/scripts/transform_colors.py

Covers:
- Hue family detection
- Near-black/near-white passthrough
- Folder color detection and mapping
- Desaturated color mapping (toward indigo)
- Per-family saturated color mapping
- process_svg: color substitution in SVG text
- Idempotency: transforming a transformed color again should not change it dramatically
- Repo-scan target list integrity
"""

import sys
from pathlib import Path
import pytest

# Import from the script directly
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import transform_colors as tc


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def to_hsl(r, g, b):
    h, s, l = tc.rgb_to_hsl(r, g, b)
    return h, s, l


# ---------------------------------------------------------------------------
# Near-black and near-white passthrough
# ---------------------------------------------------------------------------

class TestPassthrough:
    def test_pure_black_unchanged(self):
        assert tc.transform_color(0, 0, 0) == (0, 0, 0)

    def test_near_black_unchanged(self):
        assert tc.transform_color(10, 10, 10) == (10, 10, 10)

    def test_pure_white_unchanged(self):
        assert tc.transform_color(255, 255, 255) == (255, 255, 255)

    def test_near_white_unchanged(self):
        assert tc.transform_color(240, 240, 240) == (240, 240, 240)

    def test_border_black_not_passed(self):
        # r=21 breaks threshold; should be transformed
        r, g, b = tc.transform_color(21, 21, 21)
        assert (r, g, b) != (21, 21, 21)


# ---------------------------------------------------------------------------
# Folder color detection
# ---------------------------------------------------------------------------

class TestFolderDetection:
    def test_mate_folder_color_detected(self):
        # MATE folders: pale yellow-green, H~65, S~0.15, L~0.78
        assert tc.is_folder_color(198, 199, 172) is True

    def test_blue_not_folder(self):
        assert tc.is_folder_color(100, 100, 220) is False

    def test_red_not_folder(self):
        assert tc.is_folder_color(220, 50, 50) is False

    def test_folder_color_maps_to_indigo(self):
        # Transformed folder color should land in indigo hue range (200-280)
        r, g, b = tc.transform_color(198, 199, 172)
        h, s, l = to_hsl(r, g, b)
        assert 200 <= h <= 280, f"Expected indigo hue, got H={h:.1f}"


# ---------------------------------------------------------------------------
# Hue family mapping
# ---------------------------------------------------------------------------

class TestHueFamily:
    def test_red(self):
        assert tc.get_hue_family(10) == 'red'
        assert tc.get_hue_family(355) == 'red'

    def test_orange(self):
        assert tc.get_hue_family(30) == 'orange'

    def test_yellow(self):
        assert tc.get_hue_family(60) == 'yellow'

    def test_green(self):
        assert tc.get_hue_family(120) == 'green'

    def test_cyan(self):
        assert tc.get_hue_family(180) == 'cyan'

    def test_blue(self):
        assert tc.get_hue_family(230) == 'blue'

    def test_purple(self):
        assert tc.get_hue_family(280) == 'purple'

    def test_magenta(self):
        assert tc.get_hue_family(320) == 'magenta'

    def test_blue_maps_to_indigo_range(self):
        # #4169e1 = royal blue (H~225, S~0.73, L~0.57) -> should go indigo
        r, g, b = tc.transform_color(65, 105, 225)
        h, s, l = to_hsl(r, g, b)
        assert 230 <= h <= 265, f"Blue should map to indigo, got H={h:.1f}"

    def test_green_maps_to_teal_range(self):
        # #228b22 = forest green (H~120, S~0.61, L~0.34)
        r, g, b = tc.transform_color(34, 139, 34)
        h, s, l = to_hsl(r, g, b)
        assert 140 <= h <= 185, f"Green should map to teal, got H={h:.1f}"

    def test_purple_maps_to_mauve_range(self):
        # #8000ff = vivid purple (H=270)
        r, g, b = tc.transform_color(128, 0, 255)
        h, s, l = to_hsl(r, g, b)
        assert 260 <= h <= 295, f"Purple should map to mauve, got H={h:.1f}"


# ---------------------------------------------------------------------------
# Desaturated colors (toward indigo)
# ---------------------------------------------------------------------------

class TestDesaturated:
    def test_gray_maps_to_indigo(self):
        # Mid-gray: S~0, should shift toward indigo
        r, g, b = tc.transform_color(128, 128, 128)
        h, s, l = to_hsl(r, g, b)
        assert 200 <= h <= 280, f"Gray should shift to indigo range, got H={h:.1f}"
        assert s >= 0.10, f"Gray should gain some saturation, got S={s:.2f}"


# ---------------------------------------------------------------------------
# SVG processing
# ---------------------------------------------------------------------------

class TestSvgProcessing:
    def test_svg_hex_color_replaced(self, tmp_path):
        # A blue folder color in SVG should be transformed
        svg_content = '<circle fill="#4169e1" r="10"/>'
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding='utf-8')

        filepath, success, message = tc.process_svg(svg_file)
        assert success, f"SVG processing failed: {message}"
        result = svg_file.read_text(encoding='utf-8')
        # Color should have changed (blue -> indigo family)
        assert "#4169e1" not in result

    def test_svg_unchanged_passthrough(self, tmp_path):
        # Near-white on a background -- should not change
        svg_content = '<circle fill="#ffffff" r="10"/>'
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding='utf-8')

        filepath, success, message = tc.process_svg(svg_file)
        assert success
        result = svg_file.read_text(encoding='utf-8')
        assert "#ffffff" in result

    def test_svg_nonexistent_file_returns_error(self, tmp_path):
        fake = tmp_path / "nonexistent.svg"
        filepath, success, message = tc.process_svg(fake)
        assert not success


# ---------------------------------------------------------------------------
# Idempotency check
# ---------------------------------------------------------------------------

class TestIdempotency:
    """
    Transforming an already-transformed color should not produce wildly
    different output. Hue should remain stable within +/-30 degrees.
    """
    def test_blue_idempotent(self):
        once = tc.transform_color(65, 105, 225)   # royal blue
        twice = tc.transform_color(*once)
        h1 = to_hsl(*once)[0]
        h2 = to_hsl(*twice)[0]
        assert abs(h1 - h2) <= 30, f"Hue drift too large: {h1:.1f} -> {h2:.1f}"

    def test_green_idempotent(self):
        once = tc.transform_color(34, 139, 34)
        twice = tc.transform_color(*once)
        h1 = to_hsl(*once)[0]
        h2 = to_hsl(*twice)[0]
        assert abs(h1 - h2) <= 30, f"Hue drift too large: {h1:.1f} -> {h2:.1f}"


# ---------------------------------------------------------------------------
# Repo scan targets
# ---------------------------------------------------------------------------

class TestRepoScanTargets:
    def test_all_expected_targets_present(self):
        expected = {'icons', 'metacity-1', 'gtk-2.0', 'gtk-3.0',
                    'gtk-3.20', 'gtk-4.0', 'xfwm4', 'cinnamon'}
        assert expected.issubset(set(tc.REPO_SCAN_TARGETS))
