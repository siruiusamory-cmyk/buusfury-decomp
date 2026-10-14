from dataclasses import dataclass, replace
import re

from .allocation import AllocationRequest
from .binary import GBA_ROM_BASE
from .formats.map_entry import MAP_ENTRY_SIZE
from .layout import AnchorId, LayoutError
from .maps import MapIdentity, PlacementIdentity
from .project.placements import BehaviorTrigger


@dataclass(frozen=True, slots=True)
class PlannedPlacement:
    identity: str
    provenance: str
    clone_from: str | None
    payload: bytes
    behavior: str | None = None
    inherited_descriptor_raw: int | None = None
    descriptor_pointer_raw: int | None = None
    script_body: bytes | None = None
    trigger: BehaviorTrigger | None = None

    @property
    def behavior_is_authored(self):
        """True when project state, not the clone source, decided this descriptor."""
        return (self.behavior is not None and
                self.descriptor_pointer_raw != self.inherited_descriptor_raw)

    @property
    def body_is_authored(self):
        return self.script_body is not None

    @property
    def behavior_identity(self):
        """The authored behavior's stable semantic ID: `<record>/behavior`."""
        return f"{self.identity}/behavior"

    @property
    def script_identity(self):
        """The authored script body's stable semantic ID: `<record>/behavior/script`."""
        return f"{self.identity}/behavior/script"

    def to_json(self):
        document = {"identity": self.identity, "provenance": self.provenance,
                    "clone_from": self.clone_from, "serialized_size": len(self.payload)}
        if self.behavior is not None:
            document.update(behavior=self.behavior,
                            inherited_descriptor=f"0x{self.inherited_descriptor_raw:08X}",
                            behavior_is_authored=self.behavior_is_authored)
            if self.body_is_authored:
                document.update(attached_descriptor="ALLOCATED_AT_BUILD",
                                authored_script_bytes=len(self.script_body),
                                body_is_authored=True)
            else:
                document["attached_descriptor"] = f"0x{self.descriptor_pointer_raw:08X}"
        if self.trigger is not None:
            document["trigger"] = self.trigger.value
        return document


class AuthoredBehaviorError(LayoutError):
    """A declared behavior cannot be resolved to a verified descriptor."""


class AuthoredTriggerError(LayoutError):
    """A trigger lacks the exact profile/type evidence required to name it."""


# on_defeat is proven only for one stable placement-type identity.
def _require_trigger_contract(clone, maps, source_id, placement_types=None):
    if clone.trigger is None:
        return placement_types
    from .data.behavior_triggers import BEHAVIOR_TRIGGER_CONTRACTS
    from .entities import PlacementTypes

    profile_contract = BEHAVIOR_TRIGGER_CONTRACTS.get(maps.profile.id)
    # The profile's declared identity is the authority; the contract's own hash
    # is a cross-check against it, so a contract entry that has drifted from the
    # catalog is refused rather than silently trusted.
    if (profile_contract is None or
            profile_contract.get("sha256") != maps.profile.sha256):
        raise AuthoredTriggerError(
            f"{clone.identity}: trigger {clone.trigger.value} has no evidence contract "
            f"for verified profile {maps.profile.id}")
    contract = profile_contract.get(clone.trigger.value)
    if contract is None:
        raise AuthoredTriggerError(
            f"{clone.identity}: trigger {clone.trigger.value} is unsupported for "
            f"verified profile {maps.profile.id}")
    placement_types = placement_types or PlacementTypes(maps)
    item = placement_types.type_of(source_id)
    if str(item.identity) != contract["placement_type"]:
        raise AuthoredTriggerError(
            f"{clone.identity}: trigger {clone.trigger.value} requires canonical "
            f"template type {contract['placement_type']}; {clone.clone_from} resolves "
            f"to {item.identity}")
    if (item.enemy_identity is None or item.original_bytes is None or
            item.classification != contract["required_classification"]):
        raise AuthoredTriggerError(
            f"{clone.identity}: trigger {clone.trigger.value} requires a canonical "
            "template with a CONFIRMED enemy-stat link")
    return placement_types


# No address is accepted from project source, so a behavior can only name a descriptor this profile has already verified.
def _resolve_behavior(clone, maps):
    if clone.behavior is None:
        return None
    if clone.authored_behavior:
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
    return GBA_ROM_BASE + descriptor.file_offset


def _expand_semantic_source(source, profile, identity):
    from .data.script_effects import SCRIPT_EFFECTS
    text_strings = profile.text_strings
    if text_strings is None:
        raise AuthoredBehaviorError(
            f"{identity}: profile {profile.id!r} declares no text table, so an "
            "authored text identity cannot be bounded")
    text_count = text_strings.count
    expanded = []
    effects = SCRIPT_EFFECTS.get(profile.id, {})
    for line in source:
        parts = line.split()
        effect = effects.get(parts[0]) if parts else None
        if effect is None:
            expanded.append(line)
            continue
        if parts[0] != 'show_centered_sprite_text' or len(parts) != 4:
            raise AuthoredBehaviorError(
                f"{identity}: show_centered_sprite_text requires text:NNNN, X and Y")
        match = re.fullmatch(r'text:([0-9]+)', parts[1])
        if match is None:
            raise AuthoredBehaviorError(
                f"{identity}: show_centered_sprite_text requires a text:NNNN identity")
        text_index = int(match.group(1), 10)
        try:
            x, y = (int(value, 0) for value in parts[2:])
        except ValueError:
            raise AuthoredBehaviorError(
                f"{identity}: show_centered_sprite_text coordinates must be integers") from None
        if not 0 <= text_index < text_count:
            raise AuthoredBehaviorError(
                f"{identity}: text identity is outside the profile's declared "
                f"0..{text_count - 1} text range")
        if not (0 <= x < 240 and 0 <= y < 160):
            raise AuthoredBehaviorError(
                f"{identity}: show_centered_sprite_text coordinates must be on screen")
        expanded.extend((
            f"push_many 3 {text_index} {x} {y}",
            f"{effect['native_opcode']} {effect['native_slot']}",
        ))
    return tuple(expanded)


# The opcode set is the profile's verified script contract, so an authored body can only be instructions the toolkit has decoded from canonical bytes.
def _assemble_script(clone, maps):
    from .data.placement_contracts import CONTRACTS
    from .data.script_specs import OPCODE_SETS
    from .formats.script_vm import ScriptError, assemble_source
    contract = CONTRACTS.get(maps.profile.id)
    # The profile's declared identity is the authority; the contract's own
    # `sha256` is compared against it, so a contract entry that has drifted from
    # the catalog for this profile is refused rather than silently trusted. It
    # is not the ROM check (identify_rom already did that) and it is not a
    # second authority: if the two ever disagree, the profile wins and this
    # refuses.
    if contract is None or contract['sha256'] != maps.profile.sha256:
        raise AuthoredBehaviorError(
            f"{clone.identity}: no verified script contract for this profile, so an "
            "authored behavior body cannot be encoded")
    spec = OPCODE_SETS[contract['encoding']]
    if maps.profile.id not in spec.profiles:
        raise AuthoredBehaviorError(
            f"{clone.identity}: the {spec.name} VM is not verified for this profile")
    source = _expand_semantic_source(clone.script, maps.profile, clone.identity)
    try:
        return assemble_source(source, spec)
    except ScriptError as exc:
        raise AuthoredBehaviorError(f"{clone.identity}: authored script body rejected: {exc}") from None


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
    canonical_slots: tuple = ()
    map_entry_offset: int | None = None
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
        """Slots the authored array declares, derived from the modelled array and never supplied by a project, so an expansion can only append."""
        return len(self.canonical_slots) + len(self.authored_records)

    @property
    def allocation_request(self):
        # No guessed engine count/sentinel or suffix is added to this request.
        # TOOLKIT-025: pointer slots are counted over the full heterogeneous array,
        # because the engine consumes `count * 4` bytes regardless of family.
        #
        # This is a PROPOSAL for sizing, and the production transaction does not
        # issue it: the build allocates the bodies and the array as two separate
        # calls, in that order, so the array can carry the bodies' finished
        # addresses. It is retained and pinned by test so it cannot quietly become
        # the sizing rule (BUU_VERIFIED_CAPACITY.md section 1).
        from .allocation import AllocationKind
        return AllocationRequest(self.identity, f"map:{self.map_index:04d}",
                                 4 * self.target_slot_count + len(self.serialized_records), 4,
                                 kind=AllocationKind.AUTHORED_MAP_EXPANSION,
                                 evidence="contiguous whole-map proposal; not issued by the "
                                          "production transaction")

    def derive_count_change(self, image):
        """The exact `MapEntry+0x04` byte change this authored expansion requires."""
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
    """Called only after base identity and exact canonical reconciliation."""
    from .formats.map_placements import PlacementRecord
    from .project import ProjectValidationError
    from .project.placements import validate_templates
    validate_templates(project.maps)
    runs = []
    placement_types = None
    for index, values in sorted(project.maps.items()):
        additions = values.get("authored_placements", ())
        if not additions:
            continue
        if maps is None:
            raise ProjectValidationError("authored placements require verified maps")
        canonical = maps.map_placements(MapIdentity(index))
        if not canonical:
            raise ProjectValidationError(f"map:{index:04d}: authoring requires an existing owned placement run")
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
            placement_types = _require_trigger_contract(
                clone, maps, source_id, placement_types)
            pointer = _resolve_behavior(clone, maps)
            script = _assemble_script(clone, maps) if clone.authored_behavior else None
            records.append(PlannedPlacement(clone.identity, clone.provenance, clone.clone_from,
                                           clone.serialize(template, pointer),
                                           behavior=clone.behavior,
                                           inherited_descriptor_raw=template.descriptor_pointer_raw,
                                           descriptor_pointer_raw=pointer or template.descriptor_pointer_raw,
                                           script_body=script,
                                           trigger=clone.trigger))
        runs.append(AuthoredRun(index, tuple(records), len(canonical),
                                canonical_slots=slots,
                                map_entry_offset=entry.file_offset,
                                canonical_engine_count=entry.record.trigger_count_raw))
    return tuple(runs)


# These kinds describe bytes the build is about to create, unlike the canonical kinds that describe bytes measured in the verified base.
AUTHORED_BODY_KIND = "authored_placement_body"

AUTHORED_DESCRIPTOR_KIND = "authored_placement_descriptor"
AUTHORED_SCRIPT_KIND = "authored_placement_script"

# PlacementRecord+0x14 holds the descriptor pointer and DescriptorRecord+0x04 the script pointer, the fields the engine reads, as offsets inside an authored body.
DESCRIPTOR_POINTER_OFFSET = 0x14
SCRIPT_POINTER_OFFSET = 0x04


class AuthoringOverlayError(LayoutError):
    """An authored overlay cannot be justified against the document it extends."""


def _authored_anchor_id(identity):
    return AnchorId(identity)


def authoring_overlay(document, run):
    """The created anchors and references hold post-relocation addresses, the only image in which the appended slot and the authored bodies decode."""
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

    def fresh(identity):
        try:
            document.anchor(identity)
        except LayoutError:
            return identity
        raise AuthoringOverlayError(
            f"{identity.value}: an anchor with this authored identity already exists")

    for position, record in enumerate(run.authored_records):
        identity = fresh(_authored_anchor_id(record.identity))
        bodies.append(AuthoredBody(identity, record.payload,
                                   len(run.canonical_slots) + position, array.owner, provenance,
                                   AUTHORED_BODY_KIND))
        if not record.body_is_authored:
            continue
        # TOOLKIT-032: the descriptor and its script are two more authored bodies,
        # created here for exactly the reason the record body is - the relocator
        # creates no anchors and no references, and neither structure exists in the
        # verified base at any address. Each is reached from a fixed 4-byte field
        # inside the body above it, which is the same edge the engine follows:
        from .formats.map_placements import DescriptorRecord, SCRIPT_DISPATCH_HANDLER
        descriptor = fresh(AnchorId(record.behavior_identity))
        script = fresh(AnchorId(record.script_identity))
        bodies.append(AuthoredBody(descriptor,
                                   DescriptorRecord(SCRIPT_DISPATCH_HANDLER, 0).to_bytes(),
                                   None, array.owner, provenance, AUTHORED_DESCRIPTOR_KIND,
                                   (identity, DESCRIPTOR_POINTER_OFFSET)))
        bodies.append(AuthoredBody(script, record.script_body, None, array.owner, provenance,
                                   AUTHORED_SCRIPT_KIND, (descriptor, SCRIPT_POINTER_OFFSET)))
    return tuple(bodies)


@dataclass(frozen=True, slots=True)
class AuthoredBody:
    """An authored body is reached either by an appended array slot or by a fixed field inside the body above it, and exactly one of slot_index and pointer_source is set."""

    identity: AnchorId
    payload: bytes
    slot_index: int | None
    owner: str
    provenance: object
    kind: str = None
    pointer_source: tuple | None = None

    def to_json(self):
        document = {"anchor": self.identity.value, "slot_index": self.slot_index,
                    "body_size": len(self.payload), "owner": self.owner}
        if self.pointer_source is not None:
            document["pointer_source"] = [self.pointer_source[0].value, self.pointer_source[1]]
        return document


def _bind_pointers(bodies, allocations, image_size):
    from .binary import FileOffset
    from .formats.map_placements import DescriptorRecord, PlacementRecord
    from dataclasses import replace as _replace

    payloads = {b.identity: b.payload for b in bodies}
    for body in bodies:
        if body.pointer_source is None:
            continue
        owner, offset = body.pointer_source
        if owner not in payloads:
            raise AuthoringOverlayError(
                f"{body.identity.value}: nothing authored owns the field that points at it")
        address = FileOffset(allocations[body.identity].range.start.value).to_gba_address(
            image_size).raw
        if offset == DESCRIPTOR_POINTER_OFFSET:
            record = PlacementRecord.from_bytes(payloads[owner])
            payloads[owner] = _replace(record, descriptor_pointer_raw=address).to_bytes()
        elif offset == SCRIPT_POINTER_OFFSET:
            record = DescriptorRecord.from_bytes(payloads[owner])
            payloads[owner] = _replace(record, payload_raw=address).to_bytes()
        else:
            raise AuthoringOverlayError(
                f"{body.identity.value}: no production codec owns a pointer field at "
                f"+0x{offset:02X}")
        if len(payloads[owner]) != len(next(b for b in bodies if b.identity == owner).payload):
            raise AuthoringOverlayError(
                f"{owner.value}: rewriting its pointer field changed its serialized size")
    return tuple(_replace(b, payload=payloads[b.identity]) for b in bodies)


def plan_authored_materialization(document, run, reserved=()):
    """reserved is the build-scoped set of spans earlier allocating domains already took, and it is empty when this domain allocates first."""
    from .allocation import AllocationKind, allocate, withhold
    from .binary import FileOffset
    from .layout import Anchor, OwnedRegion, Reference, ReferenceClass, ReferenceEncoding
    from .relocation import RelocationRequest, plan_relocation
    from .write import ByteChange

    reserved = tuple(reserved)
    if reserved:
        document = replace(document, profile=replace(document.profile,
            free_regions=withhold(document.profile.free_regions, reserved)))

    bodies = authoring_overlay(document, run)
    if not bodies:
        raise AuthoringOverlayError(f"{run.identity.value}: no authored records to materialize")
    array = document.anchor(run.identity)

    occupied = [OwnedRegion(a.range, a.owner) for a in document.anchors]
    for ref in document.references:
        if not any(a.range.contains(ref.source) for a in document.anchors):
            occupied.append(OwnedRegion(ref.source_range, f"reference:{ref.target.value}"))
    placements = allocate(document.profile,
                          [AllocationRequest(b.identity, b.owner, len(b.payload), 4,
                                             kind=AllocationKind.PLACEMENT_BODY,
                                             evidence="authored placement body")
                           for b in bodies],
                          occupied=occupied)
    allocations = {a.request.anchor: a for a in placements}

    # TOOLKIT-032: an authored body that POINTS AT another authored body cannot know
    # the address it must carry until the allocator has placed the target, so its
    # payload is finished here, once, and every later step sees only finished bytes.
    bodies = _bind_pointers(bodies, allocations, len(document.image))

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
        free_regions=withhold(document.profile.free_regions,
                              tuple(allocations[b.identity].range for b in bodies))))

    image = document.image
    payload = bytearray(image[array.range.start.value:array.range.end])
    if len(payload) != 4 * len(run.canonical_slots):
        raise AuthoringOverlayError(f"{run.identity.value}: canonical slot bytes are not intact")
    for body in bodies:
        # Only a record body occupies an object-array slot. A descriptor and a script
        # are reached from a field inside the body above them, never from the array,
        # so appending a slot for them would declare objects the engine would then
        # count and dereference as placements.
        if body.slot_index is None:
            continue
        destination = FileOffset(allocations[body.identity].range.start.value)
        payload += destination.to_gba_address(len(image)).raw.to_bytes(4, "little")

    result = plan_relocation(staged, [RelocationRequest(run.identity, bytes(payload))])
    moved = result.document.anchor(run.identity)
    if any(moved.range.overlaps(allocations[b.identity].range) for b in bodies):
        raise AuthoringOverlayError(
            f"{run.identity.value}: the expanded array was placed over an authored body")

    anchors = list(result.document.anchors)
    references = list(result.document.references)
    changes = []
    spans = {b.identity: allocations[b.identity].range for b in bodies}
    for body in bodies:
        span = spans[body.identity]
        anchors.append(Anchor(body.identity, span, body.kind, body.owner, 4,
                              False, body.provenance))
        if body.slot_index is not None:
            source = FileOffset(moved.range.start.value + 4 * body.slot_index)
        else:
            owner, offset = body.pointer_source
            source = FileOffset(spans[owner].start.value + offset)
        references.append(Reference(source, body.identity, 0,
                                    ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                                    ReferenceClass.DECLARED_REFERENCE, body.provenance))
        changes.append(ByteChange(span.start.value,
                                  result.document.image[span.start.value:span.end], body.payload,
                                  body.owner, f"authored placement body: {body.identity.value}"))
    # TOOLKIT-032: the record->descriptor and descriptor->script edges are SOURCED
    # inside authored bodies, whose bytes exist only in `changes` until they are
    # applied - so unlike the array slot, the relocated image cannot decode them and
    # publishing them against it would be publishing an edge on trust. Applying this
    # plan's own changes gives the one image in which every authored edge decodes,
    # and re-validating the whole graph there is what makes them measured rather
    # than declared. Uses the same production write path; it emits nothing.
    from hashlib import sha256
    from .write import apply_plan, plan_changes
    from .document import RomDocument
    relocated = result.document.image
    wired = apply_plan(relocated,
                       plan_changes(relocated, changes, profile_id=document.profile.id,
                                    base_sha256=sha256(relocated).hexdigest()))
    RomDocument(wired, document.profile, tuple(anchors), tuple(references),
                result.document.retired).validate()

    every = (*allocations.values(), *result.allocations)
    return AuthoredMaterialization(run, result, tuple(bodies), tuple(anchors), tuple(references),
                                   tuple(changes),
                                   tuple(sorted(every, key=lambda a: a.request.anchor)))


@dataclass(frozen=True, slots=True)
class AuthoredMaterialization:

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


def materialize_authored_runs(document, runs, image, reserved=()):
    """The relocated owner pointer and the derived count are emitted as one MapEntry-wide change rather than two changes claiming bytes inside that record."""
    from .write import ByteChange

    reserved = tuple(reserved)
    changes = []
    for run in sorted(runs, key=lambda r: r.map_index):
        plan = plan_authored_materialization(document, run, reserved)
        reserved += tuple(a.range for a in plan.allocations)
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
    return changes, reserved


def materialize_for_build(project, maps, document_factory, reserved=()):
    """Every authored byte change a build must emit, and the maps that yield to it."""
    authored_runs = prepare_authored_runs(project, maps)
    authored_changes = []
    reserved = tuple(reserved)
    authored_map_identities = frozenset(MapIdentity(run.map_index) for run in authored_runs)
    if authored_runs and maps is not None:
        document = document_factory(maps)
        if document is None:
            require_materialization_contract(authored_runs, maps.base_bytes, None)
        else:
            try:
                authored_changes, reserved = materialize_authored_runs(
                    document, authored_runs, maps.base_bytes, reserved)
            except LayoutError:
                # Re-raise through the gate so the blocker is reported with its full
                # measured context instead of a bare allocator or overlay error.
                require_materialization_contract(authored_runs, maps.base_bytes, document)
                raise
    elif authored_runs:
        require_materialization_contract(authored_runs, None, None)
    return authored_changes, authored_map_identities, reserved


@dataclass(frozen=True, slots=True)
class AuthoredPlacementPolicy:

    project: object
    map_view: object
    _legacy: bool
    _relationships_bound: bool
    _relationships: object

    def placement_problems(self, item, live_placement):
        """Validate domain-owned structure for one reconciled placement."""
        # This preserves the baseline path where relationships was bound only by the CONTRACTS branch and its later structural read raised UnboundLocalError.
        if self._relationships_bound:
            relationships = self._relationships
        if self._legacy:
            return []
        expected_structure = {
            'descriptor': relationships.descriptor_of(live_placement.identity).identity,
            'child_count': live_placement.record.child_count,
            'child_pointers_raw': list(live_placement.record.child_pointers_raw),
            'record_size': live_placement.record.consumed_length,
        }
        if any(item.get(k) != v for k, v in expected_structure.items()):
            return [f'{live_placement.identity}: structural placement fields differ from base']
        return []

    def final_problems(self):
        """Surface anything authored-run preparation refuses as a problem."""
        try:
            prepare_authored_runs(self.project, self.map_view)
        except (ValueError, KeyError) as exc:
            return [str(exc)]
        return []


def check_authored_placement_policy(project, maps):
    from .data.placement_contracts import CONTRACTS
    problems = []
    relationships = None
    relationships_bound = False
    structured = any('descriptor' in p for m in project.maps.values()
                     for p in m.get('placements', []))
    legacy = project.placement_events is None and not structured
    if maps is not None and maps.profile.id in CONTRACTS:
        from .placement_events import PlacementEvents
        from .entities import PlacementTypes
        relationships = PlacementEvents(maps)
        relationships_bound = True
        if not legacy:
            expected_events = relationships.project_document()
            expected_events['reference_graph'] = PlacementTypes(maps).reference_document().to_compact_json()
            if project.placement_events != expected_events:
                problems.append('placement descriptor/event catalog differs from verified base; editing unsupported')
        else:
            maps = maps.legacy_view()
    elif project.placement_events is not None or structured:
        problems.append('placement descriptor/event data requires verified profile support')
    if project.placement_types is not None:
        from .entities import PlacementTypes, PlacementTypeError
        import json
        if maps is None:
            problems.append("placement type catalog requires verified map/type support")
        else:
            try:
                expected = PlacementTypes(maps).project_document()
                if json.dumps(project.placement_types, sort_keys=True) != json.dumps(expected, sort_keys=True):
                    problems.append("placement type catalog differs from verified base; type reassignment is unsupported")
            except (PlacementTypeError, TypeError, ValueError) as exc:
                problems.append(f"invalid placement type catalog: {exc}")
    return problems, AuthoredPlacementPolicy(
        project, maps, legacy, relationships_bound, relationships)


def require_materialization_contract(runs, image=None, document=None):
    """Fail at the exact remaining ownership boundary, before allocation/writes.
    TOOLKIT-024 PROVED the outer traversal contract: the map loader at 0x08008C9E
    runs a counted loop over `MapEntry+0x04` (unsigned byte) indexing the pointer
    array at `MapEntry+0x14`; there is no sentinel and no suffix, so a run owns
    exactly `count * 4` array bytes. See BUU_PLACEMENT_RUN_RELOCATION.md.
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
