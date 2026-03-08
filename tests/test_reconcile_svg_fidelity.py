"""
Unit tests for src/scripts/reconcile_svg_fidelity.py
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import reconcile_svg_fidelity as rsf


class TestReconcileSvgFidelity:
    def test_collect_override_candidates_uses_wrappers_for_native_mismatches(self, tmp_path):
        repo = tmp_path / "repo"
        wrapper = repo / "src" / "raster_wrappers" / "gnome-shell" / "assets" / "ws-switch-arrow-up.svg"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("<svg/>", encoding="utf-8")
        payload = {
            "results": [
                {
                    "relative_png": "gnome-shell/assets/ws-switch-arrow-up.png",
                    "parity_status": "mismatch",
                    "source_authority": "gnome-shell/assets/ws-switch-arrow-up.svg",
                    "normalized_rmse": 0.293527,
                    "differing_ratio": 0.13802083333333334,
                    "family": "gnome-shell",
                },
                {
                    "relative_png": "icons/Synthesis-Dark-Icons/16x16/actions/tab-new.png",
                    "parity_status": "mismatch",
                    "source_authority": "src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/actions/tab-new.svg",
                    "normalized_rmse": 0.000880459,
                    "differing_ratio": 0.328125,
                    "family": "icon",
                },
            ]
        }

        candidates = rsf.collect_override_candidates(repo, payload)

        assert candidates == [
            {
                "relative_png": "gnome-shell/assets/ws-switch-arrow-up.png",
                "native_authority": "gnome-shell/assets/ws-switch-arrow-up.svg",
                "preferred_authority": "src/raster_wrappers/gnome-shell/assets/ws-switch-arrow-up.svg",
                "normalized_rmse": 0.293527,
                "differing_ratio": 0.13802083333333334,
                "family": "gnome-shell",
            }
        ]
