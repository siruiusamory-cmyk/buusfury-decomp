"""WARPRAND-APP-001 - the one window of the *Buu's Fury Warp Randomizer*.

This module is now a **product configuration** of the shared window in
:mod:`tools.webfoot.randomizer.gui` rather than a window of its own. The widgets,
the states, the worker thread, the progress panel, the four failure outcomes and
the collision-confirm-retry cycle all live in that one implementation, which the
enemy executable also uses; what is left here is what is genuinely warp-specific:

* the words - the product name, the ROM prompt, the refusals, the disclaimer;
* the launch seed and the output template;
* the one module this product offers;
* the success block, which this product has shown in the same order since v0.1.0
  with the same returned numbers; two labels in it were rewritten in the reader's
  words, and a user of the released tool still recognises the block;
* the release-verification entry, whose usage text names this executable.

Why the window moved rather than being copied
=============================================

The eventual product is one application with several independently selectable
randomizer modules. Two windows would have meant two layout contracts, two places
to fix a focus-ring bug, and a third one for the combined tool. The retrofit was
checked against the behaviour this module has always had: the focused window tests
(``tests/unit/test_warp_randomizer_gui.py``) run unmodified against it apart from
the stand-in boundary's method name, and the released golden hash is unchanged.

Appearance
==========

The window is a client of the one DragonByte Z theme and holds no colour of its
own; ``test_the_app_module_holds_no_colour_of_its_own`` still scans this file, and
the shared window is scanned too.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

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
from . import service as warprand

# Alias, so a caller that imported the worker from here before the retrofit still
# finds it. There is one worker implementation, not two.
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
WINDOW_TITLE = f"{warprand.TOOL_NAME} v{warprand.TOOL_VERSION}"

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
EXECUTABLE_STEM = "Buu-Fury-Warp-Randomizer"

#: This product's presentation. Everything user-facing that the shared window
#: needs, in one place, so a wording change is one edit and no widget.
WARPRAND_PRESENTATION = ProductPresentation(
    tool_name=warprand.TOOL_NAME,
    tool_version=warprand.TOOL_VERSION,
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
    default_seed=warprand.DEFAULT_SEED,
    output_template=warprand.OUTPUT_TEMPLATE,
    disclaimer=warprand.PROGRESSION_DISCLAIMER,
    # The status bar states what this product does to *which* game and version, in
    # the same shape the enemy executable's status bar uses: the provenance a user
    # can check without opening a file, then one plain sentence about the change.
    # The policy id stays in the manifest, where it identifies the algorithm that
    # produced a run, and is not shown to a player.
    status_note=(
        "Dragon Ball Z: Buu's Fury (US) - door destinations; doors move in "
        "reciprocal pairs"
    ),
    # One module, so the window draws no options area at all and the layout is the
    # one this product has always shipped.
    module_toggles=(
        ModuleToggle(
            module_id=warprand.MODULE_ID,
            label="Shuffle map warps",
            help=warprand.PROGRESSION_DISCLAIMER,
        ),
    ),
    offers_spoiler=False,
    running_status=RUNNING_STATUS,
    no_rom_text=NO_ROM_TEXT,
)


class MainWindow(RandomizerWindow):
    """The single window. Construct it with a boundary, ``show()``, done."""

    def __init__(self, service=None, *, parent=None) -> None:
        super().__init__(
            WARPRAND_PRESENTATION,
            service if service is not None else warprand.default_service(),
            parent=parent,
        )
        # The status-bar note under the name this product has always used for it.
        self.policy_label = self.status_note_label

    def success_lines(self, outcome) -> list[str]:
        """The success block this product has shown since v0.1.0.

        Same lines, same order and the same eleven facts as v0.1.0; the two labels
        that only made sense to the author are now the reader's words. "Supported"
        and "Randomized" carried no noun, so a player could not tell what was being
        counted, and the policy id named the algorithm rather than the change.

        Built entirely from what the boundary returned, never from a constant, so
        a policy change can never leave a stale number on screen.
        """
        return [
            "Success",
            "ROM verified \u2713",
            f"Seed: {outcome.seed}",
            f"Door transitions: {outcome.supported}",
            f"Doors randomized: {outcome.randomized}",
            f"Destinations moved: {outcome.destinations_moved}",
            f"Left unchanged: {outcome.skipped}",
            f"Output: {outcome.output_path}",
            f"SHA-256: {outcome.output_sha256}",
            f"Manifest: {outcome.manifest_path}",
            f"Source ROM unchanged: {'yes' if outcome.source_unchanged else 'NO'}",
        ]


def configure_application(app: QApplication) -> None:
    """Name the application and apply the one DragonByte Z theme to it."""
    _configure_application(app, WARPRAND_PRESENTATION)


# --- the release-verification entry ------------------------------------------

#: Printed by ``--help``. Short, because the whole product is short.
USAGE = f"""\
{warprand.TOOL_NAME} v{warprand.TOOL_VERSION}

  {EXECUTABLE_STEM}                       open the window

  {EXECUTABLE_STEM} {SMOKE_FLAG} --rom <rom> --output <rom>
      [--seed <seed>] [--report <file>]
        perform one run through the same window and write a JSON report.
        Used to verify a packaged release without a human at the keyboard.
"""


def parse_smoke_arguments(argv: list[str]) -> SmokeRequest | None:
    """The smoke request in ``argv``, or ``None`` for an ordinary launch."""
    return _parse_smoke_arguments(
        argv, usage=USAGE, error_type=warprand.WarpRandomizerAppError
    )


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
    beside it. ``service`` exists so this path can be tested against a stand-in
    boundary; :func:`main` never passes one.
    """
    window = MainWindow(service)
    messages = drive_smoke(
        app, window, request, timeout_ms=timeout_ms
    )

    outcome = window.outcome
    report = {
        "tool": warprand.TOOL_NAME,
        "version": warprand.TOOL_VERSION,
        "policy": warprand.POLICY_ID,
        "ok": outcome is not None,
        "seed": window.seed_text(),
        "seed_is_launch_seed": window.seed_text() == warprand.DEFAULT_SEED,
        "rom": str(request.rom),
        "output": outcome.output_path.as_posix() if outcome else str(request.output),
        "output_sha256": outcome.output_sha256 if outcome else None,
        "manifest": outcome.manifest_path.as_posix() if outcome else None,
        "supported": outcome.supported if outcome else None,
        "randomized": outcome.randomized if outcome else None,
        "destinations_moved": outcome.destinations_moved if outcome else None,
        "skipped": outcome.skipped if outcome else None,
        "source_sha256": outcome.source_sha256 if outcome else None,
        "source_unchanged": outcome.source_unchanged if outcome else None,
        "status": window.status_text(),
        "messages": messages,
        "progress_hidden": not window.progress_panel.isVisible(),
    }
    window.close()
    return (0 if outcome is not None else 1), report


def main(argv: list[str] | None = None) -> int:
    """``python -m tools.webfoot.warprand`` - show the window and run Qt."""
    arguments = list(sys.argv if argv is None else argv)
    if "--help" in arguments or "-h" in arguments:
        print(USAGE)
        return 0
    try:
        request = parse_smoke_arguments(arguments)
    except warprand.WarpRandomizerAppError as exc:
        print(f"error: {exc}")
        return 2

    app = QApplication(arguments)
    configure_application(app)
    if request is not None:
        code, report = run_smoke(app, request)
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
