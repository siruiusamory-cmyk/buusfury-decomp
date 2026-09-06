"""Portable tests for the authored map surface. Synthetic values only."""

from __future__ import annotations

import pytest

from tools.webfoot.project import (
    PROJECT_FORMAT_VERSION,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    read_project,
    write_project,
)


META = ProjectMeta(
    format_version=PROJECT_FORMAT_VERSION,
    profile_id="synthetic_exact",
    game="synthetic",
    base_rom_sha256="0" * 64,
    base_rom_size=0x100,
    name="synthetic",
)


def map_document(index: int, *, slots: bytes | None = None, **overrides):
    document = {
        "index": index,
        "key": f"map:{index:04d}",
        "raw": bytes(range(0x38)),
        "slots": slots,
        "shape": None if slots is None else "OPAQUE",
        "zone": 11,
        "area": 1,
        "variation": 4,
        "flags": 0,
        "music_id": 15,
    }
    document.update(overrides)
    return document


def write(tmp_path, maps):
    write_project(tmp_path, META, enemies=[], characters=[], maps=maps)
    return tmp_path


def test_a_map_project_round_trips_through_disk(tmp_path):
    slots = bytes.fromhex("0300020008010008")
    root = write(tmp_path, [map_document(39, slots=slots), map_document(1)])

    project = read_project(root)

    assert sorted(project.maps) == [1, 39]
    assert project.maps[39]["music_id"] == 15
    assert project.maps[39]["raw"] == bytes(range(0x38))
    assert project.maps[39]["slots"] == slots
    assert project.maps[39]["shape"] == "OPAQUE"
    assert "slots" not in project.maps[1]


def test_extraction_is_byte_identical_for_the_same_input(tmp_path):
    maps = [map_document(2), map_document(1, slots=b"\x00" * 8)]
    first = write(tmp_path / "a", maps).joinpath("maps", "maps.toml").read_bytes()
    second = write(tmp_path / "b", maps).joinpath("maps", "maps.toml").read_bytes()
    assert first == second


def test_maps_are_ordered_by_index_not_by_input_order(tmp_path):
    root = write(tmp_path, [map_document(10), map_document(2), map_document(1)])
    text = (root / "maps" / "maps.toml").read_text(encoding="utf-8")
    assert text.index("map:0001") < text.index("map:0002") < text.index("map:0010")


def test_a_project_without_maps_stays_loadable(tmp_path):
    write_project(tmp_path, META, enemies=[], characters=[])
    assert read_project(tmp_path).maps == {}
    assert not (tmp_path / "maps" / "maps.toml").exists()


def test_a_malformed_identity_key_is_refused(tmp_path):
    root = write(tmp_path, [map_document(1)])
    path = root / "maps" / "maps.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("map:0001", "zone:0001"),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectLoadError, match="not a valid map identity"):
        read_project(root)


def test_an_unknown_field_is_refused(tmp_path):
    root = write(tmp_path, [map_document(1)])
    path = root / "maps" / "maps.toml"
    path.write_text(
        path.read_text(encoding="utf-8") + "invented = 1\n",
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectLoadError, match="unknown fields"):
        read_project(root)


def test_a_non_integer_field_is_refused(tmp_path):
    root = write(tmp_path, [map_document(1)])
    path = root / "maps" / "maps.toml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("music_id = 15", "music_id = true"),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectValidationError, match="must be an integer"):
        read_project(root)


def test_invalid_hex_is_refused(tmp_path):
    root = write(tmp_path, [map_document(1)])
    path = root / "maps" / "maps.toml"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace('raw = "00', 'raw = "zz', 1), encoding="utf-8", newline="\n"
    )
    with pytest.raises(ProjectValidationError, match="not valid hex"):
        read_project(root)


def test_slots_without_a_shape_is_refused(tmp_path):
    root = write(tmp_path, [map_document(1, slots=b"\x00" * 8)])
    path = root / "maps" / "maps.toml"
    path.write_text(
        "\n".join(
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("shape")
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectValidationError, match="both 'slots' and 'shape'"):
        read_project(root)


def test_an_empty_map_table_is_refused(tmp_path):
    root = write(tmp_path, [map_document(1)])
    (root / "maps" / "maps.toml").write_text(
        "[map]\n", encoding="utf-8", newline="\n"
    )
    with pytest.raises(ProjectLoadError, match="declares no records"):
        read_project(root)
