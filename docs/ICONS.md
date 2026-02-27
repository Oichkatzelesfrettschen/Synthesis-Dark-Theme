# Synthesis-Dark Icon Themes

## Overview

Synthesis-Dark ships two icon themes:

| Theme directory | Purpose |
|---|---|
| `icons/Synthesis-Dark-Icons/` | Primary icon theme (tracked in git) |
| `icons/Synthesis-Dark-Cursors/` | Cursor theme (tracked in git) |

Color variant themes are **generated at build time** from the Tela Circle
submodule source and are **not committed** to git (reproduced by `make icon-variants`):

| Generated directory | Accent color |
|---|---|
| `icons/Synthesis-Dark-Icons-Purple/` | `#bd93f9` (Dracula purple) |
| `icons/Synthesis-Dark-Icons-Teal/` | `#17b169` (CachyOS teal) |
| `icons/Synthesis-Dark-Icons-Mauve/` | `#cba6f7` (Catppuccin mauve) |
| `icons/Synthesis-Dark-Icons-Blue/` | `#b4befe` (lavender blue) |

---

## Icon Theme Structure

```
icons/Synthesis-Dark-Icons/
  index.theme           -- XDG icon theme descriptor
  scalable/
    actions/            -- MATE-origin action icons
    animations/         -- MATE-origin animation icons
    apps/               -- Tela Circle app icons (generated into variant dirs)
    categories/         -- MATE-origin category icons
    devices/            -- Tela Circle device icons
    emblems/            -- MATE-origin emblems
    emotes/             -- MATE-origin emotes
    mimetypes/          -- Tela Circle mimetype icons
    places/             -- Tela Circle place/folder icons (circle style)
    status/             -- MATE-origin status icons
  16x16/ 22x22/ ... 256x256/   -- Fixed-size raster versions
```

**What comes from where:**

- `actions`, `animations`, `categories`, `emblems`, `emotes`, `status` -- from the
  original MATE icon set. These provide consistent action/status iconography.
- `apps`, `devices`, `mimetypes`, `places` -- from Tela Circle (GPL-3.0-or-later).
  These provide ~1600 modern scalable application and folder icons.

---

## Tela Circle Attribution

The app, mimetype, device, and places icons are derived from:

> **Tela Circle Icon Theme**
> Author: vinceliuice
> License: GPL-3.0-or-later
> Source: https://github.com/vinceliuice/Tela-circle-icon-theme

The upstream source is tracked as a git submodule at `upstream/tela-circle/`.
Our `generate_variants.sh` applies color substitution (replacing Tela's source
accent `#5294e2` with our palette colors) -- the same technique Tela Circle's
own `install.sh` uses for its 15 built-in color variants.

To initialise the submodule after cloning:
```sh
git submodule update --init upstream/tela-circle
```

---

## Variant System

### How it works

The variant generator (`src/scripts/generate_variants.sh`) reads from
`upstream/tela-circle/src/` and writes into `icons/Synthesis-Dark-Icons-<Name>/`.
It substitutes Tela's source accent color (`#5294e2`) with each variant's hex.

Variants inherit from the base theme via `Inherits=Synthesis-Dark-Icons` in
their `index.theme`, so they only need to override the colored categories.

### Generate all variants

```sh
make icon-variants
# or equivalently:
sh src/scripts/generate_variants.sh all
```

### Generate a single variant

```sh
make icon-variant-Purple
make icon-variant-Teal
# or:
sh src/scripts/generate_variants.sh Purple
```

### Available variants

| Variant name | Hex | Theme directory | Description |
|---|---|---|---|
| Default | `#8e95b8` | `Synthesis-Dark-Icons` | Indigo-gray (canonical) |
| Purple | `#bd93f9` | `Synthesis-Dark-Icons-Purple` | Dracula purple |
| Teal | `#17b169` | `Synthesis-Dark-Icons-Teal` | CachyOS teal |
| Mauve | `#cba6f7` | `Synthesis-Dark-Icons-Mauve` | Catppuccin mauve |
| Blue | `#b4befe` | `Synthesis-Dark-Icons-Blue` | Lavender |

### Clean generated variants

```sh
make clean
# Removes all icons/Synthesis-Dark-Icons-<Variant>/ directories.
# Does NOT remove icons/Synthesis-Dark-Icons/ (base theme, tracked in git).
```

---

## Adding a New Variant

1. Add an entry to `src/colors.json` under `icon_variants`:
   ```json
   "Coral": {
     "hex": "#ff7f7f",
     "role": "Coral red accent",
     "theme_name": "Synthesis-Dark-Icons-Coral"
   }
   ```

2. Add the variant to `VARIANTS` in `src/scripts/generate_variants.sh`:
   ```
   Coral|#ff7f7f|Synthesis-Dark-Icons-Coral
   ```

3. Add `.PHONY` and `icon-variant-Coral` to `Makefile` if you want a named target.

4. Add the output directory to `.gitignore`.

5. Run `make icon-variants` and verify the output.

---

## Installation

### Manual

```sh
# Base theme
cp -r icons/Synthesis-Dark-Icons ~/.icons/

# Cursor theme
cp -r icons/Synthesis-Dark-Cursors ~/.icons/

# A color variant (generate first)
make icon-variant-Purple
cp -r icons/Synthesis-Dark-Icons-Purple ~/.icons/
```

### Via Makefile (system-wide)

```sh
sudo make install PREFIX=/usr
```

### Apply via gsettings (GNOME/MATE)

```sh
# GNOME
gsettings set org.gnome.desktop.interface icon-theme 'Synthesis-Dark-Icons'

# MATE
gsettings set org.mate.interface icon-theme 'Synthesis-Dark-Icons'

# Cursor theme
gsettings set org.gnome.desktop.interface cursor-theme 'Synthesis-Dark-Cursors'
```

---

## License

- MATE-origin icons: GPL-2.0-or-later (inherited from MATE icon set)
- Tela Circle icons: GPL-3.0-or-later (vinceliuice)
- Synthesis-Dark modifications, scripts, and palette: GPL-3.0-or-later
