"""ROM-CAPACITY-AND-ALLOCATION-001 addendum: the domain reachable-capacity map.

Checkpoint A asked "what can each pointer domain address?" and answered it
qualitatively. This module answers it *quantitatively*, one row per domain, and it
keeps three reachability levels apart because collapsing them is how a 32-bit
field becomes a capacity claim:

``ENCODING``
    the field's wire form can represent the address at all. A 4-byte absolute GBA
    pointer encodes the whole documented ROM window; that is a property of the
    format and of nothing else.

``ENGINE_STATIC``
    static analysis of the consuming code found no truncation, masking, sign
    extension, fixed high bits or comparison that would reject the address. This
    is deliberately ``UNKNOWN`` almost everywhere, because *not finding* a bound is
    not the same as proving there is none, and this project has been wrong before
    by promoting the absence of evidence.

``RUNTIME``
    a real derivative actually caused the engine to dereference bytes in that
    range. Exactly one domain has this, and only over the extent it read.

The numbers are per domain and none of them is inferred from the nominal GBA
window alone: where a value is not established it is ``None``, and the report
prints ``UNKNOWN``. `validate` enforces the ordering the levels imply, so a
theoretical maximum can never be recorded as runtime-proven.

Research adapter: it measures and reports, and promotes nothing.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from tools.webfoot.binary import GBA_ROM_BASE

#: The documented Game Pak ROM window upper bound, from `binary.GBA_ROM_BASE`.
#: PLATFORM evidence (GBATEK), not a measurement of this engine.
ROM_WINDOW_END = GBA_ROM_BASE + 0x02000000 - 1          # 0x09FFFFFF
ROM_WINDOW_END_OFFSET = ROM_WINDOW_END - GBA_ROM_BASE   # 0x01FFFFFF

#: The profile contract's own ceiling on a generated image: at most 32 MiB and a
#: power of two (`profile.py:782-788`). Policy, not engine behaviour.
GENERATED_IMAGE_CEILING = 0x02000000

#: The largest generated image any experiment has used: the declared expansion of
#: the canonical profile, and the size the Checkpoint D derivative was emitted at.
PROVEN_GENERATED_SIZE = 0x01000000

CANONICAL_SIZE = 0x00800000
CANONICAL_EOF = CANONICAL_SIZE
#: The one canonical region a reviewed ticket declared free (TOOLKIT-028).
CANONICAL_VERIFIED_FREE = 256
EXPANSION_BASE = CANONICAL_SIZE                          # file offset
EXPANSION_BASE_ADDRESS = GBA_ROM_BASE + CANONICAL_SIZE   # 0x08800000
#: The production allocation Checkpoint D emitted: a rebuilt dialogue container.
CHECKPOINT_D_ALLOCATION_OFFSET = 0x00800000
CHECKPOINT_D_ALLOCATION_SIZE = 17932
CHECKPOINT_D_ALLOCATION_END = CHECKPOINT_D_ALLOCATION_OFFSET + CHECKPOINT_D_ALLOCATION_SIZE


class ProofLevel(str, Enum):
    """The strongest thing established for a domain's reach above canonical EOF."""

    NONE = "NONE"                 # not established at all
    ENCODING = "ENCODING"         # the wire form can encode it
    ENGINE_STATIC = "ENGINE_STATIC"  # static analysis found no rejecting bound
    RUNTIME = "RUNTIME"           # a real derivative was dereferenced there


class StructuralClass(str, Enum):
    """Whether the count/index/table limit that bounds a domain can grow."""

    FIXED = "FIXED"                       # proven bound, no growth path
    RELOCATABLE = "RELOCATABLE"           # the payload may move; the count may not
    THEORETICALLY_WIDENABLE = "THEORETICALLY_WIDENABLE"  # needs an executable patch
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class DomainReach:
    """One domain's reachable capacity, with the evidence for every number."""

    key: str
    title: str
    pointer_form: str
    #: Highest FILE OFFSET the wire form can represent, or None.
    encoding_max_offset: int | None
    #: Highest file offset static analysis supports, or None (UNKNOWN).
    engine_static_max_offset: int | None
    #: Range a real derivative caused the engine to dereference, or None.
    runtime_min_offset: int | None
    runtime_max_offset: int | None
    #: Canonical VERIFIED_FREE bytes this domain can address.
    canonical_reachable_bytes: int | None
    #: Expanded bytes the wire form can represent.
    expanded_encodable_bytes: int | None
    #: Expanded bytes static analysis supports, or None (UNKNOWN).
    expanded_engine_bytes: int | None
    #: Expanded bytes a runtime run actually dereferenced.
    expanded_runtime_bytes: int | None
    structural_limit: str
    structural_class: StructuralClass
    alignment: str
    allocator_policy: str
    bottleneck: str
    notes: str
    evidence: tuple[str, ...]

    @property
    def proof_level(self) -> ProofLevel:
        if self.runtime_max_offset is not None:
            return ProofLevel.RUNTIME
        if self.engine_static_max_offset is not None:
            return ProofLevel.ENGINE_STATIC
        if self.encoding_max_offset is not None:
            return ProofLevel.ENCODING
        return ProofLevel.NONE

    def to_json(self) -> dict:
        def offset(value):
            return None if value is None else {
                "file_offset": value, "hex": f"0x{value:08X}",
                "rom_address": GBA_ROM_BASE + value,
                "rom_address_hex": f"0x{GBA_ROM_BASE + value:08X}"}
        return {
            "domain": self.key, "title": self.title, "pointer_form": self.pointer_form,
            "proof_level": self.proof_level.value,
            "encoding_max": offset(self.encoding_max_offset),
            "engine_static_max": offset(self.engine_static_max_offset),
            "runtime_proven_min": offset(self.runtime_min_offset),
            "runtime_proven_max": offset(self.runtime_max_offset),
            "canonical_verified_free_reachable": self.canonical_reachable_bytes,
            "expanded_encodable_bytes": self.expanded_encodable_bytes,
            "expanded_engine_justified_bytes": self.expanded_engine_bytes,
            "expanded_runtime_proven_bytes": self.expanded_runtime_bytes,
            "structural_limit": self.structural_limit,
            "structural_class": self.structural_class.value,
            "alignment": self.alignment,
            "allocator_policy": self.allocator_policy,
            "bottleneck": self.bottleneck,
            "notes": self.notes,
            "evidence": list(self.evidence),
        }


#: One row per domain in the Checkpoint A inventory, same sixteen, same names.
DOMAINS: tuple[DomainReach, ...] = (
    DomainReach(
        key="generic_rom_pointer", title="Generic ROM pointers",
        pointer_form="absolute GBA u32 LE; no relative form",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="none (a helper, not a table)",
        structural_class=StructuralClass.THEORETICALLY_WIDENABLE,
        alignment="none imposed by the helper",
        allocator_policy="per kind: only PACKED_STREAM defaults expanded-permitted",
        bottleneck="no bound found is not a bound found: the consumer decides",
        notes="Representation is CONFIRMED; engine acceptance above EOF is UNKNOWN "
              "for every consumer that has not been tested.",
        evidence=("tools/webfoot/binary.py:8,22-25,46-57",
                  "docs/research/ROM_CAPACITY_AND_ALLOCATION.md section 4"),
    ),
    DomainReach(
        key="compressed_dialogue_selector", title="Compressed-dialogue selector table",
        pointer_form="absolute GBA u32 LE at 0x7B5B64 + selector*4",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None,
        runtime_min_offset=CHECKPOINT_D_ALLOCATION_OFFSET,
        runtime_max_offset=CHECKPOINT_D_ALLOCATION_END - 1,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None,
        expanded_runtime_bytes=CHECKPOINT_D_ALLOCATION_SIZE,
        structural_limit="exactly 7 selectors; the gate must NOT be widened",
        structural_class=StructuralClass.FIXED,
        alignment="4 (word-indexed table)",
        allocator_policy="PACKED_STREAM, EXPANDED_PERMITTED",
        bottleneck="the 7-entry selector table, not bytes: 8 MiB of expansion "
                   "cannot add an eighth container",
        notes="The one domain with runtime proof above EOF. Proven over the extent "
              "the engine actually read - the relocated container - NOT over the "
              "whole expansion.",
        evidence=("docs/research/ROM_EXPANSION.md:24-46",
                  "docs/research/archive/ROM-EXPAND-001-COMPLETE.md:149-176",
                  "tools/webfoot/compressed_dialogue.py:68-77,142-168",
                  "docs/research/ROM-CAPACITY-AND-ALLOCATION-001-checkpoint-d.md"),
    ),
    DomainReach(
        key="map_entry_scripts_pointer", title="MapEntry +0x14 object array pointer",
        pointer_form="absolute GBA u32 LE; count is +0x04 (u8)",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="object count is one byte: 255 per map",
        structural_class=StructuralClass.RELOCATABLE,
        alignment="4",
        allocator_policy="PLACEMENT_REFERENCE_ARRAY, canonical-only",
        bottleneck="the count byte, then the relocation-eligible array kind",
        notes="Relocatable as an anchor kind; expansion above EOF is UNKNOWN.",
        evidence=("docs/research/BUU_PLACEMENT_RUN_RELOCATION.md:70-71,96-142",
                  "tools/webfoot/authored_placements.py:260-263"),
    ),
    DomainReach(
        key="map_entry_variation_array", title="MapEntry +0x2C scene selector array",
        pointer_form="base of a u32 selector array; descriptor = base + 4*(selector-1)",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="selector width UNKNOWN; longest observed run is 12 words",
        structural_class=StructuralClass.UNKNOWN,
        alignment="4",
        allocator_policy="canonical-only (no kind allocates it)",
        bottleneck="selector resolution proven only for selector 1",
        notes="Resolution mechanism CONFIRMED at LEVEL 3; expansion UNKNOWN.",
        evidence=("tools/webfoot/atlas_producers/seed.py:201-202",
                  "tools/webfoot/map_render.py:327-332"),
    ),
    DomainReach(
        key="map_entry_other_pointers",
        title="MapEntry +0x10/+0x18/+0x1C/+0x20/+0x28/+0x30/+0x34",
        pointer_form="absolute GBA u32 LE (shape only; no consumer decoded)",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=None,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="+0x10 count field is UNIDENTIFIED",
        structural_class=StructuralClass.UNKNOWN,
        alignment="4",
        allocator_policy="canonical-only",
        bottleneck="no consumer decoded, so no bound and no capacity claim",
        notes="The toolkit still sizes the +0x10 extent with +0x04, a pairing the "
              "project has since shown bounds +0x14 instead.",
        evidence=("docs/research/MAP_FORMAT.md:184-187",
                  "tools/webfoot/maps.py:308-315",
                  "docs/research/BUU_PLACEMENT_RUN_RELOCATION.md:207-219"),
    ),
    DomainReach(
        key="placement_run", title="Placement-run pointer array (engine object array)",
        pointer_form="array of absolute GBA u32 LE; exactly count*4, no sentinel",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="255 slots per map (MapEntry+0x04, one ldrb)",
        structural_class=StructuralClass.RELOCATABLE,
        alignment="4",
        allocator_policy="PLACEMENT_REFERENCE_ARRAY, canonical-only",
        bottleneck="the count byte",
        notes="Traversal contract CONFIRMED; address range above EOF UNKNOWN.",
        evidence=("docs/research/BUU_PLACEMENT_RUN_RELOCATION.md:96-142,290",
                  "docs/research/BUU_MAP_OBJECT_ARRAYS.md:32-48"),
    ),
    DomainReach(
        key="map_slot_arrays", title="Eight-byte slot arrays (MapEntry +0x10)",
        pointer_form="two u32 LE per slot; second word treated as a reference",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="array shape by measurement; no engine count decoded",
        structural_class=StructuralClass.UNKNOWN,
        alignment="4 (required by the classifier)",
        allocator_policy="canonical-only",
        bottleneck="the typed rung is a heuristic, not a decoded consumer",
        notes="Round-trip is proven for the bytes; semantics are not.",
        evidence=("tools/webfoot/formats/map_slots.py:69-71,153-164",),
    ),
    DomainReach(
        key="placement_records", title="Placement and descriptor records",
        pointer_form="u32 LE words at fixed record offsets; child_count 1..4",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="child_count clamped 1..4 (corpus bound, not an engine max)",
        structural_class=StructuralClass.UNKNOWN,
        alignment="4",
        allocator_policy="canonical-only",
        bottleneck="the descriptor pointer's own validation window",
        notes="The only production pointer bound using the nominal 32 MiB window "
              "(map_placements.py:166); that is a TOOLKIT bound, not engine evidence.",
        evidence=("tools/webfoot/formats/map_placements.py:1-8,83-131,166",
                  "docs/research/PLACEMENT_CODEC.md:22,47"),
    ),
    DomainReach(
        key="text_table", title="Text pointer table and string pool",
        pointer_form="absolute LE GBA addresses; access is by index",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="1,534 entries; index widths u16 at consumers (65,535 max)",
        structural_class=StructuralClass.THEORETICALLY_WIDENABLE,
        alignment="pool alignment 2",
        allocator_policy="TEXT_STRING, canonical-only",
        bottleneck="the table has no growth path: a 1,535th string needs the table "
                   "grown and 51 code references rewritten",
        notes="Per-ENTRY relocation is proven on synthetic fixtures only.",
        evidence=("docs/research/TEXT_FORMAT.md:79-101,120-153",
                  "tools/webfoot/formats/text_tables.py:66,260-278"),
    ),
    DomainReach(
        key="script_bodies", title="Script record slots and bodies",
        pointer_form="absolute u32 LE in the record slot; body offset is pool-relative",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="static40: exactly 40 records (engine bound); item_use: 83",
        structural_class=StructuralClass.FIXED,
        alignment="4",
        allocator_policy="canonical-only",
        bottleneck="the walker's immediate: retail is exactly at the 40-record bound",
        notes="28 execute from a runtime cursor, so a static pool cannot enumerate "
              "every reachable body.",
        evidence=("docs/research/BUU_SCRIPT_VM.md:92-119,160-172",
                  "tools/webfoot/scripts.py:144-175"),
    ),
    DomainReach(
        key="actor_sprite_chain",
        title="Actor sprite chain (character/animation/frame/piece/container)",
        pointer_form="absolute u32 LE at every hop",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="297 sprite definitions, terminated by a non-ROM word",
        structural_class=StructuralClass.FIXED,
        alignment="4 on the table; no alignment test on a container pointer",
        allocator_policy="canonical-only",
        bottleneck="the 297-entry run and its literal terminator",
        notes="Containers are packed with zero slack: pixel edits do not relocate.",
        evidence=("docs/research/GRAPHICS_FORMAT.md:92-122,454-485",
                  "tools/webfoot/graphics.py:755-759"),
    ),
    DomainReach(
        key="map_graphics", title="Map scene descriptor and map graphics",
        pointer_form="absolute u32 LE at fixed descriptor offsets",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="187 tile banks declared 0x4000 each",
        structural_class=StructuralClass.UNKNOWN,
        alignment="4",
        allocator_policy="canonical-only",
        bottleneck="VRAM character extent, not ROM bytes (see runtime ceilings)",
        notes="Rendering is proven only for maps 39/40, within the canonical image.",
        evidence=("docs/research/MAP_RENDER_FORMAT.md:73-91,211-225",
                  "tools/webfoot/formats/map_graphics.py:403-422"),
    ),
    DomainReach(
        key="palettes", title="Object and background palettes",
        pointer_form="NO indirection: a fixed absolute address, entry is the colour",
        encoding_max_offset=None,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=0,
        expanded_encodable_bytes=0, expanded_engine_bytes=0, expanded_runtime_bytes=0,
        structural_limit="256 object entries; 256 background entries",
        structural_class=StructuralClass.FIXED,
        alignment="2",
        allocator_policy="no kind allocates a palette; edits are in place",
        bottleneck="the address is a code literal, so a palette cannot be moved "
                   "without an executable patch",
        notes="The one authoring class with no capacity question at all.",
        evidence=("tools/webfoot/graphics.py:487-506",
                  "docs/research/MAP_RENDER_FORMAT.md:37,128-132"),
    ),
    DomainReach(
        key="stat_tables", title="Stat tables and the placement-type selector",
        pointer_form="fixed table + stride; the selector is an INDEX, not a pointer",
        encoding_max_offset=None,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=0,
        expanded_encodable_bytes=0, expanded_engine_bytes=0, expanded_runtime_bytes=0,
        structural_limit="enemy_stats 141 x 0x1C; character_base_stats 9 x 0x12",
        structural_class=StructuralClass.FIXED,
        alignment="4",
        allocator_policy="no kind allocates a stat table",
        bottleneck="the table address is a code literal; six selectors already "
                   "point past the verified extent",
        notes="Index encodings are read-only: reassignment is not verified.",
        evidence=("docs/research/PLACEMENT_TYPES.md:45-48,116-120",
                  "tools/webfoot/layout.py:149-150"),
    ),
    DomainReach(
        key="relocation_families", title="Relocation and indirect pointer families",
        pointer_form="ABSOLUTE_ROM_U32_LE, RELATIVE_I32_LE, INDEX_U32_LE, INDEX_U8",
        encoding_max_offset=ROM_WINDOW_END_OFFSET,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=CANONICAL_VERIFIED_FREE,
        expanded_encodable_bytes=ROM_WINDOW_END_OFFSET - CANONICAL_EOF,
        expanded_engine_bytes=None, expanded_runtime_bytes=None,
        structural_limit="two anchor kinds are relocation-eligible",
        structural_class=StructuralClass.THEORETICALLY_WIDENABLE,
        alignment="4 (1 for INDEX_U8)",
        allocator_policy="depends on the anchor kind's semantic class",
        bottleneck="RELATIVE_I32_LE has no ROM user; index encodings are read-only",
        notes="There is no relocation table in the ROM; relocation is a codec phase "
              "over anchors and typed references.",
        evidence=("tools/webfoot/layout.py:120-158,188-196,238",
                  "tools/webfoot/relocation.py:47-141"),
    ),
    DomainReach(
        key="packed_text_handle", title="Packed text handle",
        pointer_form="32-bit handle: selector 0-5, decoded start 6-20, length 21-31",
        encoding_max_offset=None,
        engine_static_max_offset=None, runtime_min_offset=None, runtime_max_offset=None,
        canonical_reachable_bytes=None,
        expanded_encodable_bytes=None, expanded_engine_bytes=None,
        expanded_runtime_bytes=None,
        structural_limit="selector 6 bits (64) but only 7 containers exist; "
                         "record length 0..4,094 bytes",
        structural_class=StructuralClass.FIXED,
        alignment="no address; the extent is even by construction",
        allocator_policy="not an address carrier; the selector slot carries the pointer",
        bottleneck="the handle never moves, which is why relocation works at all",
        notes="Proven address-INDEPENDENT: the handle was unchanged while its "
              "container moved to 0x08800000. It is not itself an above-EOF carrier.",
        evidence=("tools/webfoot/handles.py:17-31",
                  "docs/research/archive/TEXT-HANDLE-002-COMPLETE.md:79-82"),
    ),
)


def validate(domains: tuple[DomainReach, ...] = DOMAINS) -> None:
    """Refuse a map whose levels contradict each other or Checkpoint A."""
    if len(domains) != 16:
        raise ValueError(f"the Checkpoint A inventory has 16 domains, not {len(domains)}")
    keys = [domain.key for domain in domains]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate domain key")
    for domain in domains:
        if domain.runtime_max_offset is not None:
            if domain.runtime_min_offset is None:
                raise ValueError(f"{domain.key}: runtime range has no start")
            if domain.runtime_min_offset > domain.runtime_max_offset:
                raise ValueError(f"{domain.key}: runtime range is inverted")
            if (domain.encoding_max_offset is not None
                    and domain.runtime_max_offset > domain.encoding_max_offset):
                raise ValueError(
                    f"{domain.key}: runtime-proven offset exceeds what the format encodes")
            if (domain.engine_static_max_offset is not None
                    and domain.runtime_max_offset > domain.engine_static_max_offset):
                raise ValueError(
                    f"{domain.key}: runtime-proven offset exceeds the static bound")
        if (domain.engine_static_max_offset is not None
                and domain.encoding_max_offset is not None
                and domain.engine_static_max_offset > domain.encoding_max_offset):
            raise ValueError(
                f"{domain.key}: static bound exceeds what the format encodes")
        if (domain.expanded_runtime_bytes or 0) > (domain.expanded_encodable_bytes or 0):
            raise ValueError(f"{domain.key}: runtime-proven bytes exceed encodable bytes")
        if (domain.expanded_engine_bytes or 0) > (domain.expanded_encodable_bytes or 0):
            raise ValueError(f"{domain.key}: static bytes exceed encodable bytes")
        if not domain.evidence:
            raise ValueError(f"{domain.key}: no evidence recorded")
    runtime = [d for d in domains if d.proof_level is ProofLevel.RUNTIME]
    if len(runtime) != 1 or runtime[0].key != "compressed_dialogue_selector":
        raise ValueError(
            "exactly one domain is runtime-proven above EOF, and it is the "
            "compressed-dialogue selector")


def checkpoints() -> dict:
    """The headline numbers the report and the status return quote."""
    validate()
    encodable = [d for d in DOMAINS if d.encoding_max_offset is not None
                 and d.encoding_max_offset > CANONICAL_EOF]
    static = [d for d in DOMAINS if d.engine_static_max_offset is not None]
    runtime = [d for d in DOMAINS if d.proof_level is ProofLevel.RUNTIME]
    return {
        "domains": len(DOMAINS),
        "raw_physical_expanded_bytes": PROVEN_GENERATED_SIZE - CANONICAL_SIZE,
        "canonical_verified_free_bytes": CANONICAL_VERIFIED_FREE,
        "domains_encoding_capable_above_eof": [d.key for d in encodable],
        "domains_engine_static_capable_above_eof": [d.key for d in static],
        "domains_runtime_proven_above_eof": [d.key for d in runtime],
        "allocator_expanded_default_domains": ["compressed_dialogue_selector"],
        "rom_window_end_address": ROM_WINDOW_END,
        "generated_image_ceiling": GENERATED_IMAGE_CEILING,
        "proven_generated_size": PROVEN_GENERATED_SIZE,
        "runtime_proven_offset_range": [CHECKPOINT_D_ALLOCATION_OFFSET,
                                        CHECKPOINT_D_ALLOCATION_END - 1],
        "runtime_proven_address_range": [GBA_ROM_BASE + CHECKPOINT_D_ALLOCATION_OFFSET,
                                         GBA_ROM_BASE + CHECKPOINT_D_ALLOCATION_END - 1],
    }


MARKER_BEGIN = "<!-- BEGIN GENERATED: domain reachable-capacity map -->"
MARKER_END = "<!-- END GENERATED: domain reachable-capacity map -->"


def _cells(domain: DomainReach) -> dict:
    return {
        "canonical": ("UNKNOWN" if domain.canonical_reachable_bytes is None
                      else str(domain.canonical_reachable_bytes)),
        "encodable": ("UNKNOWN" if domain.expanded_encodable_bytes is None
                      else f"{domain.expanded_encodable_bytes:,}"),
        "engine": ("UNKNOWN" if domain.expanded_engine_bytes is None
                   else f"{domain.expanded_engine_bytes:,}"),
        "runtime": ("UNKNOWN" if domain.expanded_runtime_bytes is None
                    else f"{domain.expanded_runtime_bytes:,}"),
        "max_encodable": ("UNKNOWN" if domain.encoding_max_offset is None
                          else f"0x{GBA_ROM_BASE + domain.encoding_max_offset:08X}"),
        "max_engine": ("UNKNOWN" if domain.engine_static_max_offset is None
                       else f"0x{GBA_ROM_BASE + domain.engine_static_max_offset:08X}"),
        "max_runtime": ("UNKNOWN" if domain.runtime_max_offset is None else
                        f"0x{GBA_ROM_BASE + domain.runtime_min_offset:08X}.."
                        f"0x{GBA_ROM_BASE + domain.runtime_max_offset:08X}"),
    }


def markdown_table() -> str:
    """The reachable-capacity tables, GENERATED so the report cannot drift.

    The report embeds this between :data:`MARKER_BEGIN` and :data:`MARKER_END`, and
    a test compares the two, so a number changed here without regenerating the
    report fails instead of leaving a stale figure in a durable document.
    """
    lines = [
        MARKER_BEGIN,
        "",
        "#### Reachable bytes by domain",
        "",
        "| Domain | Pointer / reference form | Canonical VERIFIED_FREE reachable | "
        "Expanded ENCODABLE bytes | Expanded ENGINE-JUSTIFIED bytes | "
        "Expanded RUNTIME-PROVEN bytes | Proof level |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for domain in DOMAINS:
        cell = _cells(domain)
        lines.append(f"| {domain.title} | {domain.pointer_form} | {cell['canonical']} | "
                     f"{cell['encodable']} | {cell['engine']} | {cell['runtime']} | "
                     f"{domain.proof_level.value} |")
    lines += [
        "",
        "#### Address ranges, limits and policy by domain",
        "",
        "| Domain | Max ENCODABLE address | Max ENGINE-JUSTIFIED address | "
        "RUNTIME-PROVEN address | Structural / table limit | Structural class | "
        "Alignment / format | Allocator range policy | Primary bottleneck | Notes / UNKNOWN |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for domain in DOMAINS:
        cell = _cells(domain)
        lines.append(
            f"| {domain.title} | {cell['max_encodable']} | {cell['max_engine']} | "
            f"{cell['max_runtime']} | {domain.structural_limit} | "
            f"{domain.structural_class.value} | {domain.alignment} | "
            f"{domain.allocator_policy} | {domain.bottleneck} | {domain.notes} |")
    lines += ["", MARKER_END]
    return "\n".join(lines) + "\n"


def main() -> int:
    validate()
    print(json.dumps({"checkpoints": checkpoints(),
                      "domains": [d.to_json() for d in DOMAINS]},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
