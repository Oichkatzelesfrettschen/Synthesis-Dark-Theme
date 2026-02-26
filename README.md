# Synthesis-Dark

**Synthesis-Dark** is a unified dark theme suite integrating the aesthetic precision of
**Ant-Dracula** with Synthesis window management and CachyOS-inspired teal accents.
It provides a complete, consistent theming experience across MATE, GNOME, XFCE, KDE Plasma,
Cinnamon, and other GTK environments.

## Features

- **GTK Theme**: GTK2/3/4 styling derived from Ant-Dracula with a harmonized
  indigo-mauve-purple selection palette (replaces pink with `#b9a4fa`)
- **Window Manager**: Metacity/Marco theme with gradient titlebars
- **GNOME Shell / Cinnamon**: SCSS-compiled shell themes
- **XFWM4**: Rendered theme assets at standard, HiDPI, and XHiDPI resolutions
- **KDE Plasma**: Aurorae, color-scheme, Kvantum, SDDM, and desktop themes
- **Icons**: MATE-Synthesis-Dark icon set
- **Cursors**: Matching MATE-Synthesis-Dark-Cursors
- **Extras**: Tilix terminal color scheme, Alacritty config, btop theme, WindowMaker

## Installation

### Arch Linux (AUR)

```sh
# With an AUR helper
paru -S synthesis-dark-gtk-theme synthesis-dark-icons synthesis-dark-cursors

# Manual PKGBUILD build
git clone https://github.com/Oichkatzelesfrettschen/Synthesis-Dark-Theme
cd Synthesis-Dark-Theme
makepkg -si
```

### From Source (any distro)

```sh
git clone https://github.com/Oichkatzelesfrettschen/Synthesis-Dark-Theme
cd Synthesis-Dark-Theme
make check-deps          # verify build tools are installed
make all                 # build all themes
make install PREFIX=~/.local  # install to ~/.local/share/
```

### Manual Installation

Copy directories to their respective locations:

- **Themes**: `gtk-2.0`, `gtk-3.0`, `gtk-4.0`, `metacity-1`, `gnome-shell`, `cinnamon`, `xfwm4`
  -> `~/.themes/Synthesis-Dark/` or `/usr/share/themes/Synthesis-Dark/`
- **Icons**: `icons/MATE-Synthesis-Dark` -> `~/.icons/` or `/usr/share/icons/`
- **Cursors**: `icons/MATE-Synthesis-Dark-Cursors` -> `~/.icons/` or `/usr/share/icons/`
- **Tilix**: `extras/tilix/Synthesis-Dark.json` -> `~/.config/tilix/schemes/`

## Applying the Theme

### MATE Desktop

```sh
gsettings set org.mate.interface gtk-theme 'Synthesis-Dark'
gsettings set org.mate.interface icon-theme 'MATE-Synthesis-Dark'
gsettings set org.mate.marco.general theme 'Synthesis-Dark'
```

### GNOME

```sh
gsettings set org.gnome.desktop.interface gtk-theme 'Synthesis-Dark'
gsettings set org.gnome.desktop.interface icon-theme 'MATE-Synthesis-Dark'
```

### XFCE / Others

Use `lxappearance` or your DE's appearance settings panel.

## Repository Structure

```
gtk-2.0/          GTK2 theme (rendered PNGs + gtkrc)
gtk-3.0/          GTK3 theme (hand-authored CSS)
gtk-3.20/         GTK3.20+ theme (SCSS compiled)
gtk-4.0/          GTK4 theme (SCSS compiled)
gnome-shell/      GNOME Shell theme (SCSS compiled)
cinnamon/         Cinnamon theme (SCSS compiled)
metacity-1/       Marco/Metacity window decorations
xfwm4/            XFWM4 theme and asset renderer
icons/            MATE-Synthesis-Dark icons and cursors
kde/              KDE Plasma, Aurorae, Kvantum, SDDM, color-scheme files
extras/           App-specific configs (Tilix, Alacritty, btop, WindowMaker)
src/              Build tools and canonical color palette
  colors.json     Single source of truth for all palette colors
  scripts/        Python and shell build utilities
docs/             Design documentation and rationale
```

## Color Palette

The canonical palette is `src/colors.json`. Key colors:

| Role | Hex | Note |
|------|-----|------|
| Background | `#282a36` | Dracula base |
| Foreground | `#f8f8f2` | Dracula text |
| Selection | `#b9a4fa` | Indigo-mauve centroid (H=255) |
| Accent | `#8e95b8` | Indigo-gray |
| Teal | `#17b169` | CachyOS teal; WM button accent |
| Error | `#ff5555` | Dracula red |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for build setup, code standards, and PR process.

## Credits

- **[Ant-Dracula](https://github.com/EliverLara/Ant-Dracula)**: Base GTK styling and asset pipeline
- **[Catppuccin](https://catppuccin.com/)**: Color family rationale and SCSS patterns
- **Synthesis**: Original window manager and icon theme basis
- **Consolidation and harmonization**: Eirikr (Oichkatzelesfrettschen)
