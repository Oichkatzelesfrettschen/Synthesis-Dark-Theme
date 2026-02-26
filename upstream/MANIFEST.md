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

- patches/ - Color transformation patches and diffs
- pkgbuilds/ - Arch Linux packaging templates
- dotfiles_config/ - Reference dotfile configurations
- extras/ - Additional theme components (catppuccin, etc.)
- local_share/ - Desktop entries and application data
- local_config/ - Config file templates
- eggwm/ - Window manager theme
- plank/ - Dock theme

## Restoration

To restore upstream references, clone the original repositories:
```bash
git clone https://github.com/dracula/gtk themes/Dracula-Backup
git clone https://github.com/dracula/wallpaper wallpapers/Dracula-repo
```
