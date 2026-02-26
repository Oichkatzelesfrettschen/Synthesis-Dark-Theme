#!/usr/bin/env python3
import os, re, sys, colorsys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

TARGET_FOLDER_RGB = (142, 149, 184) # #8e95b8

def rgb_to_hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    return h * 360, s, l

def hsl_to_rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h/360.0, l, s)
    return int(round(r*255)), int(round(g*255)), int(round(b*255))

def is_folder_color(r, g, b):
    h, s, l = rgb_to_hsl(r, g, b)
    return (40 <= h <= 90 and s < 0.3 and l > 0.5)

def transform_color(r, g, b):
    if (r < 20 and g < 20 and b < 20) or (r > 240 and g > 240 and b > 240):
        return (r, g, b)
    if is_folder_color(r, g, b):
        return TARGET_FOLDER_RGB
    return (r, g, b)

def process_png(path):
    if not HAS_PIL: return
    try:
        img = Image.open(path)
        if img.mode not in ('RGB', 'RGBA'): img = img.convert('RGBA')
        pix = img.load()
        w, h = img.size
        mod = False
        for y in range(h):
            for x in range(w):
                p = pix[x, y]
                if len(p) == 4 and p[3] == 0: continue
                nr, ng, nb = transform_color(*p[:3])
                if (nr, ng, nb) != p[:3]:
                    mod = True
                    pix[x, y] = (nr, ng, nb, p[3]) if len(p) == 4 else (nr, ng, nb)
        if mod: img.save(path)
    except Exception as e:
        print(f"ERROR processing PNG {path}: {e}", file=sys.stderr)

SVG_HEX = re.compile(r'#([0-9a-fA-F]{3,6})')

def process_svg(path):
    try:
        txt = path.read_text()
        def repl(m):
            c = m.group(1)
            if len(c) == 3: c = ''.join(x*2 for x in c)
            rgb = (int(c[:2], 16), int(c[2:4], 16), int(c[4:], 16))
            nr, ng, nb = transform_color(*rgb)
            return f"#{nr:02x}{ng:02x}{nb:02x}"
        ntxt = SVG_HEX.sub(repl, txt)
        if ntxt != txt: path.write_text(ntxt)
    except Exception as e:
        print(f"ERROR processing SVG {path}: {e}", file=sys.stderr)

def main():
    repo_root = Path(__file__).resolve().parents[2]
    print(f"Scanning repository at {repo_root}...")
    
    # Target folders containing assets
    targets = ['icons', 'metacity-1', 'gtk-2.0', 'gtk-3.0', 'gtk-3.20', 'gtk-4.0', 'xfwm4', 'cinnamon']
    
    all_pngs = []
    all_svgs = []
    
    for t in targets:
        dir_path = repo_root / t
        if dir_path.exists():
            all_pngs.extend(list(dir_path.glob("**/*.png")))
            all_svgs.extend(list(dir_path.glob("**/*.svg")))

    print(f"Synthesis in progress: {len(all_pngs)} PNGs, {len(all_svgs)} SVGs...")
    
    for s in all_svgs:
        process_svg(s)
        
    with ProcessPoolExecutor(max_workers=4) as ex:
        list(ex.map(process_png, all_pngs))
        
    print("Repository-wide Synthesis Complete.")

if __name__ == "__main__":
    main()
