def get_luminance(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

def get_contrast(hex1, hex2):
    l1 = get_luminance(hex1)
    l2 = get_luminance(hex2)
    if l1 < l2: l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)

palette = {
    "Background": "#282a36",
    "Current Line": "#44475a",
    "Foreground": "#f8f8f2",
    "Comment": "#6272a4",
    "Indigo-Gray": "#8e95b8",
    "Cyan": "#8be9fd",
    "Green": "#50fa7b",
    "Orange": "#ffb86c",
    "Pink": "#ff79c6",
    "Purple": "#bd93f9",
    "Red": "#ff5555",
    "Yellow": "#f1fa8c"
}

bg = palette["Background"]
fg = palette["Foreground"]

print(f"--- WCAG 2.1 Contrast Audit (Target BG: {bg}) ---")
for name, hex_val in palette.items():
    if name == "Background": continue
    ratio = get_contrast(hex_val, bg)
    status = "PASS (AAA)" if ratio >= 7 else "PASS (AA)" if ratio >= 4.5 else "FAIL"
    print(f"{name:15} ({hex_val}): {ratio:5.2f} : 1 [{status}]")
