"""The ROM map's structural invariants.

The first ten tests are the ten invariants the ticket requires, each named so a
failure says which one broke. They run against the COMMITTED map, so they are
portable and need no ROM. The last group rebuilds the map from the real ROM and
asserts it is reproducible, which is ROM-gated.
"""

from __future__ import annotations

import json

import pytest

from buusfury import gba, rommap

ROM_SIZE = 8_388_608


@pytest.fixture(scope="module")
def committed() -> dict:
    from buusfury import identity

    path = identity.CONFIG_DIR / "rom_map.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rom_map(committed) -> rommap.RomMap:
    return rommap.RomMap.from_dict(committed)


@pytest.fixture(scope="module")
def ordered(rom_map):
    return sorted(rom_map.regions, key=lambda r: r.start)


# ---------------------------------------------------------------------------
# the ten required invariants
# ---------------------------------------------------------------------------
def test_invariant_1_map_starts_at_file_offset_zero(ordered):
    assert ordered[0].start == 0x000000


def test_invariant_2_map_ends_exactly_at_0x800000(ordered):
    assert ordered[-1].end == 0x800000


def test_invariant_3_no_region_overlaps_another(ordered):
    cursor = 0
    for region in ordered:
        assert region.start >= cursor, (
            f"{region.id} starts at 0x{region.start:06X} inside the previous region "
            f"(which ends at 0x{cursor:06X})"
        )
        cursor = region.end


def test_invariant_4_no_gaps(ordered):
    cursor = 0
    for region in ordered:
        assert region.start == cursor, (
            f"gap of {region.start - cursor} bytes before {region.id} at 0x{cursor:06X}"
        )
        cursor = region.end


def test_invariant_5_lengths_sum_to_the_rom_size(rom_map):
    assert sum(r.length for r in rom_map.regions) == ROM_SIZE == rom_map.rom_size


def test_invariant_6_address_conversion_is_consistent(ordered):
    for region in ordered:
        assert region.address_start == gba.to_address(region.start)
        assert gba.to_offset(region.address_start) == region.start
        assert region.address_end == gba.to_address(region.end - 1) + 1
        assert region.address_end - region.address_start == region.length


def test_invariant_7_generated_fixed_regions_reproduce(rom_bytes):
    """Covered in full by tests/test_fixed_regions.py; asserted here too."""
    from buusfury import fixed

    results = fixed.verify_all(rom_bytes)
    assert results, "no fixed regions were generated"
    assert all(r.matches_rom for r in results), [r.detail for r in results if not r.matches_rom]


def test_invariant_8_no_test_writes_to_the_canonical_rom(baserom):
    """The ROM's digest and mtime must be identical before and after a rebuild."""
    before = baserom.stat().st_mtime_ns
    import hashlib

    digest_before = hashlib.sha1(baserom.read_bytes()).hexdigest()
    from buusfury import analysis, mapbuild

    data = baserom.read_bytes()
    mapbuild.build_rom_map(data, digest_before)
    analysis.trace_reset(data)
    assert baserom.stat().st_mtime_ns == before
    assert hashlib.sha1(baserom.read_bytes()).hexdigest() == digest_before


def test_invariant_9_no_rom_bytes_are_committed():
    """No ROM image, save or state is tracked; data/ holds only the platform constant.

    Scoped to what Git would publish, so gitignored working copies under build/
    (which the baseline ticket legitimately creates) are not mistaken for
    committed content.
    """
    from buusfury import identity

    ignored_dirs = {".git", "build", "reference", "__pycache__"}
    for path in identity.REPO_ROOT.rglob("*"):
        if not path.is_file() or ignored_dirs & set(path.parts):
            continue
        assert not path.name.endswith((".gba", ".sav", ".ss1", ".ss2", ".sps")), path
    data_dir = identity.REPO_ROOT / "data"
    if data_dir.is_dir():
        for path in data_dir.rglob("*"):
            if not path.is_file():
                continue
            # Declared facts are text and are fine. The only BINARY permitted
            # under data/ is the 156-byte GBA platform constant, which
            # test_gba.py asserts is the standard boot logo.
            if path.suffix.lower() in (".json", ".md", ".txt", ".yaml", ".toml"):
                continue
            assert path.name == "gba_boot_logo.bin", path.name


def test_the_map_carries_extents_and_claims_never_bytes(committed):
    """A map is a description. It must not smuggle ROM bytes into the repo."""
    for region in committed["regions"]:
        assert set(region) & {"bytes_hex", "data", "blob", "hex", "raw"} == set(), region["id"]
    text = json.dumps(committed).lower()
    for needle in ("hexdump", "base64", "incbin_data"):
        assert needle not in text


def test_invariant_10_dragonbyte_z_is_never_a_write_target():
    """Production code must contain no path into the other checkout.

    A mention of the project by NAME in a provenance note is fine and expected;
    a hardcoded absolute path is what would let a future edit write into it. The
    needle is assembled at runtime so this test does not match itself.
    """
    from buusfury import identity

    needle_a = "C:" + "\\" + "Dev" + "\\" + "log1" + "-remake"
    needle_b = needle_a.replace("\\", "/")
    offenders = []
    for path in (identity.REPO_ROOT / "tools").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if needle_a in text or needle_b in text:
            offenders.append(str(path.relative_to(identity.REPO_ROOT)))
    assert not offenders, f"hardcoded paths to the other checkout: {offenders}"
    # And the two repositories must never be linked as one Git repository.
    assert not (identity.REPO_ROOT / ".gitmodules").exists(), (
        ".gitmodules would link this repository to another"
    )


# ---------------------------------------------------------------------------
# structural sanity that the ten invariants do not cover
# ---------------------------------------------------------------------------
def test_every_region_declares_evidence_and_provenance(rom_map):
    for region in rom_map.regions:
        assert region.evidence, f"{region.id} has no evidence"
        assert region.provenance, f"{region.id} has no provenance"
        assert region.confidence in rommap.CONFIDENCE_LEVELS
        assert region.classification in rommap.CLASSIFICATIONS


def test_region_ids_are_unique(rom_map):
    ids = [r.id for r in rom_map.regions]
    assert len(ids) == len(set(ids))


def test_coverage_by_classification_sums_to_the_rom_size(rom_map):
    coverage = rom_map.coverage()
    assert sum(slot["bytes"] for slot in coverage.values()) == ROM_SIZE
    for slot in coverage.values():
        assert sum(slot["confidence"].values()) == slot["bytes"]


def test_executable_coverage_sums_to_the_rom_size(rom_map):
    assert sum(rom_map.executable_coverage().values()) == ROM_SIZE


def test_no_code_region_is_merely_a_guess(rom_map):
    """`code` at `proven` or `high` must come from evidence, not a pattern match.

    This engine's Thumb data decodes at roughly 94%, so a windowed classifier
    cannot prove code. `high` is therefore reserved for recursive reachability
    and for region anchors whose extent was derived from the ROM.
    """
    allowed = {"reset_code", "gbaram_code", "codec_blob"}
    for region in rom_map.regions:
        if region.classification == "code" and region.confidence in ("proven", "high"):
            assert (
                "reachability" in region.provenance
                or "anchor" in region.provenance
                or "derived" in region.provenance
                or region.id in allowed
            ), f"{region.id} claims {region.confidence} code from: {region.provenance}"
    # And the heuristic must never emit `high` code at all.
    for region in rom_map.regions:
        if region.provenance.startswith("windowed classifier"):
            assert not (
                region.classification == "code" and region.confidence == "high"
            ), f"{region.id} is heuristic code claiming high confidence"


def test_invariant_regions_have_the_expected_shape(rom_map):
    expected = {
        "rom_header": (0x000000, 0x0000C0, "header", "proven"),
        "reset_code": (0x0000C0, 0x000134, "code", "proven"),
        "reset_literals": (0x000134, 0x000158, "lookup_table", "proven"),
        "text_string_pool": (0x05792C, 0x06BCE6, "strings", "proven"),
        "text_pointer_table": (0x06BCE8, 0x06D4E0, "pointer_table", "proven"),
        "codec_blob": (0x07B79A4, 0x07B89A8, "code", "high"),
        "opaque_tail_padding": (0x07B89A8, 0x0800000, "padding", "proven"),
    }
    by_id = {r.id: r for r in rom_map.regions}
    for region_id, (start, end, classification, confidence) in expected.items():
        region = by_id[region_id]
        assert (region.start, region.end) == (start, end), region_id
        assert region.classification == classification, region_id
        assert region.confidence == confidence, region_id


def test_codec_blob_is_arm_and_the_engine_is_mostly_thumb(rom_map):
    """Two independent ISA claims that the map must not silently flip."""
    by_id = {r.id: r for r in rom_map.regions}
    assert by_id["codec_blob"].isa == "arm"
    assert by_id["reset_code"].isa == "arm"
    assert by_id["gbaram_code"].isa == "thumb"
    isa = rom_map.isa_coverage()
    assert isa.get("thumb", 0) > isa.get("arm", 0), (
        "the engine decodes overwhelmingly as Thumb; an ARM-majority map means "
        "the classifier or the ISA propagation regressed"
    )


def test_the_padding_region_is_never_labelled_free_space(rom_map):
    """Fill value does not imply unused; the notes must say so."""
    region = next(r for r in rom_map.regions if r.id == "opaque_tail_padding")
    assert "NOT free space" in region.notes


def test_generated_fixed_regions_are_accounted_as_generated(rom_map):
    """The three promoted regions must not still be counted as copied bytes.

    If a region is regenerated from project facts but the map still calls it
    `incbin`, the coverage report understates what the project actually owns.
    """
    by_id = {r.id: r for r in rom_map.regions}
    for region_id in ("rom_header", "gbaram_literals", "titlescreen_data"):
        assert by_id[region_id].representation == "generated", region_id
    counts = rom_map.representation_coverage()
    assert counts["generated"] == 192 + 16 + 104 == 312
    assert counts["reproduced"] == 26_112
    assert sum(counts.values()) == ROM_SIZE


def test_reproduced_bytes_cover_the_baseline_asset_regions(rom_map):
    """The baseline's 26,112 reproduced bytes must still be exactly that.

    Six structural regions carry them, not the build model's ten: two pairs are
    merged here because they are contiguous and share a provenance (the two
    dialog-box streams, and the four corner images).
    """
    reproduced = [r for r in rom_map.regions if r.representation == "reproduced"]
    assert len(reproduced) == 6
    assert sum(r.length for r in reproduced) == 26_112
    assert all(
        r.classification in ("palette", "lookup_table", "compressed_asset") for r in reproduced
    )
    by_id = {r.id: r.length for r in reproduced}
    assert by_id == {
        "intro_asset": 2_980,
        "splash_asset": 20_516,
        "dialogbox_assets": 1_336,
        "corner_images": 256,
        "background_palette": 512,
        "object_palette": 512,
    }


def test_proven_bytes_are_a_meaningful_floor(rom_map):
    """A regression lock on how much of the ROM carries direct evidence.

    The floor is deliberately just below the measured value rather than near
    1.0: most of this cartridge is NOT proven, and the map says so. The point of
    this test is to catch the anchor set collapsing, not to flatter the map.
    """
    coverage = rom_map.coverage()
    proven = sum(slot["confidence"].get("proven", 0) for slot in coverage.values())
    assert proven > 400_000, (
        f"only {proven:,} bytes are proven; the anchor set or the fixed structures "
        "have regressed"
    )
    # The largest single proven structure is the padding run; if that vanishes
    # the map has lost its most certain region.
    assert coverage["padding"]["confidence"]["proven"] == 292_442


# ---------------------------------------------------------------------------
# ROM-gated: the map is reproducible from the ROM
# ---------------------------------------------------------------------------
def test_map_is_reproducible_from_the_rom(rom_bytes, committed):
    from buusfury import mapbuild

    rebuilt = mapbuild.build_rom_map(rom_bytes, committed["source_sha1"])
    assert len(rebuilt.regions) == len(committed["regions"])
    for fresh, saved in zip(
        sorted(rebuilt.regions, key=lambda r: r.start),
        sorted(committed["regions"], key=lambda r: int(r["file_start"], 0)),
    ):
        assert fresh.start == int(saved["file_start"], 0)
        assert fresh.end == int(saved["file_end"], 0)
        assert fresh.classification == saved["classification"]
        assert fresh.confidence == saved["confidence"]


def test_rebuild_is_deterministic(rom_bytes, committed):
    from buusfury import mapbuild

    first = mapbuild.build_rom_map(rom_bytes, committed["source_sha1"])
    second = mapbuild.build_rom_map(rom_bytes, committed["source_sha1"])
    assert first.to_json() == second.to_json()
