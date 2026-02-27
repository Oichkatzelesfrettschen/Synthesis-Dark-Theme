#!/bin/sh
# test_icon_variants.sh -- Verify icon variant generation correctness
#
# WHY: Ensures that make icon-variants produces the expected directory structure,
#      applies the correct accent colors, and removes the source color. Intended
#      to run in CI after make icon-variants.
#
# WHAT: Checks existence, index.theme correctness, accent color presence, and
#       source color absence for each generated variant.
#
# HOW:
#   sh tests/test_icon_variants.sh
#   (exit code 0 = all pass, non-zero = failures)

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ICONS_DIR="${REPO_ROOT}/icons"

# Tela Circle source accent (must NOT appear in generated SVGs)
TELA_SRC_COLOR="#5294e2"

# Variants to test: NAME|HEX|DIRNAME
# Default variant is tested separately (no index.theme at root, inherits from MATE base)
VARIANTS="
Purple|#bd93f9|Synthesis-Dark-Icons-Purple
Teal|#17b169|Synthesis-Dark-Icons-Teal
Mauve|#cba6f7|Synthesis-Dark-Icons-Mauve
Blue|#b4befe|Synthesis-Dark-Icons-Blue
"

# Use a temp file to accumulate failure count across subshells (POSIX sh workaround).
# printf|while runs in a subshell; variables set inside don't propagate to parent.
_FAIL_FILE="$(mktemp)"
trap 'rm -f "${_FAIL_FILE}"' EXIT

ok() { echo "  [PASS] $1"; }
fail() {
    echo "  [FAIL] $1"
    echo "x" >> "${_FAIL_FILE}"
}

check_dir() {
    if [ -d "$1" ]; then ok "dir exists: $1"; else fail "dir missing: $1"; fi
}

check_file() {
    if [ -f "$1" ]; then ok "file exists: $1"; else fail "file missing: $1"; fi
}

check_color_present() {
    # Checks that at least one SVG in the directory contains the hex color
    _dir="$1"; _color="$2"; _label="$3"
    _count=0
    for _svg in "${_dir}"/*.svg; do
        [ -f "${_svg}" ] || continue
        if grep -qF "${_color}" "${_svg}" 2>/dev/null; then
            _count=$((_count + 1))
        fi
    done
    if [ "${_count}" -gt 0 ]; then
        ok "color ${_color} found in ${_count} SVGs under ${_label}"
    else
        fail "color ${_color} NOT found in any SVG under ${_label}"
    fi
}

check_color_absent() {
    # Checks that no SVG in the directory contains the hex color
    _dir="$1"; _color="$2"; _label="$3"
    _count=0
    for _svg in "${_dir}"/*.svg; do
        [ -f "${_svg}" ] || continue
        if grep -qF "${_color}" "${_svg}" 2>/dev/null; then
            _count=$((_count + 1))
        fi
    done
    if [ "${_count}" -eq 0 ]; then
        ok "source color ${_color} absent from ${_label}"
    else
        fail "source color ${_color} still present in ${_count} SVGs under ${_label}"
    fi
}

check_index_theme_name() {
    _file="$1"; _expected="$2"
    if grep -qF "Name=${_expected}" "${_file}" 2>/dev/null; then
        ok "index.theme Name=${_expected}"
    else
        fail "index.theme Name field does not contain '${_expected}' in ${_file}"
    fi
}

check_index_theme_inherits() {
    _file="$1"; _expected="$2"
    if grep -qF "Inherits=${_expected}" "${_file}" 2>/dev/null; then
        ok "index.theme Inherits=${_expected}"
    else
        fail "index.theme Inherits field does not contain '${_expected}' in ${_file}"
    fi
}

# ============================================================================
echo "=== Icon Variant Tests ==="
echo ""

# Test base theme exists (prerequisite)
echo "-- Base theme (Synthesis-Dark-Icons) --"
check_dir "${ICONS_DIR}/Synthesis-Dark-Icons"
check_file "${ICONS_DIR}/Synthesis-Dark-Icons/index.theme"
check_dir "${ICONS_DIR}/Synthesis-Dark-Icons/scalable/apps"
check_dir "${ICONS_DIR}/Synthesis-Dark-Icons/scalable/places"

echo ""

# Test each variant
printf '%s\n' "${VARIANTS}" | while IFS='|' read -r name hex dirname; do
    [ -z "${name}" ] && continue
    dest="${ICONS_DIR}/${dirname}"

    echo "-- Variant: ${name} (${hex}) --"

    # Directory structure
    check_dir "${dest}"
    check_dir "${dest}/scalable/apps"
    check_dir "${dest}/scalable/places"
    check_dir "${dest}/scalable/mimetypes"
    check_dir "${dest}/scalable/devices"
    check_file "${dest}/index.theme"

    # index.theme correctness
    check_index_theme_name "${dest}/index.theme" "Synthesis-Dark Icons ${name}"
    check_index_theme_inherits "${dest}/index.theme" "Synthesis-Dark-Icons"

    # Color substitution: accent present, source absent
    check_color_present "${dest}/scalable/apps" "${hex}" "${dirname}/scalable/apps"
    check_color_absent  "${dest}/scalable/apps" "${TELA_SRC_COLOR}" "${dirname}/scalable/apps"
    check_color_present "${dest}/scalable/places" "${hex}" "${dirname}/scalable/places"
    check_color_absent  "${dest}/scalable/places" "${TELA_SRC_COLOR}" "${dirname}/scalable/places"

    echo ""
done

# ============================================================================
_fail_count=0
if [ -s "${_FAIL_FILE}" ]; then
    _fail_count=$(wc -l < "${_FAIL_FILE}")
fi

echo "=== Results ==="
echo "  Failed: ${_fail_count}"
echo ""

if [ "${_fail_count}" -gt 0 ]; then
    echo "FAIL: ${_fail_count} test(s) failed. Run 'make icon-variants' to regenerate."
    exit 1
else
    echo "PASS: All icon variant tests passed."
fi
