"""Read-only ROM-gated evidence for LOGX-CODEC-001.

Only findings independently established in
``docs/research/LOGX_CODEC_PROVENANCE.md`` are asserted here: the wrapper's
dispatch contract as the engine's own instructions state it, the census
arithmetic, the two canonical zero-header containers, the fixture digests, and
the whole-corpus differential between the project decoder and the independent
reimplementation.

The suite skips cleanly when the private canonical ROM is not configured and it
never writes to it. No decoded payload is committed: fixtures are asserted by
length and SHA-256 only.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import logx_codec_probe as probe
from tools.research import webfoot_codec_reference as reference
from tools.research.thumb_disasm import resolve_thumb_bl
from tools.webfoot.formats import webfoot_lz as wl

ROM_BASE = 0x08000000

#: The Thumb->ARM stub run's exact extent and targets, read from each stub's own
#: literal. Values measured, never inferred from a label.
EXPECTED_VENEER_STUBS = 15
EXPECTED_VENEER_TARGETS = {
    0x08049120: 0x03000040,
    0x0804912C: 0x030007A8,
    0x08049138: 0x03000768,
    0x08049144: 0x030007FC,
    0x08049150: 0x03000388,
    0x0804915C: 0x030004C0,
    0x08049168: 0x03000858,
    0x08049174: 0x03000560,
    0x08049180: 0x03000700,
    0x0804918C: 0x030002DC,
    0x080491A8: 0x03000CA0,
    0x080491B4: 0x03000A4C,
    0x080491C0: 0x03000000,
}

# --- locally verified constants of the canonical image -----------------------

EXPECTED_DISTINCT_ROOTS = 421

#: Dominant-layer chunk containers: unique, and the reference count over them.
EXPECTED_CHUNK_UNIQUE = 3745
EXPECTED_CHUNK_REFERENCES = 3912
EXPECTED_CHUNK_DECLARED_SIZE = 0x800

EXPECTED_STREAM_UNIQUE = 392
EXPECTED_STREAM_REFERENCES = 421

EXPECTED_BANK_UNIQUE = 187
EXPECTED_BANK_REFERENCES = 187

EXPECTED_CENSUS_REFERENCES = 4520
EXPECTED_CENSUS_UNIQUE = 4324
EXPECTED_CENSUS_DIGESTS = 4324
EXPECTED_PACKED = 4322
EXPECTED_STORED = 2
EXPECTED_ZERO_HEADER = 2

EXPECTED_DECLARED_SIZE_MIN = 4
EXPECTED_DECLARED_SIZE_MAX = 16384

#: The dominant-layer constructor's own default container.
ENGINE_DEFAULT_CONTAINER = 0x08070808

#: The two canonical zero-header containers, with their decoded digest.
ZERO_HEADER_FIXTURES = {
    0x082B5F1C: "9c14ff2232b3d3427a3197aa999afadc58d36c2c3f855c9efcd5f1675291997a",
    0x082B5F94: "b98a002565f52a2b53593a390fdcfd620a4e5783d545779e5fbbac207e995101",
}

#: Curated fixtures: address -> (declared size, decoded SHA-256).
FIXTURES = {
    0x08179A50: (2048, "f7ac0e36dd93d70c22ea62884adfdffbb7af1d597ca78b399fb35b1d7e507c27"),
    0x0820BE10: (2048, "b6df3104b1ef19f5538c0fc760451fedfed1d016f0efd0302b26d6d2364715f3"),
    0x082B8BAC: (2048, "0757872b4b26d36cd91ae3a60d55c8cdd5f4da5a60f0cda029fcab3a38250ac8"),
    0x0817A75C: (904, "4edc8d61b019dd8371c5cbc49f6315769aee163c6a40f9ab79687084b28057e2"),
    0x0817BA28: (478, "8d045c3637f6eb73a3a650b27eeb76e125d0e27e7fc680d932d192d24f113e16"),
    0x082B8BF4: (1682, "9b473f15cf67eea0fa3882780ee54527684fa208bc66b268af2f416713affbe0"),
    0x082B5F1C: (4, "9c14ff2232b3d3427a3197aa999afadc58d36c2c3f855c9efcd5f1675291997a"),
    0x080945C0: (16384, "ccfa6a39379a38a292504012568d6bd39bd7c50bf5c50cb4e2334fd5370953f0"),
    0x08177AB8: (15424, "e1c9b6dd8a61ace97e7009f8b7523666150575737933b9ec706108b25e608909"),
}


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest().upper() == probe.CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def groups(canonical_bytes: bytes) -> dict[str, dict[int, set[str]]]:
    return {
        "dominant_layer_chunk": probe.iter_dominant_chunk_targets(canonical_bytes),
        "selector_stream_root_48": probe.iter_selector_streams(canonical_bytes),
        "selector_bank_root_4c": probe.iter_bank_containers(canonical_bytes),
    }


# --- section A: the wrapper --------------------------------------------------


def test_dispatcher_is_a_two_argument_thunk_on_a_tagged_header() -> None:
    report = reference.dispatcher_report()
    assert report["dispatcher"] == 0x0803D940
    decoded = report["dispatcher_decoded"]
    # The first instruction discards the incoming third argument.
    assert decoded[0].startswith("0803d940 adds r2, r0, #0")
    assert any("cmp  r3, #0" in line for line in decoded)
    assert any("cmp  r3, #1" in line for line in decoded)
    assert any("cmp  r3, #2" in line for line in decoded)
    assert any("adds r1, #8" in line for line in decoded)
    assert any("ldr  r2, [r2, #4]" in line for line in decoded)


def test_veneer_run_resolves_to_iwram_targets(canonical_bytes: bytes) -> None:
    """The stub run: 15 stubs, both forms, targets read from each stub's literal."""
    rows = reference.veneer_table(canonical_bytes)
    assert len(rows) == EXPECTED_VENEER_STUBS
    by_form = {form: sum(1 for r in rows if r["form"] == form)
               for form in ("ldr_pc", "branch")}
    assert by_form == {"ldr_pc": 13, "branch": 2}

    ldr_pc = {row["veneer"]: row["iwram_target"] for row in rows
              if row["form"] == "ldr_pc"}
    assert ldr_pc == EXPECTED_VENEER_TARGETS
    assert reference.IWRAM_PACKED == 0x03000040
    assert reference.IWRAM_MEMCPY == 0x03000768
    # 0x03000190 was asserted by an earlier revision of this ticket and does not
    # occur anywhere in the image.
    assert 0x03000190 not in ldr_pc.values()

    # The 8-byte branch stubs carry an ARM branch target instead of a literal.
    branch = [row for row in rows if row["form"] == "branch"]
    assert [row["veneer"] for row in branch] == [0x08049198, 0x080491A0]
    for row in branch:
        assert row["iwram_target"] is None
        assert row["size"] == 8
    for row in rows:
        if row["form"] == "ldr_pc":
            assert row["instruction_bytes"].startswith("7847c04604f01fe5")
            assert row["size"] == 12


def test_dispatcher_stored_branch_calls_a_rom_memcpy(canonical_bytes: bytes) -> None:
    """`0x0803D960` is `bl 0x08046D18`, a ROM ARM routine - not a stub call."""
    hi = int.from_bytes(canonical_bytes[0x0803D960 - ROM_BASE:0x0803D962 - ROM_BASE],
                        "little")
    lo = int.from_bytes(canonical_bytes[0x0803D962 - ROM_BASE:0x0803D964 - ROM_BASE],
                        "little")
    assert resolve_thumb_bl(0x0803D960, hi, lo) == 0x08046D18
    # And that routine is a Thumb->ARM interworking head, i.e. it runs in ARM.
    assert canonical_bytes[0x08046D18 - ROM_BASE:0x08046D1A - ROM_BASE] == b"\x78\x47"


def test_iwram_blob_base_is_confirmed_by_the_startup_dma3(canonical_bytes: bytes) -> None:
    """The blob mapping is CONFIRMED by the DMA3 literals, not inferred."""
    source = probe._u32(canonical_bytes, 0x08000148)
    destination = probe._u32(canonical_bytes, 0x0800014C)
    control = probe._u32(canonical_bytes, 0x08000150)
    assert source == reference.IWRAM_BLOB_ROM_BASE == 0x087B79A4
    assert destination == 0x03000000
    assert (control & 0xFFFF) >> 2 == 0x401  # 2050 bytes
    # ROM base + 0x40 is the stub's target, and it is a valid ARM prologue.
    assert reference.PACKED_DECODER_ROM == source + 0x40 == 0x087B79E4
    assert canonical_bytes[0x087B79E4 - ROM_BASE:0x087B79E8 - ROM_BASE] == bytes.fromhex(
        "f04f2de9"
    )


def test_the_default_container_is_kind_zero_declaring_zero(canonical_bytes: bytes) -> None:
    kind, declared = wl.read_header(
        canonical_bytes, ENGINE_DEFAULT_CONTAINER - ROM_BASE
    )
    assert (kind, declared) == (0, 0)
    got = wl.unpack(canonical_bytes, ENGINE_DEFAULT_CONTAINER - ROM_BASE)
    assert got.data == b""


# --- section B: census arithmetic --------------------------------------------


def test_census_arithmetic(
    canonical_bytes: bytes, groups: dict[str, dict[int, set[str]]]
) -> None:
    chunks = groups["dominant_layer_chunk"]
    streams = groups["selector_stream_root_48"]
    banks = groups["selector_bank_root_4c"]

    assert len(probe.iter_selector_roots(canonical_bytes)) == EXPECTED_DISTINCT_ROOTS

    assert len(chunks) == EXPECTED_CHUNK_UNIQUE
    assert sum(len(v) for v in chunks.values()) == EXPECTED_CHUNK_REFERENCES
    assert len(streams) == EXPECTED_STREAM_UNIQUE
    assert sum(len(v) for v in streams.values()) == EXPECTED_STREAM_REFERENCES
    assert len(banks) == EXPECTED_BANK_UNIQUE
    assert sum(len(v) for v in banks.values()) == EXPECTED_BANK_REFERENCES

    rows = probe.census(canonical_bytes, groups)
    summary = probe.census_summary(rows)
    assert summary["references"] == EXPECTED_CENSUS_REFERENCES
    assert summary["unique_containers"] == EXPECTED_CENSUS_UNIQUE
    assert summary["unique_payload_digests"] == EXPECTED_CENSUS_DIGESTS
    assert summary["declared_size_min"] == EXPECTED_DECLARED_SIZE_MIN
    assert summary["declared_size_max"] == EXPECTED_DECLARED_SIZE_MAX
    assert summary["anomalies"] == []

    classes = summary["wrapper_classes"]
    packed = sum(v for k, v in classes.items() if "packed" in k)
    stored = sum(v for k, v in classes.items() if "stored" in k)
    assert packed == EXPECTED_PACKED
    assert stored == EXPECTED_STORED

    # 4,324 = 3,745 + 392 + 187
    assert (
        EXPECTED_CHUNK_UNIQUE + EXPECTED_STREAM_UNIQUE + EXPECTED_BANK_UNIQUE
        == EXPECTED_PACKED + EXPECTED_STORED
    )
    # 4,520 = 3,912 + 421 + 187
    assert (
        EXPECTED_CHUNK_REFERENCES
        + EXPECTED_STREAM_REFERENCES
        + EXPECTED_BANK_REFERENCES
        == EXPECTED_CENSUS_REFERENCES
    )


def test_dominant_chunks_all_declare_0x800(
    canonical_bytes: bytes, groups: dict[str, dict[int, set[str]]]
) -> None:
    members = groups["dominant_layer_chunk"]
    assert len(members) == EXPECTED_CHUNK_UNIQUE, "population must not be empty"
    checked = 0
    for address in sorted(members):
        kind, declared = wl.read_header(canonical_bytes, address - ROM_BASE)
        assert kind == 1, hex(address)
        assert declared == EXPECTED_CHUNK_DECLARED_SIZE, hex(address)
        checked += 1
    assert checked == EXPECTED_CHUNK_UNIQUE


# --- section C: zero-header ---------------------------------------------------


def test_zero_header_containers(canonical_bytes: bytes) -> None:
    found = {}
    for members in (
        probe.iter_dominant_chunk_targets(canonical_bytes),
        probe.iter_selector_streams(canonical_bytes),
        probe.iter_bank_containers(canonical_bytes),
    ):
        for address in members:
            if wl.read_header(canonical_bytes, address - ROM_BASE)[0] == 0:
                found[address] = None
    assert len(found) == EXPECTED_ZERO_HEADER
    for address, digest in ZERO_HEADER_FIXTURES.items():
        assert address in found, hex(address)
        kind, declared = wl.read_header(canonical_bytes, address - ROM_BASE)
        assert (kind, declared) == (0, 4)
        got = wl.unpack(canonical_bytes, address - ROM_BASE)
        assert len(got.data) == declared
        assert hashlib.sha256(got.data).hexdigest() == digest


# --- section D: fixtures ------------------------------------------------------


@pytest.mark.parametrize("address", sorted(FIXTURES))
def test_fixture_digests(canonical_bytes: bytes, address: int) -> None:
    declared, digest = FIXTURES[address]
    off = address - ROM_BASE
    kind, header_declared = wl.read_header(canonical_bytes, off)
    assert header_declared == declared
    project = wl.unpack(canonical_bytes, off)
    assert len(project.data) == declared
    assert hashlib.sha256(project.data).hexdigest() == digest
    if kind in wl.PACKED_KINDS:
        reference_decode = reference.decode_packed(
            canonical_bytes, off + wl.HEADER_SIZE, declared_size=declared
        )
        assert reference_decode.data == project.data
        assert reference_decode.actual_size == declared


# --- section E: whole-corpus differential ------------------------------------


def test_every_packed_container_decodes_identically(
    canonical_bytes: bytes, groups: dict[str, dict[int, set[str]]]
) -> None:
    """The headline invariant: two implementations, one answer, zero exceptions."""
    compared = 0
    for members in groups.values():
        for address in sorted(members):
            off = address - ROM_BASE
            kind, declared = wl.read_header(canonical_bytes, off)
            project = wl.unpack(canonical_bytes, off)
            if kind not in wl.PACKED_KINDS:
                assert kind == 0
                continue
            got = reference.decode_packed(
                canonical_bytes, off + wl.HEADER_SIZE, declared_size=declared
            )
            assert got.data == project.data, hex(address)
            assert got.actual_size == declared, hex(address)
            compared += 1
    assert compared == EXPECTED_PACKED


def test_every_packed_stream_terminates_at_its_declared_size(
    canonical_bytes: bytes, groups: dict[str, dict[int, set[str]]]
) -> None:
    """The stream's own end marker and the declared size agree everywhere."""
    compared = 0
    for members in groups.values():
        for address in sorted(members):
            off = address - ROM_BASE
            kind, declared = wl.read_header(canonical_bytes, off)
            if kind not in wl.PACKED_KINDS:
                continue
            got = reference.decode_packed(
                canonical_bytes,
                off + wl.HEADER_SIZE,
                declared_size=declared,
                stop_on="end_marker",
            )
            assert got.terminator == "end_marker", hex(address)
            assert got.actual_size == declared, hex(address)
            compared += 1
    assert compared == EXPECTED_PACKED


def test_source_consumption_is_whole_words(
    canonical_bytes: bytes, groups: dict[str, dict[int, set[str]]]
) -> None:
    compared = 0
    for members in groups.values():
        for address in sorted(members):
            off = address - ROM_BASE
            kind, declared = wl.read_header(canonical_bytes, off)
            if kind not in wl.PACKED_KINDS:
                continue
            got = reference.decode_packed(
                canonical_bytes, off + wl.HEADER_SIZE, declared_size=declared
            )
            assert got.source_consumed % 4 == 0, hex(address)
            assert got.source_consumed > 0, hex(address)
            compared += 1
    assert compared == EXPECTED_PACKED, "population must not be empty"


def test_every_packed_stream_opens_with_the_same_control_token(
    canonical_bytes: bytes,
) -> None:
    """Read from the raw bits: the opening token assigns the literal width.

    This is what makes the initial-width register immaterial for decoding, and it
    is measured without any decoder involved.
    """
    report = probe.opening_token_report(canonical_bytes)
    assert report["packed_containers"] == EXPECTED_PACKED
    assert report["prefix_bits_histogram"] == {"001": EXPECTED_PACKED}
    assert report["shapes"] == {"four_bit_escape": EXPECTED_PACKED}
    # The escape's two-bit field is not constant: most containers select an
    # 8-bit literal width and read no base byte at all.
    fields = report["escape_two_bit_field"]
    assert set(fields) == {"0", "1"}
    assert sum(fields.values()) == EXPECTED_PACKED
    # The base byte is only read when that field is zero, and it is not constant
    # among the containers that do read one.
    assert report["containers_reading_a_base_byte"] == fields["0"]
    assert report["distinct_escape_base_bytes"] > 1


# --- section F: the probe is deterministic -----------------------------------


def test_probe_report_is_deterministic(canonical_bytes: bytes) -> None:
    first = probe.census(
        canonical_bytes,
        {
            "dominant_layer_chunk": probe.iter_dominant_chunk_targets(canonical_bytes),
            "selector_stream_root_48": probe.iter_selector_streams(canonical_bytes),
            "selector_bank_root_4c": probe.iter_bank_containers(canonical_bytes),
        },
    )
    second = probe.census(
        canonical_bytes,
        {
            "dominant_layer_chunk": probe.iter_dominant_chunk_targets(canonical_bytes),
            "selector_stream_root_48": probe.iter_selector_streams(canonical_bytes),
            "selector_bank_root_4c": probe.iter_bank_containers(canonical_bytes),
        },
    )
    assert first == second


def test_canonical_rom_gate_accepts_the_canonical_image(canonical_bytes: bytes) -> None:
    """The gate itself: the canonical bytes satisfy it."""
    assert hashlib.sha256(canonical_bytes).hexdigest().upper() == probe.CANONICAL_SHA256
