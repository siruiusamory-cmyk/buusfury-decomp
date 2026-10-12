"""QA probe: is a status sentence drawn more than once on one screen?

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001` fixed the same defect four separate times
(a status sentence rendered twice on one screen: Atlas, Graphics, the Map
workspace, the Scene editor), each instance found by a human or an independent
reviewer rather than by a test. This probe finds them in one pass.

It deliberately checks only the SHELL'S OWN status sentences. A repeated field
caption such as "Behavior" appears in two panels on purpose, because each panel is
labelled for itself; a repeated *status* sentence is never intentional, because the
status line belongs to the shell and there is exactly one of it.

For every reachable screen it reports any of these that renders more than once:
the active editor's status line, and each half of the project-state line.

Run:

    python -m tools.qa.status_duplication_probe
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PySide6.QtWidgets import QApplication, QLabel, QStatusBar  # noqa: E402

#: Every screen this probe walks, named here rather than discovered. The claim
#: being made is coverage of a whole class, so a screen that stops being reachable
#: has to be a failure rather than a silently shorter list.
SCREENS: tuple[str, ...] = (
    "Atlas",
    "Inspector",
    "Maps",
    "Graphics",
    "Maps/browse",
    "Maps/layout",
    "Maps/objects",
    "Maps/objects (scene action)",
    "Scene",
)


def drawn_texts(window) -> Counter:
    """Every sentence actually drawn in the window, with its render count."""
    counts: Counter = Counter()
    for label in window.findChildren(QLabel):
        if not label.isVisible() or label.parentWidget() is None:
            continue
        text = label.text().strip()
        if text:
            counts[text] += 1
    return counts


def status_sentences(window) -> list[str]:
    """The sentences the shell's own status bar is currently showing."""
    parts = [window._status_context.text().strip()]
    parts.extend(
        piece.strip()
        for piece in window._status_project.text().split("\u2502")
        if piece.strip()
    )
    return [part for part in parts if part]


def status_vacuity(name: str, sentences: list[str]) -> str | None:
    """Why a screen with no status sentence is not clean, or None when it is readable.

    An empty list means the bar is not being read, not that the screen is clean:
    with no sentence to look for, every duplicate is invisible.
    """
    if sentences:
        return None
    return (
        f"[{name}] the status bar rendered no sentence, so this screen was not "
        "measured and is not clean"
    )


def unreached_screens(reached: list[str]) -> list[str]:
    """The named screens the walk did not reach, in the order they were named."""
    return [name for name in SCREENS if name not in reached]


def screens(harness):
    """Each reachable screen, in order, with its name."""
    window = harness.window
    for editor in ("Atlas", "Inspector", "Maps", "Graphics"):
        window.show_editor(editor)
        yield editor
    for mode in ("browse", "layout", "objects"):
        window.show_editor("Maps")
        harness.maps.set_mode(mode)
        yield f"Maps/{mode}"
    # The Scene editor is reached from the object mode, not from the strip.
    window.show_editor("Maps")
    harness.maps.set_mode("objects")
    yield "Maps/objects (scene action)"
    window._scene_action.setEnabled(True)
    window._scene_action.trigger()
    harness.pump(6)
    yield "Scene"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    from tools.qa.visual_pass_capture import Harness

    app = QApplication.instance() or QApplication([])
    workspace = Path(tempfile.mkdtemp(prefix="dbz-status-audit-"))
    harness = Harness(Path(tempfile.mkdtemp(prefix="dbz-status-out-")), workspace)
    problems = 0
    unmeasured = 0
    reached: list[str] = []
    try:
        bars = len(harness.window.findChildren(QStatusBar))
        print(f"status bars in the window: {bars}")
        if bars != 1:
            problems += 1
        for name in screens(harness):
            reached.append(name)
            harness.pump(6)
            counts = drawn_texts(harness.window)
            # Re-read the sentences AFTER settling, so the bar's own two labels
            # count once each rather than being compared against stale text.
            sentences = status_sentences(harness.window)
            refusal = status_vacuity(name, sentences)
            if refusal is not None:
                unmeasured += 1
                print(refusal)
                continue
            offenders = {
                sentence: counts[sentence]
                for sentence in sentences
                if counts[sentence] > 1
            }
            if offenders:
                problems += len(offenders)
                print(f"[{name}] {len(offenders)} duplicated status sentence(s)")
                for text, n in offenders.items():
                    print(f"   x{n} {text[:88]!r}")
            else:
                print(f"[{name}] clean")
        for name in unreached_screens(reached):
            unmeasured += 1
            print(f"[{name}] never reached, so it was not measured")
        if unmeasured:
            print(f"UNMEASURED {unmeasured} screen(s): a clean line above is not evidence")
        print(
            f"\nTOTAL {problems} duplicated status sentence(s) "
            f"across {len(SCREENS)} screen(s)"
        )
    finally:
        harness.window.close()
        shutil.rmtree(workspace, ignore_errors=True)
    del app
    return 1 if problems or unmeasured else 0


if __name__ == "__main__":
    raise SystemExit(main())
