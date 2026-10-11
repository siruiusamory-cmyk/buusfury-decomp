"""The one window of the Enemy Randomizer: options, preset and wiring.

ENEMY-RANDOMIZER-EXE-001. The window is a thin client over the shared application
foundation, so this file proves the *product configuration* and the wiring that a
user actually touches: that the two toggles exist and default on, that a disabled
module reaches the boundary as a disabled module, that the STREAM SAFE button
restores exactly the declared defaults, and that nothing in the public surface
implies an enemy's species is changed.

The boundary is replaced with a recorder, which is what makes "the window passes
the enabled set through" a claim about the call rather than about a ROM. Offscreen
Qt is set before PySide6 is imported, the repository's convention for a
dependency-guarded GUI module.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")
QtGui = pytest.importorskip("PySide6.QtGui")
QtTest = pytest.importorskip("PySide6.QtTest")

from tools.webfoot.enemyrand import gui  # noqa: E402
from tools.webfoot.randomizer import gui as shell_gui  # noqa: E402
from tools.webfoot.randomizer.errors import (  # noqa: E402
    OutputAlreadyExistsError,
    RandomizerAppError,
)
from tools.webfoot.randomizer.service import (  # noqa: E402
    RandomizerResult,
    RomVerification,
)
from tools.webfoot.workbench import theme  # noqa: E402

VALID_ROM = Path("C:/games/Dragon Ball Z - Buu's Fury (U).gba")
OTHER_ROM = Path("C:/games/Dragon Ball Z - The Legacy of Goku (USA).gba")
OUTPUT_ROM = Path("C:/games/Buu's Fury - Enemy Randomized - StreamBlind-0001.gba")
OUTPUT_SHA256 = "4d" * 32

GUI_SOURCES = (Path(gui.__file__), Path(shell_gui.__file__))


def verified(path: Path = VALID_ROM) -> RomVerification:
    digest = "ab" * 32
    return RomVerification(
        path=path,
        status="verified",
        size=8_388_608,
        sha256=digest,
        expected_size=8_388_608,
        expected_sha256=digest,
        problem="",
    )


def unsupported(path: Path = OTHER_ROM) -> RomVerification:
    return RomVerification(
        path=path,
        status="unsupported",
        size=8_388_608,
        sha256="3b" * 32,
        expected_size=8_388_608,
        expected_sha256="94" * 32,
        problem="This version currently supports the verified US Buu's Fury ROM only.",
    )


def settled(predicate, qapp, timeout_ms: int = 5_000) -> bool:
    """Pump events until ``predicate`` holds, or the deadline passes.

    A fixed number of ``processEvents`` calls is not a synchronization point:
    under ``QT_QPA_PLATFORM=offscreen`` on a contended CI runner, key delivery
    and focus activation are not guaranteed inside any fixed count, so a test
    that pumps twenty times and then asserts can fail on a slow worker while
    passing on a fast one. Waiting on the condition is what makes the assertion
    about behaviour instead of about scheduling. Returns the last reading so a
    caller can assert on it and still get the counterexample.
    """
    deadline = time.monotonic() + timeout_ms / 1000
    while True:
        result = predicate()
        if result or time.monotonic() >= deadline:
            return result
        QtTest.QTest.qWait(5)
        qapp.processEvents()


def quiet(qapp, ms: int = 250) -> None:
    """Let the event queue drain for a bounded moment before reading a negative.

    The counterpart to ``settled``: a test that asserts nothing happened has
    nothing to wait for, so it waits a bounded interval instead. 250 ms is long
    enough for a spurious activation to arrive and short enough not to matter;
    the bounded wait cannot hang a job, unlike an unbounded pump.
    """
    QtTest.QTest.qWait(ms)
    qapp.processEvents()


def outcome(**overrides) -> RandomizerResult:
    fields = dict(
        master_seed="StreamBlind-0001",
        enabled=("enemy-placement", "enemy-stat"),
        module_seeds={"enemy-placement": "a" * 64, "enemy-stat": "b" * 64},
        module_versions={"enemy-placement": 1, "enemy-stat": 1},
        output_path=OUTPUT_ROM,
        output_sha256=OUTPUT_SHA256,
        output_size=8_388_608,
        manifest_path=OUTPUT_ROM.with_name(
            "Buu's Fury - Enemy Randomized - StreamBlind-0001.manifest.json"
        ),
        spoiler_path=OUTPUT_ROM.with_name(
            "Buu's Fury - Enemy Randomized - StreamBlind-0001.spoiler.json"
        ),
        changed_byte_count=3202,
        source_sha256="ab" * 32,
        source_unchanged=True,
        tool_name="Enemy Randomizer",
        tool_version="0.1.0",
        document={
            "modules": {
                "enemy-placement": {"summary_lines": ["Placements moved: 1177"]},
                "enemy-stat": {
                    "summary_lines": ["Enemy records changed: 91"],
                    "delivers_ticket_module_c": False,
                },
            }
        },
    )
    fields.update(overrides)
    return RandomizerResult(**fields)


class FakeBoundary:
    """The service surface the shared window is allowed to use, with a memory."""

    def __init__(self) -> None:
        self.verification = verified()
        self.result = outcome()
        self.seed_to_generate = "Namek-0042"
        self.error: Exception | None = None
        self.collide_first = False
        self.verify_calls: list[str] = []
        self.randomize_calls: list[dict] = []
        self._runs = 0

    def verify_rom(self, path):
        self.verify_calls.append(str(path))
        return self.verification

    def default_output_path(self, rom, seed):
        safe = "".join(c if (c.isalnum() or c in " _-") else " " for c in str(seed))
        safe = " ".join(safe.split()).rstrip(". ") or "seed"
        return Path(rom).parent / f"Buu's Fury - Enemy Randomized - {safe}.gba"

    def generate_seed(self):
        return self.seed_to_generate

    def output_is_the_input(self, source, output):
        return os.path.normcase(str(Path(source))) == os.path.normcase(str(Path(output)))

    def randomize(self, request):
        self.randomize_calls.append(
            {
                "source": str(request.source_rom),
                "output": str(request.output_rom),
                "seed": request.master_seed,
                "enabled": sorted(request.enabled),
                "settings": dict(request.module_settings),
                "spoiler": request.spoiler,
                "overwrite": request.overwrite,
                "on_progress": request.on_progress,
            }
        )
        self._runs += 1
        if request.on_progress is not None:
            steps = gui.enemyrand.PROGRESS_STEPS
            for step, label in enumerate(steps, start=1):
                request.on_progress(step, len(steps), label)
        if self.collide_first and not request.overwrite:
            raise OutputAlreadyExistsError(
                f"{Path(request.output_rom).name} already exists. Choose another "
                "name, or confirm that you want to replace it."
            )
        if self.error is not None:
            raise self.error
        return self.result


@pytest.fixture(scope="module")
def qapp():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app


@pytest.fixture
def boundary() -> FakeBoundary:
    return FakeBoundary()


@pytest.fixture
def window(qapp, boundary):
    win = gui.MainWindow(boundary)
    win.notify = lambda message: None
    win.confirm = lambda message: False
    win.show_details = lambda message, details: None
    win.show()
    yield win
    win.close()


# --- identity and appearance --------------------------------------------------


def test_the_window_names_the_product_and_its_version():
    assert gui.WINDOW_TITLE == "Enemy Randomizer v0.1.0"
    assert gui.enemyrand.TOOL_NAME == "Enemy Randomizer"


def test_the_window_holds_no_colour_of_its_own():
    """One theme for the editor, the site and every randomizer.

    A hex literal in either the product window or the shared one would fork the
    palette into a private copy, which is exactly what the warp product's own
    guard has forbidden since v0.1.0.
    """
    for path in GUI_SOURCES:
        source = path.read_text(encoding="utf-8")
        assert "#" not in _code_only(source), f"{path} names a colour literally"
        assert "QColor(" not in source, f"{path} builds a colour"


def _code_only(source: str) -> str:
    """The source's statements, so a ``#`` in prose is not mistaken for a colour."""
    lines = []
    for line in source.splitlines():
        stripped = line.split("#", 1)[0]
        lines.append(stripped)
    return "\n".join(lines)


# --- the options --------------------------------------------------------------


def test_both_proven_modules_are_offered_and_default_on(window):
    assert set(window.module_checks) == {"enemy-placement", "enemy-stat"}
    assert window.enabled_modules() == {"enemy-placement", "enemy-stat"}


def test_there_is_no_toggle_for_enemy_types_not_even_a_disabled_one(window):
    """"Prefer not showing it at all": a greyed-out box would advertise a feature."""
    labels = " ".join(
        child.text() for child in window.options_group.findChildren(QtWidgets.QCheckBox)
    ).lower()

    assert "type" not in labels
    assert "species" not in labels
    assert "identity" not in labels


def test_the_spoiler_option_is_offered_and_on_by_default(window):
    assert window.spoiler_check is not None
    assert window.spoiler_enabled() is True


def test_the_band_setting_offers_the_cores_own_presets(window):
    combo = window.setting_widgets[("enemy-stat", "stat_band")]

    assert combo.currentData() == "stream-safe"
    assert combo.itemData(0) == "stream-safe", "the shipped default is listed first"
    assert {combo.itemData(index) for index in range(combo.count())} == {
        "stream-safe",
        "chaos",
    }


def test_the_stream_safe_preset_restores_every_declared_default(window):
    window.module_checks["enemy-stat"].setChecked(False)
    window.spoiler_check.setChecked(False)
    band = window.setting_widgets[("enemy-stat", "stat_band")]
    band.setCurrentIndex(band.findData("chaos"))

    window.apply_preset()

    assert window.enabled_modules() == {"enemy-placement", "enemy-stat"}
    assert window.spoiler_enabled() is True
    assert band.currentData() == "stream-safe"


def test_the_progress_plan_follows_the_module_selection(window):
    assert window.progress_phases() == gui.enemyrand.PROGRESS_STEPS

    window.module_checks["enemy-stat"].setChecked(False)

    assert window.progress_phases() == (
        "Verifying the ROM",
        "Shuffling enemy placements",
        "Writing the randomized ROM",
        "Verifying the source ROM and writing the manifest",
    )


# --- the ROM and the run ------------------------------------------------------


def test_a_supported_rom_enables_randomize_and_derives_the_output(window):
    window.set_rom_path(VALID_ROM)

    assert window.randomize_button.isEnabled()
    assert window.output_path().endswith(
        "Buu's Fury - Enemy Randomized - StreamBlind-0001.gba"
    )


def test_an_unsupported_rom_is_reported_immediately_and_blocks_randomize(
    window, boundary
):
    boundary.verification = unsupported()

    window.set_rom_path(OTHER_ROM)

    assert "Unsupported ROM" in window.rom_status_label.text()
    assert not window.randomize_button.isEnabled()


def test_unticking_both_modules_blocks_the_run(window):
    window.set_rom_path(VALID_ROM)
    for check in window.module_checks.values():
        check.setChecked(False)

    assert not window.randomize_button.isEnabled()
    assert window.start_randomization() is None
    assert "Cannot randomize" in window.status_text()


def test_the_window_passes_the_enabled_modules_and_the_spoiler_option_through(
    window, qapp, boundary
):
    window.set_rom_path(VALID_ROM)
    window.seed_edit.setText("StreamBlind-0001")
    window.module_checks["enemy-stat"].setChecked(False)
    window.set_output_path("C:/games/out.gba")

    worker = window.start_randomization()
    assert worker is not None
    assert worker.wait(30_000)

    call = boundary.randomize_calls[-1]
    assert call["enabled"] == ["enemy-placement"]
    assert call["spoiler"] is True
    assert call["seed"] == "StreamBlind-0001"
    assert call["source"] == str(VALID_ROM)


def test_the_window_passes_the_declared_settings_through(window, qapp, boundary):
    window.set_rom_path(VALID_ROM)
    window.set_output_path("C:/games/out.gba")
    band = window.setting_widgets[("enemy-stat", "stat_band")]
    band.setCurrentIndex(band.findData("chaos"))

    worker = window.start_randomization()
    assert worker is not None
    assert worker.wait(30_000)

    assert boundary.randomize_calls[-1]["settings"]["enemy-stat"]["stat_band"] == "chaos"


def test_the_success_block_names_the_seed_the_output_the_manifest_and_the_spoiler(
    window, qapp
):
    window.set_rom_path(VALID_ROM)
    window.set_output_path("C:/games/out.gba")

    worker = window.start_randomization()
    assert worker is not None
    assert worker.wait(30_000)
    assert settled(lambda: "Seed:" in window.status_text(), qapp), (
        "the success block never reached the window"
    )

    status = window.status_text()
    assert "Seed: StreamBlind-0001" in status
    assert "Output:" in status
    assert "Manifest:" in status
    assert "Spoiler:" in status
    assert "Placements moved: 1177" in status
    assert "Enemy records changed: 91" in status


def test_a_core_refusal_is_a_message_not_a_traceback(window, qapp, boundary):
    window.set_rom_path(VALID_ROM)
    window.set_output_path("C:/games/out.gba")
    shown: list[str] = []
    window.notify = shown.append
    boundary.error = RandomizerAppError(
        "The randomizer refused this run: this record needs a field"
    )

    worker = window.start_randomization()
    assert worker is not None
    assert worker.wait(30_000)
    assert settled(lambda: bool(shown), qapp), "the refusal never reached the window"

    assert shown and "refused this run" in shown[-1]
    assert "Cannot randomize" in window.status_text()


# --- layout ------------------------------------------------------------------


def test_no_label_is_clipped_and_no_two_rows_share_a_row(window, qapp, boundary):
    """The geometry the cold review measured, pinned as an invariant.

    Two things are checked at the real window size in its busiest state, where the
    three-line ROM verdict is on screen: a single-line form label fits its own
    widget, and the verdict label does not sit on top of the Seed row that follows
    it. That second one is not hypothetical - the window's own comment records a
    second line landing there before the height was reserved.
    """
    boundary.verification = unsupported()
    window.set_rom_path(OTHER_ROM)
    for _ in range(10):
        qapp.processEvents()
    assert not window.verification.ok

    for label in window.findChildren(QtWidgets.QLabel):
        if not label.isVisible() or label.wordWrap():
            continue
        advance = label.fontMetrics().horizontalAdvance(label.text())
        assert advance <= label.width(), (
            f"{label.text()!r} needs {advance}px in {label.width()}px"
        )

    verdict = window.rom_status_label.geometry()
    assert verdict.height() >= window.rom_status_label.fontMetrics().lineSpacing() * 3
    assert verdict.bottom() < window.seed_edit.geometry().top()
    assert verdict.bottom() < window.output_edit.geometry().top()
    assert window.randomize_button.geometry().bottom() < (
        window.centralWidget().height()
    )


# --- keyboard ----------------------------------------------------------------


def test_enter_performs_the_primary_action(window, qapp, boundary):
    """Enter is the button.

    A Windows user presses Enter to accept the form, and ``QMainWindow`` has no
    default button of its own, so without an explicit binding the key did nothing
    at all on a form whose whole purpose is one action. Routed through the same
    handler the click uses, so Enter can only ever do what the button would.
    """
    window.set_rom_path(VALID_ROM)
    window.set_output_path("C:/games/out.gba")
    assert window.randomize_button.isEnabled()
    window.activateWindow()
    window.rom_edit.setFocus()
    assert settled(lambda: window.rom_edit.hasFocus(), qapp), "the field never took focus"

    QtTest.QTest.keyClick(window.rom_edit, QtCore.Qt.Key.Key_Return)

    assert settled(lambda: bool(boundary.randomize_calls), qapp), (
        "Enter did not reach the boundary"
    )
    worker = window.active_worker
    if worker is not None:
        assert worker.wait(30_000)


def test_enter_does_not_start_a_run_that_the_button_would_refuse(window, qapp, boundary):
    """The disabled state is the guard, so Enter cannot slip past it.

    A negative needs a bounded wait rather than a condition: there is nothing to
    wait for, so the test drains the queue for 250 ms and only then reads the
    empty boundary. Focusing and activating first makes the key delivery real,
    so a later regression that quietly stops delivering the key at all would be
    caught by the positive test above rather than hidden here.
    """
    window.set_rom_path(VALID_ROM)
    window.set_output_path("C:/games/out.gba")
    for check in window.module_checks.values():
        check.setChecked(False)
    assert not window.randomize_button.isEnabled()
    window.activateWindow()
    window.rom_edit.setFocus()
    assert settled(lambda: window.rom_edit.hasFocus(), qapp), "the field never took focus"

    QtTest.QTest.keyClick(window.rom_edit, QtCore.Qt.Key.Key_Return)
    quiet(qapp)

    assert boundary.randomize_calls == []
    assert window.active_worker is None


def test_the_focus_order_reads_down_the_form_and_ends_at_the_primary_action(
    window, qapp
):
    """Tab walks the controls in the order the form is read.

    The two post-success actions are disabled before a run and are deliberately
    left out of this list: the chain Qt keeps contains them, but a disabled widget
    is not a Tab stop, so listing them here would describe a stop the user never
    lands on. The keyboard probe that walks the real key events is what proves the
    distinction, and this pins the order itself.
    """
    window.set_rom_path(VALID_ROM)
    window.set_output_path("C:/games/out.gba")
    for _ in range(5):
        qapp.processEvents()
    assert window.randomize_button.isEnabled()

    chain = [window.rom_edit.nextInFocusChain()]
    for _ in range(40):
        nxt = chain[-1].nextInFocusChain()
        if nxt is chain[0]:
            break
        chain.append(nxt)

    labels: list[str] = []
    for widget in chain:
        if not widget.isEnabled():
            continue
        if isinstance(widget, QtWidgets.QComboBox):
            labels.append(f"choice:{widget.currentText()}")
        elif isinstance(
            widget,
            (QtWidgets.QLineEdit, QtWidgets.QPushButton, QtWidgets.QCheckBox),
        ):
            labels.append(widget.text() or type(widget).__name__)
    assert "Randomize" in labels
    assert "Open Folder" not in labels
    assert "Copy Hash" not in labels
    assert any(label.startswith("choice:") for label in labels)
    # The ROM row is the first stop after the field itself, which is where the
    # chain starts; each field is immediately followed by its own action.
    assert labels[0] == "Browse..."
    seed_index = labels.index("StreamBlind-0001")
    assert labels[seed_index + 1] == "Random Seed"
    assert labels[seed_index + 2] == "Copy Seed"
    assert labels.index("STREAM SAFE") < labels.index("Randomize")


# --- the check box indicator --------------------------------------------------


def _relative_luminance(rgb) -> float:
    channels = []
    for value in rgb:
        channel = value / 255.0
        channels.append(
            channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4
        )
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast(first, second) -> float:
    a, b = _relative_luminance(first), _relative_luminance(second)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def _rgb(colour) -> tuple[int, int, int]:
    return (colour.red(), colour.green(), colour.blue())


def test_a_check_box_draws_a_box_and_not_only_a_tick(window, qapp):
    """A control the user is asked to click has to look like one.

    The platform indicator is a font glyph, and with the label background left
    transparent an unchecked box drew no box at all: measured in the shipped
    window, 227 of the 256 pixels inside the indicator rectangle were the surface
    colour, so the control read as a bullet beside its label. The indicator is
    painted here now, and this pins the two facts that make it a control - a fill
    that is not the panel, and a tick drawn in the contrasting ink.
    """
    box = window.module_checks["enemy-placement"]
    box.setChecked(True)
    for _ in range(5):
        qapp.processEvents()

    image = box.grab().toImage().convertToFormat(
        QtGui.QImage.Format.Format_RGB32
    )
    indicator = box.indicator_rect()
    assert indicator.width() >= 14 and indicator.height() >= 14

    colours: dict[tuple[int, int, int], int] = {}
    for x in range(indicator.width()):
        for y in range(indicator.height()):
            pixel = image.pixelColor(indicator.x() + x, indicator.y() + y)
            rgb = (pixel.red(), pixel.green(), pixel.blue())
            colours[rgb] = colours.get(rgb, 0) + 1
    fill = _rgb(theme.color("accent"))
    ink = _rgb(theme.color("accent_ink"))
    surface = _rgb(theme.color("surface"))

    assert colours.get(fill, 0) > 40, "the checked indicator is not filled with the accent"
    assert colours.get(ink, 0) > 10, "the tick is not drawn in the accent ink"
    assert _contrast(fill, surface) >= 3.0


def test_an_unchecked_box_is_visible_against_the_panel_without_its_label(
    window, qapp
):
    """An unchecked box is nothing but its boundary, so the boundary is the control.

    WCAG 2.1 non-text contrast asks 3:1 for a UI component's visual boundary. The
    theme's ``border_strong`` is a 2.05:1 hairline against this fill - right for a
    separator, wrong for the edge of a control - so the edge is the palette's own
    tertiary neutral and this asserts the ratio rather than the token name.
    """
    box = window.module_checks["enemy-stat"]
    box.setChecked(False)
    for _ in range(5):
        qapp.processEvents()

    image = box.grab().toImage().convertToFormat(
        QtGui.QImage.Format.Format_RGB32
    )
    indicator = box.indicator_rect()
    surface = _rgb(theme.color("surface"))
    # The stroke colour is the edge's most common pixel. The darkest pixel on the
    # edge is a rounded corner blended towards the fill, which is lighter than the
    # stroke rather than part of it.
    edges: dict[tuple[int, int, int], int] = {}
    for x in range(indicator.width()):
        for y in (0, indicator.height() - 1):
            pixel = image.pixelColor(indicator.x() + x, indicator.y() + y)
            rgb = (pixel.red(), pixel.green(), pixel.blue())
            edges[rgb] = edges.get(rgb, 0) + 1
    stroke = max(edges.items(), key=lambda item: item[1])[0]
    assert _contrast(stroke, surface) >= 3.0, (
        f"the unchecked indicator edge is only {_contrast(stroke, surface):.2f}:1 "
        "against the panel"
    )


def test_the_controls_in_one_window_are_all_the_same_height(window, qapp):
    """A row of buttons is one size, including the primary action.

    The primary action used to take the toolbar's height instead of the control
    height, so the emphasized button was drawn two pixels taller than every button
    beside it. The window also had to stop opening 44 px shorter than its own
    layout, which squashed four buttons from 24 px to 22 px without clipping them.
    """
    window.set_rom_path(VALID_ROM)
    for _ in range(5):
        qapp.processEvents()

    buttons = [
        button
        for button in window.findChildren(QtWidgets.QPushButton)
        if button.isVisible()
    ]
    heights = {button.text(): button.height() for button in buttons}
    assert len(set(heights.values())) == 1, heights
    assert set(heights.values()) == {theme.CONTROL_HEIGHT}, heights
    assert window.height() >= window.sizeHint().height() - 1


# --- the release-verification entry ------------------------------------------


def test_the_usage_text_names_the_shipped_executable():
    assert gui.SMOKE_FLAG == "--smoke"
    assert "Enemy-Randomizer" in gui.USAGE
    assert "--without" in gui.USAGE


def test_smoke_arguments_are_parsed_with_the_products_own_flags():
    request = gui.parse_smoke_arguments(
        [
            "app.exe",
            "--smoke",
            "--rom",
            "R",
            "--output",
            "O",
            "--seed",
            "S",
            "--report",
            "J",
            "--without",
            "enemy-stat",
            "--no-spoiler",
        ]
    )

    assert request.rom == "R"
    assert request.output == "O"
    assert request.seed == "S"
    assert request.report == "J"
    assert request.options["without"] == "enemy-stat"
    assert request.options["no-spoiler"] == "1"


def test_an_ordinary_launch_is_not_a_smoke_run():
    assert gui.parse_smoke_arguments(["app.exe"]) is None


def test_a_smoke_run_without_a_rom_says_so():
    with pytest.raises(RandomizerAppError) as caught:
        gui.parse_smoke_arguments(["app.exe", "--smoke", "--rom", "R"])

    assert "--output" in str(caught.value)
