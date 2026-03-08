# Icon Reconciliation Report

## Summary
- Icon PNG outputs discovered: `6715`
- Unique icon semantic IDs: `1196`
- Semantic IDs with authoritative SVG candidates: `1196`
- Semantic IDs still needing shared-backend reconciliation: `0`
- `mate` skin outputs: `3681`
- `tela` skin outputs: `3034`
- `safe-batch-generation` outputs: `6715`
- `icon-family-reconciliation` outputs: `0`

## Shared Backend Priorities
- Promote semantic IDs with authoritative scalable SVGs into the shared backend first.
- Use unresolved semantic IDs as the redraw and reconciliation queue.
- Keep backend output ownership by semantic ID, not by installed filename.

## Highest-Fanout Geometry Candidates
- `start-here`: `12` outputs, categories=`apps, places`, skins=`tela`
- `distributor-logo`: `11` outputs, categories=`apps, places`, skins=`tela`
- `emblem-noread`: `7` outputs, categories=`emblems`, skins=`mate`
- `emblem-nowrite`: `7` outputs, categories=`emblems`, skins=`mate`
- `emblem-readonly`: `7` outputs, categories=`emblems`, skins=`mate`
- `emblem-symbolic-link`: `7` outputs, categories=`emblems`, skins=`mate`
- `emblem-synchronizing`: `7` outputs, categories=`emblems`, skins=`mate`
- `emblem-unreadable`: `7` outputs, categories=`emblems`, skins=`mate`
- `3floppy_unmount`: `6` outputs, categories=`devices`, skins=`tela`
- `ac-adapter`: `6` outputs, categories=`devices`, skins=`tela`
- `access`: `6` outputs, categories=`apps`, skins=`tela`
- `accessibility-directory`: `6` outputs, categories=`apps`, skins=`tela`
- `accessories-calculator`: `6` outputs, categories=`apps`, skins=`tela`
- `accessories-character-map`: `6` outputs, categories=`apps`, skins=`tela`
- `accessories-dictionary`: `6` outputs, categories=`apps`, skins=`tela`
- `accessories-text-editor`: `6` outputs, categories=`apps`, skins=`tela`
- `address-book-new`: `6` outputs, categories=`actions`, skins=`mate`
- `applets-screenshooter`: `6` outputs, categories=`apps`, skins=`tela`
- `application-pgp-encrypted`: `6` outputs, categories=`mimetypes`, skins=`tela`
- `application-rss+xml`: `6` outputs, categories=`mimetypes`, skins=`tela`
- `application-vnd.ms-excel.sheet.macroEnabled.12`: `6` outputs, categories=`mimetypes`, skins=`tela`
- `application-vnd.ms-powerpoint.presentation.macroEnabled.12`: `6` outputs, categories=`mimetypes`, skins=`tela`
- `application-vnd.ms-word.document.macroEnabled.12`: `6` outputs, categories=`mimetypes`, skins=`tela`
- `application-vnd.openofficeorg.extension`: `6` outputs, categories=`mimetypes`, skins=`tela`
- `application-vnd.openxmlformats-officedocument.presentationml.presentation`: `6` outputs, categories=`mimetypes`, skins=`tela`

## First Shared-Backend Tranche
- Start with semantic IDs that already have authoritative SVG candidates and many installed outputs.
- After those are backend-owned, reconcile unresolved `mate` and `tela` IDs into shared geometry plus skin layers.

## Sample Unresolved Semantic IDs
- None
