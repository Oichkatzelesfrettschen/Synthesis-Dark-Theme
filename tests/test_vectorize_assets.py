"""
Unit tests for src/scripts/vectorize_assets.py
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import vectorize_assets as va


class TestDiscoverPngs:
    def test_non_recursive_only_reads_top_level(self, tmp_path):
        top = tmp_path / "top.png"
        nested = tmp_path / "nested" / "inner.png"
        top.write_bytes(b"")
        nested.parent.mkdir()
        nested.write_bytes(b"")

        found = va.discover_pngs(tmp_path, recursive=False)

        assert found == [top]

    def test_recursive_reads_nested_paths(self, tmp_path):
        top = tmp_path / "top.png"
        nested = tmp_path / "nested" / "inner.png"
        top.write_bytes(b"")
        nested.parent.mkdir()
        nested.write_bytes(b"")

        found = va.discover_pngs(tmp_path, recursive=True)

        assert found == [nested, top]


class TestClassification:
    def test_thumbnail_assets_are_review_later_even_under_theme_dirs(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "metacity-1" / "thumbnail.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "reference_raster"
        assert entry["batch_priority"] == "review-later"

    def test_hidpi_assets_are_excluded(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "assets" / "widget@2.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "derived_hidpi"
        assert entry["batch_priority"] == "exclude-derived"

    def test_cursor_build_pngs_are_generated(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "kde" / "cursors" / "build" / "x1" / "default.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "generated_raster"
        assert entry["source_authority"] == "kde/cursors/src/cursors.svg"

    def test_icon_with_matching_scalable_svg_is_safe_batch(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "16x16" / "apps" / "firefox.png"
        svg = input_dir / "icons" / "Synthesis-Dark-Icons" / "scalable" / "apps" / "firefox.svg"
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["batch_priority"] == "safe-batch-generation"
        assert entry["style_skin"] == "tela"
        assert entry["semantic_id"] == "icon/apps/firefox"

    def test_icon_can_harvest_upstream_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "22" / "emblems" / "emblem-readonly.png"
        svg = input_dir / "upstream" / "tela-circle" / "src" / "22" / "emblems" / "emblem-readonly.svg"
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == "upstream/tela-circle/src/22/emblems/emblem-readonly.svg"

    def test_mate_icon_without_scalable_svg_is_reconciliation_work(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "16x16" / "actions" / "document-save.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "complex_icon_source"
        assert entry["batch_priority"] == "icon-family-reconciliation"
        assert entry["style_skin"] == "mate"

    def test_simple_ui_assets_are_non_icon_first(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "gtk-2.0" / "assets" / "button.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "simple_ui_source"
        assert entry["batch_priority"] == "non-icon-first"

    def test_metacity_assets_pick_up_new_authoritative_svg_targets(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "metacity-1" / "shade_focused_normal.png"
        svg = input_dir / "metacity-1" / "assets" / "shade_focused_normal.svg"
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == "metacity-1/assets/shade_focused_normal.svg"

    def test_kde_preview_raster_is_not_treated_as_source(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "kde" / "sddm" / "Synthesis-Dark" / "preview.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "reference_raster"
        assert entry["batch_priority"] == "review-later"

    def test_upstream_eggwm_buttons_are_reference_only(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "upstream" / "eggwm" / "dracula" / "images" / "exit_button.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "reference_raster"
        assert entry["batch_priority"] == "review-later"

    def test_gnome_shell_runtime_assets_are_promoted_to_simple_ui(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "gnome-shell" / "assets" / "ws-switch-arrow-up.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "simple_ui_source"
        assert entry["batch_priority"] == "non-icon-first"

    def test_upstream_eggwm_assets_are_reference_rasters(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "upstream" / "eggwm" / "dracula" / "images" / "exit_button.png"
        png.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "reference_raster"
        assert entry["batch_priority"] == "review-later"

    def test_icons_can_use_backend_geometry_as_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "16x16" / "actions" / "document-save.png"
        svg = input_dir / "src" / "icons_backend" / "geometry" / "actions" / "document-save.svg"
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == "src/icons_backend/geometry/actions/document-save.svg"

    def test_preferred_authority_override_beats_runtime_sibling_svg(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "gnome-shell" / "assets" / "ws-switch-arrow-up.png"
        sibling_svg = input_dir / "gnome-shell" / "assets" / "ws-switch-arrow-up.svg"
        wrapper_svg = input_dir / "src" / "raster_wrappers" / "gnome-shell" / "assets" / "ws-switch-arrow-up.svg"
        preferred = input_dir / "src" / "raster_wrappers" / "preferred-authorities.json"
        png.parent.mkdir(parents=True)
        sibling_svg.parent.mkdir(parents=True, exist_ok=True)
        wrapper_svg.parent.mkdir(parents=True, exist_ok=True)
        preferred.parent.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        sibling_svg.write_text("<svg native/>", encoding="utf-8")
        wrapper_svg.write_text("<svg wrapper/>", encoding="utf-8")
        preferred.write_text(
            '{"gnome-shell/assets/ws-switch-arrow-up.png": "src/raster_wrappers/gnome-shell/assets/ws-switch-arrow-up.svg"}\n',
            encoding="utf-8",
        )

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == "src/raster_wrappers/gnome-shell/assets/ws-switch-arrow-up.svg"

    def test_icon_alias_can_use_local_symbolic_svg_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "16x16" / "actions" / "stock_save.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "actions"
            / "document-save-symbolic.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["semantic_id"] == "icon/actions/stock_save"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/actions/document-save-symbolic.svg"
        )

    def test_icon_alias_normalizes_hyphen_and_underscore_in_symbolic_svg_names(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "16x16" / "actions" / "bookmark_add.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "actions"
            / "bookmark-add-symbolic.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/actions/bookmark-add-symbolic.svg"
        )

    def test_status_alias_can_use_dialog_symbolic_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "24x24" / "status" / "gtk-dialog-warning.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "status"
            / "dialog-warning-symbolic.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/status/dialog-warning-symbolic.svg"
        )

    def test_gtk_action_alias_can_use_document_symbolic_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "24x24" / "actions" / "gtk-save.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "actions"
            / "document-save-symbolic.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/actions/document-save-symbolic.svg"
        )

    def test_emblem_alias_can_use_upstream_tela_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "22" / "emblems" / "emblem-nowrite.png"
        svg = (
            input_dir
            / "upstream"
            / "tela-circle"
            / "src"
            / "22"
            / "emblems"
            / "emblem-readonly.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == "upstream/tela-circle/src/22/emblems/emblem-readonly.svg"

    def test_trash_alias_can_use_status_or_places_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "24x24" / "status" / "trashcan_full.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "status"
            / "user-trash-full-symbolic.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/status/user-trash-full-symbolic.svg"
        )

    def test_apps_alias_can_use_terminal_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "24x24" / "apps" / "gnome-terminal.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "apps"
            / "utilities-terminal.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/apps/utilities-terminal.svg"
        )

    def test_apps_alias_can_use_cross_category_color_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "24x24" / "apps" / "gcolor2.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "actions"
            / "color-select-symbolic.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/actions/color-select-symbolic.svg"
        )

    def test_devices_alias_can_use_harddisk_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "24x24" / "devices" / "gnome-dev-harddisk-usb.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "devices"
            / "drive-harddisk-usb.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/devices/drive-harddisk-usb.svg"
        )

    def test_places_alias_can_use_user_desktop_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = input_dir / "icons" / "Synthesis-Dark-Icons" / "24x24" / "places" / "desktop.png"
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "places"
            / "user-desktop.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/places/user-desktop.svg"
        )

    def test_mimetype_alias_can_strip_gnome_prefix(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "48x48"
            / "mimetypes"
            / "gnome-mime-application-vnd.ms-excel.png"
        )
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "mimetypes"
            / "application-vnd.ms-excel.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/mimetypes/application-vnd.ms-excel.svg"
        )

    def test_mimetype_alias_can_collapse_office_family_names(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "48x48"
            / "mimetypes"
            / "openofficeorg3-spreadsheet.png"
        )
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "mimetypes"
            / "x-office-spreadsheet.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/mimetypes/x-office-spreadsheet.svg"
        )

    def test_category_alias_can_use_sized_symbolic_authority(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "24x24"
            / "categories"
            / "package_network.png"
        )
        svg = (
            input_dir
            / "upstream"
            / "tela-circle"
            / "src"
            / "22"
            / "categories"
            / "applications-network-symbolic.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "upstream/tela-circle/src/22/categories/applications-network-symbolic.svg"
        )

    def test_mimetype_alias_can_map_gnome_legacy_office_names(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "48x48"
            / "mimetypes"
            / "gnome-mime-application-msword.png"
        )
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "mimetypes"
            / "x-office-document.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/mimetypes/x-office-document.svg"
        )

    def test_mimetype_alias_can_map_legacy_pgp_names(self, tmp_path):
        input_dir = tmp_path / "repo"
        output_dir = tmp_path / "out"
        png = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "48x48"
            / "mimetypes"
            / "application-pgp-encrypted.png"
        )
        svg = (
            input_dir
            / "icons"
            / "Synthesis-Dark-Icons"
            / "scalable"
            / "mimetypes"
            / "application-pgp.svg"
        )
        png.parent.mkdir(parents=True)
        svg.parent.mkdir(parents=True)
        output_dir.mkdir()
        png.write_bytes(b"")
        svg.write_text("<svg/>", encoding="utf-8")

        entry = va.classify_asset(input_dir, png.relative_to(input_dir), output_dir, False)

        assert entry["source_class"] == "already_has_authoritative_svg"
        assert entry["source_authority"] == (
            "icons/Synthesis-Dark-Icons/scalable/mimetypes/application-pgp.svg"
        )


class TestCanonicalOutputPaths:
    def test_xfwm_outputs_land_under_assets_directory(self, tmp_path):
        output_root = tmp_path / "repo"
        relative_png = Path("xfwm4/right-inactive.png")

        output_svg = va.canonical_output_svg_path(output_root, relative_png)

        assert output_svg == output_root / "xfwm4" / "assets" / "right-inactive.svg"

    def test_metacity_outputs_land_under_assets_directory(self, tmp_path):
        output_root = tmp_path / "repo"
        relative_png = Path("metacity-1/unshade_focused_pressed.png")

        output_svg = va.canonical_output_svg_path(output_root, relative_png)

        assert output_svg == output_root / "metacity-1" / "assets" / "unshade_focused_pressed.svg"


class TestSelectionAndReporting:
    def test_execution_candidates_default_to_simple_ui_only(self):
        manifest = [
            {"input_png": "a.png", "source_class": "simple_ui_source"},
            {"input_png": "b.png", "source_class": "complex_ui_source"},
            {"input_png": "c.png", "source_class": "complex_icon_source"},
        ]

        selected = va.select_execution_candidates(
            manifest,
            allow_complex_ui=False,
            allow_icon_raster=False,
        )

        assert [entry["input_png"] for entry in selected] == ["a.png"]

    def test_execution_candidates_can_expand(self):
        manifest = [
            {"input_png": "a.png", "source_class": "simple_ui_source"},
            {"input_png": "b.png", "source_class": "complex_ui_source"},
            {"input_png": "c.png", "source_class": "complex_icon_source"},
        ]

        selected = va.select_execution_candidates(
            manifest,
            allow_complex_ui=True,
            allow_icon_raster=True,
        )

        assert [entry["input_png"] for entry in selected] == ["a.png", "b.png", "c.png"]

    def test_report_mentions_cuda_state(self, tmp_path):
        manifest = [
            {
                "relative_png": "gtk-2.0/assets/button.png",
                "batch_priority": "non-icon-first",
                "source_class": "simple_ui_source",
                "style_skin": "n/a",
            },
            {
                "relative_png": "icons/Synthesis-Dark-Icons/16x16/actions/document-save.png",
                "batch_priority": "icon-family-reconciliation",
                "source_class": "complex_icon_source",
                "style_skin": "mate",
            },
        ]

        report = va.render_priority_report(
            manifest,
            tmp_path / "repo",
            tmp_path / "out",
            workers=6,
            cuda_info={
                "available": True,
                "backend": "opencv-cuda",
                "device_name": "RTX Test",
                "reason": "available",
            },
        )

        assert "RTX Test" in report
        assert "non-icon-first" in report
        assert "icon-family-reconciliation" in report

    def test_icon_registry_groups_outputs_by_semantic_id(self):
        manifest = [
            {
                "family": "icon",
                "semantic_id": "icon/apps/firefox",
                "style_skin": "tela",
                "relative_png": "icons/Synthesis-Dark-Icons/16x16/apps/firefox.png",
                "batch_priority": "safe-batch-generation",
                "source_class": "already_has_authoritative_svg",
                "source_authority": "icons/Synthesis-Dark-Icons/scalable/apps/firefox.svg",
            },
            {
                "family": "icon",
                "semantic_id": "icon/apps/firefox",
                "style_skin": "tela",
                "relative_png": "icons/Synthesis-Dark-Icons/32x32/apps/firefox.png",
                "batch_priority": "safe-batch-generation",
                "source_class": "already_has_authoritative_svg",
                "source_authority": "icons/Synthesis-Dark-Icons/scalable/apps/firefox.svg",
            },
        ]

        registry = va.build_icon_registry(manifest)

        assert len(registry) == 1
        assert registry[0]["semantic_id"] == "icon/apps/firefox"
        assert registry[0]["installed_output_count"] == 2
        assert registry[0]["has_authoritative_svg"] is True

    def test_icon_collision_report_counts_high_fanout_stems(self):
        manifest = [
            {
                "family": "icon",
                "semantic_id": "icon/actions/document-save",
                "style_skin": "mate",
                "relative_png": "icons/Synthesis-Dark-Icons/16x16/actions/document-save.png",
                "batch_priority": "icon-family-reconciliation",
                "source_class": "complex_icon_source",
                "source_authority": None,
            },
            {
                "family": "icon",
                "semantic_id": "icon/actions/document-save",
                "style_skin": "mate",
                "relative_png": "icons/Synthesis-Dark-Icons/32x32/actions/document-save.png",
                "batch_priority": "icon-family-reconciliation",
                "source_class": "complex_icon_source",
                "source_authority": None,
            },
        ]

        collisions = va.build_icon_stem_collisions(manifest)

        assert len(collisions) == 1
        assert collisions[0]["stem"] == "document-save"
        assert collisions[0]["installed_output_count"] == 2

    def test_icon_report_mentions_unique_semantic_ids(self):
        manifest = [
            {
                "family": "icon",
                "semantic_id": "icon/actions/document-save",
                "style_skin": "mate",
                "relative_png": "icons/Synthesis-Dark-Icons/16x16/actions/document-save.png",
                "batch_priority": "icon-family-reconciliation",
                "source_class": "complex_icon_source",
                "source_authority": None,
            }
        ]

        report = va.render_icon_reconciliation_report(manifest, va.build_icon_registry(manifest))

        assert "Unique icon semantic IDs" in report
        assert "document-save" in report
