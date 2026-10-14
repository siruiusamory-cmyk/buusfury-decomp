
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import appearances as ap
from .binary import FileOffset
from .capability import Capability, CapabilityError
from .capability import require as capability_require
from .allocation import (AllocationKind, AllocationRequest, Addressability,
                         allocate)
from .layout import (AnchorId, OwnedRegion, ReferenceClass, ReferenceEncoding,
                     RomRange)
from .write import ByteChange, ReferenceRewrite, RelocationProvenance

DOMAIN = "appearance_authoring"

TABLE_OWNER = "appearance_authoring:table"

ALIGNMENT = 4

# The lowest logical sprite id the engine's accessor resolves from the character registry, since ids below it are party-slot aliases and take a different path.
SPRITE_ID_FLOOR = 10

# The sprite id the engine remaps before its search compares anything, so no record bound to it is ever returned.
UNMATCHABLE_SPRITE_ID = 149


class AppearanceAuthoringError(ValueError):
    """A refusal from the authored-appearance domain, in this domain's terms."""


class AppearanceAuthoringProfileError(AppearanceAuthoringError, CapabilityError):
    """A profile that cannot back the authored-appearance domain."""


@dataclass(frozen=True, slots=True)
class AppearanceMaterialization:

    record_count: int
    table_range: RomRange
    table_address: int
    records: tuple[ap.AppearanceRecord, ...]
    changes: tuple[ByteChange, ...]
    reserved: tuple[OwnedRegion, ...]
    generated_allocations: tuple
    relocations: tuple[RelocationProvenance, ...]




def _require_declared(identification, profile, capability: Capability, subsystem: str):
    return capability_require(
        identification, capability, subsystem=subsystem,
        error_type=AppearanceAuthoringProfileError, check_header=True)


def _text_count(profile) -> int:
    layout = getattr(profile, "text_strings", None)
    if layout is None:
        raise AppearanceAuthoringError(
            f"profile {profile.id!r} declares no text table; an appearance "
            "definition's two text indices have nowhere to resolve"
        )
    return layout.count


def _sprite_ceiling(profile, authored_sprite_id: int | None) -> int:
    layout = getattr(profile, "actor_sprites", None)
    if layout is None:
        # The message names the profile when it can: a caller may hand this a
        # stand-in profile, and a refusal must not become an AttributeError.
        named = getattr(profile, "id", None) or getattr(profile, "profile_id", None) \
            or "this profile"
        raise AppearanceAuthoringError(
            f"profile {named!r} declares no actor_sprites; an appearance "
            "definition's sprite id has nowhere to resolve"
        )
    ceiling = SPRITE_ID_FLOOR + layout.character_count - 1
    if authored_sprite_id is not None:
        ceiling = max(ceiling, authored_sprite_id)
    return ceiling


# One statement of the count bound, so the two entry points cannot drift.
def _refuse_over_the_flag_ceiling(added, count) -> None:
    if count > ap.APPEARANCE_COUNT_FLAG_CEILING:
        raise AppearanceAuthoringError(
            f"{len(added)} new appearance definition(s) would raise the record count "
            f"to {count}, past {ap.APPEARANCE_COUNT_FLAG_CEILING}. The engine's seen-flag "
            "array is 232 bits and the word at block+0xE4 is the engine's, so a record "
            "beyond the first byte after the array has no established flag storage")


def authorable_sprite_ids(image: bytes, profile, *,
                          authored_sprite_id: int | None = None) -> tuple[int, ...]:
    """The sprite ids a new appearance definition may bind, ascending.
    Every id a canonical record selects is excluded, because binding one redirects
    an existing object's resolution rather than extending the table. That is the
    engine's two-loop search at `0x08027948`, measured:
    * loop 1, `0x08027960`-`0x0802799A`, returns the first record whose sprite
      matches AND whose `+0x0C` is negative, skipping every non-negative one;
    * loop 2, `0x0802799C`-`0x080279CE`, runs only when loop 1 found nothing, and
      when the second argument is zero it skips the stat test altogether
      (`0x080279A6`-`0x080279A8`) and returns the first record whose sprite matches
      whatever its sign.
    """
    ceiling = _sprite_ceiling(profile, authored_sprite_id)
    used = {record.sprite_id for record in ap.read_records(image, profile)}
    # 149 is offered by nothing and matched by nothing: the search replaces a
    # request for accessor(0x95) with accessor(0x92) at 0x0802794E before it
    # compares anything, and the two values differ (0x086AED8C and 0x086AEBF0),
    # so a record bound to 149 can never be returned.
    used.add(UNMATCHABLE_SPRITE_ID)
    ids = [sprite_id for sprite_id in range(SPRITE_ID_FLOOR, ceiling + 1)
           if sprite_id not in used]
    if authored_sprite_id is not None and authored_sprite_id not in ids:
        ids.append(authored_sprite_id)
        ids.sort()
    return tuple(ids)


def new_records(profile, definitions, *, authored_sprite_id: int | None = None,
                canonical=()) -> tuple[ap.AppearanceRecord, ...]:
    """The records the document asks for, each checked against the image's own
    The sprite-id rule is not cosmetic. The engine's search at 0x08027948 has two
    loops and the first one runs first, and what each returns depends on the
    caller's second argument:
    * with the second argument ZERO - the caller at 0x08010312 - loop 1 returns the
      first record whose sprite matches AND whose ``+0x0C`` is negative
      (``0x0802798E``-``0x08027992``); loop 2 runs only if loop 1 found nothing and
      skips the stat test entirely (``0x080279A6``-``0x080279A8``), returning the
      first record whose sprite matches whatever its sign. An appended record
      carries ``+0x0C = -1``, so it is returned by loop 1 before loop 2 is reached,
      and the lookup moves from the retail record to the authored one;
    * with the second argument SET - the caller at 0x0800FB72, which passes
      ``[actor+0x224]`` - both loops require ``+0x0C >= 0`` and a computed
      stat-record pointer to equal that argument (``0x08027978``-``0x08027988`` and
      ``0x080279AA``-``0x080279BA``), so an appended record is never returned on
      that path at all.
    """
    text_count = _text_count(profile)
    ceiling = _sprite_ceiling(profile, authored_sprite_id)
    used: dict[int, int] = {}
    negative_bound: set[int] = set()
    for position, record in enumerate(canonical):
        used.setdefault(record.sprite_id, position)
        if record.stat_index < 0:
            negative_bound.add(record.sprite_id)
    records = []
    for definition in definitions:
        index = definition.text_index
        if not 0 <= index < text_count:
            raise AppearanceAuthoringError(
                f"appearance {definition.name!r}: text index {index} is outside the "
                f"declared text table's 0..{text_count - 1}"
            )
        if index + 1 >= text_count:
            raise AppearanceAuthoringError(
                f"appearance {definition.name!r}: text index {index} has no successor "
                f"inside the declared text table, and the record's second index is "
                f"authored as its successor"
            )
        sprite_id = definition.sprite_id
        if not SPRITE_ID_FLOOR <= sprite_id <= ceiling:
            raise AppearanceAuthoringError(
                f"appearance {definition.name!r}: sprite id {sprite_id} is outside "
                f"the {SPRITE_ID_FLOOR}..{ceiling} range this image resolves"
            )
        if sprite_id == UNMATCHABLE_SPRITE_ID:
            raise AppearanceAuthoringError(
                f"appearance {definition.name!r}: sprite id "
                f"{UNMATCHABLE_SPRITE_ID} is remapped by the engine at "
                f"0x0802794E before the search compares anything, so a record "
                f"bound to it can never be returned"
            )
        if sprite_id in negative_bound:
            raise AppearanceAuthoringError(
                f"appearance {definition.name!r}: sprite id {sprite_id} is selected "
                f"by a canonical record whose stat index is negative, and the "
                f"engine's first search loop returns that record before any appended "
                f"one, so an authored record bound to this id can never be returned "
                f"even with the override set. Choose a sprite id no canonical record "
                f"selects."
            )
        if sprite_id in used and not getattr(definition, "override", False):
            raise AppearanceAuthoringError(
                f"appearance {definition.name!r}: sprite id {sprite_id} is already "
                f"selected by canonical record {used[sprite_id]}. An appended record "
                f"carries a negative stat index, so the engine's first search loop "
                f"returns it before its second loop can return the retail record, "
                f"which means binding this id redirects that object's resolution to "
                f"the authored appearance rather than extending the table. Set this "
                f"definition's override to true to take the binding over "
                f"deliberately, or choose a sprite id no canonical record selects."
            )
        records.append(ap.AppearanceRecord(
            text_index=index,
            description_index=index + 1,
            sprite_id=sprite_id,
            portrait_slot=ap.DEFAULT_PORTRAIT_SLOT,
            stat_index=ap.DEFAULT_STAT_INDEX,
        ))
    return tuple(records)




# Every check is a way the relocation contract could be false for this image, and each is a refusal rather than a workaround, because moving a table whose anchor is not published relocatable would strand whatever really reaches it.
def _table(image: bytes, profile):
    document = ap.reference_document(profile, image)
    anchor = document.anchor(AnchorId(ap.table_identity(profile)))
    expected_offset = ap.table_offset(profile, len(image))
    expected_size = ap.record_count(profile) * ap.APPEARANCE_RECORD_SIZE
    if anchor.kind != ap.APPEARANCE_TABLE_KIND:
        raise AppearanceAuthoringError(
            f"{ap.table_identity(profile)} is published as kind {anchor.kind!r}, not "
            f"a {ap.APPEARANCE_TABLE_KIND}")
    if (anchor.range.start.value != expected_offset
            or anchor.range.size != expected_size):
        raise AppearanceAuthoringError(
            f"{ap.table_identity(profile)} spans {anchor.range.to_json()}, but the "
            f"profile declares {ap.record_count(profile)} records at file "
            f"0x{expected_offset:06X}")
    if not anchor.relocatable:
        raise AppearanceAuthoringError(
            f"{ap.table_identity(profile)} is not published relocatable, so its "
            "inbound surface is not fully expressed by the reference graph and "
            "moving it would strand whatever reaches it")
    references = document.inbound(anchor.identity)
    if not references:
        raise AppearanceAuthoringError(
            f"{ap.table_identity(profile)} has no published inbound word, so a moved "
            "table would have no owner to rewrite")
    expected = anchor.range.start.to_gba_address(len(image)).raw.to_bytes(4, "little")
    for reference in references:
        if (reference.target != anchor.identity
                or reference.classification is not ReferenceClass.CONFIRMED_REFERENCE
                or reference.encoding is not ReferenceEncoding.ABSOLUTE_ROM_U32_LE
                or reference.target_delta != 0):
            raise AppearanceAuthoringError(
                f"the table's inbound word at 0x{reference.source.value:06X} is "
                f"{reference.classification.value} / {reference.encoding.value} with "
                f"delta {reference.target_delta}; only a confirmed, delta-free word "
                "addressing the table start can be repointed")
        source = reference.source.value
        if image[source:source + 4] != expected:
            raise AppearanceAuthoringError(
                f"the published reference at 0x{source:06X} does not hold the "
                "canonical table address, so this image is not the one the reference "
                "was published for")
    return document, anchor, references


def _occupied(document, reserved: tuple[OwnedRegion, ...]) -> tuple[OwnedRegion, ...]:
    occupied = [OwnedRegion(anchor.range, anchor.owner) for anchor in document.anchors]
    for reference in document.references:
        if not any(anchor.range.contains(reference.source)
                   for anchor in document.anchors):
            occupied.append(OwnedRegion(
                reference.source_range, f"reference:{reference.target.value}"))
    occupied.extend(reserved)
    return tuple(occupied)


def _expansion(profile):
    expansion = profile.generated_expansion
    if expansion is None:
        raise AppearanceAuthoringError(
            "a new appearance definition cannot be authored inside the canonical "
            "image - the record's own extent ends where a literal-named structure "
            "begins - and this profile declares no generated expansion to place the "
            "grown table in")
    return expansion


# The builder sizes one object as four bytes of index entries per record, then the display-list count, then eight bytes of display entries per record and a 0x28 tail, so a count raise that leaves the object canonical would let the builder write an index entry over the display-list count.
def _roster_changes(image: bytes, count: int) -> list[ByteChange]:
    if count > ap.ROSTER_SUPPORTED_COUNT:
        raise AppearanceAuthoringError(
            f"a {count}-record table needs roster storage for {count} entries and "
            f"this build relocates it for {ap.ROSTER_SUPPORTED_COUNT}; the index "
            f"array, the display list, the object's own allocation size and the two "
            f"tail bases would all have to grow again"
        )
    changes = []
    for site in ap.ROSTER_PATCH_SITES:
        try:
            site.check(image)
        except ap.AppearanceError as refused:
            raise AppearanceAuthoringError(str(refused)) from refused
        changes.append(ByteChange(
            site.offset,
            image[site.offset:site.offset + len(site.expected)],
            site.replacement,
            TABLE_OWNER,
            f"roster layout: the {site.role} restated for "
            f"{ap.ROSTER_SUPPORTED_COUNT} entries, so the builder's own object grows "
            f"with the table",
        ))
    return changes


# The count is code rather than a reference field, so it cannot be expressed as a relocation rewrite.
def _count_changes(image: bytes, count: int) -> list[ByteChange]:
    changes = []
    for offset in ap.APPEARANCE_COUNT_OFFSETS:
        old = image[offset:offset + ap.APPEARANCE_COUNT_OFFSET_WIDTH]
        if old != bytes([ap.APPEARANCE_CANONICAL_COUNT]):
            raise AppearanceAuthoringError(
                f"file 0x{offset:06X} is published as one of the appearance count "
                f"bounds, but its immediate is 0x{old.hex() or 'nothing'} rather "
                f"than the canonical 0x{ap.APPEARANCE_CANONICAL_COUNT:02X}")
        changes.append(ByteChange(
            offset, old, bytes([count]), TABLE_OWNER,
            f"appearance count bound: the loop at this halfword now admits "
            f"{count} records instead of {ap.APPEARANCE_CANONICAL_COUNT}"))
    return changes


def materialize_authored_appearances(
    image: bytes,
    identification,
    profile,
    appearances,
    *,
    authored_sprite_id: int | None = None,
    reserved: tuple[OwnedRegion, ...] = (),
) -> AppearanceMaterialization:
    """reserved is the build-scoped reservation set every allocating domain shares, the span this domain places is returned for the domains after it, and authored_sprite_id is the engine id an authored actor-sprite identity in the same project will take."""
    _require_declared(identification, profile, Capability.APPEARANCES,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.TEXT_STRINGS,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.ACTOR_SPRITES,
                      "authored appearance definitions")

    canonical = ap.read_records(image, profile)
    added = new_records(profile, appearances.ordered(),
                        authored_sprite_id=authored_sprite_id, canonical=canonical)
    count = ap.record_count(profile) + len(added)
    _refuse_over_the_flag_ceiling(added, count)
    if not added:
        raise AppearanceAuthoringError(
            "planning an appearance table needs at least one authored definition")

    document, anchor, references = _table(image, profile)
    expansion = _expansion(profile)
    size = count * ap.APPEARANCE_RECORD_SIZE
    request = AllocationRequest(
        AnchorId(TABLE_OWNER), TABLE_OWNER, size, ALIGNMENT,
        kind=AllocationKind.APPEARANCE_RECORD_TABLE,
        addressability=Addressability.EXPANDED_ONLY,
        evidence="the appearance-definition table, re-emitted whole with the "
                 "authored records appended",
    )
    allocation = allocate(profile, (request,),
                          occupied=_occupied(document, reserved))[0]
    table_at = allocation.range.start.value
    table_address = FileOffset(table_at).to_gba_address(expansion.output_size).raw

    block = ap.canonical_table(image, profile) + b"".join(
        record.encode() for record in added)
    changes = [ByteChange(
        table_at, bytes([expansion.padding_byte]) * size, block, TABLE_OWNER,
        f"the {count}-record appearance-definition table, moved above canonical EOF "
        f"with {len(added)} authored record(s) appended",
    )]
    rewrites = []
    for reference in references:
        source = reference.source.value
        changes.append(ByteChange(
            source, image[source:source + 4], table_address.to_bytes(4, "little"),
            TABLE_OWNER,
            "appearance table relocation: this word named the canonical table and now "
            f"names the {count}-record table",
        ))
        rewrites.append(ReferenceRewrite(
            reference=reference,
            new_source_file_offset=source,
            old_target_file_offset=document.target_offset(reference).value,
            new_target_file_offset=table_at,
        ))
    changes.extend(_count_changes(image, count))
    changes.extend(_roster_changes(image, count))

    generated = (allocation.generated_allocation_provenance(
        domain=DOMAIN, resource=TABLE_OWNER,
        pointer_offset=min(reference.source.value for reference in references),
        source_range=anchor.range),)
    relocations = (RelocationProvenance(
        anchor=anchor.identity.value,
        owner=TABLE_OWNER,
        old_range=anchor.range,
        new_range=RomRange(FileOffset(table_at), size),
        alignment=anchor.alignment,
        free_region_evidence=allocation.free_region_evidence,
        references=tuple(rewrites),
    ),)
    return AppearanceMaterialization(
        record_count=count,
        table_range=RomRange(FileOffset(table_at), size),
        table_address=table_address,
        records=canonical + added,
        changes=tuple(changes),
        reserved=(OwnedRegion(allocation.range, TABLE_OWNER),),
        generated_allocations=generated,
        relocations=relocations,
    )




def authored_appearances(project_dir: str | Path):
    """The project's authored definitions, or an empty document."""
    from .project.model import read_project

    return read_project(project_dir).appearances


def validate_authored_appearances(
    image: bytes,
    identification,
    profile,
    appearances,
    *,
    authored_sprite_id: int | None = None,
) -> None:
    """The field-level half of the plan, for a surface that must answer quickly."""
    _require_declared(identification, profile, Capability.APPEARANCES,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.TEXT_STRINGS,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.ACTOR_SPRITES,
                      "authored appearance definitions")
    canonical = ap.read_records(image, profile)
    added = new_records(profile, appearances.ordered(),
                        authored_sprite_id=authored_sprite_id, canonical=canonical)
    count = ap.record_count(profile) + len(added)
    _refuse_over_the_flag_ceiling(added, count)
    _table(image, profile)


def apply_authored_appearances(project_dir: str | Path, appearances) -> bool:
    """The one write path for the document, returning whether the project changed so a surface leaves the project revision alone on a no-op."""
    from .project.model import read_project, write_authored_appearances

    committed = read_project(project_dir).appearances
    if committed == appearances:
        return False
    write_authored_appearances(project_dir, appearances)
    return True
