# Synthesis-Dark Build System
# Adheres to XDG and Standard Linux Packaging Conventions
#
# Architecture:
#   - GTK2 assets: Rendered from src/assets/gtk2/assets.svg
#   - GTK3/4 assets: Pre-rendered in ./assets/ (shared by gtk-3.0, gtk-3.20, gtk-4.0)
#   - SCSS: Compiled via sassc for gtk-3.20, gtk-4.0, gnome-shell, cinnamon
#   - Icons: Synthesis-Dark-Icons and cursors in icons/
#   - Color harmonization: src/scripts/transform_colors.py applies Indigo-Gray palette

PREFIX ?= /usr
DESTDIR ?=
THEME_NAME = Synthesis-Dark
THEME_DIR = $(DESTDIR)$(PREFIX)/share/themes/$(THEME_NAME)
ICON_DIR = $(DESTDIR)$(PREFIX)/share/icons/$(THEME_NAME)-Icons
CURSOR_DIR = $(DESTDIR)$(PREFIX)/share/icons/$(THEME_NAME)-Cursors
TILIX_DIR = $(DESTDIR)$(PREFIX)/share/tilix/schemes

PYTHON = python3
SASSC = sassc
RENDER_ENGINE = src/scripts/render_engine.py
TRANSFORMER = src/scripts/transform_colors.py
ACCESSIBILITY_AUDIT = src/scripts/accessibility_audit.py
WM_CONTROLS_SCRIPT = src/scripts/render_wm_controls.sh
XFWM4_SCRIPT = xfwm4/render-assets.sh
CURSOR_SCRIPT = kde/cursors/build.sh

.PHONY: all build themes scss gtk2 icons harmonize xfwm4 cursors wm-assets \
	audit lint install clean check-deps help \
	icon-variants icon-variant-Default icon-variant-Purple icon-variant-Teal \
	icon-variant-Mauve icon-variant-Blue

ICON_VARIANT_SCRIPT = src/scripts/generate_variants.sh

all: build audit

help:
	@echo "Synthesis-Dark Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all                - Build everything and run accessibility audit"
	@echo "  build              - Build themes and harmonize icons"
	@echo "  themes             - Build GTK2 + compile SCSS"
	@echo "  scss               - Compile SCSS for gtk-3.20, gtk-4.0, gnome-shell, cinnamon"
	@echo "  gtk2               - Render GTK2 assets from SVG source"
	@echo "  xfwm4              - Render XFWM4 window manager assets"
	@echo "  cursors            - Build cursor theme (requires inkscape, xcursorgen)"
	@echo "  wm-assets          - Render WM control button PNGs"
	@echo "  harmonize          - Apply Synthesis palette to all assets"
	@echo "  icon-variants      - Generate all 5 icon color variants from Tela Circle source"
	@echo "  icon-variant-NAME  - Generate a single variant (Default/Purple/Teal/Mauve/Blue)"
	@echo "  audit              - Run WCAG accessibility contrast audit"
	@echo "  lint               - Run ruff (Python) and shellcheck (shell scripts)"
	@echo "  install            - Install to system (use DESTDIR for staging)"
	@echo "  clean              - Remove generated artifacts"
	@echo "  check-deps         - Verify build prerequisites"
	@echo ""
	@echo "Variables:"
	@echo "  PREFIX=$(PREFIX)"
	@echo "  DESTDIR=$(DESTDIR)"

# -----------------------------------------------------------------------------
# Icon Variants (Step 2 of v2.1.0)
# WHY: Users expect folder/accent color choices (Papirus/Tela Circle precedent).
#      Our monochromatic Tela Circle source makes this trivially scriptable.
#      Variants are generated at build time and gitignored (reproducible output).
# HOW: make icon-variants        -- all 5 variants
#      make icon-variant-Purple  -- single variant
# -----------------------------------------------------------------------------
icon-variants:
	@echo "--- Generating all icon color variants ---"
	@git submodule update --init upstream/tela-circle
	@sh $(ICON_VARIANT_SCRIPT) all

icon-variant-%:
	@echo "--- Generating icon variant: $* ---"
	@git submodule update --init upstream/tela-circle
	@sh $(ICON_VARIANT_SCRIPT) $*

build: themes icons

themes: gtk2 scss
	@echo "--- Themes built ---"

# -----------------------------------------------------------------------------
# SCSS Compilation (P2.1)
# WHY: Replaces dead Gulp pipeline. sassc is lightweight with no runtime deps.
# -----------------------------------------------------------------------------
scss:
	@echo "--- Compiling SCSS ---"
	@$(SASSC) gtk-3.20/gtk.scss gtk-3.20/gtk.css
	@$(SASSC) gtk-3.20/gtk-dark.scss gtk-3.20/gtk-dark.css
	@$(SASSC) gtk-4.0/gtk.scss gtk-4.0/gtk.css
	@$(SASSC) gtk-4.0/gtk-dark.scss gtk-4.0/gtk-dark.css
	@$(SASSC) gnome-shell/gnome-shell.scss gnome-shell/gnome-shell.css
	@$(SASSC) cinnamon/cinnamon.scss cinnamon/cinnamon.css
	@$(SASSC) cinnamon/cinnamon-dark.scss cinnamon/cinnamon-dark.css
	@echo "--- SCSS compilation done ---"

# -----------------------------------------------------------------------------
# GTK2 Rendering
# -----------------------------------------------------------------------------
gtk2:
	@echo "--- Building GTK2 Assets ---"
	@if [ -f gtk-2.0/assets.txt ] && [ -f src/assets/gtk2/assets.svg ]; then \
		$(PYTHON) $(RENDER_ENGINE) --source src/assets/gtk2/assets.svg --index gtk-2.0/assets.txt --outdir gtk-2.0/assets; \
	else \
		echo "WARNING: Skipping GTK2 render -- missing source files"; \
		[ -f gtk-2.0/assets.txt ] || echo "  Missing: gtk-2.0/assets.txt"; \
		[ -f src/assets/gtk2/assets.svg ] || echo "  Missing: src/assets/gtk2/assets.svg"; \
	fi

# -----------------------------------------------------------------------------
# XFWM4 Assets (P2.2 / P2.3)
# WHY: xfwm4/render-assets.sh was standalone; now integrated into Make.
# -----------------------------------------------------------------------------
xfwm4:
	@echo "--- Rendering XFWM4 Assets ---"
	@if [ -d xfwm4/assets ] && ls xfwm4/assets/*.svg > /dev/null 2>&1; then \
		cd xfwm4 && sh render-assets.sh; \
	else \
		echo "WARNING: No SVG sources found in xfwm4/assets/ -- skipping"; \
	fi

# -----------------------------------------------------------------------------
# Cursor Theme (P2.4)
# WHY: kde/cursors/build.sh was standalone; now integrated into Make.
# -----------------------------------------------------------------------------
cursors:
	@echo "--- Building Cursor Theme ---"
	@if [ -f $(CURSOR_SCRIPT) ]; then \
		cd kde/cursors && sh build.sh; \
	else \
		echo "WARNING: $(CURSOR_SCRIPT) not found -- skipping"; \
	fi

# -----------------------------------------------------------------------------
# WM Control Buttons (P2.5)
# WHY: Replaces src/wm_controls.fish (removed Fish dependency).
# -----------------------------------------------------------------------------
wm-assets:
	@echo "--- Rendering WM Control Assets ---"
	@sh $(WM_CONTROLS_SCRIPT)

icons: harmonize

harmonize:
	@echo "--- Harmonizing Synthesis Palette ---"
	$(PYTHON) $(TRANSFORMER)

audit:
	@echo "--- WCAG 2.1 Accessibility Audit (enforcing AA >= 4.5:1) ---"
	@$(PYTHON) $(ACCESSIBILITY_AUDIT) --fail-below 4.5 --palette src/colors.json

# -----------------------------------------------------------------------------
# Lint (P2 / P7.2)
# WHY: Single target for all linters prevents regressions in Python and shell.
# -----------------------------------------------------------------------------
lint:
	@echo "--- Linting Python ---"
	@ruff check --ignore=E501 src/scripts/
	@echo "--- Linting Shell Scripts ---"
	@shellcheck -S error xfwm4/render-assets.sh kde/cursors/build.sh \
		src/scripts/render_wm_controls.sh src/scripts/generate_variants.sh \
		tests/test_icon_variants.sh
	@echo "--- Lint passed ---"

# -----------------------------------------------------------------------------
# Dependency Check (P2.6)
# WHY: Gives clear feedback about missing tools before a confusing build failure.
# -----------------------------------------------------------------------------
check-deps:
	@echo "--- Checking Build Dependencies ---"
	@ok=1; \
	for tool in inkscape optipng sassc python3 shellcheck; do \
		if command -v $$tool > /dev/null 2>&1; then \
			echo "  [OK] $$tool"; \
		else \
			echo "  [MISSING] $$tool"; ok=0; \
		fi; \
	done; \
	if python3 -c "import PIL" > /dev/null 2>&1; then \
		echo "  [OK] python-pillow"; \
	else \
		echo "  [MISSING] python-pillow (pip install Pillow)"; ok=0; \
	fi; \
	if command -v xcursorgen > /dev/null 2>&1; then \
		echo "  [OK] xcursorgen"; \
	else \
		echo "  [MISSING] xcursorgen (optional: only needed for 'make cursors')"; \
	fi; \
	if [ $$ok -eq 1 ]; then echo "All required dependencies satisfied."; \
	else echo "ERROR: Some dependencies missing. See above."; exit 1; fi

install:
	@echo "--- Installing to $(DESTDIR)$(PREFIX) ---"
	# Theme files
	install -d $(THEME_DIR)
	cp -r assets gtk-2.0 gtk-3.0 gtk-3.20 gtk-4.0 metacity-1 cinnamon gnome-shell xfwm4 unity index.theme $(THEME_DIR)/

	# Icons
	install -d $(ICON_DIR)
	cp -r icons/Synthesis-Dark-Icons/* $(ICON_DIR)/

	# Cursors
	install -d $(CURSOR_DIR)
	cp -r icons/Synthesis-Dark-Cursors/* $(CURSOR_DIR)/

	# Extras
	install -d $(TILIX_DIR)
	install -m 644 extras/tilix/Synthesis-Dark.json $(TILIX_DIR)/

# -----------------------------------------------------------------------------
# Clean (P2.8)
# WHY: Full clean enables a reproducible rebuild cycle.
# -----------------------------------------------------------------------------
clean:
	@echo "--- Cleaning Generated Artifacts ---"
	# GTK2 rendered PNGs
	find gtk-2.0/assets -type f -name "*.png" -delete 2>/dev/null || true
	# SCSS-compiled CSS (regenerated by 'make scss')
	rm -f gtk-3.20/gtk.css gtk-3.20/gtk-dark.css
	rm -f gtk-4.0/gtk.css gtk-4.0/gtk-dark.css
	rm -f gnome-shell/gnome-shell.css
	rm -f cinnamon/cinnamon.css cinnamon/cinnamon-dark.css
	# XFWM4 rendered PNGs (in Synthesis-Dark*/ subdirs created by render-assets.sh)
	rm -rf xfwm4/Synthesis-Dark xfwm4/Synthesis-Dark-hdpi xfwm4/Synthesis-Dark-xhdpi
	# Cursor build artifacts
	rm -rf kde/cursors/build
	# Icon cache
	find . -type f -name "icon-theme.cache" -delete 2>/dev/null || true
	# Icon variants (generated at build time, safe to delete and regenerate)
	rm -rf icons/Synthesis-Dark-Icons-Purple icons/Synthesis-Dark-Icons-Teal \
		icons/Synthesis-Dark-Icons-Mauve icons/Synthesis-Dark-Icons-Blue
	@echo "Note: Pre-rendered assets in ./assets/ and icons/Synthesis-Dark-Icons/ are preserved"
