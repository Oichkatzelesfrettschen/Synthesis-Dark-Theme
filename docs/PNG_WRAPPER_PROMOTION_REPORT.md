# PNG Wrapper Promotion Report

## Summary
- Output root: `/home/eirikr/Github/Synthesis-Dark-Theme/src/raster_wrappers`
- Dry run: `no`
- Wrapper SVGs promoted this run: `99`
- Existing wrapper SVGs skipped: `6550`

## By Promotion Reason
- `icon-family-reconciliation`: `99`

## By Family
- `icon`: `99`

## Decision
- These wrapper SVGs preserve shipped pixel output exactly by embedding the PNG payload.
- They are a reproducibility fallback, not the end-state shared-geometry solution.
- After promotion, runtime references can be rewired toward SVG while preserving render fidelity.
