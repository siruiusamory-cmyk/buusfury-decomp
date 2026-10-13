"""Kind by content sniff, never by extension.

Extension is a hint and is recorded as one; the kind comes from the first bytes.

* ``screenshot-png``: the PNG signature without the ``gbAs`` chunk. A file whose
  extension says state and whose content says screenshot gets ``misnamed`` and is
  never offered as a state to load.
* ``battery``: a save image whose size matches a known geometry. 8,192 bytes is
  the Buu's Fury EEPROM family; 32,768 is the SRAM-family size already seen in
  the corpus. The size alone is the evidence, and it is recorded as such. A state
  extension is checked first, so an 8,192-byte file named `.ss1` is not called a
  battery, and the size test never runs before the extension test.
* ``savestate``: an mGBA PNG container carrying the private ``gbAs`` chunk. The
  chunk is what makes it a state; the container's own header is still a
  HYPOTHESIS, so no game or ROM is attributed from a state.
* ``unknown-state``: a state extension whose bytes carry neither chunk nor a
  verified header. It is never a savestate, and the evidence says why.
* ``unknown``: anything else, with the first 16 bytes stored as a signature
  (a signature, never the bytes).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
#: The private chunk mGBA writes into a savestate's PNG container. Its presence
#: is what makes a PNG a state rather than a screenshot.
GBAS_CHUNK = b"gbAs"
BATTERY_SIZES = {512: "eeprom-512", 8192: "eeprom-8k", 32768: "sram-32k"}
#: Extensions that say "state" without being one.
STATE_SUFFIX_PREFIX = ".ss"
SIGNATURE_LEN = 16

screenshot = "screenshot-png"
battery = "battery"
savestate = "savestate"
unknown_state = "unknown-state"
unknown = "unknown"

KINDS = (battery, screenshot, savestate, unknown_state, unknown)


@dataclass(frozen=True)
class Kind:
    kind: str
    evidence: str
    misnamed: bool


def sniff(head: bytes, size: int, suffix: str, chunk_names: frozenset[bytes] = frozenset()) -> Kind:
    """The kind of one file from its first bytes, its size and its extension.

    ``chunk_names`` is the caller's PNG chunk walk, when it did one: an mGBA
    savestate is a PNG container carrying a private ``gbAs`` chunk, so the
    presence of that chunk is what separates a state from a screenshot. Without
    the walk, or without the chunk, a PNG stays a screenshot.
    """
    extension = suffix.lower()
    if head.startswith(PNG_SIGNATURE):
        width, height = _png_ihdr(head)
        detail = f"PNG signature, IHDR {width}x{height}" if width else "PNG signature"
        if GBAS_CHUNK in chunk_names:
            return Kind(savestate,
                        f"{detail}; carries the mGBA {GBAS_CHUNK.decode()} chunk",
                        False)
        return Kind(screenshot, f"{detail}; extension {extension or 'none'}",
                    extension.startswith(STATE_SUFFIX_PREFIX))
    if extension.startswith(STATE_SUFFIX_PREFIX):
        return Kind(unknown_state,
                    f"extension {extension}; no mGBA {GBAS_CHUNK.decode()} chunk and no verified"
                    " savestate header, so no state and no game are claimed",
                    False)
    if size in BATTERY_SIZES:
        return Kind(battery, f"{size} bytes, the {BATTERY_SIZES[size]} geometry", False)
    return Kind(unknown, f"first {SIGNATURE_LEN} bytes: {head[:SIGNATURE_LEN].hex()}", False)


def png_chunk_names(path: Path, limit: int = 64) -> frozenset[bytes]:
    """The chunk types in a PNG, read read-only and bounded.

    A PNG is a length-prefixed chunk stream; the walk stops at a truncated or
    implausible chunk rather than guessing, so a malformed file yields the
    chunks it actually had.
    """
    names: set[bytes] = set()
    try:
        with path.open("rb") as handle:
            if handle.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
                return frozenset()
            for _ in range(limit):
                header = handle.read(8)
                if len(header) < 8:
                    break
                length = int.from_bytes(header[:4], "big")
                names.add(header[4:8])
                if header[4:8] == b"IEND" or length > (1 << 24):
                    break
                # The chunk's data, then its four CRC bytes.
                handle.seek(length + 4, 1)
    except OSError:
        return frozenset()
    return frozenset(names)


def _png_ihdr(head: bytes) -> tuple[int, int]:
    """Width and height from an IHDR that is actually present, else zeroes."""
    if len(head) < 24 or head[12:16] != b"IHDR":
        return 0, 0
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
