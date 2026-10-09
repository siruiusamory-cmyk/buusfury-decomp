"""The one owner-bearing free byte edit.

A raw write is the product's honest fallback for bytes no domain model names. It
carries the owner `raw:<image address>`, which is what keeps the manifest
answerable - every emitted change still names who changed these bytes.

Three questions are answered here and nowhere else.

*What owns these bytes?* :func:`claimed_by` answers with an owner and the extent
it claims, or with nothing when the range is free. It consults all three sources
the product spec requires: the journal's own committed spans (a pending edit the
SDK has no word for), the declared table extents the profile vouches for, and
the atlas objects. The ROM surface passes the atlas from the range index it
already holds (S4); a caller without one keeps the conservative two-source
answer, and a byte is refused when ANY source claims it.

*Is this write confirmed?* An unclaimed overwrite changes bytes no model
explains, so it is refused until the caller states that the range, the old bytes
and the new bytes were shown to a person.

*What does the write look like as a change?* :func:`raw_change` mints the
`ByteChange` the plan consumes.

The document format is the journal's to persist; this module owns its shape so
the two cannot disagree.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path

from tools.webfoot.atlas import Atlas, Confidence, strength
from tools.webfoot.binary import GBA_ROM_BASE, FileOffset
from tools.webfoot.layout import RomRange
from tools.webfoot.profile import RomProfile
from tools.webfoot.project import ProjectFormatError, dump_toml, load_toml
from tools.webfoot.project.atomic import replace_document
from tools.webfoot.write import ByteChange

#: The journal target a raw write is committed under. One target, one owner
#: namespace, one adapter: a byte edit is not a second kind of document.
RAW_TARGET = "rawbytes"

#: Where the raw byte document lives inside a project. A sibling of the dialogue
#: document, written by the same atomic replacement and named by this module
#: alone; `read_project` loads exact names, so an existing reader ignores it.
RAW_DOCUMENT = Path("raw") / "bytes.toml"

#: The confidence at which an atlas object is treated as owning bytes. Weak
#: evidence must not be able to block an honest write, and the ROM surface reads
#: this same floor so the owners it shows and the writes it refuses agree.
OWNERSHIP_FLOOR = Confidence("INFERRED")


def blocks_a_write(confidence: Confidence) -> bool:
    """Whether evidence this strong makes the bytes someone else's to edit."""
    return strength(confidence) >= strength(OWNERSHIP_FLOOR)


class RawRefusal(Exception):
    """A free byte edit was refused; the message and the fields say why.

    ``owner`` is the claiming identity and ``claimed`` the extent it claims, so
    a caller can offer `Go to owner` without parsing the sentence.
    """

    def __init__(self, message: str, *, owner: str = "", claimed: RomRange | None = None):
        super().__init__(message)
        self.message = message
        self.owner = owner
        self.claimed = claimed


@dataclass(frozen=True, slots=True)
class RawWrite:
    """One requested overwrite at one file offset.

    ``before`` is what the image holds there and ``new`` is what replaces it;
    both are kept so the manifest is self-describing and the journal can undo the
    write from the two values alone.
    """

    offset: int
    before: bytes
    new: bytes
    confirmed: bool = False

    def __post_init__(self) -> None:
        if type(self.offset) is not int or self.offset < 0:
            raise RawRefusal("a raw byte write needs a non-negative file offset")
        for name in ("before", "new"):
            value = getattr(self, name)
            if not isinstance(value, bytes):
                raise RawRefusal(f"a raw byte write needs {name} bytes")
            if not value:
                raise RawRefusal(f"a raw byte write needs non-empty {name} bytes")
        if len(self.before) != len(self.new):
            raise RawRefusal(
                f"a raw byte write overwrites in place: {len(self.before)} -> "
                f"{len(self.new)} bytes needs a relocation, which S8 owns"
            )

    @property
    def span(self) -> RomRange:
        return RomRange(FileOffset(self.offset), len(self.before))

    @property
    def address(self) -> int:
        return GBA_ROM_BASE + self.offset

    @property
    def owner(self) -> str:
        return raw_owner(self.address)


@dataclass(frozen=True, slots=True)
class RawEdits:
    """The authored raw bytes of one project: file offset -> replacement bytes."""

    bytes_by_offset: dict[int, bytes] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.bytes_by_offset)

    def with_write(self, write: RawWrite) -> "RawEdits":
        return replace(self, bytes_by_offset={**self.bytes_by_offset, write.offset: write.new})


def raw_owner(address: int) -> str:
    """The owner namespace for a write at one image address."""
    return f"raw:0x{address:08X}"


def raw_change(write: RawWrite) -> ByteChange:
    """The SDK change one raw write mints."""
    return ByteChange(
        offset=write.offset,
        old=write.before,
        new=write.new,
        owner=write.owner,
        reason="raw byte write",
    )

# --- what owns these bytes ----------------------------------------------------


def declared_extents(profile: RomProfile) -> tuple[tuple[RomRange, str], ...]:
    """The extents the profile itself vouches for, as (range, owner) pairs.

    Owner names are the profile's own table and field names, so a refusal names
    a fact the configuration file states rather than anything invented here. It
    is public because it is also the range index's declared layer and the ROM
    surface's jump list: one list, so a table a jump offers and a table a write
    is refused by cannot disagree.
    """
    size = profile.size
    spans: list[tuple[RomRange, str]] = []

    def one(name: str, address, span_size: int) -> None:
        start = address.to_file_offset(size)
        if span_size > 0 and start < size:
            spans.append((RomRange(FileOffset(start), span_size), name))

    if profile.map_entries is not None:
        table = profile.map_entries
        one("map_entries", table.address, table.count * table.record_size)
    for name, table in (
        ("enemy_stats", profile.enemy_stats),
        ("character_base_stats", profile.character_base_stats),
        ("appearances", profile.appearances),
    ):
        if table is not None:
            one(name, table.address, table.total_size)
    text = profile.text_strings
    if text is not None:
        one("text_strings.pointer_table", text.pointer_table_address, text.count * 4)
        one("text_strings.pool", text.pool_address, text.pool_size)
    for script in profile.scripts or ():
        one("scripts", script.table_address, script.count * script.stride)
    if profile.placement_types is not None:
        table = profile.placement_types
        one(
            "placement_types",
            table.table_address,
            (table.max_selector + 1) * table.stride,
        )
    if profile.actor_sprites is not None:
        one(
            "actor_sprites",
            profile.actor_sprites.character_table_address,
            profile.actor_sprites.character_count * 4,
        )
    return tuple(spans)


def _atlas_span(atlas: Atlas, span: RomRange) -> tuple[str, RomRange] | None:
    """The strongest atlas object the range touches, if any is strong enough.

    Overlap, not containment of the first byte: a write that starts in an unowned
    gap and reaches into an object would otherwise be accepted over that object's
    bytes.
    """
    best: tuple[str, RomRange] | None = None
    best_strength = -1
    for item in atlas.objects:
        if not item.range.overlaps(span):
            continue
        rank = strength(item.confidence)
        if not blocks_a_write(item.confidence) or rank <= best_strength:
            continue
        best = (f"atlas:{item.identity}", item.range)
        best_strength = rank
    return best


def claimed_by(
    profile: RomProfile,
    span: RomRange,
    *,
    spans: frozenset[RomRange] = frozenset(),
    atlas: Atlas | None = None,
) -> tuple[str, RomRange] | None:
    """Who owns the bytes `span` covers, or nothing when they are free.

    `spans` are the byte ranges the journal's committed edits declare. They are
    consulted first because they are the one source the SDK cannot see: a
    semantic edit that has not been built has no word in any artifact yet.

    `atlas` is the third source the specification names. The ROM surface holds
    one already, taken from the range index over the open image, and passes it
    here; a caller without one keeps the conservative answer from the journal's
    spans and the profile's declared extents, rather than assembling an atlas of
    its own per write.
    """
    for declared in sorted(spans, key=lambda item: (item.start.value, item.size)):
        if declared.overlaps(span):
            # The owner is the edit's own, which only the journal holds; it is
            # substituted there rather than invented here.
            return ("", declared)
    if atlas is not None:
        found = _atlas_span(atlas, span)
        if found is not None:
            return found
    for declared, name in declared_extents(profile):
        if declared.overlaps(span):
            return (name, declared)
    return None


# --- the document -------------------------------------------------------------


def read_raw_document(path: Path) -> RawEdits:
    """Read the raw byte document, or an empty document when it is absent.

    Absence means "this project authors no raw byte", exactly as a missing
    dialogue document means "this project authors no dialogue".
    """
    if not path.exists():
        return RawEdits()
    try:
        document = load_toml(path.read_text(encoding="utf-8"))
    except (ProjectFormatError, OSError) as exc:
        raise RawRefusal(f"{path}: {exc}") from exc
    table = document.get("bytes")
    if table is None:
        return RawEdits()
    if not isinstance(table, dict) or not table:
        raise RawRefusal(f"{path}: a raw byte table must be a non-empty table")
    edits: dict[int, bytes] = {}
    for key, value in table.items():
        try:
            offset = int(key, 0)
        except ValueError as exc:
            raise RawRefusal(f"{path}: {key!r} is not a file offset") from exc
        if not isinstance(value, str) or not value or len(value) % 2:
            raise RawRefusal(f"{path}: raw byte value for 0x{offset:06X} is not hex")
        try:
            edits[offset] = bytes.fromhex(value)
        except ValueError as exc:
            raise RawRefusal(f"{path}: raw byte value for 0x{offset:06X} is not hex") from exc
    return RawEdits(edits)


def write_raw_document(directory: Path, edits: RawEdits) -> Path:
    """Persist the raw byte document, removing it when nothing is authored.

    An empty document is removed rather than written empty: a table with no
    bytes claims an intent that does not exist.
    """
    path = Path(directory) / RAW_DOCUMENT
    if not edits.bytes_by_offset:
        path.unlink(missing_ok=True)
        return path
    table = {
        f"0x{offset:08X}": value.hex()
        for offset, value in sorted(edits.bytes_by_offset.items())
    }
    return replace_document(path, dump_toml({"bytes": table}))
