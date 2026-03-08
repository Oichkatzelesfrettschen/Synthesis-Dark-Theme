#!/usr/bin/env python3
"""
Promote SVG-backed icon semantic IDs into the shared icon backend.
"""

import argparse
import json
import shutil
from pathlib import Path

import vectorize_assets as va


def semantic_parts(semantic_id: str) -> tuple[str, str]:
    """Extract the icon category and stem from a semantic ID."""
    parts = semantic_id.split('/')
    if len(parts) < 3:
        raise ValueError(f"Unsupported semantic ID: {semantic_id}")
    return parts[1], parts[2]


def geometry_target_path(backend_root: Path, semantic_id: str) -> Path:
    """Return the target geometry SVG path for a semantic ID."""
    category, stem = semantic_parts(semantic_id)
    return backend_root / 'geometry' / category / f'{stem}.svg'


def skin_metadata_path(backend_root: Path, semantic_id: str, style_skin: str) -> Path:
    """Return the skin metadata path for a semantic ID."""
    category, stem = semantic_parts(semantic_id)
    return backend_root / 'skins' / style_skin / category / f'{stem}.json'


def unresolved_work_item_path(backend_root: Path, semantic_id: str, style_skin: str) -> Path:
    """Return the unresolved registry work-item path for a semantic ID."""
    category, stem = semantic_parts(semantic_id)
    return backend_root / 'registry' / 'unresolved' / style_skin / category / f'{stem}.json'


def clear_generated_backend_files(backend_root: Path) -> None:
    """Remove generated backend artifacts so promotion output stays current."""
    for path in (backend_root / 'geometry').rglob('*.svg'):
        path.unlink()
    for path in (backend_root / 'skins').rglob('*.json'):
        path.unlink()
    registry_dir = backend_root / 'registry'
    if registry_dir.exists():
        shutil.rmtree(registry_dir)
    aliases_path = backend_root / 'aliases' / 'installed-output-aliases.json'
    if aliases_path.exists():
        aliases_path.unlink()


def find_unresolved_seed_candidate(repo_root: Path, semantic_id: str) -> str | None:
    """Return the best available SVG seed candidate for an unresolved icon."""
    category, stem = semantic_parts(semantic_id)
    for candidate in va.icon_authority_candidates(repo_root, category, stem):
        if candidate.exists():
            return va._path_to_str(candidate.relative_to(repo_root))
    return None


def build_alias_map(icon_registry: list[dict]) -> dict:
    """Build installed-output aliases keyed to semantic IDs."""
    aliases = {}
    for item in icon_registry:
        for output in item['installed_outputs']:
            aliases[output] = {
                'semantic_id': item['semantic_id'],
                'style_skin': item['style_skin'],
            }
    return aliases


def promote_svg_backed_icons(
    icon_registry: list[dict],
    backend_root: Path,
    repo_root: Path,
    min_seed_outputs: int,
) -> dict:
    """Copy SVG-backed semantic IDs into the backend geometry and skin metadata."""
    promoted = []
    unresolved = {'mate': [], 'tela': [], 'n/a': []}
    unresolved_work_items = 0
    seed_promoted = 0

    registry_dir = backend_root / 'registry'
    clear_generated_backend_files(backend_root)
    registry_dir.mkdir(parents=True, exist_ok=True)
    (backend_root / 'aliases').mkdir(parents=True, exist_ok=True)

    for item in icon_registry:
        source_authority = None
        source_kind = 'authoritative-svg'

        if item['has_authoritative_svg']:
            source_authority = item['authoritative_svg_candidates'][0]
        elif item['installed_output_count'] >= min_seed_outputs:
            source_authority = find_unresolved_seed_candidate(repo_root, item['semantic_id'])
            source_kind = 'geometry-seed'

        if source_authority is None:
            unresolved.setdefault(item['style_skin'], []).append(item)
            continue

        source = repo_root / source_authority
        geometry_path = geometry_target_path(backend_root, item['semantic_id'])
        skin_path = skin_metadata_path(backend_root, item['semantic_id'], item['style_skin'])
        geometry_path.parent.mkdir(parents=True, exist_ok=True)
        skin_path.parent.mkdir(parents=True, exist_ok=True)

        if source.resolve() != geometry_path.resolve():
            shutil.copy2(source, geometry_path)

        metadata = {
            'semantic_id': item['semantic_id'],
            'style_skin': item['style_skin'],
            'category': item['category'],
            'geometry_svg': va._path_to_str(geometry_path.relative_to(backend_root)),
            'source_authority': source_authority,
            'source_kind': source_kind,
            'installed_outputs': item['installed_outputs'],
        }
        skin_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding='utf-8')
        promoted.append(metadata)
        if source_kind == 'geometry-seed':
            seed_promoted += 1

    alias_map = build_alias_map(icon_registry)
    (backend_root / 'aliases' / 'installed-output-aliases.json').write_text(
        json.dumps(alias_map, indent=2, sort_keys=True) + "\n",
        encoding='utf-8',
    )
    (registry_dir / 'promoted-icons.json').write_text(
        json.dumps(promoted, indent=2) + "\n",
        encoding='utf-8',
    )

    unresolved_index = []
    for skin, items in unresolved.items():
        (backend_root / 'skins' / skin).mkdir(parents=True, exist_ok=True)
        unresolved_path = backend_root / 'skins' / skin / 'unresolved.json'
        unresolved_payload = [
            {
                'semantic_id': item['semantic_id'],
                'category': item['category'],
                'installed_output_count': item['installed_output_count'],
                'installed_outputs': item['installed_outputs'],
                'registry_work_item': va._path_to_str(
                    unresolved_work_item_path(backend_root, item['semantic_id'], item['style_skin']).relative_to(backend_root)
                ),
            }
            for item in items
        ]
        unresolved_path.write_text(
            json.dumps(unresolved_payload, indent=2) + "\n",
            encoding='utf-8',
        )

        for item in items:
            work_item_path = unresolved_work_item_path(backend_root, item['semantic_id'], item['style_skin'])
            work_item_path.parent.mkdir(parents=True, exist_ok=True)
            work_item = {
                'semantic_id': item['semantic_id'],
                'style_skin': item['style_skin'],
                'category': item['category'],
                'status': 'needs-authoritative-geometry',
                'suggested_geometry_svg': va._path_to_str(
                    geometry_target_path(backend_root, item['semantic_id']).relative_to(backend_root)
                ),
                'suggested_skin_metadata': va._path_to_str(
                    skin_metadata_path(backend_root, item['semantic_id'], item['style_skin']).relative_to(backend_root)
                ),
                'installed_output_count': item['installed_output_count'],
                'installed_outputs': item['installed_outputs'],
                'authoritative_svg_candidates': item['authoritative_svg_candidates'],
            }
            work_item_path.write_text(
                json.dumps(work_item, indent=2) + "\n",
                encoding='utf-8',
            )
            unresolved_index.append(
                {
                    'semantic_id': item['semantic_id'],
                    'style_skin': item['style_skin'],
                    'category': item['category'],
                    'registry_work_item': va._path_to_str(work_item_path.relative_to(backend_root)),
                }
            )
            unresolved_work_items += 1

    (registry_dir / 'unresolved-index.json').write_text(
        json.dumps(sorted(unresolved_index, key=lambda item: item['semantic_id']), indent=2) + "\n",
        encoding='utf-8',
    )

    return {
        'promoted': len(promoted),
        'seed_promoted': seed_promoted,
        'unresolved': {skin: len(items) for skin, items in unresolved.items()},
        'unresolved_work_items': unresolved_work_items,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Promote SVG-backed icon semantic IDs into src/icons_backend'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help='Repository root',
    )
    parser.add_argument(
        '--backend-root',
        type=Path,
        default=None,
        help='Backend root (default: <repo>/src/icons_backend)',
    )
    parser.add_argument(
        '--report-output',
        type=Path,
        default=Path('/tmp/synthesis-dark-svg-migration'),
        help='Scratch output root used for manifest discovery',
    )
    parser.add_argument(
        '--min-seed-outputs',
        type=int,
        default=5,
        help='Only promote unresolved same-stem seed candidates when they fan out to at least this many installed outputs',
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    backend_root = args.backend_root.resolve() if args.backend_root else repo_root / 'src' / 'icons_backend'

    manifest = va.build_asset_manifest(
        repo_root,
        args.report_output,
        recursive=True,
        include_existing_svg=False,
    )
    icon_registry = va.build_icon_registry(manifest)
    summary = promote_svg_backed_icons(
        icon_registry,
        backend_root,
        repo_root,
        min_seed_outputs=args.min_seed_outputs,
    )

    print(f"Promoted SVG-backed semantic IDs: {summary['promoted']}")
    print(f"Promoted unresolved seed candidates: {summary['seed_promoted']}")
    print(f"Unresolved work items: {summary['unresolved_work_items']}")
    for skin, count in sorted(summary['unresolved'].items()):
        print(f"Unresolved {skin}: {count}")


if __name__ == '__main__':
    main()
