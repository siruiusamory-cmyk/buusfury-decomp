"""Semantic access to a profile's string table, whichever game declares one.

This is the layer callers are meant to use::

    strings = load_text_strings(rom_path, catalog)
    entry = strings.entry(TextIdentity(12))
    strings.set_text(entry.identity, "New Game")
    plan = strings.plan()

A caller names a string by identity and supplies text. It never computes a file
offset, never touches the pointer table, and never sees raw bytes - those are
provenance carried alongside a value, which is the boundary `ARCH-TOOL-001`
requires so a decomp backend can later replace the binary one underneath.

**Nothing here knows which game it is reading.** The table's address, entry
count and pool extent come from the ROM profile, and the reader is selected from
the profile's declared `encoding` through `_CODECS`. Supporting another game is
therefore a profile declaration plus, if its bytes are shaped differently, a
codec - never a branch in this module. TOOLKIT-004 shipped the first encoding
and TOOLKIT-005 added the second, which is what forced the profile-driven shape:
before it, this module carried one game's profile id and one game's table size.

Per-game numbers live in `config/roms.yaml` and in the evidence documents under
`docs/research/`, deliberately not here. A count written into this docstring is
a fact about one profile that will silently go stale the moment another is added
- which is exactly how the wording this replaced came to be wrong.

**Why in-place edits are the shipped capability.** A pool is exhaustively tiled:
every byte belongs to exactly one string, and each string abuts the next. There
is therefore no slack after a string to grow into, and a longer string must be
relocated rather than extended. Relocation needs profile-declared free space,
which no verified profile shipped today has - so this layer supports edits that
fit the original allocation, and reports the exact deficit when one does not.
`webfoot.relocation` proves the growth path on synthetic fixtures instead.

Shorter text is padded to the original allocation rather than shrinking it.
Repacking the pool would move every subsequent string and rewrite every pointer
to reclaim a few bytes, converting a one-word edit into a whole-region rewrite;
the padding is deterministic, so a build stays reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path
from typing import Callable, Iterator

from . import capability
from .formats import ascii_text_tables as att
from .formats import text_tables as tt
from .formats.text_tables import TextCodecError, TextIdentity
from .hashing import hash_stream
from .profile import (
    RomProfile,
    RomProfileCatalog,
    TextTableProfile,
)
from .rom import RomChangedError, RomIdentification, identify_rom
from .write import ByteChange, WritePlan, plan_changes


class TextTableError(ValueError):
    """Base error for semantic string-table access."""


class TextProfileError(TextTableError, capability.CapabilityError):
    """Raised when a ROM or profile is not authorized for text access.

    Inherits `CapabilityError` so the shared gate can raise this exact type:
    callers already catching `TextProfileError` are unaffected by the move, and
    a caller handling capability failures generically can catch them too.
    """


class UnknownTextError(TextTableError):
    """Raised when an identity names no string in this table."""


class TextTooLongError(TextTableError):
    """Raised when edited text cannot fit the string's current allocation.

    Distinct from a validation failure on purpose: the text is *well-formed*,
    and would be writable if this profile declared free space to relocate into.
    The message therefore reports the deficit rather than implying the text is
    wrong.
    """


#: CONFIRMED. Byte written into the slack left by a shorter replacement. Zero,
#: because a run of `00 00` past a terminator is what the untouched image
#: already contains between the pool's end and the pointer table, and because
#: any nonzero filler would decode as text if a terminator were ever lost.
#: Both shipped encodings use the same filler, for the same reason.
PAD_BYTE = 0x00


@dataclass(frozen=True, slots=True)
class TextCodec:
    """One encoding's reader, writer and enumerator.

    This is the seam that keeps the games apart without a branch. A profile
    declares an `encoding`; `_codec_for` looks that name up in `_CODECS` and
    everything downstream - loading, editing, planning - runs against whichever
    codec came back. No function in this module asks which game it is reading.

    `enumerate_pool` yields one `_RawEntry` per string, and both codecs must
    account for the pool's whole extent. They reach that guarantee differently,
    because the two tables have different shapes:

    * Buu's Fury enumerates *through the pointer table*. Its 1,534 entries are
      unique and strictly ascending, so table order, address order and pool
      coverage coincide and walking the table walks the pool.
    * Legacy of Goku II enumerates *by walking the pool*, then looks each
      string's slot up. Its 260 entries alias - 9 targets are shared by 14 extra
      slots - so table order is neither address order nor free of repeats, and
      following it would visit 246 strings in an order that proves nothing about
      coverage.

    Either way every string ends with a table index, which is its identity. A
    pool string no slot reaches is refused rather than represented: it would
    have no durable identity, so it could not appear in a project.
    """

    name: str
    decode: "Callable[[bytes, int], tuple[str, int]]"
    encode: "Callable[[str], bytes]"
    enumerate_pool: "Callable[[bytes, TextTableProfile, int, int, int], Iterator[_RawEntry]]"
    pointer_size: int


@dataclass(frozen=True, slots=True)
class _RawEntry:
    """One enumerated string, before identity and location are attached."""

    index: int
    text: str
    offset: int
    size: int


def _enumerate_utf16le(
    data: bytes,
    table: TextTableProfile,
    table_start: int,
    pool_start: int,
    pool_end: int,
) -> Iterator[_RawEntry]:
    """Enumerate through the pointer table, requiring exhaustive tiling.

    This profile's declared property is that table order, address order and pool
    coverage all coincide, so a violation means the image or the metadata is not
    what it claims. Checking during the load makes that a refusal rather than a
    subtly wrong allocation size later.
    """
    expected = pool_start
    for index in range(table.count):
        offset = tt.read_pointer(data, index)
        if not pool_start <= offset < pool_end:
            raise TextProfileError(
                f"pointer table entry {index} targets {offset:#010x}, outside "
                f"the declared pool {pool_start:#010x}..{pool_end:#010x}"
            )
        try:
            text, end = tt.decode_string(data, offset)
        except TextCodecError as exc:
            raise TextProfileError(f"string {index} does not decode: {exc}") from exc
        if offset != expected:
            raise TextProfileError(
                f"string {index} starts at {offset:#010x}, but the previous "
                f"string ends at {expected:#010x}; the declared pool is not "
                "exhaustively tiled"
            )
        expected = end
        yield _RawEntry(index=index, text=text, offset=offset, size=end - offset)

    if expected != pool_end:
        raise TextProfileError(
            f"strings end at {expected:#010x} but the declared pool ends at "
            f"{pool_end:#010x}; the enumeration is not exhaustive"
        )


def _enumerate_ascii(
    data: bytes,
    table: TextTableProfile,
    table_start: int,
    pool_start: int,
    pool_end: int,
) -> Iterator[_RawEntry]:
    """Enumerate by walking the pool, then attach each string's table index.

    Walking rather than following the table is what proves the round trip covers
    the whole extent. Following the table would prove only that the strings the
    table happens to name round-trip, which is a weaker claim and one that
    happens to be indistinguishable from the strong one on this image.

    The table is read too, for two reasons. It supplies each string's durable
    identity, and its targets are checked to land on real string starts - a slot
    pointing into the middle of a string would otherwise decode successfully and
    be silently wrong.

    Both directions must account for everything: every table target is a string
    start, and every string has a table slot. A pool string no slot reaches
    would have no durable identity and could not be represented in a project, so
    it is refused rather than silently dropped from the round trip.
    """
    starts: dict[int, int] = {}
    for index in range(table.count):
        offset = att.read_pointer(data, table_start, index)
        if not pool_start <= offset < pool_end:
            raise TextProfileError(
                f"pointer table entry {index} targets {offset:#010x}, outside "
                f"the declared pool {pool_start:#010x}..{pool_end:#010x}"
            )
        # First slot wins, so a shared target keeps its lowest index as identity
        # and the mapping stays stable across loads.
        starts.setdefault(offset, index)

    position = pool_start
    seen: set[int] = set()
    while position < pool_end:
        try:
            text, end = att.decode_string(data, position)
        except TextCodecError as exc:
            raise TextProfileError(
                f"string at {position:#010x} does not decode: {exc}"
            ) from exc
        if end > pool_end:
            raise TextProfileError(
                f"string at {position:#010x} runs past the declared pool end "
                f"{pool_end:#010x}"
            )
        index = starts.get(position)
        if index is None:
            raise TextProfileError(
                f"string at {position:#010x} is not reached by any pointer "
                "table entry, so it has no durable identity"
            )
        seen.add(position)
        yield _RawEntry(index=index, text=text, offset=position, size=end - position)
        position = end

    if position != pool_end:
        raise TextProfileError(
            f"strings end at {position:#010x} but the declared pool ends at "
            f"{pool_end:#010x}; the enumeration is not exhaustive"
        )
    stray = sorted(set(starts) - seen)
    if stray:
        raise TextProfileError(
            f"pointer table entry targets {stray[0]:#010x}, which is not the "
            "start of any string in the declared pool"
        )


#: Encoding name -> codec. `profile._SUPPORTED_TEXT_ENCODINGS` gates which names
#: a profile may declare; this maps an accepted name to the reader that
#: implements it. The two must stay in step, which `_codec_for` enforces by
#: refusing a name it has no entry for rather than falling back to a default.
_CODECS = {
    "utf16le_nul_terminated": TextCodec(
        name="utf16le_nul_terminated",
        decode=tt.decode_string,
        encode=tt.encode_string,
        enumerate_pool=_enumerate_utf16le,
        pointer_size=tt.TEXT_POINTER_SIZE,
    ),
    "ascii_nul_terminated": TextCodec(
        name="ascii_nul_terminated",
        decode=att.decode_string,
        encode=att.encode_string,
        enumerate_pool=_enumerate_ascii,
        pointer_size=att.POINTER_SIZE,
    ),
}


def _codec_for(table: TextTableProfile) -> TextCodec:
    """The codec implementing this profile's declared encoding.

    Refuses an unimplemented name rather than guessing, so a profile can never
    be decoded by the wrong reader.
    """
    try:
        return _CODECS[table.encoding]
    except KeyError:
        supported = ", ".join(sorted(_CODECS))
        raise TextProfileError(
            f"no text codec implements encoding {table.encoding!r}; "
            f"available: {supported}"
        ) from None


@dataclass(frozen=True, slots=True)
class TextLocation:
    """Where a string sits right now. Provenance only, never identity."""

    index: int
    file_offset: int
    allocation: int
    pointer_offset: int

    @property
    def gba_address(self) -> int:
        return self.file_offset + tt.GBA_ROM_BASE


@dataclass(frozen=True, slots=True)
class TextEntry:
    """One string: durable identity, current text, current location, bytes."""

    identity: TextIdentity
    text: str
    location: TextLocation
    original_bytes: bytes


def _require_text_profile(identification: RomIdentification) -> RomProfile:
    """Fail closed unless this exact ROM is verified and declares the table.

    `capability.require` owns the checks - verified identity, declared
    capability, and the packaged-contract comparison that stops a hand-edited
    `--profiles` YAML from moving the declared extents while leaving the ROM
    hashes intact. TOOLKIT-005 removed a fourth check requiring the profile id
    to equal one constant naming Buu's Fury; the contract is now looked up by
    the identified profile's own id, so a second game with a declared string
    table is served by the same path.

    Note the profile only authorises *access*. Which codec reads the bytes is
    chosen from the profile's declared `encoding`, so a game whose strings are
    not UTF-16LE is refused by the codec selector rather than mis-decoded here.
    """
    return capability.require(
        identification,
        capability.Capability.TEXT_STRINGS,
        subsystem="text access",
        error_type=TextProfileError,
    )


class TextStrings:
    """Loaded strings plus any pending semantic edits.

    Edits accumulate in memory and become a `WritePlan` only when `plan()` is
    called. Nothing here writes, and nothing here knows a destination path.
    """

    def __init__(
        self,
        *,
        identification: RomIdentification,
        profile: RomProfile,
        entries: tuple[TextEntry, ...],
        codec: TextCodec,
    ) -> None:
        self.identification = identification
        self.profile = profile
        self.codec = codec
        self._entries = {entry.identity: entry for entry in entries}
        self._order = tuple(entry.identity for entry in entries)
        self._edited: set[TextIdentity] = set()
        #: Full base image, set by `load_text_strings`. Retained so `plan()`
        #: validates against exactly the bytes the strings were decoded from.
        self._base_bytes: bytes = b""

    @property
    def layout(self) -> TextTableProfile:
        table = self.profile.text_strings
        assert table is not None  # guaranteed by `_require_text_profile`
        return table

    # --- reading -------------------------------------------------------

    @property
    def base_bytes(self) -> bytes:
        """The exact image these strings were decoded from.

        Mirrors `StatTables.base_bytes`. Exposed so a build whose profile
        declares text but no stats can still name the base every change was
        computed against, rather than re-reading a file whose identity this
        object already settled.
        """
        return self._base_bytes

    def entries(self) -> Iterator[TextEntry]:
        """Every string, in table order. Order is presentation, not identity."""
        for identity in self._order:
            yield self._entries[identity]

    def entry(self, identity: TextIdentity) -> TextEntry:
        try:
            return self._entries[identity]
        except KeyError:
            raise UnknownTextError(f"no string with identity {identity}") from None

    def find(self, needle: str) -> tuple[TextEntry, ...]:
        """Every string containing ``needle``. Case-sensitive, substring match.

        Searching by content is how a person actually finds a line to edit; the
        index that identifies it is not something they would know in advance.
        """
        return tuple(e for e in self.entries() if needle in e.text)

    # --- editing -------------------------------------------------------

    def set_text(self, identity: TextIdentity, text: str) -> None:
        """Replace one string's text.

        Validates immediately - encodability and fit are both checked here, so a
        caller learns at the point of the edit rather than at plan time. Encode
        errors surface as `TextCodecError`; an over-long but well-formed string
        surfaces as `TextTooLongError` with the exact deficit.
        """
        entry = self.entry(identity)
        if not isinstance(text, str):
            raise TextTableError(f"text must be a string, got {text!r}")
        encoded = self.codec.encode(text)  # raises TextCodecError if malformed
        allocation = entry.location.allocation
        if len(encoded) > allocation:
            raise TextTooLongError(
                f"{identity}: encoded text needs {len(encoded)} bytes but its "
                f"allocation is {allocation}; {len(encoded) - allocation} bytes "
                "too long. Growing a string requires relocation, and this "
                "profile declares no verified free space."
            )
        self._entries[identity] = replace(entry, text=text)
        if text != self._original_text(entry):
            self._edited.add(identity)
        else:
            self._edited.discard(identity)

    # --- planning ------------------------------------------------------

    def changes(self) -> tuple[ByteChange, ...]:
        """Encode every string into an attributed change, in table order.

        Every string is encoded, not just edited ones, because that is what
        proves round-trip: an untouched string must re-encode to exactly its
        original bytes, and `plan_changes` drops it as a no-op. A string that
        differed without having been edited would surface as an unexplained
        change rather than passing silently.

        Returned as changes rather than as a finished plan so a caller building
        several subsystems at once can put them all in one plan. That matters:
        overlap detection is per-plan, so two subsystems in two plans could each
        look valid while together writing the same bytes.
        """
        changes: list[ByteChange] = []
        for entry in self.entries():
            encoded = self.codec.encode(entry.text)
            allocation = entry.location.allocation
            if len(encoded) > allocation:
                # Unreachable through `set_text`, which refuses first. Kept
                # because this is the last point before bytes are computed, and
                # a silently truncated string would be worse than a raise.
                raise TextTooLongError(
                    f"{entry.identity}: encoded text exceeds its allocation"
                )
            padded = encoded + bytes([PAD_BYTE]) * (allocation - len(encoded))
            changes.append(
                ByteChange(
                    offset=entry.location.file_offset,
                    old=entry.original_bytes,
                    new=padded,
                    owner=str(entry.identity),
                    reason=self._reason(entry.identity),
                )
            )
        return tuple(changes)

    def plan(self) -> WritePlan:
        """Validate this subsystem's changes alone and return an applicable plan."""
        return plan_changes(
            self._base_bytes,
            self.changes(),
            profile_id=self.profile.id,
            base_sha256=self.identification.hashes.sha256,
        )

    def _reason(self, identity: TextIdentity) -> str:
        return "text edit" if identity in self._edited else "text unchanged"

    def _original_text(self, entry: TextEntry) -> str:
        text, _ = self.codec.decode(entry.original_bytes, 0)
        return text


def load_text_strings(path: str | Path, catalog: RomProfileCatalog) -> TextStrings:
    """Identify `path`, then read the whole string table from it. Never writes.

    The whole image is retained so `plan()` can validate changes against the
    exact bytes they were computed from, mirroring `load_stat_tables`.
    """
    source = Path(path)
    identification = identify_rom(source, catalog)
    profile = _require_text_profile(identification)

    with source.open("rb") as stream:
        before = os.fstat(stream.fileno())
        hashes, _ = hash_stream(stream)
        if hashes != identification.hashes:
            raise RomChangedError(f"ROM identity changed before text read: {source}")
        stream.seek(0)
        data = stream.read()
        after = os.fstat(stream.fileno())

    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise RomChangedError(f"ROM changed while text was read: {source}")

    table = profile.text_strings
    assert table is not None
    codec = _codec_for(table)

    pool_start = table.pool_address.to_file_offset(len(data))
    pool_end = pool_start + table.pool_size
    table_start = table.pointer_table_address.to_file_offset(len(data))
    if pool_end > len(data) or table_start + table.pointer_table_size > len(data):
        raise TextProfileError("configured text regions extend beyond the ROM")

    entries: list[TextEntry] = []
    for raw in codec.enumerate_pool(data, table, table_start, pool_start, pool_end):
        # The upper bound lives here rather than in `TextIdentity`, because the
        # count is a property of the profile's table and not of identity itself.
        if raw.index >= table.count:
            raise TextProfileError(
                f"string index {raw.index} is outside the declared table "
                f"count {table.count}"
            )
        entries.append(
            TextEntry(
                identity=TextIdentity(raw.index),
                text=raw.text,
                location=TextLocation(
                    index=raw.index,
                    file_offset=raw.offset,
                    allocation=raw.size,
                    pointer_offset=table_start + raw.index * codec.pointer_size,
                ),
                original_bytes=data[raw.offset : raw.offset + raw.size],
            )
        )

    strings = TextStrings(
        identification=identification,
        profile=profile,
        entries=tuple(entries),
        codec=codec,
    )
    strings._base_bytes = data
    return strings
