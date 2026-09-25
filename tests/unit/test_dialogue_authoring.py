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
    """The length rule became a CAPACITY rule, not an equality rule.

    DIALOGUE-VARIABLE-LENGTH-001. Until this ticket the only way a replacement
    could fail here was by not encoding to exactly the record's 32 retail bytes.
    The durable handle is now authored for whatever the replacement encodes to,
    so a different length is valid; what remains invalid is text no handle can
    describe, and the two structured failures below are the ones the field
    actually imposes.
    """
    target = resolve_dialogue_target(result(), profile)
    assert validate_dialogue_replacement(target, "Nice work, Goku!", profile).valid
    # Shorter and longer are both ordinary edits now.
    assert validate_dialogue_replacement(target, "Hi!", profile).valid
    assert validate_dialogue_replacement(
        target, "Hot take: SSJ3 is the worst form imo", profile).valid
    # One past what the handle's 11-bit halfword length field can encode.
    too_long = validate_dialogue_replacement(target, "a" * 2048, profile)
    assert not too_long.valid
    assert too_long.problems[0].code == "decoded_length"
    assert "4094" in too_long.problems[0].message
    # Text UTF-16LE cannot represent at all.
    unsupported = validate_dialogue_replacement(target, "\ud800", profile)
    assert not unsupported.valid
    assert unsupported.problems[0].code == "unsupported_character"
    # And the empty case keeps its own code.
    empty = validate_dialogue_replacement(target, "", profile)
    assert not empty.valid
    assert empty.problems[0].code == "empty_replacement"


def test_a_record_still_resolves_after_its_retail_handle_is_superseded(profile):
    """Reopen: the semantic record is identified by its own anchor, not the handle.

    A derivative this toolkit built carries a re-authored handle, so resolution
    by the retail value alone would answer "not found" and the record would look
    like a different message. The record's decoded start is invariant under the
    authoring operation, so it names the same record in both images.
    """
    superseded = "0x04802641"          # what `Hot take: SSJ3 ...` authors
    # The raw handle is one of the record's compiled properties, not its
    # identity: the new value alone ties to nothing registered.
    assert resolve_dialogue_target(result(superseded), profile) is None
    reopened = {
        "source": "decoded-container-text",
        "text": "Hot take: SSJ3 is the worst form imo",
        "identity": {"packed_handle": superseded,
                     "handle_selector": 1,
                     "handle_decoded_start": "0x132",
                     "handle_decoded_length": "0x48"},
    }
    assert resolve_dialogue_target(reopened, profile).name == "goku-greeting"
    # A different record's anchor is still not the target.
    other = dict(reopened, identity={"packed_handle": superseded,
                                     "handle_selector": 1,
                                     "handle_decoded_start": "0x17A",
                                     "handle_decoded_length": "0xA0"})
    assert resolve_dialogue_target(other, profile) is None


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
        set_dialogue_replacement(project, profile, target, "")
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
