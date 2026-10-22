from __future__ import annotations

import hashlib


def read_rom(path, digest):
    data = open(path, "rb").read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != digest:
        raise SystemExit("ROM sha256 %s is not the canonical %s" % (actual, digest))
    if len(data) != 0x800000:
        raise SystemExit("ROM is %d bytes" % len(data))
    return data
