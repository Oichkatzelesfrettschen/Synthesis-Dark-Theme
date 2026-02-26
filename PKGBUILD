# Maintainer: Eirikr <eirikr@example.com>
# Synthesis-Dark Theme Suite
# A unified dark theme integrating Dracula, Ant, and CachyOS aesthetics
# Documentation: docs/PKGBUILD.md

pkgbase=synthesis-dark-suite
pkgname=('synthesis-dark-gtk-theme' 'synthesis-dark-marco-theme' 'synthesis-dark-icons' 'synthesis-dark-cursors' 'synthesis-dark-tilix')
pkgver=2.0.0
pkgrel=1
pkgdesc="A unified dark theme suite (GTK2/3/4, Marco/Metacity, Icons, Cursors, Extras)"
arch=('any')
url="https://github.com/Oichkatzelesfrettschen/Synthesis-Dark-Theme"
license=('GPL-3.0-or-later')

# Build dependencies - required for rendering SVG to PNG
makedepends=(
    'git'
    'inkscape'       # SVG rendering
    'optipng'        # PNG optimization
    'python-pillow'  # Image processing
    'potrace'        # PNG to SVG vectorization (optional rebuild)
    'svgo'           # SVG optimization (optional)
)

source=("git+file://${HOME}/Github/Synthesis-Dark-Theme")
sha256sums=('SKIP')

build() {
    cd "${srcdir}/Synthesis-Dark-Theme"
    # We do not run 'make build' here by default to save build time in standard installs
    # unless we want to force re-rendering from source.
    # We will run the palette harmonizer to ensure consistent colors.
    make icons
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
    cp -r icons/MATE-Synthesis-Dark/* "${pkgdir}/usr/share/icons/Synthesis-Dark-Icons/"
}

package_synthesis-dark-cursors() {
    pkgdesc="Synthesis-Dark Cursor Theme"

    optdepends=('xcursor-themes: X cursor support')

    cd "${srcdir}/Synthesis-Dark-Theme"
    install -d "${pkgdir}/usr/share/icons/Synthesis-Dark-Cursors"
    cp -r icons/MATE-Synthesis-Dark-Cursors/* "${pkgdir}/usr/share/icons/Synthesis-Dark-Cursors/"
}

package_synthesis-dark-tilix() {
    pkgdesc="Synthesis-Dark Tilix Color Scheme"

    optdepends=('tilix: GPU-accelerated terminal emulator')

    cd "${srcdir}/Synthesis-Dark-Theme"
    install -d "${pkgdir}/usr/share/tilix/schemes"
    install -m 644 extras/tilix/Synthesis-Dark.json "${pkgdir}/usr/share/tilix/schemes/"
}