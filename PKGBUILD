# Maintainer: Eirikr <eirikr@example.com>
# Synthesis-Dark Theme Suite
# A unified dark theme integrating Dracula, Ant, and CachyOS aesthetics
# Documentation: docs/PKGBUILD.md

pkgbase=synthesis-dark-suite
pkgname=('synthesis-dark-gtk-theme' 'synthesis-dark-marco-theme' 'synthesis-dark-icons' 'synthesis-dark-cursors' 'synthesis-dark-tilix' 'synthesis-dark-icons-variants')
pkgver=2.1.0
pkgrel=1
pkgdesc="A unified dark theme suite (GTK2/3/4, Marco/Metacity, Icons, Cursors, Extras)"
arch=('any')
url="https://github.com/Oichkatzelesfrettschen/Synthesis-Dark-Theme"
license=('GPL-3.0-or-later')
install=synthesis-dark-suite.install

# Build dependencies - required for rendering SVG to PNG
makedepends=(
    'git'
    'inkscape'       # SVG rendering (GTK2 assets, WM controls, cursors)
    'optipng'        # PNG optimization
    'python-pillow'  # Image processing (color transformation)
    'sassc'          # SCSS compilation (gtk-3.20, gtk-4.0, gnome-shell, cinnamon)
    'xcursorgen'     # Cursor theme building (optional: only needed for 'make cursors')
)

source=("git+file://${HOME}/Github/Synthesis-Dark-Theme")
sha256sums=('SKIP')

build() {
    cd "${srcdir}/Synthesis-Dark-Theme"
    # Run full build: compile SCSS and harmonize palette.
    # GTK2 SVG rendering is skipped if source files are absent (make warns).
    make build
    # Generate icon color variants from Tela Circle submodule source.
    # Requires the submodule to be initialised (included in git clone --recurse-submodules).
    git submodule update --init upstream/tela-circle
    make icon-variants
}

package_synthesis-dark-gtk-theme() {
    pkgdesc="Synthesis-Dark GTK and WM Theme (Dracula+Ant+CachyOS hybrid)"

    # Runtime dependencies
    depends=(
        'gtk3'
        'gtk4'
        'gtk-engine-murrine'  # GTK2 theme engine
    )

    # Optional dependencies for enhanced compatibility
    optdepends=(
        'gtk-engines: Legacy GTK2 engine support'
        'libadwaita: Modern GNOME/GTK4 applications'
        'gnome-themes-extra: Additional theme support'
        'xfce4-settings: XFCE theme configuration'
        'lxappearance: GTK theme configuration tool'
    )

    # Conflicts with upstream Dracula and derivative themes
    conflicts=(
        'ant-dracula-theme-git'
        'ant-dracula-gtk-theme'
        'dracula-gtk-theme'
        'dracula-gtk-theme-git'
        'dracula-gtk-theme-full'
        'colloid-dracula-gtk-theme-git'
    )

    # This package provides/replaces the original themes
    provides=('dracula-gtk-theme' 'ant-dracula-gtk-theme')
    replaces=('ant-dracula-theme-git')

    cd "${srcdir}/Synthesis-Dark-Theme"
    make DESTDIR="${pkgdir}" PREFIX="/usr" install
}

package_synthesis-dark-marco-theme() {
    pkgdesc="Synthesis-Dark Marco/Metacity window theme with gradient titlebars and CachyOS teal accents"

    depends=('gtk3')
    optdepends=(
        'marco: MATE window manager'
        'metacity: GNOME 2 window manager'
        'mutter: GNOME 3+ window manager'
    )

    conflicts=('synthesis-dark-marco-theme-git')
    provides=('metacity-theme-synthesis-dark')

    cd "${srcdir}/Synthesis-Dark-Theme"
    local _destdir="${pkgdir}/usr/share/themes/Synthesis-Dark-Marco"

    install -dm755 "${_destdir}"
    install -dm755 "${_destdir}/metacity-1"
    install -dm755 "${_destdir}/metacity-1/assets"

    # Install index.theme
    install -Dm644 index.theme "${_destdir}/index.theme"

    # Install metacity theme XMLs
    install -Dm644 metacity-1/metacity-theme-3.xml "${_destdir}/metacity-1/metacity-theme-3.xml"
    install -Dm644 metacity-1/metacity-theme-2.xml "${_destdir}/metacity-1/metacity-theme-2.xml"
    install -Dm644 metacity-1/metacity-theme-1.xml "${_destdir}/metacity-1/metacity-theme-1.xml"

    # Install PNG button assets
    install -Dm644 metacity-1/*.png -t "${_destdir}/metacity-1/"

    # Install SVG assets if present
    if [ -d metacity-1/assets ]; then
        install -Dm644 metacity-1/assets/*.svg -t "${_destdir}/metacity-1/assets/" 2>/dev/null || true
    fi
}

package_synthesis-dark-icons() {
    pkgdesc="Synthesis-Dark Icon Theme with CachyOS branding"

    depends=('hicolor-icon-theme')
    optdepends=(
        'gtk-update-icon-cache: Icon cache generation'
        'librsvg: SVG icon rendering'
    )

    cd "${srcdir}/Synthesis-Dark-Theme"
    install -d "${pkgdir}/usr/share/icons/Synthesis-Dark-Icons"
    cp -r icons/Synthesis-Dark-Icons/* "${pkgdir}/usr/share/icons/Synthesis-Dark-Icons/"
}

package_synthesis-dark-cursors() {
    pkgdesc="Synthesis-Dark Cursor Theme"

    optdepends=('xcursor-themes: X cursor support')

    cd "${srcdir}/Synthesis-Dark-Theme"
    install -d "${pkgdir}/usr/share/icons/Synthesis-Dark-Cursors"
    cp -r icons/Synthesis-Dark-Cursors/* "${pkgdir}/usr/share/icons/Synthesis-Dark-Cursors/"
}

package_synthesis-dark-tilix() {
    pkgdesc="Synthesis-Dark Tilix Color Scheme"

    optdepends=('tilix: GPU-accelerated terminal emulator')

    cd "${srcdir}/Synthesis-Dark-Theme"
    install -d "${pkgdir}/usr/share/tilix/schemes"
    install -m 644 extras/tilix/Synthesis-Dark.json "${pkgdir}/usr/share/tilix/schemes/"
}

package_synthesis-dark-icons-variants() {
    pkgdesc="Synthesis-Dark Icon Theme Color Variants (Purple, Teal, Mauve, Blue) -- generated from Tela Circle source"

    # Depends on the base icon theme; variants inherit from it via index.theme
    depends=('synthesis-dark-icons' 'hicolor-icon-theme')
    optdepends=(
        'gtk-update-icon-cache: Icon cache generation'
        'librsvg: SVG icon rendering'
    )

    cd "${srcdir}/Synthesis-Dark-Theme"
    for variant in Purple Teal Mauve Blue; do
        local _theme="Synthesis-Dark-Icons-${variant}"
        if [ -d "icons/${_theme}" ]; then
            install -d "${pkgdir}/usr/share/icons/${_theme}"
            cp -r "icons/${_theme}/"* "${pkgdir}/usr/share/icons/${_theme}/"
        fi
    done
}