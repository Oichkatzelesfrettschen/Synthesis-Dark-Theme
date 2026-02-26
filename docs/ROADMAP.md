# Synthesis-Dark Strategic Roadmap

**Objective:** Establish `Synthesis-Dark` as the singular, harmonized source of truth for the
system-wide aesthetic, merging the best elements of Synthesis, Dracula, and Catppuccin into a
granular, high-quality infrastructure.

> **Status tracking:** This file is the single source of truth for project status.
> TASKS.md, TODO.md, and MIGRATION_STATUS.md are historical snapshots; see this file for current state.

---

## Phase 0: Foundation & Safety (Complete)

- [x] Create `.gitignore` and `.editorconfig`
- [x] Defang Gulpfile.js (remove gsettings desktop-mutation calls)
- [x] Defang package.json (remove `git push` in build script)
- [x] Fix bare-except clauses in `src/scripts/transform_colors.py`
- [x] Add GTK2 missing-source warning to Makefile
- [x] Create initial git commit

## Phase 1: Dead Code Elimination (Complete)

- [x] Delete dead Gulp pipeline (Gulpfile.js, package.json, package-lock.json)
- [x] Delete stale upstream docs (INSTALL.original.md, README.original.md)
- [x] Merge both `transform_colors.py` versions into single canonical `src/scripts/transform_colors.py`
  (full hue-family mapping + repo-scan mode; root copy deleted)
- [x] Remove Node.js/npm from requirements.md; add sassc, python-pillow, xcursorgen
- [x] Fix docs/STANDARDS.md naming convention (remove inaccurate `1_` prefix rule)

## Phase 2: Build System Unification (Complete)

- [x] Single Makefile as orchestrator with `scss`, `xfwm4`, `cursors`, `wm-assets`, `check-deps`, `lint` targets
- [x] `make scss`: sassc compiles gtk-3.20, gtk-4.0, gnome-shell, cinnamon
- [x] `make xfwm4`: integrates `xfwm4/render-assets.sh`
- [x] `make cursors`: integrates `kde/cursors/build.sh`
- [x] `make wm-assets`: new POSIX sh script (`src/scripts/render_wm_controls.sh`) replaces Fish script
- [x] `make check-deps`: validates all prerequisites
- [x] Fix `xfwm4/render-assets.sh`: replace Dracula theme name with Synthesis-Dark

## Phase 3: Color System Canonicalization (Complete)

- [x] Create `src/colors.json`: single canonical color definition with hex values, semantic roles, WCAG ratios
- [x] Reconcile selection color: gtk-3.0 pink `#ff79c6` replaced by indigo-mauve centroid `#b9a4fa` (H=255)
- [x] Document adjusted cyan `#72BFD0` in gnome-shell and cinnamon (canonical: `src/colors.json`)
- [x] Fix gnome-shell `$teal`: was wrongly aliased to purple `#bd93f9`; corrected to `#72BFD0`
- [x] Document metacity legacy `#fc2` yellow button with comment
- [x] Reconcile COLORSCHEME.md vs COLOR-STRATEGY.md: relationship note added; both reference `src/colors.json`
- [x] Fix COLOR-STRATEGY.md paths: replaced `~/` home paths with repo-relative paths
- [x] Extend `transform_colors.py`: add `--palette src/colors.json` flag

## Phase 4: Documentation Reconciliation (Complete)

- [x] Fix USAGE.md: `~/Github/Synthesis-Dark/` -> `~/Github/Synthesis-Dark-Theme/`
- [x] Fix USAGE.md maintenance command: `./src/build.sh` (non-existent) -> `make all`
- [x] Fix ROADMAP.md: remove false claim that `src/build.sh` was finalized (it does not exist)
- [x] Consolidate status trackers: this file is now the single source of truth
- [x] Fix MIGRATION_STATUS.md path: `~/Github/Synthesis-Dark` -> `~/Github/Synthesis-Dark-Theme`
- [x] Update requirements.md: remove Node.js/npm, add sassc, python-pillow, xcursorgen
- [x] Fix README.md credits placeholder "[Your Name/Agent]"
- [x] Create CHANGELOG.md with v2.0.0 entry
- [x] Fix docs/PKGBUILD.md: document synthesis-dark-marco-theme package
- [x] Create upstream/MANIFEST.md

## Phase 5: Test Infrastructure (Planned)

- [ ] Add `[project]` section to `pyproject.toml` with name, version, dependencies
- [ ] Write transform_color() unit tests
- [ ] Write CSS validation tests
- [ ] Write SVG well-formedness tests
- [ ] Write color consistency tests (SCSS hex vs src/colors.json)
- [ ] Write PKGBUILD lint test using `namcap`
- [ ] Write build reproducibility test
- [ ] Harden `accessibility_audit.py` with `--fail-below` and non-zero exit
- [ ] Complete colorblind validation checklist

## Phase 6: Package System Hardening (Planned)

- [ ] Fix PKGBUILD `build()`: change `make icons` to `make build`
- [ ] Remove unused makedepends: potrace, svgo
- [ ] Add sassc to makedepends
- [ ] Add xcursorgen to makedepends
- [ ] Rename KDE Aurorae from Dracula to Synthesis-Dark (~25 files)
- [ ] Reconcile index.theme IconTheme name vs PKGBUILD install name
- [ ] Test PKGBUILD in clean chroot
- [ ] Add `.install` file with post-install checks

## Phase 7: Quality Enforcement (Planned)

- [ ] Create `.pre-commit-config.yaml`
- [ ] Fix `xfwm4/render-assets.sh` shellcheck violations
- [ ] Fix `kde/cursors/build.sh` shellcheck violations
- [ ] Upgrade accessibility audit to enforce WCAG AA as `make audit`
- [ ] Create `.github/workflows/ci.yml`
- [ ] Fix `render_engine.py` single-file path error

## Phase 8: Release Engineering (Planned)

- [ ] Tag v2.0.0
- [ ] Finalize CHANGELOG.md
- [ ] Create CONTRIBUTING.md
- [ ] Create AUR docs and .SRCINFO
- [ ] Update README.md with screenshots and install methods
- [ ] Organize extras/
- [ ] Clean upstream/
- [ ] Final QA: full build, all tests, clean chroot install

---

**AD ASTRA PER MATHEMATICA ET SCIENTIAM**
