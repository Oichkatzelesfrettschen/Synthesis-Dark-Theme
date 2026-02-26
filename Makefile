# Synthesis-Dark Build System
# Adheres to XDG and Standard Linux Packaging Conventions
#
# Architecture:
#   - GTK2 assets: Rendered from src/assets/gtk2/assets.svg
#   - GTK3/4 assets: Pre-rendered in ./assets/ (shared by gtk-3.0, gtk-3.20, gtk-4.0)
#   - Icons: MATE-Synthesis-Dark and cursors in icons/
#   - Color harmonization: transform_colors.py applies Indigo-Gray palette

PREFIX ?= /usr
DESTDIR ?=
THEME_NAME = Synthesis-Dark
THEME_DIR = $(DESTDIR)$(PREFIX)/share/themes/$(THEME_NAME)
ICON_DIR = $(DESTDIR)$(PREFIX)/share/icons/$(THEME_NAME)-Icons
CURSOR_DIR = $(DESTDIR)$(PREFIX)/share/icons/$(THEME_NAME)-Cursors
TILIX_DIR = $(DESTDIR)$(PREFIX)/share/tilix/schemes

PYTHON = python3
RENDER_ENGINE = src/scripts/render_engine.py
TRANSFORMER = src/scripts/transform_colors.py
ACCESSIBILITY_AUDIT = src/scripts/accessibility_audit.py

.PHONY: all build themes icons install clean audit help gtk2 harmonize

all: build audit

help:
	@echo "Synthesis-Dark Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build everything and run accessibility audit"
	@echo "  build     - Build themes and harmonize icons"
	@echo "  gtk2      - Render GTK2 assets from SVG source"
	@echo "  harmonize - Apply Synthesis palette to all assets"
	@echo "  audit     - Run WCAG accessibility contrast audit"
	@echo "  install   - Install to system (use DESTDIR for staging)"
	@echo "  clean     - Remove generated artifacts"
	@echo ""
	@echo "Variables:"
	@echo "  PREFIX=$(PREFIX)"
	@echo "  DESTDIR=$(DESTDIR)"

build: themes icons

themes: gtk2
	@echo "--- GTK3/4 assets ready (pre-rendered in ./assets/) ---"

gtk2:
	@echo "--- Building GTK2 Assets ---"
	@if [ -f gtk-2.0/assets.txt ] && [ -f src/assets/gtk2/assets.svg ]; then \
		$(PYTHON) $(RENDER_ENGINE) --source src/assets/gtk2/assets.svg --index gtk-2.0/assets.txt --outdir gtk-2.0/assets; \
	else \
		echo "WARNING: Skipping GTK2 render -- missing source files"; \
		[ -f gtk-2.0/assets.txt ] || echo "  Missing: gtk-2.0/assets.txt"; \
		[ -f src/assets/gtk2/assets.svg ] || echo "  Missing: src/assets/gtk2/assets.svg"; \
	fi

icons: harmonize

harmonize:
	@echo "--- Harmonizing Synthesis Palette ---"
	$(PYTHON) $(TRANSFORMER)

audit:
	@echo "--- WCAG 2.1 Accessibility Audit ---"
	@$(PYTHON) $(ACCESSIBILITY_AUDIT)

install:
	@echo "--- Installing to $(DESTDIR)$(PREFIX) ---"
	# Theme files
	install -d $(THEME_DIR)
	cp -r assets gtk-2.0 gtk-3.0 gtk-3.20 gtk-4.0 metacity-1 cinnamon gnome-shell xfwm4 unity index.theme $(THEME_DIR)/

	# Icons (rename to Synthesis-Dark-Icons)
	install -d $(ICON_DIR)
	cp -r icons/MATE-Synthesis-Dark/* $(ICON_DIR)/

	# Cursors (rename to Synthesis-Dark-Cursors)
	install -d $(CURSOR_DIR)
	cp -r icons/MATE-Synthesis-Dark-Cursors/* $(CURSOR_DIR)/

	# Extras
	install -d $(TILIX_DIR)
	install -m 644 extras/tilix/Synthesis-Dark.json $(TILIX_DIR)/

clean:
	@echo "--- Cleaning Generated Artifacts ---"
	find gtk-2.0/assets -type f -name "*.png" -delete 2>/dev/null || true
	find . -type f -name "icon-theme.cache" -delete 2>/dev/null || true
	@echo "Note: Pre-rendered assets in ./assets/ and icons/ are preserved"