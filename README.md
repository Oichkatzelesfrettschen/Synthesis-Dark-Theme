# Synthesis-Dark

**Synthesis-Dark** is a granular, harmonized, and modular theme suite that integrates the aesthetic precision of **Ant-Dracula** with the window management and icon styles of the **Synthesis** family.

This repository consolidates code, assets, and documentation into a unified structure, providing a complete theming experience for GTK environments (MATE, GNOME, XFCE, etc.).

## Features

*   **GTK Theme**: A hybrid "Dracant-Synthesis" design. Base GTK2/3/4 styling from Ant-Dracula, harmonized with Synthesis headers and controls.
*   **Window Manager**: Synthesis-Dark Metacity/Marco theme for elegant window borders.
*   **Icons**: Complete MATE-Synthesis-Dark icon set.
*   **Cursors**: Matching MATE-Synthesis-Dark cursors.
*   **Extras**: Tilix terminal color scheme.

## Installation

### Arch Linux
You can build and install the entire suite using the included `PKGBUILD`:

```bash
cd Synthesis-Dark
makepkg -si
```

### Manual Installation
Copy the folders to their respective system or user directories:

*   **Themes**: `gtk-2.0`, `gtk-3.0`, `gtk-4.0`, `metacity-1`, etc. -> `~/.themes/Synthesis-Dark/` or `/usr/share/themes/Synthesis-Dark/`
*   **Icons**: `icons/MATE-Synthesis-Dark` -> `~/.icons/` or `/usr/share/icons/`
*   **Cursors**: `icons/MATE-Synthesis-Dark-Cursors` -> `~/.icons/` or `/usr/share/icons/`
*   **Tilix**: `extras/tilix/Synthesis-Dark.json` -> `~/.config/tilix/schemes/`

## Repository Structure

*   `gtk-*`: GTK toolkit styles (2.0, 3.0, 4.0).
*   `metacity-1`: Window manager theme (Marco/Metacity).
*   `cinnamon`, `gnome-shell`, `xfwm4`: Desktop environment specific themes.
*   `icons/`: Icon and Cursor themes.
*   `extras/`: Additional config files (e.g., Tilix).
*   `src/`: Source files for assets and build scripts.
*   `docs/`: Documentation and screenshots.

## Credits

*   **Ant-Dracula**: Base GTK styling and asset generation scripts.
*   **Synthesis-Dark**: Original Window Manager and Icon themes.
*   **Consolidation**: Harmonized by [Your Name/Agent].

## Contributing
See `requirements.md` for build dependencies.
