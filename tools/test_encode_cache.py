from __future__ import annotations

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import encode_cache


def cache(root, name):
    return os.path.join(root, name)


def test_a_create_publishes_a_short_entry_and_a_replace_heals_one():
    root = tempfile.mkdtemp(prefix="encode-cache-test-")
    fresh = cache(root, "a" * 64 + ".bin")
    held = cache(root, "b" * 64 + ".bin")
    encode_cache.write_new(fresh, b"payload")
    encode_cache.write_new(fresh, b"a later blob")
    with open(held, "wb") as handle:
        handle.write(b"short")
    encode_cache.write_bytes(held, b"whole")
    with open(fresh, "rb") as handle:
        published = handle.read()
    with open(held, "rb") as handle:
        repaired = handle.read()
    assert published == b"a later blob"
    assert repaired == b"whole"


def test_a_stamp_whose_bytes_change_is_replaced():
    root = tempfile.mkdtemp(prefix="encode-cache-test-")
    path = cache(root, encode_cache.EXE_STAMP)
    encode_cache.write_metadata(path, b"one")
    encode_cache.write_metadata(path, b"two")
    with open(path, "rb") as handle:
        assert handle.read() == b"two"


def test_a_batchs_stamp_keeps_a_later_pass_from_re_encoding_the_store():
    root = tempfile.mkdtemp(prefix="encode-cache-test-")
    store = cache(root, "store")
    executable = cache(root, "encoder.exe")
    os.makedirs(store)
    with open(executable, "wb") as handle:
        handle.write(b"the encoder")
    payload = b"a payload"
    entry = os.path.join(store, encode_cache.digest_bytes(payload) + ".bin")
    with open(entry, "wb") as handle:
        handle.write(b"encoded output, longer than the header")
    encode_cache.write_metadata(os.path.join(store, encode_cache.EXE_STAMP),
                                encode_cache.digest_file(executable).encode())

    spawned = []

    def compress(payload):
        spawned.append(payload)
        return b"re-encoded"

    snapshot = encode_cache.stamp_of(store)
    os.environ[encode_cache.STAMP_ENV] = snapshot
    try:
        first, first_stats, _ = encode_cache.cached_compress(compress, executable, store)
        second, second_stats, _ = encode_cache.cached_compress(compress, executable, store)
        later = first(payload)
        os.environ[encode_cache.STAMP_ENV] = ""
        third, third_stats, _ = encode_cache.cached_compress(compress, executable, store)
        perturbed = third(payload)
    finally:
        os.environ.pop(encode_cache.STAMP_ENV, None)
    assert snapshot and snapshot == encode_cache.stamp_of(store)
    assert (first_stats["trusted"], second_stats["trusted"], third_stats["trusted"]) == (1, 1, 0)
    assert later == b"encoded output, longer than the header"
    assert perturbed == b"re-encoded"
    assert spawned == [payload]
    assert encode_cache.trusted_store(executable, store)


def test_a_killed_pass_leaves_the_store_untrusted_and_the_next_pass_heals_the_entry():
    root = tempfile.mkdtemp(prefix="encode-cache-test-")
    store = cache(root, "store")
    executable = cache(root, "encoder.exe")
    with open(executable, "wb") as handle:
        handle.write(b"the encoder")
    payload = b"a payload whose entry was torn"
    key = encode_cache.digest_bytes(payload)
    entry = os.path.join(store, key + ".bin")
    os.makedirs(store)
    with open(entry, "wb") as handle:
        handle.write(b"short")
    encode_cache.write_metadata(os.path.join(store, encode_cache.EXE_STAMP),
                                encode_cache.digest_file(executable).encode())
    assert encode_cache.trusted_store(executable, store)

    calls = []

    def dies(payload):
        calls.append(payload)
        raise KeyboardInterrupt("killed mid-pass")

    blob, _, _ = encode_cache.cached_compress(dies, executable, store)
    try:
        blob(payload)
        raise AssertionError("the killed pass did not raise")
    except KeyboardInterrupt:
        pass
    assert calls == [payload]
    assert not encode_cache.trusted_store(executable, store)

    healed = []

    def works(payload):
        healed.append(payload)
        return b"whole output"

    blob, stats, close = encode_cache.cached_compress(works, executable, store)
    assert stats["trusted"] == 0
    assert blob(payload) == b"whole output"
    assert healed == [payload]
    close()
    with open(entry, "rb") as handle:
        assert handle.read() == b"whole output"


def test_an_untrusted_pass_counts_its_own_duplicate_payload_as_a_hit():
    root = tempfile.mkdtemp(prefix="encode-cache-test-")
    store = cache(root, "store")
    executable = cache(root, "encoder.exe")
    with open(executable, "wb") as handle:
        handle.write(b"the encoder")
    spawned = []

    def compress(payload):
        spawned.append(payload)
        return b"output"

    os.environ[encode_cache.STAMP_ENV] = ""
    try:
        blob, stats, _ = encode_cache.cached_compress(compress, executable, store)
        served = [blob(b"a"), blob(b"a"), blob(b"b"), blob(b"a")]
    finally:
        os.environ.pop(encode_cache.STAMP_ENV, None)
    assert served == [b"output"] * 4
    assert spawned == [b"a", b"b"]
    assert (stats["spawns"], stats["hits"], stats["total"]) == (2, 2, 4)


BATCH_WORKER = """
import os, sys
sys.path.insert(0, sys.argv[1])
import encode_cache
store, exe, snapshot, rounds = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
payloads = [bytes([65 + index]) * 64 for index in range(8)]


def compress(payload):
    return b"out" + payload


for round_number in range(rounds):
    os.environ[encode_cache.STAMP_ENV] = snapshot if round_number % 2 else ""
    blob, stats, close = encode_cache.cached_compress(compress, exe, store)
    for payload in payloads:
        got = blob(payload)
        if got != b"out" + payload:
            raise SystemExit("bad blob %r" % (got,))
    close()
"""


def test_six_batched_passes_share_one_store_through_a_sharing_violation():
    root = tempfile.mkdtemp(prefix="encode-cache-batch-")
    store = cache(root, "store")
    executable = cache(root, "encoder.exe")
    os.makedirs(store)
    with open(executable, "wb") as handle:
        handle.write(b"the encoder")
    snapshot = encode_cache.digest_file(executable)
    encode_cache.write_metadata(os.path.join(store, encode_cache.EXE_STAMP), snapshot.encode())
    rounds = 80
    children = [subprocess.Popen([sys.executable, "-c", BATCH_WORKER, HERE, store, executable,
                                  snapshot, str(rounds)], stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True) for _ in range(6)]
    failures = []
    for child in children:
        output = child.communicate()[0]
        if child.returncode != 0:
            failures.append("exit %d\n%s" % (child.returncode, output[-1400:]))
    assert not failures, failures[0]
    for payload in [bytes([65 + index]) * 64 for index in range(8)]:
        entry = os.path.join(store, encode_cache.digest_bytes(payload) + ".bin")
        with open(entry, "rb") as handle:
            assert handle.read() == b"out" + payload


if __name__ == "__main__":
    test_a_create_publishes_a_short_entry_and_a_replace_heals_one()
    test_a_stamp_whose_bytes_change_is_replaced()
    test_a_batchs_stamp_keeps_a_later_pass_from_re_encoding_the_store()
    test_an_untrusted_pass_counts_its_own_duplicate_payload_as_a_hit()
    test_a_killed_pass_leaves_the_store_untrusted_and_the_next_pass_heals_the_entry()
    test_six_batched_passes_share_one_store_through_a_sharing_violation()
    print("PASS test_encode_cache")
