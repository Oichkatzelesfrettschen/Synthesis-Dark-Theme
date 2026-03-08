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
VECTORIZER = src/scripts/vectorize_assets.py
ICON_BACKEND_PROMOTER = src/scripts/promote_icon_backend.py
SVG_PARITY_AUDITOR = src/scripts/verify_svg_parity.py
PNG_WRAPPER_PROMOTER = src/scripts/promote_png_wrappers.py
RUNTIME_ASSET_SVG_MATERIALIZER = src/scripts/materialize_runtime_asset_svgs.py
SVG_FIDELITY_RECONCILER = src/scripts/reconcile_svg_fidelity.py
SVG_MIGRATION_REPORT = docs/SVG_MIGRATION_REPORT.md
ICON_RECONCILIATION_REPORT = docs/ICON_RECONCILIATION_REPORT.md
PNG_SVG_PARITY_REPORT = docs/PNG_SVG_PARITY_AUDIT.md
PNG_WRAPPER_REPORT = docs/PNG_WRAPPER_PROMOTION_REPORT.md
SVG_FIDELITY_REPORT = docs/SVG_FIDELITY_RECONCILIATION.md

.PHONY: all build themes scss gtk2 marco mate legacy-surfaces icons harmonize xfwm4 cursors wm-assets \
	audit lint install clean check-deps help svg-migration-report icon-reconciliation-report \
	promote-icon-backend vectorize-nonicon-sources svg-parity-audit promote-png-wrappers \
	materialize-runtime-asset-svgs reconcile-svg-fidelity \
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
	@echo "  scss               - Compile SCSS for gtk-3.20, gtk-4.0, gnome-shell, gnome-shell/legacy, cinnamon"
	@echo "  gtk2               - Render GTK2 assets from SVG source"
	@echo "  marco              - Materialize SVG runtime assets for the Marco/Metacity theme surface"
	@echo "  mate               - Refresh GTK2 plus Marco/Metacity assets for the MATE theme surface"
	@echo "  legacy-surfaces    - Refresh GTK2 and Marco/Metacity assets together"
	@echo "  xfwm4              - Render XFWM4 window manager assets"
	@echo "  cursors            - Build cursor theme (requires inkscape, xcursorgen)"
	@echo "  wm-assets          - Render WM control button PNGs"
	@echo "  harmonize          - Apply Synthesis palette to all assets"
	@echo "  icon-variants      - Generate all 5 icon color variants from Tela Circle source"
	@echo "  icon-variant-NAME  - Generate a single variant (Default/Purple/Teal/Mauve/Blue)"
	@echo "  audit              - Run WCAG accessibility contrast audit"
	@echo "  svg-migration-report - Generate the repo-wide SVG migration report"
	@echo "  icon-reconciliation-report - Generate the icon backend dedupe/reconciliation report"
	@echo "  promote-icon-backend - Promote scalable-backed icon semantic IDs into src/icons_backend"
	@echo "  vectorize-nonicon-sources - Convert the safe non-icon source tranche into canonical SVGs"
	@echo "  svg-parity-audit   - Compare SVG-backed PNGs against rendered SVG output before any PNG removal"
	@echo "  promote-png-wrappers - Promote mismatched PNGs into self-contained SVG wrapper authorities"
	@echo "  materialize-runtime-asset-svgs - Sync assets/*.svg siblings into the runtime asset directory"
	@echo "  reconcile-svg-fidelity - Prefer raster-wrapper SVGs only where native SVGs still drift"
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

marco: materialize-runtime-asset-svgs
	@echo "--- Marco/Metacity assets prepared ---"

mate: gtk2 marco
	@echo "--- MATE legacy surfaces prepared ---"

legacy-surfaces: gtk2 marco
	@echo "--- Legacy GTK2 + Marco surfaces prepared ---"

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
	@$(SASSC) -I gnome-shell gnome-shell/legacy/gnome-shell.scss gnome-shell/legacy/gnome-shell.css
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

svg-migration-report:
	@echo "--- Generating SVG Migration Report ---"
	@$(PYTHON) $(VECTORIZER) \
		--input . \
		--output /tmp/synthesis-dark-svg-migration \
		--recursive \
		--dry-run \
		--manifest /tmp/synthesis-dark-svg-migration.json \
		--report-markdown $(SVG_MIGRATION_REPORT)

icon-reconciliation-report:
	@echo "--- Generating Icon Reconciliation Report ---"
	@$(PYTHON) $(VECTORIZER) \
		--input . \
		--output /tmp/synthesis-dark-svg-migration \
		--recursive \
		--dry-run \
		--icon-registry-json /tmp/synthesis-dark-icon-registry.json \
		--icon-report-markdown $(ICON_RECONCILIATION_REPORT)

promote-icon-backend:
	@echo "--- Promoting SVG-backed icon semantic IDs into src/icons_backend ---"
	@$(PYTHON) $(ICON_BACKEND_PROMOTER)

vectorize-nonicon-sources:
	@echo "--- Vectorizing safe non-icon sources into canonical SVG authority paths ---"
	@$(PYTHON) $(VECTORIZER) \
		--input . \
		--output . \
		--recursive \
		--manifest /tmp/synthesis-dark-svg-execution.json

svg-parity-audit:
	@echo "--- Auditing PNG/SVG render parity ---"
	@$(PYTHON) $(SVG_PARITY_AUDITOR) \
		--input . \
		--output /tmp/synthesis-dark-svg-parity \
		--recursive \
		--manifest-json /tmp/synthesis-dark-svg-migration.json \
		--report-json /tmp/synthesis-dark-svg-parity.json \
		--report-markdown $(PNG_SVG_PARITY_REPORT)

promote-png-wrappers:
	@echo "--- Promoting mismatched PNGs into SVG wrapper authorities ---"
	@$(PYTHON) $(PNG_WRAPPER_PROMOTER) \
		--repo-root . \
		--parity-json /tmp/synthesis-dark-svg-parity.json \
		--output-root src/raster_wrappers \
		--report-json /tmp/synthesis-dark-png-wrapper-promotion.json \
		--report-markdown $(PNG_WRAPPER_REPORT)

materialize-runtime-asset-svgs:
	@echo "--- Materializing runtime SVG siblings in assets/ ---"
	@if [ ! -f /tmp/synthesis-dark-svg-migration.json ]; then \
		$(MAKE) svg-migration-report >/dev/null; \
	fi
	@$(PYTHON) $(RUNTIME_ASSET_SVG_MATERIALIZER) \
		--repo-root . \
		--manifest-json /tmp/synthesis-dark-svg-migration.json \
		--report-json /tmp/synthesis-dark-runtime-asset-svgs.json

reconcile-svg-fidelity:
	@echo "--- Reconciling native SVG drift with wrapper authority overrides ---"
	@if [ ! -f /tmp/synthesis-dark-svg-parity.json ]; then \
		$(MAKE) svg-parity-audit >/dev/null; \
	fi
	@$(PYTHON) $(SVG_FIDELITY_RECONCILER) \
		--repo-root . \
		--parity-json /tmp/synthesis-dark-svg-parity.json \
		--output-json src/raster_wrappers/preferred-authorities.json \
		--report-markdown $(SVG_FIDELITY_REPORT)

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
	find gtk-2.0/assets -type f \( -name '*.[Pp][Nn][Gg]' \) -delete 2>/dev/null || true
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
