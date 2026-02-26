#!/bin/sh
# Render WM control button PNGs from SVG sources.
# Replaces src/wm_controls.fish (removed Fish dependency).
#
# WHY: WM button PNGs are generated build artifacts, not hand-edited.
#      Using inkscape + optipng matches the rest of the asset pipeline.
#
# Usage: sh src/scripts/render_wm_controls.sh [assets_dir]
#   assets_dir defaults to ./assets/ (repo root relative)

set -eu

ASSETS_DIR="${1:-assets}"
INKSCAPE="${INKSCAPE:-inkscape}"
OPTIPNG="${OPTIPNG:-optipng}"

WM_CONTROLS="close close_prelight close_unfocused min min_prelight maximize maximize_prelight"

if ! command -v "$INKSCAPE" > /dev/null 2>&1; then
    echo "ERROR: inkscape not found" >&2
    exit 1
fi

if ! command -v "$OPTIPNG" > /dev/null 2>&1; then
    echo "ERROR: optipng not found" >&2
    exit 1
fi

for item in $WM_CONTROLS; do
    src="${ASSETS_DIR}/${item}.svg"
    dst="${ASSETS_DIR}/${item}@2.png"
    if [ ! -f "$src" ]; then
        echo "WARNING: source not found, skipping: $src" >&2
        continue
    fi
    echo "Rendering $dst"
    "$INKSCAPE" "$src" -o "$dst" --export-dpi=192
    "$OPTIPNG" -o7 --quiet "$dst"
done

echo "WM controls rendered."
