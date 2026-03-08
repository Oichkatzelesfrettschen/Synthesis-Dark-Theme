#!/usr/bin/env python3
"""
Materialize runtime SVG siblings for theme PNG assets.

This bridges source-authority SVGs living under src/ into the actual runtime
asset directories consumed by GTK and GNOME Shell, and it also materializes
explicit runtime SVGs that can be derived from source sheets or safe aliases.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import shutil
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from embed_png_as_svg import wrap_png_as_svg
from raster_wrapper_preferences import preferred_authority_for


DEFAULT_MANIFEST_JSON = Path('/tmp/synthesis-dark-svg-migration.json')
INKSCAPE = 'inkscape'
INKSCAPE_NS = '{http://www.inkscape.org/namespaces/inkscape}'
SVG_NS = '{http://www.w3.org/2000/svg}'
SELECTION_SHEET = Path('gtk-3.20/assets/gtk3-selection.svg')

SELECTION_MODE_CHECKBOX_EXPORTS = {
    'selection-mode-checkbox-checked',
    'selection-mode-checkbox-checked-active',
    'selection-mode-checkbox-checked-backdrop',
    'selection-mode-checkbox-checked-hover',
    'selection-mode-checkbox-unchecked',
    'selection-mode-checkbox-unchecked-active',
    'selection-mode-checkbox-unchecked-backdrop',
    'selection-mode-checkbox-unchecked-hover',
}

SELECTION_MODE_SVG_ALIASES = {
    'assets/selection-mode-checkbox-unchecked-insensitive.svg': 'assets/checkbox-unchecked-insensitive.svg',
    'assets/selection-mode-checkbox-unchecked-backdrop-insensitive.svg': 'assets/checkbox-unchecked-insensitive-backdrop.svg',
    'assets/selection-mode-radio-unchecked.svg': 'assets/radio-unchecked.svg',
    'assets/selection-mode-radio-unchecked-hover.svg': 'assets/radio-unchecked-hover.svg',
    'assets/selection-mode-radio-unchecked-active.svg': 'assets/radio-unchecked-active.svg',
    'assets/selection-mode-radio-unchecked-backdrop.svg': 'assets/radio-unchecked-backdrop.svg',
    'assets/selection-mode-radio-unchecked-insensitive.svg': 'assets/radio-unchecked-insensitive.svg',
    'assets/selection-mode-radio-unchecked-backdrop-insensitive.svg': 'assets/radio-unchecked-insensitive-backdrop.svg',
}

EXPLICIT_WRAPPED_RUNTIME_PNGS = {
    'gnome-shell/assets/noise-texture.svg': 'gnome-shell/assets/noise-texture.png',
}

METACITY_THEME_XMLS = (
    Path('metacity-1/metacity-theme.xml'),
    Path('metacity-1/metacity-theme-1.xml'),
    Path('metacity-1/metacity-theme-2.xml'),
    Path('metacity-1/metacity-theme-3.xml'),
)
RUNTIME_SVG_PREFIXES = (
    ('assets',),
    ('gnome-shell', 'assets'),
    ('cinnamon', 'common-assets', 'misc'),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Materialize runtime SVG siblings for assets/*.png')
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    parser.add_argument('--manifest-json', type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--report-json', type=Path)
    return parser.parse_args()


def choose_svg_source(repo_root: Path, entry: dict) -> tuple[str, Path | None]:
    relative_png = entry['relative_png']
    preferred_authority = preferred_authority_for(repo_root, Path(relative_png))
    if preferred_authority is not None:
        return 'preferred-authority', preferred_authority

    runtime_svg = repo_root / Path(relative_png).with_suffix('.svg')
    if runtime_svg.exists():
        return 'existing-runtime-svg', runtime_svg

    source_authority = entry.get('source_authority')
    if source_authority:
        source_path = repo_root / source_authority
        if source_path.exists() and source_path.suffix == '.svg':
            return 'source-authority', source_path

    wrapper = repo_root / 'src' / 'raster_wrappers' / Path(relative_png).with_suffix('.svg')
    if wrapper.exists():
        return 'raster-wrapper', wrapper

    return 'wrap-png', None


def should_materialize_runtime_svg(relative_png: Path) -> bool:
    """Return whether this PNG participates in runtime SVG materialization."""
    for prefix in RUNTIME_SVG_PREFIXES:
        if relative_png.parts[:len(prefix)] == prefix:
            return True
    return False


def export_svg_fragment(svg_source: Path, fragment_id: str, output_path: Path) -> None:
    subprocess.run(
        [
            INKSCAPE,
            str(svg_source),
            f'--export-id={fragment_id}',
            '--export-id-only',
            '--export-type=svg',
            f'--export-filename={output_path}',
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def load_baseplate_rects(svg_path: Path) -> dict[str, str]:
    root = ET.fromstring(svg_path.read_text(encoding='utf-8'))
    baseplates: dict[str, str] = {}
    for group in root.iter(f'{SVG_NS}g'):
        if group.attrib.get(f'{INKSCAPE_NS}groupmode') != 'layer':
            continue
        label = group.attrib.get(f'{INKSCAPE_NS}label', '')
        if not label.startswith('Baseplate '):
            continue

        icon_name = None
        rect_id = None
        for child in group:
            child_label = child.attrib.get(f'{INKSCAPE_NS}label')
            if child.tag == f'{SVG_NS}text' and child_label == 'icon-name':
                icon_name = ''.join(child.itertext()).strip()
            if child.tag == f'{SVG_NS}rect' and rect_id is None:
                rect_id = child.attrib.get('id')

        if icon_name and rect_id:
            baseplates[icon_name] = rect_id

    return baseplates


def materialize_explicit_runtime_svgs(
    repo_root: Path,
    force: bool,
    dry_run: bool,
    exporter=export_svg_fragment,
) -> list[dict]:
    materialized: list[dict] = []

    selection_sheet = repo_root / SELECTION_SHEET
    if selection_sheet.exists():
        baseplates = load_baseplate_rects(selection_sheet)
        for icon_name in sorted(SELECTION_MODE_CHECKBOX_EXPORTS):
            rect_id = baseplates.get(icon_name)
            if rect_id is None:
                continue
            relative_svg = Path('assets') / f'{icon_name}.svg'
            output_path = repo_root / relative_svg
            if output_path.exists() and not force:
                continue
            if not dry_run:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                exporter(selection_sheet, rect_id, output_path)
            materialized.append(
                {
                    'relative_svg': relative_svg.as_posix(),
                    'source_kind': 'selection-sheet-export',
                    'source_path': SELECTION_SHEET.as_posix(),
                    'fragment_id': rect_id,
                }
            )

    for relative_svg, relative_source in sorted(SELECTION_MODE_SVG_ALIASES.items()):
        output_path = repo_root / relative_svg
        source_path = repo_root / relative_source
        if not source_path.exists():
            continue
        if output_path.exists() and not force:
            continue
        if not dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, output_path)
        materialized.append(
            {
                'relative_svg': relative_svg,
                'source_kind': 'svg-alias-copy',
                'source_path': relative_source,
                'fragment_id': None,
            }
        )

    for relative_svg, relative_png in sorted(EXPLICIT_WRAPPED_RUNTIME_PNGS.items()):
        output_path = repo_root / relative_svg
        source_path = repo_root / relative_png
        if not source_path.exists():
            continue
        if output_path.exists() and not force:
            continue
        if not dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            wrap_png_as_svg(source_path, output_path)
        materialized.append(
            {
                'relative_svg': relative_svg,
                'source_kind': 'wrap-png-explicit',
                'source_path': relative_png,
                'fragment_id': None,
            }
        )

    for source_path, output_path in load_metacity_runtime_assets(repo_root):
        relative_png = source_path.relative_to(repo_root)
        relative_svg = output_path.relative_to(repo_root)
        if not source_path.exists():
            continue
        if output_path.exists() and not force:
            continue
        if not dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            wrap_png_as_svg(source_path, output_path)
        materialized.append(
            {
                'relative_svg': relative_svg.as_posix(),
                'source_kind': 'metacity-wrap-png',
                'source_path': relative_png.as_posix(),
                'fragment_id': None,
            }
        )

    return materialized


def load_metacity_runtime_assets(repo_root: Path) -> list[tuple[Path, Path]]:
    references: set[tuple[Path, Path]] = set()
    for relative_xml in METACITY_THEME_XMLS:
        xml_path = repo_root / relative_xml
        if not xml_path.exists():
            continue
        for match in re.finditer(r'filename="([^"]+)\.(png|svg)"', xml_path.read_text(encoding='utf-8')):
            base = match.group(1)
            source_png = repo_root / 'metacity-1' / f'{base}.png'
            output_svg = repo_root / 'metacity-1' / f'{base}.svg'
            if source_png.exists():
                references.add((source_png, output_svg))
    return sorted(references)


def materialize_runtime_svgs(
    repo_root: Path,
    manifest: list[dict],
    force: bool,
    dry_run: bool,
) -> dict:
    summary = {
        'materialized': [],
        'skipped_existing': [],
    }

    for entry in manifest:
        relative_png = Path(entry['relative_png'])
        if '@2' in relative_png.name:
            continue
        if not should_materialize_runtime_svg(relative_png):
            continue

        runtime_svg = repo_root / relative_png.with_suffix('.svg')
        if runtime_svg.exists() and not force:
            summary['skipped_existing'].append(relative_png.as_posix())
            continue

        source_kind, source_path = choose_svg_source(repo_root, entry)
        if not dry_run:
            runtime_svg.parent.mkdir(parents=True, exist_ok=True)
            if source_kind == 'wrap-png':
                wrap_png_as_svg(repo_root / relative_png, runtime_svg)
            elif source_path == runtime_svg:
                pass
            else:
                shutil.copyfile(source_path, runtime_svg)

        summary['materialized'].append({
            'relative_png': relative_png.as_posix(),
            'runtime_svg': runtime_svg.as_posix(),
            'source_kind': source_kind,
            'source_path': source_path.as_posix() if source_path else None,
        })

    for item in materialize_explicit_runtime_svgs(
        repo_root=repo_root,
        force=force,
        dry_run=dry_run,
    ):
        summary['materialized'].append(
            {
                'relative_png': None,
                'runtime_svg': str(repo_root / item['relative_svg']),
                'source_kind': item['source_kind'],
                'source_path': item['source_path'],
                'fragment_id': item['fragment_id'],
            }
        )

    summary['materialized_count'] = len(summary['materialized'])
    summary['skipped_existing_count'] = len(summary['skipped_existing'])
    summary['by_source_kind'] = dict(
        Counter(item['source_kind'] for item in summary['materialized'])
    )
    return summary


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    manifest = json.loads(args.manifest_json.resolve().read_text(encoding='utf-8'))
    summary = materialize_runtime_svgs(
        repo_root=repo_root,
        manifest=manifest,
        force=args.force,
        dry_run=args.dry_run,
    )

    print('=== Synthesis-Dark Runtime SVG Materialization ===')
    print(f"Dry run: {'yes' if args.dry_run else 'no'}")
    print(f"Materialized: {summary['materialized_count']}")
    print(f"Skipped existing: {summary['skipped_existing_count']}")
    for kind, count in sorted(summary['by_source_kind'].items()):
        print(f"{kind}: {count}")

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(f"Wrote JSON report: {args.report_json}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
