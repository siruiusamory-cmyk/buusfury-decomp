"""TOOLKIT-004 proofs for the authored text representation.

Portable: these build a project tree by hand rather than extracting one, so no
ROM is required. The ROM-gated extraction proofs live in
`tests/integration/test_text_rom.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.webfoot.formats.text_tables import TextIdentity
from tools.webfoot.project import (
    PROJECT_FORMAT_VERSION,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    dump_toml,
    load_toml,
    read_project,
    write_project,
)
from tools.webfoot.formats import stat_tables as st


SHA = "0" * 64


def _meta() -> ProjectMeta:
    return ProjectMeta(
        format_version=PROJECT_FORMAT_VERSION,
        profile_id="synthetic-v1",
        game="synthetic",
        base_rom_sha256=SHA,
        base_rom_size=1024,
        name="fixture",
    )


def _minimal_records():
    """One enemy and one character, so `write_project` has something to write."""
    enemy = st.EnemyRecord(
        offset=0,
        exp=1,
        hp=2,
        type_id=434,
        level=3,
        strength=4,
        power=5,
        endurance=6,
    )
    character = st.BaseStatRecord(
        offset=0,
        level=1,
        hp=2,
        ep=3,
        strength=4,
        power=5,
        endurance=6,
        speed=7,
        person=8,
        technique_count=0,
    )
    return (
        [(st.enemy_identity(enemy), enemy, bytes(st.ENEMY_RECORD_SIZE), None)],
        [
            (
                st.character_identity(0),
                character,
                bytes(st.BASE_STAT_RECORD_SIZE),
                "Goku",
            )
        ],
    )


def _write(tmp_path: Path, strings) -> Path:
    enemies, characters = _minimal_records()
    write_project(
        tmp_path,
        _meta(),
        enemies=enemies,
        characters=characters,
        strings=strings,
    )
    return tmp_path


# --- exit criterion 9: deterministic project extraction ------------------


def test_strings_file_is_written_only_when_there_is_text():
    """A profile with no string table must not leave a file claiming otherwise."""
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        root = _write(Path(directory), [])
        assert not (root / "text" / "strings.toml").exists()


def test_strings_are_written_in_index_order_regardless_of_input_order(tmp_path):
    given = [
        (TextIdentity(10), "ten"),
        (TextIdentity(2), "two"),
        (TextIdentity(1), "one"),
    ]
    root = _write(tmp_path, given)
    text = (root / "text" / "strings.toml").read_text(encoding="utf-8")
    assert text.index("text:0001") < text.index("text:0002") < text.index("text:0010")


def test_writing_the_same_strings_twice_produces_identical_bytes(tmp_path):
    strings = [(TextIdentity(i), f"line {i}") for i in (5, 1, 3)]
    first = _write(tmp_path / "a", strings).joinpath("text/strings.toml").read_bytes()
    second = _write(tmp_path / "b", strings).joinpath("text/strings.toml").read_bytes()
    assert first == second


def test_the_authored_file_carries_no_address_and_no_raw_blob(tmp_path):
    """Text needs no opaque blob: the codec is lossless, so the text IS the bytes.

    Also asserts the file is free of addresses, which would tie a portable mod
    to one ROM layout.
    """
    root = _write(tmp_path, [(TextIdentity(0), "Start")])
    text = (root / "text" / "strings.toml").read_text(encoding="utf-8")
    assert "raw" not in text
    assert "0x" not in text
    assert "address" not in text


def test_written_strings_load_back_unchanged(tmp_path):
    strings = [
        (TextIdentity(0), "Start"),
        (TextIdentity(1), ""),
        (TextIdentity(2), "A\nB"),
        (TextIdentity(3), "with {08:07} control"),
        (TextIdentity(4), 'quote " and backslash \\'),
        (TextIdentity(5), "Hercule Café"),
    ]
    root = _write(tmp_path, strings)
    loaded = read_project(root)
    assert loaded.strings == dict(strings)


# --- absence is legal -----------------------------------------------------


def test_a_project_without_a_strings_file_loads_with_no_strings(tmp_path):
    root = _write(tmp_path, [])
    assert read_project(root).strings == {}


# --- exit criterion 8: invalid text fails before output ------------------


@pytest.mark.parametrize(
    "value",
    ["bad {08:ZZ} token", "emoji \U0001F600"],
    ids=["malformed-control-token", "unencodable-character"],
)
def test_text_the_codec_cannot_encode_loads_but_never_reaches_an_image(
    tmp_path, value
):
    """Encodability is a property of the ROM's encoding, not of the project.

    TOOLKIT-004 refused these at project load, against the UTF-16LE codec. That
    was right while one game existed and is wrong now: "{08:ZZ}" and an
    astral-plane character are unencodable *in UTF-16LE*, and a project does not
    know which encoding its base ROM uses until a build pairs the two.

    So loading now succeeds and the refusal moved to `build`, which runs with
    the profile-selected codec. The guarantee that matters is unchanged and is
    asserted here: nothing is emitted. The ROM-gated proof that a build actually
    reports these lives in `tests/integration/test_text_rom.py`.
    """
    root = _write(tmp_path, [(TextIdentity(0), "ok")])
    path = root / "text" / "strings.toml"
    path.write_text(
        dump_toml({"text": {"text:0000": {"text": value}}}),
        encoding="utf-8",
        newline="\n",
    )

    assert read_project(root).strings == {TextIdentity(0): value}


def test_a_malformed_identity_key_is_refused(tmp_path):
    root = _write(tmp_path, [(TextIdentity(0), "ok")])
    path = root / "text" / "strings.toml"
    path.write_text(
        dump_toml({"text": {"string-0": {"text": "hi"}}}),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectLoadError, match="not a valid text identity key"):
        read_project(root)


def test_a_negative_identity_is_refused(tmp_path):
    """The one bound that is game-independent: an index cannot be negative.

    An *upper* bound is deliberately not checked here. It is the profile's table
    count, which differs per game - 1,534 for Buu's Fury, 217 for Legacy of Goku
    II - and a project is not tied to a profile until it is built. An index past
    the end is caught by `build._check_strings` as "a string this ROM does not
    contain", which is both accurate and the earliest point it can be known.
    """
    root = _write(tmp_path, [(TextIdentity(0), "ok")])
    path = root / "text" / "strings.toml"
    path.write_text(
        dump_toml({"text": {"text:-1": {"text": "hi"}}}),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectLoadError, match="not a valid text identity key"):
        read_project(root)


def test_an_unknown_field_is_refused_rather_than_ignored(tmp_path):
    """Silently dropping a field would let a mod think it authored something."""
    root = _write(tmp_path, [(TextIdentity(0), "ok")])
    path = root / "text" / "strings.toml"
    path.write_text(
        dump_toml({"text": {"text:0000": {"text": "hi", "address": "0x1"}}}),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectLoadError, match="unknown fields"):
        read_project(root)


def test_a_non_string_text_value_is_refused(tmp_path):
    root = _write(tmp_path, [(TextIdentity(0), "ok")])
    path = root / "text" / "strings.toml"
    path.write_text(
        dump_toml({"text": {"text:0000": {"text": 7}}}),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectValidationError, match="must be a string"):
        read_project(root)


def test_an_empty_strings_table_is_refused(tmp_path):
    """An empty [text] table means "I meant to author text and did not"."""
    root = _write(tmp_path, [(TextIdentity(0), "ok")])
    path = root / "text" / "strings.toml"
    path.write_text(dump_toml({"text": {}}), encoding="utf-8", newline="\n")
    with pytest.raises(ProjectLoadError, match="declares no strings"):
        read_project(root)


# --- the TOML escape the text format needed ------------------------------


def test_newline_and_tab_survive_the_toml_round_trip():
    document = {"text": {"text:0000": {"text": "a\nb\tc"}}}
    assert load_toml(dump_toml(document)) == document


def test_other_control_characters_are_still_refused():
    from tools.webfoot.project import ProjectFormatError

    with pytest.raises(ProjectFormatError, match="control characters"):
        dump_toml({"text": {"text:0000": {"text": "bell \x07"}}})
