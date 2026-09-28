"""Unit tests for the map-layout half of provenance, and its ROM-free refusals.

Synthetic only: the manifest parser, the identity checks and the canonical
reconstruction are no longer this module's code - they live once in
``tools.webfoot.authored_image`` and are pinned by ``tests/unit/test_authored_image.py``
against a synthetic domain. What is pinned *here* is what stays specific to a
map-layout derivative: the owner vocabulary this editor writes, and the public
error type and document path the rest of the product uses. The end-to-end
accept/reject behaviour against a real emitted ROM, including the same-layer
replacement rule, is pinned in ``tests/integration/test_map_layout_editor_rom.py``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.export import map_browser as mb
from tools.export import profile_authority
from tools.webfoot import map_layout_provenance as prov
from tools.webfoot.authored_image import DeclaredChange

CHUNKS = (0x082928DC, 0x08292A54)
OFFSET = 0x00292CA0

#: The one profile-backed identity, which the manifest must name as its base.
CANONICAL_SHA256 = profile_authority.canonical_export_identity().sha256


def _change(**overrides) -> dict:
    change = {
        "offset": OFFSET,
        "offset_hex": f"0x{OFFSET:08X}",
        "size": 4,
        "old": CHUNKS[0].to_bytes(4, "little").hex(),
        "new": CHUNKS[1].to_bytes(4, "little").hex(),
        "owner": "map:0040 layer 1 cell 0",
        "reason": prov.REASON,
    }
    change.update(overrides)
    return change


def _document(changes: list[dict] | None = None, **overrides) -> dict:
    document = {
        "schema_version": 1,
        "base": {"profile_id": "buus_fury_usa_rev0_01c1707f", "sha256": CANONICAL_SHA256},
        "output": {"sha256": "00" * 32, "size": 8},
        "changed_byte_count": 2,
        "changes": [_change()] if changes is None else changes,
    }
    document.update(overrides)
    return document


def _declared(owner: str) -> DeclaredChange:
    return DeclaredChange(
        owner=owner,
        offset=OFFSET,
        old=CHUNKS[0].to_bytes(4, "little"),
        new=CHUNKS[1].to_bytes(4, "little"),
    )


def test_manifest_path_is_a_sibling_of_its_rom() -> None:
    rom = Path("/roms/Dragon Ball Z - Buu's Fury (U) - Edited.gba")
    manifest = prov.manifest_path_for(rom)
    assert manifest.parent == rom.parent
    assert manifest.name == "Dragon Ball Z - Buu's Fury (U) - Edited.gba.dragonbyte.json"
    # The document convention is the shared one, not a second copy of it.
    assert prov.MANIFEST_SUFFIX == ".dragonbyte.json"


@pytest.mark.parametrize(
    "owner",
    [
        "enemy:434",
        "map:0040 layer 1 cell 0 ",
        "map:040 layer 1 cell 0",
        "map:0040 layer 1 cell",
        "map:0040 layer 4 cell 0",
        "map:0040 BG1 cell 0",
        "",
    ],
)
def test_a_declared_change_must_name_a_field_this_editor_writes(owner: str) -> None:
    """The owner vocabulary is this editor's, and nothing else's.

    Checked through the domain hook directly: these refusals must not depend on
    the canonical image being readable, which is why the owner is the first thing
    the hook inspects.
    """
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov._check_layout_changes((_declared(owner),), b"", b"")
    assert "did not make" in str(excinfo.value)


def test_a_declared_change_may_not_name_a_map_out_of_range() -> None:
    """The map-range rule is checked before the image is read, so it is portable.

    ROM-free on purpose: without this, the newest rule in the domain hook is
    exercised only where the canonical ROM is configured.
    """
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov._check_layout_changes((_declared("map:0452 layer 1 cell 0"),), b"", b"")
    assert "out of range" in str(excinfo.value)


def test_a_missing_or_malformed_manifest_is_refused(tmp_path: Path) -> None:
    rom = tmp_path / "edited.gba"
    rom.write_bytes(b"not a canonical rom")
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(rom)
    assert "provenance manifest" in str(excinfo.value)
    assert prov.manifest_path_for(rom).name in str(excinfo.value)

    prov.manifest_path_for(rom).write_text("not json", encoding="utf-8")
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(rom)
    assert "malformed" in str(excinfo.value)

    prov.manifest_path_for(rom).write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(prov.ProvenanceError):
        prov.verify_authored_rom(rom)


def test_an_unsupported_schema_is_refused(tmp_path: Path) -> None:
    rom = tmp_path / "edited.gba"
    rom.write_bytes(b"not a canonical rom")
    for schema in (2, "1", True, None):
        manifest = _document(schema_version=schema)
        manifest["output"] = {
            "sha256": hashlib.sha256(b"not a canonical rom").hexdigest(),
            "size": len(b"not a canonical rom"),
        }
        prov.manifest_path_for(rom).write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(prov.ProvenanceError) as excinfo:
            prov.verify_authored_rom(rom)
        assert "schema" in str(excinfo.value)


def test_the_base_must_be_the_supported_canonical_image(tmp_path: Path) -> None:
    """This editor builds from one canonical image, and only that one."""
    rom = tmp_path / "edited.gba"
    rom.write_bytes(b"not a canonical rom")
    manifest = _document()
    manifest["output"] = {
        "sha256": hashlib.sha256(b"not a canonical rom").hexdigest(),
        "size": len(b"not a canonical rom"),
    }
    manifest["base"]["sha256"] = "ab" * 32
    prov.manifest_path_for(rom).write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(rom)
    assert "canonical base" in str(excinfo.value)


def test_an_explicit_manifest_path_is_honoured(tmp_path: Path) -> None:
    rom = tmp_path / "edited.gba"
    rom.write_bytes(b"not a canonical rom")
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.write_text(json.dumps(_document()), encoding="utf-8")
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(rom, manifest_path=elsewhere)
    # Reached the declared-output check, so the explicit manifest was read.
    assert "does not match its provenance" in str(excinfo.value)


def test_an_expanded_derivative_reopens_using_the_profile_canonical_size(
    tmp_path: Path,
) -> None:
    """A derivative larger than the canonical image still proves its base.

    The canonical span is the profile's own declared size, not a literal: this
    pins that ``verify_authored_rom`` takes the base extent from
    ``RomProfile.identity`` (here reached through the export authority, the same
    triple) rather than hashing whatever length the file happens to be.

    The image is synthetic, so it is not the canonical bytes; what the
    reconstruction must produce is exactly the profile's canonical *length*, and
    that span is then held to the canonical digest and refused. A refusal whose
    reconstructed digest differs from the image's own digest is the positive
    evidence that the generated tail was excluded: hashing the whole file could
    only ever report the longer buffer's digest.
    """
    identity = profile_authority.canonical_export_identity()
    canonical_size = identity.image_size
    padding_byte = 0x5A
    # A file the profile would measure as canonical in length, then expanded.
    expanded = (
        bytes([padding_byte]) * canonical_size
        + bytes([padding_byte]) * canonical_size
    )
    assert len(expanded) == 2 * canonical_size, "the fixture really is expanded"

    rom = tmp_path / "expanded.gba"
    rom.write_bytes(expanded)
    manifest = _document()
    manifest["output"] = {
        "sha256": hashlib.sha256(expanded).hexdigest(),
        "size": len(expanded),
    }
    prov.manifest_path_for(rom).write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(rom)

    message = str(excinfo.value)
    # It reached reconstruction (not an identity or size refusal) ...
    assert "canonical ROM plus the changes" in message
    # ... and the span it hashed is the canonical one, not the whole file:
    # reversing the declared change over the canonical prefix is what the rule
    # reports, while the generated tail never enters the digest at all.
    declared = _change()
    span = bytearray(expanded[:canonical_size])
    span[declared["offset"] : declared["offset"] + declared["size"]] = bytes.fromhex(
        declared["old"]
    )
    assert hashlib.sha256(bytes(span)).hexdigest() in message
    assert hashlib.sha256(expanded).hexdigest() not in message
