"""ROM-gated proofs: an authored raw byte reaches the emitted image. LOG1-RAW-WRITE-BUILD-001.

The one claim this ticket exists to make good, and the one that cannot be
demonstrated on synthetic data:

    an accepted raw edit appears in the emitted image at exactly the intended
    offsets, the manifest names it, and a build that cannot place it refuses
    instead of emitting the canonical bytes and reporting success.

The raw document is written with the APPLICATION's own writer
(`tools.dragonbyte.rawbytes`) rather than with a fixture string, so this file
also proves the two halves meet: what the product saves is what the SDK build
applies.

These skip cleanly when the canonical ROM is absent. The canonical image is
opened read-only, its digest is asserted unchanged before and after, and no
ROM-derived fixture is committed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.rom_support import (
    CANONICAL_ROM_SHA256,
    assert_canonical_unchanged,
    assert_distinct_file_identity,
    canonical_rom_bytes,
    canonical_rom_path,
)
from tools.dragonbyte.rawbytes import RawEdits, write_raw_document
from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import ProjectValidationError
from tools.webfoot.write import ByteChange, OverlappingChangeError

CANONICAL_SHA256 = CANONICAL_ROM_SHA256

#: A four-byte run of zeroes past the stat tables, in the same unowned region the
#: S3 review measured its raw write in. The test asserts the whole image differs
#: from the canonical one at these offsets alone, so nothing has to be trusted
#: about the region being unowned.
RAW_OFFSET = 0x40083C
RAW_NEW = b"\xAA\xBB"
CANONICAL_AT_RAW_OFFSET = b"\x00\x00"

#: P-010 runtime capture, the offset `test_project_build_rom` also uses: the wolf's
#: HP byte, which a stat record owns and a semantic edit writes.
WOLF_TYPE_ID = 434
WOLF_RECORD_OFFSET = 0x00711BDC
WOLF_HP_BYTE_OFFSET = WOLF_RECORD_OFFSET + 0x04
WOLF_HP = 175


def _rom_path() -> str:
    """The canonical ROM this suite may READ, by exact name.

    A glob over `roms/*Buu*.gba` matches eight files in the local working
    directory, the randomized derivatives included, and half of them carry a
    valid checksum of their own - so the file this suite is written against is
    named rather than searched for, and a local copy that is not canonical is
    skipped rather than tested against. `tests/rom_support` owns the name; every
    WRITE in this file goes to a private copy instead.
    """
    path = canonical_rom_path()
    if path is None:
        pytest.skip("canonical Buu's Fury ROM not present locally")
    if hashlib.sha256(path.read_bytes()).hexdigest() != CANONICAL_SHA256:
        pytest.skip("local ROM is not the canonical profile these offsets target")
    return str(path)


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


@pytest.fixture
def project(tmp_path: Path, mutable_rom: Path, catalog: RomProfileCatalog) -> Path:
    """A private project extracted without graphics, as the sibling build proof does.

    Nothing here asserts anything about sprite assets and a graphics extraction
    writes 7,390 PNGs against a few dozen TOML files.
    """
    directory = tmp_path / "project"
    extract_project(str(mutable_rom), directory, catalog, graphics=False)
    return directory


def _author_raw(project: Path, offset: int, new: bytes) -> None:
    """Write the raw document the way the application writes it."""
    path = project / "raw" / "bytes.toml"
    existing = {}
    if path.exists():
        from tools.dragonbyte.rawbytes import read_raw_document

        existing = dict(read_raw_document(path).bytes_by_offset)
    existing[offset] = new
    write_raw_document(project, RawEdits(bytes_by_offset=existing))


def _build(project: Path, rom: str, catalog: RomProfileCatalog, output: Path):
    return build_project(project, rom, output, catalog)


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


# --- the positive round trip --------------------------------------------------


def test_an_authored_raw_byte_reaches_the_emitted_image_at_its_offsets(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    """The whole claim: the write is in the image, at exactly its offsets."""
    _author_raw(project, RAW_OFFSET, RAW_NEW)

    output = tmp_path / "out.gba"
    result = _build(project, str(mutable_rom), catalog, output)

    canonical = canonical_rom_bytes()
    emitted = output.read_bytes()

    assert emitted[RAW_OFFSET : RAW_OFFSET + len(RAW_NEW)] == RAW_NEW
    assert canonical[RAW_OFFSET : RAW_OFFSET + len(RAW_NEW)] == CANONICAL_AT_RAW_OFFSET
    # Exactly the intended offsets: every other byte of the 8 MiB image is
    # canonical, and this project authors nothing else.
    differing = [
        index
        for index, (before, after) in enumerate(zip(canonical, emitted))
        if before != after
    ]
    assert differing == list(range(RAW_OFFSET, RAW_OFFSET + len(RAW_NEW)))
    assert result.manifest.output_sha256 == hashlib.sha256(emitted).hexdigest()
    assert_canonical_unchanged()


def test_the_manifest_names_the_raw_edit_and_its_offset(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    _author_raw(project, RAW_OFFSET, RAW_NEW)

    output = tmp_path / "out.gba"
    result = _build(project, str(mutable_rom), catalog, output)

    document = result.manifest.to_json()
    (change,) = document["changes"]
    assert change["offset"] == RAW_OFFSET
    assert change["offset_hex"] == f"0x{RAW_OFFSET:08X}"
    assert change["old"] == CANONICAL_AT_RAW_OFFSET.hex()
    assert change["new"] == RAW_NEW.hex()
    assert change["owner"] == f"raw:0x{0x08000000 + RAW_OFFSET:08X}"
    assert document["changed_byte_count"] == len(RAW_NEW)

    published = result.manifest_path.read_text(encoding="utf-8")
    assert f'"offset": {RAW_OFFSET}' in published
    assert_canonical_unchanged()


def test_a_raw_edit_and_a_semantic_edit_share_one_plan(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    """A mixed project emits both edits and names both owners in one manifest."""
    _set_wolf_hp(project, WOLF_HP + 1)
    _author_raw(project, RAW_OFFSET, RAW_NEW)

    output = tmp_path / "out.gba"
    result = _build(project, str(mutable_rom), catalog, output)
    emitted = output.read_bytes()

    assert emitted[WOLF_HP_BYTE_OFFSET] == WOLF_HP + 1
    assert emitted[RAW_OFFSET : RAW_OFFSET + len(RAW_NEW)] == RAW_NEW
    owners = {change["owner"] for change in result.manifest.to_json()["changes"]}
    assert owners == {"enemy:434", f"raw:0x{0x08000000 + RAW_OFFSET:08X}"}
    assert_canonical_unchanged()


# --- the negative cases -------------------------------------------------------


def test_a_raw_write_outside_the_image_is_refused_before_any_output(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    image_size = mutable_rom.stat().st_size
    _author_raw(project, image_size - 1, b"\xAA\xBB")
    output = tmp_path / "out.gba"

    with pytest.raises(ProjectValidationError, match="is not inside the"):
        _build(project, str(mutable_rom), catalog, output)

    assert not output.exists()
    assert_canonical_unchanged()


def test_a_raw_write_over_a_semantic_edit_is_refused_by_the_one_plan(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    """A conflict is the plan's own overlap rule, not a second arbiter."""
    _set_wolf_hp(project, WOLF_HP + 1)
    # The whole three-byte HP field, which the stat record's own change writes.
    _author_raw(project, WOLF_HP_BYTE_OFFSET, b"\x01\x02\x03")
    output = tmp_path / "out.gba"

    with pytest.raises(OverlappingChangeError, match="would write the same bytes"):
        _build(project, str(mutable_rom), catalog, output)

    assert not output.exists()
    assert_canonical_unchanged()


def test_a_base_that_changes_between_plan_and_emit_is_refused(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog,
    monkeypatch: pytest.MonkeyPatch,
):
    """The canonical before bytes are verified at emission, not only at planning.

    A raw change is computed against the bytes the canonical image holds, so the
    document cannot carry a wrong `before` into the plan. What can still go wrong
    is the image itself moving between the read the plan was computed from and the
    read the image is emitted from, and `emit_image` re-verifies every change
    against the bytes it actually materializes.

    Driven with the SAME absolute path across both reads - the real emitter
    re-verifies `plan.base_sha256` and each change's bytes against whatever that
    path holds - so a private copy of the image stands in for it. The copy's file
    identity is asserted distinct from every protected input before it is written,
    which is the check that would have caught the incident at its first line.
    """
    import hashlib as _hashlib

    from tools.webfoot import build as build_module
    from tools.webfoot.write import ChangeValidationError

    _author_raw(project, RAW_OFFSET, RAW_NEW)

    private_rom = tmp_path / "private-base.gba"
    private_rom.write_bytes(canonical_rom_bytes())
    assert_distinct_file_identity(private_rom)
    canonical_digest = _hashlib.sha256(private_rom.read_bytes()).hexdigest()

    real_emit = build_module.emit_image

    def emit_a_moved_image(base_path, output_path, plan, **kwargs):
        # The write lands at the raw offset before the emitter reads the image, so
        # the bytes the raw change expects are no longer there.
        moved = bytearray(private_rom.read_bytes())
        moved[RAW_OFFSET : RAW_OFFSET + len(RAW_NEW)] = b"\x11\x22"
        private_rom.write_bytes(bytes(moved))
        return real_emit(base_path, output_path, plan, **kwargs)

    monkeypatch.setattr(build_module, "emit_image", emit_a_moved_image)
    output = tmp_path / "out.gba"

    with pytest.raises(ChangeValidationError):
        _build(project, str(private_rom), catalog, output)

    assert not output.exists()
    assert private_rom.read_bytes()[RAW_OFFSET : RAW_OFFSET + 2] == b"\x11\x22"
    # The stand-in was a canonical image when it was planned against, and no
    # protected repository input was the file that moved.
    assert canonical_digest == CANONICAL_SHA256
    assert _hashlib.sha256(mutable_rom.read_bytes()).hexdigest() == CANONICAL_SHA256
    assert_canonical_unchanged()


def test_a_stale_raw_write_is_refused_rather_than_applied(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    """A change whose `before` is not what the image holds is refused by the plan.

    The offset is the same and the authored value is the same; only the bytes the
    change claims to replace differ, which is the case a stored `before` would
    have hidden. The document has no `before` field to disagree with, so this
    drives the refusal the build depends on: `plan_changes` compares the change
    with the image it is actually applied to and refuses rather than writing over
    bytes it never read.
    """
    from tools.webfoot.project import raw_byte_changes, read_raw_bytes
    from tools.webfoot.write import ChangeValidationError, plan_changes

    _author_raw(project, RAW_OFFSET, RAW_NEW)
    image = canonical_rom_bytes()
    assert image[RAW_OFFSET : RAW_OFFSET + len(RAW_NEW)] == CANONICAL_AT_RAW_OFFSET

    (change,) = raw_byte_changes(read_raw_bytes(project), image)
    claimed = ByteChange(
        offset=change.offset,
        old=b"\x01\x02",
        new=change.new,
        owner=change.owner,
        reason=change.reason,
    )

    with pytest.raises(ChangeValidationError, match="this plan was computed against"):
        plan_changes(
            image,
            [claimed],
            profile_id="buus_fury_usa_rev0_01c1707f",
            base_sha256=hashlib.sha256(image).hexdigest(),
        )


# --- validation, determinism and the canonical digest -------------------------
#
# Every test below ends with `assert_canonical_unchanged()`: the DETECTIVE half of
# the safety pair. The preventive half is `assert_distinct_file_identity`, run on
# every fixture this file mutates.


def test_validate_reports_the_raw_problem_and_writes_nothing(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    image_size = mutable_rom.stat().st_size
    _author_raw(project, image_size - 1, b"\xAA\xBB")

    report = validate_project(project, str(mutable_rom), catalog)

    assert not report.passed
    assert any("authored raw bytes" in problem for problem in report.problems)
    assert_canonical_unchanged()


def test_a_raw_build_is_deterministic_and_leaves_the_canonical_rom_untouched(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    before = hashlib.sha256(mutable_rom.read_bytes()).hexdigest()
    _author_raw(project, RAW_OFFSET, RAW_NEW)

    first = tmp_path / "first.gba"
    second = tmp_path / "second.gba"
    _build(project, str(mutable_rom), catalog, first)
    _build(project, str(mutable_rom), catalog, second)

    assert first.read_bytes() == second.read_bytes()
    assert hashlib.sha256(mutable_rom.read_bytes()).hexdigest() == before == CANONICAL_SHA256
    assert_canonical_unchanged()


def test_a_write_equal_to_the_canonical_bytes_is_reported_as_no_change(
    tmp_path: Path, project: Path, mutable_rom: Path, catalog: RomProfileCatalog
):
    """An authored write that changes nothing is not an edit, and says so."""
    _author_raw(project, RAW_OFFSET, CANONICAL_AT_RAW_OFFSET)

    output = tmp_path / "out.gba"
    result = _build(project, str(mutable_rom), catalog, output)

    assert result.manifest.to_json()["changes"] == []
    assert output.read_bytes() == canonical_rom_bytes()
    assert_canonical_unchanged()
