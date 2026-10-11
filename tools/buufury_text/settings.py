"""Per-user window state: the theme mode and the splitter sizes.

Plain JSON under Qt's per-user AppConfigLocation, so the file can be read and
repaired by hand. Nothing here imports a widget: a test drives load and save
with no window open, and a settings file that cannot be written is a window
that still works.

The config directory comes from ``QStandardPaths``, which is why a caller sets
the application name before the first load.
"""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

#: Where the file lives when Qt is not configured (a bare interpreter, a test).
FALLBACK_DIRECTORY = Path.home() / ".buufury-text"

FILE_NAME = "settings.json"

#: Every key the window reads, with the value it gets when the file is silent.
#: The splitter sizes are left, centre and right: the centre takes the slack.
#: `view`, `order` and `group` are the dialogue list's shape; the words are the
#: session's own (`session.LINES`, `session.APPEARANCE`, `session.UNGROUPED`) and
#: are repeated here rather than imported so this module stays data only.
DEFAULTS: dict[str, object] = {
    "theme": "system",
    "splitter": [330, 540, 350],
    "view": "lines",
    "order": "appearance",
    "group": "none",
}


def directory() -> Path:
    """The directory the settings file lives in."""
    located = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
    return Path(located) if located else FALLBACK_DIRECTORY


def path() -> Path:
    """The settings file itself."""
    return directory() / FILE_NAME


def load() -> dict[str, object]:
    """The stored settings, with a default for every key the file does not hold.

    A corrupt, unreadable or wrongly shaped file answers the defaults rather
    than raising: this file remembers a window size, it does not gate a task.
    """
    values = dict(DEFAULTS)
    try:
        stored = json.loads(path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return values
    if not isinstance(stored, dict):
        return values
    for key, default in DEFAULTS.items():
        value = stored.get(key)
        if isinstance(value, list) and all(isinstance(item, int) for item in value):
            value = list(value)
        if isinstance(value, type(default)):
            values[key] = value
    return values


def save(values: dict[str, object]) -> None:
    """Write ``values`` over the stored ones, keeping every key not named here."""
    merged = {**load(), **values}
    target = path()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(merged, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        return
