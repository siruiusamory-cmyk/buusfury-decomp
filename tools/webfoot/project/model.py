"""The authored project: what a mod IS on disk, and what it promises.

TOOLKIT-002. A mod is a directory of text, not a sequence of edits applied to a
binary. That inversion is the whole point of this ticket, and three properties
follow from it:

**The project is the authoring surface; the ROM is the truth.** `project.toml`
pins the base ROM by SHA-256 and the profile by id, so a project carries the
identity of the thing it was authored against and can refuse to build against
anything else. It does NOT carry a path to that ROM: a path is a fact about one
machine, and a project that recorded one would stop being portable the moment
it was cloned.

**Authored values are semantic.** `hp = 200`, never `0x00711BE0 = 0xC8`. A mod
that stored offsets would break when anything moved and would be unreadable to
a future decomp backend; a mod that stores `hp` survives both. Addresses appear
in the project only as commentary the build never reads back.

**Unknown bytes are the project's responsibility.** Both stat layouts have
spans this project has not decoded, and byte-identical reconstruction requires
them verbatim. They live in the authored file as an opaque hex blob per record
(`raw`), which the user is not expected to edit and which the build re-emits
untouched. Dropping them would make the round-trip proof unachievable; hiding
them somewhere outside the authored tree would make the project incomplete.

Layout, deliberately the smallest thing that works:

    project/
      project.toml      identity: format version, profile, base ROM hash
      enemies/          one file per stat table, not one file per record
        enemies.toml
      characters/
        characters.toml
      text/             TOOLKIT-004
        strings.toml

One file per table rather than per record: 141 single-record files would be a
worse Git experience, not a better one, and nothing here needs per-record file
granularity. Directories exist only for the supported content types; no empty
directories are reserved for systems that do not exist yet.

**Text carries no `raw` blob, and that is not an inconsistency.** A stat record
needs one because only part of its stride is decoded, so the undecoded spans
have to ride along verbatim. The text codec is lossless over the whole pool -
every byte, control codes included, survives `decode` then `encode` - so the
authored string already IS the complete description of its bytes. Adding a
redundant hex copy would create a second source of truth that could disagree
with the first, which is worse than having one.

1,534 strings live in a single `text/strings.toml` rather than in per-scene
files, because nothing here yet knows which scene a string belongs to. Inventing
a grouping would mean inventing facts; the index key already sorts stably and
gives a one-line-per-edit diff.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Mapping

from ..formats import stat_tables as st
from ..formats import text_tables as tt
from .format import ProjectFormatError, dump_toml, load_toml

#: TOOLKIT-007. Authored map field order, mirroring `_ENEMY_FIELD_ORDER`:
#: fixed so output is deterministic, and ordered for reading rather than sorted.
#: Kept as a local constant rather than imported from `webfoot.maps`, because
#: this package owns the authoring surface and must not reach into a module that
#: opens ROMs - the same boundary `webfoot.project` docstring states. The names
#: are checked against `maps.MAP_FIELDS` by a test, so the two cannot drift.
_MAP_FIELD_ORDER = ("zone", "area", "variation", "flags", "music_id")

#: Bumped when the authored layout changes incompatibly. A project declaring a
#: version this toolkit does not implement is refused rather than guessed at.
PROJECT_FORMAT_VERSION = 1

_PROJECT_FILE = "project.toml"
_ENEMY_FILE = Path("enemies") / "enemies.toml"
_CHARACTER_FILE = Path("characters") / "characters.toml"
_TEXT_FILE = Path("text") / "strings.toml"
_DIALOGUE_FILE = Path("dialogue") / "replacements.toml"
_MAP_FILE = Path("maps") / "maps.toml"
PLACEMENT_TYPES_FILE = Path("placement_types") / "types.toml"

#: TOOLKIT-010. Graphics extraction writes one manifest plus one indexed PNG per
#: distinct payload. The manifest is the canonical part: a PNG carries pixels and
#: a palette but not the ROM-specific facts - dimensions as the *piece* declares
#: them, bit depth, sharing, the packed extent an edit is bounded by - so those
#: live in deterministic sidecar metadata rather than being inferred from the
#: image. Assets are named by stable identity, so a shared payload appears once.
GRAPHICS_FILE = Path("graphics") / "graphics.toml"
GRAPHICS_ASSET_DIR = Path("graphics") / "assets"

#: WORKBENCH-005. Authored graphics edits, kept apart from the extracted
#: `graphics.toml` manifest: the manifest is deterministic ROM-derived output a
#: user does not hand-edit, while this file is authored source - one palette
#: recolour per line, so a visual edit made in the GUI travels into the build.
#: A missing file means the project authors no graphics edits, matching every
#: other subsystem; only RGB is stored, because the SDK owns the RGB->GBA-word
#: packing and a project that stored the word would leak that format upward.
GRAPHICS_OVERRIDES_FILE = Path("graphics") / "overrides.toml"

#: MAP-TILE-PAINT-001. Authored dominant-layer chunk-cell edits. A sibling of
#: `maps/maps.toml` rather than a field inside it, because the two describe
#: different things and are edited by different surfaces: `maps.toml` is the map
#: *record* (zone, area, music, placements), while this is the map's **layout** -
#: which existing chunk occupies which cell of which layer. Keeping them apart
#: leaves a layout edit's diff readable. A missing file means the project paints
#: no layout, matching every other optional subsystem.
LAYOUT_FILE = Path("maps") / "layout.toml"

#: MAP-CHUNK-AUTHORING-001. Project-authored dominant chunks: chunk bodies the
#: author created that the canonical image does not contain.
#:
#: A third `maps/` document rather than a field of `layout.toml`, because the two
#: have different lifetimes and different owners. A layout cell is a *reference*;
#: an authored chunk is a *resource* that outlives any single cell and may be
#: referenced by several. Keeping them apart means deleting every reference to a
#: chunk leaves the chunk intact and re-placeable, and a chunk's own body diff
#: stays readable instead of being buried in a cell table.
#:
#: A missing file means the project authors no chunks, matching every other
#: optional subsystem, so a project extracted before this capability stays
#: loadable.
CHUNK_FILE = Path("maps") / "chunks.toml"

#: The side of a dominant chunk's screen-entry plane. As with `_LAYER_SLOT_COUNT`
#: this is the hardware's number stated locally rather than imported - this
#: package owns the authored surface and must not reach into a module that opens
#: ROMs - and a test pins it against `formats.map_graphics.CHUNK_SIDE_TILES`.
_CHUNK_SIDE = 32

#: The screen-entry width a chunk cell holds. Sixteen bits is the GBA's screen
#: entry, so this is the hardware's number too.
_CHUNK_ENTRY_MAX = 0xFFFF

#: The two authored-chunk identity forms, matched rather than trusted.
#:
#: ``chunk:name`` is the chunk's own durable identity, following the authored
#: placement precedent (`map:NNNN/authored:name`): lowercase, stable, and
#: independent of any address, so a chunk can be authored before a build has
#: chosen where it will live.
#:
#: ``map:NNNN/layer:N/chunk:N`` names the CANONICAL chunk a body started from, by
#: the layer's own 1-based vocabulary ordinal - the same "Chunk N" a person reads
#: in the map editor, and the same vocabulary `layout.toml` stores. A template is
#: resolved against the canonical image and never against the authored one, so
#: painting a cell can never silently re-point a template that names it.
_CHUNK_IDENTITY = re.compile(r"^chunk:([a-z][a-z0-9_-]{0,63})$")
_CHUNK_TEMPLATE = re.compile(r"^map:(\d{4})/layer:([0-3])/chunk:(\d+)$")

#: The chunk-cell key inside `chunks.toml`: a zero-padded ``row,column`` pair, so
#: lexical order is row-major order and a diff reads top-to-bottom.
_CHUNK_CELL = re.compile(r"^(\d{2}),(\d{2})$")

#: The BG slot count an authored layout may name. Four is the GBA's regular-BG
#: count, so this is the hardware's number rather than a per-game extent. It is
#: stated here rather than imported because this package owns the authored
#: surface and must not reach into a module that opens ROMs (the same boundary
#: `_MAP_FIELD_ORDER` respects); `test_map_layout_project` asserts it against
#: `formats.map_graphics.ROOT_LAYER_SLOTS`, so the two cannot drift.
_LAYER_SLOT_COUNT = 4

#: The two identity forms an authored layout key may take. Both are matched
#: rather than trusted: a file naming `zone:0001` or `BG9` must be refused at
#: load, not silently dropped from the build.
_MAP_KEY = re.compile(r"^map:\d{4}$")
_BG_KEY = re.compile(r"^BG(\d+)$")

#: Authored field order within a record. Fixed, so output is deterministic;
#: chosen for reading rather than sorted, because a human edits these.
_ENEMY_FIELD_ORDER = ("hp", "exp", "level", "strength", "power", "endurance")
_CHARACTER_FIELD_ORDER = (
    "level",
    "hp",
    "ep",
    "strength",
    "power",
    "endurance",
    "speed",
)

#: Decoded-but-not-editable fields. They are authored so the file is a complete
#: description of the record, and validated on load, but no CLI edit path
#: exposes them: `type_id` IS the enemy identity, and `person` /
#: `technique_count` index tables this ticket does not decode.
_ENEMY_FIXED_FIELDS = ("type_id",)
_CHARACTER_FIXED_FIELDS = ("person", "technique_count")


class ProjectError(ValueError):
    """Base error for project source problems."""


class ProjectLoadError(ProjectError):
    """Raised when a project cannot be read or its schema is unusable."""


class ProjectValidationError(ProjectError):
    """Raised when project content is structurally valid but semantically wrong.

    Distinct from `ProjectLoadError` on purpose: one means "this is not a
    project", the other means "this is a project that says something false".
    Both fail before any output is written.
    """


@dataclass(frozen=True, slots=True)
class ProjectMeta:
    """What `project.toml` pins. Everything here is identity, not preference.

    `base_rom_sha256` is the contract: a build against any other image is
    refused. `profile_id` names the metadata contract - which extents the
    records were authored against - and is checked independently, because a
    matching hash with mismatched extents would still be wrong.
    """

    format_version: int
    profile_id: str
    game: str
    base_rom_sha256: str
    base_rom_size: int
    name: str

    def to_document(self) -> dict[str, Any]:
        return {
            "project": {
                "format_version": self.format_version,
                "name": self.name,
            },
            "base": {
                "profile_id": self.profile_id,
                "game": self.game,
                "sha256": self.base_rom_sha256,
                "size": self.base_rom_size,
            },
        }

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> "ProjectMeta":
        project = _require_table(document, "project", _PROJECT_FILE)
        base = _require_table(document, "base", _PROJECT_FILE)

        version = project.get("format_version")
        if type(version) is not int:
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: project.format_version must be an integer"
            )
        if version != PROJECT_FORMAT_VERSION:
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: project format version {version} is not "
                f"supported; this toolkit implements version "
                f"{PROJECT_FORMAT_VERSION}"
            )

        sha256 = _require_str(base, "sha256", "base", _PROJECT_FILE).lower()
        if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: base.sha256 must be 64 hexadecimal characters"
            )
        size = base.get("size")
        if type(size) is not int or size <= 0:
            raise ProjectLoadError(
                f"{_PROJECT_FILE}: base.size must be a positive integer"
            )

        return cls(
            format_version=version,
            profile_id=_require_str(base, "profile_id", "base", _PROJECT_FILE),
            game=_require_str(base, "game", "base", _PROJECT_FILE),
            base_rom_sha256=sha256,
            base_rom_size=size,
            name=_require_str(project, "name", "project", _PROJECT_FILE),
        )


@dataclass(frozen=True, slots=True)
class StatProject:
    """A whole loaded project: identity plus authored records.

    Records are held keyed by durable `StatIdentity`, and every record carries
    the opaque bytes it was extracted with. That pairing is what makes a build
    lossless: the semantic fields describe what a person edits, and `raw`
    carries everything the project has not learned to describe yet.
    """

    meta: ProjectMeta
    enemies: dict[st.StatIdentity, dict[str, Any]]
    characters: dict[st.StatIdentity, dict[str, Any]]
    #: TOOLKIT-004. Authored strings by durable identity. Empty for a project
    #: extracted before text support existed, which stays loadable: a missing
    #: `text/strings.toml` means "this project does not author text", not
    #: "this project is broken". A build then leaves the ROM's text alone.
    strings: dict[tt.TextIdentity, str] = field(default_factory=dict)
    dialogues: dict[str, str] = field(default_factory=dict)
    #: TOOLKIT-007. Authored map records by table index. Empty for a project
    #: extracted before map support existed, which stays loadable on the same
    #: reasoning as `strings`: a missing `maps/maps.toml` means "this project
    #: does not author maps", not "this project is broken".
    maps: dict[int, dict[str, Any]] = field(default_factory=dict)
    # Optional v1 read-only relationship catalog. Missing keeps old projects valid.
    placement_types: dict[str, Any] | None = None
    placement_events: dict[str, Any] | None = None
    #: WORKBENCH-005. Authored palette recolours. Empty for a project that
    #: authors no graphics edits, which stays loadable on the same reasoning as
    #: `strings`: absence means "no graphics edits", not "broken".
    graphics_overrides: "GraphicsOverrides" = field(default_factory=lambda: GraphicsOverrides())
    #: MAP-TILE-PAINT-001. Authored layout-cell edits. Empty for a project that
    #: paints no layout, which stays loadable on the same reasoning as `strings`.
    layout: "LayoutEdits" = field(default_factory=lambda: LayoutEdits())
    #: MAP-CHUNK-AUTHORING-001. Chunk bodies this project authored. Empty for a
    #: project that authors none, which stays loadable on the same reasoning.
    chunks: "AuthoredChunks" = field(default_factory=lambda: AuthoredChunks())


@dataclass(frozen=True, slots=True)
class AuthoredChunkEntry:
    """One screen-entry cell an author changed inside an authored chunk.

    ``prior`` is stored, not merely derivable: it is the entry the template held
    at this cell, so the document itself proves the body was authored against the
    template it names. A template that resolved to different bytes would make
    every stored ``prior`` disagree, and the build refuses rather than composing a
    chunk from a source nobody agreed on - the same fail-closed shape a
    :class:`tools.webfoot.write.ByteChange` uses for in-place edits.
    """

    row: int
    column: int
    prior: int
    entry: int

    @property
    def cell(self) -> int:
        """Row-major index of this cell inside the chunk's own plane."""
        return self.row * _CHUNK_SIDE + self.column

    @property
    def key(self) -> str:
        """The zero-padded ``row,column`` key this cell is stored under."""
        return f"{self.row:02d},{self.column:02d}"


@dataclass(frozen=True, slots=True)
class AuthoredChunk:
    """One project-authored chunk: a new body plus the template it came from.

    Deliberately a sparse delta over a named canonical chunk rather than a
    copied-out plane. Three reasons, and they are the same three that make a
    project directory a usable mod source:

    * a delta is what a reviewer reads - "these nine cells changed" - while 1,024
      copied integers bury the authored intent in unchanged content;
    * a delta diffs, so a Git-tracked project shows a authored change as a small
      hunk rather than a rewritten blob;
    * the template keeps the author honest about the *vocabulary*: the body is
      composed from entries that a real map already displays, which is exactly
      the "existing graphics only" boundary this capability ships under.

    The chunk's own identity is independent of every address, so it exists before
    a build has decided where the body will live.
    """

    identity: str
    #: ``map:NNNN/layer:N/chunk:N`` - the canonical source body's location.
    template: str
    #: The authored cells, sorted by (row, column). Never empty: a chunk with no
    #: authored cell would be a byte-identical copy of its template, and the
    #: capability is creation, not aliasing.
    entries: tuple[AuthoredChunkEntry, ...] = ()

    def __post_init__(self) -> None:
        match = _CHUNK_IDENTITY.match(self.identity or "")
        if match is None:
            raise ProjectValidationError(
                f"authored chunk identity {self.identity!r} must be "
                "'chunk:<name>' with a lowercase name"
            )
        template = _CHUNK_TEMPLATE.match(self.template or "")
        if template is None:
            raise ProjectValidationError(
                f"authored chunk {self.identity!r} names template "
                f"{self.template!r}, which is not 'map:NNNN/layer:N/chunk:N'"
            )
        slots = {entry.row * _CHUNK_SIDE + entry.column for entry in self.entries}
        if len(slots) != len(self.entries):
            raise ProjectValidationError(
                f"authored chunk {self.identity!r} edits one cell twice"
            )
        for entry in self.entries:
            if not 0 <= entry.row < _CHUNK_SIDE or not 0 <= entry.column < _CHUNK_SIDE:
                raise ProjectValidationError(
                    f"authored chunk {self.identity!r} edits cell "
                    f"({entry.row}, {entry.column}), which is outside the "
                    f"{_CHUNK_SIDE}x{_CHUNK_SIDE} plane"
                )
            for name, value in (("prior", entry.prior), ("entry", entry.entry)):
                if type(value) is not int or not 0 <= value <= _CHUNK_ENTRY_MAX:
                    raise ProjectValidationError(
                        f"authored chunk {self.identity!r} cell {entry.key} has a "
                        f"{name} of {value!r}, which is not a 16-bit screen entry"
                    )

    def to_document(self) -> dict:
        return {
            "template": self.template,
            "entries": {
                entry.key: [entry.prior, entry.entry]
                for entry in sorted(self.entries, key=lambda e: (e.row, e.column))
            },
        }

    @classmethod
    def from_document(cls, identity: object, document: object, where: object) -> "AuthoredChunk":
        if not isinstance(document, dict):
            raise ProjectLoadError(f"{where}: authored chunk {identity!r} is not a table")
        unknown = set(document) - {"template", "entries"}
        if unknown:
            raise ProjectLoadError(
                f"{where}: authored chunk {identity!r} declares unknown key(s) "
                f"{sorted(unknown)}"
            )
        template = document.get("template")
        if not isinstance(template, str):
            raise ProjectLoadError(
                f"{where}: authored chunk {identity!r} declares no template"
            )
        raw = document.get("entries")
        if not isinstance(raw, dict) or not raw:
            raise ProjectLoadError(
                f"{where}: authored chunk {identity!r} declares no entries"
            )
        entries: list[AuthoredChunkEntry] = []
        for key, value in raw.items():
            match = _CHUNK_CELL.match(str(key))
            if match is None:
                raise ProjectLoadError(
                    f"{where}: authored chunk {identity!r} names cell {key!r}, "
                    "which is not a 'row,column' pair"
                )
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ProjectLoadError(
                    f"{where}: authored chunk {identity!r} cell {key} must be "
                    "[prior, entry]"
                )
            row, column = int(match.group(1)), int(match.group(2))
            entries.append(
                AuthoredChunkEntry(
                    row=row, column=column, prior=value[0], entry=value[1]
                )
            )
        return cls(
            identity=str(identity),
            template=template,
            entries=tuple(sorted(entries, key=lambda e: (e.row, e.column))),
        )


@dataclass(frozen=True)
class AuthoredChunks:
    """Every chunk a project authors, keyed by its own durable identity."""

    chunks: dict[str, AuthoredChunk] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not self.chunks

    def get(self, identity: str) -> AuthoredChunk | None:
        return self.chunks.get(identity)

    def identities(self) -> tuple[str, ...]:
        return tuple(sorted(self.chunks))

    def to_document(self) -> dict:
        return {
            "chunk": {
                identity: chunk.to_document()
                for identity, chunk in sorted(self.chunks.items())
            }
        }

    @classmethod
    def from_document(cls, document: object, where: object) -> "AuthoredChunks":
        table = document.get("chunk") if isinstance(document, dict) else None
        if not isinstance(table, dict) or not table:
            raise ProjectLoadError(f"{where}: declares no authored chunks")
        unknown = set(document) - {"chunk"}
        if unknown:
            raise ProjectLoadError(
                f"{where}: unknown top-level key(s) {sorted(unknown)}"
            )
        chunks: dict[str, AuthoredChunk] = {}
        for identity, value in table.items():
            if not isinstance(identity, str) or _CHUNK_IDENTITY.match(identity) is None:
                raise ProjectLoadError(
                    f"{where}: {identity!r} is not a 'chunk:<name>' identity"
                )
            if identity in chunks:
                raise ProjectLoadError(f"{where}: duplicate chunk {identity!r}")
            chunks[identity] = AuthoredChunk.from_document(identity, value, where)
        return cls(chunks=dict(sorted(chunks.items())))


@dataclass(frozen=True)
class LayoutEdits:
    """Authored dominant-layer chunk-cell edits, keyed by map and layer.

    ``layout["map:0040"][1][0] = 2`` reads "cell 0 of map 40's BG1 becomes the
    layer's 2nd existing chunk". Three properties make that a semantic authoring
    value rather than a disguised offset:

    * the map is named by its durable identity (``map:NNNN``, the same key
      ``maps/maps.toml`` uses), and the layer by BG slot, so nothing points at a
      file offset or a raw address;
    * the replacement is the chunk's **1-based ordinal inside that layer's own
      existing chunk vocabulary** - the same "Chunk N" a person reads in the map
      editor - not the pointer address. The ordinal is resolved against the base
      image at build time, and because the vocabulary is the first-appearance
      order of the layer's own non-null pointers it is a deterministic property
      of that image, so the same project file resolves identically on every
      machine and after any reopen;
    * the cell is a row-major index into the layer's own chunk window, which is
      the index the engine's loader uses.

    A pointer address is deliberately NOT storable. The proven replacement rule
    is "a chunk this same layer already uses", and an ordinal states exactly
    that; a stored address would additionally pin the edit to one image's layout
    of the bank data, and would be unreadable in a project file.

    MAP-CHUNK-AUTHORING-001 widens the value by exactly one form and no more: a
    cell may also hold the **identity** of a project-authored chunk
    (``chunk:name``, declared in :class:`AuthoredChunks`). A cell still carries
    one value and one meaning; what changed is that "which chunk" is no longer
    only answerable from the canonical image. The identity is deliberately what is
    stored rather than the address the build will choose, because before a build
    there IS no address - the map cell knows its chunk, and the build resolves
    identity to address, in that order, exactly once.
    """

    #: ``"map:NNNN"`` -> BG slot -> row-major cell -> 1-based chunk ordinal, or
    #: the ``chunk:name`` identity of a project-authored chunk.
    maps: dict[str, dict[int, dict[int, int | str]]] = field(default_factory=dict)

    @staticmethod
    def key_for(index: int) -> str:
        """The durable identity key for a map table index."""
        return f"map:{index:04d}"

    def is_empty(self) -> bool:
        return not any(layers for layers in self.maps.values())

    def cells(self) -> dict[tuple[int, int, int], int | str]:
        """Flatten to ``{(map index, layer slot, cell): value}``.

        The one place the ``map:NNNN`` key is turned back into an index, so
        every caller reads the identity form the same way. A key that is not
        that form cannot occur: `from_document` refuses anything else.

        A value is an ``int`` (the layer's 1-based canonical chunk ordinal) or a
        ``str`` (a project-authored chunk identity); the two are never mixed
        within one cell and a caller that needs only one form filters on ``type``.
        """
        flat: dict[tuple[int, int, int], int | str] = {}
        for key, layers in self.maps.items():
            index = int(key[4:], 10)
            for slot, cells in layers.items():
                for cell, value in cells.items():
                    flat[(index, slot, cell)] = value
        return flat

    def for_map(self, index: int) -> dict[int, dict[int, int | str]]:
        """BG slot -> cell -> value for one map, empty when it paints none."""
        return dict(self.maps.get(LayoutEdits.key_for(index), {}))

    def to_document(self) -> dict[str, Any]:
        """The `[layout]` table: map, then BG slot, then row-major cell.

        Every level is keyed by a zero-padded or fixed-width integer, so lexical
        order is numeric order and the file is deterministic without the writer
        having to sort anything. Each level is emitted sorted for that reason.
        """
        return {
            "layout": {
                key: {
                    f"BG{slot}": {
                        f"{cell:03d}": ordinal
                        for cell, ordinal in sorted(cells.items())
                    }
                    for slot, cells in sorted(layers.items())
                }
                for key, layers in sorted(self.maps.items())
            }
        }

    @classmethod
    def from_document(cls, document: Mapping[str, Any], where: object) -> "LayoutEdits":
        table = document.get("layout")
        if table is None:
            raise ProjectLoadError(f"{where}: missing required [layout] table")
        if not isinstance(table, Mapping):
            raise ProjectLoadError(f"{where}: [layout] must be a table")
        maps: dict[str, dict[int, dict[int, int | str]]] = {}
        for map_key, layers in table.items():
            label = f"layout.{map_key}"
            if not _MAP_KEY.match(str(map_key)):
                raise ProjectLoadError(
                    f"{where}: {label} is not a valid map identity; expected "
                    "'map:NNNN' with four digits"
                )
            if not isinstance(layers, Mapping):
                raise ProjectLoadError(f"{where}: {label} must be a table")
            by_slot: dict[int, dict[int, int | str]] = {}
            for slot_key, cells in layers.items():
                slot_label = f"{label}.{slot_key}"
                match = _BG_KEY.match(str(slot_key))
                if match is None:
                    raise ProjectLoadError(
                        f"{where}: {slot_label} is not a layer slot; expected "
                        "'BG0'..'BG3'"
                    )
                slot = int(match.group(1), 10)
                # A file naming BG4 would otherwise be silently dropped from the
                # build - the exact "authored but not applied" failure this
                # format exists to prevent.
                if slot >= _LAYER_SLOT_COUNT:
                    raise ProjectValidationError(
                        f"{where}: {slot_label} is outside BG0..BG{_LAYER_SLOT_COUNT - 1}"
                    )
                if not isinstance(cells, Mapping):
                    raise ProjectLoadError(f"{where}: {slot_label} must be a table")
                by_cell: dict[int, int | str] = {}
                for cell_key, ordinal in cells.items():
                    cell_label = f"{slot_label}.{cell_key}"
                    if not str(cell_key).isdigit():
                        raise ProjectLoadError(
                            f"{where}: {cell_label} is not a valid cell index; "
                            "expected a zero-padded integer key"
                        )
                    cell = int(cell_key, 10)
                    if cell in by_cell:
                        raise ProjectLoadError(f"{where}: duplicate cell {cell} in {slot_label}")
                    # MAP-CHUNK-AUTHORING-001: the value is an integer chunk
                    # ordinal, or the identity of a project-authored chunk. The
                    # identity is matched here; whether it EXISTS is checked
                    # across documents in `read_project`, because this class
                    # cannot see the chunk table.
                    if isinstance(ordinal, str):
                        if _CHUNK_IDENTITY.match(ordinal) is None:
                            raise ProjectValidationError(
                                f"{where}: {cell_label} names {ordinal!r}, which is "
                                "neither an integer chunk ordinal nor a "
                                "'chunk:<name>' authored chunk"
                            )
                        by_cell[cell] = ordinal
                        continue
                    if type(ordinal) is not int:
                        raise ProjectValidationError(
                            f"{where}: {cell_label} must be an integer chunk ordinal "
                            f"or an authored chunk identity, got {ordinal!r}"
                        )
                    if ordinal < 1:
                        raise ProjectValidationError(
                            f"{where}: {cell_label} names chunk {ordinal}; ordinals are "
                            "1-based, so 0 is not a chunk this layer uses"
                        )
                    by_cell[cell] = ordinal
                if not by_cell:
                    raise ProjectLoadError(f"{where}: {slot_label} declares no cells")
                if slot in by_slot:
                    raise ProjectLoadError(f"{where}: duplicate layer BG{slot} in {label}")
                by_slot[slot] = by_cell
            if not by_slot:
                raise ProjectLoadError(f"{where}: {label} declares no layers")
            if map_key in maps:
                raise ProjectLoadError(f"{where}: duplicate map {map_key}")
            maps[map_key] = by_slot
        if not maps:
            raise ProjectLoadError(f"{where}: [layout] declares no edits")
        return cls(maps=maps)


@dataclass(frozen=True)
class GraphicsOverrides:
    """Authored graphics edits: palette-index -> 8-bit RGB recolour.

    Only RGB is held, never the packed GBA word: the SDK owns the RGB->word
    packing (`sprite_graphics.pack_gba_colour`), and a project that stored the
    word would bake ROM-format knowledge into authored source. The build packs
    each triple and plans it through `ActorSprites.plan_palette_entry`, so an
    authored recolour reaches the emitted ROM at that entry's two bytes.
    """

    #: palette index -> (red, green, blue), each channel 0..255.
    palette: dict[int, tuple[int, int, int]] = field(default_factory=dict)

    def to_document(self) -> dict[str, Any]:
        """The `[palette]` table, keyed by zero-padded index for numeric order."""
        return {
            "palette": {
                f"{index:03d}": {
                    "red": rgb[0],
                    "green": rgb[1],
                    "blue": rgb[2],
                }
                for index, rgb in sorted(self.palette.items())
            }
        }

    @classmethod
    def from_document(cls, document: Mapping[str, Any], where: object) -> "GraphicsOverrides":
        table = document.get("palette")
        if table is None:
            raise ProjectLoadError(f"{where}: missing required [palette] table")
        if not isinstance(table, Mapping):
            raise ProjectLoadError(f"{where}: [palette] must be a table")
        palette: dict[int, tuple[int, int, int]] = {}
        for key, entry in table.items():
            label = f"palette.{key}"
            if not str(key).isdigit():
                raise ProjectLoadError(
                    f"{where}: {label} is not a valid palette index; expected a "
                    "zero-padded integer key"
                )
            index = int(key, 10)
            if not 0 <= index < 256:
                raise ProjectValidationError(
                    f"{where}: {label} index {index} is outside 0..255"
                )
            if not isinstance(entry, Mapping):
                raise ProjectLoadError(f"{where}: {label} must be a table")
            unexpected = set(entry) - {"red", "green", "blue"}
            if unexpected:
                joined = ", ".join(sorted(unexpected))
                raise ProjectLoadError(f"{where}: {label} has unknown fields: {joined}")
            channels = []
            for name in ("red", "green", "blue"):
                value = _require_int(entry, name, label, where)
                if not 0 <= value <= 255:
                    raise ProjectValidationError(
                        f"{where}: {label}.{name}={value} is outside 0..255"
                    )
                channels.append(value)
            if index in palette:
                raise ProjectLoadError(f"{where}: duplicate palette index {index}")
            palette[index] = (channels[0], channels[1], channels[2])
        if not palette:
            raise ProjectLoadError(f"{where}: [palette] declares no overrides")
        return cls(palette=palette)


# --- helpers -------------------------------------------------------------


def _require_table(
    document: Mapping[str, Any], key: str, where: object
) -> Mapping[str, Any]:
    value = document.get(key)
    if not isinstance(value, Mapping):
        raise ProjectLoadError(f"{where}: missing required [{key}] table")
    return value


def _require_str(
    table: Mapping[str, Any], key: str, section: str, where: object
) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProjectLoadError(
            f"{where}: {section}.{key} must be a non-empty string"
        )
    return value.strip()


def _require_int(
    table: Mapping[str, Any], key: str, label: str, where: object
) -> int:
    value = table.get(key)
    # bool is an int subclass; `hp = true` must not silently become 1.
    if type(value) is not int:
        raise ProjectValidationError(
            f"{where}: {label}.{key} must be an integer, got {value!r}"
        )
    return value


def _require_hex_blob(
    table: Mapping[str, Any], label: str, where: object, size: int
) -> bytes:
    raw = table.get("raw")
    if not isinstance(raw, str):
        raise ProjectValidationError(
            f"{where}: {label}.raw must be a hexadecimal string carrying the "
            "record's undecoded bytes; without it the record cannot be rebuilt"
        )
    try:
        blob = bytes.fromhex(raw)
    except ValueError as exc:
        raise ProjectValidationError(f"{where}: {label}.raw is not valid hex: {exc}") from exc
    if len(blob) != size:
        raise ProjectValidationError(
            f"{where}: {label}.raw must be exactly {size} bytes; got {len(blob)}"
        )
    return blob


# --- serialization -------------------------------------------------------


def _enemy_document(
    records: list[tuple[st.StatIdentity, st.EnemyRecord, bytes, str | None]],
) -> dict[str, Any]:
    """Build the enemies document, ordered by durable identity key.

    Sorted by `type_id`, NOT by table position. Table order is a fact about the
    current ROM layout; identity order is a fact about the project. Sorting by
    identity means a record that moves in the ROM does not move in the file,
    which is the difference between a diff that shows one edit and a diff that
    shows a reshuffle.
    """
    tables: dict[str, Any] = {}
    for identity, record, original, alias in sorted(records, key=lambda item: item[0].key):
        entry: dict[str, Any] = {}
        if alias is not None:
            entry["alias"] = alias
        entry["type_id"] = record.type_id
        for field in _ENEMY_FIELD_ORDER:
            entry[field] = getattr(record, field)
        entry["raw"] = original.hex()
        tables[str(identity.key)] = entry
    return {"enemy": tables}


def _character_document(
    records: list[tuple[st.StatIdentity, st.BaseStatRecord, bytes, str]],
) -> dict[str, Any]:
    tables: dict[str, Any] = {}
    for identity, record, original, alias in sorted(records, key=lambda item: item[0].key):
        entry: dict[str, Any] = {"alias": alias}
        for field in _CHARACTER_FIELD_ORDER:
            entry[field] = getattr(record, field)
        for field in _CHARACTER_FIXED_FIELDS:
            entry[field] = getattr(record, field)
        entry["raw"] = original.hex()
        tables[str(identity.key)] = entry
    return {"character": tables}


def _text_document(strings: list[tuple[tt.TextIdentity, str]]) -> dict[str, Any]:
    """Build the strings document, ordered by durable identity key.

    The key is the pointer-table index zero-padded to four digits, so the
    lexical order TOML preserves is also the numeric order - `text:0009` sorts
    before `text:0010`, which a bare `9` and `10` would not.

    Each entry is a single `text` field. No address, no length, no `raw`: the
    address is where the string sits today, the length follows from the text,
    and the codec is lossless so the text is already complete.
    """
    tables: dict[str, Any] = {}
    for identity, text in sorted(strings, key=lambda item: item[0].index):
        tables[identity.key] = {"text": text}
    return {"text": tables}


def _dialogue_document(dialogues: Mapping[str, str]) -> dict[str, Any]:
    return {"dialogue": {name: {"text": text} for name, text in sorted(dialogues.items())}}


def _map_document(maps: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the maps document, ordered by map index.

    One entry per map record, keyed `map:0039` so lexical order is numeric
    order. Each carries the editable semantic fields, the record's undecoded
    bytes as `raw`, and - when the map has a readable slot extent - that
    extent's bytes as `slots`.

    `slots` is a second opaque blob rather than a decoded structure because for
    77 of the 112 extents this toolkit cannot say what the bytes mean, and for
    the other 35 the typed reading is a classification of the same bytes rather
    than a different encoding of them. One blob per extent reconstructs both
    exactly; a decoded form would have to reconstruct the opaque case anyway,
    and would then be two sources of truth for one span. `shape` records the
    classification so a reader can see which extents are typed without the file
    implying the toolkit can rebuild them from fields it does not have.

    TOOLKIT-008 adds `placements`: one entry per factory-led placement record the
    map owns, in placement-index order. Unlike `slots` these carry authorable
    semantic fields, because the record's layout *is* established - but only
    `position_low`/`position_high` are authored raw halfwords, and `raw` still
    carries the whole record so every UNKNOWN word round-trips exactly. Their
    confirmed signed map/world interpretation is X then Y; the scene facade
    exposes that interpretation while this project model retains the lossless
    source representation.
    """
    tables: dict[str, Any] = {}
    for entry in sorted(maps, key=lambda item: item["index"]):
        record: dict[str, Any] = {}
        for field in _MAP_FIELD_ORDER:
            record[field] = entry[field]
        record["raw"] = entry["raw"].hex()
        if entry.get("slots") is not None:
            record["shape"] = entry["shape"]
            record["slots"] = entry["slots"].hex()
        placements = entry.get("placements")
        if placements:
            # A table keyed `placement:0000` rather than an array of tables:
            # the emitter carries nested tables and flat scalars only, and a
            # zero-padded key sorts lexically in numeric order, so the file is
            # deterministic without teaching the writer a new TOML construct.
            record["placements"] = {
                f"placement:{item['index']:04d}": {
                    "position_low": item["position_low"],
                    "position_high": item["position_high"],
                    "raw": item["raw"].hex(),
                    **{key: item[key] for key in ('descriptor', 'child_count', 'child_pointers_raw', 'record_size') if key in item},
                }
                for item in sorted(placements, key=lambda item: item["index"])
            }
        if entry.get("authored_placements"):
            record["authored_placements"] = {p.identity: p.to_document()
                for p in sorted(entry["authored_placements"], key=lambda p: p.identity)}
        tables[entry["key"]] = record
    return {"map": tables}


def write_project(
    directory: str | Path,
    meta: ProjectMeta,
    *,
    enemies: list[tuple[st.StatIdentity, st.EnemyRecord, bytes, str | None]],
    characters: list[tuple[st.StatIdentity, st.BaseStatRecord, bytes, str]],
    strings: list[tuple[tt.TextIdentity, str]] | None = None,
    dialogues: Mapping[str, str] | None = None,
    maps: list[dict[str, Any]] | None = None,
    graphics_overrides: "GraphicsOverrides | None" = None,
    layout: "LayoutEdits | None" = None,
    chunks: "AuthoredChunks | None" = None,
) -> list[Path]:
    """Write the whole authored tree. Returns the files written, in order.

    Overwrites deliberately: extraction is idempotent by design, so re-running
    it over an existing project must converge rather than refuse. That is the
    opposite of `emit_image`, which refuses to overwrite - a built ROM is an
    artefact whose provenance would become unanswerable if silently replaced,
    while an authored file is source the user can diff and revert.
    """
    root = Path(directory)
    written: list[Path] = []

    # Each subsystem's file is written only when that subsystem has content, so
    # a profile that does not declare one produces no empty file claiming it
    # authors it. `project.toml` is unconditional: it is what makes the
    # directory a project at all.
    #
    # This matters beyond tidiness. `read_project` refuses a file whose table is
    # empty, on the grounds that "I meant to author this and did not" is a
    # mistake worth catching - so an empty file written here would make the
    # project it just extracted unloadable.
    documents = [(Path(_PROJECT_FILE), meta.to_document())]
    if enemies:
        documents.append((_ENEMY_FILE, _enemy_document(enemies)))
    if characters:
        documents.append((_CHARACTER_FILE, _character_document(characters)))
    if strings:
        documents.append((_TEXT_FILE, _text_document(strings)))
    if dialogues:
        documents.append((_DIALOGUE_FILE, _dialogue_document(dialogues)))
    if maps:
        documents.append((_MAP_FILE, _map_document(maps)))
    if graphics_overrides and graphics_overrides.palette:
        documents.append((GRAPHICS_OVERRIDES_FILE, graphics_overrides.to_document()))
    if layout and not layout.is_empty():
        documents.append((LAYOUT_FILE, layout.to_document()))
    if chunks and not chunks.is_empty():
        documents.append((CHUNK_FILE, chunks.to_document()))

    for relative, document in documents:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n" explicitly: the default on Windows would translate to
        # CRLF and the "same project extracts to the same bytes" property would
        # then depend on which machine ran the extraction.
        path.write_text(dump_toml(document), encoding="utf-8", newline="\n")
        written.append(path)

    return written


def write_dialogue_replacements(
    directory: str | Path, dialogues: Mapping[str, str]
) -> Path:
    """Persist only the canonical dialogue source document for a loaded project.

    The authoring API validates the project and replacements before calling this
    narrow writer.  An empty mapping means the project has no dialogue override,
    so the optional document is removed instead of writing an invalid empty table.
    """
    path = Path(directory) / _DIALOGUE_FILE
    if not dialogues:
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        dump_toml(_dialogue_document(dialogues)), encoding="utf-8", newline="\n"
    )
    return path


def write_graphics_overrides(
    directory: str | Path, palette: Mapping[int, tuple[int, int, int]]
) -> Path:
    """Persist only the graphics overrides document for a loaded project.

    The narrow writer that mirrors `write_dialogue_replacements`: the graphics
    authoring API validates before calling it. An empty mapping means the project
    authors no palette edit, so the optional document is removed rather than
    written as an invalid empty table (which `read_project` would then refuse).
    """
    path = Path(directory) / GRAPHICS_OVERRIDES_FILE
    if not palette:
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    document = GraphicsOverrides(palette=dict(palette)).to_document()
    path.write_text(dump_toml(document), encoding="utf-8", newline="\n")
    return path


def _read_document(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ProjectLoadError(f"project file is missing: {path}") from exc
    except OSError as exc:
        raise ProjectLoadError(f"cannot read {path}: {exc}") from exc
    try:
        return load_toml(text)
    except ProjectFormatError as exc:
        raise ProjectLoadError(f"{path}: {exc}") from exc


def _read_records(
    path: Path,
    section: str,
    kind: str,
    fields: tuple[str, ...],
    fixed: tuple[str, ...],
    record_size: int,
) -> dict[st.StatIdentity, dict[str, Any]]:
    """Load one record file, or nothing at all if it is absent.

    Absence is legal and means the project does not author these records,
    matching `_read_strings`. A profile that declares no stat tables - Legacy of
    Goku II declares none this toolkit can read - extracts to a project with no
    stat files, and that project must load. A file that exists but is malformed
    is still an error; "missing" and "wrong" are different answers.
    """
    if not path.is_file():
        return {}

    document = _read_document(path)
    table = document.get(section)
    if not isinstance(table, Mapping):
        raise ProjectLoadError(f"{path}: missing required [{section}] table")

    records: dict[st.StatIdentity, dict[str, Any]] = {}
    for key, entry in table.items():
        label = f"{section}.{key}"
        if not isinstance(entry, Mapping):
            raise ProjectLoadError(f"{path}: {label} must be a table")
        try:
            identity = st.StatIdentity(kind=kind, key=int(key, 10))
        except ValueError as exc:
            raise ProjectLoadError(
                f"{path}: {label} is not a valid {kind} identity key: {exc}"
            ) from exc

        values: dict[str, Any] = {}
        for field in fields + fixed:
            values[field] = _require_int(entry, field, label, path)
        values["raw"] = _require_hex_blob(entry, label, path, record_size)

        alias = entry.get("alias")
        if alias is not None and not isinstance(alias, str):
            raise ProjectLoadError(f"{path}: {label}.alias must be a string")
        values["alias"] = alias

        unexpected = set(entry) - set(fields) - set(fixed) - {"raw", "alias"}
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(
                f"{path}: {label} has unknown fields: {joined}"
            )

        if identity in records:
            raise ProjectLoadError(f"{path}: duplicate {kind} identity {identity}")
        records[identity] = values

    if not records:
        raise ProjectLoadError(f"{path}: [{section}] declares no records")
    return records


def _read_strings(path: Path) -> dict[tt.TextIdentity, str]:
    """Load `text/strings.toml`, or nothing at all if it is absent.

    Absence is legal and means the project does not author text - a project
    extracted before TOOLKIT-004 stays loadable, and a build leaves the ROM's
    text untouched. A file that exists but is malformed is still an error;
    "missing" and "wrong" are different answers.

    Structure is checked here - key form, field names, duplicate identities, the
    value being a string. *Encodability* is not, and deliberately so: whether a
    given string can be encoded depends on the profile's encoding, which a
    project does not know. TOOLKIT-004 checked it here against the UTF-16LE
    codec, which was correct while one game existed and would now reject valid
    Legacy of Goku II text. The check moved to `build._check_strings`, which runs
    with the ROM's selected codec and reports against the same line; it is still
    validation before emission, just at the first point that can be right.
    """
    if not path.is_file():
        return {}

    document = _read_document(path)
    table = document.get("text")
    if not isinstance(table, Mapping):
        raise ProjectLoadError(f"{path}: missing required [text] table")

    strings: dict[tt.TextIdentity, str] = {}
    for key, entry in table.items():
        label = f"text.{key}"
        if not isinstance(entry, Mapping):
            raise ProjectLoadError(f"{path}: {label} must be a table")

        prefix, _, digits = key.partition(":")
        if prefix != "text" or not digits.isdigit():
            raise ProjectLoadError(
                f"{path}: {label} is not a valid text identity key; expected "
                'the form "text:0000"'
            )
        try:
            identity = tt.TextIdentity(int(digits, 10))
        except tt.TextCodecError as exc:
            raise ProjectLoadError(f"{path}: {label}: {exc}") from exc

        unexpected = set(entry) - {"text"}
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(f"{path}: {label} has unknown fields: {joined}")

        text = entry.get("text")
        if not isinstance(text, str):
            raise ProjectValidationError(f"{path}: {label}.text must be a string")

        if identity in strings:
            # Unreachable through TOML (duplicate keys are a parse error), but
            # the key form is normalized above, so two spellings of one index
            # could otherwise collide silently.
            raise ProjectLoadError(f"{path}: duplicate text identity {identity}")
        strings[identity] = text

    if not strings:
        raise ProjectLoadError(f"{path}: [text] declares no strings")
    return strings


def _read_dialogues(path: Path) -> dict[str, str]:
    """Load semantic compressed-dialogue replacements, or no dialogue edits."""
    if not path.is_file():
        return {}
    document = _read_document(path)
    table = document.get("dialogue")
    if not isinstance(table, Mapping):
        raise ProjectLoadError(f"{path}: missing required [dialogue] table")
    result: dict[str, str] = {}
    for target, entry in table.items():
        label = f"dialogue.{target}"
        if not isinstance(target, str) or not target:
            raise ProjectLoadError(f"{path}: dialogue target must be a non-empty string")
        if not isinstance(entry, Mapping) or set(entry) != {"text"}:
            raise ProjectLoadError(f"{path}: {label} requires exactly a text field")
        text = entry["text"]
        if not isinstance(text, str):
            raise ProjectValidationError(f"{path}: {label}.text must be a string")
        result[target] = text
    if not result:
        raise ProjectLoadError(f"{path}: [dialogue] declares no replacements")
    return result


def _read_maps(path: Path) -> dict[int, dict[str, Any]]:
    """Load `maps/maps.toml`, or nothing at all if it is absent.

    Structure is checked here - key form, field names, integer types, hex blob
    validity. Value *ranges* are not: the supported range for a field is a fact
    about the map codec, and a project is not paired with one until a build, so
    that check lives in `webfoot.build` alongside the same check for stats.
    """
    if not path.is_file():
        return {}

    document = _read_document(path)
    table = document.get("map")
    if not isinstance(table, Mapping):
        raise ProjectLoadError(f"{path}: missing required [map] table")

    records: dict[int, dict[str, Any]] = {}
    for key, entry in table.items():
        label = f"map.{key}"
        if not isinstance(entry, Mapping):
            raise ProjectLoadError(f"{path}: {label} must be a table")

        prefix, _, digits = key.partition(":")
        if prefix != "map" or not digits.isdigit():
            raise ProjectLoadError(
                f"{path}: {label} is not a valid map identity key; expected "
                'the form "map:0000"'
            )
        index = int(digits, 10)

        values: dict[str, Any] = {}
        for name in _MAP_FIELD_ORDER:
            values[name] = _require_int(entry, name, label, path)

        raw = entry.get("raw")
        if not isinstance(raw, str):
            raise ProjectValidationError(
                f"{path}: {label}.raw must be a hexadecimal string carrying the "
                "record's bytes; without it the record cannot be rebuilt"
            )
        try:
            values["raw"] = bytes.fromhex(raw)
        except ValueError as exc:
            raise ProjectValidationError(
                f"{path}: {label}.raw is not valid hex: {exc}"
            ) from exc

        # `slots` and `shape` travel together: an extent with no classification
        # would be unattributable, and a classification with no extent would
        # describe nothing. Refusing one without the other catches a hand-edit
        # that deleted half a pair.
        slots = entry.get("slots")
        shape = entry.get("shape")
        if (slots is None) != (shape is None):
            raise ProjectValidationError(
                f"{path}: {label} must declare both 'slots' and 'shape', or "
                "neither; one without the other describes nothing"
            )
        if slots is not None:
            if not isinstance(slots, str):
                raise ProjectValidationError(
                    f"{path}: {label}.slots must be a hexadecimal string"
                )
            try:
                values["slots"] = bytes.fromhex(slots)
            except ValueError as exc:
                raise ProjectValidationError(
                    f"{path}: {label}.slots is not valid hex: {exc}"
                ) from exc
            if not isinstance(shape, str):
                raise ProjectValidationError(
                    f"{path}: {label}.shape must be a string"
                )
            values["shape"] = shape

        placements = entry.get("placements")
        if placements is not None:
            if not isinstance(placements, dict):
                raise ProjectValidationError(
                    f"{path}: {label}.placements must be a table of records "
                    'keyed "placement:0000"'
                )
            parsed: list[dict[str, Any]] = []
            for placement_key, item in placements.items():
                item_label = f"{label}.placements.{placement_key}"
                kind, _, index_digits = str(placement_key).partition(":")
                if kind != "placement" or not index_digits.isdigit():
                    raise ProjectLoadError(
                        f"{path}: {item_label} is not a valid placement key; "
                        'expected the form "placement:0000"'
                    )
                if not isinstance(item, dict):
                    raise ProjectValidationError(
                        f"{path}: {item_label} must be a table"
                    )
                placement: dict[str, Any] = {
                    "index": int(index_digits, 10),
                    "position_low": _require_int(
                        item, "position_low", item_label, path
                    ),
                    "position_high": _require_int(
                        item, "position_high", item_label, path
                    ),
                }
                placement_raw = item.get("raw")
                if not isinstance(placement_raw, str):
                    raise ProjectValidationError(
                        f"{path}: {item_label}.raw must be a hexadecimal string "
                        "carrying the record's bytes; without it the record's "
                        "unknown words cannot be rebuilt"
                    )
                try:
                    placement["raw"] = bytes.fromhex(placement_raw)
                except ValueError as exc:
                    raise ProjectValidationError(
                        f"{path}: {item_label}.raw is not valid hex: {exc}"
                    ) from exc
                structural = {'descriptor', 'child_count', 'child_pointers_raw', 'record_size'}
                if structural & set(item):
                    if not structural <= set(item):
                        raise ProjectValidationError(f'{item_label}: incomplete placement structure')
                    children = item['child_pointers_raw']
                    if (not isinstance(item['descriptor'], str) or not item['descriptor'] or
                            not isinstance(children, list) or
                            any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF for v in children) or
                            type(item['child_count']) is not int or
                            item['child_count'] != len(children) or
                            type(item['record_size']) is not int):
                        raise ProjectValidationError(f'{item_label}: malformed child array or descriptor')
                    from ..formats.map_placements import PlacementRecord, MapPlacementError
                    try:
                        decoded = PlacementRecord.from_bytes(placement['raw'])
                    except MapPlacementError as exc:
                        raise ProjectValidationError(f'{item_label}: {exc}') from exc
                    if (tuple(children) != decoded.child_pointers_raw or
                            item['record_size'] != decoded.consumed_length):
                        raise ProjectValidationError(f'{item_label}: structural values differ from raw record')
                    placement.update({key: item[key] for key in structural})
                unknown = set(item) - {'position_low', 'position_high', 'raw'} - structural
                if unknown:
                    joined = ", ".join(sorted(unknown))
                    raise ProjectLoadError(
                        f"{path}: {item_label} has unknown fields: {joined}"
                    )
                parsed.append(placement)
            indices = [item["index"] for item in parsed]
            if len(set(indices)) != len(indices):
                raise ProjectLoadError(
                    f"{path}: {label} declares a placement index twice"
                )
            # Sorted on load as well as on write, so a hand-reordered file
            # rebuilds identically rather than depending on line order.
            values["placements"] = sorted(parsed, key=lambda item: item["index"])

        if "authored_placements" in entry:
            from .placements import parse_authored
            values["authored_placements"] = parse_authored(entry["authored_placements"], index)

        unexpected = (
            set(entry)
            - set(_MAP_FIELD_ORDER)
            - {"raw", "slots", "shape", "placements", "authored_placements"}
        )
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(f"{path}: {label} has unknown fields: {joined}")

        if index in records:
            raise ProjectLoadError(f"{path}: duplicate map identity map:{index:04d}")
        records[index] = values

    if not records:
        raise ProjectLoadError(f"{path}: [map] declares no records")
    return records


def write_layout_edits(directory: str | Path, layout: "LayoutEdits") -> Path:
    """Persist only the layout document for a loaded project.

    The narrow writer that mirrors `write_graphics_overrides`: the map authoring
    API validates before calling it, and it is the ONE place an authored layout
    reaches disk. An empty edit set means the project paints no layout, so the
    optional document is removed rather than written as an invalid empty table
    (which `read_project` would then refuse).
    """
    path = Path(directory) / LAYOUT_FILE
    if layout is None or layout.is_empty():
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_toml(layout.to_document()), encoding="utf-8", newline="\n")
    return path


def _read_graphics_overrides(path: Path) -> "GraphicsOverrides":
    """Load `graphics/overrides.toml`, or nothing at all if it is absent.

    Absence is legal and means the project authors no graphics edits. A file
    that exists but is malformed is still an error; "missing" and "wrong" are
    different answers, matching `_read_strings` and `_read_maps`.
    """
    if not path.is_file():
        return GraphicsOverrides()
    return GraphicsOverrides.from_document(_read_document(path), path)


def write_authored_chunks(directory: str | Path, chunks: "AuthoredChunks") -> Path:
    """Persist only the authored-chunk document for a loaded project.

    MAP-CHUNK-AUTHORING-001. The mirror of `write_layout_edits`: the chunk
    authoring API validates before calling it, and it is the ONE place an authored
    chunk reaches disk. An empty set means the project authors no chunk, so the
    optional document is removed rather than written as an invalid empty table
    (which `read_project` would then refuse).
    """
    path = Path(directory) / CHUNK_FILE
    if chunks is None or chunks.is_empty():
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_toml(chunks.to_document()), encoding="utf-8", newline="\n")
    return path


def _read_chunks(path: Path) -> "AuthoredChunks":
    """Load `maps/chunks.toml`, or nothing at all if it is absent.

    Absence is legal and means the project authors no chunks. A file that exists
    but is malformed is still an error; "missing" and "wrong" are different
    answers, matching `_read_layout` and `_read_strings`.
    """
    if not path.is_file():
        return AuthoredChunks()
    return AuthoredChunks.from_document(_read_document(path), path)


def _read_layout(path: Path) -> "LayoutEdits":
    """Load `maps/layout.toml`, or nothing at all if it is absent.

    Same three-state rule as every other optional subsystem: absent means the
    project paints no layout, present-and-valid means it does, and
    present-and-malformed is an error rather than an empty edit set.
    """
    if not path.is_file():
        return LayoutEdits()
    return LayoutEdits.from_document(_read_document(path), path)


def read_project(directory: str | Path) -> StatProject:
    """Load and structurally validate a project. Opens no ROM.

    Semantic validation against a base image happens in `webfoot.build`, which
    is the layer that has an image to validate against. Everything checkable
    from the text alone is checked here.
    """
    root = Path(directory)
    if not root.is_dir():
        raise ProjectLoadError(f"project directory does not exist: {root}")

    meta = ProjectMeta.from_document(_read_document(root / _PROJECT_FILE))
    enemies = _read_records(
        root / _ENEMY_FILE,
        "enemy",
        "enemy",
        _ENEMY_FIELD_ORDER,
        _ENEMY_FIXED_FIELDS,
        st.ENEMY_RECORD_SIZE,
    )
    characters = _read_records(
        root / _CHARACTER_FILE,
        "character",
        "character",
        _CHARACTER_FIELD_ORDER,
        _CHARACTER_FIXED_FIELDS,
        st.BASE_STAT_RECORD_SIZE,
    )

    for identity, values in enemies.items():
        if values["type_id"] != identity.key:
            raise ProjectValidationError(
                f"{root / _ENEMY_FILE}: enemy.{identity.key} declares type_id "
                f"{values['type_id']}; the identity key and type_id are the "
                "same fact and must agree"
            )

    strings = _read_strings(root / _TEXT_FILE)
    dialogues = _read_dialogues(root / _DIALOGUE_FILE)
    maps = _read_maps(root / _MAP_FILE)
    from .placements import validate_templates
    validate_templates(maps)

    events_path = root / 'events/placement_descriptors.json'
    events = None
    if events_path.exists():
        import json
        try:
            events = json.loads(events_path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            raise ProjectLoadError(f'{events_path}: invalid descriptor/event catalog: {exc}') from exc
        if not isinstance(events, dict):
            raise ProjectLoadError(f'{events_path}: descriptor/event catalog must be an object')

    layout = _read_layout(root / LAYOUT_FILE)
    chunks = _read_chunks(root / CHUNK_FILE)

    # MAP-CHUNK-AUTHORING-001. A layout cell that names an authored chunk must
    # name one this project declares. Checked here because it is the one place
    # both documents are in hand: `LayoutEdits` cannot see the chunk table, and a
    # project whose cell pointed at a chunk nobody declares would otherwise fail
    # at build time with a message about an image rather than about the file the
    # author has to fix.
    missing = sorted({
        value
        for value in layout.cells().values()
        if isinstance(value, str) and value not in chunks.chunks
    })
    if missing:
        raise ProjectValidationError(
            f"{root / LAYOUT_FILE}: names authored chunk(s) {missing}, which "
            f"{CHUNK_FILE} does not declare"
        )

    return StatProject(
        meta=meta,
        enemies=enemies,
        characters=characters,
        strings=strings,
        dialogues=dialogues,
        maps=maps,
        graphics_overrides=_read_graphics_overrides(root / GRAPHICS_OVERRIDES_FILE),
        layout=layout,
        chunks=chunks,
        placement_events=events,
        placement_types=(_read_document(root / PLACEMENT_TYPES_FILE)
                         if (root / PLACEMENT_TYPES_FILE).exists() else None),
    )
