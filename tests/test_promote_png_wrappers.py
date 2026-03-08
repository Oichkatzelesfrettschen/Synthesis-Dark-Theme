"""
Unit tests for src/scripts/promote_png_wrappers.py
"""

import json
import sys
from pathlib import Path

from PIL import Image


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import promote_png_wrappers as ppw
import vectorize_assets as va


class TestPromotePngWrappers:
    def test_wrapper_path_mirrors_relative_png(self):
        path = ppw.wrapper_path(Path("src/raster_wrappers"), "icons/Synthesis-Dark-Icons/16x16/apps/firefox.png")

        assert path == Path("src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/apps/firefox.svg")

    def test_promote_wrappers_writes_svg_authority_for_mismatch(self, tmp_path):
        repo = tmp_path / "repo"
        png = repo / "assets" / "button.png"
        png.parent.mkdir(parents=True)
        Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(png)

        payload = {
            "results": [
                {
                    "relative_png": "assets/button.png",
                    "parity_status": "mismatch",
                    "family": "assets",
                }
            ]
        }

        summary = ppw.promote_wrappers(
            repo_root=repo,
            output_root=repo / "src" / "raster_wrappers",
            candidates=ppw.parity_candidates(payload, {"mismatch"}, include_reference=False),
            force=False,
            dry_run=False,
        )

        wrapper = repo / "src" / "raster_wrappers" / "assets" / "button.svg"
        assert summary["promoted_count"] == 1
        assert wrapper.exists()
        text = wrapper.read_text(encoding="utf-8")
        assert "data:image/png;base64" in text
        assert summary["by_reason"] == {"mismatch": 1}

    def test_raster_wrapper_becomes_known_authority(self, tmp_path):
        repo = tmp_path / "repo"
        out = tmp_path / "out"
        png = repo / "icons" / "Synthesis-Dark-Icons" / "16x16" / "actions" / "document-save.png"
        wrapper = repo / "src" / "raster_wrappers" / "icons" / "Synthesis-Dark-Icons" / "16x16" / "actions" / "document-save.svg"
        png.parent.mkdir(parents=True)
        wrapper.parent.mkdir(parents=True)
        png.write_bytes(b"png")
        wrapper.write_text("<svg/>", encoding="utf-8")
        out.mkdir()

        entry = va.classify_asset(repo, png.relative_to(repo), out, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/actions/document-save.svg"
        )

    def test_dry_run_reports_without_writing(self, tmp_path):
        repo = tmp_path / "repo"
        png = repo / "assets" / "button.png"
        png.parent.mkdir(parents=True)
        Image.new("RGBA", (2, 2), (0, 0, 255, 255)).save(png)

        payload = {
            "results": [
                {
                    "relative_png": "assets/button.png",
                    "parity_status": "specialized-renderer",
                    "family": "assets",
                }
            ]
        }

        summary = ppw.promote_wrappers(
            repo_root=repo,
            output_root=repo / "src" / "raster_wrappers",
            candidates=ppw.parity_candidates(payload, {"specialized-renderer"}, include_reference=False),
            force=False,
            dry_run=True,
        )

        assert summary["promoted_count"] == 1
        assert not (repo / "src" / "raster_wrappers" / "assets" / "button.svg").exists()

    def test_manifest_candidates_can_promote_icon_reconciliation_items(self):
        manifest = [
            {
                "relative_png": "icons/Synthesis-Dark-Icons/16x16/status/trophy-gold.png",
                "batch_priority": "icon-family-reconciliation",
                "family": "icon",
            },
            {
                "relative_png": "Art/logo.png",
                "batch_priority": "review-later",
                "family": "Art",
            },
        ]

        candidates = ppw.manifest_candidates(
            manifest,
            {"icon-family-reconciliation"},
            include_reference=False,
        )

        assert candidates == {
            "icons/Synthesis-Dark-Icons/16x16/status/trophy-gold.png": {
                "relative_png": "icons/Synthesis-Dark-Icons/16x16/status/trophy-gold.png",
                "family": "icon",
                "reason": "icon-family-reconciliation",
            }
        }
