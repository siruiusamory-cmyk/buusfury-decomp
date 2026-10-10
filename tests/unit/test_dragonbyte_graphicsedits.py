"""The object-palette adapter: one reversible document, driven headless.

The Graphics destination edits `graphics/overrides.toml`, and this module proves
the four adapter functions and the journal registration that make that edit
undoable: the round trip through the SDK's own reader and writer, the identity
refusal, and an apply/undo/redo through the ONE journal. It needs no window and
no canonical image: the document layer is text.

The build half, where the recolour becomes a `palette_entry:NNN` byte change in
the emitted image, is proven in `test_dragonbyte_graphics_acceptance.py`, which
is where the image is.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools.dragonbyte import graphicsedits
from tools.dragonbyte.journal import DOCUMENT_ADAPTERS, EditJournal, EditKind
from tools.webfoot.project import (
    GraphicsOverrides,
    ProjectMeta,
    StatProject,
    read_project,
    write_project,
)

SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def _meta(name: str = "test-project") -> ProjectMeta:
    return ProjectMeta(
        format_version=1,
        profile_id="buus_fury_usa_rev0_01c1707f",
        game="buus_fury_usa_rev0_01c1707f",
        base_rom_sha256=SHA,
        base_rom_size=8388608,
        name=name,
    )


def _project(directory: Path, palette: dict[int, tuple[int, int, int]]) -> StatProject:
    """A project on disk carrying one palette document, and nothing else."""
    directory.mkdir(parents=True, exist_ok=True)
    write_project(directory, _meta(), enemies=[], characters=[])
    graphicsedits.write(directory, graphicsedits.AuthoredPalette(_meta(), palette))
    return read_project(directory)


# --- the registration ---------------------------------------------------------


def test_the_journal_registers_the_graphics_target_beside_the_other_four():
    assert graphicsedits.GRAPHICS_TARGET in DOCUMENT_ADAPTERS
    assert graphicsedits.GRAPHICS_TARGET == "graphics"
    for other in ("dialogues", "textstrings", "maps", "data"):
        assert other in DOCUMENT_ADAPTERS
        assert other != graphicsedits.GRAPHICS_TARGET


# --- the round trip -----------------------------------------------------------


def test_the_adapter_round_trips_the_palette_document(tmp_path):
    directory = tmp_path / "project"
    project = _project(directory, {0x001: (255, 0, 255), 0x0FF: (0, 0, 0)})

    payload = graphicsedits.read(project)

    assert payload.entry_count == 2
    assert payload.palette[1] == (255, 0, 255)

    edited = replace(payload, palette={**payload.palette, 0x002: (16, 32, 48)})
    written = tmp_path / "written"
    written.mkdir()
    write_project(written, _meta(), enemies=[], characters=[])
    graphicsedits.write(written, edited)
    again = read_project(written)

    print("\nADAPTER | round trip")
    print(f"  entries written  {len(again.graphics_overrides.palette)}")
    print(f"  entry 002        {again.graphics_overrides.palette[2]}")
    print(f"  document         {(written / 'graphics' / 'overrides.toml').is_file()}")

    assert again.graphics_overrides.palette[2] == (16, 32, 48)
    assert again.graphics_overrides.palette[1] == (255, 0, 255)
    assert (written / "graphics" / "overrides.toml").is_file()


def test_an_emptied_palette_removes_the_document_rather_than_writing_an_empty_table(
    tmp_path,
):
    """`read_project` refuses an empty table, so the writer must unlink instead."""
    directory = tmp_path / "project"
    project = _project(directory, {0x001: (1, 2, 3)})
    document = directory / "graphics" / "overrides.toml"

    assert document.is_file()

    graphicsedits.write(
        directory, replace(graphicsedits.read(project), palette={})
    )

    print("\nADAPTER | emptied document")
    print(f"  exists after write  {document.exists()}")
    print(f"  reloads             {read_project(directory).graphics_overrides.palette}")

    assert not document.exists()
    assert read_project(directory).graphics_overrides.palette == {}


# --- the refusals -------------------------------------------------------------


def test_a_payload_carrying_a_foreign_identity_is_refused(tmp_path):
    project = _project(tmp_path / "mine", {0x001: (1, 2, 3)})
    foreign = graphicsedits.AuthoredPalette(_meta("another-project"), {0x001: (4, 5, 6)})

    with pytest.raises(graphicsedits.GraphicsEditError) as refusal:
        graphicsedits.validate(project, foreign)

    assert "another-project" in str(refusal.value)
    assert "test-project" in str(refusal.value)


@pytest.mark.parametrize(
    "palette",
    [
        {256: (1, 2, 3)},
        {-1: (1, 2, 3)},
        {1: (1, 2)},
        {1: (1, 2, 256)},
        {1: (1, 2, -1)},
        {1: 3},
    ],
)
def test_an_entry_the_document_reader_would_refuse_is_refused_here(tmp_path, palette):
    project = _project(tmp_path / "p", {0x001: (1, 2, 3)})

    with pytest.raises(graphicsedits.GraphicsEditError):
        graphicsedits.validate(
            project, graphicsedits.AuthoredPalette(_meta(), palette)
        )


def test_a_payload_that_is_not_this_documents_type_is_refused(tmp_path):
    project = _project(tmp_path / "p", {0x001: (1, 2, 3)})

    with pytest.raises(graphicsedits.GraphicsEditError):
        graphicsedits.validate(project, {1: (1, 2, 3)})
    with pytest.raises(graphicsedits.GraphicsEditError):
        graphicsedits.install(project, {"palette": {}})


# --- the one journal ----------------------------------------------------------


def test_one_palette_edit_is_one_entry_and_undo_returns_the_project(tmp_path):
    directory = tmp_path / "project"
    project = _project(directory, {0x010: (0, 0, 0)})
    journal = EditJournal()
    journal.bind(f"{project.meta.name}/{project.meta.base_rom_sha256[:16]}/"
                 f"{project.meta.profile_id}")

    after = replace(
        graphicsedits.read(project), palette={0x010: (31, 0, 0), 0x011: (0, 31, 0)}
    )
    edited = journal.apply(
        project,
        kind=EditKind.SEMANTIC,
        target=graphicsedits.GRAPHICS_TARGET,
        after=after,
        reason="palette edit: entry 016",
    )

    print("\nJOURNAL | one palette edit")
    print(f"  depth            {journal.depth}")
    print(f"  dirty            {journal.is_dirty}")
    print(f"  entries          {journal._committed_targets()}")
    print(f"  palette after    {edited.graphics_overrides.palette}")

    assert journal.depth == 1
    assert journal.is_dirty
    assert edited.graphics_overrides.palette[0x010] == (31, 0, 0)

    back = journal.undo(edited)

    print(f"  palette undone   {back.graphics_overrides.palette}")

    assert back.graphics_overrides.palette == {0x010: (0, 0, 0)}
    assert not journal.is_dirty

    again = journal.redo(back)

    assert again.graphics_overrides.palette[0x011] == (0, 31, 0)


def test_saving_a_palette_edit_writes_the_document_and_moves_the_checkpoint(tmp_path):
    directory = tmp_path / "project"
    project = _project(directory, {0x010: (0, 0, 0)})
    journal = EditJournal()
    journal.bind(f"{project.meta.name}/{project.meta.base_rom_sha256[:16]}/"
                 f"{project.meta.profile_id}")
    edited = journal.apply(
        project,
        kind=EditKind.SEMANTIC,
        target=graphicsedits.GRAPHICS_TARGET,
        after=replace(graphicsedits.read(project), palette={0x010: (7, 8, 9)}),
    )

    document = directory / "graphics" / "overrides.toml"
    # Before Save the document on disk still holds the entry's earlier colour:
    # the edit is in memory only until the journal is told to write.
    assert read_project(directory).graphics_overrides.palette == {0x010: (0, 0, 0)}

    journal.save(directory, edited)

    text = document.read_text(encoding="utf-8")
    reloaded = read_project(directory)

    print("\nJOURNAL | save")
    print(f"  clean after save {not journal.is_dirty}")
    print(f"  on disk          {reloaded.graphics_overrides.palette}")

    assert "016" in text
    assert reloaded.graphics_overrides.palette == {0x010: (7, 8, 9)}
    assert not journal.is_dirty


def test_the_adapter_carries_the_derived_pixel_half_through_untouched(tmp_path):
    """The pixel half is derived, so an install must not rebuild it."""
    directory = tmp_path / "project"
    project = _project(directory, {0x010: (0, 0, 0)})
    original = replace(
        project,
        graphics_overrides=GraphicsOverrides(
            palette={0x010: (0, 0, 0)},
            pixels={"derived": "kept"},  # type: ignore[dict-item]
        ),
    )

    edited = graphicsedits.install(
        original, graphicsedits.AuthoredPalette(_meta(), {0x010: (9, 9, 9)})
    )

    print("\nADAPTER | derived half")
    print(f"  palette  {edited.graphics_overrides.palette}")
    print(f"  pixels   {edited.graphics_overrides.pixels}")

    assert edited.graphics_overrides.palette == {0x010: (9, 9, 9)}
    assert edited.graphics_overrides.pixels == {"derived": "kept"}
