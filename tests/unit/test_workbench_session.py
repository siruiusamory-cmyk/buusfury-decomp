"""T1.2 tests for the workbench `Session` model.

The mismatch path needs no ROM: a bogus file whose bytes match no profile must
raise a typed, catchable error rather than crash. The happy path is ROM-gated
with the same convention the integration suite uses, and additionally skips if
the assembled atlas artifact is absent, since `open_rom` reads it.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot.cli import _default_atlas_directory
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.workbench.session import (
    RomNotRecognizedError,
    Session,
    SessionError,
)

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


def _rom_path() -> str:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(open(matches[0], "rb").read()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return matches[0]


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


def test_open_rom_populates_session(catalog: RomProfileCatalog) -> None:
    rom = _rom_path()
    if not (_default_atlas_directory() / "atlas.jsonl").is_file():
        pytest.skip("assembled atlas.jsonl not present locally")

    session = Session()
    session.open_rom(Path(rom), catalog)

    assert session.profile is not None
    assert session.profile.sha256 == CANONICAL_SHA256
    assert session.atlas is not None
    assert isinstance(session.decoded_text, list)
    assert session.rom_path == Path(rom)
    assert session.rom_image == open(rom, "rb").read()
    # The Inspector's selected record belongs to the image it was resolved
    # against, so opening another image cannot leave the old one addressable.
    assert session.selected_result is None


def test_open_rom_rejects_unrecognized_bytes(
    catalog: RomProfileCatalog, tmp_path: Path
) -> None:
    # A valid-length GBA image made of bytes that hash to no profile: the
    # identify path returns UNKNOWN and open_rom must raise the typed error.
    bogus = tmp_path / "bogus.gba"
    bogus.write_bytes(b"\x00" * 0x800000)

    session = Session()
    with pytest.raises(RomNotRecognizedError) as excinfo:
        session.open_rom(bogus, catalog)

    assert str(bogus) in str(excinfo.value)
    assert isinstance(excinfo.value, SessionError)
    # Nothing was populated on the failed open.
    assert session.profile is None
    assert session.rom_image is None


def test_open_rom_accepts_a_verified_derivative_with_the_canonical_bytes(
    catalog: RomProfileCatalog, tmp_path: Path
) -> None:
    """A DragonByte Z-authored ROM opens, and readers get the canonical bytes."""
    from tools.webfoot.map_layout_edit import MapLayoutEditor

    rom = _rom_path()
    if not (_default_atlas_directory() / "atlas.jsonl").is_file():
        pytest.skip("assembled atlas.jsonl not present locally")
    source = Path(rom).read_bytes()
    editor = MapLayoutEditor(source)
    editor.set_cell(40, 1, 0, 0x08292A54)
    output = tmp_path / "derived.gba"
    saved = editor.save(output, source_path=Path(rom), profile_id="buus_fury_usa_rev0_01c1707f")

    session = Session()
    session.open_rom(output, catalog)

    assert session.authored is not None
    assert session.profile is not None
    assert session.profile.id == "buus_fury_usa_rev0_01c1707f"
    # The accepted readers run against the reconstructed canonical image, never the
    # derivative's own bytes.
    assert session.map_image == source
    assert session.rom_image == output.read_bytes()
    assert session.layout_overrides(40) == {(1, 0): 0x08292A54}
    assert session.layout_overrides(41) == {}
    # A derivative declares no scene/text domain of its own, and no canonical
    # identification is claimed for it.
    assert session.maps is None
    assert session.text_strings is None
    assert session.identification is None
    assert saved.manifest_path.is_file()


def test_open_rom_refuses_a_derivative_whose_profile_is_not_its_base(
    catalog: RomProfileCatalog, tmp_path: Path
) -> None:
    """The manifest must name the profile *of* the image it derives from."""
    from tools.webfoot.map_layout_edit import MapLayoutEditor
    from tools.webfoot.map_layout_provenance import manifest_path_for

    rom = _rom_path()
    source = Path(rom).read_bytes()
    editor = MapLayoutEditor(source)
    editor.set_cell(40, 1, 0, 0x08292A54)
    output = tmp_path / "derived.gba"
    editor.save(output, source_path=Path(rom), profile_id="buus_fury_usa_rev0_01c1707f")

    document = json.loads(manifest_path_for(output).read_text(encoding="utf-8"))
    document["base"]["profile_id"] = "legacy_of_goku_usa_a3c8c767"
    manifest_path_for(output).write_text(json.dumps(document), encoding="utf-8")

    session = Session()
    with pytest.raises(RomNotRecognizedError) as excinfo:
        session.open_rom(output, catalog)
    assert "not the profile of the canonical image" in str(excinfo.value)
    assert session.authored is None
    assert session.profile is None


def test_open_rom_refuses_a_mutated_rom_without_provenance(
    catalog: RomProfileCatalog, tmp_path: Path
) -> None:
    rom = _rom_path()
    data = bytearray(Path(rom).read_bytes())
    data[0x00292CA0] ^= 0x01
    mutated = tmp_path / "mutated.gba"
    mutated.write_bytes(bytes(data))

    session = Session()
    with pytest.raises(RomNotRecognizedError) as excinfo:
        session.open_rom(mutated, catalog)

    assert "provenance manifest" in str(excinfo.value)
    assert session.profile is None
    assert session.rom_image is None
    assert session.authored is None
    assert session.provenance_error


def test_project_revision_invalidates_validation_and_build() -> None:
    session = Session()
    session.set_project(Path("project"))
    session.record_validation(True)
    session.last_build = object()
    session.build_revision = session.project_revision
    assert session.validation_current
    assert session.build_current

    session.project_mutated()

    assert not session.validation_current
    assert not session.build_current
    assert session.last_build is None
