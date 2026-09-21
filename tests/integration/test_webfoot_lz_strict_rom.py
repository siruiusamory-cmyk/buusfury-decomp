"""ROM-gated parity proof for the strict Webfoot decoder.

EVIDENCE-RISK-DEBT-001. Removing the final-match clip from
``tools.webfoot.formats.webfoot_lz`` is only safe if no accepted stream depended
on it, and "the accepted streams" is the whole canonical sprite corpus, not a
sample. This module decodes **every container offset a sprite piece reaches** with
both the repaired project decoder and the independent research reference, which
never clipped and stops only at the declared size, and requires them to agree
byte-for-byte with the same consumed extent.

The reference is the discriminating control: if a canonical container needed the
clip, the project decoder would return its declared size while the reference
produced more and refused. Agreement on all of them is what makes the strictness
change provably behaviour-preserving on accepted input.

The suite skips cleanly when the private canonical image is not configured and
never writes to it. No ROM-derived fixture is committed: every expectation is a
count, an offset or a digest of what the two decoders agreed on.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import logx_frame_probe as fp
from tools.research import webfoot_codec_reference as reference
from tools.webfoot.formats import webfoot_lz as wl

#: The accepted corpus: distinct container offsets reachable by a sprite piece.
EXPECTED_CONTAINERS = 7_390
#: Every canonical container is the packed form, and every piece's declared
#: dimensions agree with the decoded length.
EXPECTED_PIECE_REFERENCES = 11_005


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest().upper() == fp.CANONICAL_SHA256
    return data


def _container_offsets(data: bytes) -> list[int]:
    return sorted(
        {
            resolved
            for address in fp.frame_addresses(data)
            for piece in fp.read_frame(data, address).pieces
            if (resolved := fp.resolves_to_graphics(data, piece)) is not None
        }
    )


def test_the_repaired_decoder_agrees_with_the_non_clipping_reference(
    canonical_bytes: bytes,
) -> None:
    offsets = _container_offsets(canonical_bytes)
    assert len(offsets) == EXPECTED_CONTAINERS
    kinds: set[int] = set()
    decoded_bytes = 0
    for offset in offsets:
        container = wl.unpack(canonical_bytes, offset)
        kinds.add(container.kind)
        # The reference never clips: a stream whose match overran would raise here
        # while the project decoder returned a full declared size.
        other = reference.decode_packed(
            canonical_bytes,
            offset + wl.HEADER_SIZE,
            declared_size=container.declared_size,
            initial_literal_bits=container.kind,
        )
        assert other.data == container.data, f"divergence at {offset:#x}"
        assert other.actual_size == container.declared_size
        assert other.terminator == "declared_size"
        assert other.source_consumed == container.packed_end - (
            offset + wl.HEADER_SIZE
        ), f"consumed extent diverged at {offset:#x}"
        decoded_bytes += container.declared_size
    assert kinds == {1}, "a canonical sprite container is not the packed form"
    # A container that decoded to nothing would make the parity loop vacuous.
    assert decoded_bytes > 0 and all(
        wl.unpack(canonical_bytes, offset).declared_size > 0 for offset in offsets[:64]
    )


def test_no_canonical_container_needed_the_removed_clip(canonical_bytes: bytes) -> None:
    """Stated separately, because it is the claim the strictness change rests on.

    Each container is re-decoded from its own bytes by the reference with the
    clip explicitly available to it: ``stop_on="end_marker"`` runs past the
    declared size to the stream's own terminator, so a stream that produces more
    than its header declares is visible even though the repaired decoder stops at
    the size. The count must be zero, which is the direct measurement that made
    the refusal safe.

    This covers **both** token classes. The reference's match path never clipped,
    and its raw-literal-run path was corrected to stop clipping in the same ticket
    after an independent review found it; so a container that needed either clip
    now shows up here as ``actual_size > declared``. Measured on the canonical
    image there are none, and no container's run reaches the declared size
    mid-run either.
    """
    overrunning = []
    for offset in _container_offsets(canonical_bytes):
        declared = wl.read_header(canonical_bytes, offset)[1]
        if declared == 0:
            continue
        # ``stop_on="end_marker"`` runs past the declared size to the stream's own
        # terminator, so any container whose stream produces more than the header
        # declares is visible even though the repaired decoder stops at the size.
        longer = reference.decode_packed(
            canonical_bytes,
            offset + wl.HEADER_SIZE,
            declared_size=declared,
            initial_literal_bits=wl.read_header(canonical_bytes, offset)[0],
            stop_on="end_marker",
        )
        if longer.actual_size > declared:
            overrunning.append((offset, declared, longer.actual_size))
    assert overrunning == []


def test_piece_dimensions_still_match_every_decoded_length(
    canonical_bytes: bytes,
) -> None:
    """The cross-check the strictness change must not disturb."""
    census = fp.piece_census(canonical_bytes)
    assert census["piece_references"] == EXPECTED_PIECE_REFERENCES
    assert census["unique_graphics_targets"] == EXPECTED_CONTAINERS
    assert census["container_dimension_matches"] == EXPECTED_PIECE_REFERENCES
    assert census["attribute_dimension_matches"] == EXPECTED_PIECE_REFERENCES
    assert census["attribute_dimension_mismatches"] == 0
    assert census["container_declared_sizes"], "no container size was recorded"


def test_no_canonical_container_uses_the_raw_literal_run_token(
    canonical_bytes: bytes, monkeypatch
) -> None:
    """The run-path proof, stated as the fact that is actually measurable.

    An independent review pointed out that the first version of this test was
    **vacuously true**: it reinstated the old clipping rule through
    ``webfoot_lz._emit_raw`` and asserted the rule never fired, but no canonical
    container enters the run branch at all, so the patch was never consulted and
    the assertion could not have failed for any reason connected to the corpus.
    The honest and *stronger* statement is the one measured here: the run token is
    unused by all 7,390 canonical containers, which is why the run-path strictness
    is provably corpus-inert. Instrumenting the real helper - delegating, not
    replacing it - makes that a live assertion: it fails the day a canonical
    container starts using a run.

    ``tests/unit/test_webfoot_lz.py`` carries the discriminating half: on a
    synthetic overrun the reinstated clip *does* fire and *does* change the
    decoded bytes, so the rule under test is known to bite. The match path's
    equivalent corpus measurement is
    :func:`test_no_canonical_container_needed_the_removed_clip`, which uses the
    reference's end-marker mode and is not vacuous.
    """
    offsets = _container_offsets(canonical_bytes)
    calls: list[tuple[int, int]] = []
    real_emit_raw = wl._emit_raw

    def recording_emit_raw(out: bytearray, value: int, expected: int) -> None:
        calls.append((len(out), expected))
        real_emit_raw(out, value, expected)

    monkeypatch.setattr(wl, "_emit_raw", recording_emit_raw)
    try:
        decoded = {
            offset: wl.unpack(canonical_bytes, offset).data for offset in offsets
        }
    finally:
        monkeypatch.undo()

    assert len(decoded) == EXPECTED_CONTAINERS
    assert calls == [], (
        f"a canonical container reached the raw-literal-run branch "
        f"({len(calls)} literal append(s)); the corpus-inert claim no longer holds"
    )
