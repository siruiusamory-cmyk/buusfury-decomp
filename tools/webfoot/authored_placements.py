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


@dataclass(frozen=True, slots=True)
class AuthoredRun:
    map_index: int
    records: tuple[PlannedPlacement, ...]
    canonical_count: int

    @property
    def identity(self):
        return AnchorId(f"map:{self.map_index:04d}/placement_references")

    @property
    def serialized_records(self):
        return b"".join(p.payload for p in self.records)

    @property
    def allocation_request(self):
        # A contiguous proposed replacement: target pointer slots + all bodies.
        # No guessed engine count/sentinel or suffix is added to this request.
        return AllocationRequest(self.identity, f"map:{self.map_index:04d}",
                                 4 * len(self.records) + len(self.serialized_records), 4)

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
        runs.append(AuthoredRun(index, tuple(records), len(canonical)))
    return tuple(runs)


def require_materialization_contract(runs):
    """Fail at the exact existing ownership boundary, before allocation/writes.

    All current placement graph anchors are non-relocatable, and no trusted
    declaration supplies an engine count/termination or suffix ownership rule.
    A free-region declaration alone cannot grant that missing authority.
    """
    if runs:
        run = runs[0]
        raise LayoutError(
            f"{run.identity.value}: valid authored placement content serialized; "
            f"proposed capacity request {run.allocation_request.size} bytes, alignment 4; "
            "materialization blocked by non-relocatable placement_reference_array: "
            "MapEntry+0x14 reference is CONFIRMED, but expanded-run engine count/termination "
            "and suffix ownership are UNKNOWN (MapEntry+0x05 is not a verified count). "
            "Verified capacity alone does not authorize this rewrite."
        )
