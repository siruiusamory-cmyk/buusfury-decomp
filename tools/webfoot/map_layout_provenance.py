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
* the file's own SHA-256 must equal the manifest's declared output digest, and each
  declared field must hold the declared new bytes;
* every declared change must be a four-byte field of a supported map's *dominant*
  chunk window, addressable from its own semantic owner string
  (``map:NNNN layer S cell C``), and must put a non-null chunk that the layer
  already uses at another of its cells into that cell - the single write operation
  MAP-LAYOUT-WRITE-001 proved; and
* restoring each declared ``old`` value at its declared span must reproduce the
  canonical image exactly: SHA-256 equal to the supported canonical hash.

The manifest identity, declared-change structure and canonical reconstruction are
not specific to map layouts: they live once in
:mod:`tools.webfoot.authored_image`, which every authored-image domain shares. What
stays here is exactly the map-layout half - the owner string this editor writes, the
one reason it records, the same-layer replacement rule, and the typed
:class:`AuthoredRom`/:class:`AuthoredEdit` the map readers consume.

The canonical image is untouched as the fully trusted baseline: it is accepted by
identity before any manifest is consulted.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from tools.export import canonical as canon
from tools.export import map_browser as mb

from .authored_image import (
    AUTHORED_MANIFEST_SUFFIX,
    SUPPORTED_SCHEMA_VERSION,
    AuthoredImageError,
    DeclaredChange,
    manifest_path_for,
    verify_authored_image,
)
from .map_layout_write import MapLayoutWriteError, MapLayoutWriter

#: ``MANIFEST_SUFFIX``, ``SUPPORTED_SCHEMA_VERSION`` and ``manifest_path_for`` are
#: re-exported from the shared layer on purpose: this module stays the place a
#: map-layout caller asks about a derivative and about where its document lives,
#: and the values are the shared ones rather than a second copy of them.

#: The sibling manifest a DragonByte Z-authored ROM ships with, appended to the
#: ROM's own file name so one image maps to exactly one provenance document.
MANIFEST_SUFFIX = AUTHORED_MANIFEST_SUFFIX

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


def _check_layout_changes(
    declared: tuple[DeclaredChange, ...], canonical_image: bytes, data: bytes
) -> tuple[tuple[int, int, int], ...]:
    """Every declared change must be the operation the writer is allowed to make.

    This is the domain half of provenance verification: the shared layer has
    already proved the image is the canonical image plus exactly these declared
    fields, and it is *this* rule - a four-byte dominant-layer chunk field, whose
    replacement the same layer already uses elsewhere - that decides whether such
    a derivative is one this editor could have written.

    Checked against the *canonical* window, which is the state the proven writer
    validated its replacements against. One reader and one writer are built for the
    whole check: the writer's constructor verifies the image by SHA-256, so
    constructing it per declared change would cost a full-image hash each time.
    """
    # The owner vocabulary is checked first, over the whole document: a manifest
    # this editor did not write is refused without reading the image at all.
    targets: list[tuple[int, int, int]] = []
    for change in declared:
        match = _OWNER.match(change.owner)
        if match is None:
            raise ProvenanceError(
                f"the manifest declares a change this tool did not make: "
                f"owner {change.owner!r}"
            )
        map_index = int(match.group(1))
        layer_slot = int(match.group(2))
        cell = int(match.group(3))
        if map_index >= canon.MAP_ENTRY_COUNT:
            raise ProvenanceError(
                f"the manifest names map:{map_index:04d}, which is out of range"
            )
        targets.append((map_index, layer_slot, cell))

    rom = canon.Rom(canonical_image)
    entries = canon.read_map_entries(rom)
    writer = MapLayoutWriter(canonical_image)
    for change, (map_index, layer_slot, cell) in zip(declared, targets):
        entry = entries[map_index]
        layer = canon.read_layer(rom, entry.root_address, layer_slot)
        if layer.handler != canon.DOMINANT_LAYER_HANDLER:
            raise ProvenanceError(
                f"the manifest edits BG{layer_slot} of map:{map_index:04d}, "
                "which is not a dominant chunk grid"
            )
        if not 0 <= cell < len(layer.chunk_addresses):
            raise ProvenanceError(
                f"the manifest edits cell {cell} of map:{map_index:04d} "
                f"BG{layer_slot}, which does not exist"
            )
        try:
            # The writer owns this arithmetic; re-deriving it here would be a second
            # copy of a format rule free to drift.
            expected_offset = writer.chunk_pointer_offset(map_index, layer_slot, cell)
        except MapLayoutWriteError as exc:
            raise ProvenanceError(
                f"the manifest's change at 0x{change.offset:08X} is not a dominant-layer "
                f"field of map:{map_index:04d} BG{layer_slot}: {exc}"
            ) from exc
        if expected_offset != change.offset:
            raise ProvenanceError(
                f"the manifest's change at 0x{change.offset:08X} is not "
                f"map:{map_index:04d} BG{layer_slot} cell {cell} "
                f"(that field is at 0x{expected_offset:08X})"
            )
        # The image carrying the declared replacement bytes is the shared layer's
        # check, not a second copy here.
        replacement = int.from_bytes(change.new, "little")
        try:
            mb.validate_cell_replacement(layer.chunk_addresses, replacement)
        except mb.MapBrowserError as exc:
            raise ProvenanceError(
                f"the manifest's change at 0x{change.offset:08X} is not a supported "
                f"replacement: {exc}"
            ) from exc
        others = tuple(
            address
            for index, address in enumerate(layer.chunk_addresses)
            if index != cell
        )
        if replacement not in others:
            raise ProvenanceError(
                f"the manifest's change at 0x{change.offset:08X} uses a chunk that "
                f"map:{map_index:04d} BG{layer_slot} does not already use "
                "elsewhere in that layer"
            )
    return tuple(targets)


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
    try:
        verified = verify_authored_image(
            rom_path,
            manifest_path=manifest_path,
            canonical_sha256=mb.SUPPORTED_ROM_SHA256,
            field_bytes=FIELD_BYTES,
            expected_reason=REASON,
            check_changes=_check_layout_changes,
        )
    except AuthoredImageError as exc:
        # The shared layer's refusals are this module's refusals too: one public
        # error type for every reason a derivative is not accepted.
        raise ProvenanceError(str(exc)) from exc
    return AuthoredRom(
        path=verified.path,
        manifest_path=verified.manifest_path,
        profile_id=verified.profile_id,
        canonical_sha256=verified.canonical_sha256,
        output_sha256=verified.output_sha256,
        edits=tuple(
            AuthoredEdit(
                map_index=change.target[0],
                layer_slot=change.target[1],
                cell=change.target[2],
                offset=change.offset,
                old=int.from_bytes(change.old, "little"),
                new=int.from_bytes(change.new, "little"),
            )
            for change in verified.changes
        ),
        canonical_image=verified.canonical_image,
    )
