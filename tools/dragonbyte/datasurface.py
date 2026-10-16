"""The Data destination's model: the three verified tables, read and staged.

Three tables, one shape. An enemy stat record, a character base-stat record and
a map-entry header record are all "a record with a stable identity, a byte
extent, and some named fields with a supported range", so this module presents
all three the same way and lets the page render one table.

**Nothing here re-implements an SDK codec.** The records, their field names and
their ranges come from the modules that own them - `webfoot.stats` and
`webfoot.maps` - and an edit is applied by calling the same setters the packaged
randomizer and the CLI call. What this module adds is the two things neither has:

* a *view* that answers for one open image plus the open project, so a record
  shows the value the project would build rather than the canonical one;
* a *change list*: the SDK's own `changes()`, staged from the project and
  filtered to the records that actually differ, which is where the owner-bearing
  `ByteChange` comes from. `ByteChange.owner` is the record identity, so
  "one stat edit produces one change owned by the record identity" is a
  property of the SDK this module passes through rather than states.

A field the project authors outside its supported range is skipped rather than
staged, and the record says so: the SDK would refuse it at build time, and a
surface that silently dropped it would be showing a value nothing will write.

No Qt is imported: a test drives every answer with no window open.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

from tools.webfoot import maps as maps_mod
from tools.webfoot import stats as stats_mod
from tools.webfoot.binary import GBA_ROM_BASE, FileOffset
from tools.webfoot.formats import stat_tables as st
from tools.webfoot.formats.map_entry import MAP_ENTRY_SIZE
from tools.webfoot.layout import RomRange
from tools.webfoot.maps import MapIdentity, Maps, load_maps
from tools.webfoot.profile import RomProfile, RomProfileCatalog
from tools.webfoot.rom import RomIdentification
from tools.webfoot.stats import StatTables, stat_tables_from_image
from tools.webfoot.write import ByteChange

#: The three record kinds this destination carries, in mode order.
ENEMY = "enemy"
CHARACTER = "character"
MAP_HEADER = "map-header"
KINDS: tuple[str, ...] = (ENEMY, CHARACTER, MAP_HEADER)

KIND_LABELS = {
    ENEMY: "Enemies",
    CHARACTER: "Characters",
    MAP_HEADER: "Map headers",
}


class DataSurfaceError(ValueError):
    """The open image's stat tables could not be read; the message says why."""


@dataclass(frozen=True, slots=True)
class FieldValue:
    """One editable field of one record, with the range the SDK supports."""

    name: str
    value: int
    minimum: int
    maximum: int | None

    @property
    def range_text(self) -> str:
        if self.maximum is None:
            return f"{self.minimum} or more"
        return f"{self.minimum}..{self.maximum}"


@dataclass(frozen=True, slots=True)
class RecordRow:
    """One record as the surface presents it: identity, extent, fields, state."""

    kind: str
    #: The SDK's own identity object: a `StatIdentity` or a `MapIdentity`.
    key: object
    #: The stable technical identity, exactly as the SDK spells it.
    identity: str
    label: str
    file_offset: int
    size: int
    address: int
    fields: tuple[FieldValue, ...]
    editable: bool
    note: str

    def field(self, name: str) -> FieldValue | None:
        return next((item for item in self.fields if item.name == name), None)


@dataclass(frozen=True, slots=True)
class DataSurface:
    """One open image's three tables, plus whichever project is open with them."""

    identification: RomIdentification
    profile: RomProfile
    image: bytes
    tables: StatTables
    maps: Maps | None = None
    #: Why the map-entry table is unavailable, when it is. Empty when it is.
    maps_problem: str = ""

    # -- reading --------------------------------------------------------------

    def rows(self, kind: str, project: Any | None) -> tuple[RecordRow, ...]:
        """Every record of one kind, in table order, as the project sees it."""
        if kind == ENEMY:
            return self._stat_rows(ENEMY, project)
        if kind == CHARACTER:
            return self._stat_rows(CHARACTER, project)
        if kind == MAP_HEADER:
            return self._map_rows(project)
        raise DataSurfaceError(f"{kind!r} is not a record kind this surface carries")

    def _stat_rows(self, kind: str, project: Any | None) -> tuple[RecordRow, ...]:
        authored = self._authored_stats(project, kind)
        ranges = stats_mod.ENEMY_FIELDS if kind == ENEMY else stats_mod.CHARACTER_FIELDS
        rows: list[RecordRow] = []
        for entry in (
            self.tables.enemies() if kind == ENEMY else self.tables.characters()
        ):
            values = authored.get(entry.identity)
            fields: list[FieldValue] = []
            for name, (minimum, maximum) in ranges.items():
                canonical = getattr(entry.record, name)
                value = canonical if values is None else int(values[name])
                fields.append(
                    FieldValue(
                        name=name,
                        value=value,
                        minimum=minimum,
                        maximum=maximum,
                    )
                )
            editable, note = self._stat_state(kind, entry.identity, values, ranges)
            rows.append(
                RecordRow(
                    kind=kind,
                    key=entry.identity,
                    identity=str(entry.identity),
                    label=self._stat_label(kind, entry),
                    file_offset=entry.location.file_offset,
                    size=(
                        st.ENEMY_RECORD_SIZE if kind == ENEMY else st.BASE_STAT_RECORD_SIZE
                    ),
                    address=entry.location.gba_address,
                    fields=tuple(fields),
                    editable=editable,
                    note=note,
                )
            )
        return tuple(rows)

    def _map_rows(self, project: Any | None) -> tuple[RecordRow, ...]:
        if self.maps is None:
            return ()
        authored = self._authored_maps(project)
        rows: list[RecordRow] = []
        for entry in self.maps.entries():
            values = authored.get(entry.identity.index)
            fields = tuple(
                FieldValue(
                    name=name,
                    value=(
                        self.maps.field(entry.identity, name)
                        if values is None
                        else int(values[name])
                    ),
                    minimum=bounds[0],
                    maximum=bounds[1],
                )
                for name, bounds in maps_mod.MAP_FIELDS.items()
            )
            editable, note = self._map_state(entry.identity, values)
            rows.append(
                RecordRow(
                    kind=MAP_HEADER,
                    key=entry.identity,
                    identity=str(entry.identity),
                    label=f"Map {entry.identity.index:04d}",
                    file_offset=entry.file_offset,
                    size=MAP_ENTRY_SIZE,
                    address=entry.file_offset + GBA_ROM_BASE,
                    fields=fields,
                    editable=editable,
                    note=note,
                )
            )
        return tuple(rows)

    def _stat_label(self, kind: str, entry: Any) -> str:
        if kind == ENEMY:
            return f"Enemy {entry.identity.key}"
        return f"Character {entry.identity.key} ({entry.alias})"

    def _stat_state(
        self,
        kind: str,
        identity: Any,
        values: Mapping[str, Any] | None,
        ranges: Mapping[str, tuple[int, int | None]],
    ) -> tuple[bool, str]:
        if values is None:
            return False, f"this project authors no {kind} record for {identity}"
        for name, (minimum, maximum) in ranges.items():
            value = values[name]
            if value < minimum or (maximum is not None and value > maximum):
                return False, (
                    f"the authored {name} value {value} is outside the supported "
                    f"range {minimum}..{maximum}"
                )
        return True, ""

    def _map_state(
        self, identity: MapIdentity, values: Mapping[str, Any] | None
    ) -> tuple[bool, str]:
        if self.maps is None:
            return False, self.maps_problem or "the map-entry table could not be read"
        if values is None:
            return False, f"this project authors no map record for {identity}"
        for name, (minimum, maximum) in maps_mod.MAP_FIELDS.items():
            value = values[name]
            if not minimum <= value <= maximum:
                return False, (
                    f"the authored {name} value {value} is outside the supported "
                    f"range {minimum}..{maximum}"
                )
        return True, ""

    # -- planning -------------------------------------------------------------

    def changes(self, project: Any | None) -> tuple[ByteChange, ...]:
        """Every pending data edit, as the SDK's own owner-bearing changes.

        The changes that differ from the image, and nothing else: the SDK's
        `changes()` encodes every record so that round-trip is proved, and a
        surface that reported the no-ops as changes would be reporting the whole
        table as edited.
        """
        if project is None:
            return ()
        return self._stat_changes(project) + self._map_changes(project)

    def pending_bytes(self, project: Any | None) -> dict[int, bytes]:
        """The byte effect of every pending data edit, keyed by file offset.

        This is what the ROM surface materializes as its current bytes, so a
        stat edit is visible there as a changed value rather than only as a
        claimed range. The bytes come from the SDK's own encoder, not from a
        second one here.
        """
        return {change.offset: change.new for change in self.changes(project)}

    def _stat_changes(self, project: Any) -> tuple[ByteChange, ...]:
        staged = stat_tables_from_image(self.identification, self.profile, self.image)
        touched: set[str] = set()
        for identity, values in project.enemies.items():
            if self._stage_stat(stats_mod.ENEMY_FIELDS, staged.set_enemy_field,
                                self.tables.enemy, identity, values):
                touched.add(str(identity))
        for identity, values in project.characters.items():
            if self._stage_stat(stats_mod.CHARACTER_FIELDS, staged.set_character_field,
                                self.tables.character, identity, values):
                touched.add(str(identity))
        if not touched:
            return ()
        return tuple(
            change
            for change in staged.changes()
            if change.owner in touched and change.old != change.new
        )

    def _stage_stat(
        self,
        ranges: Mapping[str, tuple[int, int | None]],
        setter: Any,
        lookup: Any,
        identity: Any,
        values: Mapping[str, Any],
    ) -> bool:
        """Stage one record's authored values, and say whether any differed."""
        try:
            entry = lookup(identity)
        except stats_mod.UnknownRecordError:
            return False
        staged = False
        for name, (minimum, maximum) in ranges.items():
            value = values[name]
            if value == getattr(entry.record, name):
                continue
            if value < minimum or (maximum is not None and value > maximum):
                continue
            setter(identity, name, value)
            staged = True
        return staged

    def _map_changes(self, project: Any) -> tuple[ByteChange, ...]:
        if self.maps is None:
            return ()
        staged = clone_maps(self.maps)
        touched: set[str] = set()
        for index, values in project.maps.items():
            identity = MapIdentity(index)
            try:
                self.maps.entry(identity)
            except maps_mod.MapError:
                continue
            for name, (minimum, maximum) in maps_mod.MAP_FIELDS.items():
                value = values[name]
                if value == self.maps.field(identity, name):
                    continue
                if not minimum <= value <= maximum:
                    continue
                staged.set_field(identity, name, value)
                touched.add(str(identity))
        if not touched:
            return ()
        return tuple(
            change
            for change in staged.changes()
            if change.owner in touched and change.old != change.new
        )

    # -- the open project's own records ---------------------------------------

    @staticmethod
    def _authored_stats(project: Any | None, kind: str) -> Mapping[Any, Any]:
        if project is None:
            return {}
        return project.enemies if kind == ENEMY else project.characters

    @staticmethod
    def _authored_maps(project: Any | None) -> Mapping[int, Any]:
        if project is None:
            return {}
        return project.maps


def clone_maps(source: Maps) -> Maps:
    """A fresh `Maps` over the same records, so staging here mutates nothing.

    The loaded `Maps` is shared with the surface's own reads; staging an edit into
    it would make the second read of a row return the edited value and turn one
    edit into two. The Entities destination stages placement edits into the same
    kind of copy, which is why this is one function rather than two.
    """
    return Maps(
        identification=source.identification,
        profile=source.profile,
        entries=tuple(source.entries()),
        arrays=tuple(source.slot_arrays()),
        placements=tuple(source.placements()),
        base_bytes=source.base_bytes,
    )


def span(row: RecordRow) -> RomRange:
    """The byte extent one record row proves, as the ROM surface's own unit."""
    return RomRange(FileOffset(row.file_offset), row.size)


def with_field(payload: Any, row: RecordRow, name: str, value: int) -> Any:
    """The authored data documents with one record's one field set.

    Returns a new payload and mutates nothing, so the journal's `before` snapshot
    stays the value the project actually held. The record must already be
    authored: a row that is not editable carries the reason and is never edited.
    """
    if row.kind == ENEMY:
        return replace(
            payload,
            enemies={**payload.enemies, row.key: {**payload.enemies[row.key], name: value}},
        )
    if row.kind == CHARACTER:
        return replace(
            payload,
            characters={
                **payload.characters,
                row.key: {**payload.characters[row.key], name: value},
            },
        )
    index = row.key.index
    return replace(
        payload, maps={**payload.maps, index: {**payload.maps[index], name: value}}
    )


def load_data_surface(
    rom_path: str | Path,
    catalog: RomProfileCatalog,
    identification: RomIdentification,
    profile: RomProfile,
    image: bytes,
) -> DataSurface:
    """Read the stat tables from an already-identified image, and the map table.

    The stat tables are decoded from the bytes in hand rather than re-read from
    the file: the image is already identified and its hash already checked, and
    `stat_tables_from_image` re-checks the profile contract on this path.

    The map table has no from-image entry point in the SDK, so it is loaded
    through `webfoot.maps.load_maps`, which re-identifies the file. A profile
    that declares no map-entry table - Legacy of Goku II's records are a variant
    layout and its profile deliberately declares none against this codec - is a
    stated absence here, not a failure: the stat tables still load and the page
    says why the map headers are missing.
    """
    try:
        tables = stat_tables_from_image(identification, profile, image)
    except (ValueError, OSError) as exc:
        raise DataSurfaceError(str(exc)) from exc

    maps: Maps | None = None
    problem = ""
    try:
        maps = load_maps(rom_path, catalog)
    except (ValueError, OSError) as exc:
        problem = str(exc)
    if maps is not None and maps.profile.id != profile.id:
        maps = None
        problem = (
            f"the map table was read against profile {maps.profile.id!r}, not the "
            f"open image's {profile.id!r}"
        )

    return DataSurface(
        identification=identification,
        profile=profile,
        image=image,
        tables=tables,
        maps=maps,
        maps_problem=problem,
    )
