#!/usr/bin/env python3
"""
Promote raster-wrapper authorities only where native SVGs still drift visually.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from raster_wrapper_preferences import PREFERRED_AUTHORITIES_PATH


DEFAULT_PARITY_JSON = Path('/tmp/synthesis-dark-svg-parity.json')
DEFAULT_REPORT_MARKDOWN = Path('docs/SVG_FIDELITY_RECONCILIATION.md')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Reconcile native SVG drift with wrapper overrides')
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    parser.add_argument('--parity-json', type=Path, default=DEFAULT_PARITY_JSON)
    parser.add_argument('--output-json', type=Path, default=PREFERRED_AUTHORITIES_PATH)
    parser.add_argument('--report-markdown', type=Path, default=DEFAULT_REPORT_MARKDOWN)
    return parser.parse_args()


def collect_override_candidates(repo_root: Path, payload: dict) -> list[dict]:
    """Return native-SVG mismatches that can fall back to exact wrapper authorities."""
    candidates = []
    for entry in payload['results']:
        if entry['parity_status'] != 'mismatch':
            continue
        source_authority = entry.get('source_authority') or ''
        if source_authority.startswith('src/raster_wrappers/'):
            continue
        wrapper = repo_root / 'src' / 'raster_wrappers' / Path(entry['relative_png']).with_suffix('.svg')
        if not wrapper.exists():
            continue
        candidates.append(
            {
                'relative_png': entry['relative_png'],
                'native_authority': source_authority,
                'preferred_authority': wrapper.relative_to(repo_root).as_posix(),
                'normalized_rmse': entry.get('normalized_rmse'),
                'differing_ratio': entry.get('differing_ratio'),
                'family': entry.get('family'),
            }
        )
    return sorted(candidates, key=lambda item: item['relative_png'])


def render_markdown_report(candidates: list[dict]) -> str:
    by_family = Counter(item['family'] for item in candidates)
    lines = [
        '# SVG Fidelity Reconciliation',
        '',
        '## Summary',
        f"- Preferred-authority overrides emitted: `{len(candidates)}`",
        '',
        '## By Family',
    ]
    if by_family:
        for family, count in sorted(by_family.items()):
            lines.append(f"- `{family}`: `{count}`")
    else:
        lines.append('- None')

    lines.extend([
        '',
        '## Overrides',
    ])
    if candidates:
        for item in candidates:
            lines.append(
                f"- `{item['relative_png']}`: `{item['native_authority']}` -> "
                f"`{item['preferred_authority']}` "
                f"(rmse `{item['normalized_rmse']}`, differing ratio `{item['differing_ratio']}`)"
            )
    else:
        lines.append('- None')
    return '\n'.join(lines) + '\n'


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    payload = json.loads(args.parity_json.resolve().read_text(encoding='utf-8'))
    candidates = collect_override_candidates(repo_root, payload)
    overrides = {
        item['relative_png']: item['preferred_authority']
        for item in candidates
    }

    output_json = (repo_root / args.output_json).resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(overrides, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    report_markdown = (repo_root / args.report_markdown).resolve()
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.write_text(render_markdown_report(candidates), encoding='utf-8')

    print('=== Synthesis-Dark SVG Fidelity Reconciliation ===')
    print(f'Overrides written: {len(overrides)}')
    print(f'JSON: {output_json}')
    print(f'Markdown: {report_markdown}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
