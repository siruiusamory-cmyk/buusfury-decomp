"""Portable tests for the authored map layout document.

MAP-TILE-PAINT-001. Synthetic only: no ROM, no extracted assets. These pin the
authoring surface's own rules - the identity keys, the ordinal domain, the
refusals, and the file's absence/removal semantics - so CI (which has no
canonical ROM) still exercises the format a painted cell is stored in. The
ROM-coupled behaviour (resolving an ordinal against a real layer) is pinned in
``tests/integration/test_map_tile_paint_rom.py``.
"""

from __future__ import annotations

import pytest

from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.project import (
    LAYOUT_FILE,
    PROJECT_FORMAT_VERSION,
    LayoutEdits,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    read_project,
    write_layout_edits,
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


# --- the value itself --------------------------------------------------------


def test_key_for_is_the_map_identity_form():
    assert LayoutEdits.key_for(0) == "map:0000"
    assert LayoutEdits.key_for(40) == "map:0040"
    assert LayoutEdits.key_for(452) == "map:0452"


def test_cells_flattens_the_three_level_document():
    layout = LayoutEdits(maps={"map:0040": {1: {0: 2, 3: 1}}, "map:0007": {2: {5: 3}}})
    assert layout.cells() == {(40, 1, 0): 2, (40, 1, 3): 1, (7, 2, 5): 3}
    assert layout.for_map(40) == {1: {0: 2, 3: 1}}
    assert layout.for_map(41) == {}
    assert not layout.is_empty()


def test_an_empty_edit_set_is_empty():
    assert LayoutEdits().is_empty()
    assert LayoutEdits().cells() == {}
    assert LayoutEdits(maps={"map:0000": {}}).is_empty()


def test_the_document_is_keyed_for_numeric_and_deterministic_order():
    """Every level sorts as text in the same order it sorts as a number."""
    layout = LayoutEdits(
        maps={"map:0400": {3: {10: 1, 2: 2}}, "map:0019": {1: {0: 3}}}
    )
    document = layout.to_document()
    assert list(document["layout"]) == ["map:0019", "map:0400"]
    assert list(document["layout"]["map:0400"]) == ["BG3"]
    assert list(document["layout"]["map:0400"]["BG3"]) == ["002", "010"]
    # Same value, same document, whatever order it was built in.
    other = LayoutEdits(maps={"map:0019": {1: {0: 3}}, "map:0400": {3: {2: 2, 10: 1}}})
    assert other.to_document() == document


# --- round trip through disk -------------------------------------------------


def test_a_layout_project_round_trips_through_disk(tmp_path):
    layout = LayoutEdits(maps={"map:0040": {1: {0: 2, 3: 1}}, "map:0007": {2: {5: 3}}})
    write_project(tmp_path, META, enemies=[], characters=[], layout=layout)

    loaded = read_project(tmp_path).layout
    assert loaded.maps == layout.maps
    assert loaded.cells() == layout.cells()


def test_the_written_file_carries_no_address_and_no_offset(tmp_path):
    """The authored file names a map, a layer, a cell and a chunk - nothing else."""
    write_layout_edits(tmp_path, LayoutEdits(maps={"map:0040": {1: {0: 2}}}))
    text = (tmp_path / LAYOUT_FILE).read_text(encoding="utf-8")
    # The map key carries a colon, so the TOML emitter quotes it; the layer and
    # cell keys are bare because they are bare-key safe.
    assert '[layout."map:0040".BG1]' in text
    assert "000 = 2" in text
    assert "0x" not in text
    assert "offset" not in text
    assert "pointer" not in text


def test_a_project_without_a_layout_document_stays_loadable(tmp_path):
    write_project(tmp_path, META, enemies=[], characters=[])
    assert read_project(tmp_path).layout.is_empty()
    assert not (tmp_path / LAYOUT_FILE).exists()


def test_an_empty_layout_writes_no_document(tmp_path):
    path = write_layout_edits(tmp_path, LayoutEdits())
    assert not path.exists()
    # ...and it removes one that was already there, rather than leaving an
    # invalid empty table for the loader to refuse.
    write_layout_edits(tmp_path, LayoutEdits(maps={"map:0001": {0: {0: 1}}}))
    assert (tmp_path / LAYOUT_FILE).is_file()
    write_layout_edits(tmp_path, LayoutEdits())
    assert not (tmp_path / LAYOUT_FILE).exists()


def test_write_project_omits_an_empty_layout(tmp_path):
    write_project(
        tmp_path, META, enemies=[], characters=[], layout=LayoutEdits(maps={})
    )
    assert not (tmp_path / LAYOUT_FILE).exists()


# --- refusals ---------------------------------------------------------------


def _document(layout):
    return {"layout": layout}


@pytest.mark.parametrize(
    "document",
    [
        {},                                   # no [layout] table at all
        {"layout": []},                       # not a table
        {"layout": {}},                       # declares no edits
        {"layout": {"zone:0001": {"BG0": {"000": 1}}}},     # not a map identity
        {"layout": {"map:1": {"BG0": {"000": 1}}}},         # not four digits
        {"layout": {"map:0001": []}},                       # layers not a table
        {"layout": {"map:0001": {"BG0": {}}}},              # declares no cells
        {"layout": {"map:0001": {}}},                       # declares no layers
        {"layout": {"map:0001": {"1": {"000": 1}}}},        # layer not named BGn
        {"layout": {"map:0001": {"BG0": {"one": 1}}}},      # cell not an integer
    ],
)
def test_a_malformed_layout_document_is_refused(document):
    with pytest.raises(ProjectLoadError):
        LayoutEdits.from_document(document, "synthetic")


@pytest.mark.parametrize("bad", [True, 1.0, "1", None])
def test_a_non_integer_ordinal_is_refused(bad):
    document = _document({"map:0001": {"BG0": {"000": bad}}})
    with pytest.raises(ProjectValidationError):
        LayoutEdits.from_document(document, "synthetic")


@pytest.mark.parametrize("bad", [0, -1])
def test_a_non_positive_ordinal_is_refused(bad):
    """Ordinals are 1-based: 0 is not "the first chunk", it is nothing."""
    document = _document({"map:0001": {"BG0": {"000": bad}}})
    with pytest.raises(ProjectValidationError):
        LayoutEdits.from_document(document, "synthetic")


def test_a_layer_slot_outside_the_hardware_count_is_refused():
    """A file naming BG4 must fail loudly, not be silently dropped from a build."""
    document = _document({"map:0001": {"BG4": {"000": 1}}})
    with pytest.raises(ProjectValidationError, match="outside BG0"):
        LayoutEdits.from_document(document, "synthetic")


def test_the_declared_layer_count_is_the_engine_s():
    """`_LAYER_SLOT_COUNT` and the format layer's four slots cannot drift."""
    from tools.webfoot.project import model as project_model

    assert project_model._LAYER_SLOT_COUNT == len(mg.ROOT_LAYER_SLOTS)


def test_a_malformed_file_on_disk_is_an_error_not_an_empty_edit_set(tmp_path):
    write_project(tmp_path, META, enemies=[], characters=[])
    (tmp_path / "maps").mkdir(parents=True, exist_ok=True)
    (tmp_path / LAYOUT_FILE).write_text("[layout]\n", encoding="utf-8", newline="\n")
    with pytest.raises(ProjectLoadError, match="declares no edits"):
        read_project(tmp_path)


def test_an_unknown_field_in_a_cell_table_is_refused(tmp_path):
    """The cell table is a mapping of index to ordinal, so a nested table is wrong."""
    write_project(tmp_path, META, enemies=[], characters=[])
    (tmp_path / "maps").mkdir(parents=True, exist_ok=True)
    (tmp_path / LAYOUT_FILE).write_text(
        '[layout."map:0001".BG0]\n000 = { chunk = 1 }\n',
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ProjectValidationError):
        read_project(tmp_path)
