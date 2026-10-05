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
from typing import Any, Iterable, Mapping

from ..formats import stat_tables as st
from ..formats import text_tables as tt
from ..formats.map_transitions import (
    ARRIVAL_UNSET_MINIMUM,
    FACING_MASK,
    MapTransitionError,
    TransitionRegion,
)
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
    #: MAP-RESIZE-AND-LAYERS-001. Authored map structure: resized layer grids and
    #: project-authored layer records. Empty for a project that authors none, which
    #: stays loadable on the same reasoning.
    structure: "MapStructure" = field(default_factory=lambda: MapStructure())
    #: MAP-WARP-PROJECT-AUTHORING-001. Authored map transitions: the destination and
    #: positional region of an existing selector-1 connection record. Empty for a
    #: project that authors none, which stays loadable on the same reasoning.
    transitions: "TransitionEdits" = field(default_factory=lambda: TransitionEdits())
    #: MAP-WARP-CREATE-PROJECT-001. Transitions this project CREATES - records the
    #: canonical image does not contain. A separate field rather than a second table
    #: of `transitions`, because a created record has no canonical index to key an
    #: edit by and the two documents have different writers. Empty for a project that
    #: creates none, which stays loadable on the same reasoning.
    transition_creations: "TransitionCreations" = field(
        default_factory=lambda: TransitionCreations()
    )
    #: SPRITE-NEW-PROJECT-SURFACE-001. New actor-sprite identities this project
    #: authors, each with the one map actor that draws it. Empty for a project that
    #: authors none, which stays loadable on the same reasoning as `strings`.
    sprites: "AuthoredSprites" = field(default_factory=lambda: AuthoredSprites())


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


#: MAP-RESIZE-AND-LAYERS-001. Project-authored **map structure**: the grid a
#: supported dominant layer's cells sit in, and the layer slots a project
#: activated with a new supported layer record.
#:
#: A fourth `maps/` document rather than fields of `layout.toml`, for the reason
#: `chunks.toml` is separate from it: a layout cell is a *reference* into a grid,
#: while a resize or an authored layer is the *grid and the record that holds it*.
#: The two have different lifetimes - a resize survives every cell being repainted
#: - and the reader refuses unknown keys, so folding a structural field into a
#: layout cell would make every existing project file ambiguous.
#:
#: A missing file means the project authors no structure, matching every other
#: optional subsystem, so a project extracted before this capability stays
#: loadable.
STRUCTURE_FILE = Path("maps") / "structure.toml"

#: The two authored structure identity forms, matched rather than trusted.
#:
#: ``map:NNNN/BGn`` names the **slot being resized** - the map by its durable
#: identity and the layer by BG slot, the same key `layout.toml` uses, so nothing
#: in the file is a file offset or a raw address. ``layer:name`` is a
#: project-authored layer's own durable identity, following the authored-chunk
#: precedent: lowercase, stable, and independent of any address, so a layer can be
#: created before a build has chosen where its record will live.
_STRUCTURE_MAP_LAYER = re.compile(r"^map:(\d{4})/BG([0-3])$")
_LAYER_IDENTITY = re.compile(r"^layer:([a-z][a-z0-9_-]{0,63})$")

#: The supported authored grid range, per axis.
#:
#: A dominant record states each axis in one unsigned byte, so 255 is the
#: encoding ceiling. This is a **policy** limit well below it and is stated here as
#: one: the canonical corpus's largest dominant grid is 5x5, and nothing has
#: established how large a grid the engine's own per-layer upload loop tolerates.
#: `test_map_structure_project` pins it against
#: `formats.map_graphics.MAX_LAYER_GRID_SIDE` so the two cannot drift.
_MAX_GRID_SIDE = 8


@dataclass(frozen=True)
class LayerResize:
    """One authored change to a supported dominant layer's chunk grid.

    Semantic and address-free: the map is named by ``map:NNNN``, the layer by BG
    slot, the new grid in whole chunks, and the initialization for the cells the
    growth adds by **the same value form a layout cell uses** - a 1-based ordinal
    into the layer's own existing chunk vocabulary, or the identity of a
    project-authored chunk. Nothing here is an offset, an address or a byte.

    Growth only: ``columns`` and ``rows`` are each at least the retail grid's, so
    the transform is fully determined (top-left anchored, old cell ``(x, y)`` at
    new cell ``(x, y)``) and no authored cell is ever dropped.
    """

    map_index: int
    layer_slot: int
    columns: int
    rows: int
    #: The chunk every cell the growth adds is initialized to. A layout cell and
    #: this field accept exactly the same two forms, so the author's vocabulary is
    #: one thing rather than two.
    fill: int | str

    @staticmethod
    def key_for(map_index: int, layer_slot: int) -> str:
        """The durable identity key for one resized layer."""
        return f"map:{map_index:04d}/BG{layer_slot}"

    @property
    def key(self) -> str:
        return LayerResize.key_for(self.map_index, self.layer_slot)

    @property
    def slots(self) -> str:
        return f"BG{self.layer_slot}"

    @property
    def owner(self) -> str:
        return self.key

    def to_document(self) -> dict[str, Any]:
        return {"columns": self.columns, "rows": self.rows, "fill": self.fill}

    @classmethod
    def from_document(
        cls, key: object, document: object, where: object
    ) -> "LayerResize":
        match = _STRUCTURE_MAP_LAYER.match(key if isinstance(key, str) else "")
        if match is None:
            raise ProjectLoadError(
                f"{where}: resize.{key} is not a layer identity; expected "
                "'map:NNNN/BGn' with four digits and a 0..3 slot"
            )
        unknown = set(document) - {"columns", "rows", "fill"} if isinstance(document, dict) else None
        if unknown is None:
            raise ProjectLoadError(f"{where}: resize.{key} must be a table")
        if unknown:
            raise ProjectLoadError(
                f"{where}: resize.{key} declares unknown key(s) {sorted(unknown)}"
            )
        return cls(
            map_index=int(match.group(1), 10),
            layer_slot=int(match.group(2), 10),
            columns=_require_grid_side(document.get("columns"), f"resize.{key}", where),
            rows=_require_grid_side(document.get("rows"), f"resize.{key}", where),
            fill=_require_fill(document.get("fill"), f"resize.{key}", where),
        )


@dataclass(frozen=True)
class AuthoredLayer:
    """One project-authored supported layer, activating a map's unused slot.

    The engine's layer count is **fixed at four**: a map root carries exactly four
    layer-slot pointers, all non-null on all 452 canonical roots, and an unused
    slot points at one shared zero-dimension placeholder record. "Create a new
    layer" therefore means exactly what the engine can actually do - point an
    unused slot at a new dominant record - and this class models that rather than
    inventing a dynamic layer list the engine does not possess.

    ``template`` names the canonical layer the new record's header is copied from,
    as ``map:NNNN/BGn``. It is resolved against the **canonical** image only, so
    editing the authored layer can never re-point the template that named it.
    """

    identity: str
    map_index: int
    layer_slot: int
    template: str
    columns: int
    rows: int
    fill: int | str

    def __post_init__(self) -> None:
        # Typed refusals, not the TypeErrors a regex would raise on a non-string: a
        # malformed document is a project error, and CQA-06 requires an expected
        # refusal to cross a caller's boundary as the declared family.
        if not isinstance(self.identity, str) or _LAYER_IDENTITY.match(self.identity) is None:
            raise ProjectValidationError(
                f"authored layer identity {self.identity!r} is not 'layer:<name>'"
            )
        match = (
            _STRUCTURE_MAP_LAYER.match(self.template)
            if isinstance(self.template, str)
            else None
        )
        if match is None:
            raise ProjectValidationError(
                f"{self.identity}: template {self.template!r} is not "
                "'map:NNNN/BGn'"
            )
        if int(match.group(1), 10) != self.map_index:
            raise ProjectValidationError(
                f"{self.identity}: template {self.template!r} names another map; "
                "an authored layer's screen-entry ordinals resolve through its own "
                "map's assembled character block, so it is map-scoped"
            )
        if int(match.group(2), 10) == self.layer_slot:
            raise ProjectValidationError(
                f"{self.identity}: template {self.template!r} is the slot it would "
                "activate"
            )
        if not 0 <= self.layer_slot < _LAYER_SLOT_COUNT:
            raise ProjectValidationError(
                f"{self.identity}: slot {self.layer_slot} is outside "
                f"BG0..BG{_LAYER_SLOT_COUNT - 1}"
            )

    @property
    def owner(self) -> str:
        return self.identity

    @property
    def template_map(self) -> int:
        return int(_STRUCTURE_MAP_LAYER.match(self.template).group(1), 10)

    @property
    def template_slot(self) -> int:
        return int(_STRUCTURE_MAP_LAYER.match(self.template).group(2), 10)

    def to_document(self) -> dict[str, Any]:
        return {
            "map": f"map:{self.map_index:04d}",
            "slot": self.layer_slot,
            "template": self.template,
            "columns": self.columns,
            "rows": self.rows,
            "fill": self.fill,
        }

    @classmethod
    def from_document(
        cls, identity: object, document: object, where: object
    ) -> "AuthoredLayer":
        if not isinstance(identity, str) or _LAYER_IDENTITY.match(identity) is None:
            raise ProjectLoadError(
                f"{where}: {identity!r} is not a 'layer:<name>' identity"
            )
        if not isinstance(document, dict):
            raise ProjectLoadError(f"{where}: layer.{identity} must be a table")
        required = {"map", "slot", "template", "columns", "rows", "fill"}
        unknown = set(document) - required
        if unknown:
            raise ProjectLoadError(
                f"{where}: layer.{identity} declares unknown key(s) {sorted(unknown)}"
            )
        missing = required - set(document)
        if missing:
            raise ProjectLoadError(
                f"{where}: layer.{identity} is missing key(s) {sorted(missing)}"
            )
        map_key = document["map"]
        match = _MAP_KEY.match(str(map_key))
        if match is None:
            raise ProjectLoadError(
                f"{where}: layer.{identity}.map is not 'map:NNNN'"
            )
        slot = document["slot"]
        if type(slot) is not int or not 0 <= slot < _LAYER_SLOT_COUNT:
            raise ProjectValidationError(
                f"{where}: layer.{identity}.slot is not a BG slot"
            )
        return cls(
            identity=identity,
            map_index=int(str(map_key)[4:], 10),
            layer_slot=slot,
            template=str(document["template"]),
            columns=_require_grid_side(document["columns"], f"layer.{identity}", where),
            rows=_require_grid_side(document["rows"], f"layer.{identity}", where),
            fill=_require_fill(document["fill"], f"layer.{identity}", where),
        )


def _require_grid_side(value: object, label: str, where: object) -> int:
    if type(value) is not int:
        raise ProjectValidationError(f"{where}: {label} needs a whole chunk count")
    if not 1 <= value <= _MAX_GRID_SIDE:
        raise ProjectValidationError(
            f"{where}: {label} states {value} chunks on one axis; the supported "
            f"range is 1..{_MAX_GRID_SIDE}"
        )
    return value


def _require_fill(value: object, label: str, where: object) -> int | str:
    """The initialization form a structural edit shares with a layout cell."""
    if isinstance(value, str):
        if _CHUNK_IDENTITY.match(value) is None:
            raise ProjectValidationError(
                f"{where}: {label}.fill names {value!r}, which is neither a chunk "
                "ordinal nor a 'chunk:<name>' authored chunk"
            )
        return value
    if type(value) is not int:
        raise ProjectValidationError(
            f"{where}: {label}.fill must be a chunk ordinal or an authored chunk "
            f"identity, got {value!r}"
        )
    if value < 1:
        raise ProjectValidationError(
            f"{where}: {label}.fill names chunk {value}; ordinals are 1-based"
        )
    return value


def _validate_slot_claims(
    resizes: Iterable["LayerResize"],
    layers: Iterable["AuthoredLayer"],
    where: object,
) -> None:
    """One slot, one owner - except a created layer and the resize that grows it.

    ``layers`` CREATES a layer record in a slot the canonical image leaves unused
    and declares the grid it is created at; ``resizes`` changes the grid of a
    layer that already exists. Two records claiming one slot would each look valid
    alone and one would silently win at build time - the "authored but not
    applied" failure this format exists to prevent - so two ``[layer]`` entries on
    one slot and two ``[resize]`` entries on one slot are each refused.

    A ``[layer]`` and a ``[resize]`` on ONE slot are the single exception, and
    only in one direction: the layer was created at the grid the ``[layer]`` entry
    declares and then grew to the grid the ``[resize]`` entry declares. That is
    one slot's worth of authored structure rather than two claims to it, and it is
    the only way the format can express "grow a layer the project itself created".
    A resize that does not in fact grow the layer - smaller on either axis, or
    unchanged - is refused here rather than left to a build that would silently
    drop the authored cells the smaller grid cannot hold.
    """
    resized: dict[tuple[int, int], LayerResize] = {}
    for resize in resizes:
        slot = (resize.map_index, resize.layer_slot)
        previous = resized.get(slot)
        if previous is not None:
            raise ProjectValidationError(
                f"{where}: map:{resize.map_index:04d}/BG{resize.layer_slot} is "
                f"claimed by both {previous.owner} and {resize.owner}"
            )
        resized[slot] = resize

    authored: dict[tuple[int, int], AuthoredLayer] = {}
    for layer in layers:
        slot = (layer.map_index, layer.layer_slot)
        previous = authored.get(slot)
        if previous is not None:
            raise ProjectValidationError(
                f"{where}: map:{layer.map_index:04d}/BG{layer.layer_slot} is "
                f"claimed by both {previous.owner} and {layer.owner}"
            )
        authored[slot] = layer

    for slot, layer in authored.items():
        resize = resized.get(slot)
        if resize is None:
            continue
        if (
            resize.columns < layer.columns
            or resize.rows < layer.rows
            or (resize.columns, resize.rows) == (layer.columns, layer.rows)
        ):
            raise ProjectValidationError(
                f"{where}: map:{layer.map_index:04d}/BG{layer.layer_slot} declares "
                f"the project-authored layer {layer.owner} at {layer.columns}x"
                f"{layer.rows} and a resize to {resize.columns}x{resize.rows}; a "
                "resize on an authored layer states the grid it is GROWN to, so it "
                "must be larger on at least one axis and smaller on neither"
            )


@dataclass(frozen=True)
class MapStructure:
    """A project's authored map structure: resized grids and authored layers.

    Two tables with one job each. ``layers`` creates a layer record in a slot the
    canonical image leaves unused and declares the grid it is created at;
    ``resizes`` changes the grid of a layer that already exists - a retail
    layer's, or the project's own. A slot carries one claim: two ``[layer]``
    entries or two ``[resize]`` entries for one slot are refused, and so is a
    resize that does not in fact grow the authored layer it names.

    ``[layer]`` and ``[resize]`` together on one slot mean **one** thing: the
    layer was created at the grid the ``[layer]`` entry declares and then grown to
    the grid the ``[resize]`` entry declares. The two are kept rather than the
    pair being collapsed into one grown layer, because they are different facts -
    the grid the project created the layer at and the grid it is emitted in - and
    a reviewer has to be able to tell an authored layer's resize from a retail
    layer's.
    """

    #: ``"map:NNNN/BGn"`` -> the resize of that layer.
    resizes: dict[str, LayerResize] = field(default_factory=dict)
    #: ``"layer:name"`` -> a project-authored layer record.
    layers: dict[str, AuthoredLayer] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # The invariant is checked on construction as well as on load, so a caller
        # cannot assemble a document its own reader would refuse and hand it to
        # `write_map_structure` - the same reason `AuthoredLayer` validates its own
        # fields in `__post_init__`. It is also what makes "two `[resize]` entries
        # for one slot" a refusal at all: the two resize keys of one slot are the
        # same string, so a duplicated claim can only be built as a dict whose two
        # values name one slot.
        _validate_slot_claims(
            self.resizes.values(), self.layers.values(), STRUCTURE_FILE
        )

    def is_empty(self) -> bool:
        return not self.resizes and not self.layers

    def resize_for(self, map_index: int, layer_slot: int) -> LayerResize | None:
        return self.resizes.get(LayerResize.key_for(map_index, layer_slot))

    def layer_at(self, map_index: int, layer_slot: int) -> AuthoredLayer | None:
        for layer in self.layers.values():
            if layer.map_index == map_index and layer.layer_slot == layer_slot:
                return layer
        return None

    def layer(self, identity: str) -> AuthoredLayer | None:
        return self.layers.get(identity)

    def structural_slots(self) -> frozenset[tuple[int, int]]:
        """Every ``(map index, layer slot)`` whose content this document owns."""
        return frozenset(
            [(item.map_index, item.layer_slot) for item in self.resizes.values()]
            + [(item.map_index, item.layer_slot) for item in self.layers.values()]
        )

    def to_document(self) -> dict[str, Any]:
        document: dict[str, Any] = {}
        if self.resizes:
            document["resize"] = {
                key: item.to_document() for key, item in sorted(self.resizes.items())
            }
        if self.layers:
            document["layer"] = {
                key: item.to_document() for key, item in sorted(self.layers.items())
            }
        return document

    @classmethod
    def from_document(cls, document: object, where: object) -> "MapStructure":
        if not isinstance(document, dict):
            raise ProjectLoadError(f"{where}: must be a table")
        unknown = set(document) - {"resize", "layer"}
        if unknown:
            raise ProjectLoadError(
                f"{where}: unknown top-level key(s) {sorted(unknown)}"
            )
        if not document:
            raise ProjectLoadError(f"{where}: declares no structural edits")

        resizes: dict[str, LayerResize] = {}
        table = document.get("resize")
        if table is not None:
            if not isinstance(table, dict) or not table:
                raise ProjectLoadError(f"{where}: [resize] declares no edits")
            for key, value in table.items():
                if key in resizes:
                    raise ProjectLoadError(f"{where}: duplicate resize {key!r}")
                resizes[key] = LayerResize.from_document(key, value, where)

        layers: dict[str, AuthoredLayer] = {}
        table = document.get("layer")
        if table is not None:
            if not isinstance(table, dict) or not table:
                raise ProjectLoadError(f"{where}: [layer] declares no edits")
            for identity, value in table.items():
                if identity in layers:
                    raise ProjectLoadError(f"{where}: duplicate layer {identity!r}")
                layers[identity] = AuthoredLayer.from_document(identity, value, where)

        # One slot, one owner - except a project-authored layer and the resize that
        # grows it, which are one slot's worth of authored structure and not two
        # claims to it. Checked here, before construction, so the refusal names the
        # document the author has to fix.
        _validate_slot_claims(resizes.values(), layers.values(), where)
        return cls(
            resizes=dict(sorted(resizes.items())),
            layers=dict(sorted(layers.items())),
        )


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


#: MAP-WARP-PROJECT-AUTHORING-001. Authored **map transitions**: the destination
#: and the positional region of an existing selector-1 connection record.
#:
#: A fifth `maps/` document rather than fields of `layout.toml`, for the reason
#: `structure.toml` is separate from it: a transition is not a map's layout but one
#: of the map's *connections*, named by the source map plus the index of the record
#: in that map's own array, and it is authored with a different vocabulary from a
#: chunk cell. A missing file means the project authors no transitions, matching
#: every other optional subsystem, so a project extracted before this capability
#: stays loadable.
TRANSITION_FILE = Path("maps") / "transitions.toml"


def _region_document(region: TransitionRegion) -> list[list[int]]:
    """One stored region: two ordered ``[low, high]`` intervals, positionally."""
    return [list(region.first), list(region.second)]


def _region_from_document(value: object, where: object) -> TransitionRegion:
    """Parse one stored region, validating it through the record codec itself.

    The rule "two ordered, non-degenerate ``u16`` intervals" is stated once, in
    `formats.map_transitions.TransitionRegion`, and this constructs that type - so a
    project file cannot carry a region the build would refuse, and the project
    format does not restate a format rule it does not own.
    """
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ProjectLoadError(
            f"{where}: a region must be two [low, high] intervals, got {value!r}"
        )
    pairs: list[tuple[int, int]] = []
    for position, pair in enumerate(value):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ProjectLoadError(
                f"{where}: region interval {position} must be a [low, high] pair, "
                f"got {pair!r}"
            )
        low, high = pair
        if type(low) is not int or type(high) is not int:
            raise ProjectValidationError(
                f"{where}: region interval {position} endpoints must be integers, "
                f"got {low!r} and {high!r}"
            )
        pairs.append((low, high))
    try:
        return TransitionRegion(first=pairs[0], second=pairs[1])
    except MapTransitionError as exc:
        raise ProjectValidationError(f"{where}: {exc}") from exc


def _optional_map_key(document: Mapping[str, Any], name: str, where: object) -> str | None:
    """One stored map identity, or None when the field is absent.

    A present value that is not a map identity is a *value* error, not a document
    structure error: the file is well-formed TOML that names something this format
    does not have, and the author has to fix the value rather than the shape.
    """
    if name not in document:
        return None
    value = document[name]
    if not isinstance(value, str) or _MAP_KEY.match(value) is None:
        raise ProjectValidationError(
            f"{where}: {name} is {value!r}, which is not a 'map:NNNN' map identity"
        )
    return value


def _optional_region(
    document: Mapping[str, Any], name: str, where: object
) -> TransitionRegion | None:
    """One stored region, or None when the field is absent."""
    if name not in document:
        return None
    return _region_from_document(document[name], f"{where}.{name}")


@dataclass(frozen=True, slots=True)
class AuthoredTransition:
    """One transition a project authors, and what each edited field started from.

    The identity is the document's own position, not a field:
    ``[transition."map:0039"."0001"]`` names the source map by the durable key
    `maps/maps.toml` uses, and the transition by its index in that map's own
    ``root + 0x44`` array - the position the engine's own walk assigns. Nothing here
    is a file offset or a raw address.

    Each editable field group is stored as a prior/authored pair, and either group
    may be absent:

    * the **destination** is the durable ``map:NNNN`` key of the map the transition
      leads to - exactly the value the engine's own two-byte lookup resolves, not
      the two record bytes and not an address;
    * the **region** is the record's four ``u16`` endpoints as two ordered
      intervals. Which interval is horizontal, and what the endpoints' unit is, are
      UNRESOLVED, so the file stores them positionally and invents no axis name;
    * the ``prior_*`` values are what the canonical record held. The build checks
      every one of them before it writes, so a project authored against a different
      image is refused rather than reinterpreted, and the document itself proves the
      base it was authored against - the same role `AuthoredChunkEntry.prior` plays.

    **No record bytes are stored, deliberately.** The unresolved bytes of the 24-byte
    record - the class word, the invariant word and the five engine-read fields whose
    meaning is UNRESOLVED - are preserved by coming from the canonical transition
    authority at build time and never from this file. Storing them would be a second
    copy of the ROM that could disagree with the first.
    """

    prior_destination: str | None = None
    destination: str | None = None
    prior_region: TransitionRegion | None = None
    region: TransitionRegion | None = None
    #: MAP-WARP-RUNTIME-EDIT-001. The measured arrival point, as ``[x, y]``.
    #: ``arrival_authored`` separates "the project sets no arrival" from "the
    #: author did not touch the arrival", because both values are None in the
    #: first case and only that flag says so.
    prior_arrival: tuple[int, int] | None = None
    arrival: tuple[int, int] | None = None
    arrival_authored: bool = False
    #: MAP-WARP-ARRIVAL-SEMANTICS-001. The ``+0x10`` byte, stored WHOLE rather
    #: than as a direction: its low two bits are the candidate facing decode and
    #: its high bits are UNRESOLVED, so a record carrying them must round-trip
    #: verbatim instead of losing them to a direction-only field.
    prior_facing_raw: int | None = None
    facing_raw: int | None = None
    facing_authored: bool = False

    def __post_init__(self) -> None:
        for prior, authored, label in (
            (self.prior_destination, self.destination, "destination"),
            (self.prior_region, self.region, "region"),
        ):
            if (prior is None) != (authored is None):
                raise ProjectValidationError(
                    f"an authored transition must state the {label} it started from "
                    f"and the {label} it authors together; got {prior!r} and {authored!r}"
                )
        for value, label in (
            (self.prior_arrival, "prior_arrival"),
            (self.arrival, "arrival"),
        ):
            if value is None:
                continue
            if (
                not isinstance(value, (list, tuple))
                or len(value) != 2
                or any(type(part) is not int or not 0 <= part < ARRIVAL_UNSET_MINIMUM
                       for part in value)
            ):
                raise ProjectValidationError(
                    f"an authored transition's {label} is {value!r}, which is not an "
                    "[x, y] pair below the measured unset sentinel"
                )
        if not self.arrival_authored and (
            self.prior_arrival is not None or self.arrival is not None
        ):
            raise ProjectValidationError(
                "an authored transition states an arrival without marking the "
                "arrival group as authored"
            )
        for value, label in (
            (self.prior_facing_raw, "prior_facing_raw"),
            (self.facing_raw, "facing_raw"),
        ):
            if value is None:
                continue
            if type(value) is not int or not 0 <= value <= 0xFF:
                raise ProjectValidationError(
                    f"an authored transition's {label} is {value!r}, which is not a "
                    "single byte"
                )
        if not self.facing_authored and (
            self.prior_facing_raw is not None or self.facing_raw is not None
        ):
            raise ProjectValidationError(
                "an authored transition states a facing without marking the facing "
                "group as authored"
            )
        for value, label in (
            (self.prior_destination, "prior_destination"),
            (self.destination, "destination"),
        ):
            if value is not None and _MAP_KEY.match(value) is None:
                raise ProjectValidationError(
                    f"an authored transition's {label} is {value!r}, which is not a "
                    "'map:NNNN' map identity"
                )
        if (
            self.destination is None
            and self.region is None
            and not self.arrival_authored
            and not self.facing_authored
        ):
            raise ProjectValidationError(
                "an authored transition must author a destination, a region, an "
                "arrival, a facing, or a combination"
            )

    def is_noop(self) -> bool:
        """Whether every stored pair authors the value it started from.

        A stored pair that authors its own prior is legal and meaningful - it is how
        a project states "leave this field exactly as the base has it" - but it is
        not an edit, and the build emits nothing for it.
        """
        return (
            (self.destination is None or self.destination == self.prior_destination)
            and (self.region is None or self.region == self.prior_region)
            and (
                not self.arrival_authored
                or tuple(self.arrival or ()) == tuple(self.prior_arrival or ())
            )
            and (not self.facing_authored or self.facing_raw == self.prior_facing_raw)
        )

    def to_document(self) -> dict[str, Any]:
        document: dict[str, Any] = {}
        if self.destination is not None:
            document["prior_destination"] = self.prior_destination
            document["destination"] = self.destination
        if self.region is not None:
            document["prior_region"] = _region_document(self.prior_region)
            document["region"] = _region_document(self.region)
        if self.arrival_authored:
            document["arrival_authored"] = True
            document["prior_arrival"] = (
                list(self.prior_arrival) if self.prior_arrival is not None else None
            )
            document["arrival"] = (
                list(self.arrival) if self.arrival is not None else None
            )
        if self.facing_authored:
            document["facing_authored"] = True
            document["prior_facing_raw"] = self.prior_facing_raw
            document["facing_raw"] = self.facing_raw
        return document

    @classmethod
    def from_document(cls, document: object, where: object) -> "AuthoredTransition":
        if not isinstance(document, Mapping):
            raise ProjectLoadError(f"{where}: an authored transition must be a table")
        unknown = set(document) - {
            "prior_destination",
            "destination",
            "prior_region",
            "region",
            "prior_arrival",
            "arrival",
            "arrival_authored",
            "prior_facing_raw",
            "facing_raw",
            "facing_authored",
        }
        if unknown:
            raise ProjectLoadError(
                f"{where}: unknown key(s) {sorted(unknown)}; an authored transition "
                "authors a destination, a region, an arrival and/or a facing, each "
                "as a prior/authored pair"
            )
        try:
            return cls(
                prior_destination=_optional_map_key(document, "prior_destination", where),
                destination=_optional_map_key(document, "destination", where),
                prior_region=_optional_region(document, "prior_region", where),
                region=_optional_region(document, "region", where),
                prior_arrival=_optional_point(document.get("prior_arrival"), where, "prior_arrival"),
                arrival=_optional_point(document.get("arrival"), where, "arrival"),
                arrival_authored=bool(document.get("arrival_authored", False)),
                prior_facing_raw=_optional_byte(
                    document.get("prior_facing_raw"), where, "prior_facing_raw"
                ),
                facing_raw=_optional_byte(document.get("facing_raw"), where, "facing_raw"),
                facing_authored=bool(document.get("facing_authored", False)),
            )
        except ProjectValidationError as exc:
            raise ProjectValidationError(f"{where}: {exc}") from exc


def _optional_byte(value: object, where: object, name: str) -> int | None:
    """One stored byte, or None when the key is absent or null."""
    if value is None:
        return None
    if type(value) is not int or not 0 <= value <= 0xFF:
        raise ProjectValidationError(
            f"{where}: {name} must be a byte or absent, got {value!r}"
        )
    return value


def _optional_point(value: object, where: object, name: str) -> tuple[int, int] | None:
    """One stored ``[x, y]`` arrival, or None when the key is absent/None."""
    if value is None:
        return None
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ProjectLoadError(
            f"{where}: {name} must be an [x, y] pair or absent, got {value!r}"
        )
    x, y = value
    if type(x) is not int or type(y) is not int:
        raise ProjectValidationError(
            f"{where}: {name} endpoints must be integers, got {x!r} and {y!r}"
        )
    return (x, y)


@dataclass(frozen=True)
class TransitionEdits:
    """Authored map transitions, keyed by source map and index in that map's array.

    ``transitions["map:0039"][1]`` reads "map 39's second transition". Two
    properties make that a semantic authoring value rather than a disguised offset:

    * the map is named by its durable identity (``map:NNNN``, the same key
      ``maps/maps.toml`` uses) and the transition by its index in the map's own
      array - never by the record's ROM address;
    * the destination is the destination map's own durable key and the region is
      four positional endpoints, so the same project file resolves identically on
      every machine and after any reopen.

    A record address is deliberately NOT storable. An address names where one record
    sits in one image; the source map plus the array index names *which transition
    it is*, and survives any rebuild that keeps the array in order - the same choice
    `LayoutEdits` and `PlacementIdentity` make.
    """

    #: ``"map:NNNN"`` -> index in that map's own transition array -> the entry.
    maps: dict[str, dict[int, AuthoredTransition]] = field(default_factory=dict)

    @staticmethod
    def key_for(index: int) -> str:
        """The durable identity key for a map table index."""
        return f"map:{index:04d}"

    def is_empty(self) -> bool:
        return not any(entries for entries in self.maps.values())

    def edits(self) -> dict[tuple[int, int], AuthoredTransition]:
        """Flatten to ``{(source map index, transition index): entry}``.

        The one place the ``map:NNNN`` key is turned back into an index, so every
        caller reads the identity form the same way. A key that is not that form
        cannot occur: `from_document` refuses anything else.
        """
        flat: dict[tuple[int, int], AuthoredTransition] = {}
        for key, entries in self.maps.items():
            index = int(key[4:], 10)
            for position, entry in entries.items():
                flat[(index, position)] = entry
        return flat

    @classmethod
    def from_edits(
        cls, edits: Mapping[tuple[int, int], AuthoredTransition]
    ) -> "TransitionEdits":
        """Build the document form from ``{(map index, transition index): entry}``.

        The inverse of :meth:`edits` and the only way an authored set reaches this
        type from the authoring API, so the two directions cannot disagree about
        what a key means.
        """
        maps: dict[str, dict[int, AuthoredTransition]] = {}
        for (map_index, position), entry in sorted(edits.items()):
            maps.setdefault(cls.key_for(map_index), {})[position] = entry
        return cls(maps=maps)

    def for_map(self, index: int) -> dict[int, AuthoredTransition]:
        """Transition index -> entry for one map, empty when it authors none."""
        return dict(self.maps.get(TransitionEdits.key_for(index), {}))

    def to_document(self) -> dict[str, Any]:
        """The `[transition]` table: map, then transition index.

        Both levels are keyed by a zero-padded integer, so lexical order is numeric
        order and the file is deterministic without the writer having to sort
        anything. Each level is emitted sorted for that reason.
        """
        return {
            "transition": {
                key: {
                    f"{position:04d}": entry.to_document()
                    for position, entry in sorted(entries.items())
                }
                for key, entries in sorted(self.maps.items())
            }
        }

    @classmethod
    def from_document(cls, document: Mapping[str, Any], where: object) -> "TransitionEdits":
        table = document.get("transition")
        if table is None:
            raise ProjectLoadError(f"{where}: missing required [transition] table")
        if not isinstance(table, Mapping):
            raise ProjectLoadError(f"{where}: [transition] must be a table")
        maps: dict[str, dict[int, AuthoredTransition]] = {}
        for map_key, entries in table.items():
            label = f"transition.{map_key}"
            if not _MAP_KEY.match(str(map_key)):
                raise ProjectLoadError(
                    f"{where}: {label} is not a valid map identity; expected "
                    "'map:NNNN' with four digits"
                )
            if not isinstance(entries, Mapping):
                raise ProjectLoadError(f"{where}: {label} must be a table")
            by_position: dict[int, AuthoredTransition] = {}
            for position_key, entry in entries.items():
                # A key that is not an index would otherwise be silently dropped
                # from the build - the "authored but not applied" failure this
                # format exists to prevent.
                if not str(position_key).isdigit():
                    raise ProjectLoadError(
                        f"{where}: {label}.{position_key} is not a transition index; "
                        "expected a zero-padded integer key"
                    )
                position = int(position_key, 10)
                if position in by_position:
                    raise ProjectLoadError(
                        f"{where}: {label} declares transition {position} twice"
                    )
                by_position[position] = AuthoredTransition.from_document(
                    entry, f"{where}: {label}.{position_key}"
                )
            if not by_position:
                raise ProjectLoadError(f"{where}: {label} declares no transitions")
            if map_key in maps:
                raise ProjectLoadError(f"{where}: duplicate map {map_key}")
            maps[map_key] = by_position
        if not maps:
            raise ProjectLoadError(f"{where}: [transition] declares no edits")
        return cls(maps=maps)


#: MAP-WARP-CREATE-PROJECT-001. Authored **created** map transitions: a selector-1
#: connection record the canonical image does not contain.
#:
#: A sixth `maps/` document rather than a second table of `transitions.toml`, for a
#: reason of write semantics rather than taste: `write_transition_edits` *deletes*
#: that document when the last edit is removed, so a creation stored beside an edit
#: would be destroyed by an author undoing an unrelated retarget. One document, one
#: authoring concern - the same reasoning that keeps `structure.toml` separate from
#: `layout.toml`.
#:
#: The durable identity is ``map:NNNN/transition:<name>``: the source map's own key
#: plus an authored name. It deliberately contains **no** address and **no** array
#: index, because the index a created record ends up at does not exist until the
#: build appends it. A missing file means the project creates no transition,
#: matching every other optional subsystem.
TRANSITION_CREATION_FILE = Path("maps") / "transition_creations.toml"

#: The document's one table: ``[creation."map:NNNN"."<name>"]``.
TRANSITION_CREATION_TABLE = "creation"

#: An authored transition name. The same shape a chunk name takes, for the same
#: reason: it becomes part of a durable identity a project file and a manifest both
#: carry, so it stays lowercase, bounded and free of path or separator characters.
_TRANSITION_NAME = re.compile(r"[a-z][a-z0-9_-]{0,63}$")

#: ``map:NNNN/transition:<name>`` - a created transition's durable identity.
_CREATED_TRANSITION_IDENTITY = re.compile(
    r"map:(\d{4})/transition:([a-z][a-z0-9_-]{0,63})$"
)

#: ``map:NNNN/transition:IIII`` - the canonical transition a creation copies.
_TRANSITION_TEMPLATE_KEY = re.compile(r"map:(\d{4})/transition:(\d{4})$")


def transition_creation_identity(map_index: int, name: str) -> str:
    """A created transition's durable identity: ``map:NNNN/transition:<name>``."""
    return f"map:{map_index:04d}/transition:{name}"


def parse_transition_creation_identity(value: object, where: object) -> tuple[int, str]:
    """Split a ``map:NNNN/transition:<name>`` identity into its two parts."""
    if not isinstance(value, str):
        raise ProjectValidationError(
            f"{where}: a created-transition identity must be a string, got {value!r}"
        )
    match = _CREATED_TRANSITION_IDENTITY.match(value)
    if match is None:
        raise ProjectValidationError(
            f"{where}: {value!r} is not a 'map:NNNN/transition:<name>' identity; the "
            "name is lowercase, starts with a letter, and uses only letters, digits, "
            "'_' and '-'"
        )
    return int(match.group(1), 10), match.group(2)


@dataclass(frozen=True, slots=True)
class AuthoredTransitionCreation:
    """One transition a project creates, and the canonical record it starts from.

    A created record has no canonical bytes, so its *initialization* has to come
    from somewhere the engine already trusts. It comes from ``template``: a
    ``map:NNNN/transition:IIII`` identity naming an existing **566-class** record of
    the SAME source map. The build copies three things from it and authors the rest:

    * **authored by the project** - the region, the destination map and the arrival
      pair;
    * **copied from the template** - the class/constructor word at ``+0x00`` and the
      invariant word at ``+0x04``, whose meanings are UNRESOLVED, so they are carried
      rather than invented;
    * **preserved from the template** - the engine-read byte at ``+0x13`` and the
      low nibble of ``+0x10`` (the door gate bits and the two bits nothing was traced
      reading). These are pinned in the document as ``prior_unresolved_raw`` and
      ``prior_facing_raw`` so an image whose template changed is refused instead of
      silently initializing the new record from different unresolved bytes.
    ``facing`` is the authored arrival-facing override, or ``None`` for "this record
    states none" - the engine's own "keep walking the way you were" state, which is a
    value and not a missing one. The template's own override is deliberately NOT
    inherited: it was a decision about a different door.

    No record bytes are stored, for the reason `AuthoredTransition` gives: the
    document names the template and the fields it authors, and the build resolves
    everything else from the canonical image.
    """

    #: ``map:NNNN`` - the map the created transition belongs to.
    source: str
    name: str
    #: ``map:NNNN/transition:IIII`` - the canonical 566-class record copied.
    template: str
    #: ``map:NNNN`` - the map the created transition leads to.
    destination: str
    region: TransitionRegion
    #: The arrival point in the destination, as ``[x, y]``.
    arrival: tuple[int, int]
    #: The template's own ``+0x10`` byte, whole. The created record keeps its low
    #: nibble and takes the high nibble from :attr:`facing`.
    prior_facing_raw: int
    #: The template's own ``+0x13`` byte, which the created record carries verbatim.
    #: Named for its STATUS rather than for a guessed meaning: it is an engine-read
    #: byte (``0x08007282``) whose semantics are UNRESOLVED, so the document records
    #: the value it inherits without claiming to know what it is - and deliberately
    #: without putting the field's offset in a project's key name.
    prior_unresolved_raw: int
    #: The direction the player is forced to face on arrival (0..3), or None for "no
    #: override stated". Never the template's own override.
    facing: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or _MAP_KEY.match(self.source) is None:
            raise ProjectValidationError(
                f"a created transition's source is {self.source!r}, which is not a "
                "'map:NNNN' map identity"
            )
        if _TRANSITION_NAME.match(self.name or "") is None:
            raise ProjectValidationError(
                f"a created transition's name is {self.name!r}; it must be lowercase, "
                "start with a letter, and use only letters, digits, '_' and '-' "
                "(at most 64 characters)"
            )
        match = _TRANSITION_TEMPLATE_KEY.match(self.template or "")
        if match is None:
            raise ProjectValidationError(
                f"a created transition's template is {self.template!r}, which is not "
                "a 'map:NNNN/transition:IIII' canonical transition identity"
            )
        if f"map:{match.group(1)}" != self.source:
            # The template supplies the created record's UNRESOLVED bytes. Borrowing
            # them from another map's record would be a claim about that map's
            # geometry that nothing measures, so it is refused here - the narrowest
            # rule this project can state, and the reason a map with no supported
            # 566-class record of its own cannot be given a created transition.
            raise ProjectValidationError(
                f"a created transition for {self.source} names template "
                f"{self.template}, which belongs to map:{match.group(1)}; a template "
                "must be a record of the same source map, because the bytes the "
                "creation does not author are copied from it"
            )
        if not isinstance(self.destination, str) or _MAP_KEY.match(self.destination) is None:
            raise ProjectValidationError(
                f"a created transition's destination is {self.destination!r}, which is "
                "not a 'map:NNNN' map identity"
            )
        if not isinstance(self.region, TransitionRegion):
            raise ProjectValidationError(
                f"a created transition's region must be a TransitionRegion, "
                f"got {self.region!r}"
            )
        if (
            not isinstance(self.arrival, (list, tuple))
            or len(self.arrival) != 2
            or any(type(part) is not int or not 0 <= part < ARRIVAL_UNSET_MINIMUM
                   for part in self.arrival)
        ):
            raise ProjectValidationError(
                f"a created transition's arrival is {self.arrival!r}, which is not an "
                "[x, y] pair below the measured unset sentinel"
            )
        for value, label in (
            (self.prior_facing_raw, "prior_facing_raw"),
            (self.prior_unresolved_raw, "prior_unresolved_raw"),
        ):
            if type(value) is not int or not 0 <= value <= 0xFF:
                raise ProjectValidationError(
                    f"a created transition's {label} is {value!r}, which is not a "
                    "single byte"
                )
        if self.facing is not None and (
            type(self.facing) is not int or not 0 <= self.facing <= FACING_MASK
        ):
            raise ProjectValidationError(
                f"a created transition's facing is {self.facing!r}, which is not an "
                f"integer 0..{FACING_MASK} or absent"
            )

    @property
    def identity(self) -> str:
        return transition_creation_identity(int(self.source[4:], 10), self.name)

    def to_document(self) -> dict[str, Any]:
        # `prior_facing_raw` and `prior_unresolved_raw` are written unconditionally:
        # they are what pins the created record's unresolved bytes to the template,
        # so unlike an edit's optional priors a creation without them is incomplete.
        document: dict[str, Any] = {
            "template": self.template,
            "destination": self.destination,
            "region": _region_document(self.region),
            "arrival": list(self.arrival),
            "prior_facing_raw": self.prior_facing_raw,
            "prior_unresolved_raw": self.prior_unresolved_raw,
        }
        if self.facing is not None:
            document["facing"] = self.facing
        return document

    @classmethod
    def from_document(
        cls, source_key: str, name: str, document: object, where: object
    ) -> "AuthoredTransitionCreation":
        if not isinstance(document, Mapping):
            raise ProjectLoadError(f"{where}: a created transition must be a table")
        unknown = set(document) - {
            "template",
            "destination",
            "region",
            "arrival",
            "facing",
            "prior_facing_raw",
            "prior_unresolved_raw",
        }
        if unknown:
            raise ProjectLoadError(
                f"{where}: unknown key(s) {sorted(unknown)}; a created transition "
                "names a template, a destination, a region, an arrival and the "
                "template bytes it preserves"
            )
        for required in ("template", "destination", "region", "arrival",
                         "prior_facing_raw", "prior_unresolved_raw"):
            if required not in document:
                raise ProjectLoadError(
                    f"{where}: a created transition must declare {required}; it is "
                    "what pins the new record to the canonical bytes it starts from"
                )
        template = document["template"]
        if not isinstance(template, str):
            raise ProjectValidationError(
                f"{where}: template must be a 'map:NNNN/transition:IIII' string, "
                f"got {template!r}"
            )
        destination = document["destination"]
        if not isinstance(destination, str):
            raise ProjectValidationError(
                f"{where}: destination must be a 'map:NNNN' string, got {destination!r}"
            )
        region = _region_from_document(document["region"], f"{where}.region")
        arrival = _optional_point(document["arrival"], where, "arrival")
        if arrival is None:
            raise ProjectValidationError(
                f"{where}: arrival must be an [x, y] pair; a created transition always "
                "states where the player lands"
            )
        try:
            return cls(
                source=source_key,
                name=name,
                template=template,
                destination=destination,
                region=region,
                arrival=arrival,
                prior_facing_raw=_optional_byte(
                    document["prior_facing_raw"], where, "prior_facing_raw"
                ),
                prior_unresolved_raw=_optional_byte(
                    document["prior_unresolved_raw"], where, "prior_unresolved_raw"
                ),
                facing=_optional_byte(document.get("facing"), where, "facing"),
            )
        except ProjectValidationError as exc:
            raise ProjectValidationError(f"{where}: {exc}") from exc


@dataclass(frozen=True)
class TransitionCreations:
    """Every transition a project creates, keyed by source map and authored name.

    ``creations["map:0040"]["kai-shop"]`` reads "map 40's created transition named
    kai-shop". Both levels are durable keys: the map is the same ``map:NNNN``
    identity every other document uses, and the name is the authored name, never an
    array index - the index does not exist until a build appends the record, and the
    project outlives that build.
    """

    #: ``"map:NNNN"`` -> authored name -> the entry.
    creations: dict[str, dict[str, AuthoredTransitionCreation]] = field(
        default_factory=dict
    )

    @staticmethod
    def key_for(index: int) -> str:
        return f"map:{index:04d}"

    def is_empty(self) -> bool:
        return not any(entries for entries in self.creations.values())

    def edits(self) -> dict[tuple[int, str], AuthoredTransitionCreation]:
        """Flatten to ``{(source map index, name): entry}``."""
        flat: dict[tuple[int, str], AuthoredTransitionCreation] = {}
        for key, entries in self.creations.items():
            index = int(key[4:], 10)
            for name, entry in entries.items():
                flat[(index, name)] = entry
        return flat

    @classmethod
    def from_edits(
        cls, creations: Mapping[tuple[int, str], AuthoredTransitionCreation]
    ) -> "TransitionCreations":
        maps: dict[str, dict[str, AuthoredTransitionCreation]] = {}
        for (map_index, name), entry in sorted(creations.items()):
            maps.setdefault(cls.key_for(map_index), {})[name] = entry
        return cls(creations=maps)

    def for_map(self, index: int) -> dict[str, AuthoredTransitionCreation]:
        return dict(self.creations.get(self.key_for(index), {}))

    def names_for_map(self, index: int) -> tuple[str, ...]:
        """This map's created transitions in the order a build appends them.

        Sorted by name, which is the only order the project defines: the *array*
        index of a created transition is a build-time fact, and nothing durable may
        depend on it. The order is stated here once so the build and any surface
        that displays "the order these will be appended in" cannot disagree.
        """
        return tuple(sorted(self.for_map(index)))

    def to_document(self) -> dict[str, Any]:
        return {
            TRANSITION_CREATION_TABLE: {
                key: {
                    name: entry.to_document()
                    for name, entry in sorted(entries.items())
                }
                for key, entries in sorted(self.creations.items())
            }
        }

    @classmethod
    def from_document(
        cls, document: Mapping[str, Any], where: object
    ) -> "TransitionCreations":
        table = document.get(TRANSITION_CREATION_TABLE)
        if table is None:
            raise ProjectLoadError(
                f"{where}: missing required [{TRANSITION_CREATION_TABLE}] table"
            )
        if not isinstance(table, Mapping):
            raise ProjectLoadError(
                f"{where}: [{TRANSITION_CREATION_TABLE}] must be a table"
            )
        maps: dict[str, dict[str, AuthoredTransitionCreation]] = {}
        for map_key, entries in table.items():
            label = f"{TRANSITION_CREATION_TABLE}.{map_key}"
            if not _MAP_KEY.match(str(map_key)):
                raise ProjectLoadError(
                    f"{where}: {label} is not a valid map identity; expected "
                    "'map:NNNN' with four digits"
                )
            if not isinstance(entries, Mapping):
                raise ProjectLoadError(f"{where}: {label} must be a table")
            by_name: dict[str, AuthoredTransitionCreation] = {}
            for name, entry in entries.items():
                name = str(name)
                if _TRANSITION_NAME.match(name) is None:
                    raise ProjectLoadError(
                        f"{where}: {label}.{name} is not a transition name; it must be "
                        "lowercase, start with a letter, and use only letters, digits, "
                        "'_' and '-'"
                    )
                if name in by_name:
                    raise ProjectLoadError(
                        f"{where}: {label} declares transition {name} twice"
                    )
                by_name[name] = AuthoredTransitionCreation.from_document(
                    str(map_key), name, entry, f"{where}: {label}.{name}"
                )
            if not by_name:
                raise ProjectLoadError(
                    f"{where}: {label} declares no created transitions"
                )
            if map_key in maps:
                raise ProjectLoadError(f"{where}: duplicate map {map_key}")
            maps[map_key] = by_name
        if not maps:
            raise ProjectLoadError(
                f"{where}: [{TRANSITION_CREATION_TABLE}] declares no creations"
            )
        return cls(creations=maps)


@dataclass(frozen=True)
class PixelOverride:
    """One graphic whose authored pixels differ from the extracted baseline.

    The authored source of a pixel override is a PNG in the project, not a field
    in a TOML document. `docs/project-format.md` writes `graphics/` as files plus
    a manifest precisely because pixels are not text, so this dataclass holds what
    the build RESOLVED from that file rather than duplicating it: a `[pixels]`
    table carrying the pixels would make the PNG and the TOML two statements of
    one asset, and one of them would eventually be the wrong one.

    ``file`` is project-relative and POSIX-spelled, matching the manifest's own
    ``file`` field. ``pixels`` are decoded linear palette indices in the order
    `ActorSprites.plan_pixels` consumes, so nothing above the codec has to know
    either the PNG container or the hardware tile order. ``width``, ``height``
    and ``colour_256`` are the facts the *piece* record declares, carried from the
    manifest so a resized or re-depth-ed PNG can be refused without opening the
    ROM.
    """

    identity: str
    file: str
    pixels: bytes
    width: int
    height: int
    colour_256: bool

    def __post_init__(self) -> None:
        for name in ("identity", "file"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ProjectValidationError(
                    f"a pixel override requires a non-empty {name}"
                )
        if type(self.pixels) is not bytes or not self.pixels:
            raise ProjectValidationError(
                f"{self.identity}: a pixel override requires non-empty immutable pixels"
            )
        if (type(self.width) is not int or self.width <= 0
                or type(self.height) is not int or self.height <= 0):
            raise ProjectValidationError(
                f"{self.identity}: a pixel override requires positive dimensions"
            )
        if len(self.pixels) != self.width * self.height:
            raise ProjectValidationError(
                f"{self.identity}: {len(self.pixels)} pixels do not describe a "
                f"{self.width}x{self.height} graphic"
            )
        if type(self.colour_256) is not bool:
            raise ProjectValidationError(
                f"{self.identity}: a pixel override requires a boolean bit depth"
            )


@dataclass(frozen=True)
class GraphicsOverrides:
    """Authored graphics edits: palette recolours and authored pixel content.

    Two edits, one document. The palette half is authored source in
    `graphics/overrides.toml` and holds only RGB, never the packed GBA word: the
    SDK owns the RGB->word packing (`sprite_graphics.pack_gba_colour`), and a
    project that stored the word would bake ROM-format knowledge into authored
    source. The build packs each triple and plans it through
    `ActorSprites.plan_palette_entry`, so an authored recolour reaches the emitted
    ROM at that entry's two bytes.

    The pixel half is resolved from the project's own PNGs against the baseline
    the extracted `graphics/graphics.toml` manifest recorded, and is empty for a
    project that authored nothing. `graphics_authoring.resolve_pixel_overrides`
    is the ONE place that derivation happens, and `validate` and `build` both go
    through it, so the two steps can never disagree about which graphics a project
    authors. Palette and pixel edits then merge into the same single write plan,
    so neither can silently overwrite the other.
    """

    #: palette index -> (red, green, blue), each channel 0..255.
    palette: dict[int, tuple[int, int, int]] = field(default_factory=dict)
    #: graphic identity (``<profile>/graphic:NNNN``) -> authored pixel content.
    #: Derived, never serialized: see the class docstring.
    pixels: dict[str, PixelOverride] = field(default_factory=dict)

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


# --- authored actor sprites --------------------------------------------------

#: SPRITE-NEW-PROJECT-SURFACE-001. Authored new actor-sprite identities: art the
#: canonical image does not contain, plus the ONE map actor that draws it.
#:
#: A document of its own rather than a field of `graphics/graphics.toml`, for the
#: reason `maps/chunks.toml` is not a field of `maps/layout.toml`: the extracted
#: graphics manifest is deterministic ROM-derived output that describes what the
#: image already holds, while this file authors content that has no canonical
#: bytes at all. A missing file means the project authors no new actor sprite,
#: matching every other optional subsystem, so a project extracted before this
#: capability stays loadable.
#:
#: The pixels live in PNG files beside it rather than in the table, exactly as the
#: extracted graphics manifest keeps its payloads as PNGs: pixels are not text, and
#: one file per sheet is what makes an edit reviewable. What a PNG cannot state -
#: which cells are frames, which engine id the identity answers to, which palette
#: entries are free, where the actor stands and what its behaviour entry starts
#: from - is the table's job.
SPRITES_FILE = Path("sprites") / "sprites.toml"

SPRITE_TABLE = "sprite"

#: An authored sprite's name, the same durable shape a chunk and a created
#: transition take: it becomes part of an identity a manifest carries, so it stays
#: lowercase, bounded and free of path or separator characters.
_SPRITE_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")

#: ``map:NNNN/object:IIII`` - one slot of a map's engine-counted object array.
#: The same durable shape as ``map:NNNN/placement:IIII``; the object array is
#: this project's own name for the array a MapEntry's ``+0x14`` names.
_OBJECT_TEMPLATE_KEY = re.compile(r"^map:(\d{4})/object:(\d{4})$")

#: The object palette's extent and its transparent entry. Hardware numbers stated
#: locally, like `_CHUNK_SIDE`: this package owns the authored surface and must not
#: reach into a module that opens ROMs. `test_sprite_project` pins them against
#: `formats.sprite_graphics`, so the two cannot drift.
_PALETTE_ENTRIES = 256
_TRANSPARENT_INDEX = 0

#: How many animation slots one identity may carry, and how many frames one of
#: those slots may hold. The structure's count byte and the project's own reader
#: bound the first; the second is the same bound stated on the sheet. Same rule as
#: above: pinned by test rather than imported.
_MAX_ANIMATION_SLOTS = 23
_MAX_FRAMES_PER_ANIMATION = 64

#: The four facings every source sheet carries. The GBA's own number for this
#: family, stated here for the same reason.
_DIRECTION_COUNT = 4

#: The colour a source sheet uses to mean "this pixel is a hole". The planner's
#: own default (`sprite_identity.DEFAULT_TRANSPARENT_COLOUR`), restated because
#: this layer owns the authored text and the default has to be written down
#: somewhere a reader can see it.
DEFAULT_SHEET_TRANSPARENT_COLOUR = (255, 0, 255)


def _require_sheet_path(value: object, where: object) -> str:
    """A project-relative, POSIX-spelled path to one sheet PNG.

    The same rule the extracted graphics manifest follows: a path is recorded
    relative to the project, never absolute, because an absolute path is a fact
    about one machine and a project that pinned one would stop being portable the
    moment it was cloned.
    """
    if not isinstance(value, str) or not value.strip():
        raise ProjectValidationError(f"{where}: sheet must be a non-empty path string")
    if "\\" in value:
        raise ProjectValidationError(
            f"{where}: sheet {value!r} uses a backslash; a project records paths "
            "with forward slashes so it reads the same everywhere"
        )
    from pathlib import PurePosixPath, PureWindowsPath

    path = PurePosixPath(value)
    # Both flavours are checked: a project is read on whatever machine a
    # contributor has, and "C:/elsewhere/sheet.png" is NOT absolute to a POSIX
    # parser while it IS absolute to the one that would resolve it on Windows.
    if (path.is_absolute() or PureWindowsPath(value).is_absolute()
            or ".." in path.parts):
        raise ProjectValidationError(
            f"{where}: sheet {value!r} must be a path inside the project, not an "
            "absolute path or one that climbs out of it"
        )
    if path.suffix.lower() != ".png":
        raise ProjectValidationError(
            f"{where}: sheet {value!r} is not a .png; a source sheet is an image "
            "file an editor can open"
        )
    return value


@dataclass(frozen=True, slots=True)
class AuthoredSpriteAnimation:
    """One animation slot of an authored identity, and the sheet that fills it.

    ``frames`` counts the frames of ONE facing. A sheet holds four facings of
    equal frame counts laid out as one row of cells, so the sheet's own width
    states the same number; recording it on both lets the loader refuse a sheet
    whose dimensions and declaration disagree instead of picking one.
    """

    name: str
    sheet: str
    frames: int

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or _SPRITE_NAME.match(self.name) is None:
            raise ProjectValidationError(
                f"animation name {self.name!r} must be lowercase, start with a "
                "letter, and use only letters, digits, '_' and '-'"
            )
        _require_sheet_path(self.sheet, f"animation {self.name}")
        if not 1 <= self.frames <= _MAX_FRAMES_PER_ANIMATION:
            raise ProjectValidationError(
                f"animation {self.name!r} declares {self.frames} frames per facing; "
                f"this project reads counts from 1 through {_MAX_FRAMES_PER_ANIMATION}"
            )

    def to_document(self) -> dict[str, Any]:
        return {"sheet": self.sheet, "frames": self.frames}

    @classmethod
    def from_document(
        cls, name: str, document: object, where: object
    ) -> "AuthoredSpriteAnimation":
        if not isinstance(document, Mapping):
            raise ProjectLoadError(f"{where}: an animation must be a table")
        unexpected = set(document) - {"sheet", "frames"}
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(
                f"{where}: unknown key(s) {joined}; an animation names a sheet and "
                "its frames per facing"
            )
        for required in ("sheet", "frames"):
            if required not in document:
                raise ProjectLoadError(f"{where}: an animation must declare {required}")
        if not isinstance(document["sheet"], str):
            raise ProjectLoadError(
                f"{where}: sheet must be a path string, got {document['sheet']!r}"
            )
        if type(document["frames"]) is not int:
            raise ProjectLoadError(
                f"{where}: frames must be an integer, got {document['frames']!r}"
            )
        return cls(name=name, sheet=document["sheet"], frames=document["frames"])


def parse_object_template_identity(value: object, where: object) -> tuple[int, int]:
    """Split a ``map:NNNN/object:IIII`` identity into its map and slot.

    The mirror of `parse_transition_creation_identity`: the durable form is
    parsed in one place so a surface that displays a template and the build that
    resolves it cannot disagree about what it names.
    """
    if not isinstance(value, str):
        raise ProjectValidationError(
            f"{where}: an object identity must be a string, got {value!r}"
        )
    match = _OBJECT_TEMPLATE_KEY.match(value)
    if match is None:
        raise ProjectValidationError(
            f"{where}: {value!r} is not a 'map:NNNN/object:IIII' identity; both "
            "numbers are four digits"
        )
    return int(match.group(1), 10), int(match.group(2), 10)


@dataclass(frozen=True, slots=True)
class AuthoredSpriteActor:
    """The one map actor an authored identity is attached to.

    Every field is either authored by this project or carried verbatim from a
    measured source, and the two are kept apart on purpose:

    * authored - ``map``, ``position`` and ``wander_box``;
    * carried - ``retained_raw`` and ``data_pointer_raw`` are the new object
      header's ``+0x04`` and ``+0x0C`` words. Both are measured and neither is
      interpreted, so they are stored as the raw 32-bit words they are, with a
      ``_raw`` suffix and no invented meaning; the SDK never dereferences them.
      They are required rather than defaulted so the project states what it is
      carrying instead of the build inventing a value.
    * resolved - ``behaviour_template`` names an EXISTING object array slot of the
      SAME map, and the build copies that record's inline behaviour entry and then
      writes the authored wander box into it. A ROM address is never accepted
      here: the slot's own bytes are what a behaviour entry has to start from, and
      naming them by their map-and-slot identity is what keeps this document
      readable against a different image.

    ``family`` names the one measured object-record layout this project writes. It
    is stated rather than assumed because it is the check that keeps an unmodelled
    family out, not a preference.
    """

    map: str
    family: str
    position: tuple[int, int]
    retained_raw: int
    data_pointer_raw: int
    behaviour_template: str
    wander_box: tuple[int, int, int, int]

    def __post_init__(self) -> None:
        if not isinstance(self.map, str) or _MAP_KEY.match(self.map) is None:
            raise ProjectValidationError(
                f"an actor's map is {self.map!r}, which is not a 'map:NNNN' identity"
            )
        _require_identity(self.behaviour_template, _OBJECT_TEMPLATE_KEY,
                          "map:NNNN/object:IIII", "template")
        match = _OBJECT_TEMPLATE_KEY.match(self.behaviour_template)
        if f"map:{match.group(1)}" != self.map:
            raise ProjectValidationError(
                f"an actor for {self.map} names behaviour template "
                f"{self.behaviour_template}, which belongs to map:{match.group(1)}; a "
                "template must be a slot of the same map, because the entry the "
                "actor starts from is one that map's own actors run"
            )
        if (
            not isinstance(self.position, tuple)
            or len(self.position) != 2
            or any(type(part) is not int for part in self.position)
        ):
            raise ProjectValidationError(
                f"an actor's position is {self.position!r}, which is not an [x, y] "
                "pair of map pixels"
            )
        if (
            not isinstance(self.wander_box, tuple)
            or len(self.wander_box) != 4
            or any(type(part) is not int for part in self.wander_box)
        ):
            raise ProjectValidationError(
                f"an actor's wander box is {self.wander_box!r}, which is not an "
                "[x1, y1, x2, y2] rectangle of map pixels"
            )
        for name in ("retained_raw", "data_pointer_raw"):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
                raise ProjectValidationError(
                    f"an actor's {name} is {value!r}, which is not an unsigned "
                    "32-bit word"
                )

    @property
    def map_index(self) -> int:
        return int(self.map[4:], 10)

    def to_document(self) -> dict[str, Any]:
        return {
            "map": self.map,
            "family": self.family,
            "position": list(self.position),
            "retained_raw": self.retained_raw,
            "data_pointer_raw": self.data_pointer_raw,
            "behaviour_template": self.behaviour_template,
            "wander_box": list(self.wander_box),
        }

    @classmethod
    def from_document(cls, document: object, where: object) -> "AuthoredSpriteActor":
        if not isinstance(document, Mapping):
            raise ProjectLoadError(f"{where}: an actor must be a table")
        fields = ("map", "family", "position", "retained_raw", "data_pointer_raw",
                  "behaviour_template", "wander_box")
        unexpected = set(document) - set(fields)
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(
                f"{where}: unknown key(s) {joined}; an actor names {', '.join(fields)}"
            )
        for required in fields:
            if required not in document:
                raise ProjectLoadError(f"{where}: an actor must declare {required}")
        for name in ("map", "family", "behaviour_template"):
            if not isinstance(document[name], str):
                raise ProjectLoadError(
                    f"{where}: {name} must be a string, got {document[name]!r}"
                )
        for name in ("retained_raw", "data_pointer_raw"):
            if type(document[name]) is not int:
                raise ProjectLoadError(
                    f"{where}: {name} must be an integer, got {document[name]!r}"
                )
        return cls(
            map=document["map"],
            family=document["family"],
            position=_pixel_pair(document["position"], where, "position"),
            retained_raw=document["retained_raw"],
            data_pointer_raw=document["data_pointer_raw"],
            behaviour_template=document["behaviour_template"],
            wander_box=_pixel_quad(document["wander_box"], where, "wander_box"),
        )


@dataclass(frozen=True, slots=True)
class AuthoredSprite:
    """One new actor-sprite identity, and the actor that draws it."""

    name: str
    sprite_id: int
    donor_sprite_id: int
    free_palette_entries: tuple[int, ...]
    animations: dict[str, AuthoredSpriteAnimation]
    actor: AuthoredSpriteActor

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or _SPRITE_NAME.match(self.name) is None:
            raise ProjectValidationError(
                f"sprite name {self.name!r} must be lowercase, start with a letter, "
                "and use only letters, digits, '_' and '-'"
            )
        for field_name in ("sprite_id", "donor_sprite_id"):
            value = getattr(self, field_name)
            if type(value) is not int or value < 0:
                raise ProjectValidationError(
                    f"sprite {self.name!r}: {field_name} must be a non-negative "
                    f"integer, got {value!r}"
                )
        if not isinstance(self.animations, dict) or not self.animations:
            raise ProjectValidationError(
                f"sprite {self.name!r} needs at least one animation"
            )
        if len(self.animations) > _MAX_ANIMATION_SLOTS:
            raise ProjectValidationError(
                f"sprite {self.name!r} declares {len(self.animations)} animation "
                f"slots; this project reads counts from 1 through "
                f"{_MAX_ANIMATION_SLOTS}"
            )
        for key, animation in self.animations.items():
            if key != animation.name:
                raise ProjectValidationError(
                    f"sprite {self.name!r}: animation table key {key!r} does not "
                    f"match the animation's own name {animation.name!r}"
                )
        if not isinstance(self.free_palette_entries, tuple):
            raise ProjectValidationError(
                f"sprite {self.name!r}: free palette entries must be a tuple"
            )
        for index in self.free_palette_entries:
            if (
                type(index) is not int
                or not _TRANSPARENT_INDEX < index < _PALETTE_ENTRIES
            ):
                raise ProjectValidationError(
                    f"sprite {self.name!r}: free palette entry {index!r} is outside "
                    f"{_TRANSPARENT_INDEX + 1}..{_PALETTE_ENTRIES - 1}; entry "
                    f"{_TRANSPARENT_INDEX} is the transparent entry"
                )
        if len(set(self.free_palette_entries)) != len(self.free_palette_entries):
            raise ProjectValidationError(
                f"sprite {self.name!r}: free palette entries repeat: "
                f"{sorted(self.free_palette_entries)}"
            )
        if not isinstance(self.actor, AuthoredSpriteActor):
            raise ProjectValidationError(
                f"sprite {self.name!r} needs an actor to attach its identity to"
            )

    @property
    def identity(self) -> str:
        return f"sprite:{self.name}"

    def animation_names(self) -> tuple[str, ...]:
        """This identity's animation slots, in the order a build emits them.

        Sorted by name, which is the only order the project defines: the engine
        reads an animation slot by its index, and a TOML table has no order to
        inherit, so the order has to be a stated rule rather than a file accident.
        The same rule `TransitionCreations.names_for_map` applies.
        """
        return tuple(sorted(self.animations))

    def ordered_animations(self) -> tuple[AuthoredSpriteAnimation, ...]:
        return tuple(self.animations[name] for name in self.animation_names())

    def to_document(self) -> dict[str, Any]:
        return {
            "sprite_id": self.sprite_id,
            "donor_sprite_id": self.donor_sprite_id,
            "free_palette_entries": list(self.free_palette_entries),
            "animation": {
                name: self.animations[name].to_document()
                for name in self.animation_names()
            },
            "actor": self.actor.to_document(),
        }

    @classmethod
    def from_document(
        cls, name: str, document: object, where: object
    ) -> "AuthoredSprite":
        if not isinstance(document, Mapping):
            raise ProjectLoadError(f"{where}: a sprite must be a table")
        fields = ("sprite_id", "donor_sprite_id", "free_palette_entries",
                  "animation", "actor")
        unexpected = set(document) - set(fields)
        if unexpected:
            joined = ", ".join(sorted(unexpected))
            raise ProjectLoadError(
                f"{where}: unknown key(s) {joined}; a sprite declares {', '.join(fields)}"
            )
        for required in fields:
            if required not in document:
                raise ProjectLoadError(f"{where}: a sprite must declare {required}")
        for field_name in ("sprite_id", "donor_sprite_id"):
            if type(document[field_name]) is not int:
                raise ProjectLoadError(
                    f"{where}: {field_name} must be an integer, got "
                    f"{document[field_name]!r}"
                )
        entries = document["free_palette_entries"]
        if not isinstance(entries, list) or any(type(item) is not int for item in entries):
            raise ProjectLoadError(
                f"{where}: free_palette_entries must be a list of integers"
            )
        table = document["animation"]
        if not isinstance(table, Mapping):
            raise ProjectLoadError(
                f"{where}: [animation] must be a table of animations"
            )
        animations: dict[str, AuthoredSpriteAnimation] = {}
        for key, value in table.items():
            label = f"{where}.animation.{key}"
            if _SPRITE_NAME.match(str(key)) is None:
                raise ProjectLoadError(
                    f"{label} is not an animation name; it must be lowercase, start "
                    "with a letter, and use only letters, digits, '_' and '-'"
                )
            animations[str(key)] = AuthoredSpriteAnimation.from_document(
                str(key), value, label
            )
        return cls(
            name=name,
            sprite_id=document["sprite_id"],
            donor_sprite_id=document["donor_sprite_id"],
            free_palette_entries=tuple(entries),
            animations=animations,
            actor=AuthoredSpriteActor.from_document(document["actor"], f"{where}.actor"),
        )


@dataclass(frozen=True)
class AuthoredSprites:
    """Every new actor-sprite identity a project authors.

    Exactly one, and that is a property of the image rather than a choice made
    here. An appended identity grows the canonical character registry and repoints
    the two literal words that name it; a second identity in the same build would
    grow the same registry again and repoint the same two words at a different
    table, so the two plans would write the same canonical bytes. A build can
    apply one of them, which is what this model accepts and what the planners
    refuse to describe otherwise.
    """

    sprites: dict[str, AuthoredSprite] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.sprites) > 1:
            raise ProjectValidationError(
                f"this project declares {len(self.sprites)} new actor-sprite "
                "identities; an appended identity grows the character registry for "
                "the whole image and repoints the two words that name it, so exactly "
                "one can be authored per build"
            )

    def is_empty(self) -> bool:
        return not self.sprites

    def only(self) -> AuthoredSprite:
        """The one authored sprite, refusing a project that names none."""
        if len(self.sprites) != 1:
            raise ProjectValidationError(
                "a build needs exactly one authored actor-sprite identity to place"
            )
        return next(iter(self.sprites.values()))

    def actor_maps(self) -> tuple[int, ...]:
        """The map indices an authored actor is appended to, in name order."""
        return tuple(sorted(sprite.actor.map_index for sprite in self.sprites.values()))

    def to_document(self) -> dict[str, Any]:
        return {
            SPRITE_TABLE: {
                name: sprite.to_document()
                for name, sprite in sorted(self.sprites.items())
            }
        }

    @classmethod
    def from_document(
        cls, document: Mapping[str, Any], where: object
    ) -> "AuthoredSprites":
        table = document.get(SPRITE_TABLE)
        if table is None:
            raise ProjectLoadError(f"{where}: missing required [{SPRITE_TABLE}] table")
        if not isinstance(table, Mapping) or not table:
            raise ProjectLoadError(
                f"{where}: [{SPRITE_TABLE}] must be a table declaring one sprite"
            )
        sprites: dict[str, AuthoredSprite] = {}
        for name, entry in table.items():
            label = f"{SPRITE_TABLE}.{name}"
            if _SPRITE_NAME.match(str(name)) is None:
                raise ProjectLoadError(
                    f"{where}: {label} is not a sprite name; it must be lowercase, "
                    "start with a letter, and use only letters, digits, '_' and '-'"
                )
            sprites[str(name)] = AuthoredSprite.from_document(str(name), entry,
                                                              f"{where}: {label}")
        return cls(sprites=sprites)


def _require_identity(value: object, pattern: "re.Pattern[str]", form: str,
                      name: str) -> None:
    """Refuse anything that is not one of this document's durable identity forms."""
    if not isinstance(value, str):
        raise ProjectValidationError(
            f"an actor's {name} must be a {form!r} string, got {value!r}"
        )
    if pattern.match(value) is None:
        raise ProjectValidationError(
            f"an actor's {name} is {value!r}, which is not a {form!r} identity"
        )


def _pixel_pair(value: object, where: object, name: str) -> tuple[int, int]:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 2
        or any(type(part) is not int for part in value)
    ):
        raise ProjectLoadError(
            f"{where}: {name} must be a two-integer [x, y] pair, got {value!r}"
        )
    return (value[0], value[1])


def _pixel_quad(value: object, where: object, name: str) -> tuple[int, int, int, int]:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 4
        or any(type(part) is not int for part in value)
    ):
        raise ProjectLoadError(
            f"{where}: {name} must be a four-integer [x1, y1, x2, y2] rectangle, "
            f"got {value!r}"
        )
    return (value[0], value[1], value[2], value[3])


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
    structure: "MapStructure | None" = None,
    transitions: "TransitionEdits | None" = None,
    transition_creations: "TransitionCreations | None" = None,
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
    if structure and not structure.is_empty():
        documents.append((STRUCTURE_FILE, structure.to_document()))
    if transitions and not transitions.is_empty():
        documents.append((TRANSITION_FILE, transitions.to_document()))
    if transition_creations and not transition_creations.is_empty():
        documents.append(
            (TRANSITION_CREATION_FILE, transition_creations.to_document())
        )

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


def write_map_structure(directory: str | Path, structure: "MapStructure") -> Path:
    """Persist only the structural document for a loaded project.

    MAP-RESIZE-AND-LAYERS-001. The mirror of `write_authored_chunks`: the
    structural authoring API validates before calling it, and it is the ONE place
    an authored resize or authored layer reaches disk. An empty document means the
    project authors no structure, so the optional file is removed rather than
    written as an invalid empty table (which `read_project` would then refuse).
    """
    path = Path(directory) / STRUCTURE_FILE
    if structure is None or structure.is_empty():
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_toml(structure.to_document()), encoding="utf-8", newline="\n")
    return path


def _read_structure(path: Path) -> "MapStructure":
    """Load `maps/structure.toml`, or nothing at all if it is absent.

    Absence is legal and means the project authors no structure. A file that
    exists but is malformed is still an error; "missing" and "wrong" are different
    answers, matching `_read_chunks` and `_read_layout`.
    """
    if not path.is_file():
        return MapStructure()
    return MapStructure.from_document(_read_document(path), path)


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


def write_transition_edits(directory: str | Path, transitions: "TransitionEdits") -> Path:
    """Persist only the transition document for a loaded project.

    MAP-WARP-PROJECT-AUTHORING-001. The mirror of `write_layout_edits`: the
    transition authoring API validates against the canonical image before calling
    it, and it is the ONE place an authored transition reaches disk. An empty edit
    set means the project authors no transition, so the optional document is removed
    rather than written as an invalid empty table (which `read_project` would then
    refuse).
    """
    path = Path(directory) / TRANSITION_FILE
    if transitions is None or transitions.is_empty():
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_toml(transitions.to_document()), encoding="utf-8", newline="\n")
    return path


def _read_transitions(path: Path) -> "TransitionEdits":
    """Load `maps/transitions.toml`, or nothing at all if it is absent.

    Same three-state rule as every other optional subsystem: absent means the
    project authors no transition, present-and-valid means it does, and
    present-and-malformed is an error rather than an empty edit set.
    """
    if not path.is_file():
        return TransitionEdits()
    return TransitionEdits.from_document(_read_document(path), path)


def write_transition_creations(
    directory: str | Path, creations: "TransitionCreations"
) -> Path:
    """Persist only the created-transition document for a loaded project.

    MAP-WARP-CREATE-PROJECT-001, and the mirror of `write_transition_edits` with one
    deliberate difference: it writes a document of its own, so removing the last
    *edit* cannot delete a *creation*. An empty creation set means the project
    creates no transition, so the optional document is removed rather than written
    as an invalid empty table (which `read_project` would then refuse).
    """
    path = Path(directory) / TRANSITION_CREATION_FILE
    if creations is None or creations.is_empty():
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_toml(creations.to_document()), encoding="utf-8", newline="\n")
    return path


def _read_transition_creations(path: Path) -> "TransitionCreations":
    """Load `maps/transition_creations.toml`, or nothing at all if it is absent."""
    if not path.is_file():
        return TransitionCreations()
    return TransitionCreations.from_document(_read_document(path), path)


def write_authored_sprites(directory: str | Path, sprites: "AuthoredSprites") -> Path:
    """Persist only the authored-sprite document for a loaded project.

    SPRITE-NEW-PROJECT-SURFACE-001. The mirror of `write_authored_chunks`: it is
    the ONE place an authored actor-sprite identity reaches disk, and the sheet
    PNGs it names are the project's own files rather than anything this writes. An
    empty document means the project authors no new sprite, so the optional file is
    removed rather than written as an invalid empty table (which `read_project`
    would then refuse).
    """
    path = Path(directory) / SPRITES_FILE
    if sprites is None or sprites.is_empty():
        path.unlink(missing_ok=True)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_toml(sprites.to_document()), encoding="utf-8", newline="\n")
    return path


def _read_sprites(path: Path) -> "AuthoredSprites":
    """Load `sprites/sprites.toml`, or nothing at all if it is absent.

    Same three-state rule as every other optional subsystem: absent means the
    project authors no new actor sprite, present-and-valid means it does, and
    present-and-malformed is an error rather than an empty document.
    """
    if not path.is_file():
        return AuthoredSprites()
    return AuthoredSprites.from_document(_read_document(path), path)


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
    structure = _read_structure(root / STRUCTURE_FILE)
    transitions = _read_transitions(root / TRANSITION_FILE)
    transition_creations = _read_transition_creations(root / TRANSITION_CREATION_FILE)
    sprites = _read_sprites(root / SPRITES_FILE)

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
    # MAP-RESIZE-AND-LAYERS-001. A structural edit's initialization chunk is the
    # same authored value form, so it is resolved the same way and reported with
    # the file the author has to fix.
    missing += sorted({
        item.fill
        for item in list(structure.resizes.values()) + list(structure.layers.values())
        if isinstance(item.fill, str) and item.fill not in chunks.chunks
    })
    if missing:
        raise ProjectValidationError(
            f"{root / LAYOUT_FILE}: names authored chunk(s) {sorted(set(missing))}, "
            f"which {CHUNK_FILE} does not declare"
        )

    # MAP-RESIZE-AND-LAYERS-001. A layout cell on a structurally authored layer
    # must fall inside the grid that structure declares. Checkable from the text
    # alone, and the alternative is an edit the author made that the build would
    # silently drop because the record's window has no such cell.
    for (map_index, slot, cell), _value in sorted(layout.cells().items()):
        structural = structure.resize_for(map_index, slot) or structure.layer_at(
            map_index, slot
        )
        if structural is None:
            continue
        if not 0 <= cell < structural.columns * structural.rows:
            raise ProjectValidationError(
                f"{root / LAYOUT_FILE}: map:{map_index:04d}/BG{slot} cell {cell} is "
                f"outside the {structural.columns}x{structural.rows} grid "
                f"{STRUCTURE_FILE} declares for it"
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
        structure=structure,
        transitions=transitions,
        transition_creations=transition_creations,
        sprites=sprites,
        placement_events=events,
        placement_types=(_read_document(root / PLACEMENT_TYPES_FILE)
                         if (root / PLACEMENT_TYPES_FILE).exists() else None),
    )
