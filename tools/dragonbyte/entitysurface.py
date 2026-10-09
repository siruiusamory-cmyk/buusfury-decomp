"""The Entities destination's model: placements, behaviours and object families.

The placement family is the one object family the SDK models, and nothing here
models a second one. What this module adds to `webfoot.maps` and
`webfoot.placement_events` is a *view*: for one open image plus the open project,
the placements a map owns, the behaviour each placement names, the script that
behaviour attaches where the verified contract decodes one, and the four
per-area object families the census records with one of them modelled.

**Nothing here re-implements an SDK codec.** The records, their positions, their
identities, their byte extents and their behaviour identities all come from the
modules that own them, and a placement is staged for editing by calling the same
`Maps.set_placement_position` the build calls. What this module adds is the two
things neither has:

* a *view* that answers for one open image plus the open project, so a row shows
  the position the project would build rather than the canonical one;
* a *change list*: the SDK's own `changes()`, staged from the project and
  filtered to the records that actually differ, which is where the owner-bearing
  `ByteChange` comes from. `ByteChange.owner` is the placement identity, which is
  what the manifest reports.

**Two rules this module obeys by construction.**

1. *No unproven relation appears.* A placement's only outgoing facts are the ones
   `webfoot.placement_events` publishes for it: its descriptor, and that
   descriptor's attached script where the verified contract decoded one. The
   trigger that invokes an attachment is not established for a canonical
   placement (`docs/research/AUTHORED_BEHAVIOR_EXECUTION.md` section 7) and no
   field here can carry one. A placement is never linked to the sprite it draws,
   and an enemy stat is never linked to a sprite: both are on the census's
   forbidden-edge list.
2. *An unmodelled family is visible and inert.* Three of the four per-area object
   families have no reader in this SDK, so they appear as sibling rows that carry
   their pointer slot and their stride and nothing else: no element type, no
   count, no record and no name, labelled `Family not modelled`.

No Qt is imported: a test drives every answer with no window open.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from tools.webfoot.binary import GBA_ROM_BASE, FileOffset
from tools.webfoot.formats import map_placements as mp
from tools.webfoot.layout import RomRange
from tools.webfoot.maps import (
    MapError,
    MapIdentity,
    Maps,
    PlacementIdentity,
    load_maps,
)
from tools.webfoot.placement_events import PlacementEvents
from tools.webfoot.profile import RomProfile, RomProfileCatalog
from tools.webfoot.rom import RomIdentification
from tools.webfoot.write import ByteChange

from . import coverage
from .datasurface import clone_maps

#: The three modes this destination carries, in mode order.
PLACEMENTS = "placements"
BEHAVIOURS = "behaviours"
FAMILIES = "families"
MODES: tuple[str, ...] = (PLACEMENTS, BEHAVIOURS, FAMILIES)

MODE_LABELS = {
    PLACEMENTS: "Placements",
    BEHAVIOURS: "Behaviours",
    FAMILIES: "Object families",
}

#: The two authored halfwords of a placement, in the order the SDK decodes them
#: (`webfoot.formats.map_placements.decode_position`). They are the only fields a
#: placement edit may change: its descriptor and child relations are read-only,
#: its flags and ids retain UNKNOWN semantics and type reassignment is unsupported.
POSITION_FIELDS: tuple[str, ...] = ("x", "y")
POSITION_RANGE: tuple[int, int] = (-0x8000, 0x7FFF)

#: The three unmodelled families are shown with this label and no other. The
#: product does not know what they are, so it does not name them.
NOT_MODELLED = "Family not modelled"

#: The four per-area object families, from the census row
#: `area-object-array-tables` (`docs/research/ROM_EDITOR_COVERAGE_LEDGER.md:211`):
#: one count byte and one array pointer per family, at +0x14, +0x18 and +0x1C
#: (stride 4) and +0x20 (stride 8). Only the +0x14 array has a reader in this SDK:
#: `webfoot.maps` enumerates the counted array the engine's own loop bound selects,
#: which TOOLKIT-024 proved against the engine's instructions. The census records
#: the four-array model itself as INFERRED and disputed (`:74`, `:224`), so a row
#: below shows the pointer slot and the stride and nothing else.
_FAMILY_SLOTS: tuple[tuple[str, int], ...] = (
    ("+0x14", 4),
    ("+0x18", 4),
    ("+0x1C", 4),
    ("+0x20", 8),
)

#: Census state -> the product's user word. The vocabulary is the coverage view's
#: own table, so the two surfaces cannot name one support state two ways.
_WORD = {state: word for state, word, _sentence in coverage.PRODUCT_STATE_WORDS}


class EntitySurfaceError(ValueError):
    """The open image's map records could not be read; the message says why."""


@dataclass(frozen=True, slots=True)
class MapChoice:
    """One entry of the map selector: an identity, a label and a count."""

    index: int
    label: str
    placements: int


@dataclass(frozen=True, slots=True)
class FamilyRow:
    """One per-area object family, as the census records it.

    `pointer_slot` and `stride` are the whole of what a row may state. `basis` is
    the census row this reading comes from, quoted rather than paraphrased.
    """

    label: str
    pointer_slot: str
    stride: int
    support: str
    modelled: bool
    note: str
    basis: str


@dataclass(frozen=True, slots=True)
class PlacementRow:
    """One placement record as the surface presents it."""

    identity: str
    label: str
    map_index: int
    placement_index: int
    #: This record's pointer index within the map's engine-owned object array. The
    #: array is heterogeneous, so it is not always the placement index.
    slot_index: int
    file_offset: int
    size: int
    address: int
    x: int
    y: int
    position_low: int
    position_high: int
    type_raw: int
    id_raw: int
    #: The descriptor this placement names, exactly as the SDK spells it.
    behaviour: str
    #: The script that descriptor attaches, or empty where none is decoded.
    attachment: str
    #: Why the behaviour columns read what they read. Never a guess.
    behaviour_note: str
    editable: bool
    note: str


@dataclass(frozen=True, slots=True)
class BehaviourRow:
    """One descriptor, as the evidence contract publishes it."""

    identity: str
    file_offset: int
    size: int
    #: The SDK's own name for the handler family this descriptor dispatches.
    handler: str
    handler_address: int
    attachment: str
    #: How many of the selected map's placements name this descriptor.
    placements: int
    note: str


@dataclass(frozen=True, slots=True)
class EntitySurface:
    """One open image's placement family, behaviours and object families."""

    identification: RomIdentification
    profile: RomProfile
    image: bytes
    maps: Maps
    #: The verified descriptor and attachment catalog, or None with a reason.
    events: PlacementEvents | None = None
    #: Why the behaviour columns are empty, when they are. Empty when they are not.
    behaviour_problem: str = ""

    # -- reading --------------------------------------------------------------

    def map_rows(self) -> tuple[MapChoice, ...]:
        """Every map record of this image, in table order, with its count."""
        counts: dict[int, int] = {}
        for placement in self.maps.placements():
            index = placement.identity.map_index
            counts[index] = counts.get(index, 0) + 1
        return tuple(
            MapChoice(
                index=entry.identity.index,
                label=f"Map {entry.identity.index:04d}",
                placements=counts.get(entry.identity.index, 0),
            )
            for entry in self.maps.entries()
        )

    def placements(self, map_index: int, project: Any | None) -> tuple[PlacementRow, ...]:
        """Every placement one map owns, in array order, as the project sees it."""
        authored = self._authored_placements(project, map_index)
        rows: list[PlacementRow] = []
        for entry in self.maps.map_placements(MapIdentity(map_index)):
            index = entry.identity.placement_index
            values = authored.get(index)
            if values is None:
                low = entry.record.position_low
                high = entry.record.position_high
                editable = False
                note = f"this project authors no placement record for {entry.identity}"
            else:
                low = int(values["position_low"])
                high = int(values["position_high"])
                editable = True
                note = ""
            x, y = mp.decode_position(low, high)
            behaviour, attachment, behaviour_note = self._behaviour_of(entry)
            rows.append(
                PlacementRow(
                    identity=str(entry.identity),
                    label=f"Placement {index:03d}",
                    map_index=map_index,
                    placement_index=index,
                    slot_index=entry.slot_index,
                    file_offset=entry.file_offset,
                    size=len(entry.original_bytes),
                    address=entry.file_offset + GBA_ROM_BASE,
                    x=x,
                    y=y,
                    position_low=low,
                    position_high=high,
                    type_raw=entry.record.type_raw,
                    id_raw=entry.record.id_raw,
                    behaviour=behaviour,
                    attachment=attachment,
                    behaviour_note=behaviour_note,
                    editable=editable,
                    note=note,
                )
            )
        return tuple(rows)

    def behaviours(self, map_index: int, project: Any | None) -> tuple[BehaviourRow, ...]:
        """Every descriptor the selected map's placements name.

        A descriptor is shared: it is identified by the first placement the
        evidence contract reaches it from, so two placements of one map may name
        one row here.
        """
        if self.events is None:
            return ()
        reached: dict[str, Any] = {}
        for entry in self.maps.map_placements(MapIdentity(map_index)):
            descriptor = self.events.descriptor_of(entry.identity)
            reached[descriptor.identity] = descriptor
        rows: list[BehaviourRow] = []
        ordered = sorted(
            reached.values(), key=lambda item: (item.file_offset, item.identity)
        )
        for descriptor in ordered:
            attachment, attachment_note = self._attachment(descriptor)
            note = (
                "a canonical descriptor is not editable here: the project "
                "attaches a behaviour by authoring a placement clone"
            )
            if attachment_note:
                note = f"{note}. {attachment_note}"
            prefix = f"map:{map_index:04d}/"
            rows.append(
                BehaviourRow(
                    identity=descriptor.identity,
                    file_offset=descriptor.file_offset,
                    size=len(descriptor.record.to_bytes()),
                    handler=mp.HANDLERS[descriptor.record.handler_pointer_raw],
                    handler_address=descriptor.record.handler_pointer_raw,
                    attachment=attachment,
                    placements=sum(
                        1 for name in descriptor.placements if name.startswith(prefix)
                    ),
                    note=note,
                )
            )
        return tuple(rows)

    # -- the unmodelled families ----------------------------------------------

    def families(self) -> tuple[FamilyRow, ...]:
        """The four per-area object families, one modelled and three not."""
        rows: list[FamilyRow] = []
        for position, (slot, stride) in enumerate(_FAMILY_SLOTS):
            modelled = position == 0
            rows.append(
                FamilyRow(
                    label=MODE_LABELS[PLACEMENTS] if modelled else NOT_MODELLED,
                    pointer_slot=slot,
                    stride=stride,
                    support=_WORD[
                        "PARTIALLY_EDITABLE" if modelled else "KNOWN_BUT_UNSUPPORTED"
                    ],
                    modelled=modelled,
                    note=(
                        "position is editable through the placement records; "
                        "everything else about the family stays fixed"
                        if modelled
                        else "no reader and no writer in this build: its element "
                        "type is not decoded, so this row reads and changes nothing"
                    ),
                    basis=(
                        "census area-object-array-tables; webfoot.maps enumerates "
                        "this counted array"
                        if modelled
                        else "census area-object-array-tables: the four-array model "
                        "is INFERRED and disputed, and the count byte base is an "
                        "open question"
                    ),
                )
            )
        return tuple(rows)

    # -- planning -------------------------------------------------------------

    def changes(self, project: Any | None) -> tuple[ByteChange, ...]:
        """Every pending placement edit, as the SDK's own owner-bearing changes."""
        if project is None:
            return ()
        staged = clone_maps(self.maps)
        touched: set[str] = set()
        for index, values in project.maps.items():
            for item in values.get("placements", ()):
                identity = PlacementIdentity(index, int(item["index"]))
                try:
                    current = self.maps.placement(identity).record
                except MapError:
                    continue
                low = int(item["position_low"])
                high = int(item["position_high"])
                if (current.position_low, current.position_high) == (low, high):
                    continue
                staged.set_placement_position(identity, low=low, high=high)
                touched.add(str(identity))
        if not touched:
            return ()
        return tuple(
            change
            for change in staged.changes()
            if change.owner in touched and change.old != change.new
        )

    def pending_bytes(self, project: Any | None) -> dict[int, bytes]:
        """The byte effect of every pending placement edit, keyed by file offset.

        This is what the ROM surface materializes as its current bytes, so a
        moved placement is visible there as a changed record rather than only as
        a claimed range. The bytes come from the SDK's own codec, not a second one.
        """
        return {change.offset: change.new for change in self.changes(project)}

    # -- the behaviours, told once --------------------------------------------

    def _behaviour_of(self, entry: Any) -> tuple[str, str, str]:
        """One placement's descriptor, its attachment and why they read so."""
        if self.events is None:
            return "", "", self.behaviour_problem
        descriptor = self.events.descriptor_of(entry.identity)
        attachment, note = self._attachment(descriptor)
        return descriptor.identity, attachment, note

    @staticmethod
    def _attachment(descriptor: Any) -> tuple[str, str]:
        """The script one descriptor attaches, and the reason when it attaches none."""
        if descriptor.event:
            return descriptor.event, ""
        if descriptor.record.handler_pointer_raw != mp.SCRIPT_DISPATCH_HANDLER:
            return "", (
                "its handler is not the script-dispatch handler, so it names no "
                "script in this image"
            )
        return "", (
            "it dispatches the script handler and the verified descriptor "
            "contract does not cover it, so no attachment is decoded for it"
        )

    @staticmethod
    def _authored_placements(project: Any | None, map_index: int) -> Mapping[int, Any]:
        if project is None:
            return {}
        values = project.maps.get(map_index)
        if not values:
            return {}
        return {int(item["index"]): item for item in values.get("placements", ())}


def family_summary(rows: tuple[FamilyRow, ...]) -> str:
    """The one line the family list states about itself."""
    modelled = sum(1 for row in rows if row.modelled)
    return f"Object families: {modelled} of {len(rows)} modelled"


def span(row: PlacementRow) -> RomRange:
    """The byte extent one placement row proves, as the ROM surface's own unit."""
    return RomRange(FileOffset(row.file_offset), row.size)


def with_position(payload: Any, row: PlacementRow, x: int, y: int) -> Any:
    """The authored data documents with one placement's position set.

    Returns a new payload and mutates nothing, so the journal's `before` snapshot
    stays the value the project actually held. Only the two authored halfwords
    change: the record's `raw` bytes stay exactly as the project holds them, which
    is what makes the build reconcile this placement rather than replace it.
    """
    low, high = mp.encode_position(x, y)
    values = payload.maps[row.map_index]
    edited = tuple(
        {**item, "position_low": low, "position_high": high}
        if int(item["index"]) == row.placement_index
        else item
        for item in values["placements"]
    )
    return replace(
        payload, maps={**payload.maps, row.map_index: {**values, "placements": edited}}
    )


def load_entity_surface(
    rom_path: str | Path,
    catalog: RomProfileCatalog,
    identification: RomIdentification,
    profile: RomProfile,
    image: bytes,
) -> EntitySurface:
    """Read a map's placements from an already-identified image, and its behaviours.

    The placement family has no from-image entry point in the SDK, so it is
    loaded through `webfoot.maps.load_maps`, which re-identifies the file. A
    profile whose verified descriptor contract is absent - the evidence covers
    Buu's Fury - still shows its placements: the behaviour columns state the
    contract's own refusal rather than the destination failing.
    """
    try:
        maps = load_maps(rom_path, catalog)
    except (ValueError, OSError) as exc:
        raise EntitySurfaceError(str(exc)) from exc
    if maps.profile.id != profile.id:
        raise EntitySurfaceError(
            f"the map records were read against profile {maps.profile.id!r}, not "
            f"the open image's {profile.id!r}"
        )

    events: PlacementEvents | None = None
    problem = ""
    try:
        events = PlacementEvents(maps)
    except (ValueError, OSError) as exc:
        problem = str(exc)

    return EntitySurface(
        identification=identification,
        profile=profile,
        image=image,
        maps=maps,
        events=events,
        behaviour_problem=problem,
    )
