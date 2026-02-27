#!/bin/sh
# generate_variants.sh -- Build Synthesis-Dark icon variants from Tela Circle source
#
# WHY: Tela Circle provides 1316+ high-quality scalable app icons, folder icons,
#      mimetype icons, and device icons that our existing MATE icon set lacks.
#      Importing from the submodule and substituting our palette colors gives us
#      full coverage with consistent Synthesis-Dark branding.
#
# WHAT: Reads upstream/tela-circle/src/, applies color substitution, writes to
#       icons/Synthesis-Dark-Icons-<Variant>/ for each configured variant.
#       The default variant (Synthesis-Dark-Icons) is regenerated from Tela source
#       only for the categories we import (apps, places, mimetypes, devices).
#       Existing MATE icons in actions/status/emblems/emotes are preserved.
#
# HOW:
#   make icon-variants        -- generate all variants
#   make icon-variant-Purple  -- generate a single variant
#   sh src/scripts/generate_variants.sh [VARIANT_NAME]
#
# Variants (defined in src/colors.json icon_variants):
#   Default   #8e95b8  Synthesis-Dark-Icons (base, overwrites Tela subdir only)
#   Purple    #bd93f9  Synthesis-Dark-Icons-Purple
#   Teal      #17b169  Synthesis-Dark-Icons-Teal
#   Mauve     #cba6f7  Synthesis-Dark-Icons-Mauve
#   Blue      #b4befe  Synthesis-Dark-Icons-Blue
#
# The Tela Circle source color (#5294e2) is substituted with each variant hex.
# Attribution: Tela Circle icon theme by vinceliuice, GPL-3.0-or-later.
# See: upstream/tela-circle/AUTHORS and upstream/tela-circle/README.md

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TELA_SRC="${REPO_ROOT}/upstream/tela-circle/src"
ICONS_DIR="${REPO_ROOT}/icons"
BASE_THEME="${ICONS_DIR}/Synthesis-Dark-Icons"

# Tela Circle source accent color (all SVGs use this as the folder/accent fill)
TELA_SRC_COLOR="#5294e2"

# Variant definitions: NAME|HEX|DEST_DIRNAME
# Default variant populates a Tela-sourced subdirectory within the base theme.
VARIANTS="
Default|#8e95b8|Synthesis-Dark-Icons
Purple|#bd93f9|Synthesis-Dark-Icons-Purple
Teal|#17b169|Synthesis-Dark-Icons-Teal
Mauve|#cba6f7|Synthesis-Dark-Icons-Mauve
Blue|#b4befe|Synthesis-Dark-Icons-Blue
"

# Which categories to import from Tela Circle.
# actions/status/emblems/emotes stay as MATE icons in the base theme.
TELA_CATEGORIES="apps mimetypes devices"
TELA_PLACE_STYLE="places-circle"

# Sizes to copy from Tela (fixed-size PNGs / symlinks)
TELA_SIZES="16 22 24 32"

# ----------------------------------------------------------------------------
# usage: die MESSAGE
die() { echo "ERROR: $1" >&2; exit 1; }

# usage: check_submodule
check_submodule() {
    if [ ! -d "${TELA_SRC}" ] || [ ! -f "${TELA_SRC}/index.theme" ]; then
        die "Tela Circle submodule not initialised. Run: git submodule update --init upstream/tela-circle"
    fi
}

# usage: apply_color SRC_DIR DEST_DIR FROM_COLOR TO_COLOR
# Copies all SVGs from SRC_DIR to DEST_DIR, substituting FROM_COLOR with TO_COLOR.
# Variable names use _ac_ prefix to avoid colliding with callers' local variables.
apply_color() {
    _ac_src="$1"; _ac_dest="$2"; _ac_from="$3"; _ac_to="$4"
    install -d "${_ac_dest}"
    for _ac_svg in "${_ac_src}"/*.svg; do
        [ -f "${_ac_svg}" ] || continue
        _ac_base="$(basename "${_ac_svg}")"
        sed "s/${_ac_from}/${_ac_to}/g" "${_ac_svg}" > "${_ac_dest}/${_ac_base}"
    done
}

# usage: build_variant NAME HEX DEST_DIRNAME
build_variant() {
    name="$1"; hex="$2"; dest_name="$3"
    dest="${ICONS_DIR}/${dest_name}"

    echo "  Generating ${dest_name} (${hex}) ..."

    # Scalable categories from Tela
    for cat in ${TELA_CATEGORIES}; do
        src_cat="${TELA_SRC}/scalable/${cat}"
        [ -d "${src_cat}" ] || continue
        apply_color "${src_cat}" "${dest}/scalable/${cat}" "${TELA_SRC_COLOR}" "${hex}"
    done

    # Places (circle style)
    src_places="${TELA_SRC}/scalable/${TELA_PLACE_STYLE}"
    if [ -d "${src_places}" ]; then
        apply_color "${src_places}" "${dest}/scalable/places" "${TELA_SRC_COLOR}" "${hex}"
    fi

    # Fixed-size: apps, places, and devices where present
    # (Tela src/16,22,24 have apps+places; src/32 has devices but not apps/places)
    for size in ${TELA_SIZES}; do
        for cat in apps places devices; do
            src_cat="${TELA_SRC}/${size}/${cat}"
            [ -d "${src_cat}" ] || continue
            apply_color "${src_cat}" "${dest}/${size}/${cat}" "${TELA_SRC_COLOR}" "${hex}"
        done
    done

    # Write index.theme for variant (non-default variants inherit from base)
    write_index_theme "${dest}" "${dest_name}" "${name}"

    echo "  Done: ${dest}"
}

# usage: write_index_theme DEST_DIR THEME_DIRNAME VARIANT_NAME
write_index_theme() {
    dest="$1"; dirname="$2"; variant="$3"

    if [ "${variant}" = "Default" ]; then
        # Default variant: index.theme already lives in the base MATE icon tree.
        # We only update the Tela-sourced subdirs; do not overwrite the full index.
        return
    fi

    cat > "${dest}/index.theme" << EOF
[Icon Theme]
Name=Synthesis-Dark Icons ${variant}
Comment=Synthesis-Dark Icon Theme -- ${variant} variant
Inherits=Synthesis-Dark-Icons,hicolor
Example=folder

[Icon Theme]
Directories=scalable/apps,scalable/places,scalable/mimetypes,scalable/devices

[scalable/apps]
Context=Applications
Size=48
MinSize=8
MaxSize=512
Type=Scalable

[scalable/places]
Context=Places
Size=48
MinSize=8
MaxSize=512
Type=Scalable

[scalable/mimetypes]
Context=MimeTypes
Size=48
MinSize=8
MaxSize=512
Type=Scalable

[scalable/devices]
Context=Devices
Size=48
MinSize=8
MaxSize=512
Type=Scalable
EOF
}

# ----------------------------------------------------------------------------
# main
check_submodule

requested="${1:-all}"

echo "==> Synthesis-Dark Icon Variant Generator"
echo "    Tela Circle source: ${TELA_SRC}"
echo "    Icons output:       ${ICONS_DIR}"
echo ""

printf '%s\n' "${VARIANTS}" | while IFS='|' read -r name hex dest_name; do
    # Skip blank lines from heredoc formatting
    [ -z "${name}" ] && continue

    if [ "${requested}" = "all" ] || [ "${requested}" = "${name}" ]; then
        build_variant "${name}" "${hex}" "${dest_name}"
    fi
done

echo ""
echo "==> Icon variant generation complete."
echo "    Run 'gtk-update-icon-cache icons/<theme>/' to update caches."
