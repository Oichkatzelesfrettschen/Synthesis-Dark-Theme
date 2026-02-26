# Changelog

All notable changes to Synthesis-Dark are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [2.0.0] - 2026-02

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
- `Makefile` targets: `scss`, `xfwm4`, `cursors`, `wm-assets`, `check-deps`, `lint`
- `--palette` flag for `src/scripts/transform_colors.py` to load from `src/colors.json`

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
