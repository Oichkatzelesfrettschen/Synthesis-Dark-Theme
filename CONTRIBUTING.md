# Contributing to Synthesis-Dark

## Development Setup

### Prerequisites

Run `make check-deps` to verify all required tools are available:

- `inkscape` -- SVG rendering (GTK2 assets, WM controls, cursors)
- `optipng` -- PNG optimization
- `sassc` -- SCSS compilation
- `python3` with `Pillow` -- color transformation and accessibility audit
- `shellcheck` -- shell script linting (for contributors)
- `xcursorgen` -- cursor theme building (optional)

Install on Arch Linux:
```
sudo pacman -S inkscape optipng sassc python-pillow shellcheck
```

### Build from Source

```sh
git clone https://github.com/Oichkatzelesfrettschen/Synthesis-Dark-Theme
cd Synthesis-Dark-Theme
make check-deps      # verify prerequisites
make all             # build themes and run accessibility audit
```

### Install Locally

```sh
make install PREFIX=~/.local   # installs to ~/.local/share/themes/ and icons/
```

## Code Standards

### Python

- Files in `src/scripts/` must pass `ruff check --ignore=E501`
- No bare-except clauses -- always catch `Exception as e` and print to stderr
- Use `if __name__ == '__main__':` guards in all scripts

### Shell Scripts

- All `.sh` files must pass `shellcheck -S error`
- Use POSIX sh unless bash arrays are required (xfwm4/render-assets.sh uses bash)
- Quote all variable expansions; use `$(cmd)` not backticks

### Colors

- All new colors must be added to `src/colors.json` before use
- See `docs/COLOR-STRATEGY.md` for the rationale behind the palette
- Selection and accent colors must remain in the indigo-mauve-purple family

## Testing

Run the full test suite:
```sh
pytest tests/ -v
```

Run specific test files:
```sh
pytest tests/test_transform_colors.py -v   # color transform unit tests
pytest tests/test_css_valid.py -v          # CSS syntax validation
pytest tests/test_svg_valid.py -v          # SVG well-formedness
pytest tests/test_color_consistency.py -v  # SCSS colors vs canonical palette
```

Run the accessibility audit:
```sh
make audit    # enforces WCAG AA (4.5:1 minimum contrast)
```

Run lint:
```sh
make lint     # ruff + shellcheck
```

## Pull Request Process

1. Fork the repository and create a feature branch: `git checkout -b feature/my-change`
2. Make your changes following the code standards above
3. Run `make lint && pytest tests/ && make audit` -- all must pass
4. Create a PR describing WHY the change is needed, not just WHAT changed
5. PRs that add new colors must include the `src/colors.json` entry

## Color Palette

The canonical palette is `src/colors.json`. See also:
- `docs/COLORSCHEME.md` -- base Dracula palette and semantic roles
- `docs/COLOR-STRATEGY.md` -- transform targets and WCAG analysis
- `docs/THEORY.md` -- design rationale

## Architecture

The build system is organized as:
- `Makefile` -- orchestrator; run `make help` for all targets
- `src/scripts/` -- Python and shell tools
- `gtk-3.20/`, `gtk-4.0/`, `gnome-shell/`, `cinnamon/` -- SCSS source
- `gtk-3.0/gtk.css` -- hand-authored (no SCSS compilation)
- `icons/` -- MATE-Synthesis-Dark icon and cursor themes
- `kde/` -- KDE Plasma, Aurorae, Kvantum, SDDM, color-scheme files

## Upstream Attribution

This theme integrates work from:
- [Ant-Dracula](https://github.com/EliverLara/Ant-Dracula) -- GTK base and asset pipeline
- [Catppuccin](https://catppuccin.com/) -- color family rationale and SCSS patterns
- [Synthesis](https://github.com/vinceliuice/Colloid-gtk-theme) -- icon and WM styling
