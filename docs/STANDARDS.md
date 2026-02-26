# Synthesis-Dark Engineering Standards

## Python Standards
*   **Tooling:** `ruff` for linting, `black` for formatting.
*   **Target:** Python 3.11+.
*   **Concurrency:** Use `ProcessPoolExecutor` for asset-heavy transformations.

## Asset Pipeline
*   **SVG First:** All icons should be sourced from SVGs. PNGs are generated build artifacts.
*   **Transformation:** Never edit raw assets manually. Use `src/scripts/transform_colors.py` to ensure reproducibility.

## Documentation
*   Changelogs must be semantic and granular.
*   Use descriptive filenames in all-caps for docs (e.g., CHANGELOG.md, CONTRIBUTING.md).
