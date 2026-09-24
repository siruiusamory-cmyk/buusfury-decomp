"""Read-only census for LOGX-MAP-RECORD-001.

This deliberately reports physical shapes and validated text-table lookups.  It
does not name either the two-byte key or the second-level targets semantically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from tools.webfoot.formats.text_tables import decode_string, read_pointer


ROM_SIZE = 0x800000
ROM_BASE = 0x08000000
TABLE_OFFSET = 0x08E2E0
RECORD_SIZE = 0x38
RECORD_COUNT = 0x1C4
TABLE_END = TABLE_OFFSET + RECORD_SIZE * RECORD_COUNT

#: The accepted UTF-16LE text pointer table, as this probe independently
#: measured it. Kept as the probe's own literal rather than imported from the
#: codec: a probe that read the extent from the code it checks could not detect
#: that code drifting.
TEXT_TABLE_FILE_OFFSET = 0x0006BCE8
TEXT_ENTRY_COUNT = 1534


def _u16le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u32le(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def _in_rom_word(value: int, size: int) -> bool:
    return value % 4 == 0 and ROM_BASE <= value <= ROM_BASE + size - 4


def analyze(data: bytes) -> dict[str, object]:
    """Return a deterministic census without modifying ``data``."""
    if len(data) != ROM_SIZE:
        raise ValueError(f"expected 0x{ROM_SIZE:X}-byte canonical ROM, got {len(data):#x}")
    if TABLE_END > len(data):
        raise ValueError("candidate table is outside ROM")

    records: list[dict[str, object]] = []
    for index in range(RECORD_COUNT):
        offset = TABLE_OFFSET + index * RECORD_SIZE
        key_be = int.from_bytes(data[offset : offset + 2], "big")
        key_le = _u16le(data, offset)
        text_word = _u32le(data, offset + 0x0C)
        text_index = text_word & 0xFFFF
        text_offset = read_pointer(data, text_index, TEXT_TABLE_FILE_OFFSET)
        text, _ = decode_string(data, text_offset)
        first_raw = _u32le(data, offset + 0x2C)
        second_raw = _u32le(data, first_raw - ROM_BASE) if _in_rom_word(first_raw, len(data)) else None
        records.append(
            {
                "index": index,
                "offset": offset,
                "bytes": data[offset : offset + RECORD_SIZE].hex(),
                "key_be": key_be,
                "key_le": key_le,
                "text_word_raw": text_word,
                "text_index_low16": text_index,
                "text": text,
                "pointer_2c_raw": first_raw,
                "second_word_raw": second_raw,
                "pointer_2c_valid": _in_rom_word(first_raw, len(data)),
                "second_word_valid": second_raw is not None and _in_rom_word(second_raw, len(data)),
            }
        )

    keys = [int(record["key_be"]) for record in records]
    names = [int(record["text_index_low16"]) for record in records]
    firsts = [int(record["pointer_2c_raw"]) for record in records]
    seconds = [int(record["second_word_raw"]) for record in records if record["second_word_raw"] is not None]
    representatives = [0, 1, 39, 100, 225, 338, 451]
    return {
        "table_offset": TABLE_OFFSET,
        "table_end": TABLE_END,
        "record_size": RECORD_SIZE,
        "record_count": RECORD_COUNT,
        "preceding_32_bytes": data[TABLE_OFFSET - 32 : TABLE_OFFSET].hex(),
        "following_32_bytes": data[TABLE_END : TABLE_END + 32].hex(),
        "key_be": {
            "unique": len(set(keys)),
            "zero": keys.count(0),
            "minimum": min(keys),
            "maximum": max(keys),
            "duplicates": {str(key): count for key, count in Counter(keys).items() if count > 1},
        },
        "key_le": {"unique": len(set(int(record["key_le"]) for record in records))},
        "text": {
            "all_words_upper16_zero": all(int(record["text_word_raw"]) <= 0xFFFF for record in records),
            "all_indices_in_range": all(0 <= index < TEXT_ENTRY_COUNT for index in names),
            "unique_indices": len(set(names)),
            "zero_indices": names.count(0),
            "empty_decodings": sum(not str(record["text"]) for record in records),
        },
        "pointer_chain": {
            "first_valid": sum(bool(record["pointer_2c_valid"]) for record in records),
            "first_unique": len(set(firsts)),
            "second_valid": sum(bool(record["second_word_valid"]) for record in records),
            "second_unique": len(set(seconds)),
        },
        "representatives": [records[index] for index in representatives],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="canonical Buu's Fury ROM (opened read-only)")
    args = parser.parse_args()
    data = args.rom.read_bytes()
    report = analyze(data)
    report["sha256"] = hashlib.sha256(data).hexdigest()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
