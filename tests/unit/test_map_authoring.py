"""MAP-NEW-AUTHORING-001: the authored-map document.

The model half of the capability, with no image involved: what a document
declares, how it round-trips through its own TOML writer and reader, what it
refuses from the text alone, and the one constant it states locally that the SDK
also states. The image half - the table relocation, the two patches, the root and
the layer - is `tests/integration/test_map_authoring_rom.py`'s.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.webfoot import map_authoring as map_sdk
from tools.webfoot.project.model import (AUTHORED_MAPS_FILE, AuthoredMap,
                                         AuthoredMaps, ProjectLoadError,
                                         ProjectMeta, ProjectValidationError,
                                         read_project, write_authored_maps,
                                         write_project)

NAME = "cave"
DONOR = 40
KEY_HIGH = 0x99
KEY_LOW = 0x01

#: The canonical MapEntry row count. A profile fact rather than an SDK constant,
#: so it is stated here rather than imported: the ceiling the two modules must
#: agree on is `MAX_SUPPORTED_ROWS - canonical rows`.
CANONICAL_ROWS = 452


def _document(*maps: AuthoredMap) -> AuthoredMaps:
    return AuthoredMaps(maps={item.name: item for item in maps})


def _project(tmp_path) -> Path:
    """A minimal project the model reads: identity only, no records."""
    write_project(tmp_path, ProjectMeta(1, "synthetic_profile", "Synthetic Game",
                                        "0" * 64, 1024, "map-model-test"),
                  enemies=[], characters=[])
    return tmp_path


def test_a_map_round_trips_through_its_own_document(tmp_path):
    project = _project(tmp_path)
    document = _document(AuthoredMap(NAME, DONOR, KEY_HIGH, KEY_LOW))

    write_authored_maps(project, document)

    assert (project / AUTHORED_MAPS_FILE).is_file()
    reopened = read_project(project).authored_maps
    assert reopened == document
    assert reopened.ordered()[0].identity == f"map-new:{NAME}"
    assert reopened.ordered()[0].key == (KEY_HIGH, KEY_LOW)


def test_an_empty_document_removes_the_file_and_reads_back_empty(tmp_path):
    project = _project(tmp_path)
    write_authored_maps(project, _document(
        AuthoredMap(NAME, DONOR, KEY_HIGH, KEY_LOW)))
    path = project / AUTHORED_MAPS_FILE
    assert path.is_file()

    write_authored_maps(project, AuthoredMaps())

    assert not path.exists()
    assert read_project(project).authored_maps.is_empty()


def test_the_build_order_is_the_document_order_and_not_the_file_order(tmp_path):
    """A TOML table has no order, so the document states one and the build obeys."""
    project = _project(tmp_path)
    document = _document(
        AuthoredMap("zulu", 1, 0x90, 0x01),
        AuthoredMap("alpha", 2, 0x91, 0x01),
        AuthoredMap("mike", 3, 0x92, 0x01),
    )

    assert tuple(item.name for item in document.ordered()) == ("alpha", "mike", "zulu")
    write_authored_maps(project, document)

    assert tuple(item.name for item in read_project(project).authored_maps.ordered()) \
        == ("alpha", "mike", "zulu")


def test_a_name_that_is_not_a_durable_handle_is_refused():
    for bad in ("", "Upper", "1leading", "has space", "slash/y", "-lead"):
        with pytest.raises(ProjectValidationError):
            AuthoredMap(bad, DONOR, KEY_HIGH, KEY_LOW)


def test_the_key_bytes_are_one_byte_each():
    with pytest.raises(ProjectValidationError):
        AuthoredMap(NAME, DONOR, 0x100, KEY_LOW)
    with pytest.raises(ProjectValidationError):
        AuthoredMap(NAME, DONOR, KEY_HIGH, -1)
    with pytest.raises(ProjectValidationError):
        AuthoredMap(NAME, DONOR, 1.5, KEY_LOW)


def test_a_zero_key_is_refused():
    """A zero pair is not an identity the corpus uses, so it is not one here."""
    with pytest.raises(ProjectValidationError) as refused:
        AuthoredMap(NAME, DONOR, 0, 0)
    assert "zero key" in str(refused.value)


def test_a_negative_donor_is_refused():
    with pytest.raises(ProjectValidationError):
        AuthoredMap(NAME, -1, KEY_HIGH, KEY_LOW)


def test_two_maps_may_not_claim_one_key():
    """The engine's lookup returns the first match, so the second could never load."""
    with pytest.raises(ProjectValidationError) as refused:
        _document(AuthoredMap("first", 1, KEY_HIGH, KEY_LOW),
                  AuthoredMap("second", 2, KEY_HIGH, KEY_LOW))
    assert "both claim key" in str(refused.value)


def test_a_document_over_the_row_ceiling_is_refused_by_the_model():
    """The ceiling is the count helper's encoding ceiling, and it is stated."""
    ceiling = map_sdk.MAX_SUPPORTED_ROWS - CANONICAL_ROWS
    accepted = {
        f"m{index:02d}": AuthoredMap(f"m{index:02d}", index, 0x90 + index // 256,
                                     index % 256)
        for index in range(ceiling)
    }
    assert len(AuthoredMaps(maps=accepted).maps) == ceiling

    with pytest.raises(ProjectValidationError):
        AuthoredMaps(maps={**accepted,
                           f"m{ceiling}": AuthoredMap(f"m{ceiling}", 0, 0xF0, 0xF0)})


def test_the_models_ceiling_cannot_drift_from_the_sdk_constant():
    """Pinned rather than imported, so the two have to be changed together."""
    from tools.webfoot.project import model

    assert model._MAX_AUTHORED_MAPS == map_sdk.MAX_SUPPORTED_ROWS - CANONICAL_ROWS
    assert map_sdk.MAX_SUPPORTED_ROWS == 0xFF + 0xFF


def test_an_unknown_or_missing_key_is_refused_when_loading():
    from tools.webfoot.project.format import dump_toml

    from tools.webfoot.project.model import AUTHORED_MAP_TABLE

    document = {AUTHORED_MAP_TABLE: {NAME: {"donor": DONOR, "key_high": KEY_HIGH,
                                            "key_low": KEY_LOW, "spare": 1}}}
    with pytest.raises(ProjectLoadError) as refused:
        AuthoredMaps.from_document(document, Path("authored.toml"))
    assert "unknown key" in str(refused.value)

    del document[AUTHORED_MAP_TABLE][NAME]["spare"]
    del document[AUTHORED_MAP_TABLE][NAME]["key_low"]
    with pytest.raises(ProjectLoadError) as missing:
        AuthoredMaps.from_document(document, Path("authored.toml"))
    assert "must declare key_low" in str(missing.value)
    assert dump_toml(document)


def test_a_project_without_the_document_authors_nothing(tmp_path):
    project = _project(tmp_path)

    assert read_project(project).authored_maps.is_empty()
    assert not (project / AUTHORED_MAPS_FILE).exists()


def test_applying_an_unchanged_document_reports_no_change(tmp_path):
    project = _project(tmp_path)
    document = _document(AuthoredMap(NAME, DONOR, KEY_HIGH, KEY_LOW))
    assert map_sdk.apply_authored_maps(project, document) is True
    assert map_sdk.apply_authored_maps(project, document) is False
    assert map_sdk.authored_maps(project) == document


def test_the_new_storage_kinds_are_pinned_with_their_addressability():
    """The kinds this domain asks for, and the policy each one states."""
    from tools.webfoot.allocation import (DEFAULT_ADDRESSABILITY, Addressability,
                                          AllocationKind)
    from tools.webfoot.layout import RELOCATION_ELIGIBLE_KINDS

    assert AllocationKind.MAP_ENTRY_TABLE.value == "map_entry_table"
    assert (DEFAULT_ADDRESSABILITY[AllocationKind.MAP_ENTRY_TABLE]
            is Addressability.EXPANDED_ONLY)
    assert AllocationKind.MAP_ROOT_RECORD.value == "map_root_record"
    assert (DEFAULT_ADDRESSABILITY[AllocationKind.MAP_ROOT_RECORD]
            is Addressability.EXPANDED_ONLY)
    assert map_sdk.MAP_TABLE_KIND in RELOCATION_ELIGIBLE_KINDS


def test_the_patch_sites_are_the_ones_the_census_measured():
    """The two engine-side sites, stated here so a move has to be deliberate."""
    assert map_sdk.BASE_POOL_FILE_OFFSET == 0x8A58
    assert map_sdk.COUNT_IMMEDIATE_FILE_OFFSET == 0x125E2
    assert map_sdk.COUNT_IMMEDIATE_CANONICAL == 0xC5
    assert map_sdk.COUNT_IMMEDIATE_BASE == 0xFF
    assert map_sdk.ROOT_SIZE == 0x50
