"""TOOLKIT-011 bounded research report; never imported by production allocation.

The upstream tail is a candidate, not a free-region declaration. This report
cannot promote it, resolve numeric matches, or establish complete ROM ownership.
Run with an explicit canonical ROM path; stdout contains metadata only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import struct

from tools.webfoot.binary import FileOffset, GbaRomAddress
from tools.webfoot.document import RomDocument
from tools.webfoot.entities import load_placement_types
from tools.webfoot.graphics import load_actor_sprites
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfileCatalog, VerificationStatus
from tools.webfoot.rom import identify_rom


def candidate_report(image, span, owned, references):
    """Bounded byte-pattern and all-byte u32 audit, with no promotion output.

    owned records are annotations; overlaps are retained, not silently merged.
    references carry source, target and the existing evidence classification.
    Numeric observations stay separate because overlapping source windows cannot
    all be inserted into the production graph as authoritative fields.
    """
    span.validate(len(image))
    known_sources = {r['source'] for r in references}
    hits = []
    for source in range(len(image) - 3):
        raw = struct.unpack_from('<I', image, source)[0]
        try:
            target = GbaRomAddress(raw).to_file_offset(len(image))
        except ValueError:
            continue
        if span.contains(FileOffset(target)) and source not in known_sources:
            hits.append({'source': source, 'target': target,
                         'classification': 'CANDIDATE_REFERENCE',
                         'source_word_aligned': source % 4 == 0})
    inbound = [r for r in references if span.contains(FileOffset(r['target']))]
    overlaps = [r for r in owned if r['start'] < span.end and r['end'] > span.start.value]
    left = [r for r in owned if r['end'] <= span.start.value]
    right = [r for r in owned if r['start'] >= span.end]
    return {
        'status': 'CANDIDATE', 'start': span.start.value, 'end': span.end,
        'size': span.size, 'byte_histogram': dict(sorted(Counter(image[span.start.value:span.end]).items())),
        'neighbor_before': max(left, key=lambda r: (r['end'], r['start'], r['owner']), default=None),
        'neighbor_after': min(right, key=lambda r: (r['start'], r['end'], r['owner']), default=None),
        'known_overlaps': overlaps, 'known_inbound': inbound,
        'reference_counts': dict(sorted(Counter(r['classification'] for r in inbound + hits).items())),
        'candidate_word_aligned_count': sum(r['source_word_aligned'] for r in hits),
        'candidate_observations': hits,
        'reasons_candidate_only': [
            'Upstream copies the tail with INCBIN; no independent unused-section proof.',
            'Unresolved numeric observations are not whitelisted.',
            'Known ownership is incomplete; absent coverage is UNKNOWN, not free.',
            'Computed references, unknown container extents and signature uses are not ruled out.',
        ],
    }


def occupancy(size, owned):
    """Deterministic disjoint coverage, retaining all overlapping annotations."""
    events = {0: [], size: []}
    records = sorted(owned, key=lambda r: (r['start'], r['end'], r['kind'], r['owner']))
    for index, row in enumerate(records):
        RomRange(FileOffset(row['start']), row['end'] - row['start']).validate(size)
        events.setdefault(row['start'], []).append((index, True))
        events.setdefault(row['end'], []).append((index, False))
    active = set()
    result = []
    points = sorted(events)
    for start, end in zip(points, points[1:]):
        for index, entering in events[start]:
            if entering:
                active.add(index)
            else:
                active.remove(index)
        result.append({'start': start, 'end': end,
                       'annotations': sorted(active),
                       'coverage': 'KNOWN_ANNOTATION' if active else 'UNKNOWN'})
    return {'annotations': records, 'segments': result}


def audit(path):
    catalog = RomProfileCatalog.load(Path(__file__).resolve().parents[1] / 'webfoot/data/roms.yaml')
    identification = identify_rom(path, catalog)
    profile = identification.profile_match.profile
    if (identification.profile_match.status is not VerificationStatus.VERIFIED
            or profile.id != 'buus_fury_usa_rev0_01c1707f'):
        raise ValueError('audit requires the exact canonical Buu profile')
    image = Path(path).read_bytes()
    RomDocument.from_bytes(image, profile)  # recheck bytes before profile access
    sprites = load_actor_sprites(image, identification)
    types = load_placement_types(path, catalog)
    if types.maps.base_bytes != image:
        raise ValueError('base changed during audit')
    documents = [sprites.reference_document(), types.reference_document()]
    owned = []
    refs = []
    for document in documents:
        for a in document.anchors:
            owned.append({'start': a.range.start.value, 'end': a.range.end,
                          'kind': a.kind, 'owner': a.owner, 'status': 'CONFIRMED'})
        for r in document.references:
            refs.append({'source': r.source.value, 'target': document.target_offset(r).value,
                         'classification': r.classification.value})
    for table_name in ('map_entries', 'enemy_stats', 'character_base_stats'):
        table = getattr(profile, table_name)
        start = table.address.to_file_offset(len(image))
        owned.append({'start': start, 'end': start + table.count * table.record_size,
                      'kind': 'declared_table', 'owner': table_name, 'status': 'DECLARED'})
    text = profile.text_strings
    for name, address, size in [('text_pool', text.pool_address, text.pool_size),
                                ('text_table', text.pointer_table_address, text.count * 4)]:
        start = address.to_file_offset(len(image))
        owned.append({'start': start, 'end': start + size,
                      'kind': 'declared_table', 'owner': name, 'status': 'DECLARED'})
    table_start = text.pointer_table_address.to_file_offset(len(image))
    for source in range(table_start, table_start + text.count * 4, 4):
        target = GbaRomAddress(struct.unpack_from('<I', image, source)[0]).to_file_offset(len(image))
        refs.append({'source': source, 'target': target, 'classification': 'CONFIRMED_REFERENCE'})
    for item in types.maps.slot_arrays():
        a = item.array
        owned.append({'start': a.file_offset, 'end': a.file_offset + len(a.original_bytes),
                      'kind': 'typed_map_slots' if item.is_typed else 'opaque_map_slots',
                      'owner': str(item.identity), 'status': 'CONFIRMED'})
    for r in types.maps.source_references():
        array = next(a.array for a in types.maps.slot_arrays() if a.identity.index == r.entry_index)
        refs.append({'source': array.file_offset + r.slot_index * 8 + 4,
                     'target': r.target_file_offset, 'classification': 'CONFIRMED_REFERENCE'})
    # Header/startup is explicitly assembled; arbitrary CODE-labelled INCBIN
    # areas are deliberately not misclassified as decoded executable coverage.
    owned.append({'start': 0, 'end': 0x158, 'kind': 'header_startup_code',
                  'owner': 'buusfury/asm/crt0.s', 'status': 'DECLARED'})
    span = RomRange(FileOffset(0x7B89A8), 0x800000 - 0x7B89A8)
    candidate = candidate_report(image, span, owned, refs)
    annotated = owned + [{'start': span.start.value, 'end': span.end,
                         'kind': 'candidate_tail', 'owner': 'upstream_tail', 'status': 'CANDIDATE'}]
    result = {'profile_id': profile.id, 'base_sha256': profile.sha256,
              'candidate': candidate, 'occupancy': occupancy(len(image), annotated),
              'reference_model_count': len(refs),
              'verified_capacity': sum(f.range.size for f in profile.free_regions),
              'decision': 'NOT_PROMOTED',
              'limits': 'Partial typed ownership only; broad INCBINs remain semantically UNKNOWN.'}
    if identify_rom(path, catalog).hashes != identification.hashes:
        raise ValueError('canonical image changed during audit')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.rom), indent=2, sort_keys=True))
