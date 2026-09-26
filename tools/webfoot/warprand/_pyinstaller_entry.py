"""PyInstaller entry shim for the Buu's Fury Warp Randomizer.

PyInstaller freezes a script, not a ``-m package`` invocation, so this file just
calls the window's real ``main()``. It exists only for the frozen build; the
normal launch paths (``python -m tools.webfoot.warprand``) do not use it.
"""

from __future__ import annotations

import sys

from tools.webfoot.warprand.gui import main

if __name__ == "__main__":
    sys.exit(main())
