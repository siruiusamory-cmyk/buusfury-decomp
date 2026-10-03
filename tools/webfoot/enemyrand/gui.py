"""The one window of the standalone *Enemy Randomizer*.

A product configuration of :class:`tools.webfoot.randomizer.gui.RandomizerWindow`
and nothing else. Everything visible here is a word, a default or a module id; the
ROM row, the verdict, the seed controls, the output derivation, the progress panel,
the worker thread and the four failure outcomes are the shared implementation the
warp executable also uses.

What the window says, and what it refuses to say
================================================

The two toggles are named for what they do - **shuffle enemy placements** and
**randomize enemy stats** - and neither implies that an enemy's species changes.
There is no third toggle for enemy types, not even a disabled one, because the
module is not registered at all: a greyed-out "enemy type randomization" checkbox
would advertise a capability, and the honest statement is that the tool does not
have it. The disclaimer says so in words, and every manifest records
``delivers_ticket_module_c: false``.

The progression disclaimer is deliberately two sentences: what varies, and what
does not. A streamer reading it should be able to tell that a level-1 area cannot
receive an endgame number and that nothing is being retyped.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from ..randomizer.errors import RandomizerAppError
from ..randomizer.gui import (
    SMOKE_FLAG,
    ModuleToggle,
    ProductPresentation,
    RandomizeWorker,
    RandomizerWindow,
    SmokeRequest,
    configure_application as _configure_application,
    drive_smoke,
    parse_smoke_arguments as _parse_smoke_arguments,
)
from . import service as enemyrand

__all__ = [
    "MainWindow",
    "NO_ROM_TEXT",
    "READY_STATUS",
    "ROM_FILTER",
    "RUNNING_STATUS",
    "RandomizeWorker",
    "SMOKE_FLAG",
    "SmokeRequest",
    "USAGE",
    "WINDOW_TITLE",
    "configure_application",
    "main",
    "parse_smoke_arguments",
    "run_smoke",
]

#: The window title, and so the OS title bar's text and the task-bar entry.
WINDOW_TITLE = f"{enemyrand.TOOL_NAME} v{enemyrand.TOOL_VERSION}"

#: The file dialog filter. GBA first, everything else still reachable, because a
#: user whose dump is named ``.bin`` should not be told their file cannot be seen.
ROM_FILTER = "Game Boy Advance ROM (*.gba *.agb *.bin);;All files (*)"

#: The status shown before anything has happened.
READY_STATUS = "Ready. Choose your clean US Buu's Fury ROM."

#: While a run is in flight.
RUNNING_STATUS = "Randomizing..."

#: The placeholder for the ROM row before a file is chosen.
NO_ROM_TEXT = "No ROM selected."

#: The executable name the usage text names. The release IS the executable, so a
#: person reading ``--help`` should see the file they double-click.
EXECUTABLE_STEM = "Enemy-Randomizer"

#: This product's presentation.
ENEMY_PRESENTATION = ProductPresentation(
    tool_name=enemyrand.TOOL_NAME,
    tool_version=enemyrand.TOOL_VERSION,
    window_title=WINDOW_TITLE,
    executable_stem=EXECUTABLE_STEM,
    ready_status=READY_STATUS,
    rom_placeholder="Select your clean US Buu's Fury ROM",
    rom_dialog_title="Select your clean US Buu's Fury ROM",
    choose_rom_first="Choose your clean US Buu's Fury ROM first.",
    output_placeholder="The randomized ROM to create (a new file, never your ROM)",
    output_dialog_title="Choose the randomized ROM to create",
    choose_output="Choose an output file name for the randomized ROM.",
    output_is_input=(
        "The output file is the input ROM. Choose a different output name; this "
        "tool never writes to the ROM you selected."
    ),
    default_seed=enemyrand.DEFAULT_SEED,
    output_template=enemyrand.OUTPUT_TEMPLATE,
    disclaimer=enemyrand.PROGRESSION_DISCLAIMER,
    # The status bar states what this product does to *which* game and version,
    # which is the provenance a user can check without opening a file. The ROM
    # itself is verified against the packaged profile, so "US" here is the same
    # fact the refusal sentence quotes.
    status_note=(
        "Dragon Ball Z: Buu's Fury (US) - placements and stats; species are not "
        "changed"
    ),
    module_toggles=(
        ModuleToggle(
            module_id="enemy-placement",
            label="Shuffle enemy placements",
            help=(
                "Shuffles eligible ordinary enemies among proven existing "
                "placements in the same map. No spawn is created and no coordinate "
                "is invented."
            ),
        ),
        ModuleToggle(
            module_id="enemy-stat",
            label="Randomize enemy stats",
            help=(
                "Randomizes supported enemy stats within safe bounds, scaling each "
                "record around its own original values so the game's general "
                "progression is preserved."
            ),
        ),
    ),
    offers_spoiler=True,
    # ON by default: the manifest is written either way, and a spoiler is the
    # readable form of the same record. Nothing opens it automatically, so a blind
    # run is still blind - the file simply exists if it is wanted afterwards.
    spoiler_default=True,
    spoiler_label="Generate spoiler log",
    spoiler_help=(
        "Writes a readable record of what changed: which enemy stands where and "
        "what its stats became. It is never opened for you, so this does not spoil "
        "a blind run unless you open it."
    ),
    preset_label="STREAM SAFE",
    preset_help=(
        "The conservative preset: both proven modules on, enemy stats scaled "
        "within 0.75x-1.35x of each record's own values. This restores exactly the "
        "defaults, so it cannot drift from what the core ships."
    ),
    options_title="Randomization",
    running_status=RUNNING_STATUS,
    no_rom_text=NO_ROM_TEXT,
)


class MainWindow(RandomizerWindow):
    """The single window. Construct it with a boundary, ``show()``, done."""

    def __init__(self, service=None, *, parent=None) -> None:
        super().__init__(
            ENEMY_PRESENTATION,
            service if service is not None else enemyrand.default_service(),
            parent=parent,
        )


def configure_application(app: QApplication) -> None:
    """Name the application and apply the one DragonByte Z theme to it."""
    _configure_application(app, ENEMY_PRESENTATION)


# --- the release-verification entry ------------------------------------------

#: Printed by ``--help``. Short, because the whole product is short.
USAGE = f"""\
{enemyrand.TOOL_NAME} v{enemyrand.TOOL_VERSION}

  {EXECUTABLE_STEM}                       open the window

  {EXECUTABLE_STEM} {SMOKE_FLAG} --rom <rom> --output <rom>
      [--seed <seed>] [--report <file>] [--without <modules>] [--no-spoiler]
        perform one run through the same window and write a JSON report.
        Used to verify a packaged release without a human at the keyboard.

  --without enemy-placement,enemy-stat   disable a module for this one run
  --no-spoiler                           do not write the spoiler log
"""


def parse_smoke_arguments(argv: list[str]) -> SmokeRequest | None:
    """The smoke request in ``argv``, or ``None`` for an ordinary launch."""
    return _parse_smoke_arguments(
        argv,
        usage=USAGE,
        extra_flags=("--without",),
        boolean_flags=("--no-spoiler",),
    )


def _apply_options(window: RandomizerWindow, request: SmokeRequest) -> None:
    """Apply the smoke run's product-specific flags to the real window.

    Goes through the same widgets the user would touch, so a smoke that disables a
    module proves the *window's* module selection reaches the boundary rather than
    proving a parameter can be passed around it.
    """
    without = request.options.get("without")
    if without:
        wanted = {name.strip() for name in without.split(",") if name.strip()}
        unknown = wanted - set(enemyrand.MODULE_IDS)
        if unknown:
            raise RandomizerAppError(
                f"--without: unknown module(s): {', '.join(sorted(unknown))}"
            )
        for module_id, check in window.module_checks.items():
            check.setChecked(module_id not in wanted)
    if request.options.get("no-spoiler"):
        if window.spoiler_check is not None:
            window.spoiler_check.setChecked(False)


def run_smoke(
    app: QApplication,
    request: SmokeRequest,
    *,
    service=None,
    timeout_ms: int = 600_000,
) -> tuple[int, dict]:
    """Drive one real run through the real window and report what happened.

    Everything here goes through the window's own public path - the same
    :meth:`MainWindow.set_rom_path` the Browse button calls, the same
    :meth:`MainWindow.start_randomization` the Randomize button calls - so a
    passing smoke is evidence about the shipped wiring and not about a shortcut
    beside it.
    """
    window = MainWindow(service)
    messages = drive_smoke(
        app,
        window,
        request,
        timeout_ms=timeout_ms,
        apply_options=_apply_options,
    )

    outcome = window.outcome
    report = {
        "tool": enemyrand.TOOL_NAME,
        "version": enemyrand.TOOL_VERSION,
        "ok": outcome is not None,
        "seed": window.seed_text(),
        "seed_is_launch_seed": window.seed_text() == enemyrand.DEFAULT_SEED,
        "modules": sorted(window.enabled_modules()),
        "spoiler": window.spoiler_enabled(),
        "rom": str(request.rom),
        "output": outcome.output_path.as_posix() if outcome else str(request.output),
        "output_sha256": outcome.output_sha256 if outcome else None,
        "manifest": outcome.manifest_path.as_posix() if outcome else None,
        "spoiler_path": (
            outcome.spoiler_path.as_posix()
            if outcome is not None and outcome.spoiler_path is not None
            else None
        ),
        "changed_byte_count": outcome.changed_byte_count if outcome else None,
        "source_sha256": outcome.source_sha256 if outcome else None,
        "source_unchanged": outcome.source_unchanged if outcome else None,
        "delivers_ticket_module_c": (
            outcome.module_section("enemy-stat").get("delivers_ticket_module_c")
            if outcome is not None
            else None
        ),
        "status": window.status_text(),
        "messages": messages,
        "progress_hidden": not window.progress_panel.isVisible(),
    }
    window.close()
    return (0 if outcome is not None else 1), report


def main(argv: list[str] | None = None) -> int:
    """``python -m tools.webfoot.enemyrand`` - show the window and run Qt."""
    arguments = list(sys.argv if argv is None else argv)
    if "--help" in arguments or "-h" in arguments:
        print(USAGE)
        return 0
    try:
        request = parse_smoke_arguments(arguments)
    except Exception as exc:
        print(f"error: {exc}")
        return 2

    app = QApplication(arguments)
    configure_application(app)
    if request is not None:
        try:
            code, report = run_smoke(app, request)
        except Exception as exc:
            print(f"error: {exc}")
            return 2
        if request.report:
            Path(request.report).write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        print(json.dumps(report, indent=2, sort_keys=True))
        return code

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover - the module entry point
    raise SystemExit(main())
