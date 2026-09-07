"""Synthetic research-only occupancy and candidate discipline."""
import struct

import pytest

from tools.research.free_space_audit import candidate_report, occupancy
from tools.webfoot.binary import FileOffset
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import ProfileConfigError, _free_regions


def test_fill_with_aligned_and_unaligned_candidates_is_never_promoted():
    image = bytearray(512)
    image[256:] = b'\xff' * 256
    struct.pack_into('<I', image, 16, 0x08000100)
    struct.pack_into('<I', image, 25, 0x08000120)
    report = candidate_report(bytes(image), RomRange(FileOffset(256), 256), [], [])
    assert report['status'] == 'CANDIDATE'
    assert report['candidate_word_aligned_count'] == 1
    assert report['reference_counts'] == {'CANDIDATE_REFERENCE': 2}
    assert report['byte_histogram'] == {255: 256}
    assert report['reasons_candidate_only']


def test_zero_hits_does_not_promote_fill():
    report = candidate_report(bytes(512), RomRange(FileOffset(256), 256), [], [])
    assert report['status'] == 'CANDIDATE'
    assert report['reference_counts'] == {}


def test_known_reference_class_and_neighbors_preserved():
    image = bytearray(512)
    struct.pack_into('<I', image, 16, 0x08000100)
    owned = [{'start': 16, 'end': 20, 'owner': 'table'},
             {'start': 400, 'end': 420, 'owner': 'other'}]
    ref = {'source': 16, 'target': 256, 'classification': 'DECLARED_REFERENCE'}
    report = candidate_report(bytes(image), RomRange(FileOffset(256), 64), owned, [ref])
    assert report['known_inbound'] == [ref]
    assert report['reference_counts'] == {'DECLARED_REFERENCE': 1}
    assert report['neighbor_before'] == owned[0]
    assert report['neighbor_after'] == owned[1]


def test_occupancy_retains_unknown_and_overlapping_annotations():
    rows = [{'start': 10, 'end': 30, 'kind': 'table', 'owner': 'A'},
            {'start': 20, 'end': 40, 'kind': 'graphic', 'owner': 'B'}]
    report = occupancy(64, rows)
    assert report == occupancy(64, list(reversed(rows)))
    assert sum(s['end'] - s['start'] for s in report['segments']) == 64
    assert report['segments'][0]['coverage'] == 'UNKNOWN'
    assert report['segments'][2]['annotations'] == [0, 1]
    assert report['segments'][-1]['coverage'] == 'UNKNOWN'


@pytest.mark.parametrize('status', ['CANDIDATE', 'CANDIDATE_REFERENCE', 'UNKNOWN'])
def test_candidate_cannot_be_parsed_as_production_free_space(status):
    with pytest.raises(ProfileConfigError, match='CONFIRMED'):
        _free_regions([{'file_offset': 256, 'size': 256, 'status': status,
                        'evidence': 'numeric scan and fill only'}], 512)


def test_out_of_bounds_candidate_refused():
    with pytest.raises(ValueError):
        candidate_report(bytes(512), RomRange(FileOffset(500), 20), [], [])
