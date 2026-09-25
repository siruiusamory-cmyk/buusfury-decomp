"""Portable tests for the authored-chunk project documents.

MAP-CHUNK-AUTHORING-001. Synthetic only: no ROM, no extracted assets. These pin
the authoring surface's own rules - the identity and template grammars, the cell
key form, the refusals, the absence/removal semantics, and the two value forms an
authored layout cell may now hold - so CI (which has no canonical ROM) still
exercises the format an authored chunk is stored in. The ROM-coupled behaviour
(resolving a template and materializing a body) is pinned in
``tests/integration/test_map_chunk_authoring_rom.py``.
"""

from __future__ import annotations

import pytest

from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.project import (
    CHUNK_FILE,
    LAYOUT_FILE,
    PROJECT_FORMAT_VERSION,
    AuthoredChunk,
    AuthoredChunkEntry,
    AuthoredChunks,
    LayoutEdits,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    dump_toml,
    load_toml,
    read_project,
    write_authored_chunks,
    write_project,
)
from tools.webfoot.project import model as project_model

META = ProjectMeta(
    format_version=PROJECT_FORMAT_VERSION,
    profile_id="synthetic_exact",
    game="synthetic",
    base_rom_sha256="0" * 64,
    base_rom_size=0x100,
    name="synthetic",
)


def _chunk(identity: str = "chunk:grass-sign") -> AuthoredChunk:
    return AuthoredChunk(
        identity=identity,
        template="map:0040/layer:1/chunk:1",
        entries=(
            AuthoredChunkEntry(row=2, column=3, prior=0x0000, entry=0x0015),
            AuthoredChunkEntry(row=2, column=4, prior=0x0020, entry=0x0015),
        ),
    )


# --- the plane geometry is the format layer's, not a second copy --------------


def test_the_chunk_side_and_entry_width_are_the_format_layers_numbers():
    """The project package states the hardware locally and must not drift.

    `project/model.py` deliberately does not import a module that opens ROMs, so
    it carries its own constants. This is the pin that keeps them equal to the
    ones the codec actually decodes with.
    """
    assert project_model._CHUNK_SIDE == mg.CHUNK_SIDE_TILES
    assert project_model._CHUNK_ENTRY_MAX == 0xFFFF
    assert mg.CHUNK_ENTRY_COUNT == project_model._CHUNK_SIDE * project_model._CHUNK_SIDE


# --- identity and template grammars ------------------------------------------


def test_a_chunk_identity_round_trips_through_the_document():
    chunk = _chunk()
    document = AuthoredChunks(chunks={chunk.identity: chunk}).to_document()
    assert document == {
        "chunk": {
            "chunk:grass-sign": {
                "template": "map:0040/layer:1/chunk:1",
                "entries": {"02,03": [0, 21], "02,04": [32, 21]},
            }
        }
    }
    assert AuthoredChunks.from_document(document, "here").chunks == {chunk.identity: chunk}


def test_the_document_carries_no_address_and_no_offset():
    """The identity architecture's central rule, asserted rather than assumed."""
    text = dump_toml(AuthoredChunks(chunks={"chunk:grass-sign": _chunk()}).to_document())
    assert "0x" not in text
    assert "offset" not in text
    assert "0829" not in text


@pytest.mark.parametrize(
    "identity",
    ["grass-sign", "chunk:Grass", "chunk:", "chunk:9grass", "chunk:has space", "chunk:a" * 40],
)
def test_a_malformed_chunk_identity_is_refused(identity):
    with pytest.raises(ProjectValidationError):
        AuthoredChunk(identity=identity, template="map:0040/layer:1/chunk:1",
                      entries=(AuthoredChunkEntry(0, 0, 0, 1),))


@pytest.mark.parametrize(
    "template",
    ["map:40/layer:1/chunk:1", "map:0040/BG1/chunk:1", "map:0040/layer:9/chunk:1",
     "0040/1/1", "", "map:0040/layer:1/chunk:0x1"],
)
def test_a_malformed_template_is_refused(template):
    with pytest.raises(ProjectValidationError):
        AuthoredChunk(identity="chunk:x", template=template,
                      entries=(AuthoredChunkEntry(0, 0, 0, 1),))


def test_a_chunk_may_not_edit_one_cell_twice():
    with pytest.raises(ProjectValidationError, match="twice"):
        AuthoredChunk(
            identity="chunk:x",
            template="map:0040/layer:1/chunk:1",
            entries=(AuthoredChunkEntry(1, 1, 0, 1), AuthoredChunkEntry(1, 1, 0, 2)),
        )


@pytest.mark.parametrize(
    "row,column", [(-1, 0), (0, -1), (mg.CHUNK_SIDE_TILES, 0), (0, mg.CHUNK_SIDE_TILES)]
)
def test_a_cell_outside_the_plane_is_refused(row, column):
    with pytest.raises(ProjectValidationError, match="plane"):
        AuthoredChunk(identity="chunk:x", template="map:0040/layer:1/chunk:1",
                      entries=(AuthoredChunkEntry(row, column, 0, 1),))


@pytest.mark.parametrize("prior,entry", [(0x10000, 1), (1, -1), ("1", 1), (1, None)])
def test_a_non_entry_value_is_refused(prior, entry):
    with pytest.raises(ProjectValidationError, match="16-bit screen entry"):
        AuthoredChunk(identity="chunk:x", template="map:0040/layer:1/chunk:1",
                      entries=(AuthoredChunkEntry(0, 0, prior, entry),))


def test_a_chunk_that_edits_nothing_is_refused_by_the_document_shape():
    """A chunk with no authored cell would be an alias, not a new resource.

    The document type does not forbid the empty tuple outright - the ROM-side
    composer does, because that is where the template is known - but `from_document`
    refuses a stored chunk with no entries, which is the one form a hand-edited
    project could produce.
    """
    with pytest.raises(ProjectLoadError, match="declares no entries"):
        AuthoredChunks.from_document(
            {"chunk": {"chunk:x": {"template": "map:0040/layer:1/chunk:1", "entries": {}}}},
            "here",
        )


# --- the document's own refusals ---------------------------------------------


def test_an_unknown_key_is_refused_rather_than_ignored():
    with pytest.raises(ProjectLoadError, match="unknown key"):
        AuthoredChunks.from_document(
            {
                "chunk": {
                    "chunk:x": {
                        "template": "map:0040/layer:1/chunk:1",
                        "entries": {"00,00": [0, 1]},
                        "address": 1234,
                    }
                }
            },
            "here",
        )


@pytest.mark.parametrize("key", ["0,0", "000,000", "aa,bb", "00-00"])
def test_a_cell_key_must_be_a_zero_padded_pair(key):
    with pytest.raises(ProjectLoadError, match="row,column"):
        AuthoredChunks.from_document(
            {"chunk": {"chunk:x": {"template": "map:0040/layer:1/chunk:1",
                                   "entries": {key: [0, 1]}}}},
            "here",
        )


def test_a_cell_value_must_be_a_prior_entry_pair():
    with pytest.raises(ProjectLoadError, match=r"\[prior, entry\]"):
        AuthoredChunks.from_document(
            {"chunk": {"chunk:x": {"template": "map:0040/layer:1/chunk:1",
                                   "entries": {"00,00": [0, 1, 2]}}}},
            "here",
        )


def test_an_empty_chunk_table_is_refused_as_a_file():
    with pytest.raises(ProjectLoadError, match="declares no authored chunks"):
        AuthoredChunks.from_document({"chunk": {}}, "here")


def test_absence_is_legal_and_removal_deletes_the_file(tmp_path):
    assert AuthoredChunks().is_empty()
    written = write_authored_chunks(tmp_path, AuthoredChunks())
    assert not written.exists()
    path = write_authored_chunks(tmp_path, AuthoredChunks(chunks={"chunk:x": _chunk("chunk:x")}))
    assert path.is_file() and path.name == CHUNK_FILE.name
    write_authored_chunks(tmp_path, AuthoredChunks())
    assert not path.exists()


def test_the_written_file_is_lf_and_ends_with_one_newline(tmp_path):
    payload = dump_toml(AuthoredChunks(chunks={"chunk:x": _chunk("chunk:x")}).to_document())
    assert payload.endswith("\n") and not payload.endswith("\n\n")
    assert "\r" not in payload
    # and it is TOML the reader accepts back
    assert load_toml(payload)["chunk"]["chunk:x"]["template"] == "map:0040/layer:1/chunk:1"


# --- the layout cell's second value form -------------------------------------


def test_an_authored_layout_cell_may_hold_a_chunk_identity():
    edits = LayoutEdits(maps={"map:0040": {1: {0: "chunk:grass-sign", 3: 2}}})
    document = edits.to_document()
    assert document == {
        "layout": {"map:0040": {"BG1": {"000": "chunk:grass-sign", "003": 2}}}
    }
    assert LayoutEdits.from_document(document, "here").maps == edits.maps
    assert edits.cells() == {(40, 1, 0): "chunk:grass-sign", (40, 1, 3): 2}


@pytest.mark.parametrize("value", ["grass", "chunk:", "chunk:Bad", "Chunk:x", 0, -1, 1.5])
def test_a_layout_cell_value_that_is_neither_form_is_refused(value):
    with pytest.raises(ProjectValidationError):
        LayoutEdits.from_document({"layout": {"map:0040": {"BG1": {"000": value}}}}, "here")


def test_a_layout_cell_naming_an_undeclared_chunk_is_refused_by_read_project(tmp_path):
    """The cross-document check: a reference must resolve inside the project.

    `LayoutEdits` cannot see the chunk table, so `read_project` is the one place
    both documents are in hand. Without this, the project would load and the
    failure would surface at build time as an image problem rather than a project
    problem.
    """
    write_project(tmp_path, META, enemies=[], characters=[])
    (tmp_path / LAYOUT_FILE.parent).mkdir(parents=True, exist_ok=True)
    (tmp_path / LAYOUT_FILE).write_text(
        dump_toml(LayoutEdits(maps={"map:0040": {1: {0: "chunk:ghost"}}}).to_document()),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectValidationError, match="chunk:ghost"):
        read_project(tmp_path)


def test_a_declared_chunk_makes_the_reference_loadable(tmp_path):
    write_project(tmp_path, META, enemies=[], characters=[],
                  chunks=AuthoredChunks(chunks={"chunk:grass-sign": _chunk()}))
    (tmp_path / LAYOUT_FILE.parent).mkdir(parents=True, exist_ok=True)
    (tmp_path / LAYOUT_FILE).write_text(
        dump_toml(
            LayoutEdits(maps={"map:0040": {1: {0: "chunk:grass-sign"}}}).to_document()
        ),
        encoding="utf-8",
        newline="\n",
    )
    project = read_project(tmp_path)
    assert project.chunks.identities() == ("chunk:grass-sign",)
    assert project.layout.cells() == {(40, 1, 0): "chunk:grass-sign"}


def test_a_project_extracted_before_this_capability_still_loads(tmp_path):
    """The additive-family rule: absence means "authors none", not "broken"."""
    write_project(tmp_path, META, enemies=[], characters=[])
    project = read_project(tmp_path)
    assert project.chunks.is_empty()
    assert project.layout.is_empty()
    assert not (tmp_path / CHUNK_FILE).exists()
