from __future__ import annotations

import hashlib
import os

import pytest


def rom_bytes(path, digest=None, size=None):
    if not os.path.exists(path):
        pytest.skip("%s is absent, so this ROM-gated test cannot run" % path)
    data = open(path, "rb").read()
    if size is not None:
        assert len(data) == size
    if digest is not None:
        assert hashlib.sha256(data).hexdigest() == digest
    return data


def refused(call):
    try:
        call()
    except ValueError as error:
        print("refused: %s" % error)
        return True
    return False


def refusal_message(call):
    try:
        call()
    except ValueError as error:
        return str(error)
    return None


def perturbed_record(module, record_index, field, delta):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rom = rom_bytes(os.path.join(root, "baserom.gba"), size=0x800000)
    image = bytearray(rom)
    offset = module.BASE + module.STRIDE * record_index
    record = module.fields(rom, offset, module.STRIDE)
    record[field] += delta
    image[offset:offset + module.STRIDE] = module.serialize(record, module.STRIDE)
    return image


def require(path, reason):
    if not os.path.exists(path):
        pytest.skip(reason)
