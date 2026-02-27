# Changelog

All notable changes to Synthesis-Dark are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [2.1.0] - 2026-02-27

### Summary

Icon theme expansion: Tela Circle app icons imported as a git submodule, icon
directories renamed from MATE-prefixed names to Synthesis-Dark-Icons/Cursors,
and a five-variant color system (Default, Purple, Teal, Mauve, Blue) added with
a POSIX sh generation script and full Makefile integration.

### Added

- `upstream/tela-circle/` git submodule (vinceliuice/Tela-circle-icon-theme, GPL-3.0-or-later)
  providing ~1600 scalable app, mimetype, device, and folder icons
- `src/scripts/generate_variants.sh`: POSIX sh script to generate icon color variants
  from Tela Circle source via sed color substitution
- `Makefile` targets: `icon-variants`, `icon-variant-<NAME>` for variant generation
- Five icon color variants (generated at build time, not committed):
  - `Synthesis-Dark-Icons-Purple` (#bd93f9, Dracula purple)
  - `Synthesis-Dark-Icons-Teal` (#17b169, CachyOS teal)
  - `Synthesis-Dark-Icons-Mauve` (#cba6f7, Catppuccin mauve)
  - `Synthesis-Dark-Icons-Blue` (#b4befe, lavender)
- `src/colors.json` `icon_variants` section with all variant color definitions
- `docs/ICONS.md`: icon theme structure, variant system, Tela Circle attribution,
  instructions for adding new variants
- `tests/test_icon_variants.sh`: POSIX sh test suite for variant generation
  (structure, index.theme correctness, color presence/absence checks)
- `PKGBUILD`: new `synthesis-dark-icons-variants` split package

### Changed

- `icons/MATE-Synthesis-Dark/` renamed to `icons/Synthesis-Dark-Icons/`
- `icons/MATE-Synthesis-Dark-Cursors/` renamed to `icons/Synthesis-Dark-Cursors/`
- `icons/Synthesis-Dark-Cursors/index.theme` Name field updated
- `index.theme` (root) IconTheme/CursorTheme fields updated to new names
- `Makefile` ICON_DIR, CURSOR_DIR, install target, clean target updated
- `PKGBUILD` icon/cursor install paths updated; pkgver bumped to 2.1.0
- All docs updated to remove MATE-prefixed icon theme references
- `synthesis-dark-suite.install` icon path and gsettings command updated
- `generate_variants.sh` added to shellcheck lint target

### Fixed

- `src/scripts/generate_variants.sh`: POSIX sh subshell variable collision bug --
  `apply_color` inner variables renamed with `_ac_` prefix to prevent overwriting
  caller's `dest` variable across loop iterations

---

## [2.0.0] - 2026-02-26

### Summary

Complete consolidation of three upstream theme families (Ant-Dracula, Synthesis,
Catppuccin) into a unified, debt-free repository with a single authoritative build
system, canonical color definitions, and automated testing infrastructure.

### Added

- `src/colors.json`: single canonical color definition file with hex values, semantic
  roles, WCAG contrast ratios, and variant rationale for all palette colors
- `src/scripts/render_wm_controls.sh`: POSIX sh replacement for removed Fish script
- `.gitignore` and `.editorconfig` for project hygiene
- `CHANGELOG.md` (this file)
- `Makefile` targets: `scss`, `xfwm4`, `cursors`, `wm-assets`, `check-deps`, `lint`, `audit`
- `--palette` flag for `src/scripts/transform_colors.py` to load from `src/colors.json`
- Test infrastructure: `tests/` with unit tests (transform_colors), CSS/SVG validation,
  color consistency checks, PKGBUILD lint, and reproducibility tests (557 tests total)
- `.pre-commit-config.yaml` with ruff, shellcheck, trailing-whitespace hooks
- `.github/workflows/ci.yml` with lint, test, pkgbuild, and accessibility audit jobs
- `synthesis-dark-suite.install` with post-install/upgrade/pre-remove hooks
- Full KDE suite: Aurorae, color-schemes, cursors, SDDM, Plasma desktop, Kvantum themes
  renamed from Dracula to Synthesis-Dark across all ~325 files

### Changed

- **Selection color**: gtk-3.0 `#ff79c6` (Dracula pink) replaced by `#b9a4fa`
  (indigo-mauve-purple centroid, H=255 S=0.90 L=0.81) to harmonize with gtk-3.20/4.0
- **GNOME Shell `$teal`**: fixed from incorrect purple alias (`#bd93f9`) to `#72BFD0`
- **Build system**: Makefile is now the single orchestrator; Gulp pipeline removed
- **`src/scripts/transform_colors.py`**: merged 549-line root copy (full hue-family
  mapping, per-family HSL transforms) with 94-line repo-scanning version; single file;
  bare-except clauses replaced with proper error handling
- `xfwm4/render-assets.sh`: replaced Dracula theme name with Synthesis-Dark
- `requirements.md`: removed Node.js/npm; added sassc, python-pillow, xcursorgen
- All docs: corrected path references (`~/Github/Synthesis-Dark` -> repo-relative)

### Removed

- `Gulpfile.js`: dead pipeline from Ant-Dracula upstream (referenced wrong theme names,
  mutated live desktop via gsettings)
- `package.json` / `package-lock.json`: dead npm configuration (4373 lines of 2015-era locks)
- `INSTALL.original.md` / `README.original.md`: stale Dracula upstream documentation
- Root `transform_colors.py`: merged into `src/scripts/transform_colors.py`
- `src/wm_controls.fish`: replaced by POSIX sh equivalent

### Fixed

- `package.json` build script ran `git push` on build (dangerous side effect; removed)
- `Gulpfile.js` ran `gsettings` calls mutating the live desktop on every build (removed)
- GNOME Shell `$teal` was `#bd93f9` (purple) -- semantic mismatch corrected
- COLORSCHEME.md vs COLOR-STRATEGY.md apparent contradiction documented and resolved
- ROADMAP.md false claim that `src/build.sh` was finalized (script does not exist)
- USAGE.md wrong repo path and non-existent `./src/build.sh` maintenance command

---

## [1.0.0] - 2025

### Summary

Initial consolidation from Ant-Dracula, Synthesis, and Catppuccin upstream sources.
Established base repository structure with GTK2/3/4, Metacity, GNOME Shell, Cinnamon,
XFWM4, icon set, cursor theme, and extras (Tilix, Alacritty, btop).
