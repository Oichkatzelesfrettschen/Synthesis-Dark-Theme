# Upstream Reference Manifest

## Cleaned Directories (2024-12-24)

The following directories were removed during release cleanup:

### wallpapers/ (entire directory removed)
#### wallpapers/Dracula-repo/ (178MB)
- Full clone of Dracula wallpaper repository
- Contained: first-collection/, second-collection/, multiple PNG wallpapers
- Source: https://github.com/dracula/wallpaper

#### wallpapers/Dracula/ (156KB)
- Broken symlinks to user's local Pictures folder
- Not portable or useful for distribution

### themes/Dracula-Backup/ (18MB)
- Complete backup of original Dracula GTK theme
- Contained: gtk-2.0, gtk-3.0, gtk-3.20, gtk-4.0, cinnamon, gnome-shell, metacity-1, xfwm4, kde, unity
- Source: https://github.com/dracula/gtk

### themes/Ant-Dracula-Bak/ (276KB)
- Backup of Ant-Dracula theme variant
- Source: Community derivative

## Retained Directories

| Directory | Status | Purpose |
|-----------|--------|---------|
| `patches/` | Reference | Color transformation patches and diffs applied to main tree |
| `pkgbuilds/` | Reference | Arch Linux PKGBUILD templates (active PKGBUILD is in repo root) |
| `dotfiles_config/` | Reference | Reference dotfile configurations (btop, fastfetch) |
| `extras/` | Reference | Additional theme components (catppuccin color references) |
| `local_share/` | Reference | Desktop entries and application data templates |
| `local_config/` | Reference | Config file templates for system integration |
| `eggwm/` | Reference | EggWM window manager theme (upstream reference only) |
| `plank/` | Reference | Plank dock theme (upstream reference only) |

**Key distinction:**
- **Merged**: Content was integrated into the main repository tree (e.g., color transforms)
- **Reference**: Kept for reference only; not part of the main build pipeline

## Restoration

To restore upstream references, clone the original repositories:
```bash
git clone https://github.com/dracula/gtk themes/Dracula-Backup
git clone https://github.com/dracula/wallpaper wallpapers/Dracula-repo
```
