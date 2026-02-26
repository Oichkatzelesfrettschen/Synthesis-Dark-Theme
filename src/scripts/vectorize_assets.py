#!/usr/bin/env python3
"""
Synthesis-Dark Asset Vectorization Pipeline

Converts pre-rendered PNG assets to SVG source files using potrace.
This establishes SVG as the source of truth for all theme assets.

Usage:
    python3 vectorize_assets.py --input assets/ --output src/assets/gtk3-4/

Requirements:
    - potrace (bitmap to vector)
    - ImageMagick (preprocessing)
    - svgo (SVG optimization, optional)
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def preprocess_png(input_png: Path, temp_pbm: Path) -> bool:
    """Convert PNG to PBM format for potrace."""
    try:
        # Convert to grayscale PBM, threshold for clean lines
        subprocess.run([
            'convert', str(input_png),
            '-colorspace', 'Gray',
            '-threshold', '50%',
            '-negate',  # Invert for potrace (black on white)
            str(temp_pbm)
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR preprocessing {input_png.name}: {e}")
        return False


def vectorize_to_svg(temp_pbm: Path, output_svg: Path, original_png: Path) -> bool:
    """Convert PBM to SVG using potrace."""
    try:
        # Get original dimensions for proper sizing
        result = subprocess.run([
            'identify', '-format', '%w %h', str(original_png)
        ], check=True, capture_output=True, text=True)
        width, height = map(int, result.stdout.strip().split())

        # Run potrace with optimized settings for UI elements
        subprocess.run([
            'potrace',
            str(temp_pbm),
            '-s',              # SVG output
            '-t', '1',         # Turdsize: suppress small features
            '-a', '1.5',       # Corner threshold
            '-O', '0.1',       # Curve optimization
            '--group',         # Group paths
            '-W', str(width),  # Match original width
            '-H', str(height), # Match original height
            '-o', str(output_svg)
        ], check=True, capture_output=True)

        # Optimize SVG if svgo is available
        if os.path.exists('/usr/bin/svgo'):
            subprocess.run([
                'svgo', str(output_svg),
                '-o', str(output_svg),
                '--multipass'
            ], check=True, capture_output=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR vectorizing {temp_pbm.name}: {e}")
        return False


def process_asset(input_png: Path, output_dir: Path) -> tuple:
    """Process a single PNG asset to SVG."""
    # Skip @2x assets (HiDPI) - they're rendered from same SVG
    if '@2' in input_png.name:
        return (input_png.name, 'skipped', 'HiDPI variant')

    output_svg = output_dir / input_png.name.replace('.png', '.svg')
    temp_pbm = output_dir / input_png.name.replace('.png', '.pbm')

    try:
        if not preprocess_png(input_png, temp_pbm):
            return (input_png.name, 'failed', 'preprocessing')

        if not vectorize_to_svg(temp_pbm, output_svg, input_png):
            return (input_png.name, 'failed', 'vectorization')

        # Cleanup temp file
        if temp_pbm.exists():
            temp_pbm.unlink()

        return (input_png.name, 'success', str(output_svg))
    except Exception as e:
        return (input_png.name, 'failed', str(e))


def main():
    parser = argparse.ArgumentParser(
        description='Vectorize PNG assets to SVG sources'
    )
    parser.add_argument('--input', required=True, help='Input directory with PNGs')
    parser.add_argument('--output', required=True, help='Output directory for SVGs')
    parser.add_argument('--workers', type=int, default=4, help='Parallel workers')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    args = parser.parse_args()
    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all PNG files (excluding @2x variants)
    png_files = list(input_dir.glob('*.png'))
    base_files = [f for f in png_files if '@2' not in f.name]

    print("=== Synthesis-Dark Asset Vectorization ===")
    print(f"Input:  {input_dir} ({len(base_files)} base assets, {len(png_files)} total)")
    print(f"Output: {output_dir}")
    print()

    if args.dry_run:
        for f in base_files[:10]:
            print(f"  Would vectorize: {f.name}")
        if len(base_files) > 10:
            print(f"  ... and {len(base_files) - 10} more")
        return

    # Process assets in parallel
    success = 0
    failed = 0
    skipped = 0

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_asset, png, output_dir): png
            for png in png_files
        }

        for future in as_completed(futures):
            name, status, detail = future.result()
            if status == 'success':
                print(f"  [OK] {name}")
                success += 1
            elif status == 'skipped':
                skipped += 1
            else:
                print(f"  [FAIL] {name}: {detail}")
                failed += 1

    print()
    print("=== Complete ===")
    print(f"Success: {success}, Skipped: {skipped}, Failed: {failed}")


if __name__ == "__main__":
    main()
