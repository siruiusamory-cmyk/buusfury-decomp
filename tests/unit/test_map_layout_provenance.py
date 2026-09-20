"""Unit tests for the provenance document's ROM-free pieces.

Synthetic only: the manifest parser, the identity checks and the canonical
reconstruction are pure functions of bytes and a document, so the rejection rules
are pinned here in CI - which has no canonical ROM. The end-to-end accept/reject
behaviour against a real emitted ROM is pinned in
``tests/integration/test_map_layout_editor_rom.py``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.export import map_browser as mb
from tools.webfoot import map_layout_provenance as prov

CHUNKS = (0x082928DC, 0x08292A54)
OFFSET = 0x00292CA0


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
        "base": {"profile_id": "buus_fury_usa_rev0_01c1707f", "sha256": mb.SUPPORTED_ROM_SHA256},
        "output": {"sha256": "00" * 32, "size": 8},
        "changed_byte_count": 2,
        "changes": [_change()] if changes is None else changes,
    }
    document.update(overrides)
    return document


def test_manifest_path_is_a_sibling_of_its_rom() -> None:
    rom = Path("/roms/Dragon Ball Z - Buu's Fury (U) - Edited.gba")
    manifest = prov.manifest_path_for(rom)
    assert manifest.parent == rom.parent
    assert manifest.name == "Dragon Ball Z - Buu's Fury (U) - Edited.gba.dragonbyte.json"


def test_a_declared_change_must_be_this_tools_output() -> None:
    assert len(prov._declared_edits(_document())) == 1
    for bad in (
        _change(owner="enemy:434"),
        _change(owner="map:0040 layer 1 cell 0 "),
        _change(owner=None),
        _change(reason="something else"),
        _change(size=2),
        _change(offset=OFFSET + 1),
        _change(offset=-4),
        _change(old="zz"),
        _change(old="00"),
        _change(new=_change()["old"]),
        _change(owner="map:0452 layer 1 cell 0"),
        _change(owner="map:0040 layer 4 cell 0"),
    ):
        with pytest.raises(prov.ProvenanceError):
            prov._declared_edits(_document([bad]))


def test_two_changes_may_not_write_one_field() -> None:
    with pytest.raises(prov.ProvenanceError):
        prov._declared_edits(_document([_change(), _change()]))


def test_a_manifest_must_declare_at_least_one_change() -> None:
    absent = _document()
    absent["changes"] = None
    missing = _document()
    del missing["changes"]
    for document in (_document([]), absent, missing, _document(changes="changes")):
        with pytest.raises(prov.ProvenanceError):
            prov._declared_edits(document)


def test_the_base_must_be_the_supported_canonical_image() -> None:
    assert prov._canonical_base(_document())[1] == "buus_fury_usa_rev0_01c1707f"
    for document in (
        _document(base={"profile_id": "buus_fury_usa_rev0_01c1707f", "sha256": "ab" * 32}),
        _document(base={"profile_id": "", "sha256": mb.SUPPORTED_ROM_SHA256}),
        _document(base="elsewhere"),
        {},
    ):
        with pytest.raises(prov.ProvenanceError):
            prov._canonical_base(document)


def test_the_image_must_match_its_declared_output() -> None:
    data = b"image"
    digest = hashlib.sha256(data).hexdigest()
    assert (
        prov._output_identity(
            _document(output={"sha256": digest, "size": len(data)}), data
        )
        == digest
    )
    for output in (
        {"sha256": "ab" * 32, "size": len(data)},
        {"sha256": digest, "size": len(data) + 1},
        {"sha256": digest},
        "unstructured",
    ):
        with pytest.raises(prov.ProvenanceError):
            prov._output_identity(_document(output=output), data)


def test_canonical_reconstruction_is_required() -> None:
    edit = prov.AuthoredEdit(
        map_index=40, layer_slot=1, cell=0, offset=OFFSET, old=CHUNKS[0], new=CHUNKS[1]
    )
    # Synthetic bytes whose inversion cannot hash to the canonical image.
    with pytest.raises(prov.ProvenanceError):
        prov._reconstruct_canonical(b"\x00" * 64, (edit,))
    # A change whose span runs past the image is refused before hashing.
    with pytest.raises(prov.ProvenanceError):
        prov._reconstruct_canonical(b"\x00" * 2, (edit,))


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
    manifest = _document(schema_version=2)
    manifest["output"] = {
        "sha256": hashlib.sha256(b"not a canonical rom").hexdigest(),
        "size": len(b"not a canonical rom"),
    }
    prov.manifest_path_for(rom).write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(rom)
    assert "schema" in str(excinfo.value)


def test_an_explicit_manifest_path_is_honoured(tmp_path: Path) -> None:
    rom = tmp_path / "edited.gba"
    rom.write_bytes(b"not a canonical rom")
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.write_text(json.dumps(_document()), encoding="utf-8")
    with pytest.raises(prov.ProvenanceError) as excinfo:
        prov.verify_authored_rom(rom, manifest_path=elsewhere)
    # Reached the declared-output check, so the explicit manifest was read.
    assert "does not match its provenance" in str(excinfo.value)
