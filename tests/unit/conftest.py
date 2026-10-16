"""Unit-test configuration shared by every module under ``tests/unit``.

The editor's theme is applied to the whole QApplication, so a module that installs it also
changes what every other product's window measures in the same process: measured, one ordinary
button's size hint goes from 20 to 26 under the stylesheet alone, and the enemy randomizer's
control-height test reads 26 where it expects 24 when the editor's theme runs first. A CI
worker can order modules either way, and that failed a pipeline run.

One module-scoped fixture does the hand-back, rather than a copy in each theme-installing file.
A module asks for it by depending on it, so it runs before that module's own fixtures and what
it captures is the application as nobody has themed it yet. It is not autouse: it creates the
application, and a module that wants none must not be handed one, which is how it broke the
launch-coverage module when it was.
"""
from __future__ import annotations

import pytest

from tests import conftest


@pytest.fixture(scope="module")
def untouched_application():
    """Create the application if Qt is present, and hand it back as this module found it."""
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        yield None
        return
    application = QApplication.instance() or QApplication([])
    state = conftest.capture_application(application)
    yield application
    conftest.hand_back_application(application, state)
