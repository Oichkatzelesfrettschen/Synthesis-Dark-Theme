#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path

INKSCAPE = os.environ.get('INKSCAPE', '/usr/bin/inkscape')
OPTIPNG = os.environ.get('OPTIPNG', '/usr/bin/optipng')
RASTER_EXT = '.png'

def render_svg_asset(svg_source, asset_id, output_path):
    print(f"  Rendering: {output_path.name}")
    try:
        subprocess.run([
            INKSCAPE,
            f"--export-id={asset_id}",
            "--export-id-only",
            "--export-background-opacity=0",
            f"--export-filename={output_path}",
            svg_source
        ], check=True, capture_output=True)

        if os.path.exists(OPTIPNG):
            subprocess.run([OPTIPNG, "-o7", "--quiet", output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  ERROR rendering {asset_id}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Universal Synthesis-Dark Asset Renderer')
    parser.add_argument('--source', required=True, help='Source SVG file')
    parser.add_argument('--index', help='Text file with list of asset IDs')
    parser.add_argument('--outdir', required=True, help='Output directory for PNGs')

    args = parser.parse_args()
    source = Path(args.source)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.index:
        with open(args.index) as f:
            asset_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        for aid in asset_ids:
            render_svg_asset(source, aid, outdir / f"{aid}{RASTER_EXT}")
    else:
        print(
            "Error: --index is required. Provide a text file listing SVG element IDs "
            "to render, one per line. Example: --index gtk-2.0/assets.txt",
            file=sys.stderr,
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
