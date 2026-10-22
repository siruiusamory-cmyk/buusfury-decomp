from __future__ import annotations

import hashlib
import os
import threading
import time

EXE_STAMP = "encoder.sha256"
HEADER_SIZE = 8
CACHE_ENV = "BUUSFURY_ENCODE_CACHE"
STAMP_ENV = "BUUSFURY_ENCODE_STAMP"
REPLACE_WAIT = 2.0
REPLACE_DELAY = 0.005
REPLACE_LIMIT = 0.2


def default_cache_dir():
    override = os.environ.get(CACHE_ENV)
    if override:
        return override
    local = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(local, "buusfury-decomp", "encode-cache")


def stamp_of(cache_dir):
    path = os.path.join(cache_dir, EXE_STAMP)
    return open(path).read().strip() if os.path.exists(path) else ""


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _discard(path):
    try:
        os.remove(path)
    except OSError:
        pass


def _replace(tmp, path, data):
    deadline = time.monotonic() + REPLACE_WAIT
    delay = REPLACE_DELAY
    while True:
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if time.monotonic() >= deadline:
                same = False
                try:
                    with open(path, "rb") as handle:
                        same = handle.read() == data
                except OSError:
                    same = False
                _discard(tmp)
                if not same:
                    raise
                return
            time.sleep(delay)
            delay = min(delay * 2, REPLACE_LIMIT)


def write_bytes(path, data):
    tmp = "%s.%d.%d.tmp" % (path, os.getpid(), threading.get_ident())
    with open(tmp, "wb") as handle:
        handle.write(data)
    _replace(tmp, path, data)


def write_new(path, data):
    write_bytes(path, data)


def write_metadata(path, data):
    write_bytes(path, data)


def publish_stamp(cache_dir, exe):
    os.makedirs(cache_dir, exist_ok=True)
    write_metadata(os.path.join(cache_dir, EXE_STAMP), digest_file(exe).encode())


def read_entry(path):
    deadline = time.monotonic() + REPLACE_WAIT
    delay = REPLACE_DELAY
    while True:
        try:
            with open(path, "rb") as handle:
                return handle.read()
        except FileNotFoundError:
            return None
        except PermissionError:
            if time.monotonic() >= deadline:
                return None
            time.sleep(delay)
            delay = min(delay * 2, REPLACE_LIMIT)


def trusted_store(exe, cache_dir):
    stamp = os.environ.get(STAMP_ENV)
    if stamp is None:
        stamp = stamp_of(cache_dir)
    return stamp == digest_file(exe)


def cached_compress(compress, exe, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    stamp_path = os.path.join(cache_dir, EXE_STAMP)
    exe_digest = digest_file(exe)
    grouped = os.environ.get(STAMP_ENV) is not None
    trusted = trusted_store(exe, cache_dir)
    if not grouped:
        try:
            os.remove(stamp_path)
        except OSError:
            pass
    stats = {"hits": 0, "misses": 0, "spawns": 0, "total": 0, "trusted": int(trusted)}
    locks: dict[str, threading.Lock] = {}
    published: dict[str, bytes] = {}

    def cached(payload):
        key = digest_bytes(payload)
        entry = os.path.join(cache_dir, key + ".bin")
        stats["total"] += 1
        with locks.setdefault(key, threading.Lock()):
            if trusted:
                blob = read_entry(entry)
                if blob is not None and len(blob) > HEADER_SIZE:
                    stats["hits"] += 1
                    return blob
            if key in published:
                stats["hits"] += 1
                return published[key]
            blob = compress(payload)
            stats["spawns"] += 1
            stats["misses"] += 1
            write_new(entry, blob)
            published[key] = blob
            return blob

    def close():
        if not grouped:
            write_metadata(stamp_path, exe_digest.encode())

    return cached, stats, close
