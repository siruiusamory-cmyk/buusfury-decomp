"""The app's model layer: the project file, the edit list, the plan, the states.

Everything here drives the shared synthetic image, so no ROM and no window are
needed and the gate stays portable.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.gates import REPOSITORY_ROOT
from tests.text_fixture import build, line_payload, lowered_record_floor
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
    path = write(directory, hello_image() if image is None else image, name)
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


# --- states ------------------------------------------------------------------


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
    assert [line.key for line in session.matching(locked=True)] == ["1:32:12"]
    assert len(session.matching(locked=False)) == 1534
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
