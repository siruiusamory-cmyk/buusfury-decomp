"""ROM-CAPACITY-AND-ALLOCATION-001 Checkpoint D: the production above-EOF path.

Checkpoint D has to show that a real game resource is placed above the original
8 MiB boundary by the production allocator, authorized by the production writer,
recorded by the production manifest, and pointed at by the real engine reference -
and that the same machinery refuses to reuse the span afterwards. The runtime half
of the proof - the derivative digest, and the 17,932-byte relocated dialogue
container the retail engine read at `0x08800000` - is recorded in
`docs/research/ROM_CAPACITY_AND_ALLOCATION.md`; this file is the deterministic
half, and it pins the derivative digest the runtime run must reproduce.

Nothing here is a research probe: every step uses the shipping path a project
build uses - `set_dialogue_replacement`, `build_project`, `emit_image`,
`WriteManifest` - and the allocator chooses the address.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.webfoot.allocation import (Addressability, AllocationKind, AllocationRequest,
                                      InsufficientSpaceError, RegionClass, allocate,
                                      reservations_from_manifest)
from tools.webfoot.binary import FileOffset
from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.dialogue import (get_dialogue_original, resolve_dialogue_target,
                                    set_dialogue_replacement)
from tools.webfoot.formats.webfoot_lz import unpack
from tools.webfoot.layout import AnchorId, RomRange
from tools.webfoot.profile import RomProfileCatalog

ROM = Path("roms/Dragon Ball Z - Buu's Fury (U).gba")
SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
CANONICAL_EOF = 0x00800000
EXPANSION_BASE_ADDRESS = 0x08800000
SELECTOR_TABLE = 0x7B5B64
SELECTOR_ONE_SLOT = 0x7B5B68
#: The other six of the table's seven words. Only selector 1's word may move.
UNCHANGED_SELECTOR_SLOTS = tuple(slot for slot in range(SELECTOR_TABLE,
                                                        SELECTOR_TABLE + 28, 4)
                                 if slot != SELECTOR_ONE_SLOT)
ORIGINAL_LINE = "Good luck, Goku!"
AUTHORED_LINE = "Nice work, Goku!"
AUTHORED_RESOURCE = "goku-greeting"
AUTHORED_PAYLOAD_SIZE = 17932
RETAIL_CONTAINER_OFFSET = 0x7A04F0
#: The digest the production path produces for this one authored substitution.
#: The runtime artifact must reproduce it byte for byte.
DERIVATIVE_SHA256 = "3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb"


def canonical_rom() -> Path:
    if not ROM.is_file() or hashlib.sha256(ROM.read_bytes()).hexdigest() != SHA:
        pytest.skip("canonical Buu ROM is not available")
    return ROM


def authored_project(tmp_path: Path, catalog) -> Path:
    """A real extracted project with one authored dialogue substitution."""
    project = tmp_path / "project"
    extract_project(ROM, project, catalog, graphics=False)
    profile = catalog.profiles[0]
    target = resolve_dialogue_target(
        {"source": "decoded-container-text",
         "identity": {"packed_handle": "0x02002641"}}, profile)
    assert target is not None and target.name == AUTHORED_RESOURCE
    assert get_dialogue_original(ROM.read_bytes(), profile, target) == ORIGINAL_LINE
    set_dialogue_replacement(project, profile, target, AUTHORED_LINE)
    return project


def expanded_request(name: str, size: int, *, kind=AllocationKind.PACKED_STREAM,
                     evidence="checkpoint D control") -> AllocationRequest:
    return AllocationRequest(AnchorId(name), name, size, 4, kind=kind,
                             addressability=Addressability.EXPANDED_PERMITTED,
                             evidence=evidence)


def test_the_production_build_places_the_resource_above_canonical_eof(tmp_path):
    """The whole chain, through the shipping build, with the allocator choosing."""
    canonical_rom()
    catalog = RomProfileCatalog.load("config/roms.yaml")
    profile = catalog.profiles[0]
    project = authored_project(tmp_path, catalog)
    assert validate_project(project, ROM, catalog).passed

    output = tmp_path / "authored.gba"
    result = build_project(project, ROM, output, catalog)

    # A real retail-derived resource, allocated above the original 8 MiB boundary.
    allocation, = result.manifest.generated_allocations
    assert allocation.domain == "compressed_dialogue"
    assert allocation.owner == f"compressed-dialogue:{AUTHORED_RESOURCE}"
    assert allocation.source_range.start.value == RETAIL_CONTAINER_OFFSET
    assert allocation.allocated_range.start.value >= CANONICAL_EOF
    assert allocation.allocated_rom_address >= EXPANSION_BASE_ADDRESS
    assert allocation.allocated_range.size == AUTHORED_PAYLOAD_SIZE

    # The placement came from the profile's declared expansion region under the
    # deterministic policy - not from a literal in the domain code.
    expanded = profile.generated_expansion
    assert expanded is not None
    declared = expanded.free_region(profile.size).range
    assert declared.start.value == CANONICAL_EOF
    assert declared.contains(FileOffset(allocation.allocated_range.start.value))
    assert allocation.expansion_evidence == expanded.evidence
    production = Path("tools/webfoot/compressed_dialogue.py").read_text(encoding="utf-8")
    for literal in ("0x800000", "0x00800000", "0x08800000", "8388608", "16777216"):
        assert literal not in production, literal

    # The production writer emitted a derivative and the manifest records it.
    assert output.stat().st_size == 0x1000000
    assert hashlib.sha256(output.read_bytes()).hexdigest() == DERIVATIVE_SHA256
    assert result.manifest_path is not None
    document = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert document["base"]["sha256"] == SHA
    assert document["base"]["profile_id"] == profile.id
    assert document["output"]["sha256"] == DERIVATIVE_SHA256
    entry, = document["generated_allocations"]
    assert entry["allocated_range"]["file_offset"] == allocation.allocated_range.start.value
    assert entry["allocated_range"]["size"] == AUTHORED_PAYLOAD_SIZE
    assert entry["allocated_rom_address"] == allocation.allocated_rom_address
    assert entry["pointer_offset"] == SELECTOR_ONE_SLOT
    assert entry["allocation_class"] == "generated_expansion"

    # The engine-visible reference now names the allocated address, and exactly
    # that one word moved in the canonical prefix.
    base = ROM.read_bytes()
    generated = output.read_bytes()
    assert generated[SELECTOR_ONE_SLOT:SELECTOR_ONE_SLOT + 4] \
        == allocation.allocated_rom_address.to_bytes(4, "little")
    for slot in UNCHANGED_SELECTOR_SLOTS:
        assert generated[slot:slot + 4] == base[slot:slot + 4], hex(slot)
    moved = {index for index in range(CANONICAL_EOF)
             if generated[index] != base[index]}
    assert moved <= set(range(SELECTOR_ONE_SLOT, SELECTOR_ONE_SLOT + 4)), moved
    assert moved, "the selector word must actually change"

    # The relocated bytes really are the authored resource, not the retail text.
    container = unpack(generated, allocation.allocated_range.start.value)
    assert container.data[0x132:0x152] == AUTHORED_LINE.encode("utf-16le")
    assert container.data[0x132:0x152] != ORIGINAL_LINE.encode("utf-16le")

    # The canonical ROM is untouched; the derivative is a separate file.
    assert hashlib.sha256(ROM.read_bytes()).hexdigest() == SHA
    assert output != ROM


def test_the_address_is_the_allocators_choice_not_a_hard_coded_constant(tmp_path, monkeypatch):
    """Move the allocator's inputs and the address follows them.

    A hard-coded `0x800000` would survive this. The control issues an earlier
    reservation through the build-scoped set the coordinator already threads, and
    the dialogue payload must land after it.
    """
    canonical_rom()
    import tools.webfoot.authored_placements as authored_placements

    issued = RomRange(FileOffset(CANONICAL_EOF), 0x100)

    def reserve_expansion_prefix(project, maps, document_factory, reserved=()):
        assert reserved == ()
        return [], frozenset(), (issued,)

    monkeypatch.setattr(authored_placements, "materialize_for_build",
                        reserve_expansion_prefix)
    catalog = RomProfileCatalog.load("config/roms.yaml")
    project = authored_project(tmp_path, catalog)
    result = build_project(project, ROM, tmp_path / "shifted.gba", catalog)
    allocation, = result.manifest.generated_allocations
    assert allocation.allocated_range.start.value == CANONICAL_EOF + 0x100
    assert allocation.allocated_rom_address == EXPANSION_BASE_ADDRESS + 0x100
    assert not allocation.allocated_range.overlaps(issued)
    assert allocation.allocated_range.size == AUTHORED_PAYLOAD_SIZE


def test_reopening_the_real_manifest_reserves_the_span(tmp_path):
    """The derivative's own provenance becomes the reservation set."""
    canonical_rom()
    catalog = RomProfileCatalog.load("config/roms.yaml")
    profile = catalog.profiles[0]
    project = authored_project(tmp_path, catalog)
    result = build_project(project, ROM, tmp_path / "authored.gba", catalog)
    allocation, = result.manifest.generated_allocations

    document = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    reopened = reservations_from_manifest(document)
    assert [r.range for r in reopened] == [allocation.allocated_range]

    # Without those reservations the allocator WOULD take the same span, so the
    # reservation is what prevents reuse rather than the span being unreachable.
    # The request is the real payload size, which no canonical region can host.
    naive = allocate(profile, [expanded_request("second", AUTHORED_PAYLOAD_SIZE)])[0]
    assert naive.range == allocation.allocated_range

    second = allocate(profile, [expanded_request("second", AUTHORED_PAYLOAD_SIZE)],
                      occupied=reopened)[0]
    assert second.storage_class is RegionClass.PADDING_EXPANDED
    assert not second.range.overlaps(allocation.allocated_range)
    assert second.range.start.value == allocation.allocated_range.end

    # The rebuild from the same inputs is byte-identical, manifest included.
    again = build_project(project, ROM, tmp_path / "again.gba", catalog)
    assert hashlib.sha256((tmp_path / "again.gba").read_bytes()).hexdigest() \
        == DERIVATIVE_SHA256
    assert again.manifest.generated_allocations == result.manifest.generated_allocations


def test_a_canonical_only_domain_cannot_receive_expanded_storage():
    """The bounded negative control: unproven addressability fails closed.

    The canonical image declares 256 bytes of free space, far less than a dialogue
    payload, so a request whose domain is not proven above canonical EOF cannot be
    satisfied at all - and it must never be handed the expanded region instead.
    """
    canonical_rom()
    profile = RomProfileCatalog.load("config/roms.yaml").profiles[0]

    unproven = AllocationRequest(
        AnchorId("compressed-dialogue:unproven"), "compressed-dialogue:unproven",
        AUTHORED_PAYLOAD_SIZE, 4, kind=AllocationKind.PLACEMENT_BODY,
        evidence="negative control: unproven domain")
    assert unproven.addressability is Addressability.CANONICAL_ONLY
    with pytest.raises(InsufficientSpaceError):
        allocate(profile, [unproven])

    # The same size through the proven kind does get an above-EOF placement, so
    # the refusal above is about addressability and not about capacity.
    proven = expanded_request("compressed-dialogue:proven", AUTHORED_PAYLOAD_SIZE)
    allocation = allocate(profile, [proven])[0]
    assert allocation.is_expanded is True
    assert allocation.range.start.value >= CANONICAL_EOF
    assert allocation.range.size == AUTHORED_PAYLOAD_SIZE

    # And a canonical-only request can never be handed an expanded span, whatever
    # the model offers: only the proven kind has expanded addressability.
    assert AllocationRequest(AnchorId("x"), "x", 4, 4,
                             kind=AllocationKind.TEXT_STRING).addressability \
        is Addressability.CANONICAL_ONLY


def test_the_canonical_rom_declares_no_promoted_candidate_capacity():
    """Checkpoint D promoted nothing: free space is still the 256-byte window."""
    canonical_rom()
    profile = RomProfileCatalog.load("config/roms.yaml").profiles[0]
    assert len(profile.free_regions) == 1
    region, = profile.free_regions
    assert (region.range.start.value, region.range.size) == (0x7EA400, 256)
    # The candidate windows stay unreachable from the allocator: it consumes
    # declared regions only, and this profile declares none of them.
    assert profile.generated_expansion is not None
