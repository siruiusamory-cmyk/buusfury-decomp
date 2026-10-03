"""PyInstaller entry shim for the standalone *Enemy Randomizer*.

PyInstaller freezes a script, not a ``-m package`` invocation, so this file just
calls the window's real ``main()``. It exists only for the frozen build; the
normal launch paths (``python -m tools.webfoot.enemyrand``) do not use it.
"""

from __future__ import annotations

import sys

from tools.webfoot.enemyrand.gui import main

if __name__ == "__main__":
    sys.exit(main())
