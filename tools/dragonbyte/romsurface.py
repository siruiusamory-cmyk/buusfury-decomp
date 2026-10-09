"""The ROM destination's model: where a number points, what owns these bytes,
what they are, and what changed.

The ROM destination is address-first. It is the one surface in the product where
a raw address is the primary label rather than a diagnostic, because the image
itself is the object under inspection (`docs/desktop-ui.md`, the ROM surface's
exception). Everything below is headless: the page renders these answers and
decides none of them.

Four questions are answered here and nowhere else.

*Where does this number point?* `Go to address` reads a number as an image
address or as a file offset, converts between the two, and says which spelling it
read. The conversion is the SDK's own (`binary.GbaRomAddress`,
`binary.FileOffset`), never a second one; the reported spelling is this module's.

*Who owns these bytes?* S4's `atlas.RangeIndex` answers for the open image, over
the atlas artifact the SDK itself assembles, with the profile's declared extents
as the index's declared layer. The owner predicate is the raw byte authority's
own floor (`rawbytes.blocks_a_write`), so the owners a strip shows and the writes
that are refused cannot disagree: an object below that floor is a known shape,
not an owner. Where the index is not available the surface says so rather than
inventing a classification, and where no owner claims a byte it says `no semantic
owner known` rather than leaving a blank.

*What changed?* The overlay is a set of file offsets: the project's own pending
edits before a build, and exactly the manifest's change set after one. A set and
not a count, because "how many bytes changed" cannot answer "which". Those
pending edits are journal-local: they reach an image only when a build applies
them, and nothing here claims otherwise.

*May these bytes be opened or written?* An extent is proven or it is not, and a
write is offered only while the range index is loaded, because without it the
surface cannot tell bytes a structure owns from bytes nobody owns. Either way the
surface states the reason instead of guessing one.

No Qt is imported: the whole surface is drivable with no window.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Iterable, Mapping

from tools.webfoot.atlas import DECLARED_EXTENT, AtlasError, Confidence, RangeIndex
from tools.webfoot.binary import (
    GBA_ROM_BASE,
    BinaryAddressError,
    FileOffset,
    GbaRomAddress,
)
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import AtlasIdentityMismatch, RomProfile
from tools.webfoot.write import ByteChange, WriteManifest

from .journal import EditJournal
from .rawbytes import blocks_a_write, declared_extents


class SurfaceError(ValueError):
    """The surface could not answer; the message says which input failed and why."""


#: Bytes per row in the byte view. Sixteen is the hex-editor convention and the
#: number the product specification names.
ROM_ROW_BYTES = 16

#: How much of the image the byte view materializes around the caret. A full
#: image is eight million rows and no widget can hold it, so the view streams.
BYTE_VIEW_ROWS = 64

#: Bytes of a coverage span shown as its preview in the range view.
PREVIEW_BYTES = 8

#: Default ceiling on returned search hits, so a one-byte pattern on a real image
#: cannot try to build a table with a million rows in it.
DEFAULT_SEARCH_HITS = 200

#: What the raw search reads, said wherever the answer could be read the other
#: way: the canonical image alone would miss a byte the project authored.
SEARCH_SCOPE = (
    "Searches the current bytes: the canonical image plus pending raw writes."
)

#: The spelling `parse_target` read a number in. The product says which one it
#: was, because a bare number is otherwise ambiguous between the two spaces.
IMAGE_ADDRESS = "image address"
FILE_OFFSET = "file offset"

#: The assembled atlas artifact, located the way the SDK's own atlas commands and
#: the beta session locate it. Named here because the file name is the contract.
ATLAS_FILE = "atlas.jsonl"

#: The byte a preview or an ascii gutter substitutes for anything unprintable.
_NOT_PRINTABLE = "."

#: The article each spelling takes, so the one sentence reads as English.
_ARTICLE = {IMAGE_ADDRESS: "an", FILE_OFFSET: "a"}


def image_address(offset: int, image_size: int) -> int:
    """The image address of one file offset, through the SDK's own typed pair.

    The one place this module converts offset to address, so the conversion and
    the size check are the SDK's rather than a second arithmetic here.
    """
    try:
        return FileOffset(offset).to_gba_address(image_size).raw
    except BinaryAddressError as exc:
        raise SurfaceError(str(exc)) from exc


# --- where a number points ----------------------------------------------------


@dataclass(frozen=True, slots=True)
class RomTarget:
    """One location in the image, in both spellings at once.

    `spelling` is the one the caller actually supplied; both values are computed
    through the SDK's own conversion, so the two can never disagree.
    """

    file_offset: int
    address: int
    spelling: str

    def __post_init__(self) -> None:
        if type(self.file_offset) is not int or self.file_offset < 0:
            raise SurfaceError("a ROM location needs a non-negative file offset")
        if type(self.address) is not int or self.address < 0:
            raise SurfaceError("a ROM location needs a non-negative image address")
        if self.spelling not in (IMAGE_ADDRESS, FILE_OFFSET):
            raise SurfaceError(f"{self.spelling!r} is not a known spelling")

    @property
    def read_as(self) -> str:
        return f"read as {_ARTICLE[self.spelling]} {self.spelling}"

    def text(self) -> str:
        return (
            f"0x{self.address:08X} is file offset 0x{self.file_offset:06X} "
            f"({self.read_as})"
        )


def parse_target(text: str, image_size: int) -> RomTarget:
    """The location `text` names, and which spelling it was read in.

    A number in the GBA ROM window is an image address; anything below that
    window is a file offset. An image larger than the window makes a value
    ambiguous, and the address reading wins, which is the rule the SDK's own
    atlas offset parser already applies - so a number is never silently read in
    the wrong space. Out of the image either way, it is refused.
    """
    if type(image_size) is not int or image_size <= 0:
        raise SurfaceError("image size must be a positive integer")
    supplied = text.strip()
    if not supplied:
        raise SurfaceError("Go to address needs an image address or a file offset.")
    try:
        value = int(supplied, 0)
    except ValueError as exc:
        raise SurfaceError(
            f"{supplied!r} is not an image address or a file offset."
        ) from exc
    if value < 0:
        raise SurfaceError(f"{supplied!r} is not an image address or a file offset.")
    if value >= GBA_ROM_BASE and value - GBA_ROM_BASE < image_size:
        return target_for_address(value, image_size)
    if value < image_size:
        return target_for_offset(value, image_size)
    if value >= GBA_ROM_BASE:
        raise SurfaceError(
            f"image address 0x{value:08X} is outside the {image_size}-byte image."
        )
    raise SurfaceError(
        f"file offset 0x{value:06X} is outside the {image_size}-byte image."
    )


def target_for_offset(offset: int, image_size: int) -> RomTarget:
    """The location at one file offset, with its image address derived."""
    if type(offset) is not int or not 0 <= offset < image_size:
        raise SurfaceError(
            f"file offset 0x{offset:06X} is outside the {image_size}-byte image."
        )
    return RomTarget(
        file_offset=offset,
        address=image_address(offset, image_size),
        spelling=FILE_OFFSET,
    )


def target_for_address(address: int, image_size: int) -> RomTarget:
    """The location at one image address, resolved through the SDK's own type."""
    try:
        offset = GbaRomAddress(address).to_file_offset(image_size)
    except BinaryAddressError as exc:
        raise SurfaceError(str(exc)) from exc
    return RomTarget(
        file_offset=offset,
        address=image_address(offset, image_size),
        spelling=IMAGE_ADDRESS,
    )


# --- the surface --------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RomSurface:
    """One image, the index that answers for it, and what the project changed.

    `pending` is the raw byte document at the journal's cursor: the bytes the
    project authors now and has not built. `overlay` is the set of offsets the
    surface marks as changed - the journal's pending claims before a build, and
    exactly a manifest's change set after one.
    """

    image: bytes
    profile: RomProfile
    index: RangeIndex | None = None
    #: Why there is no index, when there is none. Empty when there is one.
    index_problem: str = ""
    pending: Mapping[int, bytes] = field(default_factory=dict)
    overlay: frozenset[int] = frozenset()
    #: The index's owners split by the raw byte authority's floor: the ones whose
    #: evidence blocks a write, and the known shapes whose evidence does not.
    strong_owners: frozenset[str] = field(default=frozenset(), repr=False)
    shape_owners: frozenset[str] = field(default=frozenset(), repr=False)

    def __post_init__(self) -> None:
        if self.index is None:
            return
        strong: set[str] = set()
        shapes: set[str] = set()
        for item in self.index.atlas.objects:
            (strong if blocks_a_write(item.confidence) else shapes).add(item.identity)
        object.__setattr__(self, "strong_owners", frozenset(strong))
        object.__setattr__(self, "shape_owners", frozenset(shapes))

    @property
    def image_size(self) -> int:
        return len(self.image)

    def owners_of(self, spans) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """One query's spans as ``(owners, known shapes)`` under the write floor.

        A declared extent always owns: the profile vouches for it and the raw
        byte authority refuses against it whatever its evidence. An atlas object
        owns only at or above the floor, which is the rule the same authority
        applies, so a byte this reports as owned is a byte a raw write refuses.
        """
        owners = {
            span.owner
            for span in spans
            if span.source == DECLARED_EXTENT
            or span.owner in self.strong_owners
        }
        shapes = {
            span.owner
            for span in spans
            if span.source != DECLARED_EXTENT and span.owner not in self.strong_owners
        }
        return tuple(sorted(owners)), tuple(sorted(shapes))

    def canonical_bytes(self, offset: int, size: int) -> bytes:
        """The base image's own bytes: the column that is never written to."""
        return self.image[offset : offset + size]

    def current_bytes(self, offset: int, size: int) -> bytes:
        """The base bytes with the project's pending raw writes applied.

        These bytes are journal-local: they are what a build would emit for this
        range once it applies the project's raw document, and no artifact on disk
        holds them yet. A pending semantic edit is not materialized here at all:
        it has no byte value until a build produces one, and the ownership strip
        says so rather than showing a base value the project has replaced.
        """
        window = bytearray(self.canonical_bytes(offset, size))
        for written_at, value in self.pending.items():
            for position, byte in enumerate(value):
                at = written_at + position
                if offset <= at < offset + size:
                    window[at - offset] = byte
        return bytes(window)


def owner_phrase(owners: Iterable[str], shapes: Iterable[str]) -> str:
    """What the surface says it knows about one query's owners, in its own words."""
    owners = tuple(owners)
    shapes = tuple(shapes)
    if owners:
        return ", ".join(owners)
    if shapes:
        return (
            f"no semantic owner known; {len(shapes)} known shape(s) below the "
            "ownership floor"
        )
    return "no semantic owner known"


def load_index(
    profile: RomProfile, atlas_directory: Path | None = None
) -> tuple[RangeIndex | None, str]:
    """The range index for `profile`, or None and the reason it is not available.

    The atlas is located and read through the SDK's own mechanism, exactly as the
    beta session locates it, and its identity is checked against the profile's
    before a single offset is trusted. A missing, unreadable or foreign atlas is
    a stated absence here, never a silent rebuild: an atlas is evidence-producing
    work and stays explicit.
    """
    from tools.webfoot.atlas_build import load_atlas

    directory = (
        Path(atlas_directory)
        if atlas_directory is not None
        else _default_atlas_directory()
    )
    path = directory / ATLAS_FILE
    if not path.is_file():
        return None, (
            f"the range index is not assembled: {path} is missing, so no byte has "
            "a classification"
        )
    try:
        atlas = load_atlas(path)
        profile.require_identity(atlas, subject=f"atlas {path}")
        index = RangeIndex(atlas, declared_extents(profile))
    except (OSError, ValueError, AtlasError, AtlasIdentityMismatch) as exc:
        return None, f"the range index could not be used: {exc}"
    return index, ""


def _default_atlas_directory() -> Path:
    """Where the SDK's own atlas commands look, asked of the SDK."""
    from tools.webfoot.cli import _default_atlas_directory as resolve

    return Path(resolve())


def surface_for(
    image: bytes,
    profile: RomProfile,
    journal: EditJournal,
    *,
    index: RangeIndex | None = None,
    index_problem: str = "",
) -> RomSurface:
    """The surface over one open image, its profile and its journal.

    The overlay starts as the journal's pending claims: what the project has
    changed and not yet built. A build replaces it through `with_manifest`.
    """
    return RomSurface(
        image=image,
        profile=profile,
        index=index,
        index_problem=index_problem,
        pending=dict(journal.raw_edits().bytes_by_offset),
        overlay=pending_offsets(journal),
    )


def with_manifest(surface: RomSurface, manifest: WriteManifest) -> RomSurface:
    """The surface whose overlay is exactly the change set a build reported."""
    return replace(surface, overlay=changed_offsets(manifest.changes))


def changed_offsets(changes: Iterable[ByteChange]) -> frozenset[int]:
    """Every file offset where a change's new byte differs from its old one.

    Offsets, not a count: the overlay marks positions, and the manifest's own
    `changed_byte_count` cannot answer which ones they are.
    """
    offsets: set[int] = set()
    for change in changes:
        for position, (old, new) in enumerate(zip(change.old, change.new)):
            if old != new:
                offsets.add(change.offset + position)
    return frozenset(offsets)


def pending_offsets(journal: EditJournal) -> frozenset[int]:
    """Every offset the journal's applied edits claim, and nothing from a redo tail.

    A raw write claims the bytes it writes; a semantic edit claims the extent it
    rewrites, which is the honest answer until a build says exactly which bytes
    moved. `journal.edits()` is the applied prefix, so an undone edit stops
    claiming immediately.
    """
    return frozenset(
        position
        for entry in journal.edits()
        for span in entry.claimed
        for position in range(span.start.value, span.end)
    )


# --- what owns these bytes ----------------------------------------------------


@dataclass(frozen=True, slots=True)
class Ownership:
    """Everything the surface can say about one byte, and the honest limits."""

    offset: int
    address: int
    classification: str
    confidence: Confidence | None
    owners: tuple[str, ...]
    #: Identities the atlas knows here whose evidence is below the write floor.
    shapes: tuple[str, ...] = ()
    problem: str = ""

    @property
    def owner_text(self) -> str:
        """The one phrase the specification requires where nobody owns a byte."""
        return owner_phrase(self.owners, self.shapes)

    def text(self) -> str:
        """One line for the ownership strip, in the product's own words."""
        where = f"0x{self.address:08X} (file offset 0x{self.offset:06X})"
        if self.problem:
            return f"{where}: ownership unknown, {self.problem}"
        classification = self.classification or "unclassified"
        confidence = self.confidence.value if self.confidence else "UNKNOWN"
        return f"{where}: {classification} / {confidence}: {self.owner_text}"


def ownership(surface: RomSurface, offset: int) -> Ownership:
    """What owns the byte at `offset`, or why that cannot be answered."""
    if not 0 <= offset < len(surface.image):
        raise SurfaceError(
            f"file offset 0x{offset:06X} is outside the {len(surface.image)}-byte image."
        )
    where = image_address(offset, len(surface.image))
    if surface.index is None:
        return Ownership(offset, where, "", None, (), problem=surface.index_problem)
    answer = surface.index.at(FileOffset(offset))
    owners, shapes = surface.owners_of(answer["spans"])
    return Ownership(
        offset=offset,
        address=where,
        classification=answer["classification"],
        confidence=answer["confidence"],
        owners=owners,
        shapes=shapes,
    )


def summary(surface: RomSurface) -> str:
    """One line about the whole image, from the index's own totals."""
    if surface.index is None:
        return f"{len(surface.image)} bytes. {surface.index_problem}."
    overview = surface.index.overview()
    return (
        f"{overview['image_size']} bytes, {overview['coverage_spans']} coverage "
        f"spans, {overview['objects']} atlas objects, {overview['owners']} owners, "
        f"{overview['unowned_bytes']} bytes nobody owns"
    )


# --- the ranges view ----------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RangeRow:
    """One row of the range view: one coverage span and who claims its bytes."""

    span: RomRange
    address: int
    classification: str
    confidence: Confidence
    owners: tuple[str, ...]
    shapes: tuple[str, ...]
    preview: bytes

    @property
    def owner_text(self) -> str:
        return owner_phrase(self.owners, self.shapes)

    def text(self) -> str:
        return (
            f"0x{self.address:08X} + {self.span.size}: {self.classification} / "
            f"{self.confidence.value}: {self.owner_text}"
        )


def range_rows(surface: RomSurface) -> tuple[RangeRow, ...]:
    """The whole image, one row per covered span, in offset order.

    The rows are the atlas's own coverage partition, so they tile the image
    exactly once and no second partition is invented here. Ownership is the same
    floor the write path uses, so an owner shown here is an owner a raw write
    would be refused by. Empty when no index is loaded; `surface.index_problem`
    then says why.
    """
    if surface.index is None:
        return ()
    rows = []
    for span in surface.index.atlas.coverage.spans:
        owners, shapes = surface.owners_of(surface.index.spans_overlapping(span.range))
        rows.append(
            RangeRow(
                span=span.range,
                address=image_address(span.range.start.value, surface.image_size),
                classification=span.classification,
                confidence=span.confidence,
                owners=owners,
                shapes=shapes,
                preview=surface.canonical_bytes(span.range.start.value, PREVIEW_BYTES),
            )
        )
    return tuple(rows)


def declared_tables(surface: RomSurface) -> tuple[tuple[RomRange, str], ...]:
    """The profile's declared table extents: the range view's jump list.

    The one source is the same list the raw byte authority refuses against, so a
    table a jump offers and a table a write is refused by cannot disagree.
    """
    return declared_extents(surface.profile)


# --- the bytes view -----------------------------------------------------------


def row_offset(offset: int) -> int:
    """The first offset of the sixteen-byte row `offset` falls in."""
    if type(offset) is not int or offset < 0:
        raise SurfaceError("a byte row needs a non-negative offset")
    return offset - offset % ROM_ROW_BYTES


@dataclass(frozen=True, slots=True)
class ByteRow:
    """One sixteen-byte row: the current bytes beside the canonical ones."""

    offset: int
    address: int
    current: bytes
    canonical: bytes

    @property
    def changed(self) -> tuple[int, ...]:
        """Positions in this row where the current byte differs from canonical."""
        return tuple(
            position
            for position, (current, canonical) in enumerate(
                zip(self.current, self.canonical)
            )
            if current != canonical
        )

    @property
    def ascii(self) -> str:
        return ascii_gutter(self.current)

    def current_hex(self) -> str:
        return hex_bytes(self.current)

    def canonical_hex(self) -> str:
        return hex_bytes(self.canonical)


def hex_bytes(data: bytes) -> str:
    """Bytes as space-free hex pairs, the form the byte view prints."""
    return data.hex()


def ascii_gutter(data: bytes) -> str:
    """Bytes as printable characters, with a dot for everything else."""
    return "".join(
        chr(byte) if 0x20 <= byte < 0x7F else _NOT_PRINTABLE for byte in data
    )


def byte_rows(
    surface: RomSurface, offset: int, rows: int = BYTE_VIEW_ROWS
) -> tuple[ByteRow, ...]:
    """`rows` sixteen-byte rows starting at the row that contains `offset`.

    The block is bounded by the image, so the last row of an image that is not a
    multiple of sixteen is short rather than padded with bytes that do not exist.
    """
    if not 0 <= offset < len(surface.image):
        raise SurfaceError(
            f"file offset 0x{offset:06X} is outside the {len(surface.image)}-byte image."
        )
    first = row_offset(offset)
    built = []
    for start in range(first, len(surface.image), ROM_ROW_BYTES):
        if len(built) == rows:
            break
        canonical = surface.canonical_bytes(start, ROM_ROW_BYTES)
        built.append(
            ByteRow(
                offset=start,
                address=image_address(start, surface.image_size),
                current=surface.current_bytes(start, len(canonical)),
                canonical=canonical,
            )
        )
    return tuple(built)


# --- raw search ---------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SearchHit:
    """One raw hit: the offset, and the classification the index reports for it."""

    offset: int
    address: int
    classification: str
    confidence: Confidence | None
    owners: tuple[str, ...]
    shapes: tuple[str, ...] = ()

    @property
    def owner_text(self) -> str:
        return owner_phrase(self.owners, self.shapes)

    def text(self) -> str:
        confidence = self.confidence.value if self.confidence else "UNKNOWN"
        return (
            f"0x{self.address:08X} (file offset 0x{self.offset:06X}): "
            f"{self.classification or 'unclassified'} / {confidence}: {self.owner_text}"
        )


def parse_pattern(pattern: str) -> bytes:
    """A hex byte pattern, or a refusal naming what was wrong with it.

    Hex is the only spelling, because it is the only one that can express a byte
    the product has no text for; a semantic phrase is `atlas.search_text` and a
    different question. Spaces and a `0x` prefix are tolerated.
    """
    cleaned = pattern.strip().lower().replace(" ", "").replace("_", "")
    if cleaned.startswith("0x"):
        cleaned = cleaned[2:]
    if not cleaned:
        raise SurfaceError("Enter a hex byte pattern, for example DE AD BE EF.")
    if len(cleaned) % 2:
        raise SurfaceError(
            "A hex byte pattern needs pairs of digits; "
            f"{pattern.strip()!r} has an odd number of them."
        )
    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:
        raise SurfaceError(
            f"{pattern.strip()!r} is not a hex byte pattern."
        ) from exc


def search_bytes(
    surface: RomSurface, pattern: str, *, limit: int = DEFAULT_SEARCH_HITS
) -> tuple[SearchHit, ...]:
    """Every offset where `pattern` occurs, up to `limit`, in offset order.

    The bytes searched are the CURRENT bytes: the canonical image with the
    project's pending raw writes applied. Evidence for that choice: the byte view
    leads with the current bytes and shows the canonical ones beside them, so a
    search over anything else would not find a byte the view puts in front of the
    reader. The alternative, the canonical image alone, would miss exactly the
    bytes the surface itself authored, and there is no third candidate: a pending
    semantic edit has no byte value until a build emits one.

    A hit is a position, never a claim: the specification's rule is that a hit is
    not presented as an editable owner, so each one carries the classification and
    the owners the index already reports for that byte rather than a new meaning.
    """
    needle = parse_pattern(pattern)
    searched = surface.current_bytes(0, len(surface.image))
    hits = []
    start = searched.find(needle)
    while start >= 0 and len(hits) < limit:
        known = ownership(surface, start)
        hits.append(
            SearchHit(
                offset=start,
                address=known.address,
                classification=known.classification,
                confidence=known.confidence,
                owners=known.owners,
                shapes=known.shapes,
            )
        )
        start = searched.find(needle, start + 1)
    return tuple(hits)


# --- open bytes ---------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OpenBytes:
    """Whether a selection can be opened as bytes, and the reason either way.

    The rule the product specification states is that an extent is never guessed.
    So a selection carries an extent that something proved, or it carries no
    extent and this says why it cannot be opened.
    """

    what: str
    extent: RomRange | None = None
    #: Why it cannot be opened, or a note about the extent when it can.
    detail: str = ""

    @property
    def available(self) -> bool:
        return self.extent is not None and self.extent.size > 0

    @property
    def reason(self) -> str:
        """The stated reason when this cannot be opened; empty when it can."""
        if self.available:
            return ""
        detail = self.detail or "no byte range is proven for it"
        return f"Open bytes is disabled: no extent is proven for {self.what}, {detail}."

    def status(self) -> str:
        if not self.available:
            return self.reason
        assert self.extent is not None
        return (
            f"Open the {self.extent.size} byte(s) at file offset "
            f"0x{self.extent.start.value:06X} that back {self.what}{self.detail}"
        )


def open_bytes(
    surface: RomSurface,
    what: str,
    *,
    extent: RomRange | None = None,
    owner: str = "",
) -> OpenBytes:
    """What `Open bytes` would do for one selection.

    A caller that already holds a proven extent passes it. A caller holding a
    semantic identity passes the owner and gets the extent the range index
    reports, or the reason there is none. A caller holding neither gets the
    reason, because a button that opened a guessed range would be worse than one
    that explains itself.
    """
    if extent is not None:
        if extent.end > len(surface.image):
            return OpenBytes(
                what,
                None,
                detail=(
                    f"the extent 0x{extent.start.value:06X} + {extent.size} runs "
                    f"past the {len(surface.image)}-byte image"
                ),
            )
        return OpenBytes(what, extent)
    if owner:
        if surface.index is None:
            return OpenBytes(what, None, detail=surface.index_problem)
        found = surface.index.ranges_of(owner)
        if not found:
            return OpenBytes(
                what, None, detail=f"the range index knows no byte range for {owner}"
            )
        note = f" (the first of {len(found)} extents)" if len(found) > 1 else ""
        return OpenBytes(what, found[0], detail=note)
    return OpenBytes(what, None, detail="nothing is selected")


def selection_extent(surface: RomSurface, offset: int) -> RomRange:
    """The one-byte extent a byte-view selection proves."""
    if not 0 <= offset < len(surface.image):
        raise SurfaceError(
            f"file offset 0x{offset:06X} is outside the {len(surface.image)}-byte image."
        )
    return RomRange(FileOffset(offset), 1)


# --- the raw write gate -------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WriteGate:
    """Whether a raw write may be offered, and the reason either way."""

    available: bool
    reason: str


def write_gate(surface: RomSurface) -> WriteGate:
    """Whether this surface may accept a raw byte write at all.

    A raw write is refused when ANY source claims the bytes, and one of those
    sources is the atlas. Without the range index the surface cannot ask that
    question, so it fails closed here in one place rather than accepting a write
    into bytes a structure owns. The alternative, writing blind and calling the
    unowned result honest, is the thing section 9 of the product specification
    exists to prevent: an unknown byte would be taught as free.
    """
    if surface.index is None:
        return WriteGate(
            False,
            "A raw write is disabled: "
            f"{surface.index_problem or 'the range index is not loaded'}. Without "
            "it the surface cannot tell bytes a structure owns from bytes nobody "
            "owns, so no write here would be safe.",
        )
    return WriteGate(
        True,
        "Write the new bytes at the selection. The change is confirmed first, is "
        "owned by raw:<image address>, and takes effect with the project's next "
        "build.",
    )
