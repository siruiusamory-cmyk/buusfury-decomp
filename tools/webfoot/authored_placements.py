"""TOOLKIT-022 representation and capacity planning, with ownership gates.

No engine termination rule is invented here. A packing request accounts for
pointer slots plus codec-serialized bodies, but is not an approved ROM layout.
TOOLKIT-026: the graph now publishes the object-array anchor as relocatable
wherever its measured references satisfy the relocation safety contract, so the
remaining boundary is the authored record body, not the array. See
maps.py:_resolve_placements and entities.py:PlacementTypes.reference_document.
TOOLKIT-027: `authoring_overlay` gives that body a real anchor and the appended
array slot a real reference, so both move through the existing relocator.
"""
from dataclasses import dataclass, replace

from .allocation import AllocationRequest
from .formats.map_entry import MAP_ENTRY_SIZE
from .layout import AnchorId, LayoutError
from .maps import MapIdentity, PlacementIdentity


@dataclass(frozen=True, slots=True)
class PlannedPlacement:
    identity: str
    provenance: str
    clone_from: str | None
    payload: bytes
    #: TOOLKIT-030. The declared behavior identity, or None when the record simply
    #: inherits its template's descriptor. Keeping the inherited value alongside the
    #: effective one is what lets a build PROVE the attachment was authored rather
    #: than copied - the two differ exactly when project state chose the behavior.
    behavior: str | None = None
    inherited_descriptor_raw: int | None = None
    descriptor_pointer_raw: int | None = None

    @property
    def behavior_is_authored(self):
        """True when project state, not the clone source, decided this descriptor."""
        return (self.behavior is not None and
                self.descriptor_pointer_raw != self.inherited_descriptor_raw)

    def to_json(self):
        document = {"identity": self.identity, "provenance": self.provenance,
                    "clone_from": self.clone_from, "serialized_size": len(self.payload)}
        if self.behavior is not None:
            document.update(behavior=self.behavior,
                            inherited_descriptor=f"0x{self.inherited_descriptor_raw:08X}",
                            attached_descriptor=f"0x{self.descriptor_pointer_raw:08X}",
                            behavior_is_authored=self.behavior_is_authored)
        return document


class AuthoredBehaviorError(LayoutError):
    """A declared behavior cannot be resolved to a verified descriptor."""


def _resolve_behavior(clone, maps):
    """Resolve a declared behavior identity to its verified descriptor address.

    Resolution goes through `PlacementEvents`, the same read-only catalog that
    publishes descriptor identities, so a behavior can only ever name a descriptor
    this profile has actually verified. Nothing is fabricated and no address is
    accepted from project source; an unknown identity fails the build.
    """
    if clone.behavior is None:
        return None
    from .placement_events import PlacementEvents
    from .scripts import ScriptError
    owner = clone.behavior.rsplit("/", 1)[0]
    try:
        descriptor = PlacementEvents(maps).descriptor_of(owner)
    except ScriptError as exc:
        raise AuthoredBehaviorError(
            f"{clone.identity}: declared behavior {clone.behavior} names no verified "
            f"placement descriptor in this profile ({exc})") from None
    if descriptor.identity != clone.behavior:
        raise AuthoredBehaviorError(
            f"{clone.identity}: declared behavior {clone.behavior} resolved to "
            f"{descriptor.identity}; a behavior must name a descriptor by its own "
            "published identity, not by a sharing consumer")
    return 0x08000000 + descriptor.file_offset


#: `MapEntry+0x04` is read by the engine with `ldrb` (0x08008CA2, 0x08008CD2), so the
#: count is physically one unsigned byte and cannot express more than 255 slots.
COUNT_FIELD_OFFSET = 0x04
MAX_ENGINE_COUNT = 0xFF


class AuthoredCountError(LayoutError):
    """A derived count disagrees with the modelled array, or cannot be encoded."""


@dataclass(frozen=True, slots=True)
class AuthoredRun:
    map_index: int
    records: tuple[PlannedPlacement, ...]
    canonical_count: int
    #: Every canonical object slot in exact array order, placements and siblings
    #: alike. TOOLKIT-025: the engine array is heterogeneous, so a run that carried
    #: only placements would serialize a shorter array and silently drop sibling
    #: objects the engine still counts and dereferences.
    canonical_slots: tuple = ()
    #: File offset of this map's MapEntry record, so a derived count write can name
    #: the exact byte it changes.
    map_entry_offset: int | None = None
    #: The canonical `MapEntry+0x04` value, read from the record rather than inferred
    #: from how many slots this toolkit happened to model.
    canonical_engine_count: int | None = None

    @property
    def identity(self):
        return AnchorId(f"map:{self.map_index:04d}/placement_references")

    @property
    def serialized_records(self):
        return b"".join(p.payload for p in self.records)

    @property
    def authored_records(self):
        return tuple(p for p in self.records if p.provenance != "EXTRACTED")

    @property
    def target_slot_count(self):
        """Slots the authored array declares: every canonical slot, plus additions.

        Derived from the modelled array, never supplied by a project. Canonical
        slots are preserved whole - placements AND siblings - so an expansion can
        only ever append.
        """
        return len(self.canonical_slots) + len(self.authored_records)

    @property
    def allocation_request(self):
        # A contiguous proposed replacement: target pointer slots + all bodies.
        # No guessed engine count/sentinel or suffix is added to this request.
        # TOOLKIT-025: pointer slots are counted over the full heterogeneous array,
        # because the engine consumes `count * 4` bytes regardless of family.
        return AllocationRequest(self.identity, f"map:{self.map_index:04d}",
                                 4 * self.target_slot_count + len(self.serialized_records), 4)

    def derive_count_change(self, image):
        """The exact `MapEntry+0x04` byte change this authored expansion requires.

        Returns None when the authored array declares the canonical slot count, so a
        no-op project never emits a count write. The new value is DERIVED from the
        modelled array and is never accepted from a project: `MAP_FIELDS` still
        refuses every `*_count_raw` byte as directly editable, and this path is
        reachable only through a validated AUTHOR_NEW expansion.

        Fails closed rather than emitting a questionable byte:
          * the canonical count must match what the map actually declares, so a
            stale model cannot rewrite a field it mis-read;
          * canonical slots may only be appended to, never removed or reordered;
          * the derived count must fit the one byte the engine reads.
        """
        from .write import ByteChange
        if self.map_entry_offset is None or self.canonical_engine_count is None:
            raise AuthoredCountError(
                f"map:{self.map_index:04d}: authored expansion has no map-entry provenance; "
                "a count write must name the exact record it changes")
        offset = self.map_entry_offset + COUNT_FIELD_OFFSET
        actual = image[offset]
        if actual != self.canonical_engine_count:
            raise AuthoredCountError(
                f"map:{self.map_index:04d}: modelled canonical count "
                f"{self.canonical_engine_count} disagrees with MapEntry+0x04 = {actual} "
                "in the image being built; refusing to derive a count from a stale model")
        if len(self.canonical_slots) != self.canonical_engine_count:
            raise AuthoredCountError(
                f"map:{self.map_index:04d}: modelled {len(self.canonical_slots)} canonical "
                f"slots against an engine count of {self.canonical_engine_count}; the array "
                "model and the count field must agree exactly before either is rewritten")
        target = self.target_slot_count
        if target < self.canonical_engine_count:
            raise AuthoredCountError(
                f"map:{self.map_index:04d}: authored array declares {target} slots against "
                f"{self.canonical_engine_count} canonical; deleting a canonical object slot "
                "is not a supported authoring operation")
        if target > MAX_ENGINE_COUNT:
            raise AuthoredCountError(
                f"map:{self.map_index:04d}: authored array declares {target} slots, but "
                f"MapEntry+0x04 is one unsigned byte (max {MAX_ENGINE_COUNT}); the engine "
                "cannot count this array")
        if target == self.canonical_engine_count:
            return None
        return ByteChange(offset, bytes((actual,)), bytes((target,)),
                          f"map:{self.map_index:04d}/object_array_count",
                          "derived from authored object-array expansion")

    def record(self, identity):
        return next(p for p in self.records if p.identity == identity)

    def to_json(self):
        return {"owning_map": f"map:{self.map_index:04d}",
                "canonical_count": self.canonical_count, "target_count": len(self.records),
                "records": [p.to_json() for p in self.records],
                "serialized_record_bytes": len(self.serialized_records),
                "pointer_slot_bytes": 4 * len(self.records),
                "requested_allocation_bytes": self.allocation_request.size,
                "packing_status": "PROPOSED_NOT_APPROVED_ROM_LAYOUT",
                "allocated_file_offset": None, "rewritten_references": [],
                "materialization": "BLOCKED_OWNERSHIP_CONTRACT"}


def _canonical_slots(entry, image):
    """Every engine-counted object slot of one map, in exact array order.

    Reads the same two fields the engine reads - `MapEntry+0x04` for the count and
    `MapEntry+0x14` for the base - so the modelled array is the array the engine
    traverses, sibling-family objects included.
    """
    from .binary import BinaryAddressError, GbaRomAddress
    from .formats import map_placements as mp
    pointer = entry.record.scripts_pointer_raw
    count = entry.record.trigger_count_raw
    if not pointer or not count:
        return ()
    try:
        array_offset = GbaRomAddress(pointer).to_file_offset(len(image))
    except BinaryAddressError:
        return ()
    return mp.iter_object_slots(image, array_offset, count)


def prepare_authored_runs(project, maps):
    """Called only after base identity and exact canonical reconciliation.

    Extracted order is the verified run order, followed by authored ID order.
    Clone structure comes from canonical bytes, independent of source edits.
    """
    from .formats.map_placements import PlacementRecord
    from .project import ProjectValidationError
    from .project.placements import validate_templates
    validate_templates(project.maps)
    runs = []
    for index, values in sorted(project.maps.items()):
        additions = values.get("authored_placements", ())
        if not additions:
            continue
        if maps is None:
            raise ProjectValidationError("authored placements require verified maps")
        canonical = maps.map_placements(MapIdentity(index))
        if not canonical:
            raise ProjectValidationError(f"map:{index:04d}: authoring requires an existing owned placement run")
        #: TOOLKIT-025: the canonical array is heterogeneous, so the run carries EVERY
        #: engine-counted slot, not only the placement-family ones. Modelling
        #: placements alone would serialize a shorter array and silently drop the
        #: sibling objects the engine still counts and dereferences.
        entry = maps.entry(MapIdentity(index))
        slots = _canonical_slots(entry, maps.base_bytes)
        rows = {p["index"]: p for p in values.get("placements", ())}
        records = []
        for p in canonical:
            row = rows[p.identity.placement_index]
            raw = PlacementRecord.from_bytes(p.original_bytes)
            payload = raw.with_position(row["position_low"], row["position_high"]).to_bytes()
            records.append(PlannedPlacement(str(p.identity), "EXTRACTED", None, payload))
        for clone in sorted(additions, key=lambda p: p.identity):
            parts = clone.clone_from.split("/")
            source_id = PlacementIdentity(int(parts[0].split(":")[1]), int(parts[1].split(":")[1]))
            source = maps.placement(source_id)
            template = PlacementRecord.from_bytes(source.original_bytes)
            pointer = _resolve_behavior(clone, maps)
            records.append(PlannedPlacement(clone.identity, clone.provenance, clone.clone_from,
                                           clone.serialize(template, pointer),
                                           behavior=clone.behavior,
                                           inherited_descriptor_raw=template.descriptor_pointer_raw,
                                           descriptor_pointer_raw=pointer or template.descriptor_pointer_raw))
        runs.append(AuthoredRun(index, tuple(records), len(canonical),
                                canonical_slots=slots,
                                map_entry_offset=entry.file_offset,
                                canonical_engine_count=entry.record.trigger_count_raw))
    return tuple(runs)


#: TOOLKIT-027: the kind published for an authored record body. It is deliberately
#: NOT `placement`, because a canonical placement anchor describes bytes that exist
#: in the verified base and this one describes bytes the build is about to create.
#: Keeping the kinds distinct is what lets `RELOCATION_ELIGIBLE_KINDS` stay a
#: statement about measured canonical structure.
AUTHORED_BODY_KIND = "authored_placement_body"


class AuthoringOverlayError(LayoutError):
    """An authored overlay cannot be justified against the document it extends."""


def _authored_anchor_id(identity):
    """The stable semantic ID of an authored body anchor.

    It is the project's own authored identity - `map:NNNN/authored:<name>` - which
    `project.placements.AuthoredPlacement` already validates as a stable, map-scoped
    name that is neither a ROM offset nor an engine `id_raw`. Deriving the anchor ID
    from anything physical would make it move when the allocator moved the body.
    """
    return AnchorId(identity)


def authoring_overlay(document, run):
    """Describe one authored run's bodies and the array slots that will hold them.

    The relocator's contract is to move EXISTING anchors and rewrite EXISTING
    references; it creates neither. This is where they are created, and it is the
    smallest relationship that lets the appended slot point at something:

      * one anchor per authored record, holding exactly the bytes the production
        codec serialized (`PlannedPlacement.payload`), so no parallel body format
        exists anywhere in the toolkit;
      * one `ABSOLUTE_ROM_U32_LE` reference per authored record, sourced at the
        appended slot inside the EXPANDED array and targeting that body at delta 0 -
        the same encoding and the same `array_offset + 4 * slot_index` arithmetic
        `entities.reference_document` uses for canonical slots.

    Both are placed at their POST-relocation addresses, because that is the only
    image in which they decode: `RomDocument.validate` decodes every reference
    against the image it holds, and neither the appended slot nor the body exists in
    the verified base. So this returns a description to be materialized by
    `plan_authored_materialization`, which owns the ordering, rather than a document
    that would be invalid the moment it was built.

    The canonical slots are untouched. An authored record only ever appends, which
    `AuthoredRun.derive_count_change` independently refuses to violate.
    """
    array = document.anchor(run.identity)
    if array.range.size != 4 * len(run.canonical_slots):
        raise AuthoringOverlayError(
            f"{run.identity.value}: published array anchor is {array.range.size} bytes against "
            f"{len(run.canonical_slots)} modelled canonical slots; the overlay refuses to append "
            "to an array whose extent it cannot account for")
    if not array.relocatable:
        raise AuthoringOverlayError(
            f"{run.identity.value}: the array anchor is not relocatable, so the appended slot "
            "cannot be created; an authored body must not be published against a fixed array")
    provenance = array.provenance
    bodies = []
    for position, record in enumerate(run.authored_records):
        identity = _authored_anchor_id(record.identity)
        try:
            document.anchor(identity)
        except LayoutError:
            pass
        else:
            raise AuthoringOverlayError(
                f"{identity.value}: an anchor with this authored identity already exists")
        bodies.append(AuthoredBody(identity, record.payload,
                                   len(run.canonical_slots) + position, array.owner, provenance))
    return tuple(bodies)


@dataclass(frozen=True, slots=True)
class AuthoredBody:
    """One authored record body, its slot index, and the provenance it inherits."""

    identity: AnchorId
    payload: bytes
    slot_index: int
    owner: str
    provenance: object

    def to_json(self):
        return {"anchor": self.identity.value, "slot_index": self.slot_index,
                "body_size": len(self.payload), "owner": self.owner}


def _withhold(free_regions, taken):
    """The same declared free regions, minus spans already spoken for.

    Subtraction only. A region is split or trimmed around each taken span and is
    never grown, merged or moved, so this can only ever offer LESS capacity than the
    profile declared - it cannot manufacture space that was not already trusted.
    """
    from .layout import FreeRegion, RomRange
    from .binary import FileOffset
    result = []
    for region in free_regions:
        spans = [(region.range.start.value, region.range.end)]
        for span in taken:
            remaining = []
            for start, end in spans:
                if span.end <= start or span.start.value >= end:
                    remaining.append((start, end))
                    continue
                if start < span.start.value:
                    remaining.append((start, span.start.value))
                if span.end < end:
                    remaining.append((span.end, end))
            spans = remaining
        for start, end in spans:
            result.append(FreeRegion(RomRange(FileOffset(start), end - start), region.evidence))
    return tuple(result)


def plan_authored_materialization(document, run):
    """Allocate the expanded array AND one authored body, then wire the new slot.

    Uses production machinery end to end - `relocation.plan_relocation` for the
    array, `allocation.allocate` for the body, and the existing attributed write
    path for both - so nothing here is a second allocator or a second writer.

    Ordering is forced by what each step needs to know:

      1. allocate the authored body first, because the array payload has to CONTAIN
         its address before the array itself can be written;
      2. build the expanded array payload: every canonical slot pointer carried over
         byte-for-byte, then one appended pointer per authored body;
      3. hand that payload to `plan_relocation`, which moves the array, rewrites the
         `MapEntry+0x14` owner pointer, and validates the result.

    The body allocation reserves the array's own destination too, so the two can
    never be handed the same bytes. Both requests are deterministic: `allocate`
    sorts by anchor identity and takes the lowest aligned first fit.
    """
    from .allocation import allocate
    from .binary import FileOffset
    from .layout import Anchor, OwnedRegion, Reference, ReferenceClass, ReferenceEncoding
    from .relocation import RelocationRequest, plan_relocation
    from .write import ByteChange

    bodies = authoring_overlay(document, run)
    if not bodies:
        raise AuthoringOverlayError(f"{run.identity.value}: no authored records to materialize")
    array = document.anchor(run.identity)

    # Allocate the bodies FIRST, reserving everything the base already owns exactly
    # as `plan_relocation` computes it, so a body can never land on live content.
    occupied = [OwnedRegion(a.range, a.owner) for a in document.anchors]
    for ref in document.references:
        if not any(a.range.contains(ref.source) for a in document.anchors):
            occupied.append(OwnedRegion(ref.source_range, f"reference:{ref.target.value}"))
    placements = allocate(document.profile,
                          [AllocationRequest(b.identity, b.owner, len(b.payload), 4) for b in bodies],
                          occupied=occupied)
    allocations = {a.request.anchor: a for a in placements}

    # `plan_relocation` runs the allocator AGAIN, deriving its reserved set from the
    # document's anchors and profile alone. A body allocated only here would be
    # invisible to that call and the array would be handed the very same bytes - the
    # two allocations must be made to agree. A body anchor cannot do it: free space
    # is precisely where a body goes, and `RomDocument.from_bytes` refuses to call a
    # declared free region live content. So the agreement is expressed where it
    # actually belongs, in the capacity the array is offered: the bodies' spans are
    # withheld from the free regions handed to relocation. Nothing is invented - the
    # remaining regions are the same declarations, minus bytes now spoken for.
    staged = replace(document, profile=replace(document.profile,
        free_regions=_withhold(document.profile.free_regions,
                               tuple(allocations[b.identity].range for b in bodies))))

    # The expanded array: canonical pointers carried over verbatim, then the
    # authored bodies at their freshly allocated addresses.
    image = document.image
    payload = bytearray(image[array.range.start.value:array.range.end])
    if len(payload) != 4 * len(run.canonical_slots):
        raise AuthoringOverlayError(f"{run.identity.value}: canonical slot bytes are not intact")
    for body in bodies:
        destination = FileOffset(allocations[body.identity].range.start.value)
        payload += destination.to_gba_address(len(image)).raw.to_bytes(4, "little")

    result = plan_relocation(staged, [RelocationRequest(run.identity, bytes(payload))])
    moved = result.document.anchor(run.identity)
    if any(moved.range.overlaps(allocations[b.identity].range) for b in bodies):
        raise AuthoringOverlayError(
            f"{run.identity.value}: the expanded array was placed over an authored body")

    # The slot references are published onto the RELOCATED document, where the
    # appended slot now physically holds each body's address, so `validate` decodes
    # it rather than taking the reference on trust.
    anchors = list(result.document.anchors)
    references = list(result.document.references)
    changes = []
    for body in bodies:
        span = allocations[body.identity].range
        anchors.append(Anchor(body.identity, span, AUTHORED_BODY_KIND, body.owner, 4,
                              False, body.provenance))
        references.append(Reference(FileOffset(moved.range.start.value + 4 * body.slot_index),
                                    body.identity, 0, ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                                    ReferenceClass.DECLARED_REFERENCE, body.provenance))
        changes.append(ByteChange(span.start.value,
                                  result.document.image[span.start.value:span.end], body.payload,
                                  body.owner, f"authored placement body: {body.identity.value}"))
    every = (*allocations.values(), *result.allocations)
    return AuthoredMaterialization(run, result, tuple(bodies), tuple(anchors), tuple(references),
                                   tuple(changes),
                                   tuple(sorted(every, key=lambda a: a.request.anchor)))


@dataclass(frozen=True, slots=True)
class AuthoredMaterialization:
    """The planned array move plus the authored bodies that fill its new slots."""

    run: object
    relocation: object
    bodies: tuple
    anchors: tuple
    references: tuple
    body_changes: tuple
    allocations: tuple

    def slot_pointer(self, slot_index):
        """The raw GBA pointer word this plan writes into one expanded array slot."""
        array = self.relocation.document.anchor(self.run.identity)
        offset = array.range.start.value + 4 * slot_index
        return int.from_bytes(self.relocation.document.image[offset:offset + 4], "little")

    def to_json(self):
        return {"array_anchor": self.run.identity.value,
                "bodies": [b.to_json() for b in self.bodies],
                "allocations": [a.to_json() for a in self.allocations],
                "expanded_slot_count": self.run.target_slot_count}


def materialize_authored_runs(document, runs, image):
    """Every attributed byte change one or more authored runs require, in order.

    TOOLKIT-028: capacity is declared, so the plan `plan_authored_materialization`
    already produced against canonical Buu can be EMITTED rather than described and
    thrown away. This is the whole of that translation - it introduces no second
    allocator, writer or codec, and every change it returns was produced by the
    existing machinery:

      * the relocation's own effective changes (the expanded array's bytes at their
        allocated home, and the `MapEntry+0x14` owner pointer rewritten to it);
      * one body change per authored record, writing the production codec's bytes
        into the allocated body span;
      * the derived `MapEntry+0x04` count change, which `derive_count_change`
        independently re-validates against the image actually being built.

    The count and the owner pointer are two fields of ONE MapEntry record, so they
    are emitted as one change over that record rather than as two changes that would
    each claim bytes inside it. `Maps.changes` yields the record for exactly these
    maps, which is what keeps the record single-owner; `derive_count_change` still
    computes and validates the count byte, and its value is folded into that record
    rather than written separately.

    Runs are processed in map order so a multi-run build is deterministic. Each run
    is planned against the same verified base document, which is what `plan_relocation`
    requires; two runs competing for the same declared bytes therefore surface as an
    overlap error in the merged `plan_changes`, not as silent last-writer-wins.
    """
    from .write import ByteChange

    changes = []
    for run in sorted(runs, key=lambda r: r.map_index):
        plan = plan_authored_materialization(document, run)
        count = run.derive_count_change(image)

        entry_changes = []
        for change in plan.relocation.plan.effective_changes:
            if run.map_entry_offset is not None and (
                    change.offset < run.map_entry_offset + MAP_ENTRY_SIZE
                    and change.offset + len(change.new) > run.map_entry_offset):
                entry_changes.append(change)
            else:
                changes.append(change)
        changes.extend(plan.body_changes)

        # Fold every field this expansion derives - the relocated owner pointer and
        # the derived count - into one record-wide change, so the MapEntry has a
        # single writer instead of one per field.
        base = run.map_entry_offset
        if base is None:
            if entry_changes or count is not None:
                raise AuthoredCountError(
                    f"map:{run.map_index:04d}: authored expansion derives MapEntry fields "
                    "without map-entry provenance; refusing to write an unnamed record")
            continue
        old = image[base:base + MAP_ENTRY_SIZE]
        new = bytearray(old)
        for change in entry_changes:
            at = change.offset - base
            if at < 0 or at + len(change.new) > MAP_ENTRY_SIZE:
                raise AuthoredCountError(
                    f"map:{run.map_index:04d}: derived MapEntry change at "
                    f"0x{change.offset:06X} is not wholly inside the record")
            if bytes(new[at:at + len(change.old)]) != change.old:
                raise AuthoredCountError(
                    f"map:{run.map_index:04d}: derived MapEntry change at "
                    f"0x{change.offset:06X} does not match the image being built")
            new[at:at + len(change.new)] = change.new
        if count is not None:
            at = count.offset - base
            if bytes(new[at:at + 1]) != count.old:
                raise AuthoredCountError(
                    f"map:{run.map_index:04d}: derived count does not match the record "
                    "being built")
            new[at:at + 1] = count.new
        if bytes(new) != old:
            changes.append(ByteChange(
                base, old, bytes(new), f"map:{run.map_index:04d}",
                "authored object-array expansion: relocated owner pointer and derived count"))
    return changes


def require_materialization_contract(runs, image=None, document=None):
    """Fail at the exact remaining ownership boundary, before allocation/writes.

    TOOLKIT-024 PROVED the outer traversal contract: the map loader at 0x08008C9E
    runs a counted loop over `MapEntry+0x04` (unsigned byte) indexing the pointer
    array at `MapEntry+0x14`; there is no sentinel and no suffix, so a run owns
    exactly `count * 4` array bytes. See BUU_PLACEMENT_RUN_RELOCATION.md.

    TOOLKIT-025 removed the count field from this gate: an authored expansion
    derives its new `MapEntry+0x04` value from the validated object array and emits
    it as an attributed `ByteChange` (`AuthoredRun.derive_count_change`).

    TOOLKIT-026 removed the array anchor's relocatability from this gate. The
    `placement_reference_array` anchor is now published relocatable wherever its
    measured reference set satisfies the relocation safety contract
    (`layout.relocation_eligible`), and the map 10 array does: exactly one inbound
    CONFIRMED reference at `MapEntry+0x14`, no CANDIDATE reference anywhere in the
    graph, and both slot sources wholly inside the anchor. `plan_relocation` moves
    it and rewrites that owner pointer.

    TOOLKIT-027 removed the authored record body from this gate. The relocator still
    creates no anchors and no references - `authoring_overlay` does, publishing one
    anchor per authored body over exactly the production codec's bytes and one
    `ABSOLUTE_ROM_U32_LE` reference from the appended slot to it, both at their
    post-relocation addresses because that is the only image in which they decode.
    `plan_authored_materialization` then allocates the body and the expanded array
    together and fills the new slot with the body's real address.

    So this gate no longer asserts a boundary at all. It RUNS the materialization
    and reports whatever production actually refuses. Against canonical Buu that is
    capacity: the profile declares no free regions, so `allocate` raises
    `InsufficientSpaceError` and TOOLKIT-011 free-space work becomes binding.
    """
    if not runs:
        return ()
    changes = []
    for run in runs:
        if image is not None:
            change = run.derive_count_change(image)
            if change is not None:
                changes.append(change)
    run = runs[0]
    detail = ""
    if changes:
        c = changes[0]
        detail = (f"derived count write is AVAILABLE and validated "
                  f"(file 0x{c.offset:06X}: {c.old[0]} -> {c.new[0]}); ")
    array_state = "array anchor relocation eligibility is NOT ESTABLISHED for this document"
    if document is not None:
        from .layout import LayoutError as _LayoutError
        try:
            anchor = document.anchor(run.identity)
        except _LayoutError:
            anchor = None
        if anchor is not None and anchor.relocatable:
            array_state = ("array anchor IS relocatable and plan_relocation accepts it "
                           f"({len(run.canonical_slots)} -> {run.target_slot_count} slots)")
        elif anchor is not None:
            array_state = "array anchor is published relocatable=False for this document"
    bodies = ", ".join(p.identity for p in run.authored_records)
    reason = ("no reference document was supplied, so materialization was not attempted"
              if document is None else None)
    if document is not None:
        # Run the real thing. Whatever production refuses IS the blocker; nothing
        # here predicts it.
        try:
            plan_authored_materialization(document, run)
        except LayoutError as exc:
            reason = f"{type(exc).__name__}: {exc}"
        else:
            reason = None
    if reason is None:
        raise LayoutError(
            f"{run.identity.value}: authored materialization planned successfully but this "
            "build path does not yet emit it; no output was written")
    raise LayoutError(
        f"{run.identity.value}: valid authored placement content serialized; "
        f"proposed capacity request {run.allocation_request.size} bytes, alignment 4; "
        f"{detail}{array_state}; "
        f"authored record bodies are MODELLED ({bodies}) with an anchor and an "
        f"array-slot reference each; materialization blocked by {reason}"
    )
