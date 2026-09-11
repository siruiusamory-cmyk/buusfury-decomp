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

**How storage is chosen.** A pool is exhaustively tiled: every byte belongs to
exactly one string, and each string abuts the next. There is therefore no slack
after a string to grow into, and a longer string must be relocated rather than
extended. TOOLKIT-036 wired that relocation into this layer, so the SDK decides
storage and the author never does:

* a replacement that fits the original allocation is written in place, exactly
  as it always has been;
* a replacement that exceeds it is allocated into profile-declared verified free
  space and its owning table slot is rewritten - but only where the profile's
  table declares relocation AND this entry's inbound surface is measurably its
  own table slot alone;
* anything else fails closed, naming which of those it was.

Exceeding the original body is itself the reason a relocation is planned. There
is no flag asking for one and no field supplying an address: a project carries
semantic text, and where the bytes end up is this layer's decision.

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
from .layout import LayoutError, RomRange
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
    and this layer already tried to relocate it. The message therefore reports
    the deficit and then names which of the three relocation conditions actually
    refused this one - the profile's table, this entry's ownership, or capacity -
    rather than implying the text is wrong.
    """


#: TOOLKIT-036. The anchor kind a text-string body is published under. It is
#: listed in `layout.RELOCATION_ELIGIBLE_KINDS`, which is what lets the existing
#: `relocation.plan_relocation` path carry text; no second relocation path exists.
TEXT_STRING_KIND = "text-string"


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


def _relocated_span(
    data: bytes,
    index: int,
    offset: int,
    end: int,
    vacated: dict[int, int],
    writable: "tuple[RomRange, ...]",
    pool_start: int,
    pool_end: int,
    relocated: "dict[int, tuple[int, int]]",
) -> None:
    """Check one out-of-pool entry against all seven relocation conditions.

    TOOLKIT-036. Reading an entry whose body is not in the canonical pool is only
    justified when that entry is a PROVEN relocation, which is a conjunction, not
    a tolerance. Conditions 1, 2 and 6 are established before this is reached -
    the table is relocation-enabled for the profile, per-entry ownership was
    proven from the measured reference census, and `plan_changes` refuses any
    overlapping write - and the remaining four are checked here against the image
    actually being read:

      3. the old span is an exactly accounted-for vacated span;
      4. the new target lies wholly within a declared verified-writable region;
      5. the new body decodes normally (the caller decoded it to get `end`);
      7. the table pointer resolves to that new body (the caller read it there).

    A target that is neither in the pool nor wholly inside declared writable
    space is refused, exactly as before this ticket.

    Condition 4 is CONTAINMENT, not merely a lower bound: the body must start
    inside a verified region AND end inside the same one. A body that begins in
    declared space and runs past its end writes bytes nobody verified, so the
    upper bound is the half of the check that does the work, and dropping it
    would let a third-party or hand-patched image walk out of the region.

    `relocated` carries every relocated body this enumeration has already
    accepted, index -> `(start, end)`. Two further refusals are made against it,
    mirroring the exact-adjacency discipline the in-pool path already applies:

      * ALIAS: two table slots naming ONE relocated body. In the pool, aliasing
        is a measured property of a game's table and its entries are simply not
        relocation-eligible; out of the pool, an alias would mean two identities
        sharing one span, so a write attributed to either silently rewrites the
        other. This reader does not support alias semantics, so it refuses.
      * OVERLAP: two independently relocated bodies whose spans intersect. One
        would be truncated or corrupted by the other's bytes. `plan_changes`
        would catch a write that did this, but only at write time - an image
        handed to this reader may already contain it, and reading it as two
        sound strings would be the wrong answer, not a deferred one.
    """
    if not any(region.start.value <= offset and end <= region.end for region in writable):
        raise TextProfileError(
            f"pointer table entry {index} targets {offset:#010x}, outside "
            f"the declared pool {pool_start:#010x}..{pool_end:#010x} and outside "
            "every declared verified-writable region"
        )
    if index not in vacated:
        raise TextProfileError(
            f"string {index} was read outside the declared pool at {offset:#010x} "
            "but no accounted-for vacated span belongs to it; a relocated entry "
            "must own the pool bytes it left behind"
        )
    for other, (start, stop) in sorted(relocated.items()):
        if start == offset:
            raise TextProfileError(
                f"strings {other} and {index} both name the relocated body at "
                f"{offset:#010x}; a relocated body belongs to exactly one entry "
                "and this reader does not support aliased relocation targets"
            )
        if start < end and offset < stop:
            raise TextProfileError(
                f"relocated string {index} at {offset:#010x}..{end:#010x} overlaps "
                f"relocated string {other} at {start:#010x}..{stop:#010x}; two "
                "relocated bodies may not share bytes"
            )


def _enumerate_utf16le(
    data: bytes,
    table: TextTableProfile,
    table_start: int,
    pool_start: int,
    pool_end: int,
    vacated: "dict[int, int] | None" = None,
    writable: "tuple[RomRange, ...]" = (),
) -> Iterator[_RawEntry]:
    """Enumerate through the pointer table, requiring accounted-for coverage.

    This profile's declared property is that table order, address order and pool
    coverage all coincide, so a violation means the image or the metadata is not
    what it claims. Checking during the load makes that a refusal rather than a
    subtly wrong allocation size later.

    TOOLKIT-036 relaxed that from exhaustive TILING to exhaustive ACCOUNTING,
    which is the weaker claim only for entries whose relocation is proven:

        live canonical in-pool bodies
          + exact vacated spans belonging to proven relocated entries
          = exhaustive canonical pool coverage

    `vacated` maps a relocated entry's index to the exact size of the span it
    left behind, and is supplied only by a caller that has already proven that
    entry's ownership. An unexplained hole - a gap belonging to no proven
    relocation - still fails closed, and so does an out-of-pool target that is
    not inside declared verified-writable space.
    """
    vacated = vacated or {}
    expected = pool_start
    #: TOOLKIT-036. Every relocated body accepted so far, index -> (start, end).
    #: Out-of-pool bodies get the same non-sharing discipline in-pool bodies get
    #: from exact adjacency: an alias or an overlap is refused as it is read.
    relocated: dict[int, tuple[int, int]] = {}
    for index in range(table.count):
        offset = tt.read_pointer(data, index, table_start)
        try:
            text, end = tt.decode_string(data, offset)
        except TextCodecError as exc:
            raise TextProfileError(f"string {index} does not decode: {exc}") from exc
        if not pool_start <= offset < pool_end:
            _relocated_span(data, index, offset, end, vacated, writable,
                            pool_start, pool_end, relocated)
            relocated[index] = (offset, end)
            # The pool bytes this entry vacated are still accounted for, so the
            # tiling cursor advances across them exactly as if it had not moved.
            expected += vacated[index]
            yield _RawEntry(index=index, text=text, offset=offset, size=end - offset)
            continue
        if index in vacated:
            raise TextProfileError(
                f"string {index} is claimed as relocated but its pointer still "
                f"resolves into the declared pool at {offset:#010x}"
            )
        if offset != expected:
            raise TextProfileError(
                f"string {index} starts at {offset:#010x}, but the previous "
                f"string ends at {expected:#010x}; the declared pool is not "
                "exhaustively accounted for"
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
    vacated: "dict[int, int] | None" = None,
    writable: "tuple[RomRange, ...]" = (),
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

    TOOLKIT-036 did NOT enable relocation for this encoding. Its tables alias -
    9 targets are shared by 14 extra slots - so a per-entry ownership proof that
    the UTF-16LE path can make from a measured reference census cannot be made
    here. A caller that nevertheless claims a relocation is refused rather than
    served by a reader that would not detect the vacated span.
    """
    if vacated:
        raise TextProfileError(
            "this encoding does not support relocated text entries; its pointer "
            "table aliases, so no entry has proven per-entry ownership"
        )
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


def _anchor_id(identity: TextIdentity):
    """The anchor identity of one text body: its own durable `text:NNNN` key.

    Derived from identity, never from an address, so the anchor's name does not
    change when the allocator moves the body.
    """
    from .layout import AnchorId

    return AnchorId(identity.key)


def _aligned_word_census(data: bytes) -> "dict[int, int]":
    """How many word-aligned LE u32 GBA pointers in the image name each address.

    One pass over the whole image rather than one scan per entry, because the
    question - "how many aligned words in the ROM hold this body's address" - is
    the same question for every entry and the answer is a single histogram.

    Word-aligned only. A pointer the ARM core loads with `ldr` is word-aligned by
    construction, and an unaligned coincidence is not a reachable reference; the
    5 canonical coincidences this refuses are all aligned, which is exactly why
    aligned counting is sufficient to refuse them.
    """
    from array import array
    from collections import Counter

    words = array("I")
    words.frombytes(data[: len(data) - len(data) % 4])
    if words.itemsize != 4:  # pragma: no cover - 'I' is 4 bytes on every CPython
        raise TextProfileError("this platform has no 32-bit unsigned array type")
    import sys

    if sys.byteorder != "little":  # pragma: no cover - GBA tooling runs little-endian
        words.byteswap()
    return Counter(words)


def _owned_entries(
    data: bytes, entries: "tuple[TextEntry, ...]", codec: TextCodec
) -> "frozenset[TextIdentity]":
    """Every entry whose whole inbound surface is provably its own table slot.

    TOOLKIT-036. This is the per-entry relocation ownership gate, and it is a
    measurement, never a list. An entry qualifies when, and only when:

        exactly one word-aligned inbound reference exists in the whole image,
        and it is that entry's own pointer-table slot

    Both halves are checked: the census counts every aligned word holding the
    body's address, and the entry's own slot is confirmed to be one of them. An
    entry any second aligned word also names is an unresolved CANDIDATE
    relationship - the canonical image contains five, and each is refused here by
    its measured inbound count rather than by its index.
    """
    census = _aligned_word_census(data)
    owned = []
    for entry in entries:
        address = entry.location.file_offset + tt.GBA_ROM_BASE
        slot = entry.location.pointer_offset
        if slot % codec.pointer_size:
            continue
        held = int.from_bytes(data[slot : slot + codec.pointer_size], "little")
        if held != address or census.get(address, 0) != 1:
            continue
        owned.append(entry.identity)
    return frozenset(owned)


def _vacated_spans(
    data: bytes,
    table: TextTableProfile,
    codec: TextCodec,
    table_start: int,
    pool_start: int,
    pool_end: int,
) -> "dict[int, int]":
    """Each out-of-pool entry mapped to the exact pool span it left behind.

    TOOLKIT-036. A relocation does not clear the bytes it retires, so the vacated
    span is still a decodable string sitting at exactly the point the tiling
    cursor reaches - which makes the hole measurable rather than assumed. Walking
    the table in order and advancing the cursor by each body in turn attributes
    every hole to exactly one entry: the one whose pointer left the pool at that
    position.

    This measures; it decides nothing. `_enumerate_utf16le` still checks that the
    resulting accounting is exhaustive, that each claimed relocation landed in
    declared verified-writable space, and that an unexplained hole - one this
    walk could not attribute, or that leaves the cursor short of the pool end -
    fails closed. An entry the enumerator finds inside the pool is never in this
    map, so an in-pool entry can never borrow a hole's explanation.
    """
    if codec.enumerate_pool is not _enumerate_utf16le:
        return {}
    spans: dict[int, int] = {}
    cursor = pool_start
    for index in range(table.count):
        try:
            offset = tt.read_pointer(data, index, table_start)
        except TextCodecError:
            return {}
        if pool_start <= offset < pool_end:
            if offset != cursor:
                # Not a shape this walk can attribute. Returning nothing hands
                # the enumerator an unexplained hole, which it refuses.
                return {}
            try:
                _, end = tt.decode_string(data, offset)
            except TextCodecError:
                return {}
            cursor = end
            continue
        try:
            _, end = tt.decode_string(data, cursor)
        except TextCodecError:
            return {}
        if end > pool_end:
            return {}
        spans[index] = end - cursor
        cursor = end
    return spans if cursor == pool_end else {}


def _writable_regions(profile: RomProfile) -> "tuple[RomRange, ...]":
    """The profile's declared verified-writable regions, as plain ranges.

    Declared free space is the only writable destination this toolkit recognises;
    it is a trusted profile declaration and is never inferred from fill patterns.
    """
    return tuple(region.range for region in profile.free_regions)


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
        #: TOOLKIT-036. Identities whose measured inbound surface is exactly their
        #: own table slot, so the existing relocator can move them. Set by
        #: `load_text_strings` from the image; empty when the profile's table is
        #: not relocation-enabled, which is what keeps the gate per-PROFILE and
        #: per-ENTRY at once.
        self._owned: frozenset[TextIdentity] = frozenset()
        #: Text this build decided to relocate, identity -> replacement text.
        self._relocating: dict[TextIdentity, str] = {}
        #: TOOLKIT-036. The build-scoped reservation set: spans an EARLIER allocating
        #: domain of this build already took out of the same declared free regions.
        #: Set by the coordinator through `reserve`; empty for a text-only build.
        #: These are plain spans, so this layer learns nothing about who took them.
        self._reserved: "tuple[RomRange, ...]" = ()

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
            # TOOLKIT-036. Exceeding the original body is itself the reason to
            # plan a relocation; no project flag asks for one and none supplies
            # an address. The plan is built HERE, at the point of the edit, so a
            # caller learns whether the storage exists at the same moment it
            # learns the text is well-formed - and so a refusal names the exact
            # reason THIS relocation was refused rather than a stale generality.
            self._plan_relocation(identity, entry, text, encoded)
        else:
            self._relocating.pop(identity, None)
        self._entries[identity] = replace(entry, text=text)
        if text != self._original_text(entry):
            self._edited.add(identity)
        else:
            self._edited.discard(identity)

    def _plan_relocation(
        self, identity: TextIdentity, entry: TextEntry, text: str, encoded: bytes
    ) -> None:
        """Accept a longer replacement, or refuse it with the measured reason.

        Three conditions gate it, and each failure says which one it was:
        the profile's table must be relocation-enabled, this entry's ownership
        must be proven, and the declared free space must actually fit the body.
        Capacity is decided by the real allocator running over the real plan, not
        estimated here - so "it fits" means the production path produced a plan.
        """
        deficit = len(encoded) - entry.location.allocation
        if not self.layout.relocatable:
            raise TextTooLongError(
                f"{identity}: encoded text needs {len(encoded)} bytes but its "
                f"allocation is {entry.location.allocation}; {deficit} bytes too "
                "long. Growing a string requires relocation, which this profile's "
                "text table does not declare (relocatable: false)."
            )
        if identity not in self._owned:
            raise TextTooLongError(
                f"{identity}: encoded text needs {len(encoded)} bytes but its "
                f"allocation is {entry.location.allocation}; {deficit} bytes too "
                "long. Growing a string requires relocation, and this entry's "
                "inbound references are not exactly its own table slot, so moving "
                "its body would silently orphan whatever else reaches it."
            )
        candidate = dict(self._relocating)
        candidate[identity] = text
        try:
            self._relocation_result(candidate)
        except (LayoutError, ValueError) as exc:
            raise TextTooLongError(
                f"{identity}: encoded text needs {len(encoded)} bytes but its "
                f"allocation is {entry.location.allocation}; {deficit} bytes too "
                f"long. Relocation was planned but refused: {exc}"
            ) from None
        self._relocating = candidate

    # --- relocation ----------------------------------------------------

    def reserve(self, spans: "Iterable[RomRange]") -> None:
        """Withhold spans an earlier allocating domain of this build already took.

        TOOLKIT-036. Two allocators ran independently against the same declared
        free regions - this one and the placement domain's - each blind to the
        other, and met only at `plan_changes`, which is an overlap DETECTOR and not
        an allocator. The coordinator now threads one reservation set through the
        allocating domains in its existing order; this is where this domain
        receives it. The spans are subtracted from the free regions the relocator
        is offered, by the shared `allocation.withhold`, so nothing is invented:
        the remaining regions are the same declarations minus bytes spoken for.

        Plain spans in, nothing about their owner. This layer does not learn that
        placements exist, and the placement layer does not learn that text does.
        """
        self._reserved = tuple(spans)

    def allocated_spans(self) -> "tuple[RomRange, ...]":
        """The spans this build's text relocations took, for the reservation set."""
        if not self._relocating:
            return ()
        return tuple(a.range for a in self._relocation_result(self._relocating).allocations)

    def reference_document(self, identities: "Iterable[TextIdentity]"):
        """The reference graph for the entries a relocation batch names.

        TOOLKIT-036. `plan_relocation` moves EXISTING anchors and rewrites
        EXISTING references; this is where the text domain publishes them, which
        mirrors how `authored_placements.authoring_overlay` publishes the
        placement domain's. Two declarations per entry and no more, because two
        is the whole measured surface:

          * one anchor over exactly the body's current bytes, kind
            `TEXT_STRING_KIND` (listed in `layout.RELOCATION_ELIGIBLE_KINDS`, so
            the existing path accepts it), marked relocatable only for entries
            `_owned` proved carry exactly one aligned inbound reference;
          * one `ABSOLUTE_ROM_U32_LE` DECLARED_REFERENCE sourced at that entry's
            own pointer-table slot and targeting the body at delta 0.

        Only the named entries are published. Publishing all 1,534 would be
        publishing 1,534 anchors and 1,534 reference fields to move one string,
        and `RomDocument.validate` would then decode every one of them on every
        edit for no gain - the relocator only needs the graph around what moves.
        """
        from .allocation import withhold
        from .binary import FileOffset
        from .document import RomDocument
        from .layout import (Anchor, Provenance, Reference, ReferenceClass,
                             ReferenceEncoding)

        profile = self.profile
        if self._reserved:
            # TOOLKIT-036. The relocator derives its capacity from the profile it is
            # handed, so the build-scoped reservation is expressed in exactly that
            # capacity - the same place, and by the same subtraction, the placement
            # domain already used for its own two passes.
            profile = replace(profile,
                              free_regions=withhold(profile.free_regions, self._reserved))

        provenance = Provenance(self.profile.id, self.profile.sha256,
                                self.layout.evidence)
        anchors = []
        references = []
        for identity in sorted(identities, key=lambda i: i.index):
            entry = self.entry(identity)
            anchors.append(Anchor(
                _anchor_id(identity),
                RomRange(FileOffset(entry.location.file_offset),
                         entry.location.allocation),
                TEXT_STRING_KIND, entry.identity.key, self.layout.alignment,
                identity in self._owned, provenance))
            references.append(Reference(
                FileOffset(entry.location.pointer_offset),
                _anchor_id(identity), 0,
                ReferenceEncoding.ABSOLUTE_ROM_U32_LE,
                ReferenceClass.DECLARED_REFERENCE, provenance))
        return RomDocument.from_bytes(self._base_bytes, profile,
                                      anchors=tuple(anchors),
                                      references=tuple(references))

    def _relocation_result(self, relocating: "dict[TextIdentity, str]"):
        """Plan one batch through the production relocator. Writes nothing."""
        from .relocation import RelocationRequest, plan_relocation

        document = self.reference_document(relocating)
        return plan_relocation(document, [
            RelocationRequest(_anchor_id(identity), self.codec.encode(text))
            for identity, text in sorted(relocating.items(), key=lambda i: i[0].index)])

    def relocations(self) -> "tuple":
        """Provenance for every text body this build moves; empty when none do."""
        if not self._relocating:
            return ()
        return self._relocation_result(self._relocating).plan.relocations

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
            if entry.identity in self._relocating:
                # TOOLKIT-036. A relocated body does not fit where it was, so it
                # has no in-place change to make. Its bytes are written at the
                # allocated destination and its table slot is rewritten to point
                # there; both come from the relocation plan below. Emitting the
                # old span too would claim bytes this build deliberately retires.
                continue
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
        if self._relocating:
            # The relocator's own effective changes: each moved body at its
            # allocated home, and each owning table slot rewritten to reach it.
            # They join the SAME attributed change set as every in-place edit, so
            # a relocation that claimed bytes another subsystem also writes is an
            # overlap error in the merged plan rather than a silent overwrite.
            changes += self._relocation_result(self._relocating).plan.effective_changes
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

    # TOOLKIT-036. An image containing relocations is read by proving each one,
    # not by tolerating holes. Each hole is claimed by exactly one entry - the one
    # whose pointer now resolves outside the pool - and the span it must account
    # for is the string still lying at the tiling cursor, because a relocation
    # retires the old bytes rather than clearing them. So the pool stays fully
    # accounted for: every byte is either a live body or a proven vacated one.
    writable = _writable_regions(profile)
    vacated = _vacated_spans(data, table, codec, table_start, pool_start, pool_end)

    entries: list[TextEntry] = []
    for raw in codec.enumerate_pool(data, table, table_start, pool_start, pool_end,
                                    vacated, writable):
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
    # TOOLKIT-036. Ownership is measured only where the profile's table declares
    # relocation at all, so a table that is not relocation-enabled pays nothing
    # for the census and no entry of it is ever eligible.
    if table.relocatable:
        strings._owned = _owned_entries(data, tuple(entries), codec)
    return strings
