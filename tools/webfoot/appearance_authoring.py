"""The supported product path for a project's authored appearance definitions.

APPEARANCE-AUTHORING-GATE-001. `appearances/appearances.toml` is created,
replaced and removed here and nowhere else, and this module owns the plan that
turns one authored definition into engine bytes.

**Why the whole table moves.** The engine addresses record `i` as
`table + 16 * i` with no bound check, and the canonical extent ends exactly where
a literal-named descriptor block begins, so there is no room for a 233rd record
where the table is. The plan therefore re-emits the table in expanded storage
with the authored records appended, repoints the five literal-pool words that
name it and patches the three compiled count bounds. The canonical records are
copied verbatim rather than re-encoded, so every existing definition keeps its
own bytes.

**What this does not author.** `+0x08` (a portrait slot) and `+0x0C` (a stat
record index) stay at the two corpus-legal defaults this domain states, because
no shipped surface authors either target table and neither field is needed for
an identity to be reachable. `+0x02` is authored as `+0x00 + 1`, which holds on
232 of 232 canonical records; that is a data invariant of the corpus rather than
an engine rule, and it is stated as such in
`docs/research/APPEARANCE_TABLE_GROWTH.md`.
"""

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

#: This domain's name in every provenance record it writes.
DOMAIN = "appearance_authoring"

#: The semantic owner of every byte this plan writes.
TABLE_OWNER = "appearance_authoring:table"

#: The alignment the table's own record stride implies.
ALIGNMENT = 4

#: The lowest logical sprite id the engine's accessor resolves from the character
#: registry. Ids below it are party-slot aliases and take a different path.
SPRITE_ID_FLOOR = 10


class AppearanceAuthoringError(ValueError):
    """A refusal from the authored-appearance domain, in this domain's terms."""


class AppearanceAuthoringProfileError(AppearanceAuthoringError, CapabilityError):
    """A profile that cannot back the authored-appearance domain."""


@dataclass(frozen=True, slots=True)
class AppearanceMaterialization:
    """What the plan placed, and what the build may write."""

    record_count: int
    table_range: RomRange
    table_address: int
    records: tuple[ap.AppearanceRecord, ...]
    changes: tuple[ByteChange, ...]
    reserved: tuple[OwnedRegion, ...]
    generated_allocations: tuple
    relocations: tuple[RelocationProvenance, ...]


# --- the document's values, resolved against the image -----------------------


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
        raise AppearanceAuthoringError(
            f"profile {profile.id!r} declares no actor_sprites; an appearance "
            "definition's sprite id has nowhere to resolve"
        )
    ceiling = SPRITE_ID_FLOOR + layout.character_count - 1
    if authored_sprite_id is not None:
        ceiling = max(ceiling, authored_sprite_id)
    return ceiling


def new_records(profile, definitions, *, authored_sprite_id: int | None = None
                ) -> tuple[ap.AppearanceRecord, ...]:
    """The records the document asks for, each checked against the image's own
    sibling tables before anything is planned.

    The checks are the whole admissibility rule: a text pair that resolves inside
    the declared text table, and a sprite id the accessor resolves. A value
    outside either is refused rather than written and left for the engine to
    misread.
    """
    text_count = _text_count(profile)
    ceiling = _sprite_ceiling(profile, authored_sprite_id)
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
        records.append(ap.AppearanceRecord(
            text_index=index,
            description_index=index + 1,
            sprite_id=sprite_id,
            portrait_slot=ap.DEFAULT_PORTRAIT_SLOT,
            stat_index=ap.DEFAULT_STAT_INDEX,
        ))
    return tuple(records)


# --- the plan ----------------------------------------------------------------


def _table(image: bytes, profile):
    """The published anchor, its verified inbound words, and a refusal otherwise.

    Every check here is a way the relocation contract could be false for this
    image, and each is a refusal rather than a workaround: a table whose anchor is
    not published relocatable has an inbound surface the reference graph does not
    fully express, and moving it would strand whatever really reaches it.
    """
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
    """Everything the allocator must place clear of, in the established form."""
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


def _count_changes(image: bytes, count: int) -> list[ByteChange]:
    """The three compiled count bounds, patched or refused.

    The count is CODE rather than a reference field, so it cannot be expressed as
    a relocation rewrite. Each halfword is checked to hold the canonical count
    first, which is what makes the patch safe on an image that is not the one the
    census was taken from.
    """
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
    """Compile the project's new appearance definitions into attributed changes.

    ``reserved`` is the build-scoped reservation set every allocating domain
    shares; the span this domain places is returned for the domains after it.
    ``authored_sprite_id`` is the engine id an authored actor-sprite identity in
    the same project will take, when there is one, so an appearance may bind it.
    """
    _require_declared(identification, profile, Capability.APPEARANCES,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.TEXT_STRINGS,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.ACTOR_SPRITES,
                      "authored appearance definitions")

    canonical = ap.read_records(image, profile)
    added = new_records(profile, appearances.ordered(), 
                        authored_sprite_id=authored_sprite_id)
    count = ap.record_count(profile) + len(added)
    if count > ap.APPEARANCE_COUNT_CEILING:
        raise AppearanceAuthoringError(
            f"{len(added)} new appearance definition(s) would raise the record count "
            f"to {count}, past the {ap.APPEARANCE_COUNT_CEILING} a Thumb "
            "`cmp rN,#imm8` can state; the count bound would need code widening and "
            "this build refuses rather than write a bound the engine cannot obey")
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

    # The canonical bytes verbatim, then the authored records. Re-encoding the
    # canonical records would be a second implementation of the record layout that
    # could drift from the reader, and the requirement is that an untouched record
    # keeps its bytes.
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


# --- the project surface -----------------------------------------------------


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
    """The field-level half of the plan, for a surface that must answer quickly.

    Every refusal that precedes allocation runs here: the capability gates, the
    text-table and sprite-id admissibility of each definition, the count ceiling
    and the published reference census. A draft that returns from this has no
    field the build would refuse on sight. The allocation itself, and therefore
    the deterministic address, remains the build's.
    """
    _require_declared(identification, profile, Capability.APPEARANCES,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.TEXT_STRINGS,
                      "authored appearance definitions")
    _require_declared(identification, profile, Capability.ACTOR_SPRITES,
                      "authored appearance definitions")
    added = new_records(profile, appearances.ordered(),
                        authored_sprite_id=authored_sprite_id)
    count = ap.record_count(profile) + len(added)
    if count > ap.APPEARANCE_COUNT_CEILING:
        raise AppearanceAuthoringError(
            f"{len(added)} new appearance definition(s) would raise the record count "
            f"to {count}, past the {ap.APPEARANCE_COUNT_CEILING} a Thumb "
            "`cmp rN,#imm8` can state")
    _table(image, profile)


def apply_authored_appearances(project_dir: str | Path, appearances) -> bool:
    """Write the authored-appearance document, or remove it when it is empty.

    The ONE write path for this document. Returns whether the project changed, so a
    surface can leave the project revision and the build state alone on a no-op.
    """
    from .project.model import read_project, write_authored_appearances

    committed = read_project(project_dir).appearances
    if committed == appearances:
        return False
    write_authored_appearances(project_dir, appearances)
    return True
