"""The supported product path for project-authored map identities.

MAP-NEW-AUTHORING-001. `maps/authored.toml` is created, replaced and removed
here and nowhere else, and this module owns the plan that turns one authored map
into engine bytes.

**Why the whole table moves.** The map table carries no count word and no
terminator: the engine's key lookup `0x080089FC` walks `base + 0x38 * i` for `i`
below a count it reads from the helper `0x080125E0`, and the byte immediately
after the table's last record is a live tileset container. A record past the
452nd therefore has nowhere to sit. The plan re-emits the table in expanded
storage - the canonical records copied verbatim, the authored rows appended -
repoints the one literal-pool word that names the table and raises the one
compiled bound. Canonical records keep their own bytes because they are copied
rather than re-encoded.

**Why the bound is safe to raise.** The helper is two instructions,
`movs r0,#0xff; adds r0,#0xc5`, so the count is `0xff + imm8` and the encodable
ceiling is 510 rows. A whole-image census finds exactly one caller of that
helper (inside the lookup) and exactly one word in the image naming the table
base, so the two sites below are the table's whole engine-side surface. Both are
re-checked against the supplied image before anything is written, which is what
makes the patch fail closed on an image the census was not taken from.

**What a new map inherits.** The engine's load template for a map is the root
that `MapEntry+0x2C` names, and the root carries four layer-slot pointers, the
declared extent, the selector stream, the bank table and the connection pair.
Fields whose semantics are unresolved are copied from a named donor rather than
invented - the same rule the shipped resize path applies to layer fields it
cannot name. Layers and chunks are shared with the donor, which the canonical
corpus already does: 1464 unique layer records sit behind 1808 references and
165 chunk bodies serve more than one cell, 160 of them across a map boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from .allocation import (AllocationKind, AllocationRequest, Addressability,
                         allocate)
from .binary import FileOffset
from .capability import Capability, CapabilityError
from .capability import require as capability_require
from .formats import map_entry as me
from .formats import map_graphics as mg
from .layout import (Anchor, AnchorId, OwnedRegion, Provenance, Reference,
                     ReferenceClass, ReferenceEncoding, RomRange,
                     relocation_eligible)
from .write import ByteChange, ReferenceRewrite, RelocationProvenance

#: This domain's name in every provenance record it writes.
DOMAIN = "map_authoring"

#: The semantic owner of the re-emitted map table.
TABLE_OWNER = "map_authoring:table"

#: The owner prefix of one authored map's root record.
ROOT_OWNER_PREFIX = "map_authoring:root"

#: The owner prefix of one authored map's layer record.
LAYER_OWNER_PREFIX = "map_authoring:layer"

#: The anchor kind this domain publishes. A measured, closed census of the
#: table's inbound words is what admits it to
#: `layout.RELOCATION_ELIGIBLE_KINDS`.
MAP_TABLE_KIND = "map_entry_table"

#: The file offset of the one word in the image that names the table base. It is
#: the literal pool entry of `ldr r1,[pc,#0x4c]` at `0x08008A0A` in the lookup.
BASE_POOL_FILE_OFFSET = 0x8A58

#: The file offset of the `adds r0,#0xc5` immediate in the count helper at
#: `0x080125E0`. The halfword there is `0x30C5`.
COUNT_IMMEDIATE_FILE_OFFSET = 0x125E2
COUNT_IMMEDIATE_CANONICAL = 0xC5
COUNT_IMMEDIATE_OPCODE = 0x30
COUNT_IMMEDIATE_BASE = 0xFF

#: The rows the count helper can express: `0xff + imm8`. An authored map beyond
#: this ceiling would need the helper's first instruction changed too.
MAX_SUPPORTED_ROWS = COUNT_IMMEDIATE_BASE + 0xFF

#: The engine's per-root load template is 0x50 bytes: the last field this domain
#: reads is the bank-table word at `+0x4C`.
ROOT_SIZE = 0x50

#: Every field this domain writes is a 4-byte or aligned word.
ALIGNMENT = 4

#: What every anchor and reference this domain publishes cites as its ground.
EVIDENCE = "MAP-NEW-AUTHORING-001; docs/research/MAP_NEW_AUTHORING.md"


class MapAuthoringError(ValueError):
    """A refusal from the authored-map domain, in this domain's own terms."""


class MapAuthoringProfileError(MapAuthoringError, CapabilityError):
    """A profile that cannot back the authored-map domain."""


@dataclass(frozen=True, slots=True)
class AuthoredMap:
    """One project-authored map identity, before anything is placed.

    ``donor`` is a canonical table index whose record, root, layers and chunks
    the new map inherits. ``key`` is the engine's own two-byte identity, the pair
    the lookup at `0x080089FC` compares and the pair a transition record carries
    at `+0x11`/`+0x12`.
    """

    name: str
    donor: int
    key: tuple[int, int]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise MapAuthoringError("an authored map needs a non-empty name")
        if type(self.donor) is not int or self.donor < 0:
            raise MapAuthoringError(
                f"authored map {self.name!r}: donor {self.donor!r} is not a table "
                "index"
            )
        if (not isinstance(self.key, tuple) or len(self.key) != 2
                or any(type(part) is not int or not 0 <= part <= 0xFF
                       for part in self.key)):
            raise MapAuthoringError(
                f"authored map {self.name!r}: key {self.key!r} is not a pair of "
                "bytes"
            )
        if self.key == (0, 0):
            raise MapAuthoringError(
                f"authored map {self.name!r}: a zero key is not a map identity; "
                "the canonical corpus uses 0x0001..0x1601"
            )


@dataclass(frozen=True, slots=True)
class MapPlacement:
    """Where one authored map's record, source word, root and layer went."""

    identity: str
    table_index: int
    key: tuple[int, int]
    donor: int
    record_file_offset: int
    source_file_offset: int
    root_file_offset: int
    root_address: int
    layer_file_offset: int | None
    layer_slot: int | None
    layer_address: int | None


@dataclass(frozen=True, slots=True)
class MapMaterialization:
    """What the plan placed, and what the build may write."""

    row_count: int
    canonical_rows: int
    table_range: RomRange
    table_address: int
    placements: tuple[MapPlacement, ...]
    changes: tuple[ByteChange, ...]
    reserved: tuple[RomRange, ...]
    generated_allocations: tuple
    relocations: tuple[RelocationProvenance, ...]


# --- the declared table ------------------------------------------------------


def table_identity(profile) -> str:
    """The published anchor identity of the MapEntry table."""
    return f"{profile.id}/map_entry_table:0000"


def declared(profile):
    """The profile's declaration of the table, or a refusal naming the profile."""
    layout = getattr(profile, "map_entries", None)
    if layout is None:
        raise MapAuthoringError(
            f"profile {profile.id!r} declares no map_entry table; the authored-map "
            "domain is unavailable for this ROM"
        )
    return layout


def table_offset(profile, image_size: int) -> int:
    return declared(profile).address.to_file_offset(image_size)


def record_count(profile) -> int:
    return declared(profile).count


def record_size(profile) -> int:
    size = declared(profile).record_size
    if size != me.MAP_ENTRY_SIZE:
        raise MapAuthoringError(
            f"profile {profile.id!r} declares a {size}-byte MapEntry record; this "
            f"codec reads {me.MAP_ENTRY_SIZE}-byte records"
        )
    return size


def read_records(image: bytes, profile) -> tuple[me.MapEntry, ...]:
    """Every record the profile declares, refusing a short or overrun table."""
    offset = table_offset(profile, len(image))
    stride = record_size(profile)
    span = record_count(profile) * stride
    if offset + span > len(image):
        raise MapAuthoringError(
            f"the declared MapEntry table runs past the image: "
            f"{record_count(profile)} records at file 0x{offset:06X} need {span} bytes"
        )
    return tuple(
        me.MapEntry.from_bytes(image[offset + index * stride:offset + (index + 1) * stride])
        for index in range(record_count(profile))
    )


def canonical_table(image: bytes, profile) -> bytes:
    """The table's canonical bytes, as the profile declares them."""
    offset = table_offset(profile, len(image))
    return bytes(image[offset:offset + record_count(profile) * record_size(profile)])


def canonical_key(record: me.MapEntry) -> tuple[int, int]:
    """The engine identity pair a record carries."""
    return (record.output_raw, record.zone_raw)


# --- the published reference graph -------------------------------------------


def reference_document(profile, image: bytes):
    """The table's anchor and its one verified inbound word.

    The word at `BASE_POOL_FILE_OFFSET` is `CONFIRMED_REFERENCE` because the
    consuming instruction was decoded and the pool word it loads was read, and
    the value is re-checked against this image here. A word that no longer holds
    the table address is a refusal rather than a repoint, because the constant is
    a census result for one image and not a guarantee about another.

    The anchor's `relocatable` flag is decided by the shared contract
    (`layout.relocation_eligible`), not asserted.
    """
    from .document import RomDocument

    layout = declared(profile)
    offset = table_offset(profile, len(image))
    span = layout.count * layout.record_size
    expected = layout.address.raw.to_bytes(4, "little")
    provenance = Provenance(profile.id, profile.sha256, EVIDENCE)

    if image[BASE_POOL_FILE_OFFSET:BASE_POOL_FILE_OFFSET + 4] != expected:
        raise MapAuthoringError(
            f"file 0x{BASE_POOL_FILE_OFFSET:06X} is published as the literal pool "
            f"word naming the MapEntry table at 0x{layout.address.raw:08X}, but the "
            "image holds something else there"
        )
    anchors = [Anchor(
        AnchorId(table_identity(profile)),
        RomRange(FileOffset(offset), span),
        MAP_TABLE_KIND,
        table_identity(profile),
        ALIGNMENT,
        False,
        provenance,
    )]
    references = [Reference(
        FileOffset(BASE_POOL_FILE_OFFSET),
        AnchorId(table_identity(profile)),
        0,
        ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
        ReferenceClass.CONFIRMED_REFERENCE,
        provenance,
    )]
    anchors = [replace(anchor, relocatable=relocation_eligible(anchor, references))
               for anchor in anchors]
    return RomDocument.from_bytes(image, profile,
                                  anchors=tuple(anchors),
                                  references=tuple(references))


def _occupied(document, reserved: tuple[RomRange, ...]) -> tuple[OwnedRegion, ...]:
    """Everything the allocator must place clear of, in the established form.

    ``reserved`` is the build-scoped set, which is stated in plain ``RomRange``
    spans by every allocating domain in this repository and wrapped here the way
    the dialogue domain wraps it. A caller that hands in an already-owned region
    is kept as it is rather than nested.
    """
    occupied = [OwnedRegion(anchor.range, anchor.owner) for anchor in document.anchors]
    for reference in document.references:
        if not any(anchor.range.contains(reference.source)
                   for anchor in document.anchors):
            occupied.append(OwnedRegion(
                reference.source_range, f"reference:{reference.target.value}"))
    for span in reserved:
        occupied.append(span if isinstance(span, OwnedRegion)
                        else OwnedRegion(span, "build reservation"))
    return tuple(occupied)


def _expansion(profile, what: str):
    expansion = profile.generated_expansion
    if expansion is None:
        raise MapAuthoringError(
            f"{what} cannot be authored inside the canonical image - the extent ends "
            "where a live tileset container begins - and this profile declares no "
            "generated expansion to place it in"
        )
    return expansion


# --- the new rows ------------------------------------------------------------


def _require_declared(identification, profile, subsystem: str):
    return capability_require(
        identification, Capability.MAP_ENTRIES, subsystem=subsystem,
        error_type=MapAuthoringProfileError, check_header=True)


@dataclass(frozen=True, slots=True)
class _Donor:
    """Everything one authored map inherits from its donor, read and checked."""

    record: me.MapEntry
    source_address: int
    root_address: int
    root_bytes: bytes
    layer_slot: int
    layer_address: int
    layer_bytes: bytes


def _donor_facts(image: bytes, profile, records, donor: int) -> _Donor:
    """The donor's record, root bytes, and the layer this domain re-emits."""
    if not 0 <= donor < len(records):
        raise MapAuthoringError(
            f"donor map index {donor} is outside the table's 0..{len(records) - 1}"
        )
    record = records[donor]
    source_word = record.variation_array_pointer_raw
    if not source_word:
        raise MapAuthoringError(
            f"map {donor} carries no +0x2C selector source, so it has no root to "
            "inherit"
        )
    reader = _WordReader(image, profile)
    root_address = reader.u32(source_word)
    root_bytes = reader.bytes_at(root_address, ROOT_SIZE)
    layer_slot = None
    for slot, offset in enumerate(mg.ROOT_LAYER_SLOTS):
        candidate = int.from_bytes(root_bytes[offset:offset + 4], "little")
        if candidate and candidate != mg.ABSENT_LAYER_RECORD:
            layer_slot = slot
            break
    if layer_slot is None:
        raise MapAuthoringError(
            f"map {donor} has no resolved layer: all four root slots are the shared "
            "absent placeholder, so a map inheriting it would draw nothing"
        )
    layer_offset = mg.ROOT_LAYER_SLOTS[layer_slot]
    layer_address = int.from_bytes(root_bytes[layer_offset:layer_offset + 4], "little")
    layer_at = layer_address - 0x08000000
    if not 0 <= layer_at < len(image):
        raise MapAuthoringError(
            f"map {donor}'s layer slot {layer_slot} names 0x{layer_address:08X}, "
            "which is outside the image"
        )
    columns = image[layer_at + mg.LAYER_CHUNK_X_OFFSET]
    rows = image[layer_at + mg.LAYER_CHUNK_Y_OFFSET]
    if not columns or not rows:
        raise MapAuthoringError(
            f"map {donor}'s layer at 0x{layer_address:08X} declares a "
            f"{columns}x{rows} chunk grid"
        )
    size = mg.LAYER_RECORD_HEADER_BYTES + 4 * columns * rows
    layer_bytes = reader.bytes_at(layer_address, size)
    return _Donor(record=record, source_address=source_word, root_address=root_address,
                  root_bytes=root_bytes, layer_slot=layer_slot,
                  layer_address=layer_address, layer_bytes=layer_bytes)


class _WordReader:
    """Absolute reads against one image, refusing anything outside it."""

    def __init__(self, image: bytes, profile) -> None:
        self._image = image
        self._profile = profile

    def _offset(self, address: int) -> int:
        offset = address - 0x08000000
        if not 0 <= offset < len(self._image):
            raise MapAuthoringError(
                f"0x{address:08X} is outside the {len(self._image)}-byte image this "
                "plan was given"
            )
        return offset

    def u32(self, address: int) -> int:
        offset = self._offset(address)
        if offset + 4 > len(self._image):
            raise MapAuthoringError(
                f"the word at 0x{address:08X} runs past the image"
            )
        return int.from_bytes(self._image[offset:offset + 4], "little")

    def bytes_at(self, address: int, size: int) -> bytes:
        offset = self._offset(address)
        if offset + size > len(self._image):
            raise MapAuthoringError(
                f"the {size} bytes at 0x{address:08X} run past the image"
            )
        return self._image[offset:offset + size]


# --- the checks that precede any placement -----------------------------------


def _validate(maps, records, canonical: bytes) -> None:
    """Every refusal a draft can hit before the allocator runs."""
    if not maps:
        raise MapAuthoringError(
            "planning a map table needs at least one authored map")
    names = set()
    keys = {canonical[index * me.MAP_ENTRY_SIZE:index * me.MAP_ENTRY_SIZE + 2]
            for index in range(len(records))}
    for authored in maps:
        if authored.name in names:
            raise MapAuthoringError(
                f"two authored maps are named {authored.name!r}")
        names.add(authored.name)
        if not 0 <= authored.donor < len(records):
            raise MapAuthoringError(
                f"authored map {authored.name!r}: donor map index "
                f"{authored.donor} is outside the table's 0..{len(records) - 1}"
            )
        pair = bytes(authored.key)
        if pair in keys:
            raise MapAuthoringError(
                f"authored map {authored.name!r}: key "
                f"0x{authored.key[0]:02X}{authored.key[1]:02X} is already used by a "
                "record in this image, and the lookup returns the first match"
            )
        keys.add(pair)


def _row_count_change(image: bytes, profile, rows: int) -> ByteChange:
    """The one compiled bound, patched or refused.

    The count is CODE rather than a reference field, so it cannot be expressed as
    a relocation rewrite. The halfword is checked to hold the canonical immediate
    first, which is what makes the patch fail closed on an image the census was
    not taken from.
    """
    offset = COUNT_IMMEDIATE_FILE_OFFSET
    old = image[offset:offset + 2]
    expected = bytes([COUNT_IMMEDIATE_CANONICAL, COUNT_IMMEDIATE_OPCODE])
    if old != expected:
        raise MapAuthoringError(
            f"file 0x{offset:06X} is published as the map count helper's "
            f"`adds r0,#0x{COUNT_IMMEDIATE_CANONICAL:02X}` immediate, but its bytes "
            f"are 0x{old.hex() or 'nothing'} rather than 0x{expected.hex()}"
        )
    immediate = rows - COUNT_IMMEDIATE_BASE
    if not 1 <= immediate <= 0xFF:
        raise MapAuthoringError(
            f"a {rows}-row table needs the helper's immediate to be 0x{immediate:X}, "
            f"which is outside the 1..0xFF an `adds` carries"
        )
    return ByteChange(
        offset, old, bytes([immediate, COUNT_IMMEDIATE_OPCODE]), TABLE_OWNER,
        f"map count bound: the lookup at 0x080089FC now walks {rows} rows instead "
        f"of {record_count(profile)}",
    )


# --- the plan ----------------------------------------------------------------


def materialize_authored_maps(
    image: bytes,
    identification,
    profile,
    maps,
    *,
    reserved: tuple[OwnedRegion, ...] = (),
) -> MapMaterialization:
    """Compile the project's authored maps into attributed changes.

    ``reserved`` is the build-scoped reservation set every allocating domain
    shares; the spans this domain places are returned for the domains after it.
    """
    _require_declared(identification, profile, "authored maps")
    canonical_rows = record_count(profile)
    stride = record_size(profile)
    canonical = canonical_table(image, profile)
    records = read_records(image, profile)
    _validate(maps, records, canonical)

    rows = canonical_rows + len(maps)
    if rows > MAX_SUPPORTED_ROWS:
        raise MapAuthoringError(
            f"{len(maps)} authored map(s) would raise the table to {rows} rows, past "
            f"{MAX_SUPPORTED_ROWS}. The count helper is `movs r0,#0xff; adds r0,#imm8`, "
            f"so at most {MAX_SUPPORTED_ROWS - canonical_rows} maps can be added "
            "without changing a second instruction"
        )

    document = reference_document(profile, image)
    anchor = document.anchor(AnchorId(table_identity(profile)))
    if not anchor.relocatable:
        raise MapAuthoringError(
            f"{table_identity(profile)} is not published relocatable, so its inbound "
            "surface is not fully expressed by the reference graph and moving it would "
            "strand whatever reaches it")
    references = tuple(document.inbound(anchor.identity))
    if not references:
        raise MapAuthoringError(
            f"{table_identity(profile)} has no published inbound word, so a moved table "
            "would have no owner to rewrite")
    expanded = _expansion(profile, "a new map")

    donors = [_donor_facts(image, profile, records, authored.donor)
              for authored in maps]

    requests = [AllocationRequest(
        AnchorId(TABLE_OWNER), TABLE_OWNER, rows * stride, ALIGNMENT,
        kind=AllocationKind.MAP_ENTRY_TABLE,
        addressability=Addressability.EXPANDED_ONLY,
        evidence="the MapEntry table, re-emitted whole with the authored rows "
                 "appended",
    )]
    for authored, donor in zip(maps, donors, strict=True):
        requests.append(AllocationRequest(
            AnchorId(f"{ROOT_OWNER_PREFIX}:{authored.name}"),
            f"{ROOT_OWNER_PREFIX}:{authored.name}",
            4 + ROOT_SIZE, ALIGNMENT,
            kind=AllocationKind.MAP_ROOT_RECORD,
            addressability=Addressability.EXPANDED_ONLY,
            evidence="the map root load template and the selector word `MapEntry+0x2C` "
                     "names, one indivisible object",
        ))
        requests.append(AllocationRequest(
            AnchorId(f"{LAYER_OWNER_PREFIX}:{authored.name}"),
            f"{LAYER_OWNER_PREFIX}:{authored.name}",
            len(donor.layer_bytes), ALIGNMENT,
            kind=AllocationKind.LAYER_RECORD,
            addressability=Addressability.EXPANDED_ONLY,
            evidence="the donor layer record re-emitted so the new root names its "
                     "own record",
        ))
    allocations = allocate(profile, tuple(requests),
                           occupied=_occupied(document, reserved))
    # `allocate` returns the batch sorted by anchor identity, not by request order,
    # so the spans are looked up by the owner that asked for them.
    by_owner = {allocation.request.anchor.value: allocation
                for allocation in allocations}

    table_allocation = by_owner[TABLE_OWNER]
    table_at = table_allocation.range.start.value
    table_address = FileOffset(table_at).to_gba_address(expanded.output_size).raw

    changes: list[ByteChange] = []
    generated: list = []
    rewrites: list[ReferenceRewrite] = []
    block = bytearray(canonical)
    placements: list[MapPlacement] = []

    for position, (authored, donor) in enumerate(zip(maps, donors, strict=True)):
        root_allocation = by_owner[f"{ROOT_OWNER_PREFIX}:{authored.name}"]
        layer_allocation = by_owner[f"{LAYER_OWNER_PREFIX}:{authored.name}"]
        root_at = root_allocation.range.start.value
        layer_at = layer_allocation.range.start.value
        source_at = root_at
        root_at += 4
        root_address = FileOffset(root_at).to_gba_address(expanded.output_size).raw
        layer_address = FileOffset(layer_at).to_gba_address(expanded.output_size).raw

        index = canonical_rows + position
        record_offset = index * stride
        source_address = FileOffset(source_at).to_gba_address(expanded.output_size).raw
        row = replace(
            donor.record,
            output_raw=authored.key[0],
            zone_raw=authored.key[1],
            variation_array_pointer_raw=source_address,
        ).to_bytes()
        block[record_offset:record_offset + stride] = row

        root = bytearray(donor.root_bytes)
        slot_offset = mg.ROOT_LAYER_SLOTS[donor.layer_slot]
        root[slot_offset:slot_offset + 4] = layer_address.to_bytes(4, "little")
        changes.append(ByteChange(
            source_at, bytes([expanded.padding_byte]) * (4 + ROOT_SIZE),
            root_address.to_bytes(4, "little") + bytes(root),
            f"{ROOT_OWNER_PREFIX}:{authored.name}",
            f"authored map {authored.name!r}: the selector word +0x2C names, holding "
            f"the donor {authored.donor}'s root with slot BG{donor.layer_slot} "
            "repointed at this map's own record",
        ))
        changes.append(ByteChange(
            layer_at, bytes([expanded.padding_byte]) * len(donor.layer_bytes),
            donor.layer_bytes,
            f"{LAYER_OWNER_PREFIX}:{authored.name}",
            f"authored map {authored.name!r}: a copy of donor {authored.donor}'s "
            f"BG{donor.layer_slot} layer record, named by no canonical root",
        ))
        generated.append(root_allocation.generated_allocation_provenance(
            domain=DOMAIN, resource=f"{ROOT_OWNER_PREFIX}:{authored.name}",
            pointer_offset=table_at + record_offset + 0x2C,
            source_range=RomRange(
                FileOffset(donor.source_address - 0x08000000), 4),
        ))
        generated.append(layer_allocation.generated_allocation_provenance(
            domain=DOMAIN, resource=f"{LAYER_OWNER_PREFIX}:{authored.name}",
            pointer_offset=root_at + slot_offset,
            source_range=RomRange(
                FileOffset(donor.layer_address - 0x08000000),
                len(donor.layer_bytes)),
        ))
        placements.append(MapPlacement(
            identity=f"map:{index:04d}",
            table_index=index,
            key=authored.key,
            donor=authored.donor,
            record_file_offset=table_at + record_offset,
            source_file_offset=source_at,
            root_file_offset=root_at,
            root_address=root_address,
            layer_file_offset=layer_at,
            layer_slot=donor.layer_slot,
            layer_address=layer_address,
        ))

    changes.insert(0, ByteChange(
        table_at, bytes([expanded.padding_byte]) * len(block), bytes(block),
        TABLE_OWNER,
        f"the {rows}-row MapEntry table, moved above canonical EOF with "
        f"{len(maps)} authored row(s) appended",
    ))
    for reference in references:
        source = reference.source.value
        changes.append(ByteChange(
            source, image[source:source + 4], table_address.to_bytes(4, "little"),
            TABLE_OWNER,
            "map table relocation: this word named the canonical table and now names "
            f"the {rows}-row table",
        ))
        rewrites.append(ReferenceRewrite(
            reference=reference,
            new_source_file_offset=source,
            old_target_file_offset=document.target_offset(reference).value,
            new_target_file_offset=table_at,
        ))
    changes.append(_row_count_change(image, profile, rows))

    generated.insert(0, table_allocation.generated_allocation_provenance(
        domain=DOMAIN, resource=TABLE_OWNER,
        pointer_offset=min(reference.source.value for reference in references),
        source_range=anchor.range,
    ))
    relocations = (RelocationProvenance(
        anchor=anchor.identity.value,
        owner=TABLE_OWNER,
        old_range=anchor.range,
        new_range=RomRange(FileOffset(table_at), rows * stride),
        alignment=anchor.alignment,
        free_region_evidence=table_allocation.free_region_evidence,
        references=tuple(rewrites),
    ),)
    return MapMaterialization(
        row_count=rows,
        canonical_rows=canonical_rows,
        table_range=RomRange(FileOffset(table_at), rows * stride),
        table_address=table_address,
        placements=tuple(placements),
        changes=tuple(changes),
        reserved=tuple(allocation.range for allocation in allocations),
        generated_allocations=tuple(generated),
        relocations=relocations,
    )


# --- the project surface -----------------------------------------------------


def authored_map_facts(image: bytes, profile, maps):
    """The rows this project adds, as the destination facts a corpus needs.

    MAP-NEW-AUTHORING-001. A created or retargeted transition names its
    destination by the engine's two-byte key, and the corpus resolves that key and
    the destination's walkable extent from the map table. An authored row is not
    in the canonical image yet, so both facts are stated here instead: the index
    the build will give it, its key, and its donor's two stored extent halfwords.
    """
    from .map_transitions import AuthoredMapFact

    ordered = tuple(maps.ordered()) if maps is not None else ()
    if not ordered:
        return ()
    records = read_records(image, profile)
    facts = []
    for position, authored in enumerate(ordered):
        donor = _donor_facts(image, profile, records, authored.donor)
        facts.append(AuthoredMapFact(
            index=record_count(profile) + position,
            key=bytes(authored.key),
            extent_x_raw=int.from_bytes(
                donor.root_bytes[mg.ROOT_EXTENT_X_OFFSET:
                                 mg.ROOT_EXTENT_X_OFFSET + 2], "little"),
            extent_y_raw=int.from_bytes(
                donor.root_bytes[mg.ROOT_EXTENT_Y_OFFSET:
                                 mg.ROOT_EXTENT_Y_OFFSET + 2], "little"),
        ))
    return tuple(facts)


def authored_maps(project_dir: str | Path):
    """The project's authored maps, or an empty document."""
    from .project.model import read_project

    return read_project(project_dir).authored_maps


def apply_authored_maps(project_dir: str | Path, authored) -> bool:
    """Write the authored-map document, or remove it when it is empty.

    The ONE write path for this document. Returns whether the project changed, so
    a surface can leave the project revision and the build state alone on a
    no-op.
    """
    from .project.model import read_project, write_authored_maps

    committed = read_project(project_dir).authored_maps
    if committed == authored:
        return False
    write_authored_maps(project_dir, authored)
    return True


def validate_authored_maps(image: bytes, identification, profile, authored) -> None:
    """The field-level half of the plan, for a surface that must answer quickly.

    Every refusal that precedes allocation runs here: the capability gate, the
    row ceiling, each donor's record and root, and the published reference
    census. A draft that returns from this has no field the build would refuse on
    sight. The allocation itself, and therefore the deterministic address, remains
    the build's.
    """
    _require_declared(identification, profile, "authored maps")
    maps = tuple(authored.ordered()) if authored is not None else ()
    if not maps:
        return
    records = read_records(image, profile)
    canonical = canonical_table(image, profile)
    _validate(maps, records, canonical)
    rows = record_count(profile) + len(maps)
    if rows > MAX_SUPPORTED_ROWS:
        raise MapAuthoringError(
            f"{len(maps)} authored map(s) would raise the table to {rows} rows, past "
            f"{MAX_SUPPORTED_ROWS}"
        )
    for authored_map in maps:
        _donor_facts(image, profile, records, authored_map.donor)
    document = reference_document(profile, image)
    anchor = document.anchor(AnchorId(table_identity(profile)))
    if not anchor.relocatable or not tuple(document.inbound(anchor.identity)):
        raise MapAuthoringError(
            f"{table_identity(profile)} is not published relocatable with an inbound "
            "word, so this image cannot host a moved table")
    _expansion(profile, "a new map")
    _row_count_change(image, profile, rows)
