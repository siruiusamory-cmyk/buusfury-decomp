"""Portable synthetic tests for the LOGX-GFXSCAN-001 scanner models.

Every fixture here is hand-built from a bit string, so the tests pin the two
things a scanner model can get wrong without any ROM present:

* **the external reader's framing**, which is stated by
  :func:`tools.research.logx_gfxscan_probe._bits_of` and asserted against
  :class:`tools.research.logx_gfxscan_probe._BitStream` bit for bit, so a
  refactor of the fast reader cannot silently change bit order;
* **the external reader's two acceptance rules** - the ``kind == 1`` form test and
  the ``1 <= declared < 0x20000``, ``declared % 4 == 0`` size filter - which are
  reproduced as an explicit population rather than described in prose.

**What the synthetic fixtures cannot prove, and why the ROM-gated suite exists.**
A grammar can decode a hand-built stream and still fail on real data; that is
exactly what happened during this ticket, where a two-bit-per-round
transcription of the external ``GetInteger`` decoded synthetic opening tokens and
failed on every canonical container.  The authority for the grammar is
``tests/integration/test_logx_gfxscan_rom.py``, which requires the external model
to reproduce the project decoder's bytes on representative canonical containers.

No ROM bytes appear here and no decoded payload is stored.
"""

from __future__ import annotations

import struct

import pytest

from tools.research import logx_gfxscan_probe as scan


def words(*values: int) -> bytes:
    """Little-endian 32-bit words."""
    return b"".join(struct.pack("<I", value) for value in values)


def bits_to_bytes(bit_string: str) -> bytes:
    """MSB-first bit string -> little-endian 32-bit words, zero padded.

    The string's first bit must land in **bit 31 of the first word the decoder
    loads**, and the decoder loads words little-endian.  So the first 32 bits of
    the string are packed into a little-endian ``u32``: ``bits_to_bytes("1000...")``
    begins with ``0x80``, the low byte of ``0x00000001``.
    """
    padded = bit_string.ljust((len(bit_string) + 31) // 32 * 32, "0")
    return b"".join(
        struct.pack("<I", int(padded[i : i + 32], 2))
        for i in range(0, len(padded), 32)
    )


# --- bit framing --------------------------------------------------------------


def test_bits_of_is_msb_first_within_little_endian_words() -> None:
    """The bit order the scanner relies on, stated as a literal expectation.

    ``rom.ReadInt()`` is little-endian, and the external reader consumes it from
    bit 31 down.  For the bytes ``c0 48 c0 20`` the word is ``0x20C048C0``, so the
    first eight bits are ``00100000`` - not the byte's own ``11000000``.
    """
    data = bytes([0xC0, 0x48, 0xC0, 0x20])
    assert scan._bits_of(data, 0, len(data))[:8] == (0, 0, 1, 0, 0, 0, 0, 0)
    assert scan._bits_of(data, 0, len(data))[8:16] == (1, 1, 0, 0, 0, 0, 0, 0)


def test_bit_stream_agrees_with_the_readable_sequence() -> None:
    """The fast word reader and the explicit bit list must not drift apart."""
    data = bytes(range(64))
    sequence = scan._bits_of(data, 0, len(data))
    reader = scan._BitStream(data, 0)
    assert tuple(reader.bit() for _ in range(len(sequence))) == sequence


def test_bit_stream_get_matches_repeated_bit_reads() -> None:
    data = bytes(range(64))
    source = scan._BitStream(data, 0)
    reference = scan._BitStream(data, 0)
    assert source.get(13) == int("".join(str(reference.bit()) for _ in range(13)), 2)
    assert source.get(0) == 0
    # a read that crosses the word boundary keeps the buffered remainder
    assert source.get(19) == int("".join(str(reference.bit()) for _ in range(19)), 2)


def test_bit_stream_reads_past_the_image_raise() -> None:
    reader = scan._BitStream(b"\x01\x02\x03\x04", 0)
    for _ in range(32):
        reader.bit()
    with pytest.raises(scan.GfxScanError):
        reader.bit()


def test_get_rejects_an_impossible_width() -> None:
    reader = scan._BitStream(bytes(8), 0)
    with pytest.raises(scan.GfxScanError):
        reader.get(33)


# --- the external acceptance rule --------------------------------------------


def test_external_size_filter_bounds() -> None:
    """``length > 0 && length < 0x20000 && length % 4 == 0``."""
    assert scan.EXTERNAL_SIZE_MIN == 1
    assert scan.EXTERNAL_SIZE_MAX_EXCLUSIVE == 0x20000
    assert scan.EXTERNAL_SIZE_MULTIPLE == 4


def test_external_population_requires_kind_one_and_the_size_filter() -> None:
    """Build a tiny image whose wrappers exercise every filter arm.

    The wrappers are spaced by ``WRAPPER_GAP`` bytes and every unused byte is
    ``0xFF``, so no second wrapper word can appear by accident inside the padding -
    a test that let one appear would measure the padding rather than the filter.
    """
    gap = 12
    entries = [
        (1, 4),        # submitted
        (1, 2),        # rejected: not a multiple of four
        (2, 4),        # rejected: the external model requires exactly kind 1
        (1, 0x20000),  # rejected: over the exclusive bound
        (1, 0),        # rejected: the minimum is one
    ]
    data = bytearray(b"\xff" * (gap * len(entries)))
    for index, (kind, declared) in enumerate(entries):
        data[index * gap : index * gap + 8] = words(kind, declared)
    population = scan.scan_population(bytes(data), start=0, end=len(data))
    submitted = {(item.offset, item.kind, item.declared) for item in population.submitted}
    assert submitted == {(0, 1, 4)}
    # four of the five wrappers are still a whole word inside the 60-byte image;
    # the fifth starts at 48 and its declared-size word would run past the end, so
    # the loop never reaches it
    assert population.kind_word_matches == 4
    assert population.size_filter_passes == 1
    assert population.size_filter_rejects == 3


def test_external_population_scans_every_byte_not_every_word() -> None:
    """An unaligned wrapper word is still a wrapper word to the external loop."""
    data = bytearray(b"\xff" * 32)
    data[3:7] = struct.pack("<I", 1)      # kind word at an odd offset
    data[7:11] = struct.pack("<I", 4)
    population = scan.scan_population(bytes(data), start=0, end=len(data))
    assert [item.offset for item in population.submitted] == [3]
    assert population.kind_word_matches == 1
    assert population.kind_word_matches_aligned == 0


def test_engine_population_accepts_forms_zero_one_two_and_alignment() -> None:
    gap = 12
    entries = [
        (0, 0, 4),   # form 0, aligned -> submitted by both
        (12, 1, 4),  # form 1, aligned -> submitted by both
        (24, 2, 4),  # form 2, aligned -> submitted by both
        (36, 3, 4),  # unrepresentable kind -> rejected by both
        (50, 1, 4),  # unaligned -> rejected by the aligned model only
    ]
    data = bytearray(b"\xff" * 64)
    for offset, kind, declared in entries:
        data[offset : offset + 8] = words(kind, declared)
    kwargs = dict(
        start=0,
        end=len(data),
        require_kind=False,
        allowed_kinds=(0, 1, 2),
        size_multiple=None,
        size_max_exclusive=scan.HOST_CANONICAL_MAX_OUTPUT + 1,
    )
    aligned = scan.scan_population(bytes(data), aligned_only=True, **kwargs)
    assert [item.offset for item in aligned.submitted] == [0, 12, 24]
    assert aligned.kind_word_matches == 3
    unaligned = scan.scan_population(bytes(data), aligned_only=False, **kwargs)
    assert 50 in [item.offset for item in unaligned.submitted]
    assert len(unaligned.submitted) == 4
    assert gap  # the spacing is what keeps the 0xFF padding from forming wrappers


# --- the external decoder -----------------------------------------------------


def test_external_stored_arm_copies_the_declared_bytes() -> None:
    data = words(0, 3) + b"abc" + bytes(8)
    payload, overrun, consumed, terminator = scan.external_decode(data, 0)
    assert payload == b"abc"
    assert (overrun, consumed, terminator) == (0, 11, "stored_memcpy")


def test_external_stored_arm_runs_past_the_image_and_raises() -> None:
    """``Decompress``'s stored loop reads byte by byte and throws at the end."""
    data = words(0, 32) + b"abc"
    with pytest.raises(scan.GfxScanError):
        scan.external_decode(data, 0)


def test_external_rejects_a_form_outside_zero_one_two() -> None:
    data = words(3, 4) + bytes(8)
    with pytest.raises(scan.GfxScanError):
        scan.external_decode(data, 0)


def test_external_decodes_the_opening_escape_then_literals() -> None:
    """A stream the external grammar definitely decodes, built by hand.

    Shape: the opening ``0 0 1 0000`` escape with its two-bit field ``01``, which
    sets the literal width to 8 and reads no base byte, then two 8-bit literals.
    """
    bit_string = "001" + "0000" + "01" + "1" + f"{0x41:08b}" + "1" + f"{0x42:08b}"
    data = words(1, 2) + bits_to_bytes(bit_string) + bytes(8)
    payload, overrun, consumed, terminator = scan.external_decode(data, 0)
    assert payload == b"AB"
    assert overrun == 0
    assert terminator == "declared_size"
    assert consumed % 4 == 0


def test_external_stops_on_the_streams_own_end_marker() -> None:
    """The marker is ``0 0 0`` with a zero seven-bit field and a zero sub-field.

    The external reader's third branch reads a seven-bit field and then a two-bit
    sub-field; ``index == 0`` with ``length == 2`` - both fields zero - is the
    marker.  The bit string is 23 bits, so the word padding after it is never
    read: the marker fires first and the reader stops.
    """
    bit_string = "001" + "0000" + "01" + "1" + f"{0x41:08b}" + "000" + "00"
    assert len(bit_string) == 23
    data = words(1, 8) + bits_to_bytes(bit_string) + bytes(8)
    payload, overrun, consumed, terminator = scan.external_decode(data, 0)
    assert payload == b"A"
    assert terminator == "end_marker"
    assert len(payload) < 8          # shorter than declared, as Array.Resize keeps
    assert overrun == 0


def test_external_back_reference_before_the_output_start_raises() -> None:
    """``TransferMatch`` indexing before ``w`` is the host's out-of-range throw."""
    bit_string = "001" + "0000" + "01" + "1" + f"{0x41:08b}" + "000" + "1111111" + "11"
    data = words(1, 8) + bits_to_bytes(bit_string) + bytes(8)
    with pytest.raises(scan.GfxScanError):
        scan.external_decode(data, 0)


def test_external_four_bit_arm_one_writes_a_literal_zero() -> None:
    """The ``value == 0`` arm writes ``0``, not the literal base.

    The external source is ``if (value == 0) { destination[w++] = 0; }``; the
    project decoder writes its literal base there instead.  This is the one arm
    where the two grammars genuinely differ, and it is what makes them disagree on
    78 of 11,712 known kind-1 containers rather than 77.

    Bit string: the escape ``0 0 1 | 0000 | 0 | 0`` selects 7-bit literals with a
    base byte of ``0x50``, which the *next* arm must not use.
    """
    bit_string = "0010000" + "0" + "0" + f"{0x50:08b}" + "001" + "0001"
    expected = "001" + "0000" + "0" + "0" + f"{0x50:08b}" + "001" + "0001"
    assert bit_string == expected
    data = words(1, 1) + bits_to_bytes(bit_string) + bytes(8)
    payload, _overrun, _consumed, _terminator = scan.external_decode(data, 0)
    assert payload == b"\x00"          # not 0x50, which is what the base would give


def test_external_literal_state_starts_at_the_csharp_default() -> None:
    """``literalBits`` is 0 until the first escape, so a leading literal reads none.

    The C# ``CompressionState`` leaves the field at the CLR default; it is the
    *escape* that sets 7 or 8.  A stream whose first token is a literal therefore
    consumes one bit and writes the literal offset, which is also 0.  No canonical
    container does this - the corpus cannot discriminate the initial value - but
    the synthetic case pins the transcription.

    Bit string: a literal, then zeros.  Because ``literalBits`` is 0 the literal
    consumes **no** payload bits, so the very next token is read from bit 1 and the
    stream ends on its declared size after one byte.
    """
    bit_string = "1" + "0" * 14
    assert len(bit_string) == 15
    data = words(1, 1) + bits_to_bytes(bit_string) + bytes(8)
    payload, _overrun, _consumed, terminator = scan.external_decode(data, 0)
    assert payload == b"\x00"
    assert terminator == "declared_size"


def test_integer_reads_one_value_bit_per_continuation_bit() -> None:
    """``GetInteger`` reads a payload bit then a continuation bit, and stops.

    Measured values, from the bit order the decoder actually consumes:

    * ``10``    -> ``(1 << 1) + 1 = 3``: one payload bit, continuation clear;
    * ``110``   -> two rounds, ``(1 << 1 | 1) = 3`` then ``(3 << 1 | 0) = 6``;
    * ``11110`` -> ``1, 3, 7, 14``: three rounds then a clear continuation.

    The two errors this pins are reading the pair in the other order and reading
    two bits before the first continuation test.  Both produce a model that
    decodes some hand-built streams and fails on every canonical container, which
    is why ``tests/integration/test_logx_gfxscan_rom.py`` also requires the
    external model to reproduce the project decoder's bytes on real containers.
    """
    assert scan._BitStream(bits_to_bytes("10" + "0" * 30), 0).integer() == 3
    assert scan._BitStream(bits_to_bytes("110" + "0" * 29), 0).integer() == 6
    assert scan._BitStream(bits_to_bytes("11110" + "0" * 27), 0).integer() == 14


# --- the candidate record -----------------------------------------------------


def _candidate(**overrides: object) -> scan.Candidate:
    base = dict(
        model=scan.MODEL_EXTERNAL,
        position=0,
        kind=1,
        declared=4,
        decoded_length=4,
        decoded_sha256="00",
        overrun=0,
        source_end=8,
        terminator="declared_size",
        aligned=True,
        priority=9,
    )
    base.update(overrides)
    return scan.Candidate(**base)  # type: ignore[arg-type]


def test_candidate_address_normalisation() -> None:
    assert scan.to_address(0x1234) == 0x08001234
    assert _candidate(position=0x1234).address == 0x08001234


def test_candidate_exact_and_full_length_are_separate_facts() -> None:
    """No overrun and reaching the declared size are different properties."""
    assert _candidate(overrun=0, decoded_length=4, declared=4).exact
    assert _candidate(overrun=0, decoded_length=4, declared=4).full_length

    clipped = _candidate(overrun=7, decoded_length=4, declared=4)
    assert not clipped.exact
    assert clipped.full_length

    short = _candidate(decoded_length=1, declared=4, terminator="end_marker")
    assert short.exact
    assert not short.full_length


def test_resolve_offset_accepts_both_stored_forms() -> None:
    assert scan.resolve_offset(0x08001234) == 0x1234
    assert scan.resolve_offset(0x1234) == 0x1234
    assert scan.resolve_offset(0xFFFFFFFF) is None
    assert scan.resolve_offset(scan.ROM_SIZE + 1) is None


# --- classification arithmetic ------------------------------------------------


def _corpus_with_one_known(address: int = 0x08001000) -> scan.KnownCorpus:
    resource = scan.KnownResource(
        address=address,
        resource_class=scan.CLASS_SPRITE_PIECES,
        references=("frame:08000000/piece:0",),
        kind=1,
        declared_size=64,
        decoded_length=64,
        decoded_sha256="aa",
        packed_end=address + 80,
        slot_semantics="test",
        graphics_identity="CONFIRMED graphics",
    )
    return scan.KnownCorpus(
        resources={address: resource},
        classes={scan.CLASS_SPRITE_PIECES: [address]},
        by_digest={"aa": [address]},
    )


def test_classification_counts_a_known_address_as_known_graphics() -> None:
    corpus = _corpus_with_one_known()
    candidate = _candidate(position=0x1000, decoded_sha256="bb")
    tally = scan.classify_candidates([candidate], corpus)
    assert candidate.category == scan.CATEGORY_KNOWN_GRAPHICS
    assert candidate.details["known_reference"] == "wrapper_address"
    assert tally[scan.CATEGORY_KNOWN_GRAPHICS] == 1


def test_classification_matches_a_new_address_by_payload_digest() -> None:
    corpus = _corpus_with_one_known()
    candidate = _candidate(position=0x2000, decoded_sha256="aa")
    scan.classify_candidates([candidate], corpus)
    assert candidate.category == scan.CATEGORY_KNOWN_GRAPHICS
    assert candidate.details["known_reference"] == "decoded_payload_digest"
    assert candidate.details["same_payload_as"] == ["08001000"]


def test_classification_rejects_an_unrepresentable_decode() -> None:
    corpus = _corpus_with_one_known()
    candidate = _candidate(position=0x2000, decoded_sha256="bb", overrun=5)
    scan.classify_candidates([candidate], corpus)
    assert candidate.category == scan.CATEGORY_FALSE_POSITIVE
    assert candidate.details["false_positive_class"] == scan.FP_CLIPPED_DECODE


def test_classification_rejects_an_early_end_marker() -> None:
    corpus = _corpus_with_one_known()
    candidate = _candidate(
        position=0x2000, decoded_sha256="bb", decoded_length=1, terminator="end_marker"
    )
    scan.classify_candidates([candidate], corpus)
    assert candidate.details["false_positive_class"] == scan.FP_SHORT_VIA_END_MARKER


def test_classification_rejects_a_start_inside_a_known_container() -> None:
    corpus = _corpus_with_one_known()
    candidate = _candidate(position=0x1010, decoded_sha256="bb")
    scan.classify_candidates([candidate], corpus)
    assert candidate.category == scan.CATEGORY_FALSE_POSITIVE
    assert candidate.details["false_positive_class"] == scan.FP_INSIDE_KNOWN_CONTAINER
    assert candidate.details["inside_container"] == "08001000"


def test_classification_rejects_an_unaligned_start() -> None:
    corpus = _corpus_with_one_known()
    candidate = _candidate(position=0x2001, decoded_sha256="bb", aligned=False)
    scan.classify_candidates([candidate], corpus)
    assert candidate.details["false_positive_class"] == scan.FP_NOT_WORD_ALIGNED


def test_classification_separates_referenced_from_unreferenced() -> None:
    corpus = _corpus_with_one_known()
    cited = _candidate(position=0x2000, decoded_sha256="bb")
    uncited = _candidate(position=0x3000, decoded_sha256="cc")
    tally = scan.classify_candidates(
        [cited, uncited], corpus, reference_index={cited.address: [0x08009999]}
    )
    assert cited.category == scan.CATEGORY_NEW_ENGINE_REFERENCED
    assert cited.details["engine_references"] == ["08009999"]
    assert uncited.category == scan.CATEGORY_UNRESOLVED_CONTAINER
    assert tally[scan.CATEGORY_NEW_ENGINE_REFERENCED] == 1
    assert tally[scan.CATEGORY_UNRESOLVED_CONTAINER] == 1


def test_classification_tally_arithmetic_is_exact() -> None:
    """Every candidate lands in exactly one category, and the tally sums."""
    corpus = _corpus_with_one_known()
    candidates = [
        _candidate(position=0x1000, decoded_sha256="bb"),                  # known
        _candidate(position=0x2000, decoded_sha256="aa"),                  # by digest
        _candidate(position=0x3000, decoded_sha256="bb", overrun=2),       # clipped
        _candidate(position=0x4001, decoded_sha256="cc", aligned=False),   # unaligned
        _candidate(position=0x5000, decoded_sha256="dd"),                  # unresolved
    ]
    tally = scan.classify_candidates(candidates, corpus)
    assert sum(tally.values()) == len(candidates)
    assert all(candidate.category for candidate in candidates)


# --- nested candidates --------------------------------------------------------


def test_nested_candidate_flagging_uses_measured_extents() -> None:
    outer = _candidate(position=0x1000, source_end=0x400, decoded_sha256="aa")
    inner = _candidate(position=0x1100, source_end=0x100, decoded_sha256="bb")
    flagged = scan.flag_nested_candidates([outer, inner])
    assert flagged == 1
    assert inner.details["nested_inside_candidate"] == "08001000"
    assert "nested_inside_candidate" not in outer.details


def test_nested_flagging_is_a_pre_pass_independent_of_classification() -> None:
    """The flagger records an address; the classifier decides the category.

    An earlier revision skipped candidates already classified ``A``/``B``, which
    made the flagger's behaviour depend on a category assigned *after* it ran.
    It is now a pre-pass: it records ``nested_inside_candidate`` for every
    candidate, and the classifier is what tells a known container apart from a
    nested candidate.
    """
    outer = _candidate(position=0x1000, source_end=0x400, decoded_sha256="aa")
    inner = _candidate(position=0x1100, source_end=0x100, decoded_sha256="bb")
    outer.category = scan.CATEGORY_KNOWN_GRAPHICS
    assert scan.flag_nested_candidates([outer, inner]) == 1
    assert inner.details["nested_inside_candidate"] == "08001000"


def test_classifier_separates_inside_known_from_inside_another_candidate() -> None:
    """Two different defects, two different false-positive classes.

    ``0x08001010`` is inside the known container's extent; ``0x08003000`` is
    inside another *candidate's* extent only.  Conflating them was a real defect of
    an earlier revision, where the class named "inside a known container" counted
    candidates whose owner was not a known container at all.
    """
    corpus = _corpus_with_one_known()
    inside_known = _candidate(position=0x1010, decoded_sha256="bb")
    nested = _candidate(position=0x3000, source_end=0x400, decoded_sha256="cc")
    nested.details["nested_inside_candidate"] = "08002F00"
    scan.classify_candidates([inside_known, nested], corpus)
    assert inside_known.details["false_positive_class"] == scan.FP_INSIDE_KNOWN_CONTAINER
    assert inside_known.details["inside_container"] == "08001000"
    assert nested.details["false_positive_class"] == scan.FP_INSIDE_ANOTHER_CANDIDATE


# --- deduplication ------------------------------------------------------------


def test_candidate_totals_do_not_inflate_discovery_with_duplicates() -> None:
    """Two addresses with one payload are two addresses and one digest."""
    candidates = [
        _candidate(position=0x1000, decoded_sha256="aa"),
        _candidate(position=0x2000, decoded_sha256="aa"),
    ]
    totals = scan._candidate_totals(candidates)
    assert totals["raw_candidates"] == 2
    assert totals["unique_addresses"] == 2
    assert totals["unique_decoded_digests"] == 1
    assert totals["shared_payload_instances"] == 1
    assert totals["duplicate_reference_count"] == 0


def test_match_basis_tally_sums_to_the_candidate_count() -> None:
    candidates = [
        _candidate(position=0x1000, decoded_sha256="aa"),
        _candidate(position=0x2000, decoded_sha256="bb"),
    ]
    candidates[0].details["known_reference"] = "wrapper_address"
    totals = scan._candidate_totals(candidates)
    assert sum(totals["match_basis"].values()) == 2
    assert totals["match_basis"]["wrapper_address"] == 1
    assert totals["match_basis"]["no_known_match"] == 1


# --- reference search ---------------------------------------------------------


def test_reference_search_finds_both_stored_forms() -> None:
    data = bytearray(64)
    target = 0x08000010
    data[0:4] = struct.pack("<I", target)
    data[4:8] = struct.pack("<I", target - scan.ROM_BASE)
    hits, coverage = scan.reference_search(bytes(data), {target})
    assert hits[target] == [0x08000000, 0x08000004]
    assert coverage["word_positions_scanned"] == 16
    assert "computed" in coverage["coverage"]


def test_reference_search_with_no_targets_does_not_claim_coverage() -> None:
    hits, coverage = scan.reference_search(b"\x00" * 64, set())
    assert hits == {}
    assert coverage["word_positions_scanned"] == 0


# --- the canonical gate -------------------------------------------------------


def test_canonical_gate_refuses_a_wrong_length() -> None:
    with pytest.raises(scan.GfxScanError):
        scan.verify_canonical(b"\x00" * 16)


def test_canonical_gate_refuses_a_wrong_digest() -> None:
    with pytest.raises(scan.GfxScanError, match="non-canonical"):
        scan.verify_canonical(bytes(scan.ROM_SIZE))


# --- optional-dependency behaviour -------------------------------------------


def test_module_imports_without_capstone() -> None:
    """The probe must not need an optional dependency to be importable.

    ``logx_gfxscan_probe`` imports the project's research modules and its
    container decoder, and nothing else; in particular it does not import
    ``tools.research.thumb_disasm``, which is the module that requires capstone.
    """
    import importlib
    import sys

    saved = sys.modules.pop("tools.research.logx_gfxscan_probe", None)
    saved_capstone = sys.modules.get("capstone")
    sys.modules["capstone"] = None  # type: ignore[assignment]
    try:
        module = importlib.import_module("tools.research.logx_gfxscan_probe")
        assert module.CANONICAL_SHA256
    finally:
        if saved_capstone is not None:
            sys.modules["capstone"] = saved_capstone
        else:
            sys.modules.pop("capstone", None)
        if saved is not None:
            sys.modules["tools.research.logx_gfxscan_probe"] = saved
