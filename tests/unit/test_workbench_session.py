"""T1.2 tests for the workbench `Session` model.

The mismatch path needs no ROM: a bogus file whose bytes match no profile must
raise a typed, catchable error rather than crash. The happy path is ROM-gated
with the same convention the integration suite uses, and additionally skips if
the assembled atlas artifact is absent, since `open_rom` reads it.
"""

from __future__ import annotations

import glob
import hashlib
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
