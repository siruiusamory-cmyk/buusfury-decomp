"""Read-only, static placement/type relationships. Evidence: PLACEMENT_TYPES.md.

An engine selector is identity; the table address is provenance. The selected
record is shared with the existing enemy-stat subsystem where that subsystem's
verified extent covers it. There is no second editable copy of those records.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from . import capability
from .binary import FileOffset, GbaRomAddress
from .document import RomDocument
from .formats import stat_tables as st
from .layout import (Anchor, AnchorId, Provenance, Reference, ReferenceClass,
                     ReferenceEncoding, RomRange)
from .maps import MapIdentity, Maps, PlacementIdentity, load_maps


class PlacementTypeError(capability.CapabilityError):
    """Unverified profile, selector, family, or relationship."""


@dataclass(frozen=True, order=True)
class PlacementTypeIdentity:
    profile_id: str
    selector: int

    def __post_init__(self):
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise PlacementTypeError("type identity requires a profile")
        if type(self.selector) is not int or not 0 <= self.selector <= 0xFFFFFFFF:
            raise PlacementTypeError("type selector must be u32")

    def __str__(self):
        return f"{self.profile_id}/placement_type:{self.selector:04d}"


@dataclass(frozen=True)
class PlacementType:
    identity: PlacementTypeIdentity
    file_offset: int
    placements: tuple[PlacementIdentity, ...]
    enemy_identity: st.StatIdentity | None
    original_bytes: bytes | None

    @property
    def maps(self) -> tuple[MapIdentity, ...]:
        return tuple(MapIdentity(i) for i in sorted({p.map_index for p in self.placements}))

    @property
    def classification(self) -> str:
        return "CONFIRMED_ENEMY_STAT_LINK" if self.enemy_identity else "UNKNOWN_CATEGORY"

    def to_json(self) -> dict:
        return {"id": str(self.identity), "selector": self.identity.selector,
                "file_offset": self.file_offset, "reference_status": "CONFIRMED",
                "classification": self.classification,
                "enemy_id": str(self.enemy_identity) if self.enemy_identity else None,
                "record_codec": "enemy_stats" if self.original_bytes is not None else None,
                "maps": [str(m) for m in self.maps],
                "placements": [str(p) for p in self.placements]}


class PlacementTypes:
    def __init__(self, maps: Maps):
        self.profile = capability.require(maps.identification, capability.Capability.PLACEMENT_TYPES,
                                          subsystem="placement types", error_type=PlacementTypeError)
        self.maps = maps
        layout = self.profile.placement_types
        assert layout is not None
        self.layout = layout
        self.table_offset = layout.table_address.to_file_offset(len(maps.base_bytes))
        groups: dict[int, list[PlacementIdentity]] = {}
        for placement in maps.placements():
            record = placement.record
            if record.factory_raw != layout.factory_raw:
                raise PlacementTypeError("unsupported placement factory family")
            if not 0 <= record.type_raw <= layout.max_selector:
                raise PlacementTypeError("placement selector exceeds verified supported bound")
            groups.setdefault(record.type_raw, []).append(placement.identity)
        stats = self.profile.enemy_stats
        if stats is not None:
            capability.require(maps.identification, capability.Capability.ENEMY_STATS,
                               subsystem="placement enemy links", error_type=PlacementTypeError)
        types = []
        for selector, placements in sorted(groups.items()):
            offset = self.table_offset + selector * layout.stride
            RomRange(FileOffset(offset), 1).validate(len(maps.base_bytes))
            enemy = None
            raw = None
            if stats is not None:
                start = stats.address.to_file_offset(len(maps.base_bytes))
                relative = offset - start
                if (0 <= relative < stats.count * stats.record_size
                        and relative % stats.record_size == 0
                        and stats.record_size == st.ENEMY_RECORD_SIZE):
                    raw = maps.base_bytes[offset:offset + stats.record_size]
                    decoded = st.decode_enemy_record(raw, 0)
                    enemy = st.enemy_identity(decoded)
            types.append(PlacementType(PlacementTypeIdentity(self.profile.id, selector), offset,
                                       tuple(sorted(placements)), enemy, raw))
        self._types = {item.identity: item for item in types}
        self._placements = {p: item.identity for item in types for p in item.placements}

    def types(self) -> tuple[PlacementType, ...]:
        return tuple(self._types.values())

    def type(self, identity: PlacementTypeIdentity) -> PlacementType:
        try:
            return self._types[identity]
        except KeyError:
            raise PlacementTypeError(f"unknown supported placement type: {identity}") from None

    def type_of(self, placement: PlacementIdentity) -> PlacementType:
        try:
            return self.type(self._placements[placement])
        except KeyError:
            raise PlacementTypeError(f"unknown supported placement: {placement}") from None

    def placements_of_type(self, identity: PlacementTypeIdentity) -> tuple[PlacementIdentity, ...]:
        return self.type(identity).placements

    def factory_of(self, identity: PlacementTypeIdentity) -> dict:
        self.type(identity)
        return {"id": f"{self.profile.id}/placement_factory:0000",
                "raw_pointer": self.layout.factory_raw, "fetch_address": self.layout.factory_raw - 1,
                "constructor_id": f"{self.profile.id}/placement_constructor:0000",
                "constructor_fetch_address": self.layout.constructor_address.raw,
                "status": "CONFIRMED", "family": "indexed_stat_constructor",
                "per_type_factory_pointer": "NOT_PRESENT_IN_VERIFIED_LAYOUT"}

    def for_map(self, identity: MapIdentity) -> tuple[tuple[PlacementIdentity, PlacementTypeIdentity], ...]:
        return tuple((p.identity, self.type_of(p.identity).identity)
                     for p in self.maps.map_placements(identity))

    def summary(self) -> dict:
        entries = self.types()
        return {"placement_count": len(self._placements), "type_count": len(entries),
                "map_count": len({p.map_index for p in self._placements}),
                "enemy_linked_types": sum(t.enemy_identity is not None for t in entries),
                "enemy_linked_placements": sum(len(t.placements) for t in entries if t.enemy_identity),
                "placements_per_type_distribution": dict(sorted(Counter(len(t.placements) for t in entries).items())),
                "maps_per_type_distribution": dict(sorted(Counter(len(t.maps) for t in entries).items())),
                "factory_raw": self.layout.factory_raw,
                "factory_fetch": self.layout.factory_raw - 1,
                "constructor_fetch": self.layout.constructor_address.raw,
                "factory_count": 1, "reference_status": "CONFIRMED",
                "npc_friendly": "UNKNOWN", "item_pickup": "UNKNOWN",
                "script_event": "UNKNOWN", "graphics_resource": "UNKNOWN",
                "type_reassignment": "UNSUPPORTED"}

    def project_document(self) -> dict:
        """Optional v1 read-only catalog: links, never duplicate stat bytes.

        No physical addresses required for consumers; the profile resolves them.
        Unknown targets have identity but deliberately no invented record extent.
        """
        return {"placement_types": {
            str(t.identity): {"selector": t.identity.selector,
                              "factory_family": f"{self.profile.id}/placement_factory:0000",
                              "reference_status": "CONFIRMED",
                              "classification": t.classification,
                              "enemy_id": str(t.enemy_identity) if t.enemy_identity else "UNKNOWN",
                              "record_codec": "enemy_stats" if t.original_bytes is not None else "UNKNOWN"}
            for t in self.types()},
            "placements": {str(p): {"type_id": str(t)} for p, t in sorted(self._placements.items())}}

    def reference_document(self) -> RomDocument:
        """Use the common graph, including explicit read-only indexed references.

        A type's anchor is the existing enemy owner where verified. Unknown
        targets are one-byte entry anchors, NOT a claim of one-byte records.
        Code entry anchors preserve the raw Thumb state bit as target_delta=1.
        """
        image = self.maps.base_bytes
        provenance = Provenance(self.profile.id, self.profile.sha256, self.layout.evidence)
        anchors = []
        refs = []
        def anchor(key, offset, size, kind, owner=None, alignment=1):
            anchors.append(Anchor(AnchorId(key), RomRange(FileOffset(offset), size),
                                  kind, owner or key, alignment, False, provenance))
        def ref(source, target, encoding=ReferenceEncoding.ABSOLUTE_ROM_U32_LE, delta=0, **kwargs):
            refs.append(Reference(FileOffset(source), AnchorId(target), delta, encoding,
                                  ReferenceClass.CONFIRMED_REFERENCE, provenance, **kwargs))
        factory_id = f"{self.profile.id}/placement_factory:0000"
        factory_offset = FileOffset(GbaRomAddress(self.layout.factory_raw - 1).to_file_offset(len(image)))
        anchor(factory_id, factory_offset.value, 2, "thumb_entry", alignment=2)
        for item in self.types():
            anchor(str(item.identity), item.file_offset,
                   len(item.original_bytes) if item.original_bytes is not None else 1,
                   "enemy_stat_record" if item.enemy_identity else "type_target_entry",
                   str(item.enemy_identity) if item.enemy_identity else None, alignment=4)
        for entry in self.maps.entries():
            placements = self.maps.map_placements(entry.identity)
            if not placements:
                continue
            map_id = str(entry.identity)
            array_id = map_id + "/placement_references"
            array_offset = GbaRomAddress(entry.record.scripts_pointer_raw).to_file_offset(len(image))
            anchor(map_id, entry.file_offset, len(entry.original_bytes), "map_entry", alignment=4)
            #: TOOLKIT-025: the array the engine owns is `MapEntry+0x04` slots wide, not
            #: one slot per placement. Sibling-family objects share it, so sizing this
            #: anchor by placement count under-covers every heterogeneous array, and
            #: indexing references by `placement_index` writes a placement's pointer
            #: into a sibling's slot wherever the two interleave - which is exactly the
            #: target mismatch measured at map 17's slot 0x00072A38. Both now use the
            #: engine's own geometry: `trigger_count_raw` for the extent, and each
            #: record's measured `slot_index` for its position.
            anchor(array_id, array_offset, entry.record.trigger_count_raw * 4,
                   "placement_reference_array", alignment=4)
            ref(entry.file_offset + 0x14, array_id)
            for p in placements:
                key = str(p.identity)
                anchor(key, p.file_offset, len(p.original_bytes), "placement", alignment=4)
                ref(array_offset + p.slot_index * 4, key)
                ref(p.file_offset, factory_id, delta=1)
                ref(p.file_offset + 8, str(self.type_of(p.identity).identity),
                    ReferenceEncoding.INDEX_U32_LE, index_base=FileOffset(self.table_offset),
                    index_stride=self.layout.stride)
        document = RomDocument.from_bytes(image, self.profile, anchors=tuple(anchors), references=tuple(refs))
        from .data.placement_contracts import CONTRACTS
        if self.profile.id in CONTRACTS:
            from .placement_events import PlacementEvents
            document = PlacementEvents(self.maps).extend_references(document)
        return document


def load_placement_types(path, catalog) -> PlacementTypes:
    return PlacementTypes(load_maps(path, catalog))
