"""The decode cache: same payload, fewer decodes, and a stale or corrupt entry is always a miss.

The test that matters is `test_a_changed_image_is_a_miss`: a cache whose key did not include the image would
serve a payload from a different build, and every census built on it would be quietly wrong.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.research import decode_cache as cache_module  # noqa: E402
from tools.webfoot.formats import webfoot_lz  # noqa: E402

OFFSET = 0x40


def image_with_container(payload: bytes = b"tiles and tiles and tiles") -> tuple[bytes, int]:
    """A small image holding one packed container at OFFSET."""
    packed = webfoot_lz.pack(payload, kind=1)
    image = bytes(OFFSET) + packed + bytes(0x20)
    return image, len(packed)


def test_a_second_decode_is_a_hit_and_the_payload_is_identical(tmp_path: Path) -> None:
    image, _ = image_with_container()
    cache = cache_module.DecodeCache(tmp_path)
    first = cache.unpack(image, OFFSET)
    direct = webfoot_lz.unpack(image, OFFSET)
    assert (first.kind, first.declared_size, first.packed_end, first.data) == \
           (direct.kind, direct.declared_size, direct.packed_end, direct.data)
    assert cache.stats.misses == 1 and cache.stats.writes == 1

    second = cache.unpack(image, OFFSET)
    assert second.data == first.data and second.packed_end == first.packed_end
    assert cache.stats.hits == 1, "the second decode comes from the cache"
    assert all(path.parent == tmp_path for path in tmp_path.iterdir())


def test_a_changed_image_is_a_miss(tmp_path: Path) -> None:
    image, _ = image_with_container()
    cache = cache_module.DecodeCache(tmp_path)
    cache.unpack(image, OFFSET)
    other = bytearray(image)
    other[-1] ^= 0x01  # outside the container, so it still decodes but the image digest differs
    assert cache.key(bytes(other), OFFSET) != cache.key(image, OFFSET)
    cache.unpack(bytes(other), OFFSET)
    assert cache.stats.hits == 0 and cache.stats.misses == 2


def test_a_truncated_payload_is_a_miss_and_is_rebuilt(tmp_path: Path) -> None:
    image, _ = image_with_container()
    cache = cache_module.DecodeCache(tmp_path)
    cache.unpack(image, OFFSET)
    key = cache.key(image, OFFSET)
    (tmp_path / f"{key}.bin").write_bytes(b"short")
    again = cache.unpack(image, OFFSET)
    assert again.data == webfoot_lz.unpack(image, OFFSET).data
    assert cache.stats.hits == 0 and cache.stats.misses == 2


def test_metadata_naming_another_image_is_a_miss(tmp_path: Path) -> None:
    image, _ = image_with_container()
    cache = cache_module.DecodeCache(tmp_path)
    cache.unpack(image, OFFSET)
    key = cache.key(image, OFFSET)
    meta_path = tmp_path / f"{key}.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["image_sha256"] = "0" * 64
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    cache.unpack(image, OFFSET)
    assert cache.stats.hits == 0 and cache.stats.misses == 2


def test_an_offset_outside_the_image_is_refused_before_anything_is_written(tmp_path: Path) -> None:
    image, _ = image_with_container()
    cache = cache_module.DecodeCache(tmp_path)
    with pytest.raises(webfoot_lz.ContainerError):
        cache.unpack(image, len(image) - 2)
    assert cache.stats.misses == 0 and not list(tmp_path.iterdir())
