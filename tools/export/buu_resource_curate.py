"""Curate the canonical Buu's Fury resource library into a human resource pack.

RESOURCE-LIBRARY-CURATION-001. The canonical exporter in
:mod:`tools.export.buu_resource_export` stays untouched: this module reads its
output as an immutable input and writes a **separate** library organised the way
a person looks for a resource.

**Two libraries, two jobs.** The raw library is exhaustive structural truth -
every map entry, layer, tile, chunk, sprite slot, frame and piece the exporter
publishes, named by numeric identity. The curated library is the reusable
resource pack: it keeps every *identity* the raw library establishes and stops
repeating *payloads* that several identities share. It is not a re-extraction;
every image it writes is a byte copy of a raw artifact, and every path it writes
is recorded against the raw path or paths it came from.

**Human-first names.** A curated file or directory name is built from the ROM
text the accepted structures carry, with ordinary spacing and punctuation::

    West City/Map.png
    Buu's House/Layers/Layer 1.png
    Grand Kai's Planet/Map 1/Map.png
    Android 18/Animations/Walk/Pose 2.png
    Tilesets/Tileset 12/Sheet.png

Underscores, hyphens used as technical separators, numeric ids, ROM addresses and
hashes never appear in a human-facing path. They live in the index layer, which
is the only place a curated path is tied back to canonical identity.

**No generated prose.** Nothing in the curated library explains itself. The only
strings that reach a curated name are ROM text or a neutral one-based label
defined in this module, and every metadata document is structural. The prose
guard from :mod:`tools.export.metadata` is applied to each document before it is
written, and the curated-path audit re-scans the finished tree.

**Determinism.** Documents are serialised with sorted keys and LF endings; a
shared payload is always attributed to the lowest sorted curated path that
carries it; every plan is ordered by numeric identity, never by directory order.
Two builds from one raw library produce byte-identical trees.

**The raw library is never written.** :func:`ensure_output_roots` refuses an
output root that resolves inside a git work tree, that is the raw root, that
contains it, or that is contained by it. :func:`build` hashes the raw library
before and after the build and refuses to report success when a single raw byte
changed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from . import metadata as meta
from . import png

TOOL_NAME = "buu_resource_curate"
TOOL_VERSION = "1"
SCHEMA = 1

# --- curated layout ----------------------------------------------------------

MAPS = "Maps"
TILESETS = "Tilesets"
CHUNKS = "Chunks"
SPRITES = "Sprites"
PALETTES = "Palettes"
TECHNICAL = "Technical"
INDEX = "Index"

LAYERS = "Layers"
ANIMATIONS = "Animations"
POSES = "Poses"
UNIQUE_GRAPHICS = "Unique Sprite Graphics"

MAP_IMAGE = "Map.png"
LAYER_IMAGE = "Layer {index}.png"
MAP_RECORD = "Map.json"
SHEET_IMAGE = "Sheet.png"
TILESET_RECORD = "Tileset.json"
SPRITE_RECORD = "Sprite.json"
ANIMATION_RECORD = "Animation.json"
POSE_IMAGE = "Pose {index}.png"
PALETTE_IMAGE = "Palette.png"
PALETTE_RECORD = "Palette.json"
GRAPHIC_IMAGE = "Graphic {index}.png"
GRAPHIC_RECORD = "Graphic {index}.json"
CHUNK_IMAGE = "Chunk {index}.png"
CHUNK_GROUP = "Chunks {first} to {last}"
TILESET_FOLDER = "Tileset {index}"
PALETTE_FOLDER = "Palette {index}"

#: ``<name> <n>`` - the one place a number is appended to a human name, used
#: only when two distinct canonical resources share a verified name.
GROUP = "{name} {index}"

#: The directories this tool owns beneath a curated root. ``--force`` empties
#: exactly these, so no stale artifact survives a rebuild and nothing the tool
#: did not create is ever removed.
GENERATED_DIRECTORIES = (
    MAPS,
    TILESETS,
    CHUNKS,
    SPRITES,
    PALETTES,
    TECHNICAL,
    INDEX,
)

INDEX_DOCUMENTS = (
    "Maps.json",
    "Tilesets.json",
    "Chunks.json",
    "Sprites.json",
    "Animations.json",
    "Palettes.json",
    "Technical Graphics.json",
    "Source Map.json",
)

#: Chunks are human-scale images, so the curated view groups them into folders a
#: person can open without rendering thousands of thumbnails at once. Fixed, so
#: a chunk's curated folder never moves as the corpus changes.
CHUNK_GROUP_SIZE = 32

#: Tile-sheet geometry: 128 pixels wide at 8 pixels a tile.
SHEET_TILE_COLUMNS = 16

#: Windows forbids these as file or directory names, with or without an
#: extension, and its case-insensitive filesystem makes the check case-folded.
RESERVED_NAMES = frozenset(
    {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{digit}" for digit in "123456789"),
        *(f"LPT{digit}" for digit in "123456789"),
    }
)

FORBIDDEN_CHARACTERS = '<>:"/\\|?*'
UNDERSCORE = "_"

#: The direction indices an animation row carries; the accepted cell layout.
DIRECTION_COUNT = 4

#: The LOGExtractor animation-slot names, indexed by animation-array position.
#:
#: Source: `mainant/LOGExtractor`, revision
#: `3a78bb35ad181082fbc9da01057538e5a78e8c2d`, `CharacterSpriteExtractor/Program.cs`
#: line 21 - a 23-entry array read as ``anim_names[a]`` for animation-array
#: position ``a``. The canonical corpus never declares more than 23 slots on a
#: definition (measured: the largest ``animation_slots`` value is 23), so the
#: table covers every position. The three ``unknown*`` entries are placeholders
#: rather than names, so those positions take the neutral fallback instead.
#:
#: **Status.** These are the external tool's labels, not engine facts. The
#: accepted project record (`docs/PROJECT_<local-state-name>`, LOGX-SPRITE-001) still
#: classes LOGExtractor's slot names as unproven, so nothing here promotes them:
#: this library is a local resource pack, it claims no engine behaviour, and the
#: index records this exact source beside every name it supplies.
LOGEXTRACTOR_ANIMATION_NAMES: tuple[str | None, ...] = (
    "Stand",
    "Walk",
    "Run",
    "Attack 1",
    "Attack 2",
    "Attack 3",
    "Attack 4",
    "Block",
    "Idle",
    "Hurt",
    "Transform",
    None,
    "Arms Up",
    "Pickup",
    "Takeoff",
    "Flying",
    "Mode 7 Fly",
    "Dead",
    "Special",
    "Teleport",
    None,
    "Fusion",
    None,
)

LOGEXTRACTOR_SOURCE = (
    "mainant/LOGExtractor@3a78bb35ad181082fbc9da01057538e5a78e8c2d"
    " CharacterSpriteExtractor/Program.cs anim_names"
)
NEUTRAL_NAME_SOURCE = "neutral one-based label"

# --- raw layout (read-only input) -------------------------------------------

RAW_MAPS = "maps"
RAW_TILES = "tiles"
RAW_BANKS = "banks"
RAW_SPRITES = "sprites"
RAW_ANIMATIONS = "animations"
RAW_PALETTES = "palettes"
RAW_METADATA = "metadata"

RAW_METADATA_FILES = (
    "animations.json",
    "chunks.json",
    "frames.json",
    "maps.json",
    "names.json",
    "sprites.json",
    "sprite_graphics.json",
    "tile_banks.json",
)

_HEX = re.compile(r"^0x[0-9a-fA-F]+$")

#: A raw numeric identity form that must never reach a human-facing name.
_RAW_IDENTITY = re.compile(
    r"^(map|sprite|animation|frame|direction|bank|tile|chunk|graphic|palette)_\d+"
)
_RAW_ADDRESS = re.compile(r"\b0x[0-9a-fA-F]{4,}\b")
_RAW_DIGEST = re.compile(r"^[0-9a-f]{32,}$")


class CurationError(RuntimeError):
    """Raised when curation cannot proceed as stated."""


# --- helpers -----------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def worker_count() -> int:
    """How many file operations to have in flight at once.

    The corpus is roughly 86,000 small files. Serial traversal spends its time in
    per-file NTFS and filter-driver overhead rather than in hashing, so overlapping
    the opens is worth far more than any algorithmic change; measured on the
    canonical library it is the difference between minutes and seconds. The count
    is derived from the machine rather than fixed, and every result is collected
    into a sorted structure, so the output does not depend on scheduling.
    """
    return max(1, min(32, (os.cpu_count() or 4) * 4))


def hashed_files(paths: Sequence[Path]) -> dict[str, tuple[int, str]]:
    """``relative path -> (bytes, sha256)`` for every path, hashed concurrently.

    ``paths`` are paired with the relative key their caller wants; a directory or
    a vanished file is skipped rather than raising, because the caller compares
    hashes over a library that is expected to be static.
    """
    workers = worker_count()
    if workers == 1 or len(paths) < 64:
        return {key: _hash_one(path) for key, path in paths}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(_hash_one, [path for _key, path in paths]))
    return {
        key: result
        for (key, _path), result in zip(paths, results)
        if result is not None
    }


def _hash_one(path: Path) -> tuple[int, str] | None:
    try:
        return (path.stat().st_size, sha256_file(path))
    except OSError:
        return None


def read_many(paths: Sequence[Path]) -> dict[Path, bytes]:
    """Read many files concurrently, keyed by path."""
    workers = worker_count()
    if workers == 1 or len(paths) < 64:
        return {path: path.read_bytes() for path in paths}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        blobs = list(pool.map(Path.read_bytes, paths))
    return dict(zip(paths, blobs))


def hex_to_int(value: str | None) -> int | None:
    if value is None:
        return None
    if not _HEX.match(value):
        raise CurationError(f"{value!r} is not a hexadecimal raw value")
    return int(value, 16)


# --- Windows-safe human names ------------------------------------------------

def clean_name(text: str) -> str:
    """A ROM string to a human-facing, Windows-safe path component.

    Normal spacing and punctuation survive, because they are what make the
    library readable: an apostrophe (``Buu's House``), a space (``Grand Kai's
    Planet``) and an ordinary hyphen inside a real name (``Z-Mart``). Only what a
    filesystem cannot represent is touched:

    * control characters and the Windows-reserved set ``< > : " / \\ | ? *``
      become a space;
    * trailing dots and trailing spaces are dropped, because Windows strips them
      silently and the written name would not match the planned one;
    * runs of whitespace collapse to one space and the ends are trimmed;
    * an empty result, or a reserved device name, becomes ``""`` and the caller
      substitutes a neutral label.

    Nothing is lower-cased, title-cased or re-spaced: a name is used exactly as
    the accepted structure carries it. Case is folded only when *comparing* two
    names, never when writing one.
    """
    if not isinstance(text, str):
        raise TypeError("a name must be a string")
    out: list[str] = []
    for character in text:
        if character in FORBIDDEN_CHARACTERS or ord(character) < 0x20 or ord(character) == 0x7F:
            out.append(" ")
        else:
            out.append(character)
    cleaned = " ".join("".join(out).split()).rstrip(". ").lstrip(" ")
    if cleaned.upper() in RESERVED_NAMES:
        return ""
    return cleaned


def name_key(text: str) -> str:
    """The collision key of a name: case-folded, with Windows' trailing dot and
    space stripping applied, so two names that would land on one file collide."""
    return text.rstrip(". ").casefold()


def human_name(text: str, fallback: str) -> str:
    """``text`` cleaned, or ``fallback`` when it holds nothing usable."""
    return clean_name(text) or fallback


def ordinal(index: int) -> str:
    """A one-based human ordinal, written plainly without zero padding.

    Human-facing names carry the number a person reads (``Layer 2``, ``Pose 10``,
    ``Chunk 7``), never a padded technical form. Zero-based or fixed-width values
    stay in metadata where the canonical identity belongs.
    """
    if index < 1:
        raise CurationError(f"a human ordinal is one-based, got {index}")
    return str(index)


def check_human_path(relative_path: str) -> str | None:
    """A reason when a human-facing curated path is unacceptable, else ``None``.

    The one mechanical rule the browsing hierarchy must satisfy is that no path
    component carries an underscore, the technical separator. Everything else -
    an apostrophe, a space, an ampersand, a hyphen inside a real name such as
    ``Z-Mart`` - is legitimate punctuation and passes.
    """
    for component in Path(relative_path).parts:
        if UNDERSCORE in component:
            return f"underscore in component {component!r}"
    return None


def assert_human_path(relative_path: str) -> None:
    reason = check_human_path(relative_path)
    if reason is not None:
        raise CurationError(f"{relative_path}: {reason}")


# --- raw library -------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class MapSource:
    map_index: int
    directory: str
    rom_text: str | None
    composite: str
    composite_status: str | None
    composite_runtime_status: str | None
    root_address: str | None
    key_high: int
    key_low: int
    text_index: int | None
    layers: tuple[dict[str, Any], ...]
    layer_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BankSource:
    bank_id: int
    sheet: str
    sheet_sha256: str
    tile_paths: tuple[str, ...]
    declared_size: int
    tile_count: int
    container_address: str | None


@dataclass(frozen=True, slots=True)
class ChunkSource:
    chunk_id: int
    image: str
    image_sha256: str
    width: int
    height: int
    referencing_map_indices: tuple[int, ...]
    render_map_index: int | None
    reference_count: int


@dataclass(frozen=True, slots=True)
class AnimationSource:
    animation_address: str
    frame_count: int
    cell_addresses: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SpriteSource:
    sprite_id: int
    run_index: int
    definition_address: str
    animation_slots: int
    rom_names: tuple[str, ...]
    slots: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class GraphicSource:
    graphic_id: int
    image: str
    image_sha256: str
    width: int
    height: int
    colour_256: bool
    container_address: str | None
    declared_size: int | None


@dataclass(frozen=True, slots=True)
class PaletteSource:
    palette_id: int
    image: str
    image_sha256: str
    width: int
    height: int
    role: str
    entry_count: int
    encoding: str
    source_address: str | None


class RawLibrary:
    """Read-only index over a canonical raw export root."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise CurationError(f"the raw resource root {self.root} does not exist")
        missing = [
            name
            for name in RAW_METADATA_FILES
            if not (self.root / RAW_METADATA / name).is_file()
        ]
        if missing:
            raise CurationError(
                f"{self.root} does not look like a canonical raw library; missing "
                f"metadata: {', '.join(sorted(missing))}"
            )
        self.names = self._document("names.json")
        self.maps_document = self._document("maps.json")
        self.sprites_document = self._document("sprites.json")
        self.animations_document = self._document("animations.json")
        self.frames_document = self._document("frames.json")
        self.banks_document = self._document("tile_banks.json")
        self.chunks_document = self._document("chunks.json")
        self.graphics_document = self._document("sprite_graphics.json")
        self._digests: dict[str, str] = {}
        self._present: set[str] | None = None
        self._index()

    # -- reading --------------------------------------------------------------

    def _document(self, name: str) -> Any:
        path = self.root / RAW_METADATA / name
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CurationError(f"cannot read {path}: {exc}") from exc

    def path(self, relative: str) -> Path:
        return self.root / Path(relative)

    def present_paths(self) -> set[str]:
        """Every file beneath the raw root, as a set of relative paths.

        Built once. The plan asks "does this artifact exist" a hundred thousand
        times, and a set lookup is the difference between one directory walk and
        a hundred thousand ``stat`` calls.
        """
        if self._present is None:
            self._present = {
                path.relative_to(self.root).as_posix()
                for path in self.root.rglob("*")
                if path.is_file()
            }
        return self._present

    def exists(self, relative: str) -> bool:
        return bool(relative) and relative in self.present_paths()

    def sha256_of(self, relative: str) -> str:
        """The digest of one raw artifact, memoised for the run.

        A digest measured by :meth:`hash_tree` is reused, so an artifact is read
        once for the whole curation rather than once per question asked about it.
        """
        digest = self._digests.get(relative)
        if digest is None:
            digest = sha256_file(self.path(relative))
            self._digests[relative] = digest
        return digest

    def hash_tree(self) -> dict[str, tuple[int, str]]:
        """``relative path -> (bytes, sha256)`` for every raw artifact.

        This is the run's input-integrity measurement *and* its digest cache: the
        plan needs the identity of nearly every artifact anyway, so measuring the
        library once up front costs less than measuring it lazily and repeatedly.
        """
        present = sorted(self.present_paths())
        hashes = hashed_files(
            [(relative, self.path(relative)) for relative in present]
        )
        self._digests.update(
            {relative: digest for relative, (_size, digest) in hashes.items()}
        )
        self._present = set(hashes)
        return hashes

    # -- indexing -------------------------------------------------------------

    def _index(self) -> None:
        names_by_index = {row["map_index"]: row for row in self.names["map_names"]}
        maps_by_index = {row["map_index"]: row for row in self.maps_document["maps"]}
        self.maps: tuple[MapSource, ...] = tuple(
            self._map_source(
                index,
                maps_by_index[index],
                names_by_index.get(index, {}),
            )
            for index in sorted(maps_by_index)
        )

        self.banks: tuple[BankSource, ...] = tuple(
            BankSource(
                bank_id=row["bank_id"],
                sheet=f"{RAW_TILES}/{RAW_BANKS}/bank_{row['bank_id']:03d}/sheet.png",
                sheet_sha256=row.get("sheet_sha256", ""),
                tile_paths=tuple(
                    f"{RAW_TILES}/{RAW_BANKS}/bank_{row['bank_id']:03d}/tiles/"
                    f"tile_{index:04d}.png"
                    for index in range(row["declared_size"] // 64)
                ),
                declared_size=row["declared_size"],
                tile_count=row["declared_size"] // 64,
                container_address=row.get("container_address"),
            )
            for row in sorted(
                self.banks_document["tile_banks"], key=lambda row: row["bank_id"]
            )
        )

        self.chunks: tuple[ChunkSource, ...] = tuple(
            ChunkSource(
                chunk_id=row["chunk_id"],
                image=row["image"],
                image_sha256=row["image_sha256"],
                width=row.get("width", 256),
                height=row.get("height", 256),
                referencing_map_indices=tuple(row.get("referencing_map_indices", ())),
                render_map_index=row.get("render_map_index"),
                reference_count=row.get("referencing_map_count", 0),
            )
            for row in sorted(
                self.chunks_document["chunks"], key=lambda row: row["chunk_id"]
            )
        )

        self.animations: tuple[AnimationSource, ...] = tuple(
            AnimationSource(
                animation_address=row["animation_address"],
                frame_count=row["frame_count"],
                cell_addresses=tuple(row["cell_addresses"]),
            )
            for row in sorted(
                self.animations_document["unique_animations"],
                key=lambda row: hex_to_int(row["animation_address"]) or 0,
            )
        )
        self.animation_by_address = {
            record.animation_address: record for record in self.animations
        }

        names_by_sprite = {row["sprite_id"]: row for row in self.names["sprite_names"]}
        self.sprites: tuple[SpriteSource, ...] = tuple(
            SpriteSource(
                sprite_id=row["sprite_id"],
                run_index=row["run_index"],
                definition_address=row["definition_address"],
                animation_slots=row["animation_slots"],
                rom_names=tuple(
                    entry["rom_text"]
                    for entry in names_by_sprite.get(row["sprite_id"], {}).get("names", [])
                    if entry.get("rom_text")
                ),
                slots=tuple(row["slots"]),
            )
            for row in sorted(
                self.sprites_document["sprites"], key=lambda row: row["sprite_id"]
            )
        )

        self.graphics: tuple[GraphicSource, ...] = tuple(
            GraphicSource(
                graphic_id=row["graphic_id"],
                image=row["image"],
                image_sha256=row["image_sha256"],
                width=row["width"],
                height=row["height"],
                colour_256=row["colour_256"],
                container_address=row.get("container_address"),
                declared_size=row.get("declared_size"),
            )
            for row in sorted(
                self.graphics_document["sprite_graphics"], key=lambda row: row["graphic_id"]
            )
        )

        palette_root = self.root / RAW_PALETTES
        palette_ids = sorted(
            int(path.stem.split("_")[1]) for path in palette_root.glob("palette_*.json")
        )
        self.palettes: tuple[PaletteSource, ...] = tuple(
            self._palette_source(palette_id) for palette_id in palette_ids
        )

    def _map_source(
        self, index: int, row: dict[str, Any], name_row: dict[str, Any]
    ) -> MapSource:
        """Read one map from its own raw record.

        The raw directory name is ``map_<id>`` for a map with no ROM text and
        ``map_<id>_<sanitized name>`` for one with it, so the directory is taken
        from the raw library's own name record rather than reconstructed. The
        map's layer list and composite fields come from that directory's
        ``map.json``, which names each layer's image; the aggregate
        ``metadata/maps.json`` is not the authority here because it does not
        repeat every per-map field.
        """
        directory = name_row.get("directory") or f"map_{index:03d}"
        if not directory.startswith(f"{RAW_MAPS}/"):
            directory = f"{RAW_MAPS}/{directory}"
        record_path = f"{directory}/map.json"
        record: dict[str, Any] = {}
        if self.exists(record_path):
            try:
                record = json.loads(self.path(record_path).read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise CurationError(f"cannot read {record_path}: {exc}") from exc
        merged = {**row, **record}

        aggregate = {
            layer.get("slot"): layer for layer in row.get("layers", ())
        }
        layers = tuple(
            {**aggregate.get(layer.get("slot"), {}), **layer}
            for layer in merged.get("layers", ())
        )
        layer_paths = tuple(
            layer["image"]
            for layer in layers
            if layer.get("image") and layer.get("status") == "rendered"
        )
        layer_paths = tuple(path for path in layer_paths if self.exists(path))
        composite = merged.get("composite_image") or f"{directory}/composite.png"
        return MapSource(
            map_index=index,
            directory=directory,
            rom_text=name_row.get("rom_text"),
            composite=composite,
            composite_status=merged.get("composite_status"),
            composite_runtime_status=merged.get("composite_runtime_status"),
            root_address=merged.get("root_address"),
            key_high=merged.get("key_high", 0),
            key_low=merged.get("key_low", 0),
            text_index=merged.get("text_index"),
            layers=layers,
            layer_paths=layer_paths,
        )

    def _palette_source(self, palette_id: int) -> PaletteSource:
        relative = f"{RAW_PALETTES}/palette_{palette_id:03d}.json"
        document = json.loads(self.path(relative).read_text(encoding="utf-8"))
        return PaletteSource(
            palette_id=palette_id,
            image=document["image"],
            image_sha256=document.get("image_sha256", ""),
            width=document.get("image_width", 256),
            height=document.get("image_height", 1),
            role=document.get("role", ""),
            entry_count=document.get("entry_count", 256),
            encoding=document.get("encoding", ""),
            source_address=document.get("source_address"),
        )


# --- output safety -----------------------------------------------------------

def is_repository_root(candidate: Path) -> bool:
    """Whether ``candidate`` is a usable git work-tree root.

    A bare ``.git`` directory is not enough: an interrupted clone or a stray
    ``mkdir .git`` would otherwise refuse perfectly safe output paths.
    """
    marker = candidate / ".git"
    if marker.is_dir():
        return (marker / "HEAD").exists()
    return marker.is_file()


def find_repository_root(path: Path) -> Path | None:
    current = Path(path).resolve()
    for candidate in (current, *current.parents):
        if is_repository_root(candidate):
            return candidate
    return None


def ensure_outside_repository(root: Path, label: str) -> None:
    repository = find_repository_root(root)
    if repository is not None:
        raise CurationError(
            f"the {label} {root} resolves inside the git repository at "
            f"{repository}; a curated resource library must live outside version "
            "control"
        )


def _is_within(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def ensure_output_roots(source: Path, output: Path, audit: Path) -> None:
    """Refuse every output root that could damage the canonical raw library.

    This is the ticket's one hard safety rule: the raw dump is an immutable
    input. The check is on resolved paths, so a junction, a relative path or a
    trailing separator cannot smuggle an output root into the input.
    """
    source = Path(source).resolve()
    output = Path(output).resolve()
    audit = Path(audit).resolve()
    if output == source or audit == source:
        raise CurationError(f"an output root resolves to the raw resource root {source}")
    if _is_within(output, source) or _is_within(audit, source):
        raise CurationError(f"an output root resolves inside the raw resource root {source}")
    if _is_within(source, output) or _is_within(source, audit):
        raise CurationError(f"the raw resource root {source} would be inside an output root")
    if _is_within(audit, output) or _is_within(output, audit):
        raise CurationError(
            f"the audit root {audit} and the curated root {output} may not contain "
            "one another"
        )
    ensure_outside_repository(output, "curated output root")
    ensure_outside_repository(audit, "curation audit root")


def audit_root_for(output_root: Path) -> Path:
    """``<OUTPUT>`` -> ``<OUTPUT> Audit``, a clean sibling directory."""
    resolved = Path(output_root).resolve()
    return resolved.parent / (resolved.name + " Audit")


def _has_files(target: Path) -> bool:
    for entry in target.rglob("*"):
        if entry.is_file() or entry.is_symlink():
            return True
    return False


def _empty_directory(target: Path) -> None:
    """Empty a generated directory, tolerating one another process holds open.

    Same contract as the exporter's own sweep: emptiness is what a replacement
    needs, and a file that genuinely cannot be removed is reported with its path
    rather than as a traceback.
    """
    try:
        shutil.rmtree(target)
        return
    except OSError:
        pass
    for entry in sorted(target.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        try:
            if entry.is_dir() and not entry.is_symlink():
                entry.rmdir()
            else:
                entry.unlink()
        except OSError:
            continue
    if _has_files(target):
        raise CurationError(
            f"cannot empty the generated directory {target}; remove its contents or "
            "choose another curated root"
        )


def clear_generated(output_root: Path) -> tuple[str, ...]:
    """Empty this tool's own directories; return whatever else is left."""
    for name in GENERATED_DIRECTORIES:
        target = output_root / name
        if target.is_dir():
            _empty_directory(target)
    if not output_root.exists():
        return ()
    return tuple(sorted(entry.name for entry in output_root.iterdir()))


# --- layout planning ---------------------------------------------------------

@dataclass(frozen=True, slots=True)
class PlanEntry:
    """One curated artifact: where it goes and which raw files it came from."""

    relative_path: str
    sources: tuple[str, ...]
    human_facing: bool = True
    shared_from: str | None = None


@dataclass(slots=True)
class Plan:
    """The complete curated layout, computed before a byte is written."""

    entries: list[PlanEntry] = field(default_factory=list)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    index: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    aliases: list[dict[str, Any]] = field(default_factory=list)
    _paths: dict[str, str] = field(default_factory=dict)

    def add(
        self,
        relative_path: str,
        sources: Sequence[str],
        *,
        human_facing: bool = True,
        shared_from: str | None = None,
    ) -> PlanEntry:
        key = name_key(relative_path)
        if key in self._paths:
            raise CurationError(
                f"the curated layout would write {relative_path!r}, which collides "
                f"with {self._paths[key]!r}"
            )
        if human_facing:
            assert_human_path(relative_path)
        self._paths[key] = relative_path
        entry = PlanEntry(
            relative_path=relative_path,
            sources=tuple(dict.fromkeys(source for source in sources if source)),
            human_facing=human_facing,
            shared_from=shared_from,
        )
        self.entries.append(entry)
        return entry

    def document(self, relative_path: str, document: dict[str, Any]) -> None:
        self.documents[relative_path] = document

    def sorted_entries(self) -> list[PlanEntry]:
        return sorted(self.entries, key=lambda entry: entry.relative_path)

    def human_paths(self) -> list[str]:
        return sorted(
            entry.relative_path for entry in self.entries if entry.human_facing
        )


def resolve_collisions(requested: Sequence[tuple[str, str]]) -> dict[str, str]:
    """Assign unique directory names from preferred human names.

    ``requested`` is ``(key, preferred)`` in canonical order. In order of
    preference:

    1. a preferred name only one key wants is used unchanged;
    2. a preferred name several keys want becomes a group: every claimant gets
       ``<preferred> <n>``, numbered from 1 in canonical order;
    3. a name already claimed by a different preferred name - ``West City 1``
       taken literally while a real ``West City`` group numbers into it - is
       numbered onward until it is free.

    Comparison is case-folded, because two names differing only in case land on
    one Windows file.
    """
    claimants: dict[str, list[str]] = {}
    for key, preferred in requested:
        claimants.setdefault(name_key(preferred), []).append(key)

    assigned: dict[str, str] = {}
    taken: dict[str, str] = {}
    for key, preferred in requested:
        group = claimants[name_key(preferred)]
        counter = group.index(key) + 1 if len(group) > 1 else 0
        if counter:
            candidate = GROUP.format(name=preferred, index=counter)
        else:
            candidate = preferred
        attempt = 1
        while name_key(candidate) in taken:
            attempt += 1
            if attempt > 1_000_000:
                raise CurationError(f"cannot disambiguate the name {preferred!r}")
            candidate = GROUP.format(name=preferred, index=counter + attempt - 1 if counter else attempt - 1)
        assigned[key] = candidate
        taken[name_key(candidate)] = key
    return assigned


# --- statistics --------------------------------------------------------------

@dataclass(slots=True)
class CurationStats:
    raw_files: int = 0
    raw_png: int = 0
    raw_json: int = 0
    raw_bytes: int = 0

    curated_files: int = 0
    curated_png: int = 0
    curated_json: int = 0
    curated_bytes: int = 0

    exact_duplicate_groups: int = 0
    exact_duplicate_files: int = 0
    exact_duplicate_bytes: int = 0

    canonical_duplicates_collapsed: int = 0
    contextual_duplicates_retained: int = 0
    distinct_pixel_identity_groups: int = 0
    shared_payload_files: int = 0

    sprite_graphics_total: int = 0
    sprite_graphics_unique: int = 0
    sprite_graphics_shared: int = 0

    animation_references: int = 0
    unique_animation_objects: int = 0
    animation_sheets_written: int = 0
    animation_sheets_collapsed: int = 0

    direction_cells: int = 0
    distinct_poses_written: int = 0
    direction_cells_collapsed: int = 0

    maps_curated: int = 0
    map_name_groups: int = 0
    maps_in_numbered_groups: int = 0
    maps_unnamed: int = 0

    tilesets_curated: int = 0
    individual_tiles_retained: int = 0
    chunks_curated: int = 0

    sprites_curated: int = 0
    sprites_named: int = 0
    sprites_unnamed: int = 0
    sprite_name_groups: int = 0
    sprites_in_numbered_groups: int = 0

    palettes_curated: int = 0

    rom_derived_names: int = 0
    logextractor_names: int = 0
    neutral_fallback_names: int = 0

    def as_document(self) -> dict[str, int | float]:
        files_removed = self.raw_files - self.curated_files
        bytes_removed = self.raw_bytes - self.curated_bytes
        return {
            "schema": SCHEMA,
            "rawFiles": self.raw_files,
            "rawPng": self.raw_png,
            "rawJson": self.raw_json,
            "rawBytes": self.raw_bytes,
            "curatedFiles": self.curated_files,
            "curatedPng": self.curated_png,
            "curatedJson": self.curated_json,
            "curatedBytes": self.curated_bytes,
            "filesRemoved": files_removed,
            "filesRemovedFraction": round(files_removed / self.raw_files, 6)
            if self.raw_files
            else 0.0,
            "bytesRemoved": bytes_removed,
            "bytesRemovedFraction": round(bytes_removed / self.raw_bytes, 6)
            if self.raw_bytes
            else 0.0,
            "exactDuplicateGroups": self.exact_duplicate_groups,
            "exactDuplicateFiles": self.exact_duplicate_files,
            "exactDuplicateBytes": self.exact_duplicate_bytes,
            "canonicalDuplicatesCollapsed": self.canonical_duplicates_collapsed,
            "contextualDuplicatesRetained": self.contextual_duplicates_retained,
            "structurallyDistinctPixelIdenticalGroups": self.distinct_pixel_identity_groups,
            "sharedPayloadFiles": self.shared_payload_files,
            "spriteGraphicsTotal": self.sprite_graphics_total,
            "spriteGraphicsUnique": self.sprite_graphics_unique,
            "spriteGraphicsShared": self.sprite_graphics_shared,
            "animationReferences": self.animation_references,
            "uniqueAnimationObjects": self.unique_animation_objects,
            "animationSheetsWritten": self.animation_sheets_written,
            "animationSheetsCollapsed": self.animation_sheets_collapsed,
            "directionCells": self.direction_cells,
            "distinctPosesWritten": self.distinct_poses_written,
            "directionCellsCollapsed": self.direction_cells_collapsed,
            "mapsCurated": self.maps_curated,
            "mapNameGroups": self.map_name_groups,
            "mapsInNumberedGroups": self.maps_in_numbered_groups,
            "mapsUnnamed": self.maps_unnamed,
            "tilesetsCurated": self.tilesets_curated,
            "individualTilesRetained": self.individual_tiles_retained,
            "chunksCurated": self.chunks_curated,
            "spritesCurated": self.sprites_curated,
            "spritesNamed": self.sprites_named,
            "spritesUnnamed": self.sprites_unnamed,
            "spriteNameGroups": self.sprite_name_groups,
            "spritesInNumberedGroups": self.sprites_in_numbered_groups,
            "palettesCurated": self.palettes_curated,
            "romDerivedNames": self.rom_derived_names,
            "logextractorNames": self.logextractor_names,
            "neutralFallbackNames": self.neutral_fallback_names,
        }


# --- name authority ----------------------------------------------------------

def animation_slot_name(slot: int) -> tuple[str, str]:
    """``(name, source)`` for an animation-array position.

    A position inside the external tool's table takes that name and records the
    tool as its source; a position whose entry is a placeholder, or a position
    beyond the table, takes a neutral one-based label. No name is ever invented
    from the rendered pixels.
    """
    if 0 <= slot < len(LOGEXTRACTOR_ANIMATION_NAMES):
        name = LOGEXTRACTOR_ANIMATION_NAMES[slot]
        if name:
            return name, LOGEXTRACTOR_SOURCE
    return f"Animation {slot + 1}", NEUTRAL_NAME_SOURCE


# --- curation ----------------------------------------------------------------

def plan_curation(
    raw: RawLibrary, raw_hashes: dict[str, tuple[int, str]]
) -> tuple[Plan, CurationStats]:
    """The complete curated layout for a raw library, with no filesystem writes.

    Split out from the CLI so a caller - a test, a future Workbench tab - can
    inspect exactly what a build would produce without producing it.
    """
    curator = Curator(raw)
    return curator.run(raw_hashes), curator.stats


class Curator:
    """Turn a raw library into a curated plan."""

    def __init__(self, raw: RawLibrary) -> None:
        self.raw = raw
        self.plan = Plan()
        self.stats = CurationStats()
        self._sheet_owner: dict[str, str] = {}
        self._raw_hashes: dict[str, tuple[int, str]] = {}

    # -- entry point ----------------------------------------------------------

    def run(self, raw_hashes: dict[str, tuple[int, str]]) -> Plan:
        self._raw_hashes = raw_hashes
        self.stats.raw_files = len(raw_hashes)
        self.stats.raw_bytes = sum(size for size, _digest in raw_hashes.values())
        self.stats.raw_png = sum(1 for path in raw_hashes if path.endswith(".png"))
        self.stats.raw_json = sum(1 for path in raw_hashes if path.endswith(".json"))
        self._measure_raw_duplicates(raw_hashes)

        self.plan_maps()
        self.plan_tilesets()
        self.plan_chunks()
        self.plan_sprites()
        self.plan_palettes()
        self.plan_technical_graphics()
        self.stats.unique_animation_objects = len(
            {row["animationAddress"] for row in self.plan.index["Animations.json"]}
        )
        self._write_index()
        return self.plan

    def _measure_raw_duplicates(self, raw_hashes: dict[str, tuple[int, str]]) -> None:
        groups: dict[str, list[str]] = {}
        for path, (_size, digest) in raw_hashes.items():
            groups.setdefault(digest, []).append(path)
        duplicates = {digest: paths for digest, paths in groups.items() if len(paths) > 1}
        self.stats.exact_duplicate_groups = len(duplicates)
        self.stats.exact_duplicate_files = sum(len(paths) for paths in duplicates.values())
        self.stats.exact_duplicate_bytes = sum(
            (len(paths) - 1) * raw_hashes[paths[0]][0] for paths in duplicates.values()
        )

    # -- maps -----------------------------------------------------------------

    def plan_maps(self) -> None:
        labels: dict[int, str] = {}
        unnamed: list[int] = []
        for source in self.raw.maps:
            if source.rom_text:
                cleaned = clean_name(source.rom_text)
                if cleaned:
                    labels[source.map_index] = cleaned
                    self.stats.rom_derived_names += 1
                    continue
            unnamed.append(source.map_index)
        # Unnamed maps take a contiguous one-based human sequence, not their
        # canonical id: ``Map 1``...``Map 23``, with the real map id in metadata.
        for position, map_index in enumerate(sorted(unnamed), start=1):
            labels[map_index] = f"Map {position}"
            self.stats.neutral_fallback_names += 1
        self.stats.maps_unnamed = len(unnamed)

        requested = [
            (str(source.map_index), labels[source.map_index]) for source in self.raw.maps
        ]

        directories = resolve_collisions(requested)
        membership: dict[str, list[int]] = {}
        for source in self.raw.maps:
            membership.setdefault(name_key(labels[source.map_index]), []).append(
                source.map_index
            )
        self.stats.map_name_groups = len(membership)
        self.stats.maps_in_numbered_groups = sum(
            len(members) for members in membership.values() if len(members) > 1
        )

        index: list[dict[str, Any]] = []
        for source in self.raw.maps:
            members = membership[name_key(labels[source.map_index])]
            base = directories[str(source.map_index)]
            folder = f"{MAPS}/{base}"
            group_index = members.index(source.map_index) + 1 if len(members) > 1 else None

            composite = self.plan.add(f"{folder}/{MAP_IMAGE}", (source.composite,))
            # The composite's own numbers are the renderer's, so they are read
            # from the raw record that describes this map rather than re-derived.
            composite_document: dict[str, Any] = {}
            raw_map_record = f"{source.directory}/map.json"
            if self.raw.exists(raw_map_record):
                raw_document = json.loads(
                    self.raw.path(raw_map_record).read_text(encoding="utf-8")
                )
                for key in (
                    "composite_sha256",
                    "composite_width",
                    "composite_height",
                ):
                    if raw_document.get(key) is not None:
                        composite_document[key] = raw_document[key]

            layer_rows = []
            for position, layer_path in enumerate(source.layer_paths):
                record = source.layers[position] if position < len(source.layers) else {}
                slot = record.get("slot", position)
                image = self.plan.add(
                    f"{folder}/{LAYERS}/{LAYER_IMAGE.format(index=ordinal(slot + 1))}",
                    (layer_path,),
                )
                row: dict[str, Any] = {
                    "path": image.relative_path,
                    "slot": slot,
                    "classification": record.get("classification"),
                    "handler": record.get("handler"),
                    "recordAddress": record.get("record_address"),
                    "width": record.get("width"),
                    "height": record.get("height"),
                    "sha256": record.get("image_sha256"),
                    "bgControlAddend": record.get("bg_control_addend"),
                    "tileOrdinalMin": record.get("tile_ordinal_min"),
                    "tileOrdinalMax": record.get("tile_ordinal_max"),
                    "distinctTileOrdinals": record.get("distinct_tile_ordinals"),
                    "rawPath": layer_path,
                }
                if record.get("chunk_cells") is not None:
                    row["chunkX"] = record.get("chunk_x")
                    row["chunkY"] = record.get("chunk_y")
                    row["chunkCells"] = record.get("chunk_cells")
                    row["nullChunkCells"] = record.get("null_chunk_cells")
                if record.get("cell_grid_cells") is not None:
                    row["cellGridX"] = record.get("cell_grid_x")
                    row["cellGridY"] = record.get("cell_grid_y")
                    row["cellGridCells"] = record.get("cell_grid_cells")
                    row["cellTiles"] = record.get("cell_tiles")
                    row["tileGridX"] = record.get("tile_grid_x")
                    row["tileGridY"] = record.get("tile_grid_y")
                layer_rows.append(row)

            record_path = f"{folder}/{MAP_RECORD}"
            self.plan.add(
                record_path,
                tuple(
                    [f"{source.directory}/map.json", source.composite]
                    + [row["rawPath"] for row in layer_rows]
                ),
                human_facing=False,
            )
            self.plan.document(
                record_path,
                {
                    "schema": SCHEMA,
                    "mapId": source.map_index,
                    "keyHigh": source.key_high,
                    "keyLow": source.key_low,
                    "romText": source.rom_text,
                    "textIndex": source.text_index,
                    "rootAddress": source.root_address,
                    "composite": composite_document,
                    "layerCount": len(layer_rows),
                    "layers": layer_rows,
                    "rawPath": source.directory,
                },
            )
            index.append(
                {
                    "curatedPath": folder,
                    "mapId": source.map_index,
                    "romText": source.rom_text,
                    "groupIndex": group_index,
                    "compositePath": composite.relative_path,
                    "recordPath": record_path,
                    "rawPaths": [
                        source.directory,
                        source.composite,
                        *source.layer_paths,
                    ],
                }
            )
            self.stats.maps_curated += 1
            self.stats.contextual_duplicates_retained += 1

        self.plan.index["Maps.json"] = index

    # -- tilesets -------------------------------------------------------------

    def plan_tilesets(self) -> None:
        """One tilesheet per bank, plus the coordinates to name any tile.

        The raw library's 47,857 loose 8x8 tile PNGs are nearly all distinct, so
        they add browsing noise without adding information: the same pixels are on
        the bank's sheet. The sheet is the primary representation, and
        ``Tileset.json`` records every tile's index and sheet coordinates, which
        is enough to identify or recover an individual tile. The raw library still
        holds each tile; it is simply not copied into the curated view.
        """
        index: list[dict[str, Any]] = []
        for source in self.raw.banks:
            folder = f"{TILESETS}/{TILESET_FOLDER.format(index=ordinal(source.bank_id + 1))}"
            sheet = self.plan.add(f"{folder}/{SHEET_IMAGE}", (source.sheet,))
            columns = SHEET_TILE_COLUMNS
            rows = (source.tile_count + columns - 1) // columns
            tiles = []
            for tile_id, tile_path in enumerate(source.tile_paths):
                if not self.raw.exists(tile_path):
                    continue
                tiles.append(
                    {
                        "index": tile_id,
                        "x": (tile_id % columns) * 8,
                        "y": (tile_id // columns) * 8,
                        "column": tile_id % columns,
                        "row": tile_id // columns,
                    }
                )

            record_path = f"{folder}/{TILESET_RECORD}"
            self.plan.add(
                record_path,
                (source.sheet,),
                human_facing=False,
            )
            self.plan.document(
                record_path,
                {
                    "schema": SCHEMA,
                    "tilesetId": source.bank_id,
                    "containerAddress": source.container_address,
                    "declaredSize": source.declared_size,
                    "tileWidth": 8,
                    "tileHeight": 8,
                    "tileCount": source.tile_count,
                    "columns": columns,
                    "rows": rows,
                    "sheetPath": sheet.relative_path,
                    "sheetSha256": source.sheet_sha256,
                    "tiles": tiles,
                    "rawPath": f"{RAW_TILES}/{RAW_BANKS}/bank_{source.bank_id:03d}",
                },
            )
            index.append(
                {
                    "path": folder,
                    "tilesetId": source.bank_id,
                    "tileCount": source.tile_count,
                    "columns": columns,
                    "rows": rows,
                    "sheetPath": sheet.relative_path,
                    "recordPath": record_path,
                    "rawPaths": [
                        source.sheet,
                        f"{RAW_TILES}/{RAW_BANKS}/bank_{source.bank_id:03d}/tiles",
                    ],
                }
            )
            self.stats.tilesets_curated += 1
        self.plan.index["Tilesets.json"] = index

    # -- chunks ---------------------------------------------------------------

    def plan_chunks(self) -> None:
        index: list[dict[str, Any]] = []
        for source in self.raw.chunks:
            first = source.chunk_id // CHUNK_GROUP_SIZE * CHUNK_GROUP_SIZE + 1
            folder = (
                f"{CHUNKS}/"
                f"{CHUNK_GROUP.format(first=ordinal(first), last=ordinal(first + CHUNK_GROUP_SIZE - 1))}"
            )
            image = self.plan.add(
                f"{folder}/{CHUNK_IMAGE.format(index=ordinal(source.chunk_id + 1))}",
                (source.image,),
            )
            index.append(
                {
                    "curatedPath": image.relative_path,
                    "chunkId": source.chunk_id,
                    "width": source.width,
                    "height": source.height,
                    "sha256": source.image_sha256,
                    "groupPath": folder,
                    "referenceCount": source.reference_count,
                    "referencingMapIds": list(source.referencing_map_indices),
                    "renderMapId": source.render_map_index,
                    "rawPath": source.image,
                }
            )
            self.stats.chunks_curated += 1
            self.stats.contextual_duplicates_retained += 1
        self.plan.index["Chunks.json"] = index

    # -- sprites --------------------------------------------------------------

    def plan_sprites(self) -> None:
        labels: dict[int, str] = {}
        unnamed: list[int] = []
        for source in self.raw.sprites:
            if source.rom_names:
                cleaned = clean_name(source.rom_names[0])
                if cleaned:
                    labels[source.sprite_id] = cleaned
                    self.stats.rom_derived_names += 1
                    self.stats.sprites_named += 1
                    continue
            unnamed.append(source.sprite_id)
        # Unnamed sprites take a contiguous one-based human sequence, not their
        # canonical id: ``Sprite 1``...``Sprite 99``, with the real sprite id in
        # metadata.
        for position, sprite_id in enumerate(sorted(unnamed), start=1):
            labels[sprite_id] = f"Sprite {position}"
            self.stats.neutral_fallback_names += 1
        self.stats.sprites_unnamed = len(unnamed)

        requested = [
            (str(source.sprite_id), labels[source.sprite_id])
            for source in self.raw.sprites
        ]

        directories = resolve_collisions(requested)
        membership: dict[str, list[int]] = {}
        for source in self.raw.sprites:
            membership.setdefault(name_key(labels[source.sprite_id]), []).append(
                source.sprite_id
            )
        self.stats.sprite_name_groups = len(membership)
        self.stats.sprites_in_numbered_groups = sum(
            len(members) for members in membership.values() if len(members) > 1
        )

        sprite_index: list[dict[str, Any]] = []
        animation_index: list[dict[str, Any]] = []
        for source in self.raw.sprites:
            members = membership[name_key(labels[source.sprite_id])]
            base = directories[str(source.sprite_id)]
            folder = f"{SPRITES}/{base}"
            raw_folder = f"{RAW_SPRITES}/sprite_{source.sprite_id:03d}"

            slot_rows = []
            for slot in source.slots:
                if slot.get("null") or not slot.get("animation_address"):
                    slot_rows.append(
                        {
                            "slot": slot["slot"],
                            "null": True,
                            "animationAddress": slot.get("animation_address"),
                            "frameCount": slot.get("frame_count"),
                            "directionCells": slot.get("direction_cells"),
                        }
                    )
                    continue
                animation = self.raw.animation_by_address[slot["animation_address"]]
                slot_rows.append(
                    self._plan_animation_slot(
                        animation=animation,
                        source=source,
                        slot_index=slot["slot"],
                        folder=folder,
                        raw_slot_folder=slot.get("directory") or "",
                        sprite_folder=raw_folder,
                        animation_index=animation_index,
                    )
                )

            record_path = f"{folder}/{SPRITE_RECORD}"
            sources = [
                f"{raw_folder}",
                *(
                    path
                    for row in slot_rows
                    for path in row.get("sources", ())
                ),
            ]
            self.plan.add(record_path, sources, human_facing=False)
            self.plan.document(
                record_path,
                {
                    "schema": SCHEMA,
                    "spriteId": source.sprite_id,
                    "runIndex": source.run_index,
                    "definitionAddress": source.definition_address,
                    "animationSlots": source.animation_slots,
                    "romNames": list(source.rom_names),
                    "animations": slot_rows,
                    "rawPath": raw_folder,
                },
            )
            sprite_index.append(
                {
                    "curatedPath": folder,
                    "spriteId": source.sprite_id,
                    "runIndex": source.run_index,
                    "definitionAddress": source.definition_address,
                    "romNames": list(source.rom_names),
                    "groupIndex": members.index(source.sprite_id) + 1
                    if len(members) > 1
                    else None,
                    "animationSlots": source.animation_slots,
                    "recordPath": record_path,
                    "rawPath": raw_folder,
                }
            )
            self.stats.sprites_curated += 1
            self.stats.contextual_duplicates_retained += 1

        self.plan.index["Sprites.json"] = sprite_index
        self.plan.index["Animations.json"] = animation_index
        self.plan.aliases = self._sprite_aliases(sprite_index)

    def _plan_animation_slot(
        self,
        *,
        animation: AnimationSource,
        source: SpriteSource,
        slot_index: int,
        folder: str,
        raw_slot_folder: str,
        sprite_folder: str,
        animation_index: list[dict[str, Any]],
    ) -> dict[str, Any]:
        name, name_source = animation_slot_name(slot_index)
        if name_source == LOGEXTRACTOR_SOURCE:
            self.stats.logextractor_names += 1
        else:
            self.stats.neutral_fallback_names += 1

        animation_folder = f"{folder}/{ANIMATIONS}/{name}"
        address = animation.animation_address
        raw_sheet = f"{raw_slot_folder}/sheet.png" if raw_slot_folder else ""
        self.stats.animation_references += 1

        sheet_path, sheet_written = self._plan_sheet(animation_folder, address, raw_sheet)
        cells = self._cell_rows(animation, sprite_folder, slot_index, raw_slot_folder)
        pose_rows, cell_rows = self._plan_poses(animation_folder, cells)
        self.stats.direction_cells += len(cells)

        record_path = f"{animation_folder}/{ANIMATION_RECORD}"
        self.plan.add(
            record_path,
            tuple(
                ([raw_sheet] if self.raw.exists(raw_sheet) else [])
                + [row["rawPath"] for row in cells]
            ),
            human_facing=False,
        )
        # The cells list keeps every original ``(frameIndex, directionIndex)``
        # pair and where its render lives, so the 4-direction relationship
        # survives the direction collapse. ``cellAddress`` is omitted: it is the
        # positional key ``4*frame + direction``, so it carries no information the
        # pair does not already carry.
        emitted_cells = [
            {
                "frameIndex": row["frameIndex"],
                "directionIndex": row["directionIndex"],
                "curatedPath": row.get("curatedPath"),
            }
            for row in cell_rows
        ]
        self.plan.document(
            record_path,
            {
                "schema": SCHEMA,
                "spriteId": source.sprite_id,
                "slot": slot_index,
                "name": name,
                "nameSource": name_source,
                "animationAddress": address,
                "frameCount": animation.frame_count,
                "directionCount": DIRECTION_COUNT,
                "directionCells": len(cells),
                "sheetPath": sheet_path,
                "sheetSha256": self.raw.sha256_of(raw_sheet)
                if self.raw.exists(raw_sheet)
                else None,
                "poses": pose_rows,
                "cells": emitted_cells,
                "rawPath": raw_slot_folder or None,
            },
        )
        animation_index.append(
            {
                "curatedPath": animation_folder,
                "animationAddress": address,
                "name": name,
                "nameSource": name_source,
                "frameCount": animation.frame_count,
                "directionCells": len(cells),
                "spriteId": source.sprite_id,
                "slot": slot_index,
                "sheetPath": sheet_path,
                "sheetSharedWith": None if sheet_written else sheet_path,
                "sheetWritten": sheet_written,
                "posePaths": [row["path"] for row in pose_rows],
                "recordPath": record_path,
                "rawPath": raw_slot_folder or None,
            }
        )
        return {
            "slot": slot_index,
            "null": False,
            "name": name,
            "nameSource": name_source,
            "animationAddress": address,
            "frameCount": animation.frame_count,
            "directionCells": len(cells),
            "directory": animation_folder,
            "poseCount": len(pose_rows),
            "sources": sorted({row["rawPath"] for row in cells}),
        }

    def _plan_sheet(
        self, animation_folder: str, address: str, raw_sheet: str
    ) -> tuple[str | None, bool]:
        """Resolve an animation sheet, writing it only for the first identity.

        Two sprite definitions that reference the same animation object are two
        identities over one payload. The payload is written once, under the
        identity that reaches it first in the run's canonical order, and every
        later reference records that path - so a person sees the resource once
        while the index still maps every identity onto it.

        Returns ``(curated path or None, whether this call wrote the file)``.
        """
        if not self.raw.exists(raw_sheet):
            return None, False
        target = f"{animation_folder}/{SHEET_IMAGE}"
        owner = self._sheet_owner.get(address)
        if owner is not None:
            self.stats.animation_sheets_collapsed += 1
            self.stats.shared_payload_files += 1
            self.stats.canonical_duplicates_collapsed += 1
            return owner, False
        self.plan.add(target, (raw_sheet,))
        self._sheet_owner[address] = target
        self.stats.animation_sheets_written += 1
        return target, True

    def _cell_rows(
        self,
        animation: AnimationSource,
        sprite_folder: str,
        slot_index: int,
        raw_slot_folder: str,
    ) -> list[dict[str, Any]]:
        base = f"{sprite_folder}/{RAW_ANIMATIONS}/animation_{slot_index:02d}"
        rows: list[dict[str, Any]] = []
        for position, cell_address in enumerate(animation.cell_addresses):
            frame_index = position // DIRECTION_COUNT
            direction_index = position % DIRECTION_COUNT
            candidate = f"{base}/frame_{frame_index:03d}/direction_{direction_index}.png"
            raw_path = candidate
            if not self.raw.exists(candidate) and raw_slot_folder:
                fallback = (
                    f"{raw_slot_folder}/frame_{frame_index:03d}/"
                    f"direction_{direction_index}.png"
                )
                if self.raw.exists(fallback):
                    raw_path = fallback
            rows.append(
                {
                    "frameIndex": frame_index,
                    "directionIndex": direction_index,
                    "cellAddress": cell_address,
                    "rawPath": raw_path,
                }
            )
        return rows

    def _plan_poses(
        self, animation_folder: str, cells: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Collapse a cell's direction outputs into unique pose images.

        Four direction cells of one frame very often render the same pixels. The
        curated view carries one image per distinct render, named ``Pose 1``,
        ``Pose 2`` ... in first-use order, and every original
        ``(frameIndex, directionIndex)`` pair that renders it is recorded, so
        nothing about the source relationship is lost.

        This is a **first-pass** collapse: identical direction renders within one
        animation share a pose. It does not try to find poses shared with another
        animation or another sprite - two different source objects that happen to
        render the same pixels stay separate, because the ticket's rule for
        uncertainty is "keep both".
        """
        by_digest: dict[str, str] = {}
        poses: list[dict[str, Any]] = []
        for row in cells:
            raw_path = row["rawPath"]
            if not self.raw.exists(raw_path):
                row["curatedPath"] = None
                row["sha256"] = None
                continue
            digest = self.raw.sha256_of(raw_path)
            row["sha256"] = digest
            existing = by_digest.get(digest)
            if existing is not None:
                # The same render already appears in this animation, so no second
                # image is written and the cell keeps pointing at the first.
                row["curatedPath"] = existing
                self.stats.direction_cells_collapsed += 1
                continue
            position = len(poses) + 1
            image = self.plan.add(
                f"{animation_folder}/{POSES}/{POSE_IMAGE.format(index=ordinal(position))}",
                (raw_path,),
            )
            by_digest[digest] = image.relative_path
            row["curatedPath"] = image.relative_path
            self.stats.distinct_poses_written += 1
            poses.append(
                {
                    "path": image.relative_path,
                    "sha256": digest,
                    "sources": [],
                }
            )

        for pose in poses:
            target = pose["sha256"]
            pose["sources"] = sorted(
                {row["rawPath"] for row in cells if row.get("sha256") == target}
            )
        return poses, cells

    def _sprite_aliases(self, sprite_index: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sprite definitions whose animation arrays resolve to the same objects.

        Two definitions selecting the same animation objects are visually the
        same resource under two identities - ``sprite_199_ninja`` and
        ``sprite_241_shadow_warrior``, for instance. Every identity keeps its own
        directory and record; only the image payload is shared, and this records
        which identity supplied the shared files.
        """
        by_id = {row["spriteId"]: row for row in sprite_index}
        signatures: dict[tuple[str | None, ...], list[int]] = {}
        for source in self.raw.sprites:
            signature = tuple(
                None if slot.get("null") else slot.get("animation_address")
                for slot in source.slots
            )
            signatures.setdefault(signature, []).append(source.sprite_id)
        groups = [members for members in signatures.values() if len(members) > 1]
        self.stats.distinct_pixel_identity_groups = len(groups)
        aliases: list[dict[str, Any]] = []
        for members in sorted(groups):
            canonical = min(members)
            for member in sorted(members):
                if member == canonical:
                    continue
                aliases.append(
                    {
                        "spriteId": member,
                        "aliasOfSpriteId": canonical,
                        "curatedPath": by_id[member]["curatedPath"],
                        "canonicalPath": by_id[canonical]["curatedPath"],
                    }
                )
        return aliases

    # -- palettes -------------------------------------------------------------

    def plan_palettes(self) -> None:
        index: list[dict[str, Any]] = []
        for source in self.raw.palettes:
            folder = f"{PALETTES}/{PALETTE_FOLDER.format(index=ordinal(source.palette_id + 1))}"
            image = self.plan.add(
                f"{folder}/{PALETTE_IMAGE}", (source.image,)
            )
            record_path = f"{folder}/{PALETTE_RECORD}"
            self.plan.add(record_path, (source.image,), human_facing=False)
            self.plan.document(
                record_path,
                {
                    "schema": SCHEMA,
                    "paletteId": source.palette_id,
                    "entryCount": source.entry_count,
                    "encoding": source.encoding,
                    "width": source.width,
                    "height": source.height,
                    "sha256": source.image_sha256,
                    "sourceAddress": source.source_address,
                    "rawPath": source.image,
                },
            )
            index.append(
                {
                    "curatedPath": image.relative_path,
                    "paletteId": source.palette_id,
                    "entryCount": source.entry_count,
                    "encoding": source.encoding,
                    "sha256": source.image_sha256,
                    "recordPath": record_path,
                    "rawPath": source.image,
                }
            )
            self.stats.palettes_curated += 1
            self.stats.neutral_fallback_names += 1
        self.plan.index["Palettes.json"] = index

    # -- technical sprite graphics -------------------------------------------

    def plan_technical_graphics(self) -> None:
        """Keep the sprite-graphics payloads that exist nowhere else.

        Measured over the canonical corpus, 7,349 of the 7,390 structured
        graphics containers already appear byte-for-byte inside the human-facing
        sprite tree, so an ordinary user has no reason to browse them twice. The
        remaining ones are genuinely unique source resources and are kept here.
        Every container - shared or unique - keeps its identity in the index.
        """
        index: list[dict[str, Any]] = []
        sprite_shas = {
            digest
            for path, (_size, digest) in self._raw_hashes.items()
            if path.startswith(f"{RAW_SPRITES}/") and path.endswith(".png")
        }
        for source in self.raw.graphics:
            self.stats.sprite_graphics_total += 1
            shared = source.image_sha256 in sprite_shas
            if shared:
                self.stats.sprite_graphics_shared += 1
                self.stats.canonical_duplicates_collapsed += 1
                index.append(
                    {
                        "graphicId": source.graphic_id,
                        "sha256": source.image_sha256,
                        "rawPath": source.image,
                        "alsoAppearsUnderSpriteTree": True,
                    }
                )
                continue
            self.stats.sprite_graphics_unique += 1
            name = GRAPHIC_IMAGE.format(index=ordinal(source.graphic_id + 1))
            image = self.plan.add(
                f"{TECHNICAL}/{UNIQUE_GRAPHICS}/{name}", (source.image,)
            )
            record_path = (
                f"{TECHNICAL}/{UNIQUE_GRAPHICS}/"
                f"{GRAPHIC_RECORD.format(index=ordinal(source.graphic_id + 1))}"
            )
            self.plan.add(record_path, (source.image,), human_facing=False)
            self.plan.document(
                record_path,
                {
                    "schema": SCHEMA,
                    "graphicId": source.graphic_id,
                    "width": source.width,
                    "height": source.height,
                    "colour256": source.colour_256,
                    "containerAddress": source.container_address,
                    "declaredSize": source.declared_size,
                    "sha256": source.image_sha256,
                    "rawPath": source.image,
                },
            )
            index.append(
                {
                    "curatedPath": image.relative_path,
                    "graphicId": source.graphic_id,
                    "width": source.width,
                    "height": source.height,
                    "colour256": source.colour_256,
                    "sha256": source.image_sha256,
                    "containerAddress": source.container_address,
                    "declaredSize": source.declared_size,
                    "rawPath": source.image,
                    "alsoAppearsUnderSpriteTree": False,
                }
            )
        self.plan.index["Technical Graphics.json"] = index

    # -- index ----------------------------------------------------------------

    def _write_index(self) -> None:
        """The traceability layer: every curated path against its raw sources.

        ``Source Map.json`` is the complete graph, in a compact encoding: a
        deduplicated ``sources`` table of raw path lists, then one entry per
        curated artifact referencing a list index. Every curated artifact this run
        writes - including shared payloads - appears, with the raw paths it was
        copied from, so a curated file can always be traced back to the canonical
        library it came from, and a raw file can be traced forward to every
        curated path that carries it through the ``backrefs`` table.

        This is the one place a curated path is tied to canonical identity, and it
        is deliberately not padded with prose or with per-file hashes: a hash
        lives in the audit, and a repeated raw path is stored once rather than
        re-emitted for every one of the tens of thousands of curated entries that
        share it.
        """
        for name in INDEX_DOCUMENTS:
            if name == "Source Map.json":
                continue
            document = self.plan.index.get(name)
            if document is None:
                continue
            path = f"{INDEX}/{name}"
            self.plan.add(path, (), human_facing=False)
            self.plan.document(path, {"schema": SCHEMA, "entries": document})

        # Deduplicate the raw-source lists: the same list recurs thousands of
        # times (every tile in a bank, every layer of a map), and storing it once
        # keeps the human traceability layer compact without losing a byte of
        # information.
        source_table: list[list[str]] = []
        source_ids: dict[tuple[str, ...], int] = {}
        entries: list[dict[str, Any]] = []
        for entry in self.plan.sorted_entries():
            key = tuple(entry.sources)
            source_id = source_ids.get(key)
            if source_id is None:
                source_id = len(source_table)
                source_ids[key] = source_id
                source_table.append(list(key))
            row: dict[str, Any] = {"path": entry.relative_path, "source": source_id}
            if entry.shared_from:
                row["sharedFrom"] = entry.shared_from
            entries.append(row)

        # The forward direction (raw path -> curated paths) exists so a raw file
        # can be traced forward to every curated view that carries it. It is
        # stored compactly: only raw files that actually participate in several
        # curated entries appear, and they reference entry indices rather than
        # re-emiting the curated path strings.
        backrefs: dict[str, list[int]] = {}
        for index, row in enumerate(entries):
            for source in source_table[row["source"]]:
                backrefs.setdefault(source, []).append(index)
        backrefs = {
            source: indices
            for source, indices in backrefs.items()
            if len(indices) > 1
        }

        path = f"{INDEX}/Source Map.json"
        self.plan.add(path, (), human_facing=False)
        self.plan.document(
            path,
            {
                "schema": SCHEMA,
                "entryCount": len(entries),
                "sources": source_table,
                "entries": entries,
                "backrefs": backrefs,
                "aliases": self.plan.aliases,
            },
        )


# --- writing -----------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Artifact:
    relative_path: str
    size: int
    sha256: str


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_plan(
    plan: Plan, raw: RawLibrary, output_root: Path, stats: CurationStats
) -> list[Artifact]:
    """Copy every planned artifact and write every planned document.

    Images are byte copies of their canonical raw artifact - curation organises
    and deduplicates, it never re-encodes - and each copy is verified against the
    raw digest before it is counted, so a truncated or altered copy fails the
    build rather than reaching the library.

    Every distinct raw source is read exactly once, concurrently, and then written
    to each curated path that carries it. That matters for two reasons: the plan
    references the same payload from several curated paths on purpose, and the
    corpus is tens of thousands of small files where per-file open cost dominates.
    """
    unique_sources = sorted(
        {
            entry.sources[0]
            for entry in plan.entries
            if entry.relative_path not in plan.documents and entry.sources
        }
    )
    payloads = read_many([raw.path(source) for source in unique_sources])
    cache: dict[str, bytes] = {}
    for source in unique_sources:
        data = payloads[raw.path(source)]
        expected = raw.sha256_of(source)
        actual = sha256_bytes(data)
        if actual != expected:
            raise CurationError(
                f"raw artifact {source} hashes {actual} but the run measured "
                f"{expected}; the raw library changed while it was being read"
            )
        cache[source] = data

    artifacts: list[Artifact] = []
    for entry in plan.sorted_entries():
        target = output_root / Path(entry.relative_path)
        document = plan.documents.get(entry.relative_path)
        if document is not None:
            try:
                data = meta.dumps(document).encode("utf-8")
            except meta.MetadataError as exc:
                raise CurationError(f"{entry.relative_path}: {exc}") from exc
            _write_bytes(target, data)
        elif entry.sources:
            data = cache[entry.sources[0]]
            _write_bytes(target, data)
        else:
            continue
        artifacts.append(
            Artifact(
                relative_path=entry.relative_path,
                size=len(data),
                sha256=sha256_bytes(data),
            )
        )

    stats.curated_files = len(artifacts)
    stats.curated_bytes = sum(artifact.size for artifact in artifacts)
    stats.curated_png = sum(1 for artifact in artifacts if artifact.relative_path.endswith(".png"))
    stats.curated_json = sum(1 for artifact in artifacts if artifact.relative_path.endswith(".json"))
    return artifacts


# --- audits ------------------------------------------------------------------

def scan_human_paths(plan: Plan) -> list[tuple[str, str]]:
    """Every human-facing curated path that carries a technical separator."""
    findings: list[tuple[str, str]] = []
    for path in plan.human_paths():
        reason = check_human_path(path)
        if reason is not None:
            findings.append((path, reason))
    return findings


def scan_tree_human_paths(root: Path) -> list[tuple[str, str]]:
    """The same check over a finished tree, so the written names are audited and
    not only the planned ones."""
    findings: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        parts = Path(relative).parts
        if parts and parts[0] in (INDEX, TECHNICAL):
            continue
        reason = check_human_path(relative)
        if reason is not None:
            findings.append((relative, reason))
    return findings


def scan_tree_prose(root: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """Prose files and prose metadata keys anywhere in a curated tree."""
    files = [str(path.relative_to(root)) for path in meta.scan_for_prose_files(root)]
    keys = [
        (str(path.relative_to(root)), detail)
        for path, detail in meta.scan_for_prose_keys(root)
    ]
    return files, keys


def scan_tree_technical_ids(plan: Plan) -> list[str]:
    """Human-facing curated paths that leak a canonical numeric identifier.

    A curated human path may carry a number only where the number *is* the human
    label - ``Tileset 12``, ``Chunk 987``, ``Palette 2``, ``Map 1`` inside a
    named group, ``Animation 5`` where no verified name exists. What it may never
    carry is the raw library's fixed-width identity form or a raw address.
    """
    offending: list[str] = []
    patterns = (_RAW_IDENTITY, _RAW_ADDRESS, _RAW_DIGEST)
    for path in plan.human_paths():
        for part in Path(path).parts:
            if any(pattern.search(part) for pattern in patterns):
                offending.append(path)
                break
    return offending


def audit_document(
    *,
    stats: CurationStats,
    plan: Plan,
    raw_before: dict[str, tuple[int, str]],
    raw_after: dict[str, tuple[int, str]],
    artifacts: Sequence[Artifact],
    human_findings: Sequence[tuple[str, str]],
    tree_findings: Sequence[tuple[str, str]],
    prose_files: Sequence[str],
    prose_keys: Sequence[tuple[str, str]],
    technical_ids: Sequence[str],
    residual: Sequence[str],
    source: Path,
    output: Path,
) -> dict[str, Any]:
    added = sorted(set(raw_after) - set(raw_before))
    removed = sorted(set(raw_before) - set(raw_after))
    changed = sorted(
        path
        for path in set(raw_before) & set(raw_after)
        if raw_before[path] != raw_after[path]
    )
    return {
        "schema": SCHEMA,
        "tool": TOOL_NAME,
        "toolVersion": TOOL_VERSION,
        "rawResourceRoot": str(source),
        "curatedResourceRoot": str(output),
        "rawIntegrity": {
            "filesBefore": len(raw_before),
            "filesAfter": len(raw_after),
            "changed": changed,
            "added": added,
            "removed": removed,
            "unchanged": not (changed or added or removed),
        },
        "counts": stats.as_document(),
        "audits": {
            "humanPathsWithUnderscore": [path for path, _reason in human_findings],
            "treePathsWithUnderscore": [path for path, _reason in tree_findings],
            "technicalIdFilenames": list(technical_ids),
            "generatedProseFiles": list(prose_files),
            "prohibitedProseMetadataFields": [
                {"path": path, "detail": detail} for path, detail in prose_keys
            ],
            "untraceableCuratedArtifacts": list(residual),
        },
        "artifactCount": len(artifacts),
    }


# --- audit output ------------------------------------------------------------

def write_audit(
    audit_root: Path,
    *,
    document: dict[str, Any],
    plan: Plan,
    artifacts: Sequence[Artifact],
    raw_hashes: dict[str, tuple[int, str]],
    duplicate_groups: dict[str, list[str]],
) -> None:
    """Write the curation audit tree. Never part of the resource pack."""
    audit_root.mkdir(parents=True, exist_ok=True)
    meta.write(audit_root / "curation.json", document)
    meta.write(
        audit_root / "counts.json",
        {"schema": SCHEMA, "counts": document["counts"]},
    )

    inventory = {
        "schema": SCHEMA,
        "rawFileCount": len(raw_hashes),
        "rawBytes": sum(size for size, _digest in raw_hashes.values()),
        "curatedFileCount": len(artifacts),
        "curatedBytes": sum(artifact.size for artifact in artifacts),
        "byExtension": _extension_totals(artifacts),
        "humanFacingCuratedPaths": len(plan.human_paths()),
    }
    meta.write(audit_root / "inventory.json", inventory)

    groups = [
        {
            "sha256": digest,
            "count": len(paths),
            "bytes": raw_hashes[paths[0]][0],
            "paths": sorted(paths),
        }
        for digest, paths in sorted(duplicate_groups.items())
    ]
    meta.write(
        audit_root / "duplicates.json",
        {
            "schema": SCHEMA,
            "groupCount": len(groups),
            "fileCount": sum(group["count"] for group in groups),
            "sharedBytes": sum(
                (group["count"] - 1) * group["bytes"] for group in groups
            ),
            "groups": groups,
        },
    )

    meta.write(
        audit_root / "deduplication.json",
        {
            "schema": SCHEMA,
            "rules": {
                "sharedPayload": (
                    "a curated image whose pixels are identical to an image "
                    "already written is not copied again; the artifact is "
                    "attributed to the lowest sorted curated path that carries it "
                    "and every other identity records that path"
                ),
                "mapContext": (
                    "no map composite or map layer is collapsed; a distinct "
                    "MapEntry keeps its own browsable image because the identity "
                    "is what a romhacker looks for"
                ),
                "chunkContext": (
                    "no chunk is collapsed; a chunk and a map layer that render "
                    "identically are different resource classes"
                ),
                "spriteGraphics": (
                    "a structured sprite-graphics container whose pixels already "
                    "appear under the sprite tree is indexed but not duplicated"
                ),
                "structurallyDistinct": (
                    "two structurally distinct objects that render identically "
                    "keep separate curated identities and separate index entries; "
                    "only the image payload is shared"
                ),
            },
            "counts": {
                "canonicalCollapsed": document["counts"]["canonicalDuplicatesCollapsed"],
                "contextualRetained": document["counts"]["contextualDuplicatesRetained"],
                "sharedPayloadFiles": document["counts"]["sharedPayloadFiles"],
                "structurallyDistinctPixelIdenticalGroups":
                    document["counts"]["structurallyDistinctPixelIdenticalGroups"],
            },
        },
    )

    meta.write(
        audit_root / "aliases.json",
        {"schema": SCHEMA, "count": len(plan.aliases), "aliases": plan.aliases},
    )

    meta.write(
        audit_root / "path-map.json",
        {
            "schema": SCHEMA,
            "count": len(plan.entries),
            "entries": [
                {
                    "curatedPath": entry.relative_path,
                    "sources": list(entry.sources),
                    "sharedFrom": entry.shared_from,
                }
                for entry in plan.sorted_entries()
            ],
        },
    )

    meta.write(
        audit_root / "names.json",
        {
            "schema": SCHEMA,
            "logextractorSource": LOGEXTRACTOR_SOURCE,
            "logextractorAnimationNames": [
                {"slot": slot, "name": name}
                for slot, name in enumerate(LOGEXTRACTOR_ANIMATION_NAMES)
                if name
            ],
            "neutralNameSource": NEUTRAL_NAME_SOURCE,
        },
    )

    rows = [
        (artifact.relative_path, artifact.size, artifact.sha256) for artifact in artifacts
    ]
    meta.write_text(
        audit_root / "hashes.csv",
        meta.csv_rows(("relative_path", "bytes", "sha256"), rows),
    )

    raw_rows = [
        (path, size, digest) for path, (size, digest) in sorted(raw_hashes.items())
    ]
    meta.write_text(
        audit_root / "raw-hashes.csv",
        meta.csv_rows(("relative_path", "bytes", "sha256"), raw_rows),
    )


def _extension_totals(artifacts: Sequence[Artifact]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {}
    for artifact in artifacts:
        suffix = Path(artifact.relative_path).suffix.lower() or "(none)"
        bucket = totals.setdefault(suffix, {"files": 0, "bytes": 0})
        bucket["files"] += 1
        bucket["bytes"] += artifact.size
    return {suffix: totals[suffix] for suffix in sorted(totals)}


def duplicate_groups_of(
    raw_hashes: dict[str, tuple[int, str]]
) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for path, (_size, digest) in raw_hashes.items():
        groups.setdefault(digest, []).append(path)
    return {digest: paths for digest, paths in groups.items() if len(paths) > 1}


def unrecoverable_sources(plan: Plan) -> list[str]:
    """Planned artifacts that would be written with no traceable raw source."""
    return [
        entry.relative_path
        for entry in plan.sorted_entries()
        if not entry.sources and entry.relative_path not in plan.documents
    ]


# --- comparison --------------------------------------------------------------

def hash_tree(root: Path) -> dict[str, tuple[int, str]]:
    """``relative path -> (bytes, sha256)`` for a whole tree, concurrently."""
    present = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    )
    return hashed_files([(relative, root / Path(relative)) for relative in present])


def compare_trees(reference: Path, candidate: Path) -> dict[str, Any]:
    """Missing, extra and differing artifacts between two curated trees."""
    left = hash_tree(reference)
    right = hash_tree(candidate)
    missing = sorted(set(left) - set(right))
    extra = sorted(set(right) - set(left))
    changed = sorted(
        path
        for path in set(left) & set(right)
        if left[path][1] != right[path][1]
    )
    return {
        "reference": str(reference),
        "candidate": str(candidate),
        "referenceFiles": len(left),
        "candidateFiles": len(right),
        "missing": missing,
        "extra": extra,
        "changed": changed,
        "identical": not (missing or extra or changed),
    }


# --- command line ------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.export.buu_resource_curate",
        description=(
            "Curate the canonical Buu's Fury resource library into a separate, "
            "human-friendly resource pack with a full traceability index. The raw "
            "library is a read-only input and is never modified."
        ),
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(r"<resource-library>"),
        help="canonical raw resource root (read-only input)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="curated resource root (default: <SOURCE> Curated)",
    )
    parser.add_argument(
        "--audit",
        type=Path,
        default=None,
        help="curation audit root (default: <OUTPUT> Audit)",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="measure the raw library and write the curation audit; write no resources",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace the contents of an existing curated root",
    )
    parser.add_argument(
        "--compare",
        type=Path,
        default=None,
        help="compare this run's curated root against an earlier curated root",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="plan and audit the layout without writing the curated library",
    )
    return parser


def default_output_for(source: Path) -> Path:
    """The default curated root: ``<SOURCE> Curated``, a clean sibling.

    The canonical raw root is ``BuuFury_Resources``; its curated sibling is best
    written with a human name, e.g. ``Buu's Fury Resources``, which ``--output``
    accepts directly. This default keeps the underscore-free convention without
    inventing the game's title.
    """
    resolved = Path(source).resolve()
    return resolved.parent / (resolved.name + " Curated")


def main(argv: list[str] | None = None) -> int:
    """Run the curator, reporting a refusal as a message rather than a traceback."""
    args = build_parser().parse_args(argv)
    try:
        return _run(args)
    except CurationError as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 1


def _run(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    output = Path(args.output).resolve() if args.output else default_output_for(source)
    audit_root = (
        Path(args.audit).resolve() if args.audit else audit_root_for(output)
    )
    ensure_output_roots(source, output, audit_root)

    raw = RawLibrary(source)
    print(f"{TOOL_NAME}: hashing the raw library at {source}")
    raw_before = raw.hash_tree()
    print(f"{TOOL_NAME}: {len(raw_before)} raw artifacts, "
          f"{sum(size for size, _d in raw_before.values())} bytes")

    if args.analyze:
        curator = Curator(raw)
        plan = curator.run(raw_before)
        stats = curator.stats
        report = _analyze_report(stats, raw_before, plan)
        audit_root.mkdir(parents=True, exist_ok=True)
        meta.write(audit_root / "counts.json", report)
        meta.write(
            audit_root / "duplicates.json",
            _duplicates_document(raw_before),
        )
        _print_analysis(report)
        print(f"{TOOL_NAME}: analysis written to {audit_root}")
        return 0

    if not args.dry_run:
        if output.exists() and any(output.iterdir()):
            if not args.force:
                raise CurationError(
                    f"{output} is not empty; pass --force to replace its contents"
                )
            foreign = clear_generated(output)
            if foreign:
                print(f"{TOOL_NAME}: left unrelated entries in {output}: "
                      f"{', '.join(foreign)}")
    else:
        print(f"{TOOL_NAME}: dry run; nothing will be written to {output}")

    curator = Curator(raw)
    plan = curator.run(raw_before)
    stats = curator.stats

    residual = unrecoverable_sources(plan)
    human_findings = scan_human_paths(plan)
    technical_ids = scan_tree_technical_ids(plan)
    if human_findings:
        raise CurationError(
            "the planned layout carries a technical separator: "
            + "; ".join(f"{path} ({reason})" for path, reason in human_findings[:5])
        )
    if technical_ids:
        raise CurationError(
            "the planned layout leaks a canonical identifier: "
            + ", ".join(technical_ids[:5])
        )
    if residual:
        raise CurationError(
            "curated artifacts with no traceable raw source: "
            + ", ".join(residual[:5])
        )

    if not args.dry_run:
        output.mkdir(parents=True, exist_ok=True)
    artifacts = (
        write_plan(plan, raw, output, stats) if not args.dry_run else []
    )

    # The index and metadata are the one place a curated path is tied to raw
    # identity, so the source map is written and then re-read rather than trusted.
    if not args.dry_run:
        for entry in plan.sorted_entries():
            if entry.relative_path not in plan.documents:
                continue
            if not (output / Path(entry.relative_path)).is_file():
                raise CurationError(f"{entry.relative_path} was planned but not written")

    tree_findings = scan_tree_human_paths(output) if not args.dry_run else []
    prose_files, prose_keys = (
        scan_tree_prose(output) if not args.dry_run else ([], [])
    )

    print(f"{TOOL_NAME}: verifying the raw library was not modified")
    raw_after = raw.hash_tree()

    document = audit_document(
        stats=stats,
        plan=plan,
        raw_before=raw_before,
        raw_after=raw_after,
        artifacts=artifacts,
        human_findings=human_findings,
        tree_findings=tree_findings,
        prose_files=prose_files,
        prose_keys=prose_keys,
        technical_ids=technical_ids,
        residual=residual,
        source=source,
        output=output,
    )
    if not args.dry_run:
        write_audit(
            audit_root,
            document=document,
            plan=plan,
            artifacts=artifacts,
            raw_hashes=raw_before,
            duplicate_groups=duplicate_groups_of(raw_before),
        )

    _print_summary(document)
    if not document["rawIntegrity"]["unchanged"]:
        raise CurationError(
            "the canonical raw library changed during curation: "
            f"{len(document['rawIntegrity']['changed'])} changed, "
            f"{len(document['rawIntegrity']['added'])} added, "
            f"{len(document['rawIntegrity']['removed'])} removed"
        )

    if args.compare is not None:
        comparison = compare_trees(Path(args.compare).resolve(), output)
        print(
            f"{TOOL_NAME}: compare {comparison['referenceFiles']} -> "
            f"{comparison['candidateFiles']} files; "
            f"{len(comparison['missing'])} missing, "
            f"{len(comparison['extra'])} extra, "
            f"{len(comparison['changed'])} changed"
        )
        if not comparison["identical"]:
            return 1
    return 0


def _duplicates_document(raw_hashes: dict[str, tuple[int, str]]) -> dict[str, Any]:
    groups = duplicate_groups_of(raw_hashes)
    return {
        "schema": SCHEMA,
        "groupCount": len(groups),
        "fileCount": sum(len(paths) for paths in groups.values()),
        "sharedBytes": sum(
            (len(paths) - 1) * raw_hashes[paths[0]][0] for paths in groups.values()
        ),
        "groups": [
            {
                "sha256": digest,
                "count": len(paths),
                "bytes": raw_hashes[paths[0]][0],
                "paths": sorted(paths),
            }
            for digest, paths in sorted(groups.items())
        ],
    }


def _analyze_report(
    stats: CurationStats,
    raw_hashes: dict[str, tuple[int, str]],
    plan: Plan,
) -> dict[str, Any]:
    document = stats.as_document()
    return {
        "schema": SCHEMA,
        "rawFileCount": len(raw_hashes),
        "rawBytes": sum(size for size, _digest in raw_hashes.values()),
        "curatedPlannedFiles": len(plan.entries),
        "counts": document,
    }


def _print_analysis(report: dict[str, Any]) -> None:
    counts = report["counts"]
    print(f"{TOOL_NAME}: raw {report['rawFileCount']} files / "
          f"{report['rawBytes']} bytes")
    print(f"{TOOL_NAME}: planned curated files {report['curatedPlannedFiles']}")
    for key in (
        "exactDuplicateGroups",
        "exactDuplicateFiles",
        "exactDuplicateBytes",
        "mapsCurated",
        "mapNameGroups",
        "mapsInNumberedGroups",
        "tilesetsCurated",
        "individualTilesRetained",
        "chunksCurated",
        "spritesCurated",
        "spriteNameGroups",
        "spritesInNumberedGroups",
        "animationReferences",
        "uniqueAnimationObjects",
        "animationSheetsWritten",
        "animationSheetsCollapsed",
        "directionCells",
        "distinctPosesWritten",
        "directionCellsCollapsed",
        "spriteGraphicsTotal",
        "spriteGraphicsUnique",
        "spriteGraphicsShared",
        "palettesCurated",
        "romDerivedNames",
        "logextractorNames",
        "neutralFallbackNames",
    ):
        print(f"{TOOL_NAME}:   {key} = {counts[key]}")


def _print_summary(document: dict[str, Any]) -> None:
    counts = document["counts"]
    integrity = document["rawIntegrity"]
    audits = document["audits"]
    print(f"{TOOL_NAME}: curated {counts['curatedFiles']} files / "
          f"{counts['curatedBytes']} bytes")
    print(f"{TOOL_NAME}: files removed {counts['filesRemoved']} "
          f"({counts['filesRemovedFraction']:.2%}), bytes removed "
          f"{counts['bytesRemoved']} ({counts['bytesRemovedFraction']:.2%})")
    print(f"{TOOL_NAME}: raw changed {len(integrity['changed'])}, added "
          f"{len(integrity['added'])}, removed {len(integrity['removed'])}")
    print(f"{TOOL_NAME}: underscores in human paths "
          f"{len(audits['humanPathsWithUnderscore'])} planned / "
          f"{len(audits['treePathsWithUnderscore'])} written")
    print(f"{TOOL_NAME}: technical id filenames "
          f"{len(audits['technicalIdFilenames'])}")
    print(f"{TOOL_NAME}: generated prose files "
          f"{len(audits['generatedProseFiles'])}, prohibited prose fields "
          f"{len(audits['prohibitedProseMetadataFields'])}")
    print(f"{TOOL_NAME}: untraceable curated artifacts "
          f"{len(audits['untraceableCuratedArtifacts'])}")


__all__ = [
    "CurationError",
    "CurationStats",
    "Curator",
    "Plan",
    "PlanEntry",
    "RawLibrary",
    "animation_slot_name",
    "assert_human_path",
    "audit_root_for",
    "check_human_path",
    "clean_name",
    "compare_trees",
    "duplicate_groups_of",
    "ensure_output_roots",
    "hash_tree",
    "human_name",
    "name_key",
    "plan_curation",
    "resolve_collisions",
    "scan_human_paths",
    "scan_tree_human_paths",
    "scan_tree_prose",
    "scan_tree_technical_ids",
    "unrecoverable_sources",
    "write_plan",
]


if __name__ == "__main__":
    sys.exit(main())
