"""DRAGONBYTE-Z-RAW-BYTE-AUTHORITY-001: the honest free write.

Five acceptance clauses, each measured here by running it rather than reading it.

1. A raw write into bytes a declared structure owns is refused, names the owner
   once, and creates no change.
2. A raw write into a byte a pending semantic edit has changed is also refused at
   commit, naming that semantic owner.
3. A write into an unowned range creates exactly one entry owned by
   ``raw:<image address>``, the plan accepts it, and ``verify_emitted_image``
   returns exactly that offset.
4. Saving over the canonical digest is refused.
5. The canonical digest is unchanged before and after.

The headless lane runs over a real project on disk and a synthetic base image, so
no canonical ROM is needed to exercise the write path. The canonical-digest lane
skips when the sibling checkout holds no verified image, and never writes one.
"""

from __future__ import annotations

import hashlib
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from tools.webfoot.authored_image import verify_emitted_image  # noqa: E402
from tools.webfoot.binary import GBA_ROM_BASE, FileOffset  # noqa: E402
from tools.webfoot.catalog import load_catalog  # noqa: E402
from tools.webfoot.layout import RomRange  # noqa: E402
from tools.webfoot.project import read_project  # noqa: E402
from tools.webfoot.write import WriteManifest, plan_changes  # noqa: E402

from tools.dragonbyte.journal import (  # noqa: E402
    EditJournal,
    EditKind,
    RawContext,
    RawRequest,
    project_authority,
)
from tools.dragonbyte.rawbytes import (  # noqa: E402
    RAW_DOCUMENT,
    RAW_TARGET,
    RawEdits,
    RawRefusal,
    RawWrite,
    claimed_by,
    raw_change,
    raw_owner,
    read_raw_document,
    write_raw_document,
)
from tools.dragonbyte.session import Session, SessionError  # noqa: E402

from tests.unit.test_dragonbyte_state import (  # noqa: E402
    CANONICAL_SHA256,
    SIBLING_CHECKOUT,
    _write_project,
    qapp,
)


@pytest.fixture(scope="module")
def catalog():
    return load_catalog(None)


@pytest.fixture(scope="module")
def profile(catalog):
    return catalog.profiles[0]


@pytest.fixture(scope="module")
def base(profile) -> bytes:
    """A synthetic image of the profile's size: 0x00 below the free range, 0xFF in it."""
    return bytes(0x1000) + b"\xFF" * (profile.size - 0x1000)


#: An offset below every declared extent, so the bytes there are unowned.
FREE_OFFSET = 0x00001000

#: An offset inside the profile's declared enemy-stat table (0x08711274).
OWNED_OFFSET = 0x00711274

#: A second offset below every declared extent, for a document holding two writes.
SECOND_OFFSET = 0x00002000


def _session(tmp_path: Path, base: bytes) -> Session:
    """A session holding a real project and a synthetic verified base image."""
    project_dir = _write_project(tmp_path / "proj")
    session = Session()
    session.project_dir = project_dir
    session.project = read_project(project_dir)
    session.base_image = base
    session.profile = load_catalog(None).profiles[0]
    session.journal.bind(project_authority(session.project))
    return session


def _raw(offset: int, new: bytes, base: bytes, *, confirmed: bool = True) -> RawRequest:
    return RawRequest(
        write=RawWrite(
            offset=offset,
            before=base[offset : offset + len(new)],
            new=new,
            confirmed=confirmed,
        ),
        context=RawContext(base_image=base, profile=load_catalog(None).profiles[0]),
    )


def _apply_raw(journal: EditJournal, project, request: RawRequest):
    return journal.apply(
        project,
        kind=EditKind.RAW,
        target=RAW_TARGET,
        after=request,
        reason="test raw write",
    )


# --- 1. a declared structure's bytes are refused, named once, unchanged -------


def test_a_raw_write_into_a_declared_structure_is_refused_and_names_the_owner_once(
    tmp_path, base, profile
):
    session = _session(tmp_path, base)
    owner, extent = claimed_by(
        profile, RomRange(FileOffset(OWNED_OFFSET), 1)
    )
    assert owner == "enemy_stats"
    assert extent.start.value == OWNED_OFFSET

    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(OWNED_OFFSET, b"\x01", confirmed=True)

    message = str(refusal.value)
    assert "enemy_stats" in message
    assert message.count("enemy_stats") == 1
    assert "edit that object instead" in message
    assert session.journal.depth == 0
    assert not session.journal.is_dirty
    assert session.journal.edits() == ()
    assert not (session.project_dir / RAW_DOCUMENT).exists()


def test_the_refusal_carries_the_claiming_owner_as_a_field_not_only_a_sentence(
    tmp_path, base
):
    session = _session(tmp_path, base)
    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(OWNED_OFFSET, b"\x01", confirmed=True)
    cause = refusal.value.__cause__
    assert isinstance(cause, RawRefusal)
    assert cause.owner == "enemy_stats"
    assert cause.claimed.start.value == OWNED_OFFSET


def test_an_atlas_object_is_a_third_source_that_also_refuses(tmp_path, base, profile):
    from tools.webfoot.atlas import (
        Atlas,
        AtlasObject,
        Confidence,
        CoverageMap,
        Observation,
        Provenance,
    )

    provenance = Provenance(profile.id, profile.sha256, "test")
    atlas = Atlas(
        profile_id=profile.id,
        base_sha256=profile.sha256,
        image_size=profile.size,
        coverage=CoverageMap.single(
            profile.size, "UNKNOWN", Confidence.OBSERVED, provenance
        ),
        objects=(
            AtlasObject(
                "graphics:0001",
                RomRange(FileOffset(FREE_OFFSET), 16),
                "container",
                Confidence.CONFIRMED,
                provenance,
            ),
        ),
        observations=(),
    )
    span = RomRange(FileOffset(FREE_OFFSET), 1)
    assert claimed_by(profile, span, atlas=atlas) == (
        "atlas:graphics:0001",
        RomRange(FileOffset(FREE_OFFSET), 16),
    )
    assert claimed_by(profile, span) is None

    session = _session(tmp_path, base)
    request = RawRequest(
        write=RawWrite(
            offset=FREE_OFFSET,
            before=base[FREE_OFFSET : FREE_OFFSET + 1],
            new=b"\x01",
            confirmed=True,
        ),
        context=RawContext(base_image=base, profile=profile, atlas=atlas),
    )
    with pytest.raises(RawRefusal) as refusal:
        _apply_raw(session.journal, session.project, request)
    assert refusal.value.owner == "atlas:graphics:0001"
    assert session.journal.depth == 0


# --- 2. a pending semantic edit's bytes are refused at commit -----------------


def test_a_raw_write_into_a_pending_semantic_edits_bytes_is_refused_at_commit(
    tmp_path, base
):
    session = _session(tmp_path, base)
    claimed = RomRange(FileOffset(FREE_OFFSET), 4)
    session.apply_edit(
        kind=EditKind.SEMANTIC,
        target="dialogues",
        after={"goku-greeting": "Hello."},
        claimed=(claimed,),
    )
    assert session.journal.pending_spans() == (claimed,)

    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(FREE_OFFSET, b"\x01", confirmed=True)

    message = str(refusal.value)
    cause = refusal.value.__cause__
    assert isinstance(cause, RawRefusal)
    assert cause.claimed == claimed
    assert "These bytes back" in message
    assert "undo that edit first" in message
    assert cause.owner in message
    assert message.count(cause.owner) == 1
    assert session.journal.depth == 1
    assert session.journal.edits()[0].after == {"goku-greeting": "Hello."}
    assert session.project.dialogues == {"goku-greeting": "Hello."}
    assert session.journal.raw_edits().bytes_by_offset == {}
    assert len(session.journal.edits()) == 1


# --- 3. an unowned range is one entry, planned and verified -------------------


def test_a_write_into_an_unowned_range_is_one_entry_owned_by_the_raw_address(
    tmp_path, base, profile
):
    session = _session(tmp_path, base)
    new = b"\x11\x22"
    session.apply_raw_edit(FREE_OFFSET, new, confirmed=True)

    edits = session.journal.edits()
    assert len(edits) == 1
    entry = edits[0]
    expected_owner = raw_owner(GBA_ROM_BASE + FREE_OFFSET)
    assert entry.owner == expected_owner
    assert entry.owner == "raw:0x08001000"
    assert entry.kind == EditKind.RAW
    assert entry.before == b"\xFF" * len(new)
    assert entry.after == new
    assert session.journal.depth == 1
    assert session.journal.is_dirty
    assert session.journal.raw_edits().bytes_by_offset == {FREE_OFFSET: new}

    change = raw_change(
        RawWrite(offset=FREE_OFFSET, before=b"\xFF" * len(new), new=new)
    )
    plan = plan_changes(
        base, [change], profile_id=profile.id, base_sha256=profile.sha256
    )
    assert plan.changes == (change,)
    assert plan.changed_byte_count == 2
    emitted = bytearray(base)
    emitted[change.offset : change.end] = change.new
    manifest = WriteManifest(
        base_profile_id=profile.id,
        base_sha256=profile.sha256,
        output_sha256=hashlib.sha256(bytes(emitted)).hexdigest(),
        output_size=len(emitted),
        changes=plan.changes,
    )
    assert verify_emitted_image(base, bytes(emitted), plan.changes, manifest) == (
        FREE_OFFSET,
        FREE_OFFSET + 1,
    )


def test_a_write_without_confirmation_is_refused_and_creates_no_change(tmp_path, base):
    session = _session(tmp_path, base)
    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(FREE_OFFSET, b"\x11", confirmed=False)
    message = str(refusal.value)
    assert "asks first" in message
    assert "0x001000" in message
    assert "ff -> 11" in message
    assert "raw:0x08001000" in message
    assert session.journal.depth == 0
    assert session.journal.edits() == ()


def test_a_write_past_the_image_is_refused(tmp_path, base):
    session = _session(tmp_path, base)
    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(len(base) - 1, b"\x01\x02", confirmed=True)
    assert "is not a 2-byte range inside the" in str(refusal.value)
    assert session.journal.depth == 0
    assert session.journal.edits() == ()


def test_the_raw_document_round_trips_through_a_save_and_an_undo(tmp_path, base):
    session = _session(tmp_path, base)
    new = b"\x11\x22"
    session.apply_raw_edit(FREE_OFFSET, new, confirmed=True)
    session.save_project()
    assert not session.journal.is_dirty
    assert read_raw_document(session.project_dir / RAW_DOCUMENT).bytes_by_offset == {
        FREE_OFFSET: new
    }
    # The document the SDK's own reader loads is untouched and still valid.
    assert read_project(session.project_dir).meta.name == "test-project"

    session.undo_edit()
    session.save_project()
    assert session.journal.raw_edits().bytes_by_offset == {}
    assert not (session.project_dir / RAW_DOCUMENT).exists()

    session.redo_edit()
    assert session.journal.raw_edits().bytes_by_offset == {FREE_OFFSET: new}
    session.save_project()
    assert read_raw_document(session.project_dir / RAW_DOCUMENT).bytes_by_offset == {
        FREE_OFFSET: new
    }


def test_a_second_write_to_one_field_replaces_it_and_one_undo_returns_to_base(
    tmp_path, base
):
    session = _session(tmp_path, base)
    session.apply_raw_edit(FREE_OFFSET, b"\x11\x22", confirmed=True)
    session.apply_raw_edit(FREE_OFFSET, b"\x33\x44", confirmed=True)

    edits = session.journal.edits()
    assert len(edits) == 2
    assert edits[0].before == b"\xFF\xFF"
    assert edits[0].after == b"\x11\x22"
    assert edits[1].before == b"\x11\x22"
    assert edits[1].after == b"\x33\x44"
    assert session.journal.raw_edits().bytes_by_offset == {FREE_OFFSET: b"\x33\x44"}

    session.undo_edit()
    assert session.journal.raw_edits().bytes_by_offset == {FREE_OFFSET: b"\x11\x22"}
    session.undo_edit()
    assert session.journal.raw_edits().bytes_by_offset == {}
    session.redo_edit()
    session.redo_edit()
    assert session.journal.raw_edits().bytes_by_offset == {FREE_OFFSET: b"\x33\x44"}


def test_a_partial_overlap_with_a_pending_raw_write_is_refused(tmp_path, base):
    session = _session(tmp_path, base)
    session.apply_raw_edit(FREE_OFFSET, b"\x11\x22\x33\x44", confirmed=True)

    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(FREE_OFFSET + 2, b"\x55\x66", confirmed=True)

    message = str(refusal.value)
    assert "overlaps without replacing" in message
    assert "0x001000" in message
    assert len(session.journal.edits()) == 1
    assert session.journal.raw_edits().bytes_by_offset == {
        FREE_OFFSET: b"\x11\x22\x33\x44"
    }


def test_a_refused_raw_write_leaves_the_pending_document_exactly_as_it_was(
    tmp_path, base
):
    """A refusal after the replacement check must not consume the pending write.

    The document the journal reports and the entries it holds have to agree after
    every refusal, or a Save writes a state nobody asked for and the next write
    records a `before` the image never held.
    """
    session = _session(tmp_path, base)
    session.apply_raw_edit(FREE_OFFSET, b"\x11\x22", confirmed=True)
    pending = session.journal.raw_edits().bytes_by_offset
    assert pending == {FREE_OFFSET: b"\x11\x22"}

    with pytest.raises(SessionError):
        session.apply_raw_edit(FREE_OFFSET, b"\x33\x44", confirmed=False)

    assert session.journal.raw_edits().bytes_by_offset == pending
    assert [entry.after for entry in session.journal.edits()] == [b"\x11\x22"]
    assert session.journal.is_dirty
    session.save_project()
    assert read_raw_document(session.project_dir / RAW_DOCUMENT).bytes_by_offset == pending


def test_a_semantic_claim_between_two_raw_writes_does_not_consume_the_first(
    tmp_path, base
):
    """The other refusal that lands after the replacement check."""
    session = _session(tmp_path, base)
    session.apply_raw_edit(FREE_OFFSET, b"\x11\x22", confirmed=True)
    pending = session.journal.raw_edits().bytes_by_offset
    session.apply_edit(
        kind=EditKind.SEMANTIC,
        target="dialogues",
        after={"goku-greeting": "Hello."},
        claimed=(RomRange(FileOffset(FREE_OFFSET), 4),),
    )

    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(FREE_OFFSET, b"\x33\x44", confirmed=True)

    assert "These bytes back" in str(refusal.value)
    assert session.journal.raw_edits().bytes_by_offset == pending
    session.save_project()
    assert read_raw_document(session.project_dir / RAW_DOCUMENT).bytes_by_offset == pending


def test_opening_a_project_that_authors_raw_bytes_keeps_them(tmp_path, base):
    """A project's authored raw bytes survive a reopen, unaffected by new writes.

    The document on disk is the base a session replays onto. Rebuilding from this
    session's entries alone would drop every byte authored by an earlier session
    and, at an empty cursor, delete the document outright.
    """
    project_dir = _write_project(tmp_path / "proj")
    write_raw_document(project_dir, RawEdits({FREE_OFFSET: b"\x11"}))
    assert read_raw_document(project_dir / RAW_DOCUMENT).bytes_by_offset == {
        FREE_OFFSET: b"\x11"
    }

    session = Session()
    session.base_image = base
    session.profile = load_catalog(None).profiles[0]
    session.open_project(project_dir)

    assert session.journal.raw_edits().bytes_by_offset == {FREE_OFFSET: b"\x11"}
    session.apply_raw_edit(SECOND_OFFSET, b"\x33", confirmed=True)
    session.save_project()
    assert read_raw_document(project_dir / RAW_DOCUMENT).bytes_by_offset == {
        FREE_OFFSET: b"\x11",
        SECOND_OFFSET: b"\x33",
    }


# --- the non-blocking findings, each measured ---------------------------------


def test_an_undone_semantic_edit_stops_claiming_its_bytes(tmp_path, base):
    """Only the applied prefix claims bytes. A redo tail claims nothing."""
    session = _session(tmp_path, base)
    claimed = RomRange(FileOffset(FREE_OFFSET), 4)
    session.apply_edit(
        kind=EditKind.SEMANTIC,
        target="dialogues",
        after={"goku-greeting": "Hello."},
        claimed=(claimed,),
    )
    session.undo_edit()
    assert session.journal.pending_spans() == ()

    session.apply_raw_edit(FREE_OFFSET, b"\x11", confirmed=True)

    assert session.journal.raw_edits().bytes_by_offset == {FREE_OFFSET: b"\x11"}


def test_a_write_that_reaches_into_an_atlas_object_is_refused(tmp_path, base, profile):
    """Overlap with an object, not containment of its first byte."""
    from tools.webfoot.atlas import (
        Atlas,
        AtlasObject,
        Confidence,
        CoverageMap,
        Provenance,
    )

    provenance = Provenance(profile.id, profile.sha256, "test")
    atlas = Atlas(
        profile_id=profile.id,
        base_sha256=profile.sha256,
        image_size=profile.size,
        coverage=CoverageMap.single(
            profile.size, "UNKNOWN", Confidence.OBSERVED, provenance
        ),
        objects=(
            AtlasObject(
                "graphics:0001",
                RomRange(FileOffset(FREE_OFFSET), 16),
                "container",
                Confidence.CONFIRMED,
                provenance,
            ),
        ),
    )
    start = FREE_OFFSET - 8
    span = RomRange(FileOffset(start), 16)
    assert not RomRange(FileOffset(FREE_OFFSET), 16).contains(FileOffset(start))
    assert claimed_by(profile, span, atlas=atlas) == (
        "atlas:graphics:0001",
        RomRange(FileOffset(FREE_OFFSET), 16),
    )

    session = _session(tmp_path, base)
    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(start, b"\x11" * 16, confirmed=True, atlas=atlas)

    assert "atlas:graphics:0001" in str(refusal.value)
    assert session.journal.raw_edits().bytes_by_offset == {}


def test_a_same_offset_write_of_another_length_gets_the_overlap_refusal(
    tmp_path, base
):
    """The journal's own refusal, not the resize message S8 owns."""
    session = _session(tmp_path, base)
    session.apply_raw_edit(FREE_OFFSET, b"\x11\x22\x33\x44", confirmed=True)

    with pytest.raises(SessionError) as refusal:
        session.apply_raw_edit(FREE_OFFSET, b"\x55\x66", confirmed=True)

    message = str(refusal.value)
    assert "overlaps without replacing" in message
    assert "resize" not in message
    assert len(session.journal.edits()) == 1


def test_the_canonical_refusal_compares_the_profile_digest_not_the_file_itself(
    tmp_path,
):
    """A GBA image at the destination is not a copy of the canonical ROM.

    Comparing a file with its own digest refuses every image and mislabels it, so
    the digest compared against has to be the profile's canonical one. Only an
    image that really is the canonical copy is refused as one.
    """
    canonical = _canonical_image()
    other = tmp_path / "other.gba"
    other.write_bytes(canonical.read_bytes()[:0xC0] + bytes(0x400))
    assert other.is_file()

    session = _session(tmp_path, canonical.read_bytes())
    session.open_rom(canonical)
    session.project_dir = other
    session.apply_raw_edit(FREE_OFFSET, b"\x11", confirmed=True)

    with pytest.raises(SessionError) as refusal:
        session.save_project()

    assert "is a copy of the canonical ROM" not in str(refusal.value)


def test_an_owned_range_is_refused_without_asking_a_person(
    qapp, tmp_path, base, monkeypatch
):
    """The refusal costs no confirmation, and a free write shows pending bytes."""
    from PySide6.QtWidgets import QMessageBox

    from tests.unit.test_dragonbyte_state import _close, _shell

    session = _session(tmp_path, base)
    shell = _shell(tmp_path, session)
    asked: list[str] = []
    reported: list[str] = []

    def question(_parent, _title, text, *_args, **_kwargs):
        asked.append(text)
        return QMessageBox.StandardButton.Yes

    def warning(_parent, _title, text, *_args, **_kwargs):
        reported.append(text)
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "question", question)
    monkeypatch.setattr(QMessageBox, "warning", warning)

    # Both modals are answered offscreen and the window is closed before any
    # assertion, so a failure reports instead of blocking on closeEvent.
    try:
        shell.apply_raw_write(OWNED_OFFSET, b"\x01")
        owned_asked, owned_reported = list(asked), list(reported)
        owned_edits = session.journal.edits()
        shell.apply_raw_write(FREE_OFFSET, b"\x11\x22")
        first = asked[0] if asked else ""
        shell.apply_raw_write(FREE_OFFSET, b"\x33\x44")
        second = asked[1] if len(asked) > 1 else ""
    finally:
        _close(shell, session)

    assert owned_asked == [], "an owned range must not cost a confirmation"
    assert "enemy_stats" in "".join(owned_reported)
    assert owned_edits == ()
    assert "raw:0x08001000" in first
    assert "ffff -> 1122" in first
    assert "1122 -> 3344" in second


# --- 4. and 5. the canonical digest ------------------------------------------


def _canonical_image() -> Path:
    roms = SIBLING_CHECKOUT / "roms"
    candidates = sorted(roms.glob("*.gba")) if roms.is_dir() else []
    for candidate in candidates:
        if hashlib.sha256(candidate.read_bytes()).hexdigest() == CANONICAL_SHA256:
            return candidate
    pytest.skip(f"no canonical image in {roms}")


def test_saving_over_the_canonical_digest_is_refused_and_the_digest_is_unchanged(
    tmp_path,
):
    canonical = _canonical_image()
    before = hashlib.sha256(canonical.read_bytes()).hexdigest()
    assert before == CANONICAL_SHA256

    session = _session(tmp_path, canonical.read_bytes())
    session.open_rom(canonical)
    session.apply_raw_edit(0x00000004, b"\x01", confirmed=True)
    # The destination becomes the ROM itself: a save has nowhere to go but over
    # the canonical image, which is the one write every guard exists to prevent.
    session.project_dir = canonical

    with pytest.raises(SessionError) as refusal:
        session.save_project()

    assert "refusing to save" in str(refusal.value)
    assert "canonical" in str(refusal.value)
    after = hashlib.sha256(canonical.read_bytes()).hexdigest()
    assert after == before == CANONICAL_SHA256
    assert len(canonical.read_bytes()) == 8388608
    assert canonical.is_file()
    assert session.has_rom and session.has_project


def test_a_session_holds_the_opened_base_image_bytes(tmp_path):
    canonical = _canonical_image()
    session = Session()
    session.open_rom(canonical)
    assert session.base_image is not None
    assert len(session.base_image) == 8388608
    assert hashlib.sha256(session.base_image).hexdigest() == CANONICAL_SHA256
    assert hashlib.sha256(canonical.read_bytes()).hexdigest() == CANONICAL_SHA256
