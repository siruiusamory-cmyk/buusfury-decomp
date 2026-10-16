"""PyInstaller entry shim for Buu's Fury Text Editor, the product.

PyInstaller freezes a script, not a ``-m package`` invocation, so this file calls
the application's real ``main()``. It exists only for the frozen build; the normal
launch paths (``python -m tools.buufury_text``, the ``Buu's Fury Text Editor.cmd``
launcher) do not use it.

It is deliberately the sibling of the desktop application's own shim in shape and
NOT in target: that one freezes ``tools/dragonbyte``, and this one freezes
``tools/buufury_text``. Freezing the wrong package is a real defect this repository
has already paid for, so ``tests/unit/test_buufury_text_release.py`` reads the
frozen script list out of the spec template.
"""

from __future__ import annotations

import sys

from tools.buufury_text.app import main

if __name__ == "__main__":
    sys.exit(main())
