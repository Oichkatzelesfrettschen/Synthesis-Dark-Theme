# Synthesis-Dark Active Tasks

**Priority Level: Critical (Icon Harmonization)**

- [x] **Locate Tools**: Found `transform_colors.py`, moved to `src/scripts`.
- [ ] **Audit Colors**:
    - Checked `folder-symbolic.svg` -> `#bebebe` (Expected for symbolic).
    - **Action**: Check `48x48/places/folder.png` for Teal vs Indigo-Gray.
    - Expected: `#8e95b8`
    - To Fix: Any incidence of standard Dracula/Synthesis Teal/Purple if it clashes.
- [ ] **Analyze Distribution**: Count files by type (SVG vs PNG) to determine scaling strategy.
- [ ] **Fix & Render**:
    - Update `render-assets.sh` to include icon rendering if sources exist.
    - Run color transformation batch.

**Secondary Tasks (Queue)**
- [ ] Merge `upstream/dotfiles_config/synthesis-dark.btop` into `extras/btop`.
- [ ] Merge `upstream/extras/catppuccin` into a new `extras/palettes` structure if useful for cross-reference.