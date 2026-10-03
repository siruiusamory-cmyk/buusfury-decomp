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
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")

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
    for _ in range(50):
        qapp.processEvents()

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
    for _ in range(50):
        qapp.processEvents()

    assert shown and "refused this run" in shown[-1]
    assert "Cannot randomize" in window.status_text()


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
