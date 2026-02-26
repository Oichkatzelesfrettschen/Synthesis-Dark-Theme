# WindowMaker + GNUstep Desktop Configuration

A NeXTSTEP-inspired desktop environment using WindowMaker with Dracula theming.

## Components

### Window Managers
- **WindowMaker** - Lightweight NeXTSTEP-style window manager (X11)
- **wlmaker** - Wayland compositor inspired by WindowMaker (Wayland alternative)

### Dockapps (All Dracula-themed)
- **wmcpuload** - CPU monitor with purple backlight (`#bd93f9`)
- **wmcore** - Per-core CPU monitor
- **wmsysmon** - System monitor (CPU/Mem/Swap/Uptime)
- **wmclock** - Analog clock with cyan LED (`#8be9fd`)
- **wmnd** - Network monitor (green TX `#50fa7b`, pink RX `#ff79c6`)
- **wmmixer** - Audio mixer
- **wmudmount** - USB/disk mount manager
- **stalonetray** - System tray with Dracula background

### GNUstep Applications
- **GWorkspace** - File manager (NeXTSTEP-style)
- **SystemPreferences** - GNUstep preferences

### Support Services
- **picom** - Compositor for transparency and shadows
- **dunst** - Notification daemon
- **nm-applet** - NetworkManager tray icon
- **polkit-mate** - Authentication agent

## Directory Structure

```
~/GNUstep/
  Defaults/
    WindowMaker          # Main configuration (keybindings, focus, workspaces)
    WMRootMenu           # Application menu (right-click, XDG dynamic)
    WMState              # Dock and workspace state

  Library/WindowMaker/
    autostart            # Session startup script
    Styles/
      Dracula.style      # Dracula theme with gradients

~/.config/wlmaker/       # wlmaker Wayland compositor config
    wlmaker.plist        # Main configuration
    style.plist          # Dracula theme
    root-menu.plist      # Root menu with XDG integration
```

## Installation

### Packages

```bash
# WindowMaker core
paru -S windowmaker windowmaker-extra gnustep-base gnustep-gui gnustep-back

# Dockapps (all Dracula-themed via command args)
paru -S wmcpuload wmclock wmsysmon libdockapp
paru -S wmnd wmcore wmudmount wmmixer

# GNUstep applications
paru -S gworkspace systempreferences

# wlmaker (Wayland alternative)
paru -S wlmaker

# Support services
paru -S picom dunst stalonetray network-manager-applet mate-polkit
```

### Copy Configuration

```bash
# WindowMaker configs
mkdir -p ~/GNUstep/Defaults ~/GNUstep/Library/WindowMaker/Styles
cp config/GNUstep/Defaults/* ~/GNUstep/Defaults/
cp config/GNUstep/Library/WindowMaker/* ~/GNUstep/Library/WindowMaker/
chmod +x ~/GNUstep/Library/WindowMaker/autostart

# wlmaker configs
mkdir -p ~/.config/wlmaker
cp config/wlmaker/*.plist ~/.config/wlmaker/
```

### Session Files

```bash
# WindowMaker session
sudo cp config/windowmaker/windowmaker.desktop /usr/share/xsessions/

# wlmaker session (if not installed by package)
sudo cp config/wlmaker/wlmaker.desktop /usr/share/wayland-sessions/
```

Log out and select "WindowMaker" or "wlmaker" from display manager.

## Keybindings

### WindowMaker (X11)

All keybindings use **Super (Mod4)** as the modifier:

| Keybinding | Action |
|------------|--------|
| Super+Tab | Focus next window |
| Super+Shift+Tab | Focus previous window |
| Super+Up | Raise window |
| Super+Down | Lower window |
| Super+m | Maximize window |
| Super+h | Minimize (hide) window |
| Super+q | Close window |
| Super+Right | Next workspace |
| Super+Left | Previous workspace |
| Super+Space | Root menu |
| Super+w | Window list |

### wlmaker (Wayland)

Uses **Ctrl+Alt+Logo** as the modifier:

| Keybinding | Action |
|------------|--------|
| Ctrl+Alt+Logo+T | Launch terminal |
| Ctrl+Alt+Logo+R | Root menu |
| Ctrl+Alt+Logo+L | Lock screen |
| Ctrl+Alt+Logo+Q | Quit |
| Ctrl+Alt+Logo+Left/Right | Switch workspace |
| Ctrl+Alt+Logo+F | Toggle fullscreen |
| Ctrl+Alt+Logo+M | Toggle maximized |

## Workspaces

Four workspaces configured:
1. **Main** - General use
2. **Code** - Development
3. **Web** - Browsers
4. **Media** - Multimedia

## Dock Applications

The dock (right side) contains auto-launching dockapps:

| Dockapp | Function | Dracula Color |
|---------|----------|---------------|
| wmcpuload | CPU load graph | Purple backlight `#bd93f9` |
| wmcore | Per-core CPU | Default |
| wmsysmon | System stats | Default |
| wmnd | Network I/O | Green TX / Pink RX |
| wmclock | Analog clock | Cyan LED `#8be9fd` |
| wmmixer | Volume control | Default |
| wmudmount | Disk mounting | Default |

Plus quick-launch icons: Alacritty, Firefox, Caja, GWorkspace

## XDG Menu Auto-Update

The menu uses dynamic XDG integration for auto-updating application lists.

### WindowMaker (X11)
```
("Applications", OPEN_MENU, "| xdg_menu --format WindowMaker --fullmenu")
```

### wlmaker (Wayland)
```
("Applications...", GeneratePlistMenu, "/usr/bin/wmmenugen -parser:xdg /usr/share/applications/")
```

### Optional: Pacman Hook

For proactive cache generation, install the pacman hook:
```bash
sudo cp etc/pacman.d/hooks/windowmaker-menu.hook /etc/pacman.d/hooks/
sudo cp scripts/wm-update-menu /usr/local/bin/
sudo chmod +x /usr/local/bin/wm-update-menu
```

### Optional: File Watcher Service

For real-time updates (useful for AUR packages or manual .desktop installs):
```bash
cp config/systemd/user/wm-menu-watcher.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now wm-menu-watcher.path
```

## Dracula Theme Colors

| Element | Color | Hex |
|---------|-------|-----|
| Background | Dark gray | #282a36 |
| Current Line | Gray | #44475a |
| Foreground | White | #f8f8f2 |
| Comment | Blue-gray | #6272a4 |
| Focused titlebar | Purple gradient | #bd93f9 -> #6272a4 |
| Menu title | Pink gradient | #ff79c6 -> #bd93f9 |
| Highlight | Pink | #ff79c6 |
| Cyan accent | Cyan | #8be9fd |
| Green accent | Green | #50fa7b |

## Customization

### Change Theme
```bash
setstyle ~/GNUstep/Library/WindowMaker/Styles/Dracula.style
```

### Change Wallpaper
```bash
wmsetbg -u -s ~/path/to/wallpaper.png
```

### Edit Menu
Edit `~/GNUstep/Defaults/WMRootMenu` - changes take effect on next menu open.

### Preferences GUI
Run `WPrefs` for graphical configuration editor.

## Tips

- Drag applications from menu to dock to add them permanently
- Right-click dock icons for options (Lock, Auto-launch, etc.)
- Double-click titlebar to maximize (configurable)
- Clip (left side) is per-workspace; Dock (right side) is global
- Hold Super key and drag anywhere in window to move it
- Dockapps with color options are pre-configured with Dracula colors in autostart
