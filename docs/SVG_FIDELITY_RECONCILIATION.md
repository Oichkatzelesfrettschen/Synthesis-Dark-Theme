# SVG Fidelity Reconciliation

## Summary
- Preferred-authority overrides emitted: `9`

## By Family
- `assets`: `3`
- `cinnamon`: `2`
- `gnome-shell`: `4`

## Overrides
- `assets/close_unfocused.png`: `assets/close_unfocused.svg` -> `src/raster_wrappers/assets/close_unfocused.svg` (rmse `0.217877`, differing ratio `0.40816326530612246`)
- `assets/maximize_unfocused.png`: `assets/maximize_unfocused.svg` -> `src/raster_wrappers/assets/maximize_unfocused.svg` (rmse `0.358775`, differing ratio `0.8775510204081632`)
- `assets/min_unfocused.png`: `assets/min_unfocused.svg` -> `src/raster_wrappers/assets/min_unfocused.svg` (rmse `0.358775`, differing ratio `0.8775510204081632`)
- `cinnamon/common-assets/misc/overview-hover.png`: `cinnamon/common-assets/misc/overview-hover.svg` -> `src/raster_wrappers/cinnamon/common-assets/misc/overview-hover.svg` (rmse `0.412561`, differing ratio `0.509765625`)
- `cinnamon/common-assets/misc/overview.png`: `cinnamon/common-assets/misc/overview.svg` -> `src/raster_wrappers/cinnamon/common-assets/misc/overview.svg` (rmse `0.158519`, differing ratio `0.28125`)
- `gnome-shell/assets/corner-ripple-ltr.png`: `gnome-shell/assets/corner-ripple-ltr.svg` -> `src/raster_wrappers/gnome-shell/assets/corner-ripple-ltr.svg` (rmse `0.449123`, differing ratio `0.9881656804733728`)
- `gnome-shell/assets/corner-ripple-rtl.png`: `gnome-shell/assets/corner-ripple-rtl.svg` -> `src/raster_wrappers/gnome-shell/assets/corner-ripple-rtl.svg` (rmse `0.449123`, differing ratio `0.9881656804733728`)
- `gnome-shell/assets/ws-switch-arrow-down.png`: `gnome-shell/assets/ws-switch-arrow-down.svg` -> `src/raster_wrappers/gnome-shell/assets/ws-switch-arrow-down.svg` (rmse `0.293407`, differing ratio `0.1379123263888889`)
- `gnome-shell/assets/ws-switch-arrow-up.png`: `gnome-shell/assets/ws-switch-arrow-up.svg` -> `src/raster_wrappers/gnome-shell/assets/ws-switch-arrow-up.svg` (rmse `0.293527`, differing ratio `0.13802083333333334`)
