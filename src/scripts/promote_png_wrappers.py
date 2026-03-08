#!/usr/bin/env python3
"""
Promote PNG assets into self-contained SVG wrapper authorities.

This is the conservative reproducibility fallback layer:
- if a direct vector authority is visually faithful, keep using it
- if not, embed the shipped PNG into an SVG so the repo can move toward
  SVG-authoritative sources without losing pixel fidelity
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from embed_png_as_svg import wrap_png_as_svg


DEFAULT_PARITY_JSON = Path('/tmp/synthesis-dark-svg-parity.json')
DEFAULT_MANIFEST_JSON = Path('/tmp/synthesis-dark-svg-migration.json')
DEFAULT_OUTPUT_ROOT = Path('src/raster_wrappers')
PROMOTABLE_PARITY_STATUSES = {
    'mismatch',
    'close',
    'error',
    'specialized-renderer',
}
PROMOTABLE_MANIFEST_PRIORITIES = {
    'icon-family-reconciliation',
    'non-icon-first',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Promote PNGs into SVG wrapper authorities')
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path('.'),
        help='Repository root',
    )
    parser.add_argument(
        '--parity-json',
        type=Path,
        default=DEFAULT_PARITY_JSON,
        help='Parity audit JSON from verify_svg_parity.py',
    )
    parser.add_argument(
        '--manifest-json',
        type=Path,
        default=DEFAULT_MANIFEST_JSON,
        help='Manifest JSON from vectorize_assets.py for unresolved PNG queues',
    )
    parser.add_argument(
        '--output-root',
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help='Where to place mirrored SVG wrapper authorities',
    )
    parser.add_argument(
        '--statuses',
        nargs='*',
        default=sorted(PROMOTABLE_PARITY_STATUSES),
        help='Parity statuses to promote into wrapper authorities',
    )
    parser.add_argument(
        '--priorities',
        nargs='*',
        default=sorted(PROMOTABLE_MANIFEST_PRIORITIES),
        help='Manifest batch priorities to promote into wrapper authorities',
    )
    parser.add_argument(
        '--include-reference',
        action='store_true',
        help='Also wrap reference rasters if they appear in the parity report',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing wrapper SVGs',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Report what would be wrapped without writing files',
    )
    parser.add_argument(
        '--report-json',
        type=Path,
        help='Optional JSON report output',
    )
    parser.add_argument(
        '--report-markdown',
        type=Path,
        help='Optional Markdown report output',
    )
    return parser.parse_args()


def wrapper_path(output_root: Path, relative_png: str) -> Path:
    return output_root / Path(relative_png).with_suffix('.svg')


def should_promote(entry: dict, statuses: set[str], include_reference: bool) -> bool:
    if entry['parity_status'] not in statuses:
        return False
    if not include_reference and entry['family'] in {'Art', 'docs', 'upstream'}:
        return False
    return True


def parity_candidates(payload: dict, statuses: set[str], include_reference: bool) -> dict[str, dict]:
    candidates = {}
    for entry in payload['results']:
        if not should_promote(entry, statuses, include_reference):
            continue
        candidates[entry['relative_png']] = {
            'relative_png': entry['relative_png'],
            'family': entry['family'],
            'reason': entry['parity_status'],
        }
    return candidates


def manifest_candidates(payload: list[dict], priorities: set[str], include_reference: bool) -> dict[str, dict]:
    candidates = {}
    for entry in payload:
        if entry['batch_priority'] not in priorities:
            continue
        if not include_reference and entry['family'] in {'Art', 'docs', 'upstream'}:
            continue
        candidates[entry['relative_png']] = {
            'relative_png': entry['relative_png'],
            'family': entry['family'],
            'reason': entry['batch_priority'],
        }
    return candidates


def promote_wrappers(
    repo_root: Path,
    output_root: Path,
    candidates: dict[str, dict],
    force: bool,
    dry_run: bool,
) -> dict:
    promoted = []
    skipped_existing = []

    for relative_png, entry in sorted(candidates.items()):
        relative_png = entry['relative_png']
        input_png = repo_root / relative_png
        output_svg = wrapper_path(output_root, relative_png)

        if output_svg.exists() and not force:
            skipped_existing.append(relative_png)
            continue

        if not dry_run:
            output_svg.parent.mkdir(parents=True, exist_ok=True)
            wrap_png_as_svg(input_png, output_svg)

        promoted.append({
            'relative_png': relative_png,
            'wrapper_svg': output_svg.as_posix(),
            'promotion_reason': entry['reason'],
            'family': entry['family'],
        })

    by_reason = Counter(item['promotion_reason'] for item in promoted)
    by_family = Counter(item['family'] for item in promoted)
    return {
        'promoted_count': len(promoted),
        'skipped_existing_count': len(skipped_existing),
        'by_reason': dict(by_reason),
        'by_family': dict(by_family),
        'promoted': promoted,
        'skipped_existing': skipped_existing,
    }


def render_markdown_report(summary: dict, output_root: Path, dry_run: bool) -> str:
    lines = [
        '# PNG Wrapper Promotion Report',
        '',
        '## Summary',
        f"- Output root: `{output_root}`",
        f"- Dry run: `{'yes' if dry_run else 'no'}`",
        f"- Wrapper SVGs promoted this run: `{summary['promoted_count']}`",
        f"- Existing wrapper SVGs skipped: `{summary['skipped_existing_count']}`",
        '',
        '## By Promotion Reason',
    ]
    if summary['by_reason']:
        for status, count in sorted(summary['by_reason'].items()):
            lines.append(f"- `{status}`: `{count}`")
    else:
        lines.append('- None')

    lines.extend([
        '',
        '## By Family',
    ])
    if summary['by_family']:
        for family, count in sorted(summary['by_family'].items()):
            lines.append(f"- `{family}`: `{count}`")
    else:
        lines.append('- None')

    lines.extend([
        '',
        '## Decision',
        '- These wrapper SVGs preserve shipped pixel output exactly by embedding the PNG payload.',
        '- They are a reproducibility fallback, not the end-state shared-geometry solution.',
        '- After promotion, runtime references can be rewired toward SVG while preserving render fidelity.',
    ])
    return '\n'.join(lines) + '\n'


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_root = (repo_root / args.output_root).resolve()
    parity_json = args.parity_json.resolve()
    manifest_json = args.manifest_json.resolve()

    payload = json.loads(parity_json.read_text(encoding='utf-8'))
    manifest_payload = json.loads(manifest_json.read_text(encoding='utf-8'))
    statuses = set(args.statuses)
    priorities = set(args.priorities)
    candidates = parity_candidates(payload, statuses, args.include_reference)
    candidates.update(manifest_candidates(manifest_payload, priorities, args.include_reference))
    summary = promote_wrappers(
        repo_root=repo_root,
        output_root=output_root,
        candidates=candidates,
        force=args.force,
        dry_run=args.dry_run,
    )

    print('=== Synthesis-Dark PNG Wrapper Promotion ===')
    print(f"Output root: {output_root}")
    print(f"Dry run: {'yes' if args.dry_run else 'no'}")
    print(f"Promoted: {summary['promoted_count']}")
    print(f"Skipped existing: {summary['skipped_existing_count']}")
    for status, count in sorted(summary['by_reason'].items()):
        print(f"{status}: {count}")

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(f"Wrote JSON report: {args.report_json}")

    if args.report_markdown:
        args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.report_markdown.write_text(
            render_markdown_report(summary, output_root, args.dry_run),
            encoding='utf-8',
        )
        print(f"Wrote Markdown report: {args.report_markdown}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
