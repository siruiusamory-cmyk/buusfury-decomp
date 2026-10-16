"""A decoded-container cache for the static censuses, kept under ``build/`` and never committed.

WHY. The game-wide index census decodes 7,390 containers, and that walk was run at least four times in one
ticket - the index census, the actor-bank census, the per-scene free-bank question and then the model
experiments - at minutes each, for identical results. The decode is a pure function of the image bytes and
the container's offset, which is exactly what a cache key can state.

WHAT IS KEYED, AND WHY NOT THE PACKED BYTES. The key is the image's sha256, the offset, and the two header
fields. Hashing the packed extent instead would be the more natural key, but the extent is only known after
decoding, which is the work being avoided. Keying on the image digest means a changed image can never serve
a stale payload, and keying on the offset plus the declared header means a container that moved or changed
kind is a miss rather than a wrong hit.

WHERE IT LIVES. ``<repo>/build/cache/containers`` by default. ``build/`` is ignored, so a cache never enters
a commit and never carries retail bytes into the repository - the same rule the generated images follow.

A CACHE IS NOT EVIDENCE. Every read re-checks the payload length against the declared size and the metadata
against the image digest, and a mismatch is treated as a miss: a corrupt entry costs a decode, never a wrong
answer. Callers that need the exact packed extent get it from the sidecar, which is written from the same
decode that produced the payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.webfoot.formats import webfoot_lz  # noqa: E402

#: Bumped when the entry layout changes; an entry written by another version is a miss.
ENTRY_FORMAT = 1


@dataclass(frozen=True)
class Stats:
    hits: int
    misses: int
    writes: int

    def report(self) -> str:
        return f"{self.hits} hit(s), {self.misses} miss(es), {self.writes} written"


class DecodeCache:
    """``webfoot_lz.unpack`` with a payload store, keyed on the image digest and the offset.

    The object holds the hits/misses/writes counters for the run, so a caller can print them and a reader
    can see whether a number came from a decode or from the cache.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else REPO / "build" / "cache" / "containers"
        self._hits = 0
        self._misses = 0
        self._writes = 0

    @property
    def stats(self) -> Stats:
        return Stats(hits=self._hits, misses=self._misses, writes=self._writes)

    def key(self, image: bytes, offset: int) -> str:
        """The entry key for one container: image digest, offset, kind and declared size.

        Raises whatever ``webfoot_lz.read_header`` raises for an offset outside the image, so a caller
        cannot cache a container that does not exist.
        """
        kind, declared = webfoot_lz.read_header(image, offset)
        digest = hashlib.sha256(image).hexdigest()[:16]
        return f"{digest}-{offset & 0xFFFFFFFF:08x}-{kind}-{declared}"

    def _entry(self, key: str) -> tuple[Path, Path]:
        return self.root / f"{key}.bin", self.root / f"{key}.json"

    def unpack(self, image: bytes, offset: int) -> webfoot_lz.Container:
        """The container at ``offset``, from the cache when a valid entry exists."""
        key = self.key(image, offset)
        payload_path, meta_path = self._entry(key)
        cached = self._read(payload_path, meta_path, image, offset)
        if cached is not None:
            self._hits += 1
            return cached
        self._misses += 1
        container = webfoot_lz.unpack(image, offset)
        self._write(payload_path, meta_path, image, container)
        return container

    def _read(self, payload_path: Path, meta_path: Path, image: bytes,
              offset: int) -> webfoot_lz.Container | None:
        """The cached container, or None when the entry is absent, stale or not self-consistent."""
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            payload = payload_path.read_bytes()
        except (OSError, ValueError):
            return None
        if meta.get("format") != ENTRY_FORMAT:
            return None
        digest = hashlib.sha256(image).hexdigest()
        if meta.get("image_sha256") != digest or meta.get("offset") != offset:
            return None
        if len(payload) != meta.get("declared_size"):
            return None
        return webfoot_lz.Container(
            offset=offset,
            kind=meta["kind"],
            declared_size=meta["declared_size"],
            packed_end=meta["packed_end"],
            data=payload,
        )

    def _write(self, payload_path: Path, meta_path: Path, image: bytes,
               container: webfoot_lz.Container) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        meta = {
            "format": ENTRY_FORMAT,
            "image_sha256": hashlib.sha256(image).hexdigest(),
            "offset": container.offset,
            "kind": container.kind,
            "declared_size": container.declared_size,
            "packed_end": container.packed_end,
        }
        # Payload first, then the metadata: a half-written entry is a payload with no metadata, which the
        # reader treats as a miss, rather than metadata pointing at a payload that is not there yet.
        payload_path.write_bytes(container.data)
        meta_path.write_text(json.dumps(meta, sort_keys=True), encoding="utf-8")
        self._writes += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--offsets", required=True,
                        help="comma-separated container offsets, decimal or 0x-prefixed")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()

    image = args.image.read_bytes()
    cache = DecodeCache(args.root)
    for text in args.offsets.split(","):
        offset = int(text, 0)
        container = cache.unpack(image, offset)
        kind, declared = webfoot_lz.read_header(image, offset)
        print(f"0x{offset:06X}: kind {kind}, declared {declared} bytes, packed extent "
              f"{container.packed_size} bytes, {len(container.data)} byte(s) decoded")
    print(f"cache root {cache.root}: {cache.stats.report()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
