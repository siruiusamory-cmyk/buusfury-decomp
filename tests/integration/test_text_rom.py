"""ROM-gated proofs for the TOOLKIT-004 text subsystem.

These are the exit criteria that cannot be demonstrated on synthetic data: the
verified layout contract, the full 1,534-string extent round trip, the canonical
in-place edit, and the whole-image no-op rebuild with text in the pipeline.

They skip cleanly when the canonical ROM is absent, so the portable suite stays
runnable without proprietary data. The ROM is opened read-only and is verified
unchanged afterwards; no ROM-derived fixture is committed.
"""

from __future__ import annotations

import glob
import hashlib
import os

import pytest

from tools.webfoot.build import (
    build_project,
    extract_project,
    validate_project,
)
from tools.webfoot.cli import main
from tools.webfoot.formats import text_tables as tt
from tools.webfoot.formats.text_tables import TextCodecError, TextIdentity
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import read_project
from tools.webfoot.text import TextTooLongError, load_text_strings
from tools.webfoot.write import apply_plan

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: TOOLKIT-004 verified extents. Repeated here rather than imported so the test
#: fails if the module's constants drift, which is the point of a contract test.
POOL_START = 0x0005792C
POOL_END = 0x0006BCE6
TABLE_START = 0x0006BCE8
ENTRY_COUNT = 1534
POOL_SIZE = POOL_END - POOL_START

#: A string whose text is unique across the pool, used as the edit target. Its
#: uniqueness is asserted rather than assumed, so the test locates it by content
#: instead of hardcoding an index that a re-verification could invalidate.
EDIT_TEXT = "New Game"
EDIT_REPLACEMENT = "Old Game"


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
def image(rom: str) -> bytes:
    with open(rom, "rb") as stream:
        return stream.read()


@pytest.fixture
def strings(rom: str, catalog: RomProfileCatalog):
    return load_text_strings(rom, catalog)


# --- exit criterion 1: the verified layout contract ----------------------


def test_the_profile_declares_the_verified_text_layout(catalog: RomProfileCatalog):
    profile = next(
        p for p in catalog.profiles if p.id == "buus_fury_usa_rev0_01c1707f"
    )
    layout = profile.text_strings
    assert layout is not None
    assert layout.pool_address.raw == POOL_START + tt.GBA_ROM_BASE
    assert layout.pointer_table_address.raw == TABLE_START + tt.GBA_ROM_BASE
    assert layout.count == ENTRY_COUNT
    assert layout.pool_size == POOL_SIZE
    assert layout.encoding == "utf16le_nul_terminated"
    # No verified free region exists for this profile, so canonical growth is
    # blocked. If a future ticket declares one, this flag flips deliberately.
    assert layout.relocatable is False
    assert profile.free_regions == ()


def test_the_pointer_table_tiles_the_pool_exhaustively(image: bytes):
    """The property that makes a COMPLETE round trip provable.

    Every string ends exactly where the next begins, the first starts at the
    pool base, and the last ends at the pool end - so the 1,534 enumerated
    strings account for every one of the pool's bytes with no gap or overlap.
    """
    assert tt.pool_is_exhaustively_tiled(image)


def test_every_pointer_is_distinct_and_strictly_ascending(image: bytes):
    """No aliasing: no two table entries share a payload.

    This is what lets an edit be local - editing one string cannot silently
    change another - and what makes a no-op build unable to split or duplicate
    a shared string.
    """
    targets = [tt.read_pointer(image, i) for i in range(ENTRY_COUNT)]
    assert len(set(targets)) == ENTRY_COUNT
    assert targets == sorted(targets)
    assert all(a < b for a, b in zip(targets, targets[1:]))


def test_the_pool_base_has_exactly_one_inbound_reference(image: bytes):
    """Access is by table index, never by a direct pointer to a string.

    Verified by counting word-aligned words in the whole 8 MiB image that equal
    the pool base: exactly one, and it is the table's own first entry. This is
    the finding that makes relocating a string a one-word rewrite.
    """
    needle = (POOL_START + tt.GBA_ROM_BASE).to_bytes(4, "little")
    sites = [
        offset
        for offset in range(0, len(image) - 3, 4)
        if image[offset : offset + 4] == needle
    ]
    assert sites == [TABLE_START]


def test_only_five_words_coincidentally_match_a_string_address(image: bytes):
    """The candidate references, counted.

    Every one of them sits outside the pointer table in compressed graphics
    data. They are CANDIDATE, not CONFIRMED, and the relocation machinery fails
    closed on them - proved portably in `tests/unit/test_text_relocation.py`.
    """
    starts = {tt.read_pointer(image, i) for i in range(ENTRY_COUNT)}
    table_end = TABLE_START + ENTRY_COUNT * 4
    coincidences = []
    for offset in range(0, len(image) - 3, 4):
        if TABLE_START <= offset < table_end:
            continue
        value = int.from_bytes(image[offset : offset + 4], "little")
        if value - tt.GBA_ROM_BASE in starts:
            coincidences.append(offset)
    assert coincidences == [0x2DD7B4, 0x30C5DC, 0x5A51B4, 0x67907C, 0x6C8040]


# --- exit criterion 2: deterministic enumeration -------------------------


def test_enumeration_is_deterministic_and_complete(strings):
    first = [(e.identity, e.text, e.location.file_offset) for e in strings.entries()]
    second = [(e.identity, e.text, e.location.file_offset) for e in strings.entries()]
    assert first == second
    assert len(first) == ENTRY_COUNT
    assert [e[0].index for e in first] == list(range(ENTRY_COUNT))


def test_known_strings_decode_to_their_expected_text(strings):
    """Spot checks against text a human can confirm on screen.

    These are not the round-trip proof - that is exhaustive below - but a decode
    that produced plausible garbage would still round-trip, so a semantic check
    is needed alongside it.
    """
    texts = [entry.text for entry in strings.entries()]
    for expected in ("Start", "Options", "New Game", "Saving...", "Are you sure?"):
        assert expected in texts


def test_the_pool_contains_the_control_codes_the_research_documented(strings):
    """The 0x08 prefix and the newline, as counted in docs/research/TEXT_FORMAT.md."""
    joined = "".join(entry.text for entry in strings.entries())
    assert joined.count("{08:") == 100
    assert joined.count("\n") == 24


def test_eleven_strings_are_empty(strings):
    empty = [e.identity.index for e in strings.entries() if e.text == ""]
    assert len(empty) == 11
    assert 0 in empty


def test_the_single_non_ascii_codepoint_decodes_as_an_accented_e(strings):
    """The evidence that this is UTF-16LE rather than a custom glyph table."""
    hits = [e for e in strings.entries() if any(ord(c) > 0x7E for c in e.text)]
    assert len(hits) == 1
    assert hits[0].text == "Hercule Café"


def test_the_documented_examples_are_real_rom_content(strings):
    """`docs/project-format.md` shows two authored entries. Pin them.

    A worked example that drifts from the ROM is worse than no example, because
    a reader copies it. These are the two the document prints verbatim.
    """
    # Identity keys are DECIMAL, so text:0010 is index 10, not 16.
    assert strings.entry(TextIdentity(10)).text == "New Game"
    assert strings.entry(TextIdentity(41)).text == (
        "{08:05}HP:{08:02} {08:76}%d{08:05}/{08:76}%d{08:02}"
    )


# --- shared strings: duplicated content, never shared storage ------------


def test_repeated_text_has_independent_storage_not_a_shared_payload(strings):
    """The aliasing question, answered against the ROM rather than assumed.

    153 texts occur more than once - one crate description appears 25 times -
    but every occurrence has its own distinct offset and its own bytes. The
    duplication is in the CONTENT, not in the storage.

    That settles the edit semantics without needing a clone operation: editing
    one occurrence changes only that occurrence, because no two table entries
    ever address the same payload. A tool that assumed sharing would either
    wrongly update 25 lines at once or wrongly refuse the edit.
    """
    entries = list(strings.entries())
    by_text: dict[str, list[int]] = {}
    for entry in entries:
        by_text.setdefault(entry.text, []).append(entry.location.file_offset)

    repeated = {text: offsets for text, offsets in by_text.items() if len(offsets) > 1}
    assert len(repeated) == 153

    # Every occurrence of every repeated text sits at its own offset.
    for offsets in repeated.values():
        assert len(set(offsets)) == len(offsets)

    # And no offset is shared across different texts either, which is the same
    # fact approached from the other side.
    assert len({e.location.file_offset for e in entries}) == len(entries)


def test_editing_one_occurrence_leaves_its_duplicates_alone(image: bytes, strings):
    """The consequence of the finding above, proved end to end."""
    crate = "A crate with Hercule's logo on it."
    occurrences = strings.find(crate)
    assert len(occurrences) == 25

    first = occurrences[0]
    strings.set_text(first.identity, "A crate with Hercule's logo on it!")

    plan = strings.plan()
    change, = plan.effective_changes
    assert change.offset == first.location.file_offset

    built = apply_plan(image, plan)
    for other in occurrences[1:]:
        assert tt.decode_string(built, other.location.file_offset)[0] == crate


# --- exit criterion 6: the full extent round-trips byte-identically ------


def test_every_string_re_encodes_to_exactly_its_original_bytes(strings):
    failures = [
        entry.identity
        for entry in strings.entries()
        if tt.encode_string(entry.text) != entry.original_bytes
    ]
    assert failures == []


def test_the_whole_pool_extent_is_reproduced_byte_for_byte(image: bytes, strings):
    """The ROUND_TRIP proof, over the complete extent rather than a sample.

    Concatenating every encoded string must reproduce the pool's 82,874 bytes
    exactly. Because the table tiles the pool, this covers every byte in it.
    """
    rebuilt = b"".join(tt.encode_string(e.text) for e in strings.entries())
    assert len(rebuilt) == POOL_SIZE
    assert rebuilt == image[POOL_START:POOL_END]


def test_an_unedited_plan_contains_no_changes(strings):
    assert strings.plan().effective_changes == ()


# --- exit criterion 7: a same-size edit changes only the expected bytes --


def test_the_edit_target_text_is_unique_across_the_pool(strings):
    assert len(strings.find(EDIT_TEXT)) == 1


def test_a_same_size_edit_changes_exactly_the_expected_bytes(image: bytes, strings):
    entry, = strings.find(EDIT_TEXT)
    strings.set_text(entry.identity, EDIT_REPLACEMENT)

    plan = strings.plan()
    change, = plan.effective_changes
    assert change.offset == entry.location.file_offset
    assert change.size == entry.location.allocation
    assert change.owner == str(entry.identity)
    assert "text edit" in change.reason

    built = apply_plan(image, plan)
    differing = [i for i in range(len(image)) if image[i] != built[i]]
    # "New" -> "Old": three characters differ, each one UTF-16 low byte.
    expected = [
        entry.location.file_offset,
        entry.location.file_offset + 2,
        entry.location.file_offset + 4,
    ]
    assert differing == expected
    assert tt.decode_string(built, entry.location.file_offset)[0] == EDIT_REPLACEMENT


def test_a_shorter_edit_pads_deterministically_and_stays_in_its_allocation(
    image: bytes, strings
):
    entry, = strings.find(EDIT_TEXT)
    strings.set_text(entry.identity, "Old")

    change, = strings.plan().effective_changes
    assert change.size == entry.location.allocation
    assert change.new == tt.encode_string("Old") + bytes(
        entry.location.allocation - tt.encoded_size("Old")
    )
    assert tt.decode_string(change.new, 0)[0] == "Old"


def test_an_edit_that_would_not_fit_is_refused_with_the_exact_deficit(strings):
    entry, = strings.find(EDIT_TEXT)
    with pytest.raises(TextTooLongError, match="bytes too long"):
        strings.set_text(entry.identity, "A Very Much Longer Replacement Name")


def test_canonical_growth_stays_blocked_because_no_free_space_is_declared(strings):
    """The capability boundary, asserted rather than only documented.

    Longer text is refused for this ROM because no verified free region exists
    to relocate into - not because the machinery is missing. The machinery is
    proved in `tests/unit/test_text_relocation.py`.
    """
    assert strings.profile.free_regions == ()
    assert strings.layout.relocatable is False


def test_a_malformed_control_token_is_refused_before_any_plan(strings):
    entry, = strings.find(EDIT_TEXT)
    with pytest.raises(TextCodecError):
        strings.set_text(entry.identity, "bad {08:ZZ}")
    # The refusal left nothing behind: the plan is still a no-op.
    assert strings.plan().effective_changes == ()


# --- exit criteria 9-12: project extraction and the whole-ROM guarantee --


def test_extraction_includes_every_string_deterministically(
    tmp_path, rom: str, catalog: RomProfileCatalog
):
    first = tmp_path / "a"
    second = tmp_path / "b"
    extract_project(rom, first, catalog)
    extract_project(rom, second, catalog)

    path = first / "text" / "strings.toml"
    assert path.is_file()
    assert path.read_bytes() == (second / "text" / "strings.toml").read_bytes()
    assert len(read_project(first).strings) == ENTRY_COUNT


def test_an_extracted_project_validates_against_its_base_rom(
    tmp_path, rom: str, catalog: RomProfileCatalog
):
    extract_project(rom, tmp_path / "p", catalog)
    report = validate_project(tmp_path / "p", rom, catalog)
    assert report.problems == ()
    assert report.passed
    assert report.string_count == ENTRY_COUNT


def test_a_no_op_build_reproduces_the_canonical_rom_exactly(
    tmp_path, rom: str, catalog: RomProfileCatalog
):
    """TOOLKIT-002's whole-ROM guarantee, still holding with text in the pipeline."""
    extract_project(rom, tmp_path / "p", catalog)
    result = build_project(tmp_path / "p", rom, tmp_path / "out.gba", catalog)

    assert result.manifest.output_sha256 == CANONICAL_SHA256
    assert result.manifest.changes == ()
    assert (
        hashlib.sha256((tmp_path / "out.gba").read_bytes()).hexdigest()
        == CANONICAL_SHA256
    )


def test_a_text_edit_through_the_project_changes_only_that_string(
    tmp_path, rom: str, catalog: RomProfileCatalog, image: bytes
):
    extract_project(rom, tmp_path / "p", catalog)
    path = tmp_path / "p" / "text" / "strings.toml"
    source = path.read_text(encoding="utf-8")
    assert f'text = "{EDIT_TEXT}"' in source
    path.write_text(
        source.replace(f'text = "{EDIT_TEXT}"', f'text = "{EDIT_REPLACEMENT}"'),
        encoding="utf-8",
        newline="\n",
    )

    result = build_project(tmp_path / "p", rom, tmp_path / "out.gba", catalog)
    change, = result.manifest.changes
    assert change.owner.startswith("text:")
    assert "text edit" in change.reason

    built = (tmp_path / "out.gba").read_bytes()
    differing = [i for i in range(len(image)) if image[i] != built[i]]
    assert len(differing) == 3


def test_repeated_modified_builds_are_byte_identical(
    tmp_path, rom: str, catalog: RomProfileCatalog
):
    extract_project(rom, tmp_path / "p", catalog)
    path = tmp_path / "p" / "text" / "strings.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            f'text = "{EDIT_TEXT}"', f'text = "{EDIT_REPLACEMENT}"'
        ),
        encoding="utf-8",
        newline="\n",
    )

    build_project(tmp_path / "p", rom, tmp_path / "one.gba", catalog)
    build_project(tmp_path / "p", rom, tmp_path / "two.gba", catalog)
    assert (tmp_path / "one.gba").read_bytes() == (tmp_path / "two.gba").read_bytes()


def test_an_unencodable_authored_string_fails_before_any_output_exists(
    tmp_path, rom: str, catalog: RomProfileCatalog
):
    """Validation before emission: a rejected build leaves no partial image."""
    extract_project(rom, tmp_path / "p", catalog)
    path = tmp_path / "p" / "text" / "strings.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            f'text = "{EDIT_TEXT}"', 'text = "bad {08:ZZ} token"'
        ),
        encoding="utf-8",
        newline="\n",
    )

    output = tmp_path / "never.gba"
    with pytest.raises(ValueError):
        build_project(tmp_path / "p", rom, output, catalog)
    assert not output.exists()


def test_an_over_long_authored_string_fails_before_any_output_exists(
    tmp_path, rom: str, catalog: RomProfileCatalog
):
    extract_project(rom, tmp_path / "p", catalog)
    path = tmp_path / "p" / "text" / "strings.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            f'text = "{EDIT_TEXT}"', 'text = "A Very Much Longer Replacement Name"'
        ),
        encoding="utf-8",
        newline="\n",
    )

    output = tmp_path / "never.gba"
    with pytest.raises(ValueError, match="bytes too long"):
        build_project(tmp_path / "p", rom, output, catalog)
    assert not output.exists()


# --- exit criterion 17: wrong profile fails closed -----------------------


def test_text_access_refuses_a_profile_whose_metadata_was_altered(rom: str):
    """Identity verification authenticates the ROM, not the metadata about it.

    A local profile file that keeps the hashes but moves the declared extents
    must be refused, or a hand-edited YAML could redirect writes.
    """
    from tools.webfoot.text import TextProfileError

    source = open("config/roms.yaml", encoding="utf-8").read()
    tampered = source.replace("pool_size: 82874", "pool_size: 82000")
    assert tampered != source
    catalog = RomProfileCatalog.loads(tampered, source="tampered")

    with pytest.raises(TextProfileError, match="conflicts with the packaged contract"):
        load_text_strings(rom, catalog)


# --- the CLI surface ------------------------------------------------------
#
# ROM-gated rather than portable because text access requires the exact
# canonical profile by design, so a synthetic image cannot reach these paths.


def test_cli_text_list_filters_by_content(rom: str, capsys):
    assert main(["text", "list", rom, "--contains", EDIT_TEXT]) == 0
    output = capsys.readouterr().out
    assert EDIT_TEXT in output
    assert "Strings: 1 shown 1" in output


def test_cli_text_list_limit_reports_the_remainder(rom: str, capsys):
    assert main(["text", "list", rom, "--limit", "5"]) == 0
    output = capsys.readouterr().out
    assert f"Strings: {ENTRY_COUNT} shown 5" in output
    assert f"... {ENTRY_COUNT - 5} more" in output


def test_cli_text_show_accepts_an_unpadded_identity(rom: str, capsys):
    assert main(["text", "show", rom, "text:10"]) == 0
    output = capsys.readouterr().out
    assert "Identity: text:0010" in output
    assert "Allocation:" in output


def test_cli_text_show_rejects_a_malformed_identity(rom: str, capsys):
    assert main(["text", "show", rom, "0010"]) == 2
    assert "not a string identity" in capsys.readouterr().err


def test_cli_round_trip_command_reports_the_full_extent(rom: str, capsys):
    assert main(["text", "validate-round-trip", rom]) == 0
    output = capsys.readouterr().out
    assert f"Strings checked: {ENTRY_COUNT}" in output
    assert f"Byte-identical: {ENTRY_COUNT}" in output
    assert "Failures: 0" in output
    assert "COMPLETE" in output


def test_cli_text_set_writes_a_new_image_and_leaves_the_base_alone(
    tmp_path, rom: str, capsys
):
    before = hashlib.sha256(open(rom, "rb").read()).hexdigest()
    output_path = tmp_path / "edited.gba"

    assert (
        main(
            [
                "text",
                "set",
                rom,
                "text:10",
                EDIT_REPLACEMENT,
                "--output",
                str(output_path),
            ]
        )
        == 0
    )
    assert "COMPLETE" in capsys.readouterr().out
    assert output_path.is_file()
    assert hashlib.sha256(open(rom, "rb").read()).hexdigest() == before


def test_cli_text_set_refuses_over_long_text_and_writes_nothing(
    tmp_path, rom: str, capsys
):
    output_path = tmp_path / "never.gba"

    assert (
        main(
            [
                "text",
                "set",
                rom,
                "text:10",
                "A Very Much Longer Replacement Name",
                "--output",
                str(output_path),
            ]
        )
        == 2
    )
    assert "bytes too long" in capsys.readouterr().err
    assert not output_path.exists()


# --- exit criterion 12: the canonical ROM is immutable -------------------


def test_the_canonical_rom_is_unchanged_by_the_whole_text_path(
    tmp_path, rom: str, catalog: RomProfileCatalog
):
    before = hashlib.sha256(open(rom, "rb").read()).hexdigest()

    strings = load_text_strings(rom, catalog)
    entry, = strings.find(EDIT_TEXT)
    strings.set_text(entry.identity, EDIT_REPLACEMENT)
    strings.plan()
    extract_project(rom, tmp_path / "p", catalog)
    build_project(tmp_path / "p", rom, tmp_path / "out.gba", catalog)

    assert hashlib.sha256(open(rom, "rb").read()).hexdigest() == before == CANONICAL_SHA256
