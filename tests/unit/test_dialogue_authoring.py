"""Public semantic dialogue-authoring API tests; no ROM required."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools.webfoot.dialogue import (
    DialogueAuthoringError,
    get_dialogue_original,
    get_dialogue_replacement,
    remove_dialogue_replacement,
    resolve_dialogue_target,
    set_dialogue_replacement,
    validate_dialogue_replacement,
)
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import (
    PROJECT_FORMAT_VERSION,
    ProjectMeta,
    read_project,
    write_project,
)


PROFILE_ID = "buus_fury_usa_rev0_01c1707f"
SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


@pytest.fixture
def profile():
    catalog = RomProfileCatalog.load("config/roms.yaml")
    return next(item for item in catalog.profiles if item.id == PROFILE_ID)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    write_project(
        root,
        ProjectMeta(
            format_version=PROJECT_FORMAT_VERSION,
            profile_id=PROFILE_ID,
            game="buus_fury",
            base_rom_sha256=SHA256,
            base_rom_size=8388608,
            name="dialogue-test",
        ),
        enemies=[],
        characters=[],
    )
    return root


def result(handle="0x02002641", text="Good luck, Goku!"):
    return {
        "source": "decoded-container-text",
        "text": text,
        "identity": {"packed_handle": handle},
    }


def test_goku_greeting_resolves_from_durable_storage_identity(profile):
    assert resolve_dialogue_target(result(), profile).name == "goku-greeting"


def test_visible_source_text_is_not_an_authoring_identity(profile):
    assert resolve_dialogue_target(result("0x00000000"), profile) is None
    assert resolve_dialogue_target(
        {"source": "raw-rom-run", "text": "Good luck, Goku!",
         "identity": {"packed_handle": "0x02002641"}},
        profile,
    ) is None


def test_replacement_validation_is_structured(profile):
    target = resolve_dialogue_target(result(), profile)
    assert validate_dialogue_replacement(target, "Nice work, Goku!", profile).valid
    invalid = validate_dialogue_replacement(target, "too short", profile)
    assert not invalid.valid
    assert invalid.problems[0].code == "decoded_length"


def test_set_and_remove_use_canonical_project_representation(project, profile):
    target = resolve_dialogue_target(result(), profile)
    assert get_dialogue_replacement(project, profile, target) is None

    set_dialogue_replacement(project, profile, target, "Nice work, Goku!")
    assert get_dialogue_replacement(project, profile, target) == "Nice work, Goku!"
    assert read_project(project).dialogues == {"goku-greeting": "Nice work, Goku!"}
    document = (project / "dialogue" / "replacements.toml").read_text("utf-8")
    assert "[dialogue.goku-greeting]" in document
    assert "0x02002641" not in document

    assert remove_dialogue_replacement(project, profile, target)
    assert get_dialogue_replacement(project, profile, target) is None
    assert not (project / "dialogue" / "replacements.toml").exists()


def test_invalid_set_does_not_mutate_project(project, profile):
    target = resolve_dialogue_target(result(), profile)
    before = tuple(project.rglob("*"))
    with pytest.raises(DialogueAuthoringError):
        set_dialogue_replacement(project, profile, target, "too short")
    assert tuple(project.rglob("*")) == before
    assert read_project(project).dialogues == {}


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("name", "forged-target"),
        ("selector", 0),
        ("table_offset", 0),
        ("packed_handle", 0),
        ("decoded_start", 0),
        ("decoded_length", 2),
        ("profile_id", None),
    ),
)
def test_forged_target_is_refused_by_every_public_operation(
    project, profile, field, value
):
    target = resolve_dialogue_target(result(), profile)
    set_dialogue_replacement(project, profile, target, "Nice work, Goku!")
    forged = replace(target, **{field: value})

    assert not validate_dialogue_replacement(forged, "Nice work, Goku!", profile).valid
    with pytest.raises(DialogueAuthoringError):
        get_dialogue_original(b"", profile, forged)
    with pytest.raises(DialogueAuthoringError):
        get_dialogue_replacement(project, profile, forged)
    with pytest.raises(DialogueAuthoringError):
        set_dialogue_replacement(project, profile, forged, "Nice work, Goku!")
    with pytest.raises(DialogueAuthoringError):
        remove_dialogue_replacement(project, profile, forged)
    assert read_project(project).dialogues == {"goku-greeting": "Nice work, Goku!"}
