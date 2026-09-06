"""Portable tests for the project format and its validation.

No ROM required. These cover the parts of TOOLKIT-002 that are decidable from
text alone: deterministic serialization, schema and version rejection, identity
agreement, and the codec's continued independence from the filesystem.

The ROM-gated proofs - whole-image round trip, the wolf edit, repeated-build
identity - live in `tests/integration/test_project_build_rom.py`.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from tools.webfoot.formats import stat_tables as st
from tools.webfoot.project import (
    PROJECT_FORMAT_VERSION,
    ProjectFormatError,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    dump_toml,
    load_toml,
    read_project,
    write_project,
)

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)


def _meta(**overrides) -> ProjectMeta:
    values = {
        "format_version": PROJECT_FORMAT_VERSION,
        "profile_id": "buus_fury_usa_rev0_01c1707f",
        "game": "buus_fury",
        "base_rom_sha256": CANONICAL_SHA256,
        "base_rom_size": 8388608,
        "name": "test-project",
    }
    values.update(overrides)
    return ProjectMeta(**values)


def _enemy(type_id: int = 434, hp: int = 175):
    original = bytes(range(st.ENEMY_RECORD_SIZE))
    record = st.decode_enemy_record(original, 0)
    record = type(record)(
        offset=0,
        exp=record.exp,
        hp=hp,
        type_id=type_id,
        level=5,
        strength=record.strength,
        power=record.power,
        endurance=record.endurance,
    )
    # `raw` must be the bytes the semantic fields were encoded over, or a build
    # would re-emit a record whose opaque span belongs to a different record.
    return (
        st.StatIdentity(kind="enemy", key=type_id),
        record,
        st.encode_enemy_record(record, original),
        None,
    )


def _character(index: int = 0):
    original = bytes(range(st.BASE_STAT_RECORD_SIZE))
    record = st.decode_base_stat_record(original, 0)
    return (
        st.StatIdentity(kind="character", key=index),
        record,
        st.encode_base_stat_record(record, original),
        st.character_alias(index),
    )


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    write_project(
        tmp_path / "proj",
        _meta(),
        enemies=[_enemy()],
        characters=[_character()],
    )
    return tmp_path / "proj"


# --- deterministic serialization ----------------------------------------


def test_dump_toml_is_byte_stable_across_calls():
    document = {"project": {"format_version": 1, "name": "x"}, "base": {"size": 8}}
    assert dump_toml(document) == dump_toml(document)


def test_dump_toml_round_trips_through_the_standard_library_parser():
    document = {
        "project": {"format_version": 1, "name": "a project"},
        "enemy": {"434": {"hp": 175, "raw": "00ff", "alias": 'quote"and\\slash'}},
    }
    assert load_toml(dump_toml(document)) == document


def test_dump_toml_refuses_values_it_cannot_emit_unambiguously():
    # A float would serialize differently across platforms and would silently
    # break determinism; refusing is the point.
    with pytest.raises(ProjectFormatError):
        dump_toml({"table": {"value": 1.5}})


def test_dump_toml_does_not_emit_booleans_as_integers():
    assert "true" in dump_toml({"t": {"flag": True}})


def test_written_project_files_end_with_exactly_one_newline(project_dir: Path):
    for path in project_dir.rglob("*.toml"):
        text = path.read_bytes()
        assert text.endswith(b"\n")
        assert not text.endswith(b"\n\n")
        # CRLF would make extraction machine-dependent on Windows.
        assert b"\r\n" not in text


def test_extraction_is_idempotent_over_an_existing_project(tmp_path: Path):
    arguments = {"enemies": [_enemy()], "characters": [_character()]}
    write_project(tmp_path / "p", _meta(), **arguments)
    first = {p.name: p.read_bytes() for p in (tmp_path / "p").rglob("*.toml")}
    write_project(tmp_path / "p", _meta(), **arguments)
    second = {p.name: p.read_bytes() for p in (tmp_path / "p").rglob("*.toml")}
    assert first == second


def test_records_are_ordered_by_identity_not_by_table_position(tmp_path: Path):
    # Enemy type ids are unique but only mostly ascending, so file order and
    # table order genuinely disagree; the file must follow identity.
    write_project(
        tmp_path / "p",
        _meta(),
        enemies=[_enemy(type_id=900), _enemy(type_id=100)],
        characters=[_character()],
    )
    text = (tmp_path / "p" / "enemies" / "enemies.toml").read_text()
    assert text.index("[enemy.100]") < text.index("[enemy.900]")


# --- loading and schema rejection ---------------------------------------


def test_valid_project_loads(project_dir: Path):
    project = read_project(project_dir)
    assert project.meta.format_version == PROJECT_FORMAT_VERSION
    assert project.meta.base_rom_sha256 == CANONICAL_SHA256
    assert len(project.enemies) == 1
    assert len(project.characters) == 1


def test_unsupported_format_version_is_refused(project_dir: Path):
    path = project_dir / "project.toml"
    path.write_text(
        path.read_text().replace(
            f"format_version = {PROJECT_FORMAT_VERSION}",
            f"format_version = {PROJECT_FORMAT_VERSION + 1}",
        )
    )
    with pytest.raises(ProjectLoadError, match="format version"):
        read_project(project_dir)


def test_missing_project_file_is_refused(tmp_path: Path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(ProjectLoadError, match="missing"):
        read_project(tmp_path / "empty")


def test_missing_project_directory_is_refused(tmp_path: Path):
    with pytest.raises(ProjectLoadError, match="does not exist"):
        read_project(tmp_path / "absent")


def test_malformed_toml_is_refused(project_dir: Path):
    (project_dir / "project.toml").write_text("this is not = = toml")
    with pytest.raises(ProjectLoadError, match="invalid TOML"):
        read_project(project_dir)


def test_bad_base_hash_is_refused(project_dir: Path):
    path = project_dir / "project.toml"
    path.write_text(path.read_text().replace(CANONICAL_SHA256, "abc"))
    with pytest.raises(ProjectLoadError, match="64 hexadecimal"):
        read_project(project_dir)


def test_unknown_record_field_is_refused(project_dir: Path):
    path = project_dir / "enemies" / "enemies.toml"
    path.write_text(path.read_text() + "\nunexpected_field = 1\n")
    with pytest.raises(ProjectLoadError, match="unknown fields"):
        read_project(project_dir)


def test_missing_raw_bytes_are_refused(project_dir: Path):
    # Without the opaque bytes a record cannot be rebuilt losslessly, so an
    # absent `raw` has to fail rather than default to zeros.
    path = project_dir / "enemies" / "enemies.toml"
    lines = [l for l in path.read_text().splitlines() if not l.startswith("raw = ")]
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(ProjectValidationError, match="raw"):
        read_project(project_dir)


def test_wrong_length_raw_bytes_are_refused(project_dir: Path):
    path = project_dir / "enemies" / "enemies.toml"
    text = path.read_text()
    start = text.index("raw = ")
    end = text.index("\n", start)
    path.write_text(text[:start] + 'raw = "0011"' + text[end:])
    with pytest.raises(ProjectValidationError, match="exactly"):
        read_project(project_dir)


def test_non_integer_stat_value_is_refused(project_dir: Path):
    path = project_dir / "enemies" / "enemies.toml"
    path.write_text(path.read_text().replace("hp = 175", 'hp = "lots"'))
    with pytest.raises(ProjectValidationError, match="must be an integer"):
        read_project(project_dir)


def test_boolean_is_not_accepted_as_a_stat_value(project_dir: Path):
    # bool subclasses int in Python; `hp = true` must not become hp 1.
    path = project_dir / "enemies" / "enemies.toml"
    path.write_text(path.read_text().replace("hp = 175", "hp = true"))
    with pytest.raises(ProjectValidationError, match="must be an integer"):
        read_project(project_dir)


def test_identity_key_and_type_id_must_agree(project_dir: Path):
    path = project_dir / "enemies" / "enemies.toml"
    path.write_text(path.read_text().replace("type_id = 434", "type_id = 999"))
    with pytest.raises(ProjectValidationError, match="same fact"):
        read_project(project_dir)


def test_empty_record_table_is_refused(project_dir: Path):
    (project_dir / "enemies" / "enemies.toml").write_text("[enemy]\n")
    with pytest.raises(ProjectLoadError, match="no records"):
        read_project(project_dir)


# --- layer boundaries ---------------------------------------------------


def test_codecs_remain_free_of_filesystem_io():
    """`webfoot.formats` must stay a pure byte codec.

    This is one of the two ARCH-TOOL-001 rules that is cheap to keep now and
    impossible to retrofit: if the codec never opens a file, the byte source
    can later be a decomp tree instead of a ROM without touching it.
    """
    source = inspect.getsource(st)
    for forbidden in ("import os", "from pathlib", "open(", "Path("):
        assert forbidden not in source, f"codec must not reference {forbidden!r}"


def test_project_layer_does_not_compute_rom_offsets():
    """The authored format stores semantic values, never addresses.

    The other ARCH-TOOL-001 rule: a project that stored offsets would break
    whenever anything moved and would be meaningless to a different backend.
    """
    from tools.webfoot.project import model

    source = inspect.getsource(model)
    assert "GBA_ROM_BASE" not in source
    assert "file_offset" not in source
