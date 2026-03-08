# PNG/SVG Parity Audit

## Summary
- Safe-batch-generation PNGs discovered: `7076`
- Direct render parity candidates: `7076`
- Exact matches: `435`
- Close matches needing review: `6641`
- Mismatches: `0`
- Specialized renderer cases: `0`
- Errors: `0`
- Renderer used for direct checks: `rsvg`
- Theme/runtime `.png` references still in tree: `0`
- Build/tooling `.png` references still in tree: `0`

## Decision
- Do not delete PNGs solely because an SVG authority exists.
- Delete or stop tracking a PNG only after both conditions hold: exact or accepted-close render parity, and no remaining runtime path dependency on that `.png` filename.
- The highest-risk remaining authority class is sprite-sheet or scripted generation, where an SVG exists but the exported PNG is not a trivial one-file render.

## Specialized Renderer Cases
- None

## Largest Mismatches
- None

## Close Matches
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-oasis-spreadsheet-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-oasis-spreadsheet-template.svg` (rmse=`0.000898`, diff_ratio=`0.351562`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-spreadsheet-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-spreadsheet-template.svg` (rmse=`0.000898`, diff_ratio=`0.351562`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-oasis-spreadsheet-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-oasis-spreadsheet-template.svg` (rmse=`0.000898`, diff_ratio=`0.351562`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-spreadsheet-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-spreadsheet-template.svg` (rmse=`0.000898`, diff_ratio=`0.351562`)
- `icons/Synthesis-Dark-Icons/16x16/status/microphone-sensitivity-muted.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/status/microphone-sensitivity-muted.svg` (rmse=`0.000888`, diff_ratio=`0.414062`)
- `icons/Synthesis-Dark-Icons/16x16/actions/stock_new-tab.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/actions/stock_new-tab.svg` (rmse=`0.000880`, diff_ratio=`0.328125`)
- `icons/Synthesis-Dark-Icons/16x16/actions/tab-new.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/actions/tab-new.svg` (rmse=`0.000880`, diff_ratio=`0.328125`)
- `icons/Synthesis-Dark-Icons/16x16/actions/tab_new.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/actions/tab_new.svg` (rmse=`0.000880`, diff_ratio=`0.328125`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-oasis-presentation-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-oasis-presentation-template.svg` (rmse=`0.000853`, diff_ratio=`0.332031`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-presentation-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-presentation-template.svg` (rmse=`0.000853`, diff_ratio=`0.332031`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-oasis-presentation-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-oasis-presentation-template.svg` (rmse=`0.000853`, diff_ratio=`0.332031`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-presentation-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-presentation-template.svg` (rmse=`0.000853`, diff_ratio=`0.332031`)
- `icons/Synthesis-Dark-Icons/22x22/apps/mate-desktop.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/22x22/apps/mate-desktop.svg` (rmse=`0.000840`, diff_ratio=`0.283058`)
- `icons/Synthesis-Dark-Icons/16x16/status/nm-device-wired-secure.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/status/nm-device-wired-secure.svg` (rmse=`0.000825`, diff_ratio=`0.230469`)
- `icons/Synthesis-Dark-Icons/22x22/status/microphone-sensitivity-muted.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/22x22/status/microphone-sensitivity-muted.svg` (rmse=`0.000821`, diff_ratio=`0.442149`)
- `icons/Synthesis-Dark-Icons/32x32/status/microphone-sensitivity-muted.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/32x32/status/microphone-sensitivity-muted.svg` (rmse=`0.000816`, diff_ratio=`0.389648`)
- `icons/Synthesis-Dark-Icons/16x16/devices/gnome-dev-wavelan.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/devices/gnome-dev-wavelan.svg` (rmse=`0.000812`, diff_ratio=`0.457031`)
- `icons/Synthesis-Dark-Icons/16x16/devices/network-wireless.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/devices/network-wireless.svg` (rmse=`0.000812`, diff_ratio=`0.457031`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/gnome-mime-application-vnd.oasis.opendocument.graphics-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/gnome-mime-application-vnd.oasis.opendocument.graphics-template.svg` (rmse=`0.000810`, diff_ratio=`0.339844`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/gnome-mime-application-vnd.sun.xml.draw.template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/gnome-mime-application-vnd.sun.xml.draw.template.svg` (rmse=`0.000810`, diff_ratio=`0.339844`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/x-office-drawing-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/x-office-drawing-template.svg` (rmse=`0.000810`, diff_ratio=`0.339844`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-oasis-text-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-oasis-text-template.svg` (rmse=`0.000797`, diff_ratio=`0.335938`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-text-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg-text-template.svg` (rmse=`0.000797`, diff_ratio=`0.335938`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-oasis-text-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-oasis-text-template.svg` (rmse=`0.000797`, diff_ratio=`0.335938`)
- `icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-text-template.png` <= `src/raster_wrappers/icons/Synthesis-Dark-Icons/16x16/mimetypes/openofficeorg3-text-template.svg` (rmse=`0.000797`, diff_ratio=`0.335938`)

## Exact-Match Coverage By Top-Level Root
- `gtk-2.0`: `170`
- `icons`: `78`
- `assets`: `69`
- `metacity-1`: `56`
- `xfwm4`: `53`
- `gnome-shell`: `4`
- `kde`: `3`
- `cinnamon`: `1`
- `unity`: `1`

## Theme/Runtime `.png` References Still In Tree
- These are direct blockers for removing PNGs without also updating theme/runtime consumers.
- None found

## Build/Tooling `.png` References
- These do not by themselves block migration, but they must be updated if PNG generation rules change.
- None found
