# WindowMaker Startup Configuration Preserved
The following commands and arguments were previously in the autostart script.
Since scripts are not allowed, these arguments should be applied where possible (e.g., in .Xresources, alias, or manual launch).

## Color Codes & Arguments
- **Picom:** `picom --config ~/.config/picom/picom.conf`
- **StaloneTray:** `stalonetray --geometry 6x1-0+0 --grow-gravity W --icon-gravity E --background "#282a36" --icon-size 24 --kludges fix_window_pos`
- **WMCPULoad:** `wmcpuload -bl -lc "rgb:BD/93/F9" -i 2` (Purple backlight)
- **WMClock:** `wmclock -led "#8be9fd"` (Cyan LED)
- **WMND (Network):** `wmnd -c "#50fa7b" -C "#ff79c6" -i enp7s0 -w waveform` (Green TX, Pink RX)
- **WMWeather+:** `wmweather+ -c ~/.wmweather+/wmweather+.conf`
