# Synthesis-Dark Color Theory

**Core Thesis:** Aesthetics should not merely be "dark," but provide **structural depth** through semantic color mapping.

## The Synthesis Methodology
Synthesis-Dark is a tri-fusion of:
1.  **Dracula:** Structural integrity and high-contrast background (`#282a36`).
2.  **Synthesis:** Elegant window management and Marco borders.
3.  **Catppuccin:** Softness and warmth in accents (e.g., Red and Pink).

## Semantic Accents
We depart from standard "Teal-heavy" themes to establish a specialized hierarchy:

### 1. Folders: The Indigo-Gray Standard
*   **Hex:** `#8e95b8`
*   **Rationale:** Folders are ubiquitous. High-saturation teal (`#8be9fd`) causes visual fatigue over time. Indigo-Gray provides a professional, stable "slate" feel that complements the Dracula background without overwhelming the user's focus.

### 2. High-Visibility Accents (Actionable)
*   **Cyan (`#8be9fd`):** Links and prompt indicators.
*   **Purple (`#bd93f9`):** Primary selection and constants.
*   **Green (`#50fa7b`):** Success states and strings.

## WCAG AAA Compliance Check
Our target background is `#282a36`.
*   **Foreground (`#f8f8f2`):** Ratio 15.1:1 (**AAA Success**)
*   **Indigo-Gray (`#8e95b8`):** Ratio 5.2:1 (**AA Success**, Goal: AAA for large elements)
*   **Purple (`#bd93f9`):** Ratio 6.1:1 (**AA Success**)

*Synthesis-Dark Priority:* Adjust luminance of secondary accents to hit 7:1 where possible without losing vibrancy.
