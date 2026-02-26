# WindowMaker XDG Menu Auto-Update Roadmap

## Problem Statement
WindowMaker uses a static proplist format (WMRootMenu) that doesn't auto-update when applications are installed or removed. This requires manual menu editing or regeneration.

## Research Summary

### Available Tools

| Tool | Type | Pros | Cons |
|------|------|------|------|
| **xdg_menu** | Perl (archlinux-xdg-menu) | Already installed, clean output, proper categories | Requires external call |
| **wmmenugen** | C (built-in) | Native proplist output, fast | Requires piping desktop files |
| **wmgenmenu** | C (built-in) | Simple invocation | Basic menu, hardcoded items |
| **xdgmenumaker** | Python (AUR) | Feature-rich, localization | Extra dependency |

### WindowMaker Menu Commands

| Command | Description |
|---------|-------------|
| `OPEN_MENU \| command` | Pipe: runs command, parses output as menu items |
| `OPEN_MENU file.menu` | External: loads menu from file |
| `OPEN_PLMENU \|\| command` | Pipe proplist: runs command, expects proplist format |

## Chosen Architecture: Hybrid Approach

```
WMRootMenu (static)
├── Custom Items (terminals, quick access)
├── "Applications" -> OPEN_MENU | xdg_menu (dynamic)
├── Run... (dmenu)
├── Appearance (themes, backgrounds)
├── Workspaces
└── Session controls

Auto-Update Triggers:
├── Pacman hook -> regenerates cached menu on package changes
└── inotify watcher (optional) -> real-time updates
```

## Implementation Plan

### Phase 1: Dynamic Menu Integration
1. Modify WMRootMenu to use `OPEN_MENU | xdg_menu --format WindowMaker`
2. Keep custom top-level entries for quick access
3. Test menu loading speed

### Phase 2: Pacman Hook (Arch-specific)
Create `/etc/pacman.d/hooks/windowmaker-menu.hook`:
- Triggers on: package install/remove/upgrade
- Action: regenerate cached menu file
- Target: `/var/cache/xdg-menu/WindowMaker/wmrc`

### Phase 3: Inotify Watcher (Optional)
Create systemd user service:
- Watches: `/usr/share/applications/`, `~/.local/share/applications/`
- Action: regenerate menu on .desktop file changes
- Debounce: 2-second delay to batch changes

### Phase 4: Menu Refresh Entry
Add menu item for manual regeneration:
```
("Refresh Menu", EXEC, "xdg_menu --format WindowMaker > ~/.cache/wm-xdg-menu && wmaker --restart")
```

## File Locations

| File | Purpose |
|------|---------|
| `~/GNUstep/Defaults/WMRootMenu` | Main menu with dynamic include |
| `~/.cache/wm-xdg-menu` | Cached XDG menu (optional) |
| `/etc/pacman.d/hooks/windowmaker-menu.hook` | Pacman trigger |
| `~/.config/systemd/user/wm-menu-watcher.service` | Inotify service |

## Performance Considerations

- **Dynamic pipe menu**: ~50-100ms delay on first access (acceptable)
- **Cached menu**: No delay, but requires regeneration triggers
- **Recommendation**: Use dynamic for simplicity, add pacman hook for freshness

## Sources
- [xdgmenumaker GitHub](https://github.com/gapan/xdgmenumaker)
- [Arch Wiki: xdg-menu](https://wiki.archlinux.org/title/Xdg-menu)
- [WindowMaker OPEN_PLMENU](https://awbsworld.de/archives/110)
- [WindowMaker Guided Tour](http://www.windowmaker.org/docs/guidedtour/menu.html)
