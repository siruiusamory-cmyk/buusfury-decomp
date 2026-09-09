"""TOOLKIT-022 representation and capacity planning, with ownership gates.

No engine termination rule is invented here. A packing request accounts for
pointer slots plus codec-serialized bodies, but is not an approved ROM layout.
The current graph explicitly refuses relocating placement runs. See
maps.py:_resolve_placements and entities.py:PlacementTypes.reference_document.
"""
from dataclasses import dataclass

from .allocation import AllocationRequest
from .layout import AnchorId, LayoutError
from .maps import MapIdentity, PlacementIdentity


@dataclass(frozen=True, slots=True)
class PlannedPlacement:
    identity: str
    provenance: str
    clone_from: str | None
    payload: bytes

    def to_json(self):
        return {"identity": self.identity, "provenance": self.provenance,
                "clone_from": self.clone_from, "serialized_size": len(self.payload)}


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
            records.append(PlannedPlacement(clone.identity, clone.provenance, clone.clone_from,
                                           clone.serialize(template)))
        runs.append(AuthoredRun(index, tuple(records), len(canonical),
                                canonical_slots=slots,
                                map_entry_offset=entry.file_offset,
                                canonical_engine_count=entry.record.trigger_count_raw))
    return tuple(runs)


def require_materialization_contract(runs, image=None):
    """Fail at the exact remaining ownership boundary, before allocation/writes.

    TOOLKIT-024 PROVED the outer traversal contract: the map loader at 0x08008C9E
    runs a counted loop over `MapEntry+0x04` (unsigned byte) indexing the pointer
    array at `MapEntry+0x14`; there is no sentinel and no suffix, so a run owns
    exactly `count * 4` array bytes. See BUU_PLACEMENT_RUN_RELOCATION.md.

    TOOLKIT-025 removed the count field from this gate. An authored expansion now
    derives its new `MapEntry+0x04` value from the validated object array and emits
    it as an attributed `ByteChange` (see `AuthoredRun.derive_count_change`), so the
    count is no longer the thing that cannot be expressed. `maps.MAP_FIELDS` still
    refuses every `*_count_raw` byte as directly editable - the derived path is
    reachable only through a validated AUTHOR_NEW expansion, never through a project
    supplying a raw count.

    What remains is the array's own relocation. A grown array no longer fits its
    canonical extent, so it must move, and the anchor that owns it is published
    `relocatable=False` by `entities.PlacementTypes.reference_document`. That is the
    next real boundary, and it is reported with the derived count change alongside
    it so the caller can see the count is settled and what now blocks.
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
    raise LayoutError(
        f"{run.identity.value}: valid authored placement content serialized; "
        f"proposed capacity request {run.allocation_request.size} bytes, alignment 4; "
        f"{detail}"
        f"materialization blocked by a non-relocatable object-array anchor: the array grows "
        f"from {len(run.canonical_slots)} to {run.target_slot_count} slots and cannot stay at "
        "its canonical extent, but the placement_reference_array anchor is published "
        "relocatable=False, so plan_relocation refuses it before any allocation is attempted."
    )
