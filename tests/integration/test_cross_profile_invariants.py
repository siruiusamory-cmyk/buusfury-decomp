"""TOOLKIT-005 invariants that must hold for every profile, run against each.

These are parameterized rather than duplicated because the property under test
is genuinely shared: whatever a profile declares, extraction must be
deterministic, an unchanged rebuild must reproduce the whole image, a build must
never touch the base, and a project must refuse the wrong ROM. Nothing here
knows which game it is running against - the parameter is a profile id and a
glob, and everything else comes from the catalog.

Game-specific format facts are *not* here. Those live in
`tests/integration/test_text_rom.py` (Buu's Fury) and
`tests/integration/test_logii_text_rom.py` (Legacy of Goku II), because a shared
test that had to branch per game would be the same coupling this ticket removed
from the toolkit, relocated into the suite.
"""

from __future__ import annotations

import glob
import hashlib
import os

import pytest

from tools.webfoot import capability
from tools.webfoot.build import (
    ProjectRomMismatchError,
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.profile import RomProfileCatalog, VerificationStatus
from tools.webfoot.project import read_project
from tools.webfoot.rom import identify_rom


#: (profile id, glob for the local image, canonical sha256).
PROFILES = [
    pytest.param(
        "buus_fury_usa_rev0_01c1707f",
        "*Buu*.gba",
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e",
        id="buus_fury",
    ),
    pytest.param(
        "legacy_of_goku_ii_usa_rev0_204142e1",
        "*Legacy of Goku II*.gba",
        "6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75",
        id="legacy_of_goku_ii",
    ),
]


def _rom(pattern: str, expected_sha256: str) -> str:
    matches = glob.glob(os.path.join("roms", pattern))
    if not matches:
        pytest.skip(f"canonical ROM matching {pattern!r} not present locally")
    if hashlib.sha256(open(matches[0], "rb").read()).hexdigest() != expected_sha256:
        pytest.skip(f"local ROM matching {pattern!r} is not the canonical image")
    return matches[0]


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


# --- identity ------------------------------------------------------------


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_each_canonical_rom_verifies_as_exactly_its_own_profile(
    profile_id, pattern, sha256, catalog
):
    identification = identify_rom(_rom(pattern, sha256), catalog)

    assert identification.profile_match.status is VerificationStatus.VERIFIED
    assert identification.profile_match.profile is not None
    assert identification.profile_match.profile.id == profile_id
    assert identification.hashes.sha256 == sha256


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_a_single_flipped_byte_breaks_verification(
    profile_id, pattern, sha256, catalog, tmp_path
):
    """Fail-closed identity, asserted per profile rather than once for one game."""
    data = bytearray(open(_rom(pattern, sha256), "rb").read())
    data[0x00100000] ^= 0xFF
    impostor = tmp_path / "impostor.gba"
    impostor.write_bytes(bytes(data))

    match = identify_rom(impostor, catalog).profile_match
    assert match.status is VerificationStatus.UNKNOWN
    assert match.profile is None


# --- declared capabilities gate what is extracted ------------------------


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_extraction_writes_exactly_the_declared_subsystems(
    profile_id, pattern, sha256, catalog, tmp_path
):
    """One project layout serves both games; content follows the declaration."""
    rom = _rom(pattern, sha256)
    extract_project(rom, tmp_path, catalog, graphics=False)
    profile = next(p for p in catalog.profiles if p.id == profile_id)
    declared = set(capability.capabilities(profile))

    assert (tmp_path / "project.toml").is_file()
    assert (tmp_path / "enemies" / "enemies.toml").is_file() is (
        capability.Capability.ENEMY_STATS in declared
    )
    assert (tmp_path / "characters" / "characters.toml").is_file() is (
        capability.Capability.CHARACTER_BASE_STATS in declared
    )
    assert (tmp_path / "text" / "strings.toml").is_file() is (
        capability.Capability.TEXT_STRINGS in declared
    )


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_the_project_pins_its_base_by_hash_and_holds_no_rom_copy(
    profile_id, pattern, sha256, catalog, tmp_path
):
    rom = _rom(pattern, sha256)
    extract_project(rom, tmp_path, catalog, graphics=False)
    project = read_project(tmp_path)

    assert project.meta.profile_id == profile_id
    assert project.meta.base_rom_sha256 == sha256
    assert project.meta.base_rom_size == os.path.getsize(rom)
    assert not list(tmp_path.rglob("*.gba"))


# --- determinism ---------------------------------------------------------


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_extraction_is_deterministic(profile_id, pattern, sha256, catalog, tmp_path):
    rom = _rom(pattern, sha256)
    first, second = tmp_path / "a", tmp_path / "b"
    extract_project(rom, first, catalog, graphics=False)
    extract_project(rom, second, catalog, graphics=False)

    produced = sorted(p.relative_to(first) for p in first.rglob("*.toml"))
    assert produced
    for relative in produced:
        assert (first / relative).read_bytes() == (second / relative).read_bytes()


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_an_extracted_project_validates_cleanly(
    profile_id, pattern, sha256, catalog, tmp_path
):
    rom = _rom(pattern, sha256)
    extract_project(rom, tmp_path, catalog, graphics=False)

    report = validate_project(tmp_path, rom, catalog)
    assert report.problems == ()
    assert report.passed
    assert report.profile_id == profile_id


# --- the whole-ROM no-op rebuild -----------------------------------------


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_an_unchanged_project_rebuilds_the_whole_rom_byte_for_byte(
    profile_id, pattern, sha256, catalog, tmp_path
):
    """The strongest shared proof: every byte, including undecoded regions."""
    rom = _rom(pattern, sha256)
    project, output = tmp_path / "project", tmp_path / "out.gba"
    extract_project(rom, project, catalog, graphics=False)

    build_project(project, rom, output, catalog)

    assert output.read_bytes() == open(rom, "rb").read()
    assert hashlib.sha256(output.read_bytes()).hexdigest() == sha256


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_repeated_no_op_builds_are_byte_identical(
    profile_id, pattern, sha256, catalog, tmp_path
):
    rom = _rom(pattern, sha256)
    project = tmp_path / "project"
    extract_project(rom, project, catalog, graphics=False)

    first, second = tmp_path / "one.gba", tmp_path / "two.gba"
    build_project(project, rom, first, catalog)
    build_project(project, rom, second, catalog)

    assert first.read_bytes() == second.read_bytes()


# --- the base image is never written -------------------------------------


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_the_canonical_rom_is_never_modified(
    profile_id, pattern, sha256, catalog, tmp_path
):
    rom = _rom(pattern, sha256)
    before_mtime = os.stat(rom).st_mtime_ns

    project = tmp_path / "project"
    extract_project(rom, project, catalog, graphics=False)
    build_project(project, rom, tmp_path / "out.gba", catalog)

    assert hashlib.sha256(open(rom, "rb").read()).hexdigest() == sha256
    assert os.stat(rom).st_mtime_ns == before_mtime


@pytest.mark.parametrize("profile_id,pattern,sha256", PROFILES)
def test_a_build_refuses_to_overwrite_the_base_rom(
    profile_id, pattern, sha256, catalog, tmp_path
):
    from tools.webfoot.write import WriteError

    rom = _rom(pattern, sha256)
    project = tmp_path / "project"
    extract_project(rom, project, catalog, graphics=False)

    with pytest.raises(WriteError, match="over the input image"):
        build_project(project, rom, rom, catalog)
    assert hashlib.sha256(open(rom, "rb").read()).hexdigest() == sha256


# --- cross-game confusion is refused -------------------------------------


def test_a_project_cannot_be_built_against_the_other_games_rom(catalog, tmp_path):
    """The fail-closed rule the project format exists to enforce.

    A project pins one base image by SHA-256. Applying a Legacy of Goku II
    project to a Buu's Fury image would write LOGII offsets into bytes that mean
    something else entirely, so it must be refused before anything is emitted.
    """
    buu = _rom("*Buu*.gba", PROFILES[0].values[2])
    logii = _rom("*Legacy of Goku II*.gba", PROFILES[1].values[2])

    project = tmp_path / "project"
    output = tmp_path / "out.gba"
    extract_project(logii, project, catalog, graphics=False)

    with pytest.raises(ProjectRomMismatchError):
        build_project(project, buu, output, catalog)
    assert not output.exists()

    report = validate_project(project, buu, catalog)
    assert not report.passed
    assert any("mismatch" in problem for problem in report.problems)


def test_the_two_profiles_do_not_share_an_identity(catalog):
    """Distinct games must never collapse onto one profile."""
    ids = {param.values[0] for param in PROFILES}
    profiles = [p for p in catalog.profiles if p.id in ids]
    assert len(profiles) == len(ids)

    assert len({p.sha256 for p in profiles}) == len(profiles)
    assert len({p.game_code for p in profiles}) == len(profiles)
    assert len({p.game for p in profiles}) == len(profiles)
