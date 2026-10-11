"""The app's model layer: the project file, the edit list, the plan, the states.

Everything here drives the shared synthetic image, so no ROM and no window are
needed and the gate stays portable.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.gates import REPOSITORY_ROOT
from tests.text_fixture import (
    appearances,
    build,
    with_operand,
    line_payload,
    lowered_record_floor,
    speaking_image,
)
from tools.buufury_text import project as project_file
from tools.buufury_text import session as app_session
from tools.buufury_text.session import RECORD, SLOT, Session, State
from tools.buufury_text.status import PRESENTATION, label
from tools.webfoot import textedit

HELLO = "Say hello!"
SPAN = len(HELLO) * 2  # 20 bytes, the span `simple` declares for it
AT = 0x20


def write(directory, image, name: str = "fixture.gba") -> Path:
    path = Path(directory) / name
    path.write_bytes(image)
    return path


def hello_image(text: str = HELLO, slots=None):
    """One dialogue record carrying `text` at 0x20, plus the real string table."""
    return build(payloads={1: line_payload(text, AT)}, records=[(1, AT, len(text) * 2)],
                 slots=slots)


def opened(directory, image=None, name: str = "fixture.gba", **kwargs) -> Session:
    """A session over a fixture, in the RECORDS view unless asked otherwise.

    The fixture's handle sites are not in this title's event pool, so the
    pool-limited cutter rule contributes no line row. The record-level cases want
    the record view for that reason, and the line cases ask for the line view with
    the one free parameter switched off, which is the same rule.
    """
    path = write(directory, hello_image() if image is None else image, name)
    kwargs.setdefault("view", app_session.RECORDS)
    with lowered_record_floor():
        return app_session.open_image(path, **kwargs)


def record_key(session: Session) -> str:
    return session.model.records[0].key


# --- the project file --------------------------------------------------------


def test_a_project_round_trips_through_its_file(tmp_path: Path) -> None:
    edits = (
        textedit.SlotEdit(slot=1066, old="Videl", new="Lazuli"),
        textedit.RecordEdit(1, 32, 22, HELLO, "Say\x08\x03 hello!"),
        textedit.RecordEdit(2, 59518, 102, "a % sign", "another % sign"),
    )
    project = project_file.Project(rom_sha256="a" * 64, rom_name="Buu's Fury (U).gba",
                                   canonical_sha256="b" * 64, edits=edits)
    path = tmp_path / f"edits{project_file.SUFFIX}"
    project_file.save(project, path)
    assert project_file.load(path) == project


def test_the_same_edits_always_produce_the_same_project_bytes() -> None:
    project = project_file.Project(
        rom_sha256="a" * 64, rom_name="Buu's Fury (U).gba", canonical_sha256=None,
        edits=(textedit.SlotEdit(slot=1, old="one", new="two"),))
    text = project_file.encode(project)
    assert project_file.encode(project) == text
    assert project_file.encode(project_file.decode(text)) == text


def test_a_project_this_build_cannot_read_says_so() -> None:
    digest = "a" * 64
    with pytest.raises(project_file.ProjectFileError, match="format 2"):
        project_file.decode(f'[project]\nformat = 2\nrom_sha256 = "{digest}"\n')
    with pytest.raises(project_file.ProjectFileError, match="no \\[project\\] table"):
        project_file.decode("[edits]\n")
    with pytest.raises(project_file.ProjectFileError, match="SHA-256"):
        project_file.decode('[project]\nformat = 1\nrom_sha256 = "nope"\n')
    with pytest.raises(project_file.ProjectFileError, match="'slot' or a 'record'"):
        project_file.decode(f'[project]\nformat = 1\nrom_sha256 = "{digest}"\n'
                            '[edits.000]\nkind = "rename"\nold = "a"\nnew = "b"\n')
    with pytest.raises(project_file.ProjectFileError, match="%XX"):
        project_file.unpack("bad %zz escape")


def test_control_units_survive_the_project_file() -> None:
    text = "a\x08\x03b\x0ac\x00d"
    assert project_file.unpack(project_file.pack(text)) == text


# --- the edit list and the plan ---------------------------------------------


def test_the_edit_list_maps_to_engine_plans(tmp_path: Path) -> None:
    session = opened(tmp_path)
    key = record_key(session)
    session.set_edit(key, "Say bye!")
    plan = session.plan()
    assert plan is not None
    assert [item.target for item in plan.decisions] == [key]
    assert plan.decisions[0].method == textedit.IN_PLACE
    assert session.state(key) is State.EDITED
    assert session.ordered_edits() == (textedit.RecordEdit(1, AT, SPAN, HELLO, "Say bye!"),)


def test_a_growing_line_is_reported_as_a_move(tmp_path: Path) -> None:
    session = opened(tmp_path)
    key = record_key(session)
    session.set_edit(key, "Say hello! and hello again")
    assert session.state(key) is State.WILL_MOVE
    assert session.plan().decisions[0].method == textedit.MOVE


def test_a_string_slot_edit_maps_to_a_slot_plan(tmp_path: Path) -> None:
    session = opened(tmp_path, image=hello_image(slots={1066: "Videl"}))
    assert session.line("text:1066").kind == SLOT
    session.set_edit("text:1066", "Lazul")
    assert session.ordered_edits()[0].slot == 1066
    assert session.state("text:1066") is State.EDITED
    session.set_edit("text:1066", "Lazuli")
    assert session.state("text:1066") is State.WILL_MOVE


def test_an_edit_that_says_what_the_line_already_says_is_not_an_edit(tmp_path: Path) -> None:
    session = opened(tmp_path)
    key = record_key(session)
    session.set_edit(key, "Say bye!")
    assert key in session.edits
    session.set_edit(key, HELLO)
    assert session.edits == {}
    assert session.plan() is None
    assert session.state(key) is State.UNCHANGED


def test_the_meter_reports_both_units_and_the_engines_own_limit(tmp_path: Path) -> None:
    session = opened(tmp_path)
    key = record_key(session)
    session.set_edit(key, "Say bye!")
    meter = session.meter(key)
    assert (meter.chars, meter.bytes) == (8, 16)
    assert (meter.chars_limit, meter.bytes_limit) == (SPAN // 2, SPAN)


def test_headroom_states_a_rows_budget_with_nothing_used(tmp_path: Path) -> None:
    """An untouched row still has a number worth showing: zeros against its own span.

    Measured: the editor's empty state printed one placeholder twice with no number, so
    a writer could not see how much room a line had until after they had spent it. The
    limit is the row's own span, so it is read rather than invented, and the same limit
    is what an edit is then measured against.
    """
    session = opened(tmp_path)
    key = record_key(session)
    assert session.meter(key) is None, "nothing is pending on a fresh row"
    headroom = session.headroom(key)
    assert (headroom.chars, headroom.bytes) == (0, 0)
    assert headroom.bytes_limit == SPAN
    assert headroom.chars_limit == SPAN // 2
    session.set_edit(key, "Say bye!")
    pending = session.meter(key)
    assert pending.bytes_limit == headroom.bytes_limit
    assert pending.bytes > headroom.bytes


def two_line_session(directory) -> Session:
    """One record whose text is two spoken lines, so both share a record."""
    return opened(directory, image=hello_image("One\nTwo"), view=app_session.LINES,
                  cutters_from_pool=False)


def _the_two_lines(session: Session) -> tuple:
    target = record_key(session)
    rows = sorted((row for row in session.lines if row.target == target),
                  key=lambda row: row.position[1])
    assert len(rows) == 2, [row.text for row in rows]
    return rows


def test_two_edits_of_one_record_both_survive(tmp_path: Path) -> None:
    """Measured: editing a second line of one record discarded the first, silently.

    The edit was built from the ORIGINAL record text and stored under the record, so the
    second line's edit overwrote the first and no undo could bring the first back. Each
    edited row is now an entry of its own, carrying its span in the original record, and
    the record's text is rebuilt from the original every time.
    """
    session = two_line_session(tmp_path)
    first, second = _the_two_lines(session)
    # Same-length edits, so this case is about the composition and not about growth,
    # which the plan decides separately.
    session.set_edit(first.key, "Une")
    session.set_edit(second.key, "Tvo")
    assert session.pending_text(first.key) == "Une"
    assert session.pending_text(second.key) == "Tvo"
    assert session.state(first.key) is State.EDITED
    assert session.state(second.key) is State.EDITED
    # One record, so one stored edit, and its text carries both rows.
    assert len(session.edits) == 1
    stored = session.edits[record_key(session)]
    assert stored.new == "Une\nTvo"


def test_clearing_one_line_of_a_record_keeps_the_other(tmp_path: Path) -> None:
    session = two_line_session(tmp_path)
    first, second = _the_two_lines(session)
    session.set_edit(first.key, "First!")
    session.set_edit(second.key, "Second!")
    session.clear_edit(first.key)
    assert session.pending_text(first.key) == first.text
    assert session.pending_text(second.key) == "Second!"
    session.clear_edit(second.key)
    assert session.edited_keys() == ()


def test_a_whole_record_text_composes_with_a_pending_line_edit(tmp_path: Path) -> None:
    """A rename replaces the record's whole text, and a pending line edit survives it.

    Measured: the rename batch built its text from the original record as well, so it
    discarded a pending line edit the same way a second line edit did. A whole-record
    text is now a base the pending rows are re-applied to, and where a row cannot be
    located exactly once the combination is refused rather than guessed.
    """
    session = two_line_session(tmp_path)
    target = record_key(session)
    first, second = _the_two_lines(session)
    session.set_edit(second.key, "Tvo")
    original = session.line(target).text
    # Both changes are the same length as what they replace, so this case is about the
    # composition and not about the record moving.
    renamed = original.replace("One", "Uno", 1)
    assert renamed != original and len(renamed) == len(original)
    session.set_edit(target, renamed, whole=True)
    assert session.pending_text(second.key) == "Tvo"
    # The record's own pending text carries BOTH: the rename it was given and the line
    # edit that was already pending inside it.
    assert session.pending_text(target) == "Uno\nTvo"
    assert session.state(second.key) is State.EDITED




def test_a_base_changed_edit_is_marked_and_never_rebased(tmp_path: Path) -> None:
    first = tmp_path / "first"
    first.mkdir()
    made = opened(first)
    key = record_key(made)
    project = project_file.of(made.model, (textedit.RecordEdit(1, AT, SPAN, HELLO, "Say bye!"),))

    second = tmp_path / "second"
    second.mkdir()
    landed = opened(second, image=hello_image("Different!"), project=project)
    assert landed.base_changed
    assert landed.state(key) is State.BASE_CHANGED
    assert landed.edits[key].old == HELLO
    assert landed.refusals()
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        landed.export(second / "out.gba")


def test_the_same_edit_against_its_own_base_is_not_base_changed(tmp_path: Path) -> None:
    session = opened(tmp_path)
    key = record_key(session)
    project = project_file.of(session.model,
                              (textedit.RecordEdit(1, AT, SPAN, HELLO, "Say bye!"),))
    again = opened(tmp_path, project=project)
    assert not again.base_changed
    assert again.state(key) is State.EDITED


def test_an_edit_whose_line_is_gone_is_reported_not_dropped(tmp_path: Path) -> None:
    session = opened(tmp_path)
    project = project_file.of(session.model,
                              (textedit.SlotEdit(slot=999999, old="gone", new="here"),))
    landed = opened(tmp_path, project=project)
    assert landed.unmatched == ("text:999999",)
    assert landed.state("text:999999") is State.BASE_CHANGED


def test_a_state_is_never_carried_by_hue_alone() -> None:
    for state in State:
        entry = PRESENTATION[state]
        assert entry.icon and entry.glyph and entry.word and entry.marker
        assert entry.glyph in label(state)
        assert entry.word in label(state)
    assert len({entry.word for entry in PRESENTATION.values()}) == len(State)
    assert len({entry.glyph for entry in PRESENTATION.values()}) == len(State)
    assert len({entry.marker for entry in PRESENTATION.values()}) == len(State)


def test_a_line_that_differs_from_retail_is_flagged_separately(tmp_path: Path) -> None:
    retail = write(tmp_path, hello_image(), "retail.gba")
    session = opened(tmp_path, image=hello_image("Say goodbye!"), name="edited.gba",
                     canonical=retail)
    key = record_key(session)
    assert session.differs_from_retail(key) is True
    assert session.state(key) is State.UNCHANGED
    same = opened(tmp_path, image=hello_image(), name="same.gba", canonical=retail)
    assert same.differs_from_retail(record_key(same)) is False


def test_without_a_canonical_reference_differs_is_unknown(tmp_path: Path) -> None:
    session = opened(tmp_path)
    assert session.differs_from_retail(record_key(session)) is None


# --- search, filters and progress -------------------------------------------


def test_search_and_filters_read_the_same_rows(tmp_path: Path) -> None:
    session = opened(tmp_path)
    key = record_key(session)
    session.set_edit(key, "Say bye!")
    assert [line.key for line in session.matching("bye")] == [key]
    assert [line.key for line in session.matching("hello")] == [key]
    assert session.matching("nothing here") == ()
    assert [line.key for line in session.matching(states=frozenset({State.EDITED}))] == [key]
    assert len(session.matching(kind=SLOT)) == 1534
    assert session.counts(RECORD)[State.EDITED] == 1


def test_the_control_unit_filter_and_the_progress_counters(tmp_path: Path) -> None:
    session = opened(tmp_path, image=build(payloads={1: line_payload("He\x08\x03llo", AT)},
                                           records=[(1, AT, 12)]))
    assert [row.key for row in session.matching(kind=RECORD, locked=True)] == ["1:32:12"]
    assert len(session.matching(kind=SLOT, locked=False)) == 1534
    assert session.total(SLOT) == 1534
    assert session.counts(RECORD)[State.UNCHANGED] == 1


# --- per-occurrence rename ---------------------------------------------------


def test_a_rename_hit_carries_the_retail_decision_per_occurrence(tmp_path: Path) -> None:
    retail = write(tmp_path, hello_image("Goten then Videl"), "retail.gba")
    session = opened(tmp_path, image=hello_image("Videl then Videl"), canonical=retail)
    hits = session.rename_hits("Videl")
    assert [hit.decision for hit in hits] == [textedit.KEEP, textedit.RENAME]
    assert [hit.retail for hit in hits] == ["Goten", "Videl"]
    key = record_key(session)
    assert session.rename_text(key, "Videl", "Lazul", frozenset({11})) == "Videl then Lazul"
    assert session.rename_hits("") == ()


# --- export ------------------------------------------------------------------


def test_export_refuses_the_input_file_and_the_original_rom(tmp_path: Path) -> None:
    retail = write(tmp_path, hello_image(), "retail.gba")
    source = write(tmp_path, hello_image(), "source.gba")
    session = opened(tmp_path, name="source.gba", canonical=retail)
    assert session.model.path == source
    before = source.read_bytes()
    session.set_edit(record_key(session), "Say bye!")
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        session.export(source)
    with pytest.raises(textedit.TextEditError, match="REFUSED"):
        session.export(retail)
    target = tmp_path / "exported.gba"
    report = session.export(target)
    assert report["output"] == str(target)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == report["output_sha256"]
    assert source.read_bytes() == before


def test_export_refuses_a_destination_inside_the_protected_rom_directory(
        tmp_path: Path) -> None:
    session = opened(tmp_path)
    session.set_edit(record_key(session), "Say bye!")
    guarded = Path(REPOSITORY_ROOT) / "roms" / "text-tool-refused-output.gba"
    with pytest.raises(textedit.TextEditError, match="protected ROM input"):
        session.export(guarded)
    assert not guarded.exists()


def test_export_replays_from_the_base_and_leaves_it_alone(tmp_path: Path) -> None:
    source = write(tmp_path, hello_image(), "source.gba")
    before = source.read_bytes()
    session = opened(tmp_path, name="source.gba")
    key = record_key(session)
    session.set_edit(key, "Say bye!")
    first = session.export(tmp_path / "one.gba")
    session.set_edit(key, "Say night!")
    second = session.export(tmp_path / "two.gba")
    assert source.read_bytes() == before
    assert first["output_sha256"] != second["output_sha256"]
    assert session.model.path.read_bytes() == before


# --- the line view, speakers, ordering and grouping --------------------------


def lined(directory, **kwargs) -> Session:
    """A session in the LINES view over a fixture, with the cutter filter off."""
    kwargs.setdefault("view", app_session.LINES)
    kwargs.setdefault("cutters_from_pool", False)
    return opened(directory, **kwargs)


def two_lines_image():
    """One covering record and two inner records over one container."""
    return build(payloads={1: line_payload("One line, two line", 0x00)},
                 records=[(1, 0x00, 0x24), (1, 0x00, 0x12), (1, 0x12, 0x12)])


def test_the_dialogue_list_is_lines_and_records_is_a_switch(tmp_path: Path) -> None:
    session = lined(tmp_path, image=two_lines_image())
    assert session.view == app_session.LINES
    assert [row.key for row in session.lines] == ["1:0:18", "1:18:18"]
    assert session.view_size(app_session.RECORDS) == 3
    session.set_view(app_session.RECORDS)
    session.set_order(app_session.STORAGE)
    assert [row.key for row in session.lines] == ["1:0:18", "1:0:36", "1:18:18"]
    assert session.view_size(app_session.LINES) == 2


def test_editing_one_line_leaves_its_sibling_in_the_same_record_alone(tmp_path: Path) -> None:
    session = lined(tmp_path, image=two_lines_image())
    session.set_edit("1:0:18", "One row, ")
    assert session.state("1:0:18") is State.EDITED
    assert session.state("1:18:18") is State.UNCHANGED
    assert session.pending_text("1:18:18") == session.line("1:18:18").text
    # One edit, named by the record the engine reads and writes.
    assert session.edited_keys() == ("1:0:18",)
    assert session.plan().decisions[0].target == "1:0:18"
    meter = session.meter("1:0:18")
    assert (meter.chars, meter.bytes) == (9, 18)
    assert (meter.chars_limit, meter.bytes_limit) == (9, 18)
    assert session.meter("1:18:18") is None


def test_a_line_smaller_than_its_record_edits_only_its_own_span(tmp_path: Path) -> None:
    image = build(payloads={1: line_payload("first\x0asecond", 0x00)},
                  records=[(1, 0x00, 0x18)])
    session = lined(tmp_path, image=image)
    assert [row.key for row in session.lines] == ["1:0:10", "1:12:12"]
    # Neither row is the whole record, so both name it as their target.
    assert [row.target for row in session.lines] == ["1:0:24", "1:0:24"]
    session.set_edit("1:0:10", "FIRST")
    assert session.state("1:0:10") is State.EDITED
    assert session.state("1:12:12") is State.UNCHANGED
    assert session.pending_text("1:12:12") == "second"
    assert session.edited_keys() == ("1:0:24",)
    assert session.plan().decisions[0].target == "1:0:24"
    assert session.line("1:12:12").text == "second"


def test_a_line_shows_the_speaker_the_engine_resolved(tmp_path: Path) -> None:
    with appearances():
        session = lined(tmp_path, image=speaking_image("hello there"))
        row = session.lines[0]
        assert row.speaker == "Lazuli"
        assert row.speaker_label == "Lazuli"
        assert session.speaker_share() == (1, 1)
        assert session.speaker_counts() == {"Lazuli": 1}
        assert [group.label for group in session.grouped(by=app_session.BY_SPEAKER)] == \
            ["Lazuli"]
        assert session.matching(speaker="Lazuli") == session.lines
        assert session.matching(speaker=app_session.UNKNOWN_SPEAKER) == ()


def test_an_unattributed_line_says_which_gap_it_is_and_groups_honestly(
        tmp_path: Path) -> None:
    session = lined(tmp_path, image=hello_image())
    row = session.lines[0]
    # The fixture's record word carries operand 0, which the box constructor sends
    # down its no-art branch, so the honest word is "No portrait".
    assert row.speaker is None
    assert row.portrait == "No portrait"
    assert row.speaker_label == "No portrait"
    assert session.speaker_share() == (0, 1)
    assert [group.label for group in session.grouped(by=app_session.BY_SPEAKER)] == \
        ["No portrait"]
    # No proven map or chapter link exists, so there is exactly one honest group.
    placed = session.grouped(by=app_session.BY_PLACE)
    assert [group.label for group in placed] == [app_session.UNPLACED]
    assert [item.key for item in placed[0].rows] == [row.key]
    assert session.matching(speaker="No portrait") == session.lines
    assert session.matching(speaker=app_session.UNKNOWN_SPEAKER) == ()


def test_the_portrait_gaps_are_named_separately(tmp_path: Path) -> None:
    """Each gap gets its own word, so none of them reads as a guess."""
    party = lined(tmp_path, image=with_operand(hello_image(), 0x03))
    assert party.lines[0].speaker_label == "Party member (depends on save)"

    # An operand the fixture cannot resolve: the real appearance table lives outside
    # a 450 KB image, so nothing names it and the row says so.
    unnamed = lined(tmp_path, image=with_operand(hello_image(), 0x3F))
    assert unnamed.lines[0].speaker_label == "Unknown portrait"

    # Two sites, two operands: one identity, two faces, so nothing is attributed.
    contested_image = build(payloads={1: line_payload("hello there", 0x00)},
                            records=[(1, 0x00, 0x16), (1, 0x00, 0x16)])
    with_operand(contested_image, 0x3F, 0)
    with_operand(contested_image, 0x88, 1)
    contested = lined(tmp_path, image=contested_image)
    assert contested.lines[0].speaker_label == app_session.UNKNOWN_SPEAKER


def test_appearance_order_and_storage_order_can_disagree(tmp_path: Path) -> None:
    """The later line is named first by site, because its handle site comes first."""
    image = build(payloads={1: line_payload("Alpha beta ga", 0x00)},
                  records=[(1, 0x12, 0x12), (1, 0x00, 0x12)])
    session = lined(tmp_path, image=image)
    assert session.order == app_session.APPEARANCE
    assert [row.key for row in session.lines] == ["1:18:18", "1:0:18"]
    session.set_order(app_session.STORAGE)
    assert [row.key for row in session.lines] == ["1:0:18", "1:18:18"]
    assert session.line("1:0:18").first_site == 0x2014
    assert session.line("1:18:18").first_site == 0x2004


def test_a_line_no_proven_site_names_is_still_listed_and_says_so(tmp_path: Path) -> None:
    session = lined(tmp_path, image=hello_image())
    row = session.lines[0]
    assert row.proven is False
    assert row.target == "1:32:20"
    assert session.line(row.key) is row
    session.set_edit(row.key, "Say bye!")
    assert session.state(row.key) is State.EDITED


def test_the_search_term_survives_a_view_change(tmp_path: Path) -> None:
    session = lined(tmp_path, image=two_lines_image())
    assert [row.key for row in session.matching("two")] == ["1:18:18"]
    session.set_view(app_session.RECORDS)
    assert {row.key for row in session.matching("two")} == {"1:18:18", "1:0:36"}
