# Extras

Application-specific configurations using the Synthesis-Dark palette.
These are optional companion configs, not part of the core GTK/WM theme.

## Contents

| Directory | Application | Type |
|-----------|-------------|------|
| `tilix/` | Tilix terminal emulator | Color scheme JSON |
| `alacritty/` | Alacritty terminal emulator | TOML/YAML config |
| `btop/` | btop++ resource monitor | Theme config |
| `micro/` | Micro text editor | Color scheme |
| `shell/` | Bash/Zsh prompt configs | Shell scripts |
| `tint2/` | Tint2 panel | Panel config |
| `windowmaker/` | WindowMaker desktop | Theme and dockapp setup |

## Installation

### Tilix (distributed via PKGBUILD)

The Tilix scheme is installed by the `synthesis-dark-tilix` AUR package to
`/usr/share/tilix/schemes/Synthesis-Dark.json`.

For manual install:
```sh
cp tilix/Synthesis-Dark.json ~/.config/tilix/schemes/
```

### Alacritty

```sh
cp alacritty/synthesis-dark.toml ~/.config/alacritty/
# Add to your alacritty.toml:
# import = ["~/.config/alacritty/synthesis-dark.toml"]
```

### btop

```sh
cp btop/synthesis-dark.theme ~/.config/btop/themes/
```

### WindowMaker

See `windowmaker/README.md` for the full dockapp and style setup guide.
WindowMaker uses the Dracula color palette directly (pre-GTK environment).
