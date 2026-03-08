"""
Unit tests for src/scripts/promote_icon_backend.py
"""

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import promote_icon_backend as pib


class TestPromoteIconBackend:
    def test_geometry_and_skin_paths_follow_semantic_id(self, tmp_path):
        backend_root = tmp_path / "backend"

        geometry = pib.geometry_target_path(backend_root, "icon/apps/firefox")
        skin = pib.skin_metadata_path(backend_root, "icon/apps/firefox", "tela")

        assert geometry == backend_root / "geometry" / "apps" / "firefox.svg"
        assert skin == backend_root / "skins" / "tela" / "apps" / "firefox.json"

    def test_promote_svg_backed_icons_copies_svg_and_writes_metadata(self, tmp_path):
        repo_root = tmp_path / "repo"
        backend_root = repo_root / "src" / "icons_backend"
        source_svg = repo_root / "icons" / "Synthesis-Dark-Icons" / "scalable" / "apps" / "firefox.svg"
        source_svg.parent.mkdir(parents=True)
        source_svg.write_text("<svg/>", encoding="utf-8")

        registry = [
            {
                "semantic_id": "icon/apps/firefox",
                "style_skin": "tela",
                "category": "apps",
                "installed_outputs": [
                    "icons/Synthesis-Dark-Icons/16x16/apps/firefox.png",
                    "icons/Synthesis-Dark-Icons/32x32/apps/firefox.png",
                ],
                "installed_output_count": 2,
                "authoritative_svg_candidates": [
                    "icons/Synthesis-Dark-Icons/scalable/apps/firefox.svg"
                ],
                "has_authoritative_svg": True,
            },
            {
                "semantic_id": "icon/actions/document-save",
                "style_skin": "mate",
                "category": "actions",
                "installed_outputs": [
                    "icons/Synthesis-Dark-Icons/16x16/actions/document-save.png"
                ],
                "installed_output_count": 1,
                "authoritative_svg_candidates": [],
                "has_authoritative_svg": False,
            },
        ]

        summary = pib.promote_svg_backed_icons(
            registry,
            backend_root,
            repo_root,
            min_seed_outputs=5,
        )

        assert summary["promoted"] == 1
        assert summary["unresolved"]["mate"] == 1
        assert summary["unresolved_work_items"] == 1

        geometry = backend_root / "geometry" / "apps" / "firefox.svg"
        skin_json = backend_root / "skins" / "tela" / "apps" / "firefox.json"
        unresolved = backend_root / "skins" / "mate" / "unresolved.json"
        unresolved_work_item = (
            backend_root
            / "registry"
            / "unresolved"
            / "mate"
            / "actions"
            / "document-save.json"
        )
        aliases = backend_root / "aliases" / "installed-output-aliases.json"

        assert geometry.read_text(encoding="utf-8") == "<svg/>"
        metadata = json.loads(skin_json.read_text(encoding="utf-8"))
        assert metadata["semantic_id"] == "icon/apps/firefox"
        assert unresolved.exists()
        work_item = json.loads(unresolved_work_item.read_text(encoding="utf-8"))
        assert work_item["status"] == "needs-authoritative-geometry"
        assert work_item["suggested_geometry_svg"] == "geometry/actions/document-save.svg"
        alias_data = json.loads(aliases.read_text(encoding="utf-8"))
        assert "icons/Synthesis-Dark-Icons/16x16/apps/firefox.png" in alias_data

    def test_promote_cleans_stale_generated_backend_files(self, tmp_path):
        repo_root = tmp_path / "repo"
        backend_root = repo_root / "src" / "icons_backend"
        source_svg = repo_root / "icons" / "Synthesis-Dark-Icons" / "scalable" / "apps" / "firefox.svg"
        source_svg.parent.mkdir(parents=True)
        source_svg.write_text("<svg/>", encoding="utf-8")

        stale_geometry = backend_root / "geometry" / "apps" / "stale.svg"
        stale_metadata = backend_root / "skins" / "tela" / "apps" / "stale.json"
        stale_work_item = backend_root / "registry" / "unresolved" / "mate" / "actions" / "stale.json"
        stale_alias = backend_root / "aliases" / "installed-output-aliases.json"
        stale_geometry.parent.mkdir(parents=True, exist_ok=True)
        stale_metadata.parent.mkdir(parents=True, exist_ok=True)
        stale_work_item.parent.mkdir(parents=True, exist_ok=True)
        stale_alias.parent.mkdir(parents=True, exist_ok=True)
        stale_geometry.write_text("stale", encoding="utf-8")
        stale_metadata.write_text("{}", encoding="utf-8")
        stale_work_item.write_text("{}", encoding="utf-8")
        stale_alias.write_text("{}", encoding="utf-8")

        registry = [
            {
                "semantic_id": "icon/apps/firefox",
                "style_skin": "tela",
                "category": "apps",
                "installed_outputs": [
                    "icons/Synthesis-Dark-Icons/16x16/apps/firefox.png",
                ],
                "installed_output_count": 1,
                "authoritative_svg_candidates": [
                    "icons/Synthesis-Dark-Icons/scalable/apps/firefox.svg"
                ],
                "has_authoritative_svg": True,
            }
        ]

        pib.promote_svg_backed_icons(registry, backend_root, repo_root, min_seed_outputs=6)

        assert not stale_geometry.exists()
        assert not stale_metadata.exists()
        assert not stale_work_item.exists()

    def test_unresolved_seed_candidates_can_be_promoted_from_symbolic_svg(self, tmp_path):
        repo_root = tmp_path / "repo"
        backend_root = repo_root / "src" / "icons_backend"
        source_svg = (
            repo_root
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "actions"
            / "document-save-symbolic.svg"
        )
        source_svg.parent.mkdir(parents=True)
        source_svg.write_text("<svg/>", encoding="utf-8")

        registry = [
            {
                "semantic_id": "icon/actions/document-save",
                "style_skin": "mate",
                "category": "actions",
                "installed_outputs": [
                    "icons/Synthesis-Dark-Icons/16x16/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/22x22/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/24x24/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/32x32/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/48x48/actions/document-save.png",
                ],
                "installed_output_count": 5,
                "authoritative_svg_candidates": [],
                "has_authoritative_svg": False,
            },
        ]

        summary = pib.promote_svg_backed_icons(
            registry,
            backend_root,
            repo_root,
            min_seed_outputs=5,
        )

        assert summary["promoted"] == 1
        assert summary["seed_promoted"] == 1
        geometry = backend_root / "geometry" / "actions" / "document-save.svg"
        metadata = json.loads(
            (backend_root / "skins" / "mate" / "actions" / "document-save.json").read_text(encoding="utf-8")
        )
        assert geometry.read_text(encoding="utf-8") == "<svg/>"
        assert metadata["source_kind"] == "geometry-seed"

    def test_unresolved_seed_candidates_use_alias_aware_symbolic_resolution(self, tmp_path):
        repo_root = tmp_path / "repo"
        backend_root = repo_root / "src" / "icons_backend"
        source_svg = (
            repo_root
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "actions"
            / "document-save-symbolic.svg"
        )
        source_svg.parent.mkdir(parents=True)
        source_svg.write_text("<svg/>", encoding="utf-8")

        registry = [
            {
                "semantic_id": "icon/actions/stock_save",
                "style_skin": "mate",
                "category": "actions",
                "installed_outputs": [
                    "icons/Synthesis-Dark-Icons/16x16/actions/stock_save.png",
                    "icons/Synthesis-Dark-Icons/22x22/actions/stock_save.png",
                    "icons/Synthesis-Dark-Icons/24x24/actions/stock_save.png",
                    "icons/Synthesis-Dark-Icons/32x32/actions/stock_save.png",
                    "icons/Synthesis-Dark-Icons/48x48/actions/stock_save.png",
                ],
                "installed_output_count": 5,
                "authoritative_svg_candidates": [],
                "has_authoritative_svg": False,
            },
        ]

        summary = pib.promote_svg_backed_icons(
            registry,
            backend_root,
            repo_root,
            min_seed_outputs=5,
        )

        assert summary["promoted"] == 1
        assert summary["seed_promoted"] == 1
        geometry = backend_root / "geometry" / "actions" / "stock_save.svg"
        metadata = json.loads(
            (backend_root / "skins" / "mate" / "actions" / "stock_save.json").read_text(encoding="utf-8")
        )
        assert geometry.read_text(encoding="utf-8") == "<svg/>"
        assert metadata["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/actions/document-save-symbolic.svg"
        )

    def test_repromotion_cleans_stale_unresolved_work_items(self, tmp_path):
        repo_root = tmp_path / "repo"
        backend_root = repo_root / "src" / "icons_backend"
        source_svg = (
            repo_root
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "actions"
            / "document-save-symbolic.svg"
        )
        source_svg.parent.mkdir(parents=True)
        source_svg.write_text("<svg/>", encoding="utf-8")

        unresolved_registry = [
            {
                "semantic_id": "icon/actions/document-save",
                "style_skin": "mate",
                "category": "actions",
                "installed_outputs": [
                    "icons/Synthesis-Dark-Icons/16x16/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/22x22/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/24x24/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/32x32/actions/document-save.png",
                    "icons/Synthesis-Dark-Icons/48x48/actions/document-save.png",
                ],
                "installed_output_count": 5,
                "authoritative_svg_candidates": [],
                "has_authoritative_svg": False,
            },
        ]
        resolved_registry = [
            {
                **unresolved_registry[0],
                "authoritative_svg_candidates": [
                    "icons/Synthesis-Dark-Icons/scalable/actions/document-save-symbolic.svg"
                ],
                "has_authoritative_svg": True,
            },
        ]

        pib.promote_svg_backed_icons(
            unresolved_registry,
            backend_root,
            repo_root,
            min_seed_outputs=99,
        )
        stale_path = (
            backend_root / "registry" / "unresolved" / "mate" / "actions" / "document-save.json"
        )
        assert stale_path.exists()

        pib.promote_svg_backed_icons(
            resolved_registry,
            backend_root,
            repo_root,
            min_seed_outputs=99,
        )
        assert not stale_path.exists()
