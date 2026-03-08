"""
Unit tests for src/scripts/materialize_runtime_asset_svgs.py
"""

import json
import sys
from pathlib import Path

from PIL import Image


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import materialize_runtime_asset_svgs as mras


class TestMaterializeRuntimeAssetSvgs:
    def test_choose_svg_source_prefers_runtime_then_authority_then_wrapper(self, tmp_path):
        repo = tmp_path / "repo"
        runtime_svg = repo / "assets" / "button.svg"
        authority = repo / "src" / "assets" / "gtk3-4" / "button.svg"
        wrapper = repo / "src" / "raster_wrappers" / "assets" / "button.svg"
        runtime_svg.parent.mkdir(parents=True)
        authority.parent.mkdir(parents=True)
        wrapper.parent.mkdir(parents=True)
        runtime_svg.write_text("<svg/>", encoding="utf-8")
        authority.write_text("<svg authority/>", encoding="utf-8")
        wrapper.write_text("<svg wrapper/>", encoding="utf-8")

        entry = {"relative_png": "assets/button.png", "source_authority": "src/assets/gtk3-4/button.svg"}
        kind, path = mras.choose_svg_source(repo, entry)

        assert kind == "existing-runtime-svg"
        assert path == runtime_svg

    def test_choose_svg_source_prefers_recorded_fidelity_override(self, tmp_path):
        repo = tmp_path / "repo"
        runtime_svg = repo / "gnome-shell" / "assets" / "ws-switch-arrow-up.svg"
        wrapper = repo / "src" / "raster_wrappers" / "gnome-shell" / "assets" / "ws-switch-arrow-up.svg"
        preferred = repo / "src" / "raster_wrappers" / "preferred-authorities.json"
        runtime_svg.parent.mkdir(parents=True)
        wrapper.parent.mkdir(parents=True)
        preferred.parent.mkdir(parents=True, exist_ok=True)
        runtime_svg.write_text("<svg native/>", encoding="utf-8")
        wrapper.write_text("<svg wrapper/>", encoding="utf-8")
        preferred.write_text(
            json.dumps(
                {
                    "gnome-shell/assets/ws-switch-arrow-up.png": (
                        "src/raster_wrappers/gnome-shell/assets/ws-switch-arrow-up.svg"
                    )
                }
            ),
            encoding="utf-8",
        )

        entry = {
            "relative_png": "gnome-shell/assets/ws-switch-arrow-up.png",
            "source_authority": "gnome-shell/assets/ws-switch-arrow-up.svg",
        }
        kind, path = mras.choose_svg_source(repo, entry)

        assert kind == "preferred-authority"
        assert path == wrapper

    def test_should_materialize_runtime_svg_covers_shell_and_cinnamon_assets(self):
        assert mras.should_materialize_runtime_svg(Path("assets/button.png"))
        assert mras.should_materialize_runtime_svg(Path("gnome-shell/assets/ws-switch-arrow-up.png"))
        assert mras.should_materialize_runtime_svg(Path("cinnamon/common-assets/misc/overview.png"))
        assert not mras.should_materialize_runtime_svg(
            Path("icons/Synthesis-Dark-Icons/16x16/actions/document-save.png")
        )

    def test_materialize_runtime_svgs_copies_authority_when_missing(self, tmp_path):
        repo = tmp_path / "repo"
        png = repo / "assets" / "button.png"
        authority = repo / "src" / "assets" / "gtk3-4" / "button.svg"
        png.parent.mkdir(parents=True)
        authority.parent.mkdir(parents=True)
        Image.new("RGBA", (2, 2), (1, 2, 3, 255)).save(png)
        authority.write_text("<svg authority/>", encoding="utf-8")

        summary = mras.materialize_runtime_svgs(
            repo,
            [{"relative_png": "assets/button.png", "source_authority": "src/assets/gtk3-4/button.svg"}],
            force=False,
            dry_run=False,
        )

        runtime_svg = repo / "assets" / "button.svg"
        assert summary["materialized_count"] == 1
        assert summary["by_source_kind"] == {"source-authority": 1}
        assert runtime_svg.read_text(encoding="utf-8") == "<svg authority/>"

    def test_materialize_runtime_svgs_wraps_png_when_no_svg_source_exists(self, tmp_path):
        repo = tmp_path / "repo"
        png = repo / "assets" / "button.png"
        png.parent.mkdir(parents=True)
        Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(png)

        summary = mras.materialize_runtime_svgs(
            repo,
            [{"relative_png": "assets/button.png", "source_authority": None}],
            force=False,
            dry_run=False,
        )

        runtime_svg = repo / "assets" / "button.svg"
        assert summary["by_source_kind"] == {"wrap-png": 1}
        assert "data:image/png;base64" in runtime_svg.read_text(encoding="utf-8")

    def test_materialize_runtime_svgs_force_mode_tolerates_same_file_source(self, tmp_path):
        repo = tmp_path / "repo"
        runtime_svg = repo / "assets" / "button.svg"
        png = repo / "assets" / "button.png"
        runtime_svg.parent.mkdir(parents=True)
        runtime_svg.write_text("<svg runtime/>", encoding="utf-8")
        Image.new("RGBA", (2, 2), (1, 2, 3, 255)).save(png)

        summary = mras.materialize_runtime_svgs(
            repo,
            [{"relative_png": "assets/button.png", "source_authority": "assets/button.svg"}],
            force=True,
            dry_run=False,
        )

        assert summary["materialized_count"] == 1
        assert summary["by_source_kind"] == {"existing-runtime-svg": 1}
        assert runtime_svg.read_text(encoding="utf-8") == "<svg runtime/>"

    def test_dry_run_does_not_write_files(self, tmp_path):
        repo = tmp_path / "repo"
        png = repo / "assets" / "button.png"
        png.parent.mkdir(parents=True)
        Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(png)

        summary = mras.materialize_runtime_svgs(
            repo,
            [{"relative_png": "assets/button.png", "source_authority": None}],
            force=False,
            dry_run=True,
        )

        assert summary["materialized_count"] == 1
        assert not (repo / "assets" / "button.svg").exists()

    def test_load_baseplate_rects_parses_icon_names(self, tmp_path):
        svg = tmp_path / "sheet.svg"
        svg.write_text(
            """
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <g inkscape:groupmode="layer" inkscape:label="Baseplate sample-icon">
    <text inkscape:label="icon-name">sample-icon</text>
    <rect id="sample-rect" />
  </g>
</svg>
""".strip(),
            encoding="utf-8",
        )

        assert mras.load_baseplate_rects(svg) == {"sample-icon": "sample-rect"}

    def test_materialize_explicit_runtime_svgs_exports_and_aliases(self, tmp_path):
        repo = tmp_path / "repo"
        selection_sheet = repo / "gtk-3.20" / "assets" / "gtk3-selection.svg"
        radio_svg = repo / "assets" / "radio-unchecked.svg"
        radio_backdrop_svg = repo / "assets" / "radio-unchecked-insensitive-backdrop.svg"
        checkbox_insensitive_svg = repo / "assets" / "checkbox-unchecked-insensitive.svg"
        checkbox_backdrop_insensitive_svg = repo / "assets" / "checkbox-unchecked-insensitive-backdrop.svg"
        noise_png = repo / "gnome-shell" / "assets" / "noise-texture.png"
        selection_sheet.parent.mkdir(parents=True, exist_ok=True)
        radio_svg.parent.mkdir(parents=True, exist_ok=True)
        noise_png.parent.mkdir(parents=True, exist_ok=True)
        selection_sheet.write_text(
            """
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <g inkscape:groupmode="layer" inkscape:label="Baseplate selection-mode-checkbox-unchecked">
    <text inkscape:label="icon-name">selection-mode-checkbox-unchecked</text>
    <rect id="rect-unchecked" />
  </g>
  <g inkscape:groupmode="layer" inkscape:label="Baseplate selection-mode-checkbox-checked">
    <text inkscape:label="icon-name">selection-mode-checkbox-checked</text>
    <rect id="rect-checked" />
  </g>
</svg>
""".strip(),
            encoding="utf-8",
        )
        radio_svg.write_text("<svg radio/>", encoding="utf-8")
        radio_backdrop_svg.write_text("<svg radio backdrop/>", encoding="utf-8")
        checkbox_insensitive_svg.write_text("<svg checkbox insensitive/>", encoding="utf-8")
        checkbox_backdrop_insensitive_svg.write_text("<svg checkbox backdrop insensitive/>", encoding="utf-8")
        Image.new("RGBA", (2, 2), (1, 2, 3, 255)).save(noise_png)

        exported = []

        def fake_export(svg_source, fragment_id, output_path):
            exported.append((svg_source, fragment_id, output_path))
            output_path.write_text(f"<svg id='{fragment_id}'/>", encoding="utf-8")

        old_sheet = mras.SELECTION_SHEET
        old_exports = mras.SELECTION_MODE_CHECKBOX_EXPORTS
        try:
            mras.SELECTION_SHEET = Path("gtk-3.20/assets/gtk3-selection.svg")
            mras.SELECTION_MODE_CHECKBOX_EXPORTS = {
                "selection-mode-checkbox-unchecked",
                "selection-mode-checkbox-checked",
            }
            items = mras.materialize_explicit_runtime_svgs(
                repo_root=repo,
                force=False,
                dry_run=False,
                exporter=fake_export,
            )
        finally:
            mras.SELECTION_SHEET = old_sheet
            mras.SELECTION_MODE_CHECKBOX_EXPORTS = old_exports

        assert (repo / "assets" / "selection-mode-checkbox-unchecked.svg").read_text(encoding="utf-8") == "<svg id='rect-unchecked'/>"
        assert (repo / "assets" / "selection-mode-radio-unchecked.svg").read_text(encoding="utf-8") == "<svg radio/>"
        assert "data:image/png;base64" in (repo / "gnome-shell" / "assets" / "noise-texture.svg").read_text(encoding="utf-8")
        assert any(item["source_kind"] == "selection-sheet-export" for item in items)
        assert any(item["source_kind"] == "svg-alias-copy" for item in items)
        assert any(item["source_kind"] == "wrap-png-explicit" for item in items)
        assert exported == [
            (
                repo / "gtk-3.20" / "assets" / "gtk3-selection.svg",
                "rect-checked",
                repo / "assets" / "selection-mode-checkbox-checked.svg",
            ),
            (
                repo / "gtk-3.20" / "assets" / "gtk3-selection.svg",
                "rect-unchecked",
                repo / "assets" / "selection-mode-checkbox-unchecked.svg",
            ),
        ]

    def test_load_metacity_runtime_assets_collects_png_backed_outputs(self, tmp_path):
        repo = tmp_path / "repo"
        xml = repo / "metacity-1" / "metacity-theme.xml"
        png = repo / "metacity-1" / "close_focused_normal.png"
        svg_backed_png = repo / "metacity-1" / "shade_unfocused.png"
        xml.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (2, 2), (1, 2, 3, 255)).save(png)
        Image.new("RGBA", (2, 2), (4, 5, 6, 255)).save(svg_backed_png)
        xml.write_text(
            """
<metacity_theme>
  <image filename="close_focused_normal.png" />
  <image filename="shade_unfocused.svg" />
  <image filename="assets/close.svg" />
</metacity_theme>
""".strip(),
            encoding="utf-8",
        )

        assert mras.load_metacity_runtime_assets(repo) == [
            (
                repo / "metacity-1" / "close_focused_normal.png",
                repo / "metacity-1" / "close_focused_normal.svg",
            ),
            (
                repo / "metacity-1" / "shade_unfocused.png",
                repo / "metacity-1" / "shade_unfocused.svg",
            ),
        ]

    def test_materialize_explicit_runtime_svgs_wraps_metacity_pngs(self, tmp_path):
        repo = tmp_path / "repo"
        xml = repo / "metacity-1" / "metacity-theme.xml"
        png = repo / "metacity-1" / "close_focused_normal.png"
        xml.parent.mkdir(parents=True, exist_ok=True)
        xml.write_text('<image filename="close_focused_normal.png" />', encoding="utf-8")
        Image.new("RGBA", (2, 2), (10, 20, 30, 255)).save(png)

        items = mras.materialize_explicit_runtime_svgs(
            repo_root=repo,
            force=False,
            dry_run=False,
            exporter=lambda *args, **kwargs: None,
        )

        wrapped = repo / "metacity-1" / "close_focused_normal.svg"
        assert wrapped.exists()
        assert "data:image/png;base64" in wrapped.read_text(encoding="utf-8")
        assert any(item["source_kind"] == "metacity-wrap-png" for item in items)
