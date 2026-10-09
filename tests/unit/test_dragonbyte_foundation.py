"""DRAGONBYTE-Z-FOUNDATION-001: the application package, its session and its window.

Two lanes, deliberately separated.

The headless lane drives the session, the destination registry, the navigation
history, the settings file and the diagnostics text with no ``QApplication`` at
all, and proves that importing those modules leaves PySide6 out of
``sys.modules``. That proof runs in a fresh interpreter, because a suite that has
loaded Qt in this process can no longer answer the question.

The windowed lane runs offscreen and drives the real shell: the six destinations,
the one inspector, the four disabled global actions, back and forward, and a
close that persists settings. Nothing here opens a canonical image except the one
test that needs it, and that test skips when the image is not present.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import pytest  # noqa: E402

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtGui import QAction, QUndoStack  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QLabel,
    QToolBar,
    QToolButton,
)

from tools.dragonbyte import diagnostics, navigation, settings  # noqa: E402
from tools.dragonbyte.destination import (  # noqa: E402
    DESTINATIONS,
    ROM,
    ROM_DESTINATION,
    SEMANTIC,
    Destination,
    destination,
)
from tools.dragonbyte.inspector import (  # noqa: E402
    SUPPORT_STATES,
    InspectorContext,
    InspectorPane,
)
from tools.dragonbyte.navigation import MAX_HISTORY, NavigationHistory  # noqa: E402
from tools.dragonbyte.session import (  # noqa: E402
    RomNotRecognizedError,
    Session,
    SessionError,
)
from tools.dragonbyte.shell import GLOBAL_ACTIONS, Shell  # noqa: E402
from tools.webfoot.release_identity import release_identity  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPOSITORY_ROOT / "tools" / "dragonbyte"

#: The sibling primary checkout, derived from this file's own location rather
#: than written down. Its roms/ directory is where a canonical image lives.
SIBLING_CHECKOUT = Path(__file__).resolve().parents[2].parent / "log1-remake"

#: The registry, as the specification words it: id and label, in strip order.
EXPECTED_DESTINATIONS = (
    ("maps", "Maps"),
    ("entities", "Entities"),
    ("scripts_text", "Scripts & Text"),
    ("graphics", "Graphics"),
    ("data", "Data"),
    ("rom", "ROM"),
)

#: A machine-specific absolute path. The uppercase-or-symbol start after the
#: separator keeps a source escape (``states:\n`` is the two characters ``\``
#: and ``n``) from reading as a path, while a real one always starts a path
#: component with a drive root, a digit or a dot.
DRIVE_PATH = re.compile(r"[A-Za-z]:[\\/]{1,2}(?:[A-Z0-9_.$]|$)")
HOME_PATH = re.compile(r"(?:/Users/|/home/)")

#: The Qt-free modules the headless lane must be able to import with no window.
QT_FREE_MODULES = (
    "tools.dragonbyte",
    "tools.dragonbyte.session",
    "tools.dragonbyte.navigation",
    "tools.dragonbyte.destination",
    "tools.dragonbyte.diagnostics",
    "tools.dragonbyte.settings",
    "tools.dragonbyte.journal",
    "tools.dragonbyte.rawbytes",
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _package_files() -> list[Path]:
    """Every Python file in the application package, in a stable order."""
    return sorted(PACKAGE_ROOT.rglob("*.py"))


def _package_source(module: str) -> str:
    return (PACKAGE_ROOT / module).read_text(encoding="utf-8")


def _imported_names(relative: str, tree: ast.AST) -> list[str]:
    """Every dotted module a parsed file imports, relative spellings resolved.

    Reuses the purity gate's resolver, so the test and the gate cannot disagree
    about what a spelling means.
    """
    from tools.quality import architecture as arch

    return [name for name, _line in arch._imported_modules(relative, tree)]


def _shell(config_directory: Path, session: Session | None = None) -> Shell:
    return Shell(session if session is not None else Session(), config_directory)


def _strip(shell: Shell) -> QToolBar:
    strip = shell.findChild(QToolBar, "destinationStrip")
    assert strip is not None, "the destination strip is missing"
    return strip


def _strip_buttons(shell: Shell) -> list[QToolButton]:
    """The strip's own buttons, in strip order."""
    strip = _strip(shell)
    buttons = []
    for action in strip.actions():
        widget = strip.widgetForAction(action)
        if isinstance(widget, QToolButton):
            buttons.append(widget)
    return buttons


def _shows(button: QToolButton) -> str:
    """The label Qt actually draws: a doubled ampersand is one ampersand, and a
    single one would be a mnemonic and disappear from the screen."""
    return button.text().replace("&&", "&")


def _actions_by_text(shell: Shell) -> dict[str, QAction]:
    return {action.text(): action for action in shell.findChildren(QAction)}


def _run_module(arguments: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the application's module entry point from the repository root."""
    return subprocess.run(
        [sys.executable, "-m", "tools.dragonbyte", *arguments],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        env=env,
    )


# --- 1. the package imports cleanly, headless ---------------------------------


def test_the_package_imports_and_the_qt_free_modules_stay_headless():
    """The headless-lane proof, in a fresh interpreter.

    It runs in a child process on purpose: by the time a suite has built one
    window, PySide6 is in this process's ``sys.modules`` and an in-process
    assertion could no longer tell a clean import from a leaked one.
    """
    probe = (
        "import importlib, sys\n"
        f"for name in {QT_FREE_MODULES!r}:\n"
        "    importlib.import_module(name)\n"
        "leaked = sorted(\n"
        "    name for name in sys.modules\n"
        "    if name == 'PySide6' or name.startswith('PySide6.')\n"
        ")\n"
        "print('LEAKED', leaked)\n"
    )

    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "LEAKED []" in result.stdout, result.stdout


def test_every_qt_free_module_imports_in_this_process():
    import importlib

    for name in QT_FREE_MODULES:
        assert importlib.import_module(name) is not None


# --- 2. the identity has one authority ---------------------------------------


def test_the_window_title_comes_from_the_identity_authority(qapp, tmp_path):
    shell = _shell(tmp_path)

    assert shell.windowTitle() == release_identity().display

    shell.close()


def test_no_package_file_restates_the_version():
    for path in _package_files():
        assert "0.9.0" not in path.read_text(encoding="utf-8"), path


# --- 3 and 4. the destinations -------------------------------------------------


def test_the_registry_and_the_strip_agree_on_the_six_destinations(qapp, tmp_path):
    assert [(item.id, item.label) for item in DESTINATIONS] == list(
        EXPECTED_DESTINATIONS
    )
    shell = _shell(tmp_path)

    labels = [_shows(button) for button in _strip_buttons(shell)]

    assert labels[:6] == [label for _identifier, label in EXPECTED_DESTINATIONS]
    shell.close()


def test_rom_is_the_distinct_last_destination_behind_one_rule(qapp, tmp_path):
    assert ROM_DESTINATION is DESTINATIONS[-1]
    assert ROM_DESTINATION.id == "rom"
    assert [item.group for item in DESTINATIONS[:-1]] == [SEMANTIC] * 5
    assert ROM_DESTINATION.group == ROM
    shell = _shell(tmp_path)

    actions = _strip(shell).actions()

    assert [index for index, item in enumerate(actions) if item.isSeparator()] == [5]
    assert _strip_buttons(shell)[5].text() == "ROM"
    shell.close()


def test_an_unknown_destination_id_is_a_key_error():
    with pytest.raises(KeyError):
        destination("no_such_destination")


# --- 5. exactly one session authority ----------------------------------------


def test_the_shell_owns_exactly_one_session_and_two_shells_do_not_share_it(
    qapp, tmp_path
):
    first_session = Session()
    second_session = Session()
    first = _shell(tmp_path, first_session)
    second = _shell(tmp_path, second_session)

    assert first._session is first_session
    assert second._session is second_session
    assert first._session is not second._session
    first.close()
    second.close()


def test_the_session_is_defined_once_and_carries_no_second_answer_to_dirty():
    definitions = []
    for path in _package_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        definitions.extend(
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name == "Session"
        )

    assert definitions == ["Session"]

    members = {field.name for field in dataclasses.fields(Session)} | set(dir(Session))
    # STATE-001 gave the session exactly one journal, which owns every edit, every
    # checkpoint and the derived dirty state. The rule this test exists for is
    # unchanged, so it is restated rather than dropped: the session holds no
    # independent dirty flag, no edit counter and no second undo stack. Two
    # entries are deliberate and named, because they are the session's edit
    # boundary - `journal` is the one journal, and `undo_edit`/`redo_edit` are
    # thin calls into it, not an undo stack kept here.
    forbidden = ("staged", "dirty", "revision", "unsaved", "undo")
    allowed = {"journal", "undo_edit", "redo_edit"}
    assert [
        name
        for name in members
        if any(word in name for word in forbidden) and name not in allowed
    ] == []
    assert [name for name in members if "journal" in name] == ["journal"]
    assert not hasattr(Session, "register_staged_work")
    assert not hasattr(Session, "unsaved_edit_count")
    assert not hasattr(Session, "undo_stack")
    assert not hasattr(Session, "dirty")


# --- 6. navigation is not edit undo ------------------------------------------


def test_navigation_moves_a_cursor_and_never_creates_entries():
    history = NavigationHistory("maps")

    assert history.current.destination == "maps"
    assert len(history) == 1

    history.push("maps")
    assert len(history) == 1, "pushing the current destination must be a no-op"

    history.push("data")
    history.push("graphics")
    assert len(history) == 3
    assert history.back().destination == "data"

    history.push("rom")
    assert len(history) == 3, "pushing must drop the forward tail"
    assert history.current.destination == "rom"
    assert not history.can_go_forward
    assert history.forward() is None
    assert history.back().destination == "data"
    assert history.can_go_forward
    assert history.forward().destination == "rom"


def test_navigation_trims_the_oldest_entry_at_the_cap():
    history = NavigationHistory()
    for index in range(MAX_HISTORY + 5):
        history.push(f"destination-{index}")

    assert len(history) == MAX_HISTORY
    assert history.current.destination == f"destination-{MAX_HISTORY + 4}"

    steps = 0
    while history.back() is not None:
        steps += 1
    assert steps == MAX_HISTORY - 1
    assert not history.can_go_back
    assert history.back() is None


def test_the_qt_free_modules_hold_no_qt_import_and_no_undo_type():
    for module in ("session.py", "navigation.py"):
        source = _package_source(module)
        assert "QUndo" not in source, module
        tree = ast.parse(source)
        assert "PySide6" not in _imported_names(f"tools/dragonbyte/{module}", tree)


def test_no_module_in_the_package_mentions_an_undo_stack(qapp, tmp_path):
    for path in _package_files():
        assert "QUndo" not in path.read_text(encoding="utf-8"), path
    shell = _shell(tmp_path)

    assert shell.findChildren(QUndoStack) == []
    shell.close()


def test_the_shell_has_one_centre_split_with_no_tabs_and_no_docks(qapp, tmp_path):
    from PySide6.QtWidgets import QDockWidget, QSplitter, QTabWidget

    shell = _shell(tmp_path)

    assert isinstance(shell.centralWidget(), QSplitter)
    assert shell.centralWidget().count() == 2
    assert shell.findChildren(QTabWidget) == []
    assert shell.findChildren(QDockWidget) == []
    shell.close()


def test_the_action_bar_and_the_destination_strip_are_two_bands(qapp, tmp_path):
    """The approved window stacks the two bands. Sharing one row squeezes the
    strip until a destination label elides and Back and Forward fall behind the
    toolbar's overflow chevron."""
    shell = _shell(tmp_path)

    assert shell.toolBarBreak(_strip(shell)) is True
    shell.close()


def test_no_destination_label_is_left_to_elide_in_the_strip(qapp, tmp_path):
    """Measured in the real window: the style sheet's box is wider than the
    button's own size hint, so the longest label elided in a strip with room to
    spare. Every label must have at least its own text width to draw in."""
    shell = _shell(tmp_path)

    for button in _strip_buttons(shell)[:6]:
        needed = button.fontMetrics().horizontalAdvance(button.text())
        assert button.minimumWidth() > needed, button.text()

    shell.close()


def test_a_saved_window_geometry_is_restored(qapp, tmp_path):
    """The size a user leaves the window at is the size it reopens at."""
    first = Shell(Session(), tmp_path)
    # Well inside any screen, because a restored geometry is clamped to one.
    first.resize(620, 460)
    first.close()

    second = Shell(Session(), tmp_path)

    assert (second.size().width(), second.size().height()) == (620, 460)
    second.close()


def test_every_action_has_exactly_one_home(qapp, tmp_path):
    """No action is repeated in a menu and a strip, and navigation is in the
    destination strip, which is the shell's destination-and-navigation region."""
    from PySide6.QtWidgets import QMenu

    shell = _shell(tmp_path)

    menu_actions = set()
    for menu in shell.menuBar().findChildren(QMenu):
        menu_actions.update(menu.actions())
    toolbar_actions = set()
    for bar in shell.findChildren(QToolBar):
        toolbar_actions.update(bar.actions())

    assert menu_actions & toolbar_actions == set()

    strip_actions = [action.text() for action in _strip(shell).actions()]
    assert "Back" in strip_actions
    assert "Forward" in strip_actions
    shell.close()


# --- 7. one inspector ---------------------------------------------------------


def test_the_shell_has_exactly_one_inspector_for_every_destination(qapp, tmp_path):
    shell = _shell(tmp_path)

    assert len(shell.findChildren(InspectorPane)) == 1

    for identifier, _label in EXPECTED_DESTINATIONS:
        shell.show_destination(identifier)

    assert len(shell.findChildren(InspectorPane)) == 1
    shell.close()


def test_the_inspector_empty_state_names_the_destination(qapp, tmp_path):
    shell = _shell(tmp_path)
    pane = shell.findChildren(InspectorPane)[0]

    shell.show_destination("graphics")

    # The pane must not be blank: it names the destination and says nothing is
    # selected. A rendered support state is word plus glyph plus accessible name.
    rendered = " ".join(child.text() for child in pane.findChildren(QLabel))
    assert "Graphics" in rendered
    assert "Nothing is selected" in rendered

    pane.set_context(
        InspectorContext(
            friendly="Placement 037",
            stable="map:0012/placement:0037",
            support="Read-only",
        )
    )
    rendered = " ".join(child.text() for child in pane.findChildren(QLabel))
    assert "map:0012/placement:0037" in rendered
    assert "Read-only" in rendered
    shell.close()


def test_every_support_state_is_one_of_the_approved_words():
    assert SUPPORT_STATES == (
        "Editable",
        "Editable with limits",
        "Read-only",
        "Not supported yet",
        "Not mapped",
        "Not in this game",
    )


# --- 8. the four global actions ----------------------------------------------


def test_the_four_global_actions_are_disabled_and_state_their_reason(qapp, tmp_path):
    shell = _shell(tmp_path)
    actions = _actions_by_text(shell)

    for label, _reason in GLOBAL_ACTIONS:
        action = actions[label]
        assert not action.isEnabled(), label
        assert action.toolTip().strip(), label
        assert "foundation build" in action.toolTip(), label
        button = shell._action_bar.widgetForAction(action)
        assert button is not None
        assert button.accessibleName().startswith(label)
        assert action.toolTip() in button.accessibleName()

    shell.close()


def test_the_shell_offers_no_action_that_reports_success(qapp, tmp_path):
    shell = _shell(tmp_path)
    claim = re.compile(r"\b(?:succe\w*|complete\w*|finished|done)\b", re.IGNORECASE)

    assert [a.text() for a in shell.findChildren(QAction) if claim.search(a.text())] == []

    shell.close()


# --- 9. the architecture gate -------------------------------------------------


def test_the_real_tree_passes_the_gate_and_the_package_never_imports_the_beta():
    from tools.quality import architecture as arch

    assert arch._rule_import_direction(arch.tracked_files()) == []
    assert arch.check()["violations"] == []

    for path in _package_files():
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        beta = [
            name
            for name in _imported_names(relative, tree)
            if name == "tools.webfoot.workbench"
            or name.startswith("tools.webfoot.workbench.")
        ]
        assert beta == [], relative


# --- 10. no machine-specific path in the package ------------------------------


def test_no_package_file_carries_a_machine_specific_absolute_path():
    """No package file names a path on one machine.

    The project's own public-surface screen is the authority on what counts as
    a machine-specific path, so it is asked directly; the local pattern beside
    it catches a drive root the screen's narrower rule does not name.
    """
    from tools.quality import public_surface

    for path in _package_files():
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        findings, _suppressed = public_surface.scan(REPOSITORY_ROOT, relative)
        assert findings == [], findings
        source = path.read_text(encoding="utf-8")
        assert not DRIVE_PATH.search(source), relative
        assert not HOME_PATH.search(source), relative


# --- 11. opening an image never writes it ------------------------------------


def test_a_refused_image_is_byte_identical_after_the_open_attempt(tmp_path):
    image = tmp_path / "not-a-game-image.gba"
    payload = bytes(range(256)) * 8
    image.write_bytes(payload)
    before = hashlib.sha256(image.read_bytes()).hexdigest()
    session = Session()

    with pytest.raises(SessionError):
        session.open_rom(image)

    assert hashlib.sha256(image.read_bytes()).hexdigest() == before
    assert image.read_bytes() == payload
    assert not session.has_rom


def test_a_truncated_image_is_refused_as_a_session_error(tmp_path):
    """A file too short to carry a header is a fact about the input, not a
    programmer error: it must arrive as the boundary type."""
    image = tmp_path / "truncated.gba"
    image.write_bytes(b"short")
    session = Session()

    with pytest.raises(SessionError):
        session.open_rom(image)

    assert not session.has_rom


def test_the_canonical_image_is_unchanged_across_a_session_and_a_window(tmp_path, qapp):
    """A real image, when one is present, is read and never written.

    The sibling checkout's own ``roms/`` directory is derived from this file's
    location. Without a verified image there the test skips: it is evidence
    about a real read, not a synthetic one.
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
    shell = _shell(tmp_path, session)
    shell.close()

    assert hashlib.sha256(opened.read_bytes()).hexdigest() == before
    assert session.has_rom


# --- 12. the offscreen window and the process smoke --------------------------


def test_the_window_runs_offscreen_through_every_destination(qapp, tmp_path):
    session = Session()
    shell = _shell(tmp_path, session)

    assert shell.windowTitle() == release_identity().display
    assert [_shows(button) for button in _strip_buttons(shell)][:6] == [
        label for _identifier, label in EXPECTED_DESTINATIONS
    ]
    assert len(shell.findChildren(InspectorPane)) == 1
    actions = _actions_by_text(shell)
    assert [actions[label].isEnabled() for label, _reason in GLOBAL_ACTIONS] == [
        False
    ] * 4

    for identifier, _label in EXPECTED_DESTINATIONS:
        shell.show_destination(identifier)
        assert session.navigation.current.destination == identifier

    assert session.navigation.can_go_back
    shell.go_back()
    shell.go_forward()
    assert session.navigation.current.destination == "rom"

    config_directory = tmp_path / "config"
    shell2 = Shell(Session(), config_directory)
    shell2.close()
    shell.close()

    saved = config_directory / settings.SETTINGS_FILE
    assert saved.is_file()
    assert settings.Settings.load(config_directory).geometry


def test_the_version_flag_prints_the_identity_and_exits():
    result = _run_module(["--version"])

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == release_identity().display


def test_the_application_starts_and_stays_alive_offscreen():
    environment = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    process = subprocess.Popen(
        [sys.executable, "-m", "tools.dragonbyte"],
        cwd=REPOSITORY_ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    started = process.poll() is None
    assert started, "the application exited as soon as it was started"

    try:
        time.sleep(3)
        assert process.poll() is None, "the application exited during start-up"
    finally:
        process.terminate()
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()


# --- the diagnostics surface --------------------------------------------------


def test_diagnostics_reports_one_line_per_fact():
    session = Session()
    session.navigation.push("maps")
    active = Destination("maps", "Maps", SEMANTIC, "not built")

    text = diagnostics.diagnostics_text(session, active, "Open ROM: refused")
    lines = text.splitlines()

    assert lines[0].startswith("Release: ")
    assert "ROM identity: No ROM open" in lines
    assert "Project identity: No project open" in lines
    assert "Active destination: Maps (maps)" in lines
    assert "Session: ROM not open, project not open" in lines
    assert "Support: Open ROM: refused" in lines
    assert diagnostics.diagnostics_text(session, None).splitlines()[-1] == (
        "Support: none"
    )


# --- the settings surface -----------------------------------------------------


def test_settings_round_trip_and_survive_a_corrupt_file(tmp_path):
    directory = tmp_path / "config"
    saved = settings.Settings(last_directory=str(tmp_path), geometry="Z2VvbWV0cnk=")

    saved.save(directory)
    loaded = settings.Settings.load(directory)

    assert loaded == saved
    assert (directory / settings.SETTINGS_FILE).read_text(encoding="utf-8").endswith(
        "\n"
    )

    (directory / settings.SETTINGS_FILE).write_text("{not json", encoding="utf-8")
    assert settings.Settings.load(directory) == settings.Settings()
    assert settings.Settings.load(tmp_path / "absent") == settings.Settings()


def test_navigation_max_history_is_the_published_cap():
    assert navigation.MAX_HISTORY == 100
