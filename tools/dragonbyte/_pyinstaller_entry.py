"""PyInstaller entry shim for DragonByte Z, the product.

PyInstaller freezes a script, not a ``-m package`` invocation, so this file calls
the application's real ``main()``. It exists only for the frozen build; the normal
launch paths (`python -m tools.dragonbyte`, the `DragonByte Z.cmd` launcher) do
not use it.

It is deliberately the sibling of the beta workbench's own shim in shape and NOT
in target: that one freezes the beta, which is the engineering surface, and this
one freezes ``tools/dragonbyte``, which is the product a user installs.
"""

from __future__ import annotations

import sys

from tools.dragonbyte.app import main

if __name__ == "__main__":
    sys.exit(main())
