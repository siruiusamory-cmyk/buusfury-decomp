"""The authored raw byte document, and the changes it mints. LOG1-RAW-WRITE-BUILD-001.

A raw write is the product's honest fallback for bytes no domain model names. The
document is authored by the desktop application and this module is the SDK's own
reader for it, so a build applies the bytes a person authored instead of emitting
the canonical image with the write absent.

**One shape, two readers, no second format.** `tools/dragonbyte/rawbytes.py`
declares the document this reads: a `[bytes]` table whose keys are file offsets
and whose values are lowercase hex. The shipping package may not import the
application (`tools/quality/architecture.py` RULE import-direction), so the parse
is written out here rather than imported, and
`tests/unit/test_raw_byte_document.py` reads one file through both readers and
asserts they agree - that test is what keeps the two spellings from drifting.

**The document states what the bytes become, never what they were.** `before` is
not stored, because the base image is the only authority for what the bytes were
and a stored copy could disagree with it. So the build derives `before` from the
image it is actually applying the write to, and `webfoot.write.plan_changes`
refuses the change when the base does not hold those bytes. Reading the value the
reader wants to see would prove nothing.

**Refused, not silently dropped.** A document this module cannot read raises
rather than reading as "this project authors no raw bytes": a build that emits the
canonical bytes while reporting success is the defect this ticket exists to
close.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..binary import GBA_ROM_BASE
from ..write import ByteChange
from .format import ProjectFormatError, load_toml

#: Where the raw byte document lives inside a project. The sibling dialogue
#: document's convention: a directory per optional document, one file in it, and
#: absence meaning "this project authors none of them".
RAW_BYTES_FILE = Path("raw") / "bytes.toml"

#: The one table a raw byte document may hold.
RAW_BYTES_TABLE = "bytes"


class RawByteDocumentError(ProjectFormatError):
    """The raw byte document is unreadable, and a build must not proceed."""


@dataclass(frozen=True, slots=True)
class RawByteEdits:
    """The authored raw bytes of one project: file offset -> replacement bytes.

    A mapping rather than a list of pairs, because the document is one and
    because a second write to one offset is a contradiction with one answer.
    """

    bytes_by_offset: dict[int, bytes] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.bytes_by_offset)


def read_raw_bytes(directory: str | Path) -> RawByteEdits:
    """Read a project's raw byte document, or nothing when it authors none.

    Absence is the only empty answer: a document that exists must parse, hold a
    non-empty `[bytes]` table and use a file offset as every key, or it is
    refused. Anything else would let a typo turn an authored write into a build
    that emits the canonical image and reports success.
    """
    path = Path(directory) / RAW_BYTES_FILE
    if not path.exists():
        return RawByteEdits()
    try:
        document = load_toml(path.read_text(encoding="utf-8"))
    except (ProjectFormatError, OSError) as exc:
        raise RawByteDocumentError(f"{path}: {exc}") from exc
    table = document.get(RAW_BYTES_TABLE)
    if table is None:
        return RawByteEdits()
    if not isinstance(table, dict) or not table:
        raise RawByteDocumentError(
            f"{path}: a raw byte table must be a non-empty table"
        )
    edits: dict[int, bytes] = {}
    for key, value in table.items():
        try:
            offset = int(key, 0)
        except ValueError as exc:
            raise RawByteDocumentError(f"{path}: {key!r} is not a file offset") from exc
        if not isinstance(value, str) or not value or len(value) % 2:
            raise RawByteDocumentError(
                f"{path}: raw byte value for 0x{offset:06X} is not hex"
            )
        try:
            edits[offset] = bytes.fromhex(value)
        except ValueError as exc:
            raise RawByteDocumentError(
                f"{path}: raw byte value for 0x{offset:06X} is not hex"
            ) from exc
    return RawByteEdits(edits)


def raw_byte_changes(edits: RawByteEdits, image: bytes) -> list[ByteChange]:
    """The SDK changes one raw byte document mints against `image`.

    `image` is the CANONICAL base the write is applied to, and every value here is
    what the image holds rather than what the document claims: the owner is the
    image address the write lands at, and the bytes it replaces are the image's
    own. A write that reaches outside the image, or one whose authored bytes are
    already the image's bytes, is refused or dropped as the reason states - never
    omitted silently.

    The overlap guard is not restated here. These changes go into the one plan
    `build_project` already forms, so a raw write that meets a semantic edit's
    bytes is the plan's `OverlappingChangeError` by the same rule as any other two
    domains.
    """
    changes: list[ByteChange] = []
    for offset in sorted(edits.bytes_by_offset):
        new = edits.bytes_by_offset[offset]
        if offset < 0 or offset + len(new) > len(image):
            raise RawByteDocumentError(
                f"raw byte write at 0x{offset:06X} for {len(new)} byte(s) is not "
                f"inside the {len(image)}-byte canonical image"
            )
        old = image[offset : offset + len(new)]
        if old == new:
            # An authored write equal to the base changes no byte, so it mints no
            # change: the manifest would have to report a write that is not one.
            continue
        changes.append(
            ByteChange(
                offset=offset,
                old=old,
                new=new,
                owner=f"raw:0x{GBA_ROM_BASE + offset:08X}",
                reason="raw byte write",
            )
        )
    return changes
