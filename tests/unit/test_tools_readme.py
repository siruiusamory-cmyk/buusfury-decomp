"""`tools/README.md` says which tool already reads a format; this asserts it stays true.

An index that names a file that has moved is worse than no index, because it is trusted. Every path in the
document is resolved here, and every module in `tools/webfoot/formats/` must be named, so adding a codec
without listing it fails the gate rather than leaving the next session to grep for it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

README = ROOT / "tools" / "README.md"
#: Backticked repository-relative Python paths, which is how every entry names its reader.
ENTRY = re.compile(r"`(tools/[A-Za-z0-9_/]+\.py)`")


def document() -> str:
    return README.read_text(encoding="utf-8")


def test_every_reader_named_in_the_index_exists() -> None:
    named = sorted(set(ENTRY.findall(document())))
    assert named, "the index names no reader at all"
    missing = [path for path in named if not (ROOT / path).is_file()]
    assert not missing, f"the index names tool(s) that do not exist: {missing}"


def test_every_format_module_is_named_in_the_index() -> None:
    modules = sorted(path.name for path in (ROOT / "tools" / "webfoot" / "formats").glob("*.py")
                     if path.name != "__init__.py")
    assert len(modules) >= 15, "the formats package did not resolve; this check would pass vacuously"
    text = document()
    unnamed = [name for name in modules if f"formats/{name}" not in text]
    assert not unnamed, (f"format module(s) a reader would never find from the index: {unnamed}; "
                         "add a row that names them")


def test_the_index_states_the_rule_it_exists_for() -> None:
    text = document()
    assert "before writing a decoder" in text
    assert "config/public_surface" not in text, "the index is public surface and needs no private pointer"
