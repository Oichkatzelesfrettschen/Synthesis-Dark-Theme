# Dracula GTK Theme with GTK4 Compatibility Patches

**Package:** `dracula-gtk-theme-gtk4-compat`  
**Version:** 4.0.0  
**Base:** Official Dracula GTK theme (https://github.com/dracula/gtk)  
**Status:** Production Ready (2025-11-12)

---

## Overview

This is a patched version of the official Dracula GTK theme v4.0.0 with critical GTK4 CSS compatibility fixes applied. It maintains 100% visual consistency with the original while fixing CSS parser warnings.

### What's Fixed

| Issue | Fix | Impact |
|-------|-----|--------|
| Bare `height:` property in Nautilus styling | Changed to `min-height:` | Eliminates GTK4 CSS parser warning |
| **Total changes** | 1 CSS rule | **Zero visual impact** |

### Compatibility

- ✅ **GTK 2.0** - Full support (gtkrc)
- ✅ **GTK 3.0** - Full support (CSS)
- ✅ **GTK 3.20** - Full support (CSS)
- ✅ **GTK 4.0** - Full support with patches (CSS)
- ✅ **GNOME/Cinnamon/XFCE/MATE/Unity** - Desktop environment support
- ⚠️ **libadwaita** - Limited (use Gradience for full customization)

---

## Installation

### From Package (Recommended)

```bash
# Build and install
cd ~/pkgbuilds/dracula-gtk-theme-gtk4-compat
makepkg -si

# OR if already built
sudo pacman -U *.pkg.tar.zst
```

### Activate Theme

**GNOME/MATE/XFCE:**
1. Open Settings → Appearance/Look & Feel
2. Select "Dracula" from GTK theme dropdown
3. Select "Dracula" from Icon theme dropdown

**Command line:**
```bash
# GTK3
gsettings set org.gnome.desktop.interface gtk-theme 'Dracula'
gsettings set org.gnome.desktop.interface icon-theme 'Dracula'

# GTK4 (if applicable)
gsettings set org.gnome.desktop.interface gtk-theme 'Dracula'
```

### Manual Installation

```bash
# Install to user themes
mkdir -p ~/.themes
cp -r ~/.local/share/Dracula ~/.themes/

# OR system-wide (requires sudo)
sudo cp -r ~/.local/share/Dracula /usr/share/themes/
```

---

## Verification

### Verify Installation

```bash
# Check theme installed
ls /usr/share/themes/Dracula/

# Expected: assets/ cinnamon/ gnome-shell/ gtk-2.0/ gtk-3.0/ gtk-3.20/ gtk-4.0/ ...
```

### Verify Patches Applied

```bash
# Check critical fix
grep "min-height: 20px;" /usr/share/themes/Dracula/gtk-4.0/gtk.css

# Expected output: match at line 5683
```

### Test GTK4 Rendering

```bash
# Test without CSS warnings
gtk4-widget-factory 2>&1 | grep -i "css\|error\|warning"

# Expected: No warnings containing "height" or "css parser"
```

### Test Nautilus

```bash
# Test Nautilus (specific to this patch)
nautilus &

# Verify path buttons display correctly
# Should see path bar with proper height
```

---

## Building from Source

### Prerequisites

```bash
pacman -S base-devel git  # Standard build tools
# OR
yay -S base-devel git
```

### Build Steps

```bash
# Clone build directory
cd ~/pkgbuilds/dracula-gtk-theme-gtk4-compat

# Validate PKGBUILD
namcap PKGBUILD

# Generate checksums (first time only)
updpkgsums

# Build package
makepkg -f

# Validate output
namcap *.pkg.tar.zst

# Install
makepkg -si
# OR
sudo pacman -U dracula-gtk-theme-gtk4-compat-*.pkg.tar.zst
```

### Clean Build

```bash
# Remove build artifacts
makepkg --clean

# Clean and rebuild
makepkg -f
```

---

## Configuration

### Theme Customization

To modify colors, fonts, or other theme properties:

1. **User-specific overrides:**
   ```bash
   mkdir -p ~/.config/gtk-4.0
   cat > ~/.config/gtk-4.0/gtk.css << 'EOF'
   /* Override theme colors here */
   :root {
     --accent-color: #bd93f9;  /* Dracula purple */
   }
   EOF
   ```

2. **Using Gradience (recommended):**
   ```bash
   yay -S gradience
   # Then use Gradience GUI to adjust colors
   ```

---

## Troubleshooting

### GTK4 CSS Warnings Still Appear

**Symptom:** Still see "No property named 'height'" warnings

**Solution:**
```bash
# Clear GTK cache
rm -rf ~/.cache/gtk-4.0

# Verify patch applied
grep "min-height: 20px;" /usr/share/themes/Dracula/gtk-4.0/gtk.css

# Reinstall theme
sudo pacman -R dracula-gtk-theme-gtk4-compat
makepkg -si
```

### Theme Not Activating

**Symptom:** Theme dropdown empty or theme doesn't apply

**Solution:**
```bash
# Check theme directory
ls -la /usr/share/themes/Dracula/index.theme

# Rebuild theme cache
sudo gtk-update-icon-caches /usr/share/icons/Dracula/

# Restart GTK4 applications
killall -9 gtk4-widget-factory  # or other GTK4 app
```

### Colors Look Wrong

**Symptom:** Colors don't match expected Dracula palette

**Solution:**
```bash
# Verify GTK version is correct
gtk4-widget-factory --version

# Check if libadwaita is overriding (GNOME 42+)
# Use Gradience for libadwaita apps

# Compare with GTK3 rendering
GTK_THEME=Dracula gtk3-widget-factory
GTK_THEME=Dracula gtk4-widget-factory
```

---

## Updates

### Checking for Official Updates

```bash
# Visit official repository
# https://github.com/dracula/gtk/releases

# If new version includes GTK4 fixes, may not need this patch
```

### Updating This Package

```bash
# Update PKGBUILD version
nano ~/pkgbuilds/dracula-gtk-theme-gtk4-compat/PKGBUILD
# Change: pkgver=X.Y.Z

# Regenerate checksums
cd ~/pkgbuilds/dracula-gtk-theme-gtk4-compat
updpkgsums

# Rebuild
makepkg -si
```

---

## Maintenance

### Monthly Tasks
- [ ] Check for official Dracula updates
- [ ] Verify theme still applies without warnings
- [ ] Test with new GTK4 applications

### Quarterly Tasks
- [ ] Review GTK5 preparation progress
- [ ] Check for new CSS properties/standards
- [ ] Test with multiple desktop environments

---

## Related Documentation

- **Patch Details:** See `~/dotfiles/patches/dracula-gtk4/README.md`
- **Strategy Document:** See `~/dotfiles/DRACULA-GTK4-PATCH-STRATEGY.md`
- **Technical Report:** See `~/MATE-SESSION-DIAGNOSTIC-ANALYSIS.md`

---

## Support

### Official Resources
- [Dracula Theme](https://draculatheme.com/gtk)
- [GitHub Repository](https://github.com/dracula/gtk)
- [GTK Documentation](https://docs.gtk.org/)

### Arch Linux Resources
- [GTK ArchWiki](https://wiki.archlinux.org/title/GTK)
- [AUR: dracula-gtk-theme](https://aur.archlinux.org/packages/dracula-gtk-theme)

---

## License

This package inherits the GPL-3.0 license from the official Dracula GTK theme.

Patches are provided under the same license.

---

**Last Updated:** 2025-11-12  
**Maintainer:** Automated GTK4 compatibility system  
**Status:** ✅ Production Ready
