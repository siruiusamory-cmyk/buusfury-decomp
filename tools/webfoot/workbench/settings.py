"""WORKBENCH-003 - tiny per-user UI settings (currently just the mGBA path).

A remembered path is a machine fact, so it lives OUTSIDE the repo and OUTSIDE
any project - in Qt's per-user AppConfigLocation, as a small JSON file. This is
a UI convenience only: it never gates launch (a wrong/old saved mGBA must still
be launchable, same principle as the display-only version in launcher.py).

Every function fails safe: a missing/corrupt/unwritable settings file must never
raise into the UI or block a launch. Load returns None; save swallows errors.

The config dir is overridable via WEBFOOT_WORKBENCH_CONFIG_DIR (tests point it
at a tmp dir; also a headless-QStandardPaths escape hatch).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from PySide6.QtCore import QStandardPaths

_ENV_DIR = "WEBFOOT_WORKBENCH_CONFIG_DIR"
_FILE = "workbench-settings.json"
_MGBA_KEY = "mgba_path"


def _config_dir() -> Path | None:
    """The dir the settings file lives in. None if Qt yields nothing headless."""
    override = os.environ.get(_ENV_DIR)
    if override:
        return Path(override)
    loc = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
    return Path(loc) if loc else None


def _settings_file() -> Path | None:
    d = _config_dir()
    return d / _FILE if d is not None else None


def load_mgba_path() -> str | None:
    """Saved mGBA path, or None. Never raises (missing/corrupt -> None)."""
    try:
        path = _settings_file()
        if path is None or not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        value = data.get(_MGBA_KEY)
        return value if isinstance(value, str) and value else None
    except (OSError, ValueError):  # ValueError covers json.JSONDecodeError
        return None


def save_mgba_path(path: str) -> None:
    """Persist the mGBA path. Never raises (unwritable dir -> silent no-op)."""
    try:
        target = _settings_file()
        if target is None:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({_MGBA_KEY: path}), encoding="utf-8")
    except OSError:
        return
