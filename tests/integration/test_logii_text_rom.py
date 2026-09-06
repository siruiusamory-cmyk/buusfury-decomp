"""ROM-gated proofs for the TOOLKIT-005 Legacy of Goku II string subsystem.

These are the exit criteria that cannot be demonstrated on synthetic data: exact
ROM identification, the verified layout contract, the full 246-string extent
round trip, the canonical in-place edit with its exact byte diff, deterministic
extraction, and the whole-image no-op rebuild.

They skip cleanly when the canonical ROM is absent, so the portable suite stays
runnable without proprietary data. The ROM is opened read-only and is verified
unchanged afterwards; no ROM-derived fixture is committed.

The evidence behind every constant here is recorded in
`docs/research/LOGII_TEXT_FORMAT.md`.
"""

from __future__ import annotations

import glob
import hashlib
import os

import pytest

from tools.webfoot.build import build_project, extract_project, validate_project
from tools.webfoot.formats import ascii_text_tables as att
from tools.webfoot.formats.text_tables import TextIdentity
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import read_project
from tools.webfoot.stats import StatProfileError, load_stat_tables
from tools.webfoot.text import TextTooLongError, load_text_strings


PROFILE_ID = "legacy_of_goku_ii_usa_rev0_204142e1"
CANONICAL_SHA256 = (
    "6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75"
)
CANONICAL_SHA1 = "18e0715dec419f3501c301511530d2edcd590f8b"
CANONICAL_MD5 = "4e1565aa1f0627c2bf5e51019440cb70"
CANONICAL_SIZE = 8_388_608
GAME_CODE = "ALFE"

#: TOOLKIT-005 verified extents. Repeated here rather than imported so the test
#: fails if the profile's values drift, which is the point of a contract test.
TABLE_START = 0x000E2840
ENTRY_COUNT = 260
POOL_START = 0x000E2C50
POOL_END = 0x000E4090
POOL_SIZE = POOL_END - POOL_START
STRING_COUNT = 246

#: The edit target, located by content rather than by index so a re-verification
#: of the table base cannot silently retarget it. Its uniqueness is asserted.
EDIT_TEXT = "Yunzabit Heights"
EDIT_REPLACEMENT = "Yunzabit Wastes"
EDIT_TOO_LONG = "Yunzabit Highland"
EDIT_FIRST_BYTE = 0x000E4088
EDIT_LAST_BYTE = 0x000E408E


def _rom_path() -> str:
    matches = glob.glob(os.path.join("roms", "*Legacy of Goku II*.gba"))
    if not matches:
        pytest.skip("canonical Legacy of Goku II ROM not present locally")
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
def image(rom: str) -> bytes:
    with open(rom, "rb") as stream:
        return stream.read()


@pytest.fixture
def strings(rom: str, catalog: RomProfileCatalog):
    return load_text_strings(rom, catalog)


# --- exit criterion 1: exact ROM identification --------------------------


def test_the_local_rom_identifies_as_exactly_this_profile(rom, catalog):
    from tools.webfoot.rom import identify_rom
    from tools.webfoot.profile import VerificationStatus

    identification = identify_rom(rom, catalog)

    assert identification.profile_match.status is VerificationStatus.VERIFIED
    assert identification.profile_match.profile is not None
    assert identification.profile_match.profile.id == PROFILE_ID
    assert identification.size == CANONICAL_SIZE
    assert identification.hashes.sha256 == CANONICAL_SHA256
    assert identification.hashes.sha1 == CANONICAL_SHA1
    assert identification.hashes.md5 == CANONICAL_MD5
    assert identification.header.game_code == GAME_CODE
    assert identification.header.software_version == 0


def test_a_wrong_revision_is_rejected_before_any_semantic_access(rom, catalog, tmp_path):
    """One flipped byte must break identification, not merely change a checksum.

    Fail-closed identity is what stops the toolkit writing LOGII offsets into a
    ROM that is not this LOGII.
    """
    from tools.webfoot.rom import identify_rom
    from tools.webfoot.profile import VerificationStatus

    data = bytearray(open(rom, "rb").read())
    data[0x00200000] ^= 0xFF
    impostor = tmp_path / "impostor.gba"
    impostor.write_bytes(bytes(data))

    identification = identify_rom(impostor, catalog)
    assert identification.profile_match.status is VerificationStatus.UNKNOWN

    with pytest.raises(Exception) as error:
        load_text_strings(impostor, catalog)
    assert "verified" in str(error.value)


def test_the_buu_profile_is_not_accepted_for_this_rom(rom, catalog):
    """Cross-game confusion is refused: a LOGII image never matches Buu's Fury."""
    from tools.webfoot.rom import identify_rom

    profile = identify_rom(rom, catalog).profile_match.profile
    assert profile is not None
    assert profile.id != "buus_fury_usa_rev0_01c1707f"
    assert profile.game == "legacy_of_goku_ii"


# --- exit criterion 2: the verified layout contract ----------------------


def test_the_profile_declares_the_verified_string_layout(catalog):
    profile = next(p for p in catalog.profiles if p.id == PROFILE_ID)
    layout = profile.text_strings
    assert layout is not None

    assert layout.pointer_table_address.raw == TABLE_START + 0x08000000
    assert layout.count == ENTRY_COUNT
    assert layout.pool_address.raw == POOL_START + 0x08000000
    assert layout.pool_size == POOL_SIZE
    assert layout.encoding == "ascii_nul_terminated"
    assert layout.alignment == 1
    assert layout.relocatable is False
    assert layout.evidence


def test_no_free_space_is_declared_for_this_profile(catalog):
    """Free space is never inferred, so an undeclared profile declares none."""
    profile = next(p for p in catalog.profiles if p.id == PROFILE_ID)
    assert profile.free_regions == ()


def test_the_pointer_table_abuts_the_pool_with_no_bytes_between(image):
    """Both extents are measurements, so their boundary is checkable."""
    assert TABLE_START + ENTRY_COUNT * att.POINTER_SIZE == POOL_START


def test_the_table_base_is_not_preceded_by_another_pool_pointer(image):
    """The lower boundary is sharp: the run cannot start earlier than declared.

    This is the check whose absence produced a table base 43 entries too high on
    the first measurement; a forward-only scan cannot see its own start.
    """
    import struct

    word = struct.unpack("<I", image[TABLE_START - 4 : TABLE_START])[0]
    preceding = word - att.GBA_ROM_BASE
    assert not POOL_START <= preceding < POOL_END


# --- exit criterion 3: layout verification against the image -------------


def test_every_pointer_targets_a_string_start_inside_the_pool(image):
    starts = set()
    position = POOL_START
    while position < POOL_END:
        starts.add(position)
        _, position = att.decode_string(image, position)
    assert position == POOL_END

    targets = {
        att.read_pointer(image, TABLE_START, index) for index in range(ENTRY_COUNT)
    }
    assert targets <= starts
    assert len(starts) == STRING_COUNT


def test_the_table_aliases_so_pointers_are_neither_unique_nor_ascending(image):
    """The property that makes this table structurally unlike Buu's Fury's.

    Asserted rather than assumed, because the ASCII codec's enumeration strategy
    exists specifically to be correct in the presence of aliasing.
    """
    targets = [
        att.read_pointer(image, TABLE_START, index) for index in range(ENTRY_COUNT)
    ]

    assert len(targets) == ENTRY_COUNT
    assert len(set(targets)) == STRING_COUNT
    assert len(set(targets)) < len(targets)
    assert targets != sorted(targets) or len(set(targets)) != len(targets)


def test_the_pool_is_exhaustively_tiled(image):
    assert att.pool_is_exhaustively_tiled(image, POOL_START, POOL_END)


def test_the_pool_holds_only_printable_ascii_and_two_newlines(image):
    """The encoding claim, checked over the whole extent rather than a sample.

    Exactly two `0x0A` bytes exist and both sit inside the one label
    `No\\nPortrait\\nData`. That they are real newlines rather than control codes
    carrying operands is why this codec needs no control grammar at all - the
    contrast with Buu's Fury, whose pool has a `0x0008`-prefixed grammar.
    """
    blob = image[POOL_START:POOL_END]
    body = blob.replace(b"\x00", b"")
    assert all(0x20 <= byte < 0x7F or byte == 0x0A for byte in body)
    assert body.count(b"\n") == 2


# --- exit criterion 4: exhaustive round trip ------------------------------


def test_every_string_is_enumerated_with_a_table_identity(strings):
    entries = list(strings.entries())
    assert len(entries) == STRING_COUNT
    assert all(entry.location.index is not None for entry in entries)
    assert all(0 <= entry.location.index < ENTRY_COUNT for entry in entries)
    assert len({entry.identity for entry in entries}) == STRING_COUNT


def test_the_whole_pool_round_trips_byte_for_byte(strings, image):
    """The ROUND_TRIP ship gate: the whole extent, not a sample.

    Every string re-encodes to its exact original bytes, and concatenating the
    re-encoded strings in address order reproduces the pool exactly - so no byte
    of the extent sits outside the representation.
    """
    entries = sorted(strings.entries(), key=lambda e: e.location.file_offset)

    for entry in entries:
        assert strings.codec.encode(entry.text) == entry.original_bytes

    rebuilt = b"".join(strings.codec.encode(entry.text) for entry in entries)
    assert rebuilt == image[POOL_START:POOL_END]
    assert len(rebuilt) == POOL_SIZE


def test_an_unedited_plan_is_a_no_op_over_every_string(strings):
    """Every string is encoded, and every one of them re-encodes unchanged.

    The plan retains its changes rather than discarding them - that is what lets
    `emit_image` assert the base bytes still match before writing - so the proof
    is that each carries identical `old` and `new`, and that the plan reports
    itself as a no-op.
    """
    changes = strings.changes()
    assert len(changes) == STRING_COUNT

    plan = strings.plan()
    assert len(plan.changes) == STRING_COUNT
    assert plan.is_noop
    assert all(change.old == change.new for change in plan.changes)


def test_the_format_specifiers_survive_verbatim(strings):
    """`%d`/`%s` are preserved, never interpreted."""
    formatted = [entry for entry in strings.entries() if "%" in entry.text]
    assert formatted
    for entry in formatted:
        assert strings.codec.encode(entry.text) == entry.original_bytes


def test_the_embedded_newline_survives_the_round_trip(strings):
    multiline = [entry for entry in strings.entries() if "\n" in entry.text]
    assert len(multiline) == 1
    entry = multiline[0]
    assert entry.text == "No\nPortrait\nData"
    assert strings.codec.encode(entry.text) == entry.original_bytes


# --- exit criterion 5: unsupported subsystems fail clearly ---------------


def test_logii_stats_fail_clearly_rather_than_returning_something(rom, catalog):
    """Blocked on evidence, and refused by name rather than approximated."""
    with pytest.raises(StatProfileError, match="does not declare enemy_stats"):
        load_stat_tables(rom, catalog)


def test_logii_map_entries_fail_clearly(rom, catalog):
    """A 0x38-stride table exists in this ROM, but not this codec's layout."""
    from tools.webfoot.formats.map_entry import (
        MapEntryProfileError,
        read_map_entry_table,
    )

    with pytest.raises(MapEntryProfileError, match="does not declare map_entries"):
        read_map_entry_table(rom, catalog)


# --- exit criterion 6: deterministic extraction --------------------------


def test_extraction_is_deterministic_and_omits_undeclared_subsystems(
    rom, catalog, tmp_path
):
    first = tmp_path / "a"
    second = tmp_path / "b"
    extract_project(rom, first, catalog)
    extract_project(rom, second, catalog)

    written = sorted(p.name for p in first.rglob("*.toml"))
    assert written == ["project.toml", "strings.toml"]
    assert not (first / "enemies").exists()
    assert not (first / "characters").exists()

    for name in ("project.toml", "text/strings.toml"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_the_extracted_project_loads_and_carries_every_string(rom, catalog, tmp_path):
    extract_project(rom, tmp_path, catalog)
    project = read_project(tmp_path)

    assert project.meta.profile_id == PROFILE_ID
    assert project.meta.base_rom_sha256 == CANONICAL_SHA256
    assert len(project.strings) == STRING_COUNT
    assert project.enemies == {}
    assert project.characters == {}


def test_the_extracted_project_validates_with_no_problems(rom, catalog, tmp_path):
    extract_project(rom, tmp_path, catalog)
    report = validate_project(tmp_path, rom, catalog)

    assert report.problems == ()
    assert report.passed
    assert report.string_count == STRING_COUNT
    assert report.enemy_count == 0
    assert report.character_count == 0


# --- exit criterion 7: no-op whole-ROM rebuild ---------------------------


def test_an_unchanged_project_rebuilds_the_whole_rom_byte_for_byte(
    rom, catalog, tmp_path
):
    """The strongest integration proof: every byte, including undecoded ones."""
    project = tmp_path / "project"
    output = tmp_path / "out.gba"
    extract_project(rom, project, catalog)

    result = build_project(project, rom, output, catalog)

    assert result.manifest.changes == ()
    assert output.read_bytes() == open(rom, "rb").read()
    assert hashlib.sha256(output.read_bytes()).hexdigest() == CANONICAL_SHA256


# --- exit criterion 8: semantic edit, byte diff and provenance -----------


def _edit_identity(strings) -> TextIdentity:
    matches = [e for e in strings.entries() if e.text == EDIT_TEXT]
    assert len(matches) == 1, f"{EDIT_TEXT!r} must be unique to be a safe target"
    return matches[0].identity


def test_a_semantic_edit_changes_only_the_expected_bytes(
    rom, catalog, tmp_path, strings
):
    """Exit criteria 10 and 17: exact byte diff, with provenance."""
    identity = _edit_identity(strings)
    project = tmp_path / "project"
    output = tmp_path / "out.gba"
    extract_project(rom, project, catalog)

    path = project / "text" / "strings.toml"
    source = path.read_text(encoding="utf-8")
    assert f'text = "{EDIT_TEXT}"' in source
    path.write_text(
        source.replace(f'text = "{EDIT_TEXT}"', f'text = "{EDIT_REPLACEMENT}"'),
        encoding="utf-8",
        newline="\n",
    )

    result = build_project(project, rom, output, catalog)

    base = open(rom, "rb").read()
    built = output.read_bytes()
    assert len(built) == len(base)

    differing = [i for i in range(len(base)) if base[i] != built[i]]
    assert differing == list(range(EDIT_FIRST_BYTE, EDIT_LAST_BYTE + 1))
    assert len(differing) == 7

    # The replacement is shorter, so its slack is deterministically zero-padded
    # rather than the pool being repacked.
    assert built[EDIT_FIRST_BYTE - 9 : EDIT_LAST_BYTE + 2] == b"Yunzabit Wastes\x00\x00"

    (change,) = result.manifest.changes
    assert change.owner == str(identity)
    assert change.reason == "text edit"
    assert change.offset <= EDIT_FIRST_BYTE
    assert change.offset + len(change.new) > EDIT_LAST_BYTE


def test_repeated_builds_of_the_same_edit_are_byte_identical(rom, catalog, tmp_path):
    """Exit criterion 11: determinism, asserted on the modified build."""
    project = tmp_path / "project"
    extract_project(rom, project, catalog)
    path = project / "text" / "strings.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            f'text = "{EDIT_TEXT}"', f'text = "{EDIT_REPLACEMENT}"'
        ),
        encoding="utf-8",
        newline="\n",
    )

    first = tmp_path / "first.gba"
    second = tmp_path / "second.gba"
    build_project(project, rom, first, catalog)
    build_project(project, rom, second, catalog)

    assert first.read_bytes() == second.read_bytes()
    assert hashlib.sha256(first.read_bytes()).hexdigest() != CANONICAL_SHA256


def test_a_longer_string_is_refused_with_the_exact_deficit(strings):
    """The pool is exhaustively tiled, so growth needs relocation, which needs
    declared free space this profile does not have."""
    identity = _edit_identity(strings)

    with pytest.raises(TextTooLongError) as error:
        strings.set_text(identity, EDIT_TOO_LONG)

    message = str(error.value)
    assert "needs 18 bytes" in message
    assert "allocation is 17" in message
    assert "1 bytes too long" in message


def test_an_over_long_edit_writes_no_output_at_all(rom, catalog, tmp_path):
    """Validation precedes emission, so a refused build leaves nothing behind."""
    from tools.webfoot.project import ProjectValidationError

    project = tmp_path / "project"
    output = tmp_path / "out.gba"
    extract_project(rom, project, catalog)
    path = project / "text" / "strings.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            f'text = "{EDIT_TEXT}"', f'text = "{EDIT_TOO_LONG}"'
        ),
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(ProjectValidationError, match="too long"):
        build_project(project, rom, output, catalog)

    assert not output.exists()


# --- exit criterion 9: the canonical ROM is never modified ---------------


def test_the_canonical_rom_is_unchanged_by_every_operation(rom, catalog, tmp_path):
    """Asserted last, over the whole read/extract/build/edit cycle."""
    before = open(rom, "rb").read()
    before_mtime = os.stat(rom).st_mtime_ns

    project = tmp_path / "project"
    extract_project(rom, project, catalog)
    build_project(project, rom, tmp_path / "noop.gba", catalog)
    path = project / "text" / "strings.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            f'text = "{EDIT_TEXT}"', f'text = "{EDIT_REPLACEMENT}"'
        ),
        encoding="utf-8",
        newline="\n",
    )
    build_project(project, rom, tmp_path / "edited.gba", catalog)

    after = open(rom, "rb").read()
    assert after == before
    assert hashlib.sha256(after).hexdigest() == CANONICAL_SHA256
    assert os.stat(rom).st_mtime_ns == before_mtime
