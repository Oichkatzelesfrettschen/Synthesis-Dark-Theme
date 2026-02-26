#!/bin/sh
# Test PKGBUILD with namcap.
# WHY: namcap catches dependency errors, permission issues, and packaging mistakes
#      that only surface at install time in a clean environment.
#
# Usage: sh tests/test_pkgbuild.sh
# Exit code: 0 = no errors, 1 = errors found

set -eu

PKGBUILD="${1:-PKGBUILD}"
REPO_ROOT="$(dirname "$0")/.."

cd "$REPO_ROOT"

if ! command -v namcap > /dev/null 2>&1; then
    echo "WARNING: namcap not available -- skipping PKGBUILD lint"
    exit 0
fi

echo "Running namcap on $PKGBUILD..."
OUTPUT="$(namcap "$PKGBUILD" 2>&1)"

if echo "$OUTPUT" | grep -q " E:"; then
    echo "FAIL: namcap errors found:"
    echo "$OUTPUT"
    exit 1
else
    echo "PASS: namcap found no errors"
    if [ -n "$OUTPUT" ]; then
        echo "Warnings:"
        echo "$OUTPUT"
    fi
    exit 0
fi
