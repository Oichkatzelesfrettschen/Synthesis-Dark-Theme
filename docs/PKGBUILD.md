# Synthesis-Dark PKGBUILD Documentation

## Package Structure

The Synthesis-Dark suite uses a split-package pattern (`pkgbase`) to provide
modular installation of theme components.

### Packages

| Package | Description | Size |
|---------|-------------|------|
| `synthesis-dark-gtk-theme` | GTK2/3/4 and WM themes | ~15MB |
| `synthesis-dark-marco-theme` | Marco/Metacity window theme (gradient titlebars, CachyOS teal accents) | ~1MB |
| `synthesis-dark-icons` | Icon theme (MATE-Synthesis-Dark) | ~25MB |
| `synthesis-dark-cursors` | Cursor theme | ~2MB |
| `synthesis-dark-tilix` | Tilix terminal color scheme | <1KB |

## Dependencies

### Build Dependencies (makedepends)

| Package | Purpose | Required |
|---------|---------|----------|
| `git` | Source retrieval | Yes |
| `inkscape` | SVG to PNG rendering | Yes |
| `optipng` | PNG optimization | Optional |
| `python-pillow` | Image processing | Yes |
| `potrace` | PNG to SVG vectorization | Optional |
| `svgo` | SVG optimization | Optional |

### Runtime Dependencies

#### synthesis-dark-gtk-theme

| Package | Purpose | Type |
|---------|---------|------|
| `gtk3` | GTK3 applications | depends |
| `gtk4` | GTK4 applications | depends |
| `gtk-engine-murrine` | GTK2 theme engine | depends |
| `libadwaita` | Modern GNOME apps | optdepends |
| `gtk-engines` | Legacy GTK2 engines | optdepends |
| `gnome-themes-extra` | Additional theme support | optdepends |

#### synthesis-dark-icons

| Package | Purpose | Type |
|---------|---------|------|
| `hicolor-icon-theme` | Icon theme fallback | depends |
| `gtk-update-icon-cache` | Icon cache updates | optdepends |

#### synthesis-dark-cursors

| Package | Purpose | Type |
|---------|---------|------|
| `xcursor-themes` | X cursor support | optdepends |

## Conflicts

The following packages conflict with synthesis-dark-gtk-theme:

| Package | Reason |
|---------|--------|
| `ant-dracula-theme-git` | Overlapping theme files |
| `dracula-gtk-theme` | Overlapping theme files |
| `dracula-gtk-theme-git` | Overlapping theme files |
| `dracula-gtk-theme-full` | Overlapping theme files |
| `colloid-dracula-gtk-theme-git` | Similar theme namespace |
| `ant-dracula-gtk-theme` | Ancestor theme |

## Provides/Replaces

```
provides=('dracula-gtk-theme' 'ant-dracula-gtk-theme')
replaces=('ant-dracula-theme-git')
```

## Installation Paths

| Component | Path |
|-----------|------|
| GTK Theme | `/usr/share/themes/Synthesis-Dark/` |
| Icons | `/usr/share/icons/Synthesis-Dark-Icons/` |
| Cursors | `/usr/share/icons/Synthesis-Dark-Cursors/` |
| Tilix | `/usr/share/tilix/schemes/` |

## Build from Source

```bash
# Standard build
makepkg -si

# Force re-render from SVG sources
makepkg -si --noextract
cd src/Synthesis-Dark && make clean && make all
```

## Validation

After installation:

```bash
# Verify theme installation
ls /usr/share/themes/Synthesis-Dark/

# Verify icons
gtk-update-icon-cache -f /usr/share/icons/Synthesis-Dark-Icons/

# Test theme
gsettings set org.gnome.desktop.interface gtk-theme 'Synthesis-Dark'
gsettings set org.gnome.desktop.interface icon-theme 'Synthesis-Dark-Icons'
```
