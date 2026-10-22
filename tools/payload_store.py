from __future__ import annotations

import os
import struct

NAME = "payloads.store"
MAGIC = b"DBZPST01"
HEADER = struct.Struct("<8sII")
ENTRY = struct.Struct("<III")


def path(directory):
    return os.path.join(directory, NAME)


def stamp(path):
    info = os.stat(path)
    return [info.st_size, info.st_mtime_ns]


def write(path, items):
    items = sorted(items)
    entries = bytearray(HEADER.size + ENTRY.size * len(items))
    blob = bytearray()
    for index, (key, payload) in enumerate(items):
        ENTRY.pack_into(entries, HEADER.size + ENTRY.size * index, key, len(blob), len(payload))
        blob += payload
    HEADER.pack_into(entries, 0, MAGIC, len(items), len(blob))
    tmp = path + ".tmp"
    with open(tmp, "wb") as handle:
        handle.write(entries)
        handle.write(blob)
    os.replace(tmp, path)
    return stamp(path)


def read(path):
    with open(path, "rb") as handle:
        data = handle.read()
    magic, count, blob_size = HEADER.unpack_from(data, 0)
    if magic != MAGIC:
        raise ValueError("%s is not a payload store" % path)
    base = HEADER.size + ENTRY.size * count
    if base + blob_size != len(data):
        raise ValueError("%s is %d bytes, not the %d its header declares"
                         % (path, len(data), base + blob_size))
    out = {}
    for index in range(count):
        key, offset, length = ENTRY.unpack_from(data, HEADER.size + ENTRY.size * index)
        out[key] = data[base + offset:base + offset + length]
    return out
