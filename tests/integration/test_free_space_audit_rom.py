"""Explicitly configured, read-only canonical candidate regression."""
import hashlib
import os
from pathlib import Path

import pytest

from tools.research.free_space_audit import candidate_report
from tools.webfoot.binary import FileOffset
from tools.webfoot.document import RomDocument
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfileCatalog


def test_canonical_tail_stays_candidate_and_input_unchanged():
    configured = os.environ.get('TOOLKIT011_ROM')
    if not configured:
        pytest.skip('set TOOLKIT011_ROM for intentional canonical read-only audit')
    path = Path(configured)
    before = path.stat()
    image = path.read_bytes()
    profile = next(p for p in RomProfileCatalog.load('tools/webfoot/data/roms.yaml').profiles
                   if p.id == 'buus_fury_usa_rev0_01c1707f')
    RomDocument.from_bytes(image, profile)
    report = candidate_report(image, RomRange(FileOffset(0x7B89A8), 0x47658), [], [])
    assert report['status'] == 'CANDIDATE'
    assert report['byte_histogram'] == {255: 292440}
    assert report['reference_counts'] == {'CANDIDATE_REFERENCE': 516}
    assert report['candidate_word_aligned_count'] == 99
    assert profile.free_regions == ()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == profile.sha256
    assert (path.stat().st_size, path.stat().st_mtime_ns) == (before.st_size, before.st_mtime_ns)
