"""Semantic access to the Buu's Fury string table.

TOOLKIT-004. This is the layer callers are meant to use::

    strings = load_text_strings(rom_path, catalog)
    entry = strings.entry(TextIdentity(12))
    strings.set_text(entry.identity, "New Game")
    plan = strings.plan()

A caller names a string by identity and supplies text. It never computes a file
offset, never touches the pointer table, and never sees raw bytes - those are
provenance carried alongside a value, which is the boundary `ARCH-TOOL-001`
requires so a decomp backend can later replace the binary one underneath.

The extents come from the ROM profile rather than from module constants, so a
second game or revision is a data change rather than a code change.

**Why in-place edits are the shipped capability.** The pool is exhaustively
tiled: every byte belongs to exactly one string, and each string abuts the next.
There is therefore no slack after a string to grow into, and a longer string
must be relocated rather than extended. Relocation needs profile-declared free
space, which no verified Buu's Fury profile has - so this layer supports edits
that fit the original allocation, and reports the exact deficit when one does
not. `webfoot.relocation` proves the growth path on synthetic fixtures instead.

Shorter text is padded to the original allocation rather than shrinking it.
Repacking the pool would move every subsequent string and rewrite all 1,534
pointers to reclaim a few bytes, converting a one-word edit into a whole-region
rewrite; the padding is deterministic, so a build stays reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cache
from importlib import resources
import os
from pathlib import Path
from typing import Iterator

from .formats import text_tables as tt
from .formats.text_tables import TextCodecError, TextIdentity
from .hashing import hash_stream
from .profile import (
    RomProfile,
    RomProfileCatalog,
    TextTableProfile,
    VerificationStatus,
)
from .rom import RomChangedError, RomIdentification, identify_rom
from .write import ByteChange, WritePlan, plan_changes


class TextTableError(ValueError):
    """Base error for semantic string-table access."""


class TextProfileError(TextTableError):
    """Raised when a ROM or profile is not authorized for text access."""


class UnknownTextError(TextTableError):
    """Raised when an identity names no string in this table."""


class TextTooLongError(TextTableError):
    """Raised when edited text cannot fit the string's current allocation.

    Distinct from a validation failure on purpose: the text is *well-formed*,
    and would be writable if this profile declared free space to relocate into.
    The message therefore reports the deficit rather than implying the text is
    wrong.
    """


#: The profile whose text extents TOOLKIT-004 verified against the canonical ROM.
SUPPORTED_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"

#: CONFIRMED. Byte written into the slack left by a shorter replacement. Zero,
#: because a run of `00 00` past a terminator is what the untouched image
#: already contains between the pool's end and the pointer table, and because
#: any nonzero filler would decode as text if a terminator were ever lost.
PAD_BYTE = 0x00


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


@cache
def _supported_profile_contract() -> RomProfile:
    """The packaged, in-repo statement of where the string table lives.

    Read from the packaged catalog rather than from whatever the caller passed
    to `--profiles`, so it cannot be redirected by a supplied file.
    """
    packaged = resources.files("tools.webfoot.data").joinpath("roms.yaml")
    catalog = RomProfileCatalog.loads(
        packaged.read_text(encoding="utf-8"),
        source="packaged tools.webfoot.data/roms.yaml",
    )
    try:
        profile = next(
            item for item in catalog.profiles if item.id == SUPPORTED_PROFILE_ID
        )
    except StopIteration as exc:
        raise TextProfileError(
            f"packaged catalog has no {SUPPORTED_PROFILE_ID!r} profile"
        ) from exc
    if profile.text_strings is None:
        raise TextProfileError(
            "packaged target profile does not declare the string table"
        )
    return profile


def _require_text_profile(identification: RomIdentification) -> RomProfile:
    """Fail closed unless this exact ROM is verified and declares the table.

    The supplied profile is cross-checked against the packaged contract for the
    same reason `stats._require_stat_profile` does it: identity verification
    authenticates the ROM, not the metadata describing it, so without this a
    hand-edited `--profiles` YAML could keep the hashes intact while moving the
    declared extents, and the toolkit would write text into whatever region
    that file named.
    """
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise TextProfileError("text access requires an exactly verified ROM")
    profile = match.profile
    if profile.text_strings is None:
        raise TextProfileError(
            f"profile {profile.id!r} does not declare a string table; "
            "text access is unavailable for this ROM"
        )
    if profile.id != SUPPORTED_PROFILE_ID:
        raise TextProfileError(
            f"text access supports only profile {SUPPORTED_PROFILE_ID!r}; "
            f"got {profile.id!r}"
        )

    contract = _supported_profile_contract()
    if profile.text_strings != contract.text_strings:
        raise TextProfileError(
            "supplied profile text metadata conflicts with the packaged "
            "contract; refusing to read or write against unverified extents"
        )
    if (
        identification.hashes.sha256 != contract.sha256
        or identification.size != contract.size
    ):
        raise TextProfileError(
            "text access requires the exact TOOLKIT-004 target identity"
        )
    return profile


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
    ) -> None:
        self.identification = identification
        self.profile = profile
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
        encoded = tt.encode_string(text)  # raises TextCodecError if malformed
        allocation = entry.location.allocation
        if len(encoded) > allocation:
            raise TextTooLongError(
                f"{identity}: encoded text needs {len(encoded)} bytes but its "
                f"allocation is {allocation}; {len(encoded) - allocation} bytes "
                "too long. Growing a string requires relocation, and this "
                "profile declares no verified free space."
            )
        self._entries[identity] = replace(entry, text=text)
        if text != _original_text(entry):
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
            encoded = tt.encode_string(entry.text)
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


def _original_text(entry: TextEntry) -> str:
    text, _ = tt.decode_string(entry.original_bytes, 0)
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

    pool_start = table.pool_address.to_file_offset(len(data))
    pool_end = pool_start + table.pool_size
    table_start = table.pointer_table_address.to_file_offset(len(data))
    if pool_end > len(data) or table_start + table.pointer_table_size > len(data):
        raise TextProfileError("configured text regions extend beyond the ROM")

    entries: list[TextEntry] = []
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
        # The exhaustive tiling is a declared property of this profile, so a
        # violation means the image or the metadata is not what it claims.
        # Checking it during the load makes that a refusal rather than a subtly
        # wrong allocation size later.
        if offset != expected:
            raise TextProfileError(
                f"string {index} starts at {offset:#010x}, but the previous "
                f"string ends at {expected:#010x}; the declared pool is not "
                "exhaustively tiled"
            )
        expected = end
        entries.append(
            TextEntry(
                identity=TextIdentity(index),
                text=text,
                location=TextLocation(
                    index=index,
                    file_offset=offset,
                    allocation=end - offset,
                    pointer_offset=table_start + index * tt.TEXT_POINTER_SIZE,
                ),
                original_bytes=data[offset:end],
            )
        )

    if expected != pool_end:
        raise TextProfileError(
            f"strings end at {expected:#010x} but the declared pool ends at "
            f"{pool_end:#010x}; the enumeration is not exhaustive"
        )

    strings = TextStrings(
        identification=identification,
        profile=profile,
        entries=tuple(entries),
    )
    strings._base_bytes = data
    return strings
