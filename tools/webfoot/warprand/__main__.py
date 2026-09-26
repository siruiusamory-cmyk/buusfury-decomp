"""Entry point: ``python -m tools.webfoot.warprand``.

A checkout launch and the frozen build both end up in
:func:`tools.webfoot.warprand.gui.main`; this module exists so the package has
the ordinary ``-m`` entry as well as the ``.exe`` one.
"""

from __future__ import annotations

import sys

from .gui import main

if __name__ == "__main__":
    sys.exit(main())
