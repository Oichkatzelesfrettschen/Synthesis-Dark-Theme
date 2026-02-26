#!/bin/sh
# Build reproducibility test.
# WHY: Two consecutive clean builds must produce identical CSS output.
#      Deterministic output is a prerequisite for reliable packaging and caching.
#
# What it tests: 'make clean && make scss' twice produces identical .css files.
# PNG rendering is excluded (inkscape output can have non-deterministic metadata).
#
# Usage: sh tests/test_reproducibility.sh
# Exit code: 0 = reproducible, 1 = not reproducible

set -eu

REPO_ROOT="$(dirname "$0")/.."
TMP1="$(mktemp -d)"
TMP2="$(mktemp -d)"

cleanup() {
    rm -rf "$TMP1" "$TMP2"
}
trap cleanup EXIT

cd "$REPO_ROOT"

echo "Build 1: make clean && make scss..."
make clean > /dev/null 2>&1 || true
make scss > /dev/null 2>&1

# Collect CSS checksums
find gtk-3.20 gtk-4.0 gnome-shell cinnamon -name "*.css" -not -name "_*" 2>/dev/null \
    | sort | xargs sha256sum > "$TMP1/checksums.txt"

echo "Build 2: make clean && make scss..."
make clean > /dev/null 2>&1 || true
make scss > /dev/null 2>&1

find gtk-3.20 gtk-4.0 gnome-shell cinnamon -name "*.css" -not -name "_*" 2>/dev/null \
    | sort | xargs sha256sum > "$TMP2/checksums.txt"

if diff -u "$TMP1/checksums.txt" "$TMP2/checksums.txt"; then
    echo "PASS: builds are reproducible"
    exit 0
else
    echo "FAIL: builds differ"
    exit 1
fi
