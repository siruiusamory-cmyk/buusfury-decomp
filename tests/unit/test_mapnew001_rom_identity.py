"""MAP-NEW-AUTHORING-001's live-identity observer accepts an image by IDENTITY, never by size.

The observer asserted `rom_size == 8388608 or rom_size == 16777216`, so any image of either
size passed and the two numbers said nothing about which image was running. It now requires
that BOTH the size the running core reports and the SHA-256 the launcher declared name one
entry of a short allowlist, and refuses everything else.

The predicate is exercised here over the table parsed out of the observer itself, so the test
and the observer cannot drift apart: the parser reads the same `{ size = ..., sha256 = "..." }`
entries the Lua walks. The Python mirror of the predicate is pinned to the Lua's both-halves
conjunction below.

`emu:romSize()` reports the file size rather than a rounded cart size. Measured: 10,141,220 for
that image in `docs/research/FRIEND_V3_WT_SPLIT_CONTAINER_RUNTIME.md`, and the non-power-of-two
sizes `romsize=9764748` / `romsize=9732800` in `build/crash-repro/*/started.txt`.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OBSERVER = ROOT / "tools" / "runtime" / "mapnew001_live_identity.lua"
HELPER = ROOT / "tools" / "runtime" / "mgba_session.ps1"

#: The canonical Buu's Fury image and the Cell base image, with the sizes the core reports.
CANONICAL = (8388608, "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e")
CELL_BASE = (10190116, "81c5766fba8eb961d3703d8c0bae900c9a7bd8bbf5ba209a03d56e124736948c")

ENTRY = re.compile(r'\{ size = (\d+), sha256 = "([0-9a-f]{64})" \}')


def at(text: str, needle: str) -> int:
    """Where a pinned literal sits. An assertion, so a removed guard fails with its own message."""
    position = text.find(needle)
    assert position != -1, f"not present in the file under test: {needle!r}"
    return position


def observer_text() -> str:
    return OBSERVER.read_text(encoding="utf-8")


def allowlist() -> list[tuple[int, str]]:
    return [(int(size), sha) for size, sha in ENTRY.findall(observer_text())]


def allows(declared: object, size: int) -> bool:
    """The observer's predicate: both halves must match one entry, digest case-insensitively."""
    if not isinstance(declared, str):
        return False
    lowered = declared.lower()
    return any(entry_size == size and entry_sha == lowered
               for entry_size, entry_sha in allowlist())


def test_the_allowlist_holds_exactly_the_canonical_and_the_cell_base_image() -> None:
    assert sorted(allowlist()) == sorted([CANONICAL, CELL_BASE])
    text = observer_text()
    assert "16777216" not in text, (
        "the old size-only acceptance is back: an expanded image would pass on its size alone")
    assert "CANONICAL_ROM_SIZE" not in text and "EXPANDED_ROM_SIZE" not in text


def test_the_predicate_accepts_the_listed_pairs_and_refuses_everything_else() -> None:
    for size, sha in (CANONICAL, CELL_BASE):
        assert allows(sha, size)
        assert allows(sha.upper(), size), (
            "the launcher's own digest is uppercase; the observer lowercases it")
    # Each half alone is not an identity.
    assert not allows(CANONICAL[1], CELL_BASE[0])
    assert not allows(CELL_BASE[1], CANONICAL[0])
    # An image on neither entry is refused, which is the whole point of an allowlist.
    assert not allows("00" * 32, CANONICAL[0])
    assert not allows("00" * 32, CELL_BASE[0])
    # A launcher that declares nothing, or a truncated digest, is refused rather than defaulted.
    assert not allows(None, CANONICAL[0])
    assert not allows(CANONICAL[1][:-1], CANONICAL[0])
    assert not allows(CANONICAL[1], 0)


def test_the_observer_refuses_before_it_reads_emulated_memory() -> None:
    text = observer_text()
    predicate = at(text, "local function rom_identity_allowed")
    gate = at(text, "assert(rom_identity_allowed(declared_sha256, rom_size),")
    first_read = at(text, "local function safe8")
    assert gate < first_read, (
        "the identity gate must precede the observer's emulated memory readers, so an unlisted "
        "image is refused rather than sampled")
    assert "refused" in text[gate:gate + 300]
    body = text[predicate:gate]
    assert "entry.size == size and entry.sha256 == declared" in body, (
        "both halves must match the same entry; matching them separately is not an identity")
    assert body.rindex("return false") > body.index("return true"), (
        "the predicate must fall through to refusal")


def test_the_comment_says_this_is_an_addition_and_not_a_loosening() -> None:
    text = observer_text()
    assert "ADDITION" in text and "not a loosening" in text
    assert "os.getenv(ROM_SHA256_ENV)" in text, "the declared digest must come from the environment"


def test_the_declared_digest_comes_from_the_launchers_own_gate() -> None:
    helper = HELPER.read_text(encoding="utf-8")
    assert "$env:LOG1_MGBA_ROM_SHA256 = $expectedHash" in helper
    gate = at(helper, "ROM identity mismatch; run refused")
    export = at(helper, "$env:LOG1_MGBA_ROM_SHA256 = $expectedHash")
    launch = at(helper, "$process = Start-Process")
    assert gate < export < launch, (
        "the digest must be exported after the equality gate proved it and before the child starts")
    assert "LOG1_MGBA_ROM_SHA256" in observer_text()
