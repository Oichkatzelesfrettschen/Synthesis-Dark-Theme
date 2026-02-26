# AUR Submission Guide

## Overview

Synthesis-Dark is distributed via a split PKGBUILD targeting the Arch User Repository (AUR).
The base package is `synthesis-dark-suite` which produces five installable packages.

## Packages

| Package | Contents |
|---------|----------|
| `synthesis-dark-gtk-theme` | GTK2/3/4, Metacity, GNOME Shell, Cinnamon, XFWM4 |
| `synthesis-dark-marco-theme` | Marco/Metacity window decorations |
| `synthesis-dark-icons` | MATE-Synthesis-Dark icon theme |
| `synthesis-dark-cursors` | MATE-Synthesis-Dark-Cursors cursor theme |
| `synthesis-dark-tilix` | Tilix terminal color scheme |

## Local Test Build

Before submitting to AUR, test in a clean chroot:

```sh
# Install devtools if not available
sudo pacman -S devtools

# Build in clean chroot (Arch x86_64)
extra-x86_64-build

# Or with plain makepkg for quick iteration
makepkg -si --cleanbuild
```

## Generating .SRCINFO

The `.SRCINFO` file must be regenerated whenever PKGBUILD changes:

```sh
makepkg --printsrcinfo > .SRCINFO
```

The current `.SRCINFO` is committed in the repository root. Regenerate it before
any AUR submission.

## AUR Submission Checklist

Before submitting or updating the AUR package:

1. `namcap PKGBUILD` -- no errors or warnings
2. `namcap synthesis-dark-gtk-theme-*.pkg.tar.zst` -- verify all installed packages
3. Build succeeds in clean chroot (`extra-x86_64-build`)
4. All packages install and uninstall cleanly
5. Theme applies correctly in target DEs (MATE, GNOME, XFCE)
6. `.SRCINFO` is up to date (`makepkg --printsrcinfo > .SRCINFO`)
7. Version tag matches `pkgver` in PKGBUILD

## AUR Workflow

```sh
# Clone the AUR package (first submission: create via web UI at aur.archlinux.org)
git clone ssh://aur@aur.archlinux.org/synthesis-dark-suite.git aur-pkg
cd aur-pkg

# Copy PKGBUILD and .SRCINFO
cp /path/to/Synthesis-Dark-Theme/PKGBUILD .
cp /path/to/Synthesis-Dark-Theme/.SRCINFO .

# Commit and push to AUR
git add PKGBUILD .SRCINFO
git commit -m "Update to 2.0.0"
git push
```

## Dependency Notes

- `gtk-engine-murrine` is required at runtime for GTK2 rendering
- `hicolor-icon-theme` is required for the icon theme install path
- `sassc` is a build-only dependency (SCSS compilation)
- `xcursorgen` is a build-only dependency (cursor generation)
- `inkscape` + `optipng` are build dependencies (asset rendering)
- `python-pillow` is a build dependency (color transformation)
