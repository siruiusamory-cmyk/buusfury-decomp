from __future__ import annotations

import concurrent.futures
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "mapcontainer"))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "webfoot"))

import encode_cache
import generate_mapcontainer as generator
import payload_store
import spritecontainer
from testkit import rom_bytes

ROM = os.path.join(generator.ROOT, "baserom.gba")
PAYLOADS = os.path.join(generator.ROOT, "assets", "spritecontainer")
NAME = "test_the_sprite_container_population_round_trips_byte_for_byte"


def test_the_walk_reaches_the_measured_population():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    block = generator.set_block("sprite")
    offsets = spritecontainer.container_offsets(rom)
    assert len(offsets) == block.expected_containers == 7390
    assert offsets[0] == block.start == 0x3C34D0
    members = generator.read_members(rom)
    assert [one.offset for one in members] == offsets
    assert sum(one.stored_size for one in members) == block.expected_marker_union == 2753456
    assert members[-1].offset + members[-1].stored_size == block.end == 0x6A88AC
    assert not block.carve_outs


def test_the_sprite_container_population_round_trips_byte_for_byte():
    rom = rom_bytes(ROM, generator.ROM_SHA256)
    block = generator.set_block("sprite")
    members = generator.read_members(rom)
    sample = members[::61]
    store = payload_store.read(payload_store.path(PAYLOADS))
    scratch = tempfile.mkdtemp(prefix="spritecontainer-test-")
    compress, cache, close = encode_cache.cached_compress(
        generator.compressor(generator.COMPRESS, scratch), generator.COMPRESS,
        encode_cache.default_cache_dir())
    equal = 0
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            blobs = list(pool.map(lambda one: compress(store[one.offset]), sample))
        close()
        equal = sum(blob == rom[one.offset:one.offset + one.stored_size]
                    for one, blob in zip(sample, blobs))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("%d/%d byte-equal over the %d-container sample (misses=%d)"
          % (equal, len(sample), len(members), cache["misses"]))
    assert equal == len(sample)


if __name__ == "__main__":
    test_the_walk_reaches_the_measured_population()
    test_the_sprite_container_population_round_trips_byte_for_byte()
    print("PASS %s" % NAME)
