"""The version a frozen build reports, from the identity it was built with.

``identity.py`` is the one authority for the product name, the version string and
the four-field tuple, and this module repeats none of them: it is the single import
the frozen build and the packaging scripts need, so a version bump is one edit in
one place. ``tests/unit/test_buufury_text_release.py`` fails when that literal
appears anywhere in this package except ``identity.py``.
"""

from __future__ import annotations

from .identity import PRODUCT_NAME, PRODUCT_VERSION, VERSION_TUPLE

__all__ = ["PRODUCT_NAME", "PRODUCT_VERSION", "VERSION_TUPLE"]
