"""The text editor shell: the window, its panes, its menus and its notice."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6.QtWidgets")

from tools.buufury_text import shell as shell_module  # noqa: E402
from tools.buufury_text.session import (  # noqa: E402
    BY_PLACE,
    BY_SPEAKER,
    APPEARANCE,
    LINES,
    RECORDS,
    STORAGE,
    UNGROUPED,
    State,
)
from tests.unit.text_tool_shell_support import (  # noqa: E402, F401
    fixture_handle_pool,
    prose_row,
    qapp,
    select_first,
    window,
    working,
)


def test_the_move_notice_action_selects_the_records_that_carry_the_row(window) -> None:
    """The notice's one action has to land somewhere, and it lands in the list.

    A notice that names records and then does nothing when its button is pressed
    would be worse than no button, so this drives it through the real signal.
    """
    key = prose_row(window)
    loaded = window.session.line(key).text
    window.apply_edit(key, loaded + " and more words")
    window.show_line(key)
    assert window.session.state(key) is State.WILL_MOVE
    covered = window.session.covering(key)
    assert covered, "the fixture's inner record is carried by the outer one"
    assert window.pane.view() == LINES

    window.editor.notice.select_button.click()

    assert window.pane.view() == RECORDS, "the action shows the records it named"
    assert window.pane.selected() in covered


def test_the_notice_action_says_so_when_nothing_can_be_selected(window) -> None:
    """No covering records, no claim: the button is disabled rather than inert."""
    key = select_first(window)
    window.show_line(key)
    notice = window.editor.notice
    assert notice.select_button.isEnabled() == bool(window.session.covering(key))


# --- the window --------------------------------------------------------------


def test_the_window_opens_with_its_first_row_already_shown(window) -> None:
    """The pane selects row 0 while it is built, which is before this window can hear.

    Measured: the editor and the context pane opened empty beside a highlighted row,
    and clicking that same row did nothing, because a table does not report a
    current-row change for the row that is already current.
    """
    selected = window.pane.selected()
    assert selected, "the pane selects a first row"
    assert window._editor_key == selected
    assert window.editor.new_text() == window.session.line(selected).text
    assert window.context.retail.text() != "No line is selected."


def test_the_window_builds_and_every_pane_is_reachable(window) -> None:
    assert [name for name, _pane in window.panes()] == ["list", "editor", "context"]
    assert window.walk_panes() == ("list", "editor", "context")
    key = select_first(window)
    assert window.pane.selected() == key
    assert window.detail_label.text().startswith(key)
    assert window.image_label.text() == "working.gba"
    assert window.state_label.text().startswith("\u00b7 UNCHANGED")
    assert window.windowTitle() == "working.gba - Buu's Fury Text Editor"
    assert window.export_button.isEnabled() is False
    assert window.export_action.toolTip() == shell_module.EXPORT_EMPTY


def test_a_status_message_hands_the_row_identity_back_on_the_next_selection(window) -> None:
    """A message is transient; the row's identity, offset and span are not.

    Measured: eight `showMessage` call sites and no `clearMessage` in the package,
    so the last message, up to a whole `export_reason` sentence, took the status
    bar's left region and kept the selected row's own numbers hidden until the
    window closed.
    """
    first = select_first(window)
    assert window.detail_label.isVisible() is True

    window.prompt_export()  # nothing to export, so the reason takes the region

    assert window.statusBar().currentMessage() == shell_module.EXPORT_EMPTY
    assert window.detail_label.isVisible() is False

    second = next(row.key for row in window.pane.rows() if row.key != first)
    assert window.pane.select_key(second)

    assert window.statusBar().currentMessage() == ""
    assert window.detail_label.isVisible() is True
    assert window.detail_label.text().startswith(second)
    assert "container 0x" in window.detail_label.text()
    assert "span " in window.detail_label.text()


def test_the_view_menu_and_the_pane_stay_in_step_both_ways(window) -> None:
    lines, records = window.view_actions.actions()
    assert lines.isChecked()
    records.trigger()
    assert window.pane.view() == RECORDS
    assert records.isChecked() and not lines.isChecked()
    window.pane.set_view(LINES)
    assert lines.isChecked() and not records.isChecked()

    appearance, storage = window.order_actions.actions()
    storage.trigger()
    assert window.pane.order() == STORAGE
    assert storage.isChecked()
    window.pane.set_order(APPEARANCE)
    assert appearance.isChecked() and not storage.isChecked()

    none, speaker, place = window.group_actions.actions()
    place.trigger()
    assert window.pane.group() == BY_PLACE
    assert place.isChecked()
    speaker.trigger()
    assert window.pane.group() == BY_SPEAKER
    assert speaker.isChecked() and not place.isChecked()
    window.pane.set_group(UNGROUPED)
    assert none.isChecked() and not speaker.isChecked()


def test_the_view_menu_shows_and_hides_a_pane(window) -> None:
    assert window.pane_actions["list"].isChecked() is True
    window.pane_actions["list"].trigger()
    assert window.pane_actions["list"].isChecked() is False
    assert window.pane.isVisible() is False
    window.pane_actions["list"].trigger()
    assert window.pane.isVisible() is True


def test_ctrl_f_focuses_the_search_and_a_term_reaches_the_list(window) -> None:
    rows = len(window.pane.rows())
    assert rows
    window.find_action.trigger()
    assert window.search.hasFocus()
    window.search.setText("Inner")
    assert 0 < len(window.pane.rows()) <= rows
    window.search.setText("zzzz not in this image")
    assert window.pane.rows() == ()
    window.clear_search()
    assert window.search.text() == ""
    assert len(window.pane.rows()) == rows
