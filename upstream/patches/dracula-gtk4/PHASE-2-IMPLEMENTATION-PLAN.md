# PHASE 2: Deprecated Color Functions Migration - Detailed Implementation Plan

## Executive Summary

**Status:** Phase 2 is identified but NOT YET IMPLEMENTED (separate from Phase 1 production patches)

**Scope:**
- 6 shade() functions (luminosity adjustment)
- 13 alpha() functions (opacity control)
- 2 mix() functions (color blending)
- **Total:** 21 deprecated functions

**Implementation Strategy:** Conservative, tested-first approach
- Create reference implementations
- Validate color accuracy before applying
- Maintain backwards compatibility during transition
- Schedule for GTK5 pre-release testing (Q1 2026)

---

## Function-by-Function Migration Plan

### 1. SHADE() FUNCTIONS (6 occurrences)

**What it does:** Adjusts luminosity of a color
- factor > 1.0 = lighter
- factor < 1.0 = darker

**Current usage:**
```
Line 56:  @define-color wm_title shade(#f8f8f2, 1.8);
Line 60:  @define-color wm_bg_a shade(#1e1f29, 1.2);
Line 64:  @define-color wm_button_hover_color_a shade(#1e1f29, 1.3);
Line 66:  @define-color wm_button_active_color_a shade(#1e1f29, 0.85);
Line 67:  @define-color wm_button_active_color_b shade(#1e1f29, 0.89);
Line 68:  @define-color wm_button_active_color_c shade(#1e1f29, 0.9);
```

**Migration Strategy for shade():**

The GTK4 replacement should preserve the lightness adjustment semantics. Options:

**Option A: Use HSL color-mix() (Recommended for accuracy)**
```css
/* shade(#f8f8f2, 1.8) - multiply lightness by 1.8 */
@define-color wm_title hsl(from #f8f8f2 h s calc(l * 1.8));
```

**Option B: Explicit color-mix() (For safety)**
```css
/* shade(#1e1f29, 1.2) - ~20% lighter */
@define-color wm_bg_a color-mix(in lch, #1e1f29 80%, white);
```

**Validation Method:**
1. Extract color values from original theme
2. Calculate lightness adjustments
3. Compare visual output in gtk4-widget-factory
4. Verify pixel-perfect color match

### 2. ALPHA() FUNCTIONS (13 occurrences)

**What it does:** Adjusts opacity of a color
- Returns transparent version with specified opacity

**Current usage examples:**
```
Line 62:  @define-color wm_shadow alpha(black, 0.35);
Line 63:  @define-color wm_border alpha(black, 0.18);
Line 1092: color: alpha(currentColor, 0.55);
```

**Migration Strategy for alpha():**

**Option A: Use rgba() function (Simplest)**
```css
/* alpha(black, 0.35) */
@define-color wm_shadow rgba(0, 0, 0, 0.35);
```

**Option B: color-mix() with transparent (More explicit)**
```css
/* alpha(currentColor, 0.55) */
color: color-mix(in srgb, currentColor 55%, transparent);
```

**Validation Method:**
1. Compare alpha values (0.0 = transparent, 1.0 = opaque)
2. Visual testing with transparency-heavy widgets
3. Verify no color shift on transparent elements

### 3. MIX() FUNCTIONS (2 occurrences)

**What it does:** Blends two colors with specified weight

**Current usage:**
```
Line 5027: border-bottom: 1px solid mix(@theme_base_color, #000000, 0.35);
Line 5034: border-top: 1px solid mix(@theme_base_color, #000000, 0.35);
```

**Migration Strategy for mix():**

**Option A: Use color-mix() (Direct replacement)**
```css
/* mix(color1, color2, weight) */
/* In GTK4: color-mix(in srgb, color1 weight%, color2) */
border-bottom: 1px solid color-mix(in srgb, @theme_base_color 35%, #000000);
```

**Validation Method:**
1. Calculate blended color values
2. Visual comparison of border appearance
3. Verify contrast meets accessibility standards

---

## Implementation Timeline

**Phase 2.1: Preparation (Week 1-2)**
- [ ] Implement reference conversions for all 21 functions
- [ ] Create test CSS file with both old and new functions
- [ ] Visual comparison testing (gtk4-widget-factory, gtk4-demo)

**Phase 2.2: Migration (Week 3-4)**
- [ ] Migrate shade() functions (6 total)
- [ ] Migrate alpha() functions (13 total)
- [ ] Migrate mix() functions (2 total)
- [ ] Create unified diff patches

**Phase 2.3: Testing (Week 5-6)**
- [ ] Full theme visual regression testing
- [ ] Cross-application testing (Nautilus, Evince, Loupe, etc.)
- [ ] Color accuracy validation
- [ ] Performance impact assessment

**Phase 2.4: Release (Week 7)**
- [ ] Documentation and release notes
- [ ] PKGBUILD version bump (4.0.0-3)
- [ ] Commit to version control
- [ ] Community feedback collection

---

## Patch Files (To Be Created)

1. **0002-migrate-alpha-functions.patch**
   - Convert 13 alpha() calls to rgba()
   - ~30 lines changed
   - Status: PROPOSED

2. **0003-migrate-mix-functions.patch**
   - Convert 2 mix() calls to color-mix()
   - ~5 lines changed
   - Status: PROPOSED

3. **0004-migrate-shade-functions.patch**
   - Convert 6 shade() calls to calculated HSL
   - ~40 lines changed
   - Status: PROPOSED (more complex, requires validation)

---

## PKGBUILD Updates Needed

```bash
# Update pkgrel for Phase 2
pkgrel=3  # Was 2 in Phase 1

# Add Phase 2 patches to prepare() function
patch -p1 < "${srcdir}/0002-migrate-alpha-functions.patch"
patch -p1 < "${srcdir}/0003-migrate-mix-functions.patch"
patch -p1 < "${srcdir}/0004-migrate-shade-functions.patch"
```

---

## Success Criteria

- [ ] All 21 deprecated functions replaced
- [ ] Visual output identical to Phase 1
- [ ] No CSS parser warnings (even when GTK5 is released)
- [ ] All GTK4 applications render correctly
- [ ] Color accuracy within 1% of original
- [ ] Accessibility standards maintained (contrast ratios)
- [ ] Performance: no measurable impact

---

## Future Considerations

**GTK5 Readiness:**
- color-mix() becomes primary blending function
- HSL color-mix() for luminosity adjustments
- rgba() for opacity adjustments
- All deprecated functions removed

**Additional Improvements (Phase 3):**
- SASS/SCSS compilation for maintainability
- Programmatic color generation
- Automated testing in CI/CD
- Color contrast validation

---

## References

- GTK4 CSS Properties: https://docs.gtk.org/gtk4/css-properties.html
- CSS color-mix(): https://www.w3.org/TR/css-color-5/#color-mixing
- CSS HSL colors: https://www.w3.org/TR/css-color-4/#hsl-colors
- Dracula Theme Repository: https://github.com/dracula/gtk
- GTK4 CSS Overview: https://docs.gtk.org/gtk4/css-overview.html
