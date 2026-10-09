"""DRAGONBYTE-Z-STATE-001: one journal, one history, one derived dirty state.

Three lanes, deliberately separated.

The headless lane drives the journal and the session with no ``QApplication`` at
all, over a real project on disk: the round trip, the checkpoint table, the
coalescing rule, the fail-closed paths and the isolation between projects.

The windowed lane runs the real shell offscreen and proves the one thing a widget
is not allowed to decide: that the enabled state of Save, Undo and Redo EQUALS the
session's answer, and that the destination button, the visible page and the
navigation cursor never disagree.

No test here spawns a process, so no launch site needs registering, and no test
opens a canonical image for writing.
"""

from __future__ import annotations

import ast
import hashlib
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from dataclasses import replace  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from tools.webfoot.formats import stat_tables as st  # noqa: E402
from tools.webfoot.project import (  # noqa: E402
    PROJECT_FORMAT_VERSION,
    ProjectMeta,
    load_toml,
    read_project,
    write_dialogue_replacements,
    write_project,
)
from tools.webfoot.project import model as project_model  # noqa: E402

from tools.dragonbyte import journal as journal_module  # noqa: E402
from tools.dragonbyte.destination import DESTINATIONS, ROM_DESTINATION  # noqa: E402
from tools.dragonbyte.journal import (  # noqa: E402
    EditJournal,
    EditKind,
    EditOperation,
    JournalError,
    UnknownEditTargetError,
    project_authority,
)
from tools.dragonbyte.session import (  # noqa: E402
    RomNotRecognizedError,
    Session,
    SessionError,
    UnsavedChangesError,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPOSITORY_ROOT / "tools" / "dragonbyte"

#: The sibling primary checkout, derived from this file's own location rather
#: than written down. Its roms/ directory is where a canonical image lives.
SIBLING_CHECKOUT = Path(__file__).resolve().parents[2].parent / "log1-remake"

CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: The one registered document. Every journal test edits it, because a target
#: without an adapter is the fail-closed case and is tested as one.
DIALOGUES = "dialogues"


def _meta(**overrides) -> ProjectMeta:
    values = {
        "format_version": PROJECT_FORMAT_VERSION,
        "profile_id": "buus_fury_usa_rev0_01c1707f",
        "game": "buus_fury",
        "base_rom_sha256": CANONICAL_SHA256,
        "base_rom_size": 8388608,
        "name": "test-project",
    }
    values.update(overrides)
    return ProjectMeta(**values)


def _enemy(type_id: int = 434, hp: int = 175):
    original = bytes(range(st.ENEMY_RECORD_SIZE))
    record = st.decode_enemy_record(original, 0)
    record = type(record)(
        offset=0,
        exp=record.exp,
        hp=hp,
        type_id=type_id,
        level=5,
        strength=record.strength,
        power=record.power,
        endurance=record.endurance,
    )
    # `raw` must be the bytes the semantic fields were encoded over, or a build
    # would re-emit a record whose opaque span belongs to a different record.
    return (
        st.StatIdentity(kind="enemy", key=type_id),
        record,
        st.encode_enemy_record(record, original),
        None,
    )


def _character(index: int = 0):
    original = bytes(range(st.BASE_STAT_RECORD_SIZE))
    record = st.decode_base_stat_record(original, 0)
    return (
        st.StatIdentity(kind="character", key=index),
        record,
        st.encode_base_stat_record(record, original),
        st.character_alias(index, st.BASE_STAT_RECORD_COUNT),
    )


def _write_project(directory: Path, name: str = "test-project") -> Path:
    """A minimal valid project on disk, by the recipe the format tests use."""
    write_project(
        directory,
        _meta(name=name),
        enemies=[_enemy()],
        characters=[_character()],
    )
    return directory


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return _write_project(tmp_path / "proj")


def _apply(journal: EditJournal, project, dialogues: dict[str, str], **kwargs):
    return journal.apply(
        project, kind=EditKind.SEMANTIC, target=DIALOGUES, after=dialogues, **kwargs
    )


def _snapshot(journal: EditJournal) -> tuple:
    """Everything a refused edit must leave exactly as it was."""
    return (
        len(journal),
        journal.depth,
        journal.current_revision,
        journal.can_undo,
        journal.can_redo,
        journal.is_dirty,
    )


@pytest.fixture(scope="module")
def qapp():
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


# --- 1. one journal per session, and no sharing -------------------------------


def test_a_session_holds_one_journal_and_two_sessions_do_not_share_one():
    first = Session()
    second = Session()

    assert isinstance(first.journal, EditJournal)
    assert first.journal is not second.journal
    assert first.journal.authority is None
    assert second.journal.authority is None


# --- 2. the round trip --------------------------------------------------------


def test_edit_undo_redo_round_trip_on_a_real_project(project_dir):
    session = Session()
    session.open_project(project_dir)
    original = dict(session.project.dialogues)
    edited = {"goku-greeting": "Hello."}

    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after=edited)

    assert session.project.dialogues == edited
    assert session.journal.depth == 1

    session.undo_edit()
    assert session.project.dialogues == original

    session.redo_edit()
    assert session.project.dialogues == edited


# --- 3. a new edit abandons the redo branch -----------------------------------


def test_a_new_edit_after_undo_invalidates_the_redo_branch(project_dir):
    session = Session()
    session.open_project(project_dir)
    session.apply_edit(
        kind=EditKind.SEMANTIC, target=DIALOGUES, after={"first": "One."}
    )
    session.undo_edit()
    assert session.journal.can_redo

    session.apply_edit(
        kind=EditKind.SEMANTIC, target=DIALOGUES, after={"second": "Two."}
    )

    assert not session.journal.can_redo
    assert session.journal.depth == 1
    assert session.project.dialogues == {"second": "Two."}


# --- 4 and 5. the dirty checkpoint table, and redo restores it exactly --------


def test_the_dirty_checkpoint_table(project_dir):
    session = Session()
    session.open_project(project_dir)
    saved = dict(session.project.dialogues)

    assert not session.journal.is_dirty  # a freshly read project is clean

    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    assert session.journal.is_dirty

    session.undo_edit()
    assert not session.journal.is_dirty  # back at the saved checkpoint

    session.redo_edit()
    assert session.journal.is_dirty

    session.save_project()
    assert not session.journal.is_dirty
    assert session.journal.saved_revision == session.journal.current_revision

    session.undo_edit()
    assert session.journal.is_dirty

    session.redo_edit()
    assert not session.journal.is_dirty

    session.undo_edit()
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"b": "B."})
    assert session.journal.is_dirty
    assert saved == {}


def test_redo_restores_the_saved_checkpoint_exactly(project_dir):
    session = Session()
    session.open_project(project_dir)
    before = session.journal.current_revision
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    session.save_project()
    checkpoint = session.journal.saved_revision

    session.undo_edit()
    assert session.journal.current_revision != checkpoint

    session.redo_edit()

    assert session.journal.current_revision == checkpoint
    assert session.journal.saved_revision == checkpoint
    assert not session.journal.is_dirty
    assert before == 0


# --- 6. a divergent branch cannot look clean ----------------------------------


def test_a_divergent_branch_cannot_appear_clean_at_the_saved_depth(project_dir):
    session = Session()
    session.open_project(project_dir)
    journal = session.journal

    _apply(journal, session.project, {"a": "A."})
    session.project = replace(
        session.project, dialogues={"a": "A."}
    )
    journal.save(project_dir, session.project)
    saved_depth = journal.depth
    saved_revision = journal.saved_revision

    session.undo_edit()
    _apply(journal, session.project, {"b": "B."})
    session.project = replace(session.project, dialogues={"b": "B."})

    assert journal.depth == saved_depth, "the branch has the same numerical depth"
    assert journal.current_revision != saved_revision
    assert journal.is_dirty


# --- 7 and 8. the refused paths leave the state alone -------------------------


def test_a_failed_edit_leaves_entries_cursor_and_revision_unchanged(project_dir):
    session = Session()
    session.open_project(project_dir)
    journal = session.journal
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    before = _snapshot(journal)

    with pytest.raises(SessionError):
        session.apply_edit(
            kind=EditKind.SEMANTIC, target=DIALOGUES, after={"empty": ""}
        )

    assert _snapshot(journal) == before
    assert session.project.dialogues == {"a": "A."}


def test_a_failed_undo_and_a_failed_redo_leave_the_cursor_unchanged(project_dir):
    session = Session()
    session.open_project(project_dir)
    journal = session.journal

    with pytest.raises(SessionError):
        session.undo_edit()
    after_failed_undo = _snapshot(journal)
    assert after_failed_undo == (0, 0, 0, False, False, False)

    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    with pytest.raises(SessionError):
        session.redo_edit()

    assert journal.depth == 1
    assert journal.can_undo
    assert not journal.can_redo


# --- 9. a failed save does not advance the checkpoint -------------------------


def test_a_failed_save_does_not_advance_saved_revision(project_dir, monkeypatch):
    """The writer's own name, in its own module, is the honest reproduction: the
    write is the operation under test, so the write is the one made to fail."""
    session = Session()
    session.open_project(project_dir)
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})

    def refuse(path, text):
        raise OSError("disk is full")

    # `write_dialogue_replacements` binds the name at import, so the patch goes
    # where it is looked up rather than where it is defined.
    monkeypatch.setattr(project_model, "replace_document", refuse)

    with pytest.raises(SessionError):
        session.save_project()

    assert session.journal.saved_revision == 0
    assert session.journal.is_dirty
    assert not (project_dir / "dialogue" / "replacements.toml").exists()


# --- 10. replacement isolates the journal -------------------------------------


def test_project_replacement_isolates_journal_state(tmp_path):
    first = _write_project(tmp_path / "a", name="project-a")
    second = _write_project(tmp_path / "b", name="project-b")
    session = Session()
    session.open_project(first)
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    assert session.journal.is_dirty

    with pytest.raises(UnsavedChangesError):
        session.open_project(second, discard_unsaved=False)
    assert session.project_dir == first, "a refusal leaves the session intact"

    session.open_project(second, discard_unsaved=True)
    second_project = session.project

    assert session.journal.depth == 0
    assert not session.journal.is_dirty
    assert not session.journal.can_undo
    assert session.journal.saved_revision == 0
    assert session.journal.authority == project_authority(second_project)
    assert session.journal.authority != project_authority(
        read_project(first)
    )

    forged = EditOperation(
        kind=EditKind.SEMANTIC,
        target=DIALOGUES,
        owner="project-a/" + CANONICAL_SHA256[:16] + "/buus_fury_usa_rev0_01c1707f",
        before={},
        after={},
    )
    assert forged.owner != session.journal.authority
    # The authority is taken from the PROJECT, never from the caller's word, so
    # the one way to reach this refusal is to hand the journal a different
    # project - which is exactly what a stale operation would do.
    stale_journal = EditJournal()
    stale_journal.bind("project-a/" + CANONICAL_SHA256[:16] + "/buus_fury_usa_rev0_01c1707f")
    with pytest.raises(journal_module.JournalAuthorityError):
        stale_journal.apply(
            read_project(second), kind=EditKind.SEMANTIC, target=DIALOGUES, after={"b": "B."}
        )
    assert stale_journal.depth == 0


# --- 11 and 12. navigation and edit history do not meet -----------------------


def test_navigation_does_not_affect_edit_history(project_dir):
    session = Session()
    session.open_project(project_dir)
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    before = _snapshot(session.journal)

    session.navigation.push("maps")
    session.navigation.push("data")
    session.navigation.back()
    session.navigation.forward()

    assert _snapshot(session.journal) == before
    assert session.journal.depth == 1
    assert session.journal.is_dirty


def test_edit_history_does_not_affect_navigation(project_dir):
    session = Session()
    session.open_project(project_dir)
    session.navigation.push("maps")
    session.navigation.push("data")
    session.navigation.back()
    cursor = session.navigation.current.destination
    entries = len(session.navigation)

    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    session.undo_edit()
    session.redo_edit()
    session.undo_edit()

    assert session.navigation.current.destination == cursor
    assert len(session.navigation) == entries
    assert session.navigation.can_go_forward


# --- 13 and 14. the real SDK round trip, and the atomic reload ----------------


def test_a_journaled_dialogue_edit_round_trips_through_the_real_sdk(project_dir):
    """No ROM, no profile, no mock: a real project directory and the real writer."""
    document = project_dir / "dialogue" / "replacements.toml"
    project = read_project(project_dir)
    original = dict(project.dialogues)
    journal = EditJournal()

    project = journal.apply(
        project,
        kind=EditKind.SEMANTIC,
        target=DIALOGUES,
        after={"goku-greeting": "Hello."},
    )
    assert project.dialogues == {"goku-greeting": "Hello."}

    undone = journal.undo(project)
    assert undone.dialogues == original

    redone = journal.redo(undone)
    assert redone.dialogues == {"goku-greeting": "Hello."}

    journal.save(project_dir, redone)

    assert document.is_file()
    assert read_project(project_dir).dialogues == {"goku-greeting": "Hello."}
    assert load_toml(document.read_text(encoding="utf-8")) == {
        "dialogue": {"goku-greeting": {"text": "Hello."}}
    }
    assert journal.saved_revision == journal.current_revision


def test_a_save_after_undoing_every_edit_persists_the_base_state(tmp_path):
    """The checkpoint must correspond to the state actually on disk.

    The base mapping here is EMPTY, so this also exercises the SDK writer's own
    removal of the optional document for an empty mapping. The companion below
    repeats it with a non-empty base, so the assertion is not an artefact of
    that removal.
    """
    project_dir = _write_project(tmp_path / "empty-base")
    journal = EditJournal()
    project = read_project(project_dir)
    assert project.dialogues == {}
    edited = {"goku-greeting": "Hello!"}

    project = journal.apply(
        project, kind=EditKind.SEMANTIC, target=DIALOGUES, after=edited
    )
    journal.save(project_dir, project)
    assert read_project(project_dir).dialogues == edited

    undone = journal.undo(project)
    assert undone.dialogues == {}

    journal.save(project_dir, undone)

    assert read_project(project_dir).dialogues == undone.dialogues, (
        "disk equals memory"
    )
    assert journal.is_dirty is False
    assert journal.saved_revision == journal.current_revision == 0
    assert not (project_dir / "dialogue" / "replacements.toml").exists()


def test_a_save_after_undoing_every_edit_persists_a_non_empty_base_state(tmp_path):
    project_dir = _write_project(tmp_path / "base")
    write_dialogue_replacements(project_dir, {"vegeta-taunt": "Base."})
    journal = EditJournal()
    project = read_project(project_dir)
    assert project.dialogues == {"vegeta-taunt": "Base."}

    project = journal.apply(
        project,
        kind=EditKind.SEMANTIC,
        target=DIALOGUES,
        after={"vegeta-taunt": "Edited."},
    )
    journal.save(project_dir, project)
    assert read_project(project_dir).dialogues == {"vegeta-taunt": "Edited."}

    undone = journal.undo(project)
    journal.save(project_dir, undone)

    assert read_project(project_dir).dialogues == {"vegeta-taunt": "Base."}
    assert read_project(project_dir).dialogues == undone.dialogues
    assert journal.is_dirty is False
    assert journal.saved_revision == journal.current_revision == 0


def test_clearing_every_replacement_is_an_edit_the_sdk_supports(project_dir):
    """The empty mapping, all four ways it has to work.

    An empty mapping is a legitimate authored state rather than a refusal: the
    SDK's writer removes the optional document for it and ``read_project`` reads
    that absence back as "this project authors no dialogue". Refusing it would
    permanently block the clear-every-replacement edit a later dialogue surface
    needs, so this pins the whole path: apply, undo, save, reload.
    """
    journal = EditJournal()
    base = read_project(project_dir)
    assert base.dialogues == {}

    # (a) the empty mapping is accepted and install produces an empty mapping.
    cleared = journal.apply(
        base, kind=EditKind.SEMANTIC, target=DIALOGUES, after={}
    )
    assert cleared.dialogues == {}

    # Then fill it, so undo and the save below have something real to restore.
    filled = journal.apply(
        cleared,
        kind=EditKind.SEMANTIC,
        target=DIALOGUES,
        after={"goku-greeting": "Hello."},
    )
    journal.save(project_dir, filled)
    document = project_dir / "dialogue" / "replacements.toml"
    assert document.is_file()

    # Apply the empty mapping again over a one-entry base: accepted, installed.
    emptied = journal.apply(
        filled, kind=EditKind.SEMANTIC, target=DIALOGUES, after={}
    )
    assert emptied.dialogues == {}

    # (b) undo restores the base mapping, and a save writes it back.
    restored = journal.undo(emptied)
    assert restored.dialogues == {"goku-greeting": "Hello."}
    journal.save(project_dir, restored)
    assert read_project(project_dir).dialogues == {"goku-greeting": "Hello."}

    # (c) a save with the empty mapping at the cursor removes the document, and
    # (d) the project is still one `read_project` accepts.
    journal.save(project_dir, journal.redo(restored))
    assert not document.exists()
    assert read_project(project_dir).dialogues == {}
    assert read_project(project_dir).meta.name == base.meta.name


def test_a_partial_multi_document_save_writes_what_it_can_and_holds_the_checkpoint(
    project_dir, monkeypatch
):
    """The multi-document ceiling, measured rather than asserted.

    The second adapter registered here exists only to exercise the path a Save
    takes once the committed history names more than one document, which no
    registered configuration reaches today: each document is replaced on its own,
    so a failure on the second leaves the first written while the checkpoint
    correctly stays put.
    """
    second = "test-only-document"
    assert second not in journal_module.DOCUMENT_ADAPTERS

    def refuse(_directory, _payload):
        raise OSError("the second document cannot be written")

    monkeypatch.setitem(
        journal_module.DOCUMENT_ADAPTERS,
        second,
        journal_module._DocumentAdapter(
            read=lambda project: project.graphics_overrides,
            install=lambda project, payload: replace(
                project, graphics_overrides=payload
            ),
            validate=lambda _project, _payload: None,
            write=refuse,
        ),
    )

    journal = EditJournal()
    # The dialogues edit is committed first, so its write is guaranteed to have
    # happened by the time the second document refuses.
    project = journal.apply(
        read_project(project_dir), kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."}
    )
    project = journal.apply(
        project,
        kind=EditKind.STRUCTURAL,
        target=second,
        after=project_model.GraphicsOverrides(),
    )
    assert journal._committed_targets() == [DIALOGUES, second]

    with pytest.raises(JournalError) as refusal:
        journal.save(project_dir, project)

    assert second in str(refusal.value)
    assert journal.saved_revision == 0
    assert journal.is_dirty is True
    # The dialogues document really was written, because it was reached first.
    assert read_project(project_dir).dialogues == {"a": "A."}
    assert not (project_dir / "graphics" / "overrides.toml").exists()


# --- 15. the fail-closed path for an unregistered document --------------------


def test_an_unregistered_target_is_refused_and_writes_nothing(project_dir):
    journal = EditJournal()
    before = _snapshot(journal)

    with pytest.raises(UnknownEditTargetError) as refusal:
        journal.apply(
            read_project(project_dir),
            kind=EditKind.RAW,
            target="raw:0x08711274",
            after=b"\x00",
        )

    assert "no reversible document" in str(refusal.value).lower()
    assert _snapshot(journal) == before
    assert len(journal) == 0
    assert not (project_dir / "dialogue").exists()


# --- coalescing ---------------------------------------------------------------


def test_three_applies_with_one_key_are_one_entry_and_one_undo(project_dir):
    journal = EditJournal()
    project = read_project(project_dir)
    original = dict(project.dialogues)

    for text in ("H", "He", "Hel"):
        project = journal.apply(
            project,
            kind=EditKind.SEMANTIC,
            target=DIALOGUES,
            after={"goku-greeting": text},
            coalesce_key="goku-greeting",
        )
    merged = journal.edits()[-1]
    revision_before_merge = 1

    assert journal.depth == 1
    assert len(journal) == 1
    assert merged.after == {"goku-greeting": "Hel"}
    assert merged.before == original
    assert merged.revision != revision_before_merge, "a merge takes a fresh revision"

    undone = journal.undo(project)
    assert undone.dialogues == original, "one undo returns to before the whole gesture"

    assert journal.edits() == (), "the merged entry is no longer applied"


def test_a_merge_unions_the_resources_in_order_and_once(project_dir):
    journal = EditJournal()
    project = read_project(project_dir)

    for resource in ("0x08711274", "0x08711280", "0x08711274"):
        project = journal.apply(
            project,
            kind=EditKind.SEMANTIC,
            target=DIALOGUES,
            after={"goku-greeting": "H"},
            resources=(resource,),
            coalesce_key="gesture",
        )

    assert journal.depth == 1
    assert journal.pending_resources() == frozenset({"0x08711274", "0x08711280"})
    assert journal.edits()[-1].resources == ("0x08711274", "0x08711280")


def test_a_merge_needs_the_same_key_target_owner_and_kind(project_dir):
    journal = EditJournal()
    project = read_project(project_dir)

    project = journal.apply(
        project,
        kind=EditKind.SEMANTIC,
        target=DIALOGUES,
        after={"a": "A"},
        coalesce_key="key",
    )
    project = journal.apply(
        project,
        kind=EditKind.SEMANTIC,
        target=DIALOGUES,
        after={"b": "B"},
        coalesce_key="different-key",
    )
    assert journal.depth == 2, "a different key starts a new entry"

    with pytest.raises(UnknownEditTargetError):
        journal.apply(
            project,
            kind=EditKind.RAW,
            target="raw:0x1",
            after=b"\x00",
            coalesce_key="key",
        )
    assert journal.depth == 2, "a refused merge commits nothing"


def test_an_empty_coalesce_key_never_merges(project_dir):
    journal = EditJournal()
    project = read_project(project_dir)

    for text in ("H", "He"):
        project = journal.apply(
            project,
            kind=EditKind.SEMANTIC,
            target=DIALOGUES,
            after={"goku-greeting": text},
        )

    assert journal.depth == 2


# --- 16. the window renders the session's answer ------------------------------


def _shell(config_directory: Path, session: Session):
    from tools.dragonbyte.shell import Shell

    return Shell(session, config_directory)


def _close(shell, session: Session) -> None:
    """Close without reaching a modal question.

    A dirty journal makes `closeEvent` ask, and a modal QMessageBox cannot be
    answered offscreen, so a test that leaves edits pending would block forever
    instead of failing - including a test that fails BEFORE reaching its cleanup.
    Rebinding the journal is the reset that makes the window clean whatever the
    assertions already did, and it touches no state the tests assert on.
    """
    session.journal.bind(session.journal.authority or "")
    shell.close()


def test_the_edit_actions_exist_and_their_state_equals_the_session_answer(
    qapp, tmp_path
):
    from PySide6.QtGui import QAction

    from tools.dragonbyte.shell import EDIT_ACTIONS

    session = Session()
    shell = _shell(tmp_path, session)

    actions = {action.text(): action for action in shell.findChildren(QAction)}
    assert EDIT_ACTIONS == ("Save", "Undo", "Redo")
    for label in EDIT_ACTIONS:
        assert label in actions, label

    rendered = {label: actions[label].isEnabled() for label in EDIT_ACTIONS}
    answer = {label: enabled for label, (enabled, _r) in session.edit_availability().items()}
    assert rendered == answer == {"Save": False, "Undo": False, "Redo": False}
    assert actions["Save"].toolTip() == "No project is open."

    _write_project(tmp_path / "p")
    session.open_project(tmp_path / "p")
    shell._refresh_status()
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    shell._refresh_status()

    rendered = {label: actions[label].isEnabled() for label in EDIT_ACTIONS}
    answer = {label: enabled for label, (enabled, _r) in session.edit_availability().items()}
    assert rendered == answer == {"Save": True, "Undo": True, "Redo": False}

    for label in EDIT_ACTIONS:
        button = shell._action_bar.widgetForAction(actions[label])
        assert button is not None
        _enabled, reason = session.edit_availability()[label]
        assert button.accessibleName() == f"{label}. {reason}"
        assert button.toolTip() == reason

    session.undo_edit()
    shell._refresh_status()
    assert actions["Redo"].isEnabled() is True
    assert actions["Undo"].isEnabled() is False

    _close(shell, session)


def test_the_status_line_names_unsaved_changes(qapp, tmp_path):
    from PySide6.QtWidgets import QLabel

    session = Session()
    shell = _shell(tmp_path, session)
    _write_project(tmp_path / "p")
    session.open_project(tmp_path / "p")
    shell._refresh_status()

    assert "project open" in _status_text(shell)
    assert "unsaved changes" not in _status_text(shell)

    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    shell._refresh_status()

    assert "project open, unsaved changes" in _status_text(shell)
    assert shell.findChildren(QLabel)  # the status line is a real label
    _close(shell, session)


def test_a_shell_level_edit_leaves_no_stale_action_state(qapp, tmp_path):
    """An edit through the shell's own entry point must not leave it behind.

    Without a refresh inside `apply_edit`, the journal goes dirty while the status
    line still says "project open" and Save, Undo and Redo stay disabled, until
    some unrelated action happens to refresh. So nothing in this test calls a
    refresh or any other shell method between the edit and the assertions.
    """
    from PySide6.QtGui import QAction

    from tools.dragonbyte.shell import EDIT_ACTIONS

    session = Session()
    shell = _shell(tmp_path, session)
    _write_project(tmp_path / "p")
    session.open_project(tmp_path / "p")
    shell._refresh_status()
    actions = {action.text(): action for action in shell.findChildren(QAction)}

    assert not actions["Save"].isEnabled()
    assert "unsaved changes" not in _status_text(shell)

    shell.apply_edit(
        kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."}
    )

    assert "project open, unsaved changes" in _status_text(shell)
    rendered = {label: actions[label].isEnabled() for label in EDIT_ACTIONS}
    answer = {
        label: enabled for label, (enabled, _r) in session.edit_availability().items()
    }
    assert rendered == answer == {"Save": True, "Undo": True, "Redo": False}
    _close(shell, session)


def _status_text(shell) -> str:
    return shell._status_state.text()


# --- 17. the destination, the page and the cursor never disagree --------------


def test_the_selected_destination_the_visible_page_and_the_cursor_agree(
    qapp, tmp_path
):
    """The FOUNDATION observation was a selected ROM button beside a Data page.
    Nothing in the model allows it - the strip, the stack and the history are
    written in one place from one id - so this pins the invariant rather than
    reproducing a defect. See the report: not reproducible from the model.

    One page names itself differently on purpose: the ROM destination renders the
    address space (S5) rather than a foundation statement, so its page is
    ``romPage``; the Data destination renders the records and the coverage view
    (S6) rather than a statement about them, so its page is ``dataPage``; the Maps
    destination renders the map's cells and warps (S7) so its page is ``mapPage``;
    the Entities destination renders the placement family (S7) so its page is
    ``entityPage``; and the Scripts & Text destination renders the scripts, events
    and the two text systems (S7) so its page is ``textPage``. The remaining
    destination is its own ``foundationPage_<id>``.
    """
    session = Session()
    shell = _shell(tmp_path, session)
    stack = shell._page_stack

    def invariant() -> None:
        current = session.navigation.current
        assert current is not None
        checked = [
            identifier
            for identifier, button in shell._destination_buttons.items()
            if button.isChecked()
        ]
        assert checked == [current.destination], checked
        assert stack.currentWidget() is shell._pages[current.destination]
        page_name = stack.currentWidget().objectName()
        expected = {
            ROM_DESTINATION.id: "romPage",
            "data": "dataPage",
            "maps": "mapPage",
            "entities": "entityPage",
            "scripts_text": "textPage",
        }.get(current.destination, f"foundationPage_{current.destination}")
        assert page_name == expected, page_name

    for _round in range(3):
        for candidate in DESTINATIONS:
            shell.show_destination(candidate.id)
            invariant()
            shell.show_destination(candidate.id)  # repeat the current selection
            invariant()

    while session.navigation.can_go_back:
        shell.go_back()
        invariant()

    assert not session.navigation.can_go_back
    while session.navigation.can_go_forward:
        shell.go_forward()
        invariant()

    assert session.navigation.current.destination == DESTINATIONS[-1].id
    invariant()
    shell.close()


# --- 18. no per-surface undo stack -------------------------------------------


def test_no_package_file_names_a_qt_undo_type_or_holds_a_second_stack():
    names = ("QUndoStack", "QUndoCommand")
    offenders = []
    stack_owners = []
    for path in sorted(PACKAGE_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        for name in names:
            if name in source:
                offenders.append((path.name, name))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    spelled = ast.unparse(target)
                    if "_undo_stack" in spelled:
                        stack_owners.append((path.name, spelled))

    assert offenders == [], "the roadmap forbids a per-surface Qt undo stack"
    assert stack_owners == [], "the journal is the only history in the application"


# --- 19. the journal pulls in no Qt and no beta package -----------------------


def test_importing_the_journal_pulls_in_no_qt_and_no_beta_package():
    from tools.quality import architecture as arch

    relative = "tools/dragonbyte/journal.py"
    tree = ast.parse((PACKAGE_ROOT / "journal.py").read_text(encoding="utf-8"))
    imported = [name for name, _line in arch._imported_modules(relative, tree)]

    assert [name for name in imported if name.startswith("PySide6")] == []
    assert [
        name
        for name in imported
        if name == "tools.webfoot.workbench" or name.startswith("tools.webfoot.workbench.")
    ] == []
    assert "Qt" not in dir(journal_module)
    assert "PySide6" not in (PACKAGE_ROOT / "journal.py").read_text(encoding="utf-8")


# --- 20. the canonical image is read and never written ------------------------


def test_the_canonical_image_is_byte_identical_across_the_whole_round_trip(tmp_path):
    """The image, when one is present, is read for its digest and nothing else.

    The sibling checkout's own ``roms/`` directory is derived from this file's
    location. Without a verified image there the test skips: it is evidence about
    a real read, not a synthetic one.
    """
    roms = SIBLING_CHECKOUT / "roms"
    candidates = sorted(roms.glob("*.gba")) if roms.is_dir() else []
    if not candidates:
        pytest.skip(f"no canonical image in {roms}")

    session = Session()
    opened = None
    for candidate in candidates:
        try:
            session.open_rom(candidate)
        except RomNotRecognizedError:
            continue
        opened = candidate
        break
    if opened is None:
        pytest.skip(f"no image in {roms} matched a verified profile")

    before = hashlib.sha256(opened.read_bytes()).hexdigest()
    project_dir = _write_project(tmp_path / "proj")
    session.open_project(project_dir)
    session.apply_edit(kind=EditKind.SEMANTIC, target=DIALOGUES, after={"a": "A."})
    session.undo_edit()
    session.redo_edit()
    session.save_project()

    assert hashlib.sha256(opened.read_bytes()).hexdigest() == before
    assert session.has_rom
    assert session.has_project


# --- diagnostics of the journal's own state -----------------------------------


def test_the_journal_reports_its_state_as_data():
    journal = EditJournal()

    assert journal.authority is None
    assert journal.depth == 0
    assert journal.saved_revision == 0
    assert journal.current_revision == 0
    assert not journal.can_undo
    assert not journal.can_redo
    assert journal.pending_resources() == frozenset()
    assert journal.edits() == ()
