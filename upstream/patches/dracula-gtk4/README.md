# Dracula GTK4 Compatibility Patches

**Collection:** GTK4 CSS compatibility fixes for Dracula theme v4.0.0  
**Base Theme:** dracula-gtk-theme (official Arch package)  
**Date Created:** 2025-11-12  
**Status:** Production ready

---

## Overview

This patch series fixes GTK4 CSS compatibility issues in the official Dracula GTK theme while preserving the original aesthetic across all GTK versions (2.0, 3.0, 3.20, 4.0).

### Issues Fixed

| Patch | Issue | Severity | Impact |
|-------|-------|----------|--------|
| 0001-fix-gtk4-height-property.patch | Bare `height:` property (line 5683) | CRITICAL | GTK4 CSS parser warning |

### Scope

- **Total patches:** 1 (critical fix)
- **Lines affected:** ~7 (1 CSS rule change)
- **Risk level:** VERY LOW
- **Testing required:** gtk4-widget-factory, Nautilus

---

## Patch Details

### 0001-fix-gtk4-height-property.patch

**Problem:**
```css
.nautilus-window .path-buttons-box, .nautilus-window #NautilusPathBar {
  background: transparent;
  height: 20px;  /* ← NOT ALLOWED IN GTK4 */
  margin-top: 7px;
  margin-bottom: 7px;
}
```

GTK4 CSS parser rejects bare `height:` properties. Only `min-height`, `max-height`, or computed `height` values are allowed.

**Solution:**
```css
.nautilus-window .path-buttons-box, .nautilus-window #NautilusPathBar {
  background: transparent;
  min-height: 20px;  /* ← GTK4 compatible */
  margin-top: 7px;
  margin-bottom: 7px;
}
```

**Why this works:**
- `min-height` is the standard GTK4 approach for widget sizing
- Allows natural growth if content requires more space
- Eliminates CSS parser warning
- Maintains visual appearance

**Components affected:**
- Nautilus path buttons box
- Nautilus path bar

---

## Future Patches (Phase 2)

The following issues are identified but not critical. Future patches may address:

1. **Deprecated color functions** (21 occurrences)
   - `shade()`, `alpha()`, `mix()`, `lighter()`, `darker()`
   - Removal planned for GTK5
   - Current: Still functional, emit warnings
   - Solution: Migrate to standard CSS `calc()` and `color-mix()`

---

## Application Instructions

### Automatic (via PKGBUILD)

The patches are applied automatically during package build:

```bash
cd ~/pkgbuilds/dracula-gtk-theme-gtk4-compat
makepkg -si
```

### Manual Application

To apply patches manually to a Dracula theme source:

```bash
# Download Dracula theme source
git clone https://github.com/dracula/gtk.git dracula-gtk
cd dracula-gtk

# Apply patches in order
patch -p1 < /path/to/0001-fix-gtk4-height-property.patch

# Verify successful application
grep "min-height: 20px;" gtk-4.0/gtk.css
```

### Verify Patch Application

```bash
# Check if patch was applied
grep -n "min-height: 20px;" /usr/share/themes/Dracula/gtk-4.0/gtk.css

# Expected output: line 5683 contains min-height: 20px;
```

---

## Testing After Application

### Quick Test
```bash
# Test GTK4 CSS parsing
gtk4-widget-factory
# Look for CSS warnings in terminal - should be none

# Test Nautilus (specific to this patch)
nautilus
# Path buttons should display correctly
```

### Comprehensive Test
```bash
# Check for CSS warnings
gtk4-widget-factory 2>&1 | grep -i "css\|error\|warning"

# Check system logs
journalctl --since "5 min ago" | grep -i "gtk.*css\|css.*error"

# Expected: No warnings related to "height" or "css parser"
```

### Color Consistency Check
```bash
# Compare colors with GTK3 version
# Launch same app in GTK3 and GTK4 context and visually compare

# Verify dark/light variants work
GTK_THEME=Dracula gtk4-widget-factory
GTK_THEME=Dracula:dark gtk4-widget-factory  # If dark variant exists
```

---

## File Structure

```
/home/eirikr/dotfiles/patches/dracula-gtk4/
├── gtk.css.orig                           # Original file (for reference)
├── gtk.css.fixed                          # Patched version
├── 0001-fix-gtk4-height-property.patch    # Unified diff patch
├── SERIES                                 # Patch application order
└── README.md                              # This file
```

---

## Maintenance Guidelines

### Before Updating Dracula Theme

1. **Check upstream for fixes**
   ```bash
   # Visit: https://github.com/dracula/gtk/releases
   # Check if new versions include GTK4 fixes
   ```

2. **If updating, re-apply patches**
   ```bash
   cd ~/pkgbuilds/dracula-gtk-theme-gtk4-compat
   # Update PKGBUILD with new version
   updpkgsums
   makepkg -si
   ```

3. **Verify no new issues**
   ```bash
   gtk4-widget-factory 2>&1 | grep -i "error\|warning"
   ```

### Future Work (Phase 2)

When migrating deprecated color functions:

1. Research standard CSS `calc()` and `color-mix()` syntax
2. Create new patches for each function family
3. Number them: `0002-migrate-shade-functions.patch`, etc.
4. Update SERIES file
5. Test extensively with color-dependent widgets

---

## References

### GTK4 Documentation
- [GTK4 CSS Properties](https://docs.gtk.org/gtk4/css-properties.html)
- [GTK4 Migration Guide](https://docs.gtk.org/gtk4/migrating-3to4.html)
- [GTK4 CSS Overview](https://docs.gtk.org/gtk4/css-overview.html)

### Theme Resources
- [Dracula Theme Official](https://github.com/dracula/gtk)
- [Dracula Theme Website](https://draculatheme.com/gtk)

### Related Issues
- [GitHub Issue #110: GTK4 Support Request](https://github.com/dracula/gtk/issues/110)

---

## Known Limitations

### libadwaita Apps
- GNOME 42+ apps using libadwaita may not fully respect custom themes
- Workaround: Use Gradience tool or GTK_THEME environment variable

### Dark/Light Variants
- If Dracula provides light variant, verify it's also patched
- Current patch applies to standard (dark) theme

### Version Compatibility
- Patches tested with: dracula-gtk-theme v4.0.0
- Should work with nearby versions (4.0.x)
- Test before applying to significantly different versions

---

## Troubleshooting

### Patch Application Fails

**Error:** `patch: **** malformed patch`

**Solution:**
- Verify file line endings (should be LF, not CRLF)
- Check patch file path is correct
- Ensure you're in the theme source root directory

### CSS Still Shows Warnings

**Error:** Terminal shows "No property named 'height'" warnings

**Solution:**
- Verify patch was applied: `grep "min-height: 20px;" gtk-4.0/gtk.css`
- Check line 5683 specifically for the change
- May need to clear GTK theme cache: `rm -rf ~/.cache/gtk-4.0`
- Restart GTK4 application

### Widgets Display Incorrectly

**Error:** Nautilus path buttons appear wrong

**Solution:**
- Verify min-height value is correct (20px)
- Check if other CSS in that selector was modified
- Compare with original gtk.css.orig
- Test with gtk4-widget-factory

---

## Version Control

These patches are tracked in:
- Repository: `~/dotfiles`
- Directory: `patches/dracula-gtk4/`
- Git status: Included in dotfiles version control

### Commit History

```
commit: Add Dracula GTK4 patches and PKGBUILD
- Fix critical height: property issue (line 5683)
- Create modular patch system for future updates
- Include comprehensive documentation
- Ready for maintenance and future enhancements
```

---

## Contributing

To improve these patches:

1. **Report issues:** Document CSS warnings with full output
2. **Test patches:** Verify across multiple GTK4 apps
3. **Propose improvements:** Submit via issue tracker
4. **Maintain compatibility:** Ensure GTK2/3 remain unaffected

---

**Last Updated:** 2025-11-12  
**Maintained By:** Automated patch system  
**Status:** ✅ Production Ready
