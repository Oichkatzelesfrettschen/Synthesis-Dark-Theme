"""
Unit tests for src/scripts/verify_svg_parity.py
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import verify_svg_parity as vsp


class TestAuthorityMode:
    def test_gtk2_sprite_sheet_is_specialized(self):
        mode, detail = vsp.classify_authority_mode(
            "gtk-2.0/assets/button.png",
            "src/assets/gtk2/assets.svg",
        )

        assert mode == "specialized-renderer"
        assert "sprite-sheet" in detail

    def test_non_svg_authority_is_specialized(self):
        mode, detail = vsp.classify_authority_mode(
            "xfwm4/close-active.png",
            "xfwm4/render-assets.sh",
        )

        assert mode == "specialized-renderer"
        assert "scripted" in detail.lower()

    def test_direct_svg_authority_is_render_candidate(self):
        mode, detail = vsp.classify_authority_mode(
            "icons/Synthesis-Dark-Icons/16x16/apps/firefox.png",
            "icons/Synthesis-Dark-Icons/scalable/apps/firefox.svg",
        )

        assert mode == "direct-svg"
        assert "Direct SVG render parity candidate" in detail


class TestMetricParsing:
    def test_parse_ae_metric(self):
        assert vsp.parse_ae_metric("42") == 42.0

    def test_parse_rmse_metric_with_normalized_component(self):
        raw, normalized = vsp.parse_rmse_metric("123.45 (0.0188344)")

        assert raw == 123.45
        assert normalized == 0.0188344

    def test_parse_rmse_metric_without_parenthesized_component(self):
        raw, normalized = vsp.parse_rmse_metric("0")

        assert raw == 0.0
        assert normalized == 0.0


class TestParityGrading:
    def test_exact_match_requires_zero_ae_and_zero_rmse(self):
        status, ratio = vsp.grade_parity(0.0, 0.0, 16, 16, 0.002, 0.01)

        assert status == "exact"
        assert ratio == 0.0

    def test_close_match_uses_thresholds(self):
        status, ratio = vsp.grade_parity(2.0, 0.001, 32, 32, 0.002, 0.01)

        assert status == "close"
        assert ratio > 0.0

    def test_large_difference_is_mismatch(self):
        status, ratio = vsp.grade_parity(80.0, 0.02, 16, 16, 0.002, 0.01)

        assert status == "mismatch"
        assert ratio == 80.0 / 256.0

    def test_raster_wrapper_can_be_close_despite_many_small_pixel_deltas(self):
        status, ratio = vsp.grade_parity(
            84.0,
            0.000880459,
            16,
            16,
            0.002,
            0.01,
            source_authority="src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/actions/tab-new.svg",
        )

        assert status == "close"
        assert ratio == 84.0 / 256.0


class TestReferenceAudit:
    def test_is_actionable_png_reference_line_skips_extension_metadata(self):
        assert not vsp.is_actionable_png_reference_line("OUTPUT_EXT = '.png'")
        assert not vsp.is_actionable_png_reference_line("set -l output_ext '.png'")
        assert not vsp.is_actionable_png_reference_line("if filename.lower().endswith('.png'):")
        assert vsp.is_actionable_png_reference_line('source: "images/background.png"')

    def test_collect_runtime_png_references_skips_backend_alias_dump(self, tmp_path):
        repo = tmp_path / "repo"
        alias_json = repo / "src" / "icons_backend" / "aliases" / "installed-output-aliases.json"
        qml = repo / "kde" / "plasma" / "main.qml"
        svg = repo / "assets" / "button.svg"
        alias_json.parent.mkdir(parents=True)
        qml.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        alias_json.write_text('{"foo":"icon.png"}', encoding="utf-8")
        qml.write_text('source: "images/background.png"\n', encoding="utf-8")
        svg.write_text('inkscape:export-filename="button.png"\n', encoding="utf-8")

        hits = vsp.collect_runtime_png_references(repo)

        assert hits == [
            {
                "path": "kde/plasma/main.qml",
                "line": 1,
                "text": 'source: "images/background.png"',
                "reference_kind": "theme-runtime",
            }
        ]

    def test_collect_runtime_png_references_skips_analysis_scripts(self, tmp_path):
        repo = tmp_path / "repo"
        analysis_script = repo / "src" / "scripts" / "vectorize_assets.py"
        render_script = repo / "src" / "scripts" / "render_engine.py"
        analysis_script.parent.mkdir(parents=True)
        render_script.parent.mkdir(parents=True, exist_ok=True)
        analysis_script.write_text('print("thumbnail.png")\n', encoding="utf-8")
        render_script.write_text('outfile = f"{name}.png"\n', encoding="utf-8")

        hits = vsp.collect_runtime_png_references(repo)

        assert hits == [
            {
                "path": "src/scripts/render_engine.py",
                "line": 1,
                "text": 'outfile = f"{name}.png"',
                "reference_kind": "build-tooling",
            }
        ]
