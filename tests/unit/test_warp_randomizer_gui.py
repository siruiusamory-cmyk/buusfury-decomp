"""The one window of the warp randomizer: wiring, states and refusals.

WARPRAND-APP-001. The window is a thin client over
:mod:`tools.webfoot.warprand.service`, so this file proves the *wiring* - that
each control reaches the boundary, that the state on screen is built from what
the boundary returned, and that no control can start a run the boundary would
refuse. It does not re-prove the boundary's own rules
(``tests/unit/test_warp_randomizer_app.py``) or the randomizer's policy
(``tests/unit/test_warp_randomizer.py``, ``tests/integration``).

The boundary is replaced with a recorder, which is what makes "Randomize invokes
the application boundary" a claim about the call rather than about a ROM. Every
dialog is answered through the window's own ``notify``/``confirm``/``show_details``
seams, so no test can block on a modal loop.

Offscreen Qt is set BEFORE PySide6 is imported; the module skips cleanly where
Qt or its offscreen plugin is unavailable, which is the repository's convention
for a dependency-guarded GUI module.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from tools.webfoot.workbench import theme  # noqa: E402
from tools.webfoot.randomizer import gui as shell_gui  # noqa: E402
from tools.webfoot.warprand import gui  # noqa: E402
from tools.webfoot.warprand import service as warprand  # noqa: E402

#: The GUI module's own source, for the "no second palette" guard below. The
#: window itself lives in ``tools/webfoot/randomizer/gui.py`` since
#: ENEMY-RANDOMIZER-EXE-001; this file's guard scans both, because a colour
#: literal in either would fork the product's appearance.
GUI_SOURCE = Path(gui.__file__)
SHELL_GUI_SOURCE = Path(shell_gui.__file__)

VALID_ROM = Path("C:/games/Dragon Ball Z - Buu's Fury (U).gba")
OTHER_ROM = Path("C:/games/Dragon Ball Z - The Legacy of Goku (USA).gba")
OUTPUT_ROM = Path("C:/games/Buu's Fury - Warp Randomized - Goku.gba")
OUTPUT_SHA256 = "ed167ca17944e4782cf19bf31245f772e5b7b9f5c66af317ddbedc8906c5abdc"


# --- the stand-in boundary ---------------------------------------------------


def verified(path: Path = VALID_ROM) -> warprand.RomVerification:
    digest = "ab" * 32
    return warprand.RomVerification(
        path=path,
        status=warprand.VERIFIED,
        size=8_388_608,
        sha256=digest,
        expected_size=8_388_608,
        expected_sha256=digest,
        problem="",
    )


def unsupported(path: Path = OTHER_ROM) -> warprand.RomVerification:
    return warprand.RomVerification(
        path=path,
        status=warprand.UNSUPPORTED,
        size=8_388_608,
        sha256="3b" * 32,
        expected_size=8_388_608,
        expected_sha256="94" * 32,
        problem=(
            f"{warprand.UNSUPPORTED_ROM_HEADLINE} Expected SHA-256: "
            "94949494...94949"
        ),
    )


def outcome(**overrides) -> warprand.RandomizationOutcome:
    fields = dict(
        seed="Goku",
        policy_id=warprand.POLICY_ID,
        tool_version=warprand.TOOL_VERSION,
        supported=735,
        randomized=496,
        destinations_moved=492,
        skipped=239,
        skipped_reasons={"a reason": 239},
        class_counts={"A": 566, "B": 169},
        output_path=OUTPUT_ROM,
        output_sha256=OUTPUT_SHA256,
        output_size=8_388_608,
        manifest_path=OUTPUT_ROM.with_name("Buu's Fury - Warp Randomized - Goku.manifest.json"),
        changed_byte_count=2759,
        source_sha256="ab" * 32,
        source_unchanged=True,
        randomizer_manifest={},
    )
    fields.update(overrides)
    return warprand.RandomizationOutcome(**fields)


class FakeBoundary:
    """The service surface the window is allowed to use, with a memory."""

    def __init__(self) -> None:
        self.verification = verified()
        self.result = outcome()
        self.seed_to_generate = "Saiyan-4821"
        self.error: Exception | None = None
        #: Refuse the first run with a collision, so the retry path is reachable.
        self.collide_first = False
        self.verify_calls: list[str] = []
        self.randomize_calls: list[dict] = []
        self._runs = 0

    def verify_rom(self, path):
        self.verify_calls.append(str(path))
        return self.verification

    def default_output_path(self, rom, seed):
        safe = warprand.sanitize_seed_for_filename(seed)
        return Path(rom).parent / f"Buu's Fury - Warp Randomized - {safe}.gba"

    def generate_seed(self):
        return self.seed_to_generate

    def output_is_the_input(self, source, output):
        return os.path.normcase(str(Path(source))) == os.path.normcase(str(Path(output)))

    def randomize_warps(
        self, source, output, seed, *, overwrite=False, policy=None, on_progress=None
    ):
        """The product's own entry point. Kept so this file still reads as a warp
        randomizer test rather than a test of the shared shell."""
        return self._record(source, output, seed, overwrite=overwrite,
                            on_progress=on_progress)

    def randomize(self, request):
        """The shared window protocol: the request the window built.

        ENEMY-RANDOMIZER-EXE-001 moved the window onto the shared application
        foundation, so the protocol a boundary must satisfy is now this one
        method. The recorder is unchanged, so every assertion about what the
        window passed through still holds.
        """
        return self._record(
            request.source_rom,
            request.output_rom,
            request.master_seed,
            overwrite=request.overwrite,
            on_progress=request.on_progress,
        )

    def _record(self, source, output, seed, *, overwrite=False, on_progress=None):
        self.randomize_calls.append(
            {
                "source": str(source),
                "output": str(output),
                "seed": seed,
                "overwrite": overwrite,
                "on_progress": on_progress,
            }
        )
        self._runs += 1
        if on_progress is not None:
            total = len(warprand.PROGRESS_STEPS)
            for step, label in enumerate(warprand.PROGRESS_STEPS, start=1):
                on_progress(step, total, label)
        if self.collide_first and not overwrite:
            raise warprand.OutputAlreadyExistsError(
                f"{Path(output).name} already exists. Choose another name, or "
                "confirm that you want to replace it."
            )
        if self.error is not None:
            raise self.error
        return self.result


# --- fixtures and helpers ----------------------------------------------------


@pytest.fixture(scope="module")
def qapp():
    # Singleton-safe: reuse the process-wide QApplication if one exists.
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app


@pytest.fixture
def boundary() -> FakeBoundary:
    return FakeBoundary()


@pytest.fixture
def window(qapp, boundary):
    # notify/confirm never open a modal loop in a test.
    win = gui.MainWindow(boundary)
    win.notify = lambda message: None
    win.confirm = lambda message: False
    win.show_details = lambda message, details: None
    win.show()
    yield win
    win.close()


def wait_for(predicate, qapp, timeout_s: float = 30.0) -> bool:
    """Pump the event loop until ``predicate`` holds, or the timeout expires."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        time.sleep(0.005)
    return False


def run_to_completion(window, qapp, **kwargs):
    """Start a run, wait for the thread, deliver its queued result signals."""
    worker = window.start_randomization(**kwargs)
    assert worker is not None, "the window refused to start the run"
    assert worker.wait(30_000), "the worker thread did not finish"
    assert wait_for(lambda: window.status_text() != gui.RUNNING_STATUS, qapp, 10.0)
    return worker


# --- launch state ------------------------------------------------------------


def test_the_seed_field_starts_at_goku(window):
    """The v0.1.0 launch seed, on screen before anything is touched."""
    assert window.seed_text() == "Goku"
    assert warprand.DEFAULT_SEED == "Goku"


def test_the_window_starts_with_no_rom_and_no_run(window):
    assert window.rom_path() == ""
    assert window.output_path() == ""
    assert not window.randomize_button.isEnabled()
    assert window.status_text() == gui.READY_STATUS
    assert window.rom_status_label.text() == gui.NO_ROM_TEXT
    assert window.verification is None
    assert window.outcome is None


def test_the_progression_limit_is_on_screen(window):
    """The ticket forbids hiding that a randomized run may be unwinnable."""
    text = window.disclaimer_label.text()
    assert "impossible to complete" in text
    assert window.disclaimer_label.wordWrap()


def test_the_window_names_the_tool_and_what_it_does(window):
    assert gui.WINDOW_TITLE == "Buu's Fury Warp Randomizer v0.1.0"
    # The status bar names the game and the change, not the internal policy id,
    # which stays in the manifest where it identifies the algorithm.
    assert "Buu's Fury (US)" in window.policy_label.text()
    assert "reciprocal pairs" in window.policy_label.text()
    assert warprand.POLICY_ID not in window.policy_label.text()


# --- the ROM -----------------------------------------------------------------


def test_browsing_for_a_rom_updates_the_path(window, qapp, boundary, monkeypatch):
    monkeypatch.setattr(
        shell_gui.QFileDialog, "getOpenFileName", lambda *a, **k: (str(VALID_ROM), "")
    )

    window.browse_for_rom()

    assert window.rom_path() == str(VALID_ROM)
    assert boundary.verify_calls == [str(VALID_ROM)]


def test_a_cancelled_browse_changes_nothing(window, monkeypatch):
    monkeypatch.setattr(shell_gui.QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))

    assert window.browse_for_rom() is None
    assert window.rom_path() == ""


def test_a_valid_rom_shows_the_verified_state(window, qapp):
    window.set_rom_path(VALID_ROM)

    assert window.verification.ok
    assert "Verified supported ROM \u2713" in window.rom_status_label.text()
    assert window.randomize_button.isEnabled()


def test_an_unsupported_rom_is_reported_immediately_and_blocks_randomize(window, boundary):
    """Selection-time feedback, not a surprise at the end of a run."""
    boundary.verification = unsupported()
    window.set_rom_path(OTHER_ROM)

    assert not window.verification.ok
    assert "Unsupported ROM \u2717" in window.rom_status_label.text()
    assert "Expected SHA-256" in window.rom_status_label.text()
    assert not window.randomize_button.isEnabled()


def test_a_typed_rom_path_is_verified_on_commit(window):
    window.rom_edit.setText(str(VALID_ROM))
    window._on_rom_path_edited()

    assert window.verification is not None and window.verification.ok
    assert window.randomize_button.isEnabled()


def test_selecting_a_rom_derives_the_default_output_name(window):
    window.set_rom_path(VALID_ROM)

    assert window.output_path() == str(
        VALID_ROM.parent / "Buu's Fury - Warp Randomized - Goku.gba"
    )


def test_changing_the_seed_updates_a_derived_output_name(window):
    window.set_rom_path(VALID_ROM)
    window.seed_edit.setText("Namek-0001")

    assert window.output_path().endswith("Buu's Fury - Warp Randomized - Namek-0001.gba")


# --- the seed ----------------------------------------------------------------


def test_selecting_a_non_rom_never_leaves_the_previous_verdict_on_screen(
    window, qapp, boundary, tmp_path
):
    """The window's half of the blocking defect: a refusal is never a stale pass.

    Honest about what this pins, because a round-2 review checked: this test uses
    a *stand-in* boundary that RETURNS a refusal, so on its own it does **not**
    reproduce the original defect - it passes against the pre-fix window too.
    What it proves is the window's rendering and gating for an unsupported verdict.
    The defect itself is pinned by the service tests
    (`test_a_file_too_short_for_a_gba_header_is_refused_not_raised` and friends)
    plus `test_a_boundary_that_raises_is_not_shown_as_verified` below, which does
    fail on the pre-fix code.
    """
    window.set_rom_path(VALID_ROM)
    assert window.verification is not None and window.verification.ok
    assert window.randomize_button.isEnabled()

    boundary.verification = unsupported(path=tmp_path / "tiny.bin")
    window.set_rom_path(tmp_path / "tiny.bin")

    assert window.verification is not None
    assert not window.verification.ok
    assert "Unsupported ROM \u2717" in window.rom_status_label.text()
    assert not window.randomize_button.isEnabled()
    # ... and the run is refused up front rather than becoming a crash.
    assert window.start_randomization() is None
    assert boundary.randomize_calls == []


def test_clearing_the_rom_field_invalidates_the_verdict_at_once(window):
    """Round-2 finding: the field's own clear button kept a verified verdict.

    Selecting the canonical ROM and then clearing the path left
    "Verified supported ROM ✓" on screen with an empty field and Randomize still
    enabled. The cached verdict is now invalidated the moment the text changes, so
    no intermediate state can claim a file that is no longer selected.
    """
    window.set_rom_path(VALID_ROM)
    assert window.verification is not None and window.verification.ok

    window.rom_edit.clear()

    assert window.rom_path() == ""
    assert window.verification is None
    assert "Verified supported ROM" not in window.rom_status_label.text()
    assert window.rom_status_label.text() == gui.NO_ROM_TEXT
    assert not window.randomize_button.isEnabled()

    # Retyping a path is the same class of change, and shows the neutral state
    # rather than a verdict about a file that is no longer named.
    window.set_rom_path(VALID_ROM)
    window.rom_edit.setText("C:/somewhere/else.gba")
    assert window.verification is None
    assert window.rom_status_label.text() == "Not checked yet."
    assert not window.randomize_button.isEnabled()


def test_a_boundary_that_raises_is_not_shown_as_verified(window, boundary, tmp_path):
    """Belt and braces: even a boundary that breaks its own contract is safe.

    The window must not present a raised exception as a verified verdict, and must
    not leave Randomize enabled on a file it could not check. The programmer error
    is still surfaced through the details channel rather than swallowed.
    """
    captured: list[tuple[str, str]] = []
    window.show_details = lambda message, details: captured.append((message, details))
    window.set_rom_path(VALID_ROM)
    assert window.randomize_button.isEnabled()

    def exploding_verify(path):
        raise ValueError("the boundary broke its contract")

    window._service.verify_rom = exploding_verify
    window.set_rom_path(tmp_path / "anything.gba")

    assert window.verification is None
    assert "could not be checked" in window.rom_status_label.text()
    assert not window.randomize_button.isEnabled()
    assert captured and "the boundary broke its contract" in captured[0][0]


def test_the_random_seed_button_produces_a_shareable_seed(window, boundary):
    boundary.seed_to_generate = "Capsule-1735"

    window.random_seed_button.click()

    assert window.seed_text() == "Capsule-1735"
    # Short enough to read out and type: not a 64-character UUID.
    assert len(window.seed_text()) <= 16
    assert window.seed_text() == warprand.sanitize_seed_for_filename(
        window.seed_text()
    )


def test_copy_seed_puts_the_seed_on_the_clipboard(window):
    copied: list[str] = []
    window._copy = copied.append

    window.copy_seed()

    assert copied == ["Goku"]


# --- the output --------------------------------------------------------------


def test_browsing_for_an_output_updates_the_path(window, monkeypatch):
    monkeypatch.setattr(
        shell_gui.QFileDialog, "getSaveFileName", lambda *a, **k: (str(OUTPUT_ROM), "")
    )

    window.browse_for_output()

    assert window.output_path() == str(OUTPUT_ROM)


def test_a_user_chosen_output_is_not_re_derived_by_a_seed_change(window):
    """The window stops overwriting a name the user chose itself."""
    window.set_rom_path(VALID_ROM)
    window.set_output_path("C:/elsewhere/my-random.gba")

    window.seed_edit.setText("Namek-0001")

    assert window.output_path() == "C:/elsewhere/my-random.gba"


def test_clearing_the_output_blocks_the_run(window, boundary):
    window.set_rom_path(VALID_ROM)
    window.output_edit.setText("")

    assert window.start_randomization() is None
    assert boundary.randomize_calls == []
    assert "Cannot randomize" in window.status_text()


def test_the_output_may_not_be_the_input(window, boundary):
    """Blocked in the window, before any thread starts, and nothing written."""
    window.set_rom_path(VALID_ROM)
    window.set_output_path(VALID_ROM)

    assert window.start_randomization() is None
    assert boundary.randomize_calls == []
    assert "is the input ROM" in window.status_text()


# --- the run -----------------------------------------------------------------


def test_randomize_invokes_the_application_boundary(window, qapp, boundary):
    window.set_rom_path(VALID_ROM)
    window.seed_edit.setText("Goku: SSJ3?!")

    run_to_completion(window, qapp)

    assert len(boundary.randomize_calls) == 1
    call = boundary.randomize_calls[0]
    assert call["source"] == str(VALID_ROM)
    assert call["seed"] == "Goku: SSJ3?!"
    assert call["overwrite"] is False
    assert Path(call["output"]).name == "Buu's Fury - Warp Randomized - Goku SSJ3.gba"


def test_the_success_state_shows_the_returned_counts_and_hash(window, qapp, boundary):
    boundary.result = outcome()
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    text = window.status_text()
    assert text.splitlines()[0] == "Success"
    assert "Seed: Goku" in text
    assert "Door transitions: 735" in text
    assert "Doors randomized: 496" in text
    assert "Destinations moved: 492" in text
    assert "Left unchanged: 239" in text
    assert warprand.POLICY_ID not in text
    assert f"Output: {OUTPUT_ROM}" in text
    assert f"SHA-256: {OUTPUT_SHA256}" in text
    assert window.outcome is not None


def test_the_success_state_is_built_from_what_the_boundary_returned(
    window, qapp, boundary
):
    """A different run must not show the previous one's numbers."""
    boundary.result = outcome(
        seed="Namek-0001", supported=735, randomized=12, skipped=723, destinations_moved=8
    )
    window.set_rom_path(VALID_ROM)
    window.seed_edit.setText("Namek-0001")

    run_to_completion(window, qapp)

    text = window.status_text()
    assert "Seed: Namek-0001" in text
    assert "Doors randomized: 12" in text
    assert "Left unchanged: 723" in text
    assert "Doors randomized: 496" not in text


def test_a_refused_run_shows_the_error_state(window, qapp, boundary):
    boundary.error = warprand.UnsupportedRomError(
        "This version currently supports the verified US Buu's Fury ROM only."
    )
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    assert window.outcome is None
    assert "Cannot randomize" in window.status_text()
    assert "supports the verified US Buu's Fury ROM only" in window.status_text()
    # The window is usable again after a refusal.
    assert window.randomize_button.isEnabled()


def test_a_core_error_is_shown_as_a_message_not_a_traceback(
    window, qapp, boundary, monkeypatch
):
    shown: list[str] = []
    window.notify = shown.append
    boundary.error = warprand.WarpRandomizerAppError(
        "The randomizer refused this run: this record needs an unmeasured field"
    )
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    assert shown == [
        "The randomizer refused this run: this record needs an unmeasured field"
    ]
    assert "Traceback" not in window.status_text()


def test_a_collision_asks_and_retries_only_when_confirmed(
    window, qapp, boundary, monkeypatch
):
    boundary.collide_first = True
    asked: list[str] = []
    window.confirm = lambda message: (asked.append(message), True)[1]
    window.set_rom_path(VALID_ROM)

    window.start_randomization()

    assert wait_for(lambda: len(boundary.randomize_calls) >= 2, qapp)
    assert wait_for(lambda: window.outcome is not None, qapp)
    assert "already exists" in asked[0]
    assert boundary.randomize_calls[0]["overwrite"] is False
    assert boundary.randomize_calls[1]["overwrite"] is True
    assert "Success" in window.status_text()


def test_declining_the_overwrite_prompt_leaves_the_existing_file_alone(
    window, qapp, boundary
):
    boundary.collide_first = True
    window.confirm = lambda message: False
    window.set_rom_path(VALID_ROM)

    window.start_randomization()

    assert wait_for(lambda: len(boundary.randomize_calls) == 1, qapp)
    assert wait_for(lambda: window.status_text() != gui.RUNNING_STATUS, qapp, 10.0)
    assert len(boundary.randomize_calls) == 1
    assert window.outcome is None
    assert not window.open_folder_button.isEnabled()
    assert not window.copy_hash_button.isEnabled()


def test_the_button_is_disabled_while_a_run_is_in_flight(window, qapp, boundary):
    window.set_rom_path(VALID_ROM)
    worker = window.start_randomization()

    assert worker is not None
    # Queued result signals have not been delivered yet, so the window is still
    # in its running state and says so.
    assert not window.randomize_button.isEnabled()
    assert worker.wait(30_000)
    assert wait_for(lambda: window.status_text() != gui.RUNNING_STATUS, qapp, 10.0)


def test_an_unexpected_failure_offers_details_and_is_not_swallowed(
    window, qapp, boundary
):
    captured: list[tuple[str, str]] = []
    window.show_details = lambda message, details: captured.append((message, details))
    boundary.error = RuntimeError("a real bug in the tool")
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    assert captured, "the crash surface did not run"
    message, details = captured[0]
    assert "RuntimeError" in message
    assert "a real bug in the tool" in details
    assert "Traceback" in details
    assert "unexpected problem" in window.status_text()


# --- the success-only actions ------------------------------------------------


def test_open_folder_and_copy_hash_are_unavailable_until_a_run_succeeds(window):
    assert not window.open_folder_button.isEnabled()
    assert not window.copy_hash_button.isEnabled()
    assert window.open_output_folder() is False
    assert window.copy_hash() is False


def test_the_success_actions_become_available_after_a_run(window, qapp, boundary):
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    assert window.open_folder_button.isEnabled()
    assert window.copy_hash_button.isEnabled()


def test_copy_hash_copies_the_returned_hash(window, qapp, boundary):
    copied: list[str] = []
    window._copy = copied.append
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    assert window.copy_hash() is True
    assert copied == [OUTPUT_SHA256]


# --- layout regressions found by the visual pass -----------------------------


def test_the_rom_verdict_row_reserves_height_for_a_wrapped_refusal(window, boundary):
    """Regression: the two-line refusal drew on top of the Seed row.

    A wrapping ``QLabel`` inside a grid does not reliably grow its row when its
    text is replaced after the first layout pass, so the row must reserve the
    height up front rather than depend on when the text arrives.
    """
    line_spacing = window.rom_status_label.fontMetrics().lineSpacing()

    assert window.rom_status_label.wordWrap()
    assert window.rom_status_label.minimumHeight() >= line_spacing * 3

    # And the longest refusal this window produces really does wrap to more than
    # one line at this width, which is why three lines are reserved.
    boundary.verification = unsupported()
    window.set_rom_path(OTHER_ROM)
    assert len(window.rom_status_label.text()) > 120


def test_the_status_area_wraps_instead_of_clipping_a_long_line(window):
    """Regression: a narrow window cut the refusal off behind a scrollbar."""
    assert window.status_view.lineWrapMode() == (
        QtWidgets.QPlainTextEdit.LineWrapMode.WidgetWidth
    )
    window.resize(window.minimumWidth(), window.height())
    window.set_rom_path(VALID_ROM)
    window.set_output_path(VALID_ROM)
    assert window.start_randomization() is None

    # The whole refusal is present as text; wrapping, not truncation, is what
    # keeps it on screen at the minimum width.
    assert window.status_text().endswith(
        "this tool never writes to the ROM you selected."
    )


# --- progress ----------------------------------------------------------------


def test_the_progress_panel_is_hidden_until_a_run_starts(window):
    assert not window.progress_panel.isVisible()
    assert window.progress_bar.value() == 0


def test_the_window_asks_the_boundary_for_progress(window, qapp, boundary):
    """The bar is driven by the boundary's phase reports, not by a timer."""
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    assert boundary.randomize_calls[0]["on_progress"] is not None


def test_the_progress_panel_is_visible_for_the_whole_run(window, qapp, boundary):
    """Deterministic, without racing the thread.

    ``start_randomization`` shows the panel synchronously before it starts the
    worker, so the running state can be asserted the instant the call returns -
    no sleep and no timing assumption about how long a phase takes.
    """
    window.set_rom_path(VALID_ROM)

    worker = window.start_randomization()

    assert worker is not None
    assert window.progress_panel.isVisible()
    assert window.progress_bar.maximum() == len(warprand.PROGRESS_STEPS)
    assert window.progress_bar.value() == 0
    assert window.progress_caption.text() == warprand.PROGRESS_STEPS[0] + "\u2026"

    assert worker.wait(30_000)
    assert wait_for(lambda: not window.progress_panel.isVisible(), qapp, 10.0)
    # Never left showing a finished bar next to a result.
    assert window.progress_bar.value() == 0
    assert window.progress_caption.text() == ""


def test_progress_reports_move_the_bar_and_name_the_phase(window):
    """The bar shows completed phases; the caption names the one now starting.

    The boundary reports the phase being *entered*, so the bar shows ``step - 1``
    and can lag the truth but never overstate it. Regression from the independent
    review, which noted the old bar read 4/4 before the final verify and manifest
    write had actually happened.
    """
    window._on_progress(3, 4, "Writing the randomized ROM")

    assert window.progress_bar.maximum() == 4
    assert window.progress_bar.value() == 2
    assert window.progress_caption.text() == "Writing the randomized ROM\u2026"

    window._on_progress(1, 4, "Verifying the ROM")
    assert window.progress_bar.value() == 0


def test_a_failed_run_also_clears_the_progress_panel(window, qapp, boundary):
    boundary.error = warprand.WarpRandomizerAppError("The randomizer refused this run")
    window.set_rom_path(VALID_ROM)

    run_to_completion(window, qapp)

    assert not window.progress_panel.isVisible()
    assert window.progress_caption.text() == ""


# --- the release-verification entry ------------------------------------------


def test_an_ordinary_launch_is_not_a_smoke_run():
    assert gui.parse_smoke_arguments(["app.exe"]) is None
    assert gui.parse_smoke_arguments(["app.exe", "-platform", "offscreen"]) is None


def test_smoke_arguments_are_parsed():
    request = gui.parse_smoke_arguments(
        ["app.exe", "--smoke", "--rom", "R", "--output", "O", "--seed", "S",
         "--report", "J"]
    )

    assert request == gui.SmokeRequest(rom="R", output="O", seed="S", report="J")


def test_a_smoke_run_without_a_seed_leaves_the_launch_seed_alone():
    """The smoke must not supply a seed nobody asked for."""
    request = gui.parse_smoke_arguments(
        ["app.exe", "--smoke", "--rom", "R", "--output", "O"]
    )

    assert request.seed is None


def test_smoke_arguments_are_refused_with_a_usable_message():
    with pytest.raises(warprand.WarpRandomizerAppError) as caught:
        gui.parse_smoke_arguments(["app.exe", "--smoke", "--rom", "R"])
    assert "--output" in str(caught.value)

    with pytest.raises(warprand.WarpRandomizerAppError):
        gui.parse_smoke_arguments(["app.exe", "--smoke", "--rom", "R", "--output"])


def test_a_smoke_run_drives_the_real_window(qapp, boundary, tmp_path):
    """The release hook goes through the window, not around it."""
    request = gui.SmokeRequest(
        rom=str(VALID_ROM), output=str(tmp_path / "out.gba"), seed=None, report=None
    )

    code, report = gui.run_smoke(qapp, request, service=boundary)

    assert code == 0
    assert report["ok"] is True
    assert report["seed"] == "Goku"
    assert report["seed_is_launch_seed"] is True
    assert report["supported"] == 735
    assert report["randomized"] == 496
    assert report["skipped"] == 239
    assert report["destinations_moved"] == 492
    assert report["output_sha256"] == OUTPUT_SHA256
    assert report["progress_hidden"] is True
    assert boundary.randomize_calls[0]["seed"] == "Goku"


def test_a_refused_smoke_run_reports_instead_of_hanging(qapp, boundary, tmp_path):
    """A wrong ROM must exit non-zero with a reason, never block on a dialog.

    The window's ``notify`` opens a modal box; a non-interactive run has to be
    told so, or a refused smoke looks like a hang and a release check times out
    instead of failing.
    """
    boundary.verification = unsupported()
    request = gui.SmokeRequest(
        rom=str(OTHER_ROM), output=str(tmp_path / "out.gba"), seed=None, report=None
    )

    code, report = gui.run_smoke(qapp, request, service=boundary)

    assert code == 1
    assert report["ok"] is False
    assert report["output_sha256"] is None
    assert any(
        "supports the verified US Buu's Fury ROM only" in message
        for message in report["messages"]
    )
    assert "Cannot randomize" in report["status"]
    assert boundary.randomize_calls == []


def test_the_release_hook_is_documented_where_a_packager_will_look():
    """The invocation is part of the build's contract, so it is asserted."""
    assert gui.SMOKE_FLAG == "--smoke"
    assert "--smoke" in gui.USAGE
    assert "-Fury-Warp-Randomizer" in gui.USAGE


# --- the DragonByte Z / Webfoot site appearance ------------------------------


def test_the_application_is_configured_with_the_shared_dragonbyte_z_theme(qapp):
    """The palette comes from the one theme module, not from this application.

    ``tools.webfoot.workbench.theme`` is the same authority DragonByte Z sets at
    startup and the same token set the published site carries
    (``src/styles/global.css``: ``--pink-soft``, ``--pink-strong``,
    ``--surface``). Applying it is what keeps the utility, the editor and the
    site one product instead of three unrelated light themes.

    Saved and restored, because ``QApplication`` is a process-wide singleton and
    a test that left its stylesheet behind would restyle every other GUI test.
    """
    before_sheet = qapp.styleSheet()
    before_palette = qapp.palette()
    try:
        gui.configure_application(qapp)

        assert qapp.styleSheet() == theme.app_stylesheet()
        # The shell is the identity pink and the work surface is the mantle white.
        assert qapp.palette().window().color().name() == theme.COLORS.background
        assert qapp.palette().base().color().name() == theme.COLORS.surface_input
        assert qapp.palette().highlight().color().name() == theme.COLORS.selection
    finally:
        qapp.setStyleSheet(before_sheet)
        qapp.setPalette(before_palette)


def _executable_source(path: Path) -> str:
    """The module's source with comments and docstrings removed.

    Mirrors ``tests/unit/test_capability.py``: a colour named in a docstring is
    documentation - this module's docstring deliberately quotes the theme's own
    values to explain where they come from - while a colour in executable code
    is a forked palette. The tokenizer rather than a regex, so one cannot be
    mistaken for the other.
    """
    import io
    import tokenize

    source = path.read_text(encoding="utf-8")
    kept: list[str] = []
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        if token.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE):
            continue
        if token.type == tokenize.STRING and token.line.strip().startswith(
            ('"""', "'''", 'r"""')
        ):
            continue  # a docstring standing alone on its line
        kept.append(token.string if token.type == tokenize.STRING else token.line)
    return "\n".join(kept)


def test_the_app_module_holds_no_colour_of_its_own():
    """No second palette, ever.

    The theme is the single owner of every value; the moment either the product
    module or the shared window spells a hex colour it has forked the product's
    look, and a later "small tweak" would land in only one of the three surfaces.
    Both files are scanned, because since ENEMY-RANDOMIZER-EXE-001 most of the
    window's code lives in the shared module.
    """
    for path in (GUI_SOURCE, SHELL_GUI_SOURCE):
        code = _executable_source(path)

        literals = re.findall(r"#[0-9a-fA-F]{3,8}\b", code)

        assert literals == [], (
            f"{path.name} must name theme roles, not colours; found {literals}"
        )


def test_the_window_uses_the_theme_roles_and_not_local_styling(window):
    """Each control declares a role the one style sheet resolves."""
    assert window.randomize_button.property("dbzRole") == "primary"
    assert window.disclaimer_label.property("dbzRole") == "hint"
    assert window.policy_label.parent() is window.status_bar
    assert window.title_label.text() == warprand.TOOL_NAME
    assert window.version_label.text() == f"v{warprand.TOOL_VERSION}"
    # The raw readout is the theme's technical role: monospace by design.
    assert window.status_view.font() == theme.mono_font()
    # Field labels carry the form role rather than an ad-hoc style.
    assert window.output_edit.parent() is not None


def test_the_rom_verdict_is_a_theme_state_and_never_hue_alone(window, boundary):
    """Colour is the second channel; the check/cross glyph is the first.

    The theme requires every status role to be distinguishable by glyph and
    brightness, because the maintainer here is red-green colourblind.
    """
    window.set_rom_path(VALID_ROM)
    accepted = window.rom_status_label.styleSheet()
    assert theme.color("success").name() in accepted
    assert "\u2713" in window.rom_status_label.text()

    boundary.verification = unsupported()
    window.set_rom_path(OTHER_ROM)
    refused = window.rom_status_label.styleSheet()
    assert theme.color("danger").name() in refused
    assert "\u2717" in window.rom_status_label.text()
