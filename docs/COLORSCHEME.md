# Synthesis-Dark Master Colorscheme

**Version:** 2.0.0 "Harmonized"

> **Relationship to COLOR-STRATEGY.md:**
> This file documents the **base palette** -- the Dracula-derived colors that form the
> input to the color transformation pipeline. COLOR-STRATEGY.md documents the
> **transform targets** applied by `src/scripts/transform_colors.py`. Both are correct
> for their respective purposes. The canonical single source of truth for all colors
> (with contrast ratios and semantic roles) is `src/colors.json`.

## Core Palette (Base Input -- Dracula-Derived)

| Name | Hex | Usage |
| :--- | :--- | :--- |
| **Background** | `#282a36` | Main window background, terminal bg |
| **Current Line** | `#44475a` | Active list items, selection backgrounds |
| **Foreground** | `#f8f8f2` | Primary text |
| **Comment** | `#6272a4` | Secondary text, comments, borders |
| **Indigo-Gray** | `#8e95b8` | **Folders**, primary UI accents (Replaces Teal for folders) |
| **Cyan/Teal** | `#8be9fd` | Links, special keys (Retained for syntax, removed from folders) |
| **Green** | `#50fa7b` | Success, strings |
| **Orange** | `#ffb86c` | Warnings, functions |
| **Pink** | `#ff79c6` | Keywords, tags |
| **Purple** | `#bd93f9` | Constants, numbers |
| **Red** | `#ff5555` | Errors, deletions |
| **Yellow** | `#f1fa8c` | Parameters |

## Usability Guidelines (WCAG AAA)
*   Ensure text on `#282a36` is at least `#6272a4` or lighter.
*   Avoid placing `#bd93f9` (Purple) on `#44475a` (Current Line) for critical text due to low contrast.
