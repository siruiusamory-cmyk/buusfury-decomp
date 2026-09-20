"""DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001 - provenance for DragonByte Z-authored ROMs.

The Map Browser renders the canonical image and refuses any other image, because the
accepted readers resolve profile-specific addresses. A ROM this editor writes is the
canonical image plus a handful of four-byte dominant-layer chunk-pointer fields, and
the product flow requires that the user can reopen it. So a derivative is accepted
only when it can be *proved* to be canonical apart from declared, policy-legal layout
edits:

* a sibling manifest, in the project's existing write-manifest document shape
  (:meth:`tools.webfoot.write.WriteManifest.dumps`), names the canonical base by
  SHA-256 and by profile, and declares every change with its file offset and both
  byte values;
* the file's own SHA-256 must equal the manifest's declared output digest;
* every declared change must be a four-byte field of a supported map's *dominant*
  chunk window, addressable from its own semantic owner string
  (``map:NNNN layer S cell C``), and must put a non-null chunk that the layer
  already uses at another of its cells into that cell - the single write operation
  MAP-LAYOUT-WRITE-001 proved; and
* restoring each declared ``old`` value at its declared span must reproduce the
  canonical image exactly: SHA-256 equal to the supported canonical hash.

That last check is decisive. It bounds an accepted derivative to the canonical image
plus exactly the declared four-byte fields, so an arbitrary modified ROM cannot pass,
and it needs no copy of the canonical file - the canonical bytes are reconstructed
from the derivative itself.

The canonical image is untouched as the fully trusted baseline: it is accepted by
identity before any manifest is consulted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from tools.export import canonical as canon
from tools.export import map_browser as mb

from .map_layout_write import MapLayoutWriteError, MapLayoutWriter

#: The sibling manifest a DragonByte Z-authored ROM ships with, appended to the
#: ROM's own file name so one image maps to exactly one provenance document.
MANIFEST_SUFFIX = ".dragonbyte.json"

#: The only manifest schema this build understands.
SUPPORTED_SCHEMA_VERSION = 1

#: The semantic owner this editor gives every change it plans.
_OWNER = re.compile(r"^map:(\d{4}) layer ([0-3]) cell (\d+)$")

#: The reason string the layout editor records; a manifest claiming a different
#: reason is not this tool's output.
REASON = "existing same-layer chunk replacement"

#: Encoded width of a dominant-layer chunk-pointer field.
FIELD_BYTES = 4


class ProvenanceError(ValueError):
    """A non-canonical ROM did not prove that it is a tool-authored derivative."""


@dataclass(frozen=True, slots=True)
class AuthoredEdit:
    """One declared four-byte layout change, verified against the image."""

    map_index: int
    layer_slot: int
    cell: int
    offset: int
    old: int
    new: int


@dataclass(frozen=True, slots=True)
class AuthoredRom:
    """A verified DragonByte Z derivative: canonical plus declared layout edits."""

    path: Path
    manifest_path: Path
    profile_id: str
    #: The canonical image this derivative derives from, by SHA-256. The profile
    #: identity the manifest names must be the profile *of this image*.
    canonical_sha256: str
    output_sha256: str
    edits: tuple[AuthoredEdit, ...]
    #: The reconstructed canonical image, proven equal to the supported ROM by
    #: SHA-256. Every accepted reader runs against these bytes.
    canonical_image: bytes

    @property
    def maps_edited(self) -> tuple[int, ...]:
        """The distinct maps this derivative changes, in order."""
        return tuple(dict.fromkeys(edit.map_index for edit in self.edits))

    def overrides_for(self, map_index: int) -> dict[tuple[int, int], int]:
        """``{(layer slot, cell): replacement pointer}`` for one map."""
        return {
            (edit.layer_slot, edit.cell): edit.new
            for edit in self.edits
            if edit.map_index == map_index
        }

    def summary(self) -> str:
        """One honest line: what this image is, and how much of it was edited."""
        maps = ", ".join(f"map:{index:04d}" for index in self.maps_edited)
        return (
            f"DragonByte Z layout derivative of the canonical ROM "
            f"({len(self.edits)} verified layout change(s) on {maps})"
        )


def manifest_path_for(rom_path: str | Path) -> Path:
    """The provenance document path that belongs to one ROM file."""
    path = Path(rom_path)
    return path.with_name(path.name + MANIFEST_SUFFIX)


def _load_manifest(manifest_path: Path) -> dict:
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProvenanceError(
            f"no readable DragonByte Z provenance manifest beside this ROM "
            f"({manifest_path.name}): {exc}"
        ) from exc
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProvenanceError(f"malformed provenance manifest: {exc}") from exc
    if not isinstance(document, dict):
        raise ProvenanceError("malformed provenance manifest: not a JSON object")
    return document


def _declared_edits(document: dict) -> tuple[AuthoredEdit, ...]:
    """Parse and structurally check the manifest's change list."""
    changes = document.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ProvenanceError("the manifest declares no layout changes")
    edits: list[AuthoredEdit] = []
    seen: set[int] = set()
    changed_bytes = 0
    for change in changes:
        if not isinstance(change, dict):
            raise ProvenanceError("malformed provenance manifest: a change is not an object")
        owner = change.get("owner")
        match = _OWNER.match(owner) if isinstance(owner, str) else None
        if match is None:
            raise ProvenanceError(
                f"the manifest declares a change this tool did not make: owner {owner!r}"
            )
        if change.get("reason") != REASON:
            raise ProvenanceError(
                f"the manifest declares an unsupported change reason: {change.get('reason')!r}"
            )
        if change.get("size") != FIELD_BYTES:
            raise ProvenanceError(
                f"a layout change must be {FIELD_BYTES} bytes, not {change.get('size')!r}"
            )
        offset = change.get("offset")
        if type(offset) is not int or offset < 0 or offset % FIELD_BYTES:
            raise ProvenanceError(f"a layout change has an unaligned offset: {offset!r}")
        if offset in seen:
            raise ProvenanceError(f"two layout changes write the same field at 0x{offset:08X}")
        seen.add(offset)
        old = _field(change.get("old"), "old", offset)
        new = _field(change.get("new"), "new", offset)
        if old == new:
            raise ProvenanceError(f"a layout change at 0x{offset:08X} changes nothing")
        changed_bytes += sum(1 for before, after in zip(old, new) if before != after)
        edits.append(
            AuthoredEdit(
                map_index=int(match.group(1)),
                layer_slot=int(match.group(2)),
                cell=int(match.group(3)),
                offset=offset,
                old=int.from_bytes(old, "little"),
                new=int.from_bytes(new, "little"),
            )
        )
    for cell in edits:
        if cell.map_index >= canon.MAP_ENTRY_COUNT:
            raise ProvenanceError(
                f"the manifest names map:{cell.map_index:04d}, which is out of range"
            )
    declared = document.get("changed_byte_count")
    if declared != changed_bytes:
        raise ProvenanceError(
            f"the manifest declares {declared!r} changed byte(s) but its own changes "
            f"account for {changed_bytes}"
        )
    return tuple(edits)


def _field(value: object, name: str, offset: int) -> bytes:
    if not isinstance(value, str) or len(value) != FIELD_BYTES * 2:
        raise ProvenanceError(
            f"a layout change at 0x{offset:08X} has a bad {name} value: {value!r}"
        )
    try:
        field = bytes.fromhex(value)
    except ValueError as exc:
        raise ProvenanceError(
            f"a layout change at 0x{offset:08X} has a bad {name} value: {value!r}"
        ) from exc
    if len(field) != FIELD_BYTES:
        raise ProvenanceError(f"a layout change at 0x{offset:08X} has a bad {name} width")
    return field


def _canonical_base(document: dict) -> tuple[str, str]:
    base = document.get("base")
    if not isinstance(base, dict):
        raise ProvenanceError("malformed provenance manifest: no base identity")
    sha256 = base.get("sha256")
    profile_id = base.get("profile_id")
    if sha256 != mb.SUPPORTED_ROM_SHA256:
        raise ProvenanceError(
            "the manifest's canonical base is not the supported Buu's Fury USA rev0 image"
        )
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ProvenanceError("the manifest names no base profile")
    return sha256, profile_id


def _output_identity(document: dict, data: bytes) -> str:
    output = document.get("output")
    if not isinstance(output, dict):
        raise ProvenanceError("malformed provenance manifest: no output identity")
    declared = output.get("sha256")
    actual = hashlib.sha256(data).hexdigest()
    if declared != actual:
        raise ProvenanceError(
            f"the image does not match its provenance: manifest says {declared}, "
            f"the file is {actual}"
        )
    if output.get("size") != len(data):
        raise ProvenanceError(
            f"the image does not match its provenance: manifest says {output.get('size')} "
            f"bytes, the file is {len(data)}"
        )
    return actual


def _reconstruct_canonical(data: bytes, edits: tuple[AuthoredEdit, ...]) -> bytes:
    """Undo the declared changes and require the result to be the canonical image."""
    rebuilt = bytearray(data)
    for edit in edits:
        if edit.offset + FIELD_BYTES > len(rebuilt):
            raise ProvenanceError(
                f"a layout change at 0x{edit.offset:08X} lies outside the image"
            )
        rebuilt[edit.offset : edit.offset + FIELD_BYTES] = edit.old.to_bytes(
            FIELD_BYTES, "little"
        )
    digest = hashlib.sha256(rebuilt).hexdigest()
    if digest != mb.SUPPORTED_ROM_SHA256:
        raise ProvenanceError(
            "the image is not the canonical ROM plus the changes its manifest declares "
            f"(reconstructed SHA-256 {digest})"
        )
    return bytes(rebuilt)


def _verify_edits_against_canonical(
    data: bytes, canonical_image: bytes, edits: tuple[AuthoredEdit, ...]
) -> None:
    """Every declared change must be the operation the writer is allowed to make.

    Checked against the *canonical* window, which is the state the proven writer
    validated its replacements against: the replacement must be a non-null chunk
    that the same dominant layer already uses, at a cell that is not the edited one
    (otherwise the change would be a no-op, which the manifest already refuses).
    """
    rom = canon.Rom(canonical_image)
    entries = canon.read_map_entries(rom)
    for edit in edits:
        entry = entries[edit.map_index]
        layer = canon.read_layer(rom, entry.root_address, edit.layer_slot)
        if layer.handler != canon.DOMINANT_LAYER_HANDLER:
            raise ProvenanceError(
                f"the manifest edits BG{edit.layer_slot} of map:{edit.map_index:04d}, "
                "which is not a dominant chunk grid"
            )
        if not 0 <= edit.cell < len(layer.chunk_addresses):
            raise ProvenanceError(
                f"the manifest edits cell {edit.cell} of map:{edit.map_index:04d} "
                f"BG{edit.layer_slot}, which does not exist"
            )
        try:
            # The writer owns this arithmetic; re-deriving it here would be a second
            # copy of a format rule free to drift.
            expected_offset = MapLayoutWriter(canonical_image).chunk_pointer_offset(
                edit.map_index, edit.layer_slot, edit.cell
            )
        except MapLayoutWriteError as exc:
            raise ProvenanceError(
                f"the manifest's change at 0x{edit.offset:08X} is not a dominant-layer "
                f"field of map:{edit.map_index:04d} BG{edit.layer_slot}: {exc}"
            ) from exc
        if expected_offset != edit.offset:
            raise ProvenanceError(
                f"the manifest's change at 0x{edit.offset:08X} is not "
                f"map:{edit.map_index:04d} BG{edit.layer_slot} cell {edit.cell} "
                f"(that field is at 0x{expected_offset:08X})"
            )
        if data[edit.offset : edit.offset + FIELD_BYTES] != edit.new.to_bytes(
            FIELD_BYTES, "little"
        ):
            raise ProvenanceError(
                f"the image does not carry the declared value at 0x{edit.offset:08X}"
            )
        try:
            mb.validate_cell_replacement(layer.chunk_addresses, edit.new)
        except mb.MapBrowserError as exc:
            raise ProvenanceError(
                f"the manifest's change at 0x{edit.offset:08X} is not a supported "
                f"replacement: {exc}"
            ) from exc
        others = tuple(
            address
            for index, address in enumerate(layer.chunk_addresses)
            if index != edit.cell
        )
        if edit.new not in others:
            raise ProvenanceError(
                f"the manifest's change at 0x{edit.offset:08X} uses a chunk that "
                f"map:{edit.map_index:04d} BG{edit.layer_slot} does not already use "
                "elsewhere in that layer"
            )


def verify_authored_rom(
    rom_path: str | Path, *, manifest_path: str | Path | None = None
) -> AuthoredRom:
    """Prove that a non-canonical image is a DragonByte Z-authored derivative.

    Raises :class:`ProvenanceError` with the specific reason for anything that is
    not: no manifest, a malformed or unsupported manifest, a base that is not the
    supported canonical image, a file that does not match its declared output, a
    change outside the proven layout-write rules, or a file that is not the
    canonical image plus exactly its declared changes.
    """
    path = Path(rom_path)
    document_path = (
        Path(manifest_path) if manifest_path is not None else manifest_path_for(path)
    )
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ProvenanceError(f"cannot read {path}: {exc}") from exc

    document = _load_manifest(document_path)
    if type(document.get("schema_version")) is not int or (
        document["schema_version"] != SUPPORTED_SCHEMA_VERSION
    ):
        raise ProvenanceError(
            f"unsupported provenance schema {document.get('schema_version')!r}; "
            f"this build understands {SUPPORTED_SCHEMA_VERSION}"
        )
    canonical_sha256, profile_id = _canonical_base(document)
    output_sha256 = _output_identity(document, data)
    edits = _declared_edits(document)
    canonical_image = _reconstruct_canonical(data, edits)
    _verify_edits_against_canonical(data, canonical_image, edits)
    return AuthoredRom(
        path=path,
        manifest_path=document_path,
        profile_id=profile_id,
        canonical_sha256=canonical_sha256,
        output_sha256=output_sha256,
        edits=edits,
        canonical_image=canonical_image,
    )
