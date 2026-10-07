"""APPEARANCE-AUTHORING-GATE-001: the authored-appearance document.

The model half of the capability, with no image involved: what a document
declares, how it round-trips through its own TOML writer and reader, what it
refuses from the text alone, and the one constant it states locally that the SDK
also states. The image half - the record layout, the relocation, the bounds - is
`tests/integration/test_appearance_authoring_rom.py`'s.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.webfoot import appearance_authoring as appearance_sdk
from tools.webfoot import appearances as appearance_format
from tools.webfoot.project.model import (APPEARANCES_FILE, APPEARANCE_TABLE,
                                         AuthoredAppearance, AuthoredAppearances,
                                         ProjectLoadError, ProjectValidationError,
                                         read_project, write_authored_appearances)

NAME = "new_face"
TEXT_INDEX = 1188
SPRITE_ID = 137


def _document(*definitions: AuthoredAppearance) -> AuthoredAppearances:
    return AuthoredAppearances(appearances={item.name: item for item in definitions})


def _project(tmp_path) -> Path:
    """A minimal project the model reads: identity only, no records."""
    from tools.webfoot.project.model import ProjectMeta, write_project

    write_project(tmp_path, ProjectMeta(1, "synthetic_profile", "Synthetic Game",
                                        "0" * 64, 1024, "appearance-model-test"),
                  enemies=[], characters=[])
    return tmp_path


def test_a_definition_round_trips_through_its_own_document(tmp_path):
    project = _project(tmp_path)
    document = _document(AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID))

    write_authored_appearances(project, document)

    assert (project / APPEARANCES_FILE).is_file()
    reopened = read_project(project).appearances
    assert reopened == document
    assert reopened.ordered()[0].identity == f"appearance:{NAME}"


def test_an_empty_document_removes_the_file_and_reads_back_empty(tmp_path):
    project = _project(tmp_path)
    write_authored_appearances(project, _document(
        AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID)))
    path = project / APPEARANCES_FILE
    assert path.is_file()

    write_authored_appearances(project, AuthoredAppearances())

    assert not path.exists()


def test_the_build_order_is_the_document_order_and_not_the_file_order(tmp_path):
    """A TOML table has no order, so the document states one and the build obeys."""
    project = _project(tmp_path)
    document = _document(
        AuthoredAppearance("zulu", 10, 10),
        AuthoredAppearance("alpha", 11, 11),
        AuthoredAppearance("mike", 12, 12),
    )

    assert tuple(item.name for item in document.ordered()) == ("alpha", "mike", "zulu")
    write_authored_appearances(project, document)

    assert tuple(item.name for item in read_project(project).appearances.ordered()) \
        == ("alpha", "mike", "zulu")


def test_a_name_that_is_not_a_durable_handle_is_refused():
    for bad in ("", "Upper", "1leading", "has space", "slash/y", "-lead"):
        with pytest.raises(ProjectValidationError):
            AuthoredAppearance(bad, TEXT_INDEX, SPRITE_ID)


def test_the_field_widths_are_the_record_widths():
    with pytest.raises(ProjectValidationError):
        AuthoredAppearance(NAME, 2**16, SPRITE_ID)
    with pytest.raises(ProjectValidationError):
        AuthoredAppearance(NAME, -1, SPRITE_ID)
    with pytest.raises(ProjectValidationError):
        AuthoredAppearance(NAME, TEXT_INDEX, 2**32)
    with pytest.raises(ProjectValidationError):
        AuthoredAppearance(NAME, TEXT_INDEX, -1)


def test_a_document_over_the_count_ceiling_is_refused_by_the_model():
    """The count is a Thumb `cmp rN,#imm8`, so the ceiling is stated, not trimmed."""
    ceiling = appearance_format.APPEARANCE_COUNT_CEILING \
        - appearance_format.APPEARANCE_CANONICAL_COUNT
    accepted = {f"a{index}": AuthoredAppearance(f"a{index}", index, 10)
                for index in range(ceiling)}
    assert len(AuthoredAppearances(appearances=accepted).appearances) == ceiling

    with pytest.raises(ProjectValidationError):
        AuthoredAppearances(appearances={
            **accepted, f"a{ceiling}": AuthoredAppearance(f"a{ceiling}", 0, 10)})


def test_the_models_ceiling_cannot_drift_from_the_sdk_constant():
    """Pinned rather than imported, so the two have to be changed together."""
    from tools.webfoot.project import model

    assert model._MAX_AUTHORED_APPEARANCES == (
        appearance_format.APPEARANCE_COUNT_CEILING
        - appearance_format.APPEARANCE_CANONICAL_COUNT)


def test_an_unknown_or_missing_key_is_refused_when_loading():
    from tools.webfoot.project.format import dump_toml

    document = {APPEARANCE_TABLE: {NAME: {"text_index": 1, "sprite_id": 2,
                                          "portrait": 3}}}
    with pytest.raises(ProjectLoadError) as refused:
        AuthoredAppearances.from_document(document, Path("appearances.toml"))
    assert "unknown key" in str(refused.value)

    del document[APPEARANCE_TABLE][NAME]["portrait"]
    del document[APPEARANCE_TABLE][NAME]["sprite_id"]
    with pytest.raises(ProjectLoadError) as missing:
        AuthoredAppearances.from_document(document, Path("appearances.toml"))
    assert "must declare sprite_id" in str(missing.value)
    assert dump_toml(document)


def test_a_project_without_the_document_authors_nothing(tmp_path):
    from tools.webfoot.project.model import (ProjectMeta, write_project)

    write_project(tmp_path, ProjectMeta(1, "synthetic_profile", "Synthetic Game",
                                        "0" * 64, 1024, "appearance-model-test"),
                  enemies=[], characters=[])

    assert read_project(tmp_path).appearances.is_empty()
    assert not (tmp_path / APPEARANCES_FILE).exists()


def test_applying_an_unchanged_document_reports_no_change(tmp_path):
    project = _project(tmp_path)
    document = _document(AuthoredAppearance(NAME, TEXT_INDEX, SPRITE_ID))
    assert appearance_sdk.apply_authored_appearances(project, document) is True
    assert appearance_sdk.apply_authored_appearances(project, document) is False
    assert appearance_sdk.authored_appearances(project) == document
