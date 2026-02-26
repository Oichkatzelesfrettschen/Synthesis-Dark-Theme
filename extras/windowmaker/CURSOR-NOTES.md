# WindowMaker Cursor Configuration

## Overview

WindowMaker uses the X11 cursor infrastructure rather than its own cursor system.
This means the accessible cursor configured for this dotfiles repository
(Bibata-Modern-Ice) automatically applies to WindowMaker sessions.

## How It Works

The cursor theme is set via:
1. `~/.icons/default/index.theme` - Sets default X11 cursor theme
2. X resources (`.Xresources`) - Can set cursor size

WindowMaker reads these X11 defaults at session startup.

## Accessibility Features

The **Bibata-Modern-Ice** cursor provides:
- **Colorblind-friendly**: White/black high-contrast design
- **Visible to all color vision types**:
  - Deuteranopia (red-green)
  - Protanopia (red-green)
  - Tritanopia (blue-yellow)
  - Monochromacy (complete colorblindness)
- **Cognitive accessibility**: Clean, modern, uncluttered design
- **Size**: 48px (2x default) for visibility without being intrusive

## Manual Application (if needed)

If the cursor doesn't appear correctly in WindowMaker:

```bash
# Ensure ~/.icons/default/index.theme exists
mkdir -p ~/.icons/default
ln -sf ~/dotfiles/config/icons/default/index.theme ~/.icons/default/

# Set X resources (add to .Xresources)
echo 'Xcursor.theme: Bibata-Modern-Ice' >> ~/.Xresources
echo 'Xcursor.size: 48' >> ~/.Xresources
xrdb -merge ~/.Xresources

# Restart WindowMaker
wmaker --restart
```

## Verification

To verify the cursor theme is active:
```bash
# Check current X cursor theme
xrdb -query | grep Xcursor

# Expected output:
# Xcursor.theme: Bibata-Modern-Ice
# Xcursor.size:  48
```

## Desktop Support

This cursor configuration is consistent across:
- **Cinnamon** (primary desktop)
- **MATE**
- **WindowMaker**
- **Any X11-based window manager**

## Files

- `/home/eirikr/dotfiles/config/icons/default/index.theme` - Default cursor theme
- `/home/eirikr/dotfiles/config/xorg/.Xresources` - X resources including cursor
