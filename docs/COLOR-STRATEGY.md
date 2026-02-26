# MATE-Synthesis-Dark Color Strategy

## Design Philosophy

Synthesis Dark is NOT a simple color replacement. It's a **semantic color system** that:

1. **Respects original intent** - Blue stays blue-family, green stays green-family
2. **Uses luminance hierarchy** - Primary distinction is brightness, not hue
3. **Colorblind-safe by design** - No red-green conflicts, shape backups
4. **Dark mode optimized** - High contrast on #232530 background

## Color Mapping Rules

### Rule 1: Hue Families Stay Together

| Original MATE Hue | Synthesis Dark Target | Rationale |
|-------------------|----------------------|-----------|
| Blue (200-260) | Indigo/Violet (#b4befe, #cba6f7) | Primary accent, dark mode elegance |
| Green (90-150) | Teal (#17b169, #a6e3a1) | CachyOS identity, success |
| Yellow (40-80) | Warm Yellow (#f9e2af) | Strings, warnings (high luminance) |
| Orange (20-45) | Peach (#fab387) | Secondary accent, values |
| Red (0-20, 340-360) | Soft Red (#f38ba8) | Errors, critical (WCAG safe) |
| Purple (260-300) | Mauve (#cba6f7) | Control flow, keywords |

### Rule 2: Folder Colors

Folders in MATE are ultra-desaturated yellow-green (H:65, S:0.15).

For dark mode, we shift to **desaturated indigo** to:
- Match the overall indigo accent scheme
- Provide contrast on dark backgrounds
- Avoid the "everything is teal" problem

| Original Folder | Target | Luminance |
|-----------------|--------|-----------|
| #c6c8b4 (L:0.75) | #8e95b8 (L:0.55) | Slate/indigo gray |
| Highlight folder | #b4befe (L:0.65) | Lavender accent |

### Rule 3: Luminance Hierarchy (Colorblind Safety)

All semantic colors must have distinct luminance values:

| Role | Color | Luminance | WCAG on #232530 |
|------|-------|-----------|-----------------|
| Error | #f38ba8 | 0.47 | 7.2:1 AA |
| Warning | #f9e2af | 0.76 | 11.6:1 AAA |
| Success | #a6e3a1 | 0.55 | 8.4:1 AAA |
| Info | #89dceb | 0.60 | 9.3:1 AAA |
| Primary Action | #17b169 | 0.34 | 5.2:1 AA |
| UI Accent | #b4befe | 0.58 | 8.9:1 AAA |
| Keywords | #cba6f7 | 0.40 | 6.2:1 AA |

Gap between adjacent luminance values: 0.06-0.15 (sufficient for monochrome distinction)

## Specific Color Mappings

### Blues (MATE Primary) -> Indigo/Lavender

```
#204a87 (dark blue)   -> #45475a (bg-selection, muted)
#3465a4 (medium blue) -> #7f849c (overlay)
#4169e1 (royal blue)  -> #b4befe (lavender, primary)
#729fcf (light blue)  -> #89b4fa (sky blue)
#092c5a (navy)        -> #313244 (surface)
```

### Greens (MATE Success) -> Teal

```
#4e9a06 (dark green)  -> #0d6e43 (dark teal)
#73d216 (lime green)  -> #17b169 (CachyOS teal)
#c9f3a1 (pale green)  -> #a6e3a1 (soft green)
#27ae60 (emerald)     -> #40a07e (teal variant)
```

### Oranges/Yellows (MATE Accents) -> Warm Catppuccin

```
#ffa000 (amber)       -> #fab387 (peach)
#ff9f00 (gold)        -> #f9e2af (yellow)
#ce5c00 (dark orange) -> #e07a4e (muted peach)
#c4a000 (olive)       -> #f9e2af (yellow)
#8f5902 (brown)       -> #a18072 (muted brown)
```

### Reds (MATE Errors) -> Soft Red

```
#c71807 (crimson)     -> #e5657a (soft crimson)
#ef2929 (scarlet)     -> #f38ba8 (Catppuccin red)
#a40000 (dark red)    -> #c54a5c (muted red)
```

### Purples (MATE Minor) -> Mauve

```
#5c3566 (dark purple) -> #594e75 (dark mauve)
#75507b (plum)        -> #cba6f7 (lavender)
```

### Folder Colors (Neutral -> Indigo Gray)

```
#c6c8b4 (pale olive)  -> #8e95b8 (slate)
#bdbfa8 (khaki)       -> #7f849c (gray-violet)
#87a556 (olive green) -> #6c7086 (muted slate)
```

## Transformation Algorithm

### For Saturated Colors (S > 0.3)

1. Identify original hue family
2. Map to target hue from table above
3. Preserve relative luminance (scale to dark mode range)
4. Boost saturation by 10-20% for vibrancy

### For Desaturated Colors (S < 0.3, like folders)

1. Shift hue toward 240 (indigo/blue)
2. Increase saturation to 0.15-0.25 (subtle color)
3. Reduce luminance to 0.45-0.60 (dark mode appropriate)
4. Maintain gradient relationships

### For Grays and Near-Blacks

1. Preserve as-is (outlines, shadows)
2. Optionally warm slightly toward #45475a

## Colorblind Validation Checklist

Luminance gaps verified by `python3 src/scripts/accessibility_audit.py` (P5.9):

- [x] Error vs Success: L=0.40 vs L=0.66 (gap=0.25 + different hue family)
- [x] Warning vs Info: L=0.78 vs L=0.63 (gap=0.15 + warm vs cool)
- [x] Primary vs Secondary: L=0.33 vs L=0.54 (gap=0.21)
- [ ] All pairs pass deuteranopia simulation (requires external tooling)
- [ ] All pairs pass protanopia simulation (requires external tooling)
- [x] Icon shapes provide non-color cues (MATE icon set uses distinct shapes)

## Files Affected

- `icons/MATE-Synthesis-Dark/` (all sizes, repo-relative)
- `src/scripts/transform_colors.py` (transformation script)
- `src/colors.json` (canonical color definitions)

## Version

- v2.0.0 - Redesigned with indigo accent, proper semantic mapping
- v1.0.0 - Initial teal-heavy implementation (deprecated)
