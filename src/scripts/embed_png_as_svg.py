#!/usr/bin/env python3
"""
Wrap a PNG inside an SVG container while preserving exact raster visuals.
"""

import argparse
import base64
from pathlib import Path

from PIL import Image


def wrap_png_as_svg(input_png: Path, output_svg: Path) -> None:
    """Embed a PNG as a data URI inside an SVG with matching dimensions."""
    with Image.open(input_png) as image:
        width, height = image.size

    encoded = base64.b64encode(input_png.read_bytes()).decode('ascii')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <image width="{width}" height="{height}" href="data:image/png;base64,{encoded}"/>
</svg>
'''

    output_svg.parent.mkdir(parents=True, exist_ok=True)
    output_svg.write_text(svg, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Wrap PNG rasters into SVG containers')
    parser.add_argument('input_png', type=Path, help='Input PNG asset')
    parser.add_argument('output_svg', type=Path, help='Output SVG path')
    args = parser.parse_args()

    wrap_png_as_svg(args.input_png, args.output_svg)


if __name__ == '__main__':
    main()
