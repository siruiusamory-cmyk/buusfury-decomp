"""`maps/structure.toml`: the authored structural document.

MAP-RESIZE-AND-LAYERS-001. Portable and image-free: this file owns the authored
text form, so nothing here opens a ROM. The structural *semantics* against a real
image live in `test_map_resize.py` and in the ROM-gated integration module.
"""

from __future__ import annotations

import pathlib

import pytest

from tools.webfoot.formats import map_graphics as mg
from tools.webfoot.project import model as pm
from tools.webfoot.project.format import ProjectFormatError


def _resize(**overrides):
    values = {
        "map_index": 40,
        "layer_slot": 1,
        "columns": 3,
        "rows": 2,
        "fill": 2,
    }
    values.update(overrides)
    return pm.LayerResize(**values)


def _layer(**overrides):
    values = {
        "identity": "layer:overlay",
        "map_index": 39,
        "layer_slot": 0,
        "template": "map:0039/BG1",
        "columns": 3,
        "rows": 2,
        "fill": 1,
    }
    values.update(overrides)
    return pm.AuthoredLayer(**values)


# --- identity forms ----------------------------------------------------------

def test_the_document_constants_agree_with_the_binary_authority():
    """The authored surface states the engine's numbers locally and is pinned.

    This package must not import a module that opens ROMs, so the grid ceiling and
    the slot count are stated here; the test is what keeps the two from drifting.
    """
    assert pm._MAX_GRID_SIDE == mg.MAX_LAYER_GRID_SIDE
    assert pm._LAYER_SLOT_COUNT == len(mg.ROOT_LAYER_SLOTS)


def test_a_resize_key_round_trips_through_its_map_and_slot():
    resize = _resize()
    assert resize.key == "map:0040/BG1"
    assert pm.LayerResize.key_for(40, 1) == resize.key
    parsed = pm.LayerResize.from_document(
        resize.key, resize.to_document(), "test"
    )
    assert parsed == resize


@pytest.mark.parametrize(
    "key",
    ["map:40/BG1", "map:0040/BG", "map:0040/BG4", "map:0040/layer:1", "BG1", ""],
)
def test_a_resize_key_that_is_not_a_layer_identity_is_refused(key):
    with pytest.raises(pm.ProjectLoadError):
        pm.LayerResize.from_document(key, {"columns": 3, "rows": 2, "fill": 1}, "t")


@pytest.mark.parametrize("name", ["", "Overlay", "1overlay", "has space", "a" * 65, 7])
def test_an_invalid_layer_identity_is_refused(name):
    with pytest.raises((pm.ProjectError, pm.ProjectValidationError)):
        _layer(identity=name)


def test_a_layer_document_round_trips():
    layer = _layer()
    document = layer.to_document()
    assert document["map"] == "map:0039"
    assert document["slot"] == 0
    assert pm.AuthoredLayer.from_document(layer.identity, document, "t") == layer


def test_a_layer_template_must_be_another_slot_on_its_own_map():
    """An authored layer's ordinals resolve through its own map's character block.

    A template naming another map would compose a body whose ordinals mean
    something else there, and a template naming its own slot would copy the record
    it is replacing.
    """
    with pytest.raises(pm.ProjectValidationError, match="another map"):
        _layer(template="map:0040/BG1")
    with pytest.raises(pm.ProjectValidationError, match="the slot it would activate"):
        _layer(template="map:0039/BG0")


# --- dimensions --------------------------------------------------------------

@pytest.mark.parametrize("columns", [0, -1, pm._MAX_GRID_SIDE + 1, "3", None, 2.0])
def test_malformed_persisted_dimensions_are_refused(columns):
    with pytest.raises((pm.ProjectError, pm.ProjectValidationError)):
        pm.LayerResize.from_document(
            "map:0040/BG1",
            {"columns": columns, "rows": 2, "fill": 1},
            "t",
        )


def test_a_dimension_at_the_supported_ceiling_is_accepted():
    resize = pm.LayerResize.from_document(
        "map:0040/BG1",
        {"columns": pm._MAX_GRID_SIDE, "rows": 1, "fill": 1},
        "t",
    )
    assert resize.columns == pm._MAX_GRID_SIDE


def test_an_unknown_key_in_a_resize_is_refused():
    """A file that declares a field this reader does not implement would otherwise
    look valid and silently drop the author's intent."""
    with pytest.raises(pm.ProjectLoadError, match="unknown key"):
        pm.LayerResize.from_document(
            "map:0040/BG1", {"columns": 3, "rows": 2, "fill": 1, "anchor": "top"}, "t"
        )


def test_a_missing_key_in_an_authored_layer_is_refused():
    document = _layer().to_document()
    del document["template"]
    with pytest.raises(pm.ProjectLoadError, match="missing key"):
        pm.AuthoredLayer.from_document("layer:overlay", document, "t")


# --- initialization value forms ---------------------------------------------

def test_the_initialization_accepts_the_same_two_forms_a_layout_cell_does():
    ordinal = pm.LayerResize.from_document(
        "map:0040/BG1", {"columns": 2, "rows": 1, "fill": 4}, "t"
    )
    authored = pm.LayerResize.from_document(
        "map:0040/BG1", {"columns": 2, "rows": 1, "fill": "chunk:pad"}, "t"
    )
    assert ordinal.fill == 4
    assert authored.fill == "chunk:pad"


@pytest.mark.parametrize("fill", [0, -3, "pad", "chunk:Pad", 1.5, None])
def test_an_initialization_that_is_neither_form_is_refused(fill):
    with pytest.raises((pm.ProjectError, pm.ProjectValidationError)):
        pm.LayerResize.from_document(
            "map:0040/BG1", {"columns": 2, "rows": 1, "fill": fill}, "t"
        )


# --- the whole document ------------------------------------------------------

def _document():
    return pm.MapStructure(
        resizes={_resize().key: _resize()},
        layers={_layer().identity: _layer()},
    )


def test_the_document_round_trips_and_is_sorted():
    structure = _document()
    document = structure.to_document()
    assert set(document) == {"resize", "layer"}
    assert pm.MapStructure.from_document(document, "t") == structure


def test_an_empty_document_is_reported_empty():
    assert pm.MapStructure().is_empty()
    assert not _document().is_empty()


def test_an_unknown_top_level_key_is_refused():
    document = _document().to_document()
    document["warp"] = {"map:0040/BG1": {}}
    with pytest.raises(pm.ProjectLoadError, match="unknown top-level key"):
        pm.MapStructure.from_document(document, "t")


@pytest.mark.parametrize("document", [{}, {"resize": {}}, {"layer": {}}, []])
def test_a_present_but_empty_document_is_refused(document):
    """"I meant to author this and did not" is a mistake worth catching.

    It matches `LayoutEdits` and `AuthoredChunks`, which refuse an empty table for
    the same reason.
    """
    with pytest.raises(pm.ProjectLoadError):
        pm.MapStructure.from_document(document, "t")


def test_a_slot_claimed_by_two_layers_is_refused():
    """One slot, one owner: two records of the same kind claiming it would each
    look valid alone.

    A `[layer]` and a `[resize]` together on one slot are the other thing - a
    created layer and the grid it was grown to - and are covered as an accepted
    pair by `test_a_created_layer_grown_by_a_resize_round_trips`.
    """
    document = {
        "layer": {
            "layer:overlay": {
                "map": "map:0039",
                "slot": 0,
                "template": "map:0039/BG1",
                "columns": 3,
                "rows": 2,
                "fill": 1,
            },
            "layer:second": {
                "map": "map:0039",
                "slot": 0,
                "template": "map:0039/BG1",
                "columns": 2,
                "rows": 1,
                "fill": 1,
            },
        },
    }
    with pytest.raises(pm.ProjectValidationError, match="claimed by both"):
        pm.MapStructure.from_document(document, "t")


def test_the_document_reports_every_slot_it_owns():
    structure = _document()
    assert structure.structural_slots() == frozenset({(40, 1), (39, 0)})
    assert structure.resize_for(40, 1).columns == 3
    assert structure.resize_for(40, 2) is None
    assert structure.layer_at(39, 0).identity == "layer:overlay"
    assert structure.layer_at(39, 1) is None
    assert structure.layer("layer:overlay") == _layer()


# --- a created layer and the resize that grows it ----------------------------
#
# MAP-RESIZE-AND-LAYERS-001 gap closure. A `[layer]` entry declares the grid the
# layer is CREATED at; a `[resize]` entry on the same `map:NNNN/BGn` key declares
# the grid it is GROWN to. Both may exist for one slot and only in that direction,
# which is what makes "grow a layer the project itself created" expressible at all.

def _pair(columns: int = 2, rows: int = 1, fill=3) -> pm.MapStructure:
    """One slot's worth of structure: a 1x1 created layer grown to ``columns x rows``."""
    layer = _layer(columns=1, rows=1, fill=1)
    resize = _resize(map_index=39, layer_slot=0, columns=columns, rows=rows, fill=fill)
    return pm.MapStructure(
        resizes={resize.key: resize}, layers={layer.identity: layer}
    )


def test_a_created_layer_grown_by_a_resize_round_trips():
    """Both tables, one slot, and the two are different facts about it."""
    structure = _pair()
    document = structure.to_document()
    assert set(document) == {"resize", "layer"}
    assert document["resize"]["map:0039/BG0"] == {"columns": 2, "rows": 1, "fill": 3}
    assert document["layer"]["layer:overlay"] == {
        "map": "map:0039",
        "slot": 0,
        "template": "map:0039/BG1",
        "columns": 1,
        "rows": 1,
        "fill": 1,
    }
    assert pm.MapStructure.from_document(document, "t") == structure
    assert structure.structural_slots() == frozenset({(39, 0)})
    assert structure.layer_at(39, 0).columns == 1
    assert structure.resize_for(39, 0).columns == 2


def test_a_pair_that_does_not_grow_the_authored_layer_is_refused():
    """The pair states a growth, so a shrink - or a no-op - is refused.

    The authored grid is the shrink floor: the `[layer]` entry is the grid the
    author's cells live in, so a resize smaller than it would silently drop them.
    """
    # unchanged: 1x1 grown to 1x1 states no growth at all
    with pytest.raises(pm.ProjectValidationError, match="GROWN to"):
        _pair(columns=1, rows=1)
    # narrower on one axis, from a 2x2 created layer
    layer = _layer(columns=2, rows=2, fill=1)
    narrow = _resize(map_index=39, layer_slot=0, columns=1, rows=2, fill=1)
    with pytest.raises(pm.ProjectValidationError, match="smaller on neither"):
        pm.MapStructure(resizes={narrow.key: narrow}, layers={layer.identity: layer})
    # shorter on one axis, from the same 2x2 created layer
    short = _resize(map_index=39, layer_slot=0, columns=3, rows=1, fill=1)
    with pytest.raises(pm.ProjectValidationError, match="smaller on neither"):
        pm.MapStructure(resizes={short.key: short}, layers={layer.identity: layer})
    # and one genuine growth in either direction is accepted
    assert _pair(columns=2, rows=1).resize_for(39, 0).columns == 2
    assert _pair(columns=1, rows=2).resize_for(39, 0).rows == 2


def test_a_slot_claimed_by_two_resizes_is_refused():
    """Two resizes for one slot are the same double claim as two layers.

    A `[resize]` is keyed by the slot it changes, so two entries for one slot are
    the SAME key in a TOML table and the text form cannot hold them at all - the
    duplicate-key refusal below is that half. The slot-level claim is refused on
    the structure itself, which is what keeps a caller from assembling a document
    whose two resize entries resolve to one slot.
    """
    first = _resize(map_index=39, layer_slot=0, columns=2, rows=1, fill=1)
    second = _resize(map_index=39, layer_slot=0, columns=3, rows=1, fill=1)
    with pytest.raises(pm.ProjectValidationError, match="claimed by both"):
        pm.MapStructure(resizes={first.key: first, "map:0039/BG0 (again)": second})
    assert pm.MapStructure(resizes={first.key: first}).resize_for(39, 0) == first


def test_a_duplicate_resize_key_on_disk_is_refused(tmp_path):
    """A hand-written file cannot state two resizes for one slot either."""
    path = pathlib.Path(tmp_path) / "structure.toml"
    path.write_text(
        '[resize."map:0039/BG0"]\ncolumns = 2\nrows = 1\nfill = 1\n'
        "\n"
        '[resize."map:0039/BG0"]\ncolumns = 3\nrows = 1\nfill = 1\n',
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(pm.ProjectLoadError):
        pm._read_structure(path)


# --- the file on disk --------------------------------------------------------

def test_a_project_without_the_file_loads_with_no_structure(tmp_path):
    """Absence means "this project authors no structure", not "broken"."""
    from tools.webfoot.project import write_project
    from tools.webfoot.project.model import ProjectMeta

    meta = ProjectMeta(
        format_version=pm.PROJECT_FORMAT_VERSION,
        profile_id="p",
        game="buus_fury",
        base_rom_sha256="0" * 64,
        base_rom_size=8,
        name="empty",
    )
    write_project(tmp_path, meta, enemies=[], characters=[])
    assert not (pathlib.Path(tmp_path) / pm.STRUCTURE_FILE).exists()
    assert pm.read_project(tmp_path).structure.is_empty()


def test_the_narrow_writer_removes_the_file_when_the_document_is_empty(tmp_path):
    path = pm.write_map_structure(tmp_path, _document())
    assert path.is_file()
    pm.write_map_structure(tmp_path, pm.MapStructure())
    assert not path.exists()


def test_a_malformed_file_is_refused_rather_than_ignored(tmp_path):
    root = pathlib.Path(tmp_path)
    (root / "maps").mkdir(parents=True)
    (root / "maps" / "structure.toml").write_text(
        '[resize."map:0040/BG1"]\ncolumns = 99\nrows = 2\nfill = 1\n',
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises((pm.ProjectLoadError, pm.ProjectValidationError)):
        pm._read_structure(root / "maps" / "structure.toml")


def test_the_emitted_file_is_lf_and_deterministic(tmp_path):
    first = pm.write_map_structure(pathlib.Path(tmp_path) / "a", _document())
    second = pm.write_map_structure(pathlib.Path(tmp_path) / "b", _document())
    left = first.read_bytes()
    assert left == second.read_bytes()
    assert b"\r\n" not in left
    assert left.endswith(b"\n")


def test_the_pair_is_written_as_two_tables_and_reads_back(tmp_path):
    """The file on disk carries both facts, and a reopen reproduces the pair."""
    path = pm.write_map_structure(tmp_path, _pair())
    text = path.read_text(encoding="utf-8")
    assert '[resize."map:0039/BG0"]' in text
    assert '[layer."layer:overlay"]' in text
    assert pm._read_structure(path) == _pair()


def test_a_hand_written_pair_loads(tmp_path):
    """Written by hand rather than by the writer, so the text form is the input."""
    root = pathlib.Path(tmp_path)
    (root / "maps").mkdir(parents=True)
    path = root / "maps" / "structure.toml"
    path.write_text(
        '[layer."layer:overlay"]\n'
        'map = "map:0039"\n'
        "slot = 0\n"
        'template = "map:0039/BG1"\n'
        "columns = 1\n"
        "rows = 1\n"
        'fill = "chunk:pad"\n'
        "\n"
        '[resize."map:0039/BG0"]\n'
        "columns = 2\n"
        "rows = 1\n"
        "fill = 3\n",
        encoding="utf-8",
        newline="\n",
    )
    structure = pm._read_structure(path)
    assert structure.layer_at(39, 0).fill == "chunk:pad"
    assert structure.layer_at(39, 0).columns == 1
    assert structure.resize_for(39, 0).columns == 2
    assert structure.resize_for(39, 0).fill == 3


def test_reopening_the_project_reproduces_the_pair(tmp_path):
    """The pair is durable: the project reloads with both facts intact."""
    from tools.webfoot.project import write_project
    from tools.webfoot.project.model import ProjectMeta

    meta = ProjectMeta(
        format_version=pm.PROJECT_FORMAT_VERSION,
        profile_id="p",
        game="buus_fury",
        base_rom_sha256="0" * 64,
        base_rom_size=8,
        name="pair",
    )
    write_project(tmp_path, meta, enemies=[], characters=[])
    pm.write_map_structure(tmp_path, _pair())
    reopened = pm.read_project(tmp_path).structure
    assert reopened == _pair()
    assert reopened.layer_at(39, 0).identity == "layer:overlay"
    assert (reopened.layer_at(39, 0).columns, reopened.layer_at(39, 0).rows) == (1, 1)
    assert (reopened.resize_for(39, 0).columns, reopened.resize_for(39, 0).rows) == (2, 1)
