# SVG Migration Report

## Summary
- Input root: `.`
- Output root: `/tmp/synthesis-dark-svg-migration`
- Default worker plan: `6` CPU process workers
- Total PNG files discovered: `7561`
- `non-icon-first`: `0`
- `icon-family-reconciliation`: `0`
- `safe-batch-generation`: `7076`
- `exclude-derived`: `460`
- `review-later`: `25`

## Priority 1: Non-Icon First
- None

## Priority 2: Icon-Family Reconciliation
- Pending icon rasters without authoritative scalable SVG: `0`
- `mate` skin queue: `0`
- `tela` skin queue: `0`
- Reconcile by `semantic_id` and shared geometry, not by basename alone.

## Priority 3: Safe Batch Generation
- PNGs that already have authoritative SVGs and can move straight to render-only handling: `7076`

## Derived Or Excluded
- Generated or derived rasters already explained by build scripts or higher-resolution outputs: `460`

## Execution Defaults
- CPU-first execution on the local host with `6` process workers.
- Baseline toolchain: Inkscape, ImageMagick, potrace, and svgo.
- CUDA preprocessing fastpath available via `opencv-cuda` on `NVIDIA GeForce RTX 4070 Ti`.
- Optional future fastpath: add `resvg` or `rsvg-convert` for faster CPU-side raster generation.
