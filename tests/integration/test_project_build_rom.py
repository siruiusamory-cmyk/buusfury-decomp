"""ROM-gated proofs for the TOOLKIT-002 project/build model.

The central claim of this ticket, and the one that cannot be demonstrated on
synthetic data:

    canonical ROM -> extract -> build unchanged -> output == canonical, byte
    for byte, across the WHOLE 8 MiB image.

That is strictly stronger than the TOOLKIT-001 stat-table-local round trip: it
proves the project format loses nothing, including the bytes this project has
not decoded, and that the build path reproduces everything it did not touch.

These skip cleanly when the canonical ROM is absent so the portable suite stays
runnable without proprietary data. The ROM is opened read-only and verified
unchanged afterwards; no ROM-derived fixture is committed.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
from pathlib import Path

import pytest

from tools.webfoot.authored_image import manifest_path_for
from tools.webfoot.build import (
    BuildError,
    ProjectRomMismatchError,
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import ProjectValidationError, read_project
from tools.webfoot.write import WriteError

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: P-010 runtime capture. HP 175 is unique across the enemy table, which is
#: what makes it a legitimate way to name the wolf without hardcoding a slot.
WOLF_TYPE_ID = 434
WOLF_HP = 175
WOLF_NEW_HP = 200
WOLF_RECORD_OFFSET = 0x00711BDC
#: HP sits at record +0x04, so 175 -> 200 touches only the low byte of that u24.
WOLF_HP_BYTE_OFFSET = WOLF_RECORD_OFFSET + 0x04


def _rom_path() -> str:
    matches = glob.glob(os.path.join("roms", "*Buu*.gba"))
    if not matches:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(open(matches[0], "rb").read()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return matches[0]


@pytest.fixture
def rom() -> str:
    return _rom_path()


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture
def project(tmp_path: Path, rom: str, catalog: RomProfileCatalog) -> Path:
    """A private, writable project. Extracted WITHOUT graphics, deliberately.

    Nothing in this file asserts anything about sprite assets - these tests are
    about project identity, stat records, validation and the whole-ROM build -
    and graphics extraction writes 7,390 indexed PNGs against this project's few
    dozen TOML files. Measured on the canonical image: 44.0s with graphics
    against 1.8s without, and this fixture runs for 18 tests.

    Skipping them costs nothing here that matters. A build from such a project
    is still byte-identical to the canonical ROM, because unchanged graphics are
    re-emitted from the base image rather than from the project - verified, not
    assumed. The graphics representation itself is proven in
    `test_graphics_rom.py`, which extracts them in full.

    Per-test rather than shared, because half of these tests edit the project
    and a shared directory would leak that state between them.
    """
    directory = tmp_path / "project"
    extract_project(rom, directory, catalog, graphics=False)
    return directory


def _set_wolf_hp(project: Path, value: int) -> None:
    """Edit the wolf's HP in PROJECT SOURCE, the way a person would."""
    path = project / "enemies" / "enemies.toml"
    text = path.read_text(encoding="utf-8")
    marker = f"[enemy.{WOLF_TYPE_ID}]"
    start = text.index(marker)
    field = text.index(f"\nhp = {WOLF_HP}\n", start)
    path.write_text(
        text[: field + 1] + f"hp = {value}\n" + text[field + len(f"\nhp = {WOLF_HP}\n"):],
        encoding="utf-8",
        newline="\n",
    )


# --- exit criteria 1, 2, 3: extraction -----------------------------------


def test_extraction_produces_a_deterministic_project(
    tmp_path: Path, rom: str, catalog: RomProfileCatalog
):
    """Same ROM, two extractions, identical authored bytes.

    Nondeterminism here would poison everything downstream: a project whose
    files differ run to run cannot have a reproducible build, and every diff
    would be noise.
    """
    first = extract_project(rom, tmp_path / "a", catalog)
    second = extract_project(rom, tmp_path / "b", catalog)

    assert [p.name for p in first] == [p.name for p in second]
    for left, right in zip(first, second):
        assert left.read_bytes() == right.read_bytes(), left.name


def test_an_empty_destination_is_extracted_into(
    tmp_path: Path, rom: str, catalog: RomProfileCatalog
):
    """A destination that already exists and is empty is a normal target.

    The Workbench directory picker only returns directories that exist, so this
    is its everyday path; the guard must refuse only an occupied one.
    """
    destination = tmp_path / "empty"
    destination.mkdir()

    extract_project(rom, destination, catalog, graphics=False)

    assert (destination / "project.toml").is_file()


def test_re_extraction_refuses_an_authored_project_and_destroys_nothing(
    project: Path, rom: str, catalog: RomProfileCatalog
):
    """N-03: a second extraction over authored work is refused, not applied.

    Before the guard this rewrote enemies.toml from the image, so the edit below
    was gone. The refusal precedes the first write, and a call that never reached
    the image leaves the canonical ROM byte-identical.
    """
    _set_wolf_hp(project, WOLF_NEW_HP)
    authored = (project / "enemies" / "enemies.toml").read_bytes()
    rom_before = hashlib.sha256(Path(rom).read_bytes()).hexdigest()

    with pytest.raises(BuildError, match="is not empty"):
        extract_project(rom, project, catalog, graphics=False)

    assert (project / "enemies" / "enemies.toml").read_bytes() == authored
    assert b"hp = 200" in authored
    assert hashlib.sha256(Path(rom).read_bytes()).hexdigest() == rom_before
    assert rom_before == CANONICAL_SHA256


def test_project_pins_the_correct_profile_and_base_identity(project: Path):
    meta = read_project(project).meta
    assert meta.profile_id == "buus_fury_usa_rev0_01c1707f"
    assert meta.base_rom_sha256 == CANONICAL_SHA256
    assert meta.base_rom_size == 8388608


def test_project_holds_every_stat_record(project: Path):
    loaded = read_project(project)
    assert len(loaded.enemies) == 141
    assert len(loaded.characters) == 9


def test_project_does_not_contain_a_copy_of_the_rom(project: Path):
    """A project is source, not a redistribution of the game."""
    for path in project.rglob("*"):
        if path.is_file():
            assert path.stat().st_size < 1_000_000, path
            assert path.suffix != ".gba", path


def test_authored_source_carries_semantic_values_not_addresses(project: Path):
    text = (project / "enemies" / "enemies.toml").read_text(encoding="utf-8")
    assert f"hp = {WOLF_HP}" in text
    # The ROM offset of the wolf record must not appear as an authored key.
    assert f"{WOLF_RECORD_OFFSET:08x}" not in text.lower()
    assert "0x08" not in text


def test_valid_project_passes_validation(
    project: Path, rom: str, catalog: RomProfileCatalog
):
    report = validate_project(project, rom, catalog)
    assert report.passed, report.problems
    assert report.enemy_count == 141
    assert report.character_count == 9


# --- exit criterion 4: the central whole-ROM round trip ------------------


def test_unchanged_project_rebuilds_the_entire_rom_byte_identically(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    """THE central success condition of TOOLKIT-002.

    Not a table-local comparison: every one of the 8388608 bytes, including
    every span this project has never decoded.
    """
    output = tmp_path / "noop.gba"
    result = build_project(project, rom, output, catalog)

    base_bytes = Path(rom).read_bytes()
    output_bytes = output.read_bytes()

    assert output_bytes == base_bytes
    assert hashlib.sha256(output_bytes).hexdigest() == CANONICAL_SHA256
    assert result.manifest.output_sha256 == CANONICAL_SHA256
    assert result.manifest.changes == ()


# --- CQA-12: provenance is published by default ---------------------------


def test_a_default_build_publishes_its_manifest_beside_the_output(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    """The allocation-critical slice of CQA-12, on the real build path.

    A normal `build_project` call - no manifest argument, exactly what the
    Workbench Build tab makes - must leave a provenance document beside the image
    it describes, and that document must be the one for THIS output. The CLI and
    GUI used to pass no path and get no manifest, so an 8 MiB derivative carried
    its provenance only in memory.
    """
    output = tmp_path / "default.gba"
    result = build_project(project, rom, output, catalog)

    sibling = manifest_path_for(output)
    assert sibling.name == output.name + ".dragonbyte.json"
    assert sibling.is_file()
    assert result.manifest_path == sibling

    document = json.loads(sibling.read_text(encoding="utf-8"))
    assert document["output"]["sha256"] == result.manifest.output_sha256
    assert document["output"]["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert document["base"]["sha256"] == CANONICAL_SHA256

    # The same build with publication explicitly disabled writes no document, and
    # that is the ONLY way to get no document.
    silent = tmp_path / "silent.gba"
    silent_result = build_project(project, rom, silent, catalog, manifest_path=None)
    assert silent_result.manifest_path is None
    assert not manifest_path_for(silent).exists()
    # The image is identical either way: provenance never changes the bytes.
    assert silent.read_bytes() == output.read_bytes()


def test_a_default_build_refuses_to_clobber_an_existing_manifest(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    """Publication is fail-closed, exactly as the output image is.

    A build that silently replaced a previous derivative's provenance would make
    "which run produced this manifest" unanswerable, and a manifest for one image
    sitting beside another is worse than no manifest. The refusal must also land
    BEFORE anything is published, so no image is left behind.
    """
    output = tmp_path / "fresh.gba"
    sibling = manifest_path_for(output)
    sibling.write_text("{}", encoding="utf-8")

    with pytest.raises(WriteError, match="refusing to overwrite an existing manifest"):
        build_project(project, rom, output, catalog)

    assert sibling.read_text(encoding="utf-8") == "{}"
    assert not output.exists(), "a refused manifest must not leave an image behind"


# --- exit criteria 6, 7, 8: the edit proof -------------------------------


def test_project_edit_changes_only_the_expected_byte(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    """Edit HP in project source; exactly one ROM byte moves, attributed."""
    _set_wolf_hp(project, WOLF_NEW_HP)
    output = tmp_path / "edited.gba"
    manifest_path = tmp_path / "edited.json"

    result = build_project(
        project, rom, output, catalog, manifest_path=manifest_path
    )

    base_bytes = Path(rom).read_bytes()
    output_bytes = output.read_bytes()
    differing = [
        index
        for index, (a, b) in enumerate(zip(base_bytes, output_bytes))
        if a != b
    ]

    assert differing == [WOLF_HP_BYTE_OFFSET]
    assert base_bytes[WOLF_HP_BYTE_OFFSET] == WOLF_HP
    assert output_bytes[WOLF_HP_BYTE_OFFSET] == WOLF_NEW_HP
    assert len(output_bytes) == len(base_bytes)

    # Provenance names the semantic edit, not merely the bytes.
    changes = result.manifest.changes_for(f"enemy:{WOLF_TYPE_ID}")
    assert len(changes) == 1
    assert changes[0].offset == WOLF_RECORD_OFFSET
    assert "hp" in changes[0].reason

    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert document["base"]["sha256"] == CANONICAL_SHA256
    assert document["output"]["sha256"] == result.manifest.output_sha256
    assert document["changed_byte_count"] == 1
    assert document["project"]["format_version"] == 1


def test_edited_project_reports_the_new_value_on_reload(project: Path):
    _set_wolf_hp(project, WOLF_NEW_HP)
    from tools.webfoot.formats.stat_tables import StatIdentity

    loaded = read_project(project)
    identity = StatIdentity(kind="enemy", key=WOLF_TYPE_ID)
    assert loaded.enemies[identity]["hp"] == WOLF_NEW_HP


# --- exit criterion 5: repeated builds -----------------------------------


def test_repeated_builds_of_a_modified_project_are_byte_identical(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    _set_wolf_hp(project, WOLF_NEW_HP)

    first = tmp_path / "a.gba"
    second = tmp_path / "b.gba"
    first_manifest = tmp_path / "a.json"
    second_manifest = tmp_path / "b.json"

    build_project(project, rom, first, catalog, manifest_path=first_manifest)
    build_project(project, rom, second, catalog, manifest_path=second_manifest)

    assert first.read_bytes() == second.read_bytes()
    assert (
        hashlib.sha256(first.read_bytes()).hexdigest()
        == hashlib.sha256(second.read_bytes()).hexdigest()
    )
    # The manifest is a build artefact too, and carries no timestamp or path.
    assert first_manifest.read_bytes() == second_manifest.read_bytes()


def test_build_manifest_contains_no_nondeterministic_metadata(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    manifest_path = tmp_path / "m.json"
    build_project(project, rom, tmp_path / "o.gba", catalog, manifest_path=manifest_path)
    text = manifest_path.read_text(encoding="utf-8").lower()

    for forbidden in ("timestamp", "generated_at", "hostname", "user", "tmp"):
        assert forbidden not in text, forbidden
    # No absolute path from this machine may leak into a build artefact.
    assert str(tmp_path).lower().replace("\\", "/") not in text.replace("\\\\", "/")


# --- exit criteria 9, 10: fail closed ------------------------------------


def test_build_against_the_wrong_rom_is_refused(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    """A project pins one base image; anything else must fail closed."""
    path = project / "project.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(CANONICAL_SHA256, "a" * 64),
        encoding="utf-8",
        newline="\n",
    )

    output = tmp_path / "wrong.gba"
    with pytest.raises(ProjectRomMismatchError, match="base ROM mismatch"):
        build_project(project, rom, output, catalog)
    assert not output.exists(), "a refused build must leave no output behind"


def test_wrong_rom_fails_validation_without_writing(
    project: Path, rom: str, catalog: RomProfileCatalog
):
    path = project / "project.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(CANONICAL_SHA256, "b" * 64),
        encoding="utf-8",
        newline="\n",
    )
    report = validate_project(project, rom, catalog)
    assert not report.passed
    assert any("base ROM mismatch" in problem for problem in report.problems)


def test_unsupported_profile_is_refused(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    """A project naming a profile this toolkit does not support cannot build."""
    path = project / "project.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "buus_fury_usa_rev0_01c1707f", "legacy_of_goku_usa_a3c8c767"
        ),
        encoding="utf-8",
        newline="\n",
    )
    output = tmp_path / "profile.gba"
    with pytest.raises(ProjectRomMismatchError, match="profile mismatch"):
        build_project(project, rom, output, catalog)
    assert not output.exists()


def test_semantic_validation_failure_happens_before_any_write(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    """An out-of-range value is refused, and no output file is created.

    Level is capped at 200 because P-010 read `cmp r6,#0xc8` at 0x08013A00 in
    the EXP award path - the game itself treats 200 as the ceiling.
    """
    path = project / "enemies" / "enemies.toml"
    text = path.read_text(encoding="utf-8")
    start = text.index(f"[enemy.{WOLF_TYPE_ID}]")
    field = text.index("\nlevel = ", start)
    end = text.index("\n", field + 1)
    path.write_text(
        text[: field + 1] + "level = 250" + text[end:], encoding="utf-8", newline="\n"
    )

    output = tmp_path / "invalid.gba"
    with pytest.raises(ProjectValidationError, match="exceeds the maximum"):
        build_project(project, rom, output, catalog)
    assert not output.exists()


def test_missing_record_is_reported_rather_than_silently_defaulted(
    project: Path, rom: str, catalog: RomProfileCatalog
):
    path = project / "enemies" / "enemies.toml"
    text = path.read_text(encoding="utf-8")
    start = text.index(f"[enemy.{WOLF_TYPE_ID}]")
    end = text.index("[enemy.", start + 1)
    path.write_text(text[:start] + text[end:], encoding="utf-8", newline="\n")

    report = validate_project(project, rom, catalog)
    assert not report.passed
    assert any(
        f"enemy:{WOLF_TYPE_ID}" in problem and "missing" in problem
        for problem in report.problems
    )


def test_tampered_opaque_bytes_are_detected(
    project: Path, rom: str, catalog: RomProfileCatalog
):
    """`raw` must match the base image, or the record came from elsewhere."""
    path = project / "enemies" / "enemies.toml"
    text = path.read_text(encoding="utf-8")
    start = text.index(f"[enemy.{WOLF_TYPE_ID}]")
    field = text.index('\nraw = "', start)
    value_start = field + len('\nraw = "')
    value_end = text.index('"', value_start)
    original = text[value_start:value_end]
    tampered = ("ff" if original[:2] != "ff" else "00") + original[2:]
    path.write_text(
        text[:value_start] + tampered + text[value_end:],
        encoding="utf-8",
        newline="\n",
    )

    report = validate_project(project, rom, catalog)
    assert not report.passed
    assert any("raw bytes" in problem for problem in report.problems)


def test_build_refuses_to_overwrite_an_existing_output(
    tmp_path: Path, project: Path, rom: str, catalog: RomProfileCatalog
):
    output = tmp_path / "existing.gba"
    output.write_bytes(b"occupied")
    with pytest.raises(WriteError, match="refusing to overwrite"):
        build_project(project, rom, output, catalog)
    assert output.read_bytes() == b"occupied"


def test_build_refuses_to_write_over_the_base_rom(
    project: Path, rom: str, catalog: RomProfileCatalog
):
    with pytest.raises(WriteError, match="read-only"):
        build_project(project, rom, rom, catalog)


def test_cli_drives_the_same_lifecycle_as_the_api(tmp_path: Path, rom: str, capsys):
    """The CLI must call the project/build APIs, not reimplement them.

    Asserted by outcome rather than by inspection: driving the whole lifecycle
    through `main` has to produce the same byte-identical no-op ROM the API
    produces, which a second code path would not reliably do.
    """
    from tools.webfoot.cli import main

    directory = tmp_path / "cli-project"
    assert main(["extract", rom, str(directory)]) == 0
    assert main(["validate", str(directory), "--rom", rom]) == 0

    output = tmp_path / "cli.gba"
    assert main(["build", str(directory), "--rom", rom, "--output", str(output)]) == 0
    assert hashlib.sha256(output.read_bytes()).hexdigest() == CANONICAL_SHA256
    assert "RESULT:" in capsys.readouterr().out


def test_cli_build_against_a_wrong_rom_exits_nonzero(tmp_path: Path, rom: str, capsys):
    from tools.webfoot.cli import main

    directory = tmp_path / "cli-bad"
    assert main(["extract", rom, str(directory)]) == 0
    path = directory / "project.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(CANONICAL_SHA256, "c" * 64),
        encoding="utf-8",
        newline="\n",
    )

    output = tmp_path / "cli-bad.gba"
    assert main(["build", str(directory), "--rom", rom, "--output", str(output)]) == 2
    assert not output.exists()
    assert "error:" in capsys.readouterr().err


def test_canonical_rom_is_unchanged_by_the_whole_lifecycle(
    tmp_path: Path, rom: str, catalog: RomProfileCatalog
):
    """Extract, edit, build twice - the input ROM is untouched throughout."""
    before = hashlib.sha256(Path(rom).read_bytes()).hexdigest()
    before_stat = os.stat(rom)

    directory = tmp_path / "lifecycle"
    extract_project(rom, directory, catalog)
    _set_wolf_hp(directory, WOLF_NEW_HP)
    validate_project(directory, rom, catalog)
    build_project(directory, rom, tmp_path / "one.gba", catalog)
    build_project(directory, rom, tmp_path / "two.gba", catalog)

    after_stat = os.stat(rom)
    assert hashlib.sha256(Path(rom).read_bytes()).hexdigest() == before
    assert before == CANONICAL_SHA256
    assert before_stat.st_size == after_stat.st_size
    assert before_stat.st_mtime_ns == after_stat.st_mtime_ns
