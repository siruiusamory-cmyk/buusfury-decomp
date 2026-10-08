"""AUTHORED-WORK-SAFETY-001 N-08: a project document is replaced whole or not at all.

Every production writer of a project document goes through
`tools.webfoot.project.atomic.replace_document`, so an interrupted or failed
write leaves the previous document byte-identical instead of truncated. These
tests induce the failure at the two places it can happen - before the replace
and during it - and prove the old bytes survive, then hold the census in place
so a writer cannot quietly return to a raw `write_text`.
"""

from __future__ import annotations

import inspect
import os
from pathlib import Path

import pytest

from tools.webfoot import build as build_sdk
from tools.webfoot.project import atomic, model, placements
from tools.webfoot.project.model import ProjectMeta


def _meta() -> ProjectMeta:
    return ProjectMeta(
        format_version=1,
        profile_id="synthetic_exact",
        game="synthetic",
        base_rom_sha256="0" * 64,
        base_rom_size=0x100,
        name="atomic",
    )


def _stray_temporaries(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if "webfoot-partial" in path.name]


def test_an_unchanged_document_is_rewritten_byte_identically(tmp_path: Path):
    path = tmp_path / "document.toml"
    text = "[table]\nkey = 1\n"
    atomic.replace_document(path, text)
    first = path.read_bytes()
    atomic.replace_document(path, text)

    assert path.read_bytes() == first == b"[table]\nkey = 1\n"


def test_a_failure_before_the_replace_leaves_the_old_document(tmp_path: Path, monkeypatch):
    path = tmp_path / "document.toml"
    path.write_bytes(b"old\n")

    def boom(_fd):
        raise OSError("induced fsync failure")

    monkeypatch.setattr(atomic.os, "fsync", boom)

    with pytest.raises(OSError):
        atomic.replace_document(path, "new\n")

    assert path.read_bytes() == b"old\n"
    assert _stray_temporaries(tmp_path) == []


def test_a_failure_during_the_replace_leaves_the_old_document(tmp_path: Path, monkeypatch):
    path = tmp_path / "document.toml"
    path.write_bytes(b"old\n")

    def boom(*_args, **_kwargs):
        raise PermissionError("induced replace failure")

    monkeypatch.setattr(atomic.os, "replace", boom)

    with pytest.raises(PermissionError):
        atomic.replace_document(path, "new\n")

    assert path.read_bytes() == b"old\n"
    assert _stray_temporaries(tmp_path) == []


def test_a_narrow_writer_leaves_the_old_document_on_a_failed_write(
    tmp_path: Path, monkeypatch
):
    """The representative narrow writer, not just the helper in isolation."""
    path = model.write_dialogue_replacements(tmp_path, {"intro": "first"})
    before = path.read_bytes()

    def boom(_fd):
        raise OSError("induced fsync failure")

    monkeypatch.setattr(atomic.os, "fsync", boom)

    with pytest.raises(OSError):
        model.write_dialogue_replacements(tmp_path, {"intro": "second"})

    assert path.read_bytes() == before
    assert _stray_temporaries(tmp_path) == []


def test_the_full_writer_leaves_the_old_document_on_a_failed_write(
    tmp_path: Path, monkeypatch
):
    model.write_project(tmp_path, _meta(), enemies=[], characters=[])
    path = tmp_path / "project.toml"
    before = path.read_bytes()

    def boom(_fd):
        raise OSError("induced fsync failure")

    monkeypatch.setattr(atomic.os, "fsync", boom)

    with pytest.raises(OSError):
        model.write_project(tmp_path, _meta(), enemies=[], characters=[])

    assert path.read_bytes() == before
    assert _stray_temporaries(tmp_path) == []


def test_a_successful_write_leaves_no_temporary_behind(tmp_path: Path):
    model.write_project(tmp_path, _meta(), enemies=[], characters=[])
    model.write_dialogue_replacements(tmp_path, {"intro": "text"})

    assert _stray_temporaries(tmp_path) == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits are not meaningful here")
def test_an_existing_document_keeps_its_permissions(tmp_path: Path):
    path = tmp_path / "document.toml"
    atomic.replace_document(path, "text\n")
    os.chmod(path, 0o640)

    atomic.replace_document(path, "other\n")

    assert (path.stat().st_mode & 0o777) == 0o640


def test_a_missing_parent_directory_is_created(tmp_path: Path):
    path = tmp_path / "nested" / "deeper" / "document.toml"
    atomic.replace_document(path, "text\n")

    assert path.read_bytes() == b"text\n"


def test_a_parent_that_is_a_file_fails_closed(tmp_path: Path):
    blocked = tmp_path / "blocked"
    blocked.write_bytes(b"not a directory")

    with pytest.raises(OSError):
        atomic.replace_document(blocked / "document.toml", "text\n")

    assert blocked.read_bytes() == b"not a directory"


def test_an_orphan_temporary_does_not_stop_a_load_or_a_write(tmp_path: Path):
    model.write_project(tmp_path, _meta(), enemies=[], characters=[])
    orphan = tmp_path / ".project.toml.999-deadbeef.webfoot-partial"
    orphan.write_bytes(b"interrupted\n")

    assert model.read_project(tmp_path).meta.profile_id == "synthetic_exact"
    model.write_project(tmp_path, _meta(), enemies=[], characters=[])
    assert orphan.exists(), "the sweep is deliberately absent; a peer's temp is left alone"


# --- the census: no production project-document writer may go back ----------

_MODEL_WRITERS = (
    "write_project",
    "write_dialogue_replacements",
    "write_graphics_overrides",
    "write_layout_edits",
    "write_authored_chunks",
    "write_map_structure",
    "write_transition_edits",
    "write_transition_creations",
    "write_authored_sprites",
    "write_authored_appearances",
    "write_authored_maps",
)
_PLACEMENTS_WRITERS = (
    "clone_placement",
    "remove_authored_placement",
    "set_project_placement_position",
)


@pytest.mark.parametrize("name", _MODEL_WRITERS)
def test_a_model_writer_still_uses_the_atomic_authority(name: str):
    source = inspect.getsource(getattr(model, name))

    assert "replace_document(" in source
    assert "write_text(" not in source


@pytest.mark.parametrize("name", _PLACEMENTS_WRITERS)
def test_a_placement_writer_still_uses_the_atomic_authority(name: str):
    source = inspect.getsource(getattr(placements, name))

    assert "replace_document(" in source
    assert "write_text(" not in source


def test_the_extractor_still_uses_the_atomic_authority():
    source = inspect.getsource(build_sdk.extract_project)

    assert "write_text(" not in source
    assert "replace_document(" in source
