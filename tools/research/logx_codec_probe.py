"""LOGX-CODEC-001: Buu's Fury Webfoot container / codec probe.

Read-only, deterministic research tool. It answers, from the canonical image
rather than from an external tool's behaviour:

* which physical wrapper forms the engine consumes, and what each wrapper word
  means. The wrapper is the engine's own Thumb dispatcher at ``0x0803D940``; see
  :mod:`tools.research.webfoot_codec_reference`;
* whether the project's decoder agrees with an independent reimplementation of
  the same grammar, byte for byte, over every container reachable from the
  accepted resource graphs;
* where the packed stream's own terminator falls, how many source bytes it
  consumed, and whether the destination is bounded;
* a seeded census of container forms reachable from the accepted resource graphs
  (dominant layer chunks, ``root +0x48`` selector streams, ``root +0x4C``
  graphics banks), not a blind aligned-word sweep of the whole image;
* every reachable container whose first wrapper word is zero.

The ROM is gated on the canonical SHA-256 and opened read-only. No decoded
payload is written anywhere; fixtures are reported as SHA-256 digests and short
diagnostic byte samples only.

Usage::

    python -m tools.research.logx_codec_probe <rom> --report
    python -m tools.research.logx_codec_probe <rom> --fixtures
    python -m tools.research.logx_codec_probe <rom> --census
    python -m tools.research.logx_codec_probe <rom> --zero-header
    python -m tools.research.logx_codec_probe <rom> --opening
    python -m tools.research.logx_codec_probe <rom> --malformed
    python -m tools.research.logx_codec_probe <rom> --entry-points
    python -m tools.research.logx_codec_probe <rom> --json out.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.research import webfoot_codec_reference as reference  # noqa: E402
from tools.webfoot.formats import webfoot_lz as wl  # noqa: E402

ROM_BASE = 0x08000000
CANONICAL_SHA256 = "940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E"

MAP_ENTRY_TABLE = 0x0808E2E0
MAP_ENTRY_STRIDE = 0x38
MAP_ENTRY_COUNT = 452

#: Longest leading run of aligned in-ROM words the root route will walk.
SOURCE_ARRAY_WORD_LIMIT = 64

#: The selector-bank table the accepted LOGX-TILE-001 route reaches through
#: scene-descriptor ``+0x4C``; every canonical root holds this same address.
BANK_TABLE = 0x08179764

#: The dominant-layer constructor's default container (LOGX-TILE-001 4.4): kind
#: 0, declared size 0, followed by zero bytes. The engine's own zero-header
#: instance, and the reason a zero first word cannot mean "the stream is empty".
ENGINE_DEFAULT_CONTAINER = 0x08070808


class ProbeError(RuntimeError):
    """Canonical-ROM gate or a malformed probe input."""


def load_rom(path: str | Path) -> bytes:
    """Read the image and refuse anything but the canonical revision."""
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest().upper()
    if digest != CANONICAL_SHA256:
        raise ProbeError(
            f"ROM SHA-256 {digest} is not the canonical Buu's Fury image "
            f"{CANONICAL_SHA256}"
        )
    return data


def _u32(data: bytes, address: int) -> int:
    return struct.unpack_from("<I", data, address - ROM_BASE)[0]


def _u16(data: bytes, address: int) -> int:
    return struct.unpack_from("<H", data, address - ROM_BASE)[0]


def in_rom(data: bytes, address: int) -> bool:
    return ROM_BASE <= address < ROM_BASE + len(data) and address % 2 == 0


# --- wrapper classification --------------------------------------------------

#: Neutral wrapper-class labels. ``kind`` is the engine's own dispatch word; the
#: label states only what the engine does with it, never what it "means".
WRAPPER_STORED = "kind0_stored_dispatch"
WRAPPER_PACKED1 = "kind1_packed_dispatch"
WRAPPER_PACKED2 = "kind2_packed_dispatch"
WRAPPER_UNKNOWN = "kind_outside_0_1_2"


def classify_wrapper(data: bytes, address: int) -> str:
    if not in_rom(data, address):
        return "outside_rom"
    kind, _declared = wl.read_header(data, address - ROM_BASE)
    if kind == 0:
        return WRAPPER_STORED
    if kind == 1:
        return WRAPPER_PACKED1
    if kind == 2:
        return WRAPPER_PACKED2
    return WRAPPER_UNKNOWN


@dataclass
class FixtureResult:
    """One container measured by both decoders."""

    label: str
    resource_class: str
    address: int
    provenance: str
    wrapper_words: list[int]
    wrapper_class: str
    declared_size: int
    project_length: int
    project_sha256: str
    engine_length: int
    engine_sha256: str
    engine_terminator: str
    engine_source_consumed: int
    project_source_consumed: int
    payload_head_hex: str
    agrees: bool
    project_error: str = ""
    engine_error: str = ""

    @property
    def ok(self) -> bool:
        return not self.project_error and not self.engine_error


def measure_fixture(
    data: bytes,
    address: int,
    *,
    label: str,
    resource_class: str,
    provenance: str,
) -> FixtureResult:
    """Decode one container with both implementations and compare."""
    offset = address - ROM_BASE
    kind, declared = wl.read_header(data, offset)
    words = [_u32(data, address), _u32(data, address + 4)]
    result = FixtureResult(
        label=label,
        resource_class=resource_class,
        address=address,
        provenance=provenance,
        wrapper_words=words,
        wrapper_class=classify_wrapper(data, address),
        declared_size=declared,
        project_length=-1,
        project_sha256="",
        engine_length=-1,
        engine_sha256="",
        engine_terminator="",
        engine_source_consumed=-1,
        project_source_consumed=-1,
        payload_head_hex="",
        agrees=False,
    )
    try:
        container = wl.unpack(data, offset)
        result.project_length = len(container.data)
        result.project_sha256 = hashlib.sha256(container.data).hexdigest()
        result.project_source_consumed = container.packed_end - address
    except wl.ContainerError as exc:
        result.project_error = str(exc)
    except ProbeError as exc:  # pragma: no cover - defensive
        result.project_error = str(exc)

    if kind in wl.PACKED_KINDS:
        try:
            decoded = reference.decode_packed(
                data, offset + wl.HEADER_SIZE, declared_size=declared
            )
            result.engine_length = decoded.actual_size
            result.engine_sha256 = hashlib.sha256(decoded.data).hexdigest()
            result.engine_terminator = decoded.terminator
            result.engine_source_consumed = decoded.source_consumed
            if decoded.data:
                result.payload_head_hex = decoded.data[:16].hex()
        except reference.CodecError as exc:
            result.engine_error = str(exc)
    else:
        # kind 0 is a memcpy of the declared size; the engine does not walk a
        # stream at all, so the "terminator" is the declared length.
        payload = address + wl.HEADER_SIZE
        available = (ROM_BASE + len(data)) - payload
        copy_len = min(declared, max(available, 0))
        engine_data = data[payload - ROM_BASE : payload - ROM_BASE + copy_len]
        result.engine_length = copy_len
        result.engine_sha256 = hashlib.sha256(engine_data).hexdigest()
        result.engine_terminator = "declared_length_memcpy"
        result.engine_source_consumed = copy_len
        if engine_data:
            result.payload_head_hex = engine_data[:16].hex()

    result.agrees = (
        result.ok
        and result.project_length == result.engine_length
        and result.project_sha256 == result.engine_sha256
    )
    return result


# --- accepted resource graphs ------------------------------------------------


def _source_array_run(data: bytes, source: int) -> list[int]:
    """Leading run of aligned in-ROM words at ``source``.

    Identical rule to the accepted LOGX-MAP-RENDER-001 / LOGX-LAYER-001 route:
    the scan stops at the first null or non-pointer word.
    """
    words: list[int] = []
    if not in_rom(data, source):
        return words
    offset = source - ROM_BASE
    limit = min(offset + 4 * SOURCE_ARRAY_WORD_LIMIT, len(data) - 4)
    while offset <= limit:
        word = struct.unpack_from("<I", data, offset)[0]
        if word == 0 or not in_rom(data, word):
            break
        words.append(word)
        offset += 4
    return words


def iter_selector_roots(data: bytes) -> list[int]:
    """Every selector-1 root address, in ascending order.

    The route is LOGX-MAP-RENDER-001's: ``MapEntry[+0x2C]`` leads to a leading
    run of aligned in-ROM words whose first member is the root. The table is
    walked, not re-derived.
    """
    seen: list[int] = []
    for index in range(MAP_ENTRY_COUNT):
        entry = MAP_ENTRY_TABLE + index * MAP_ENTRY_STRIDE
        source = _u32(data, entry + 0x2C)
        run = _source_array_run(data, source)
        if run:
            seen.append(run[0])
    return sorted(set(seen))


def iter_dominant_chunk_targets(data: bytes):
    """Every layer ``+0x18`` element of a dominant-handler record.

    Mirrors LOGX-TILE-001's route: a selector-1 root's ``+0x14``..``+0x20``
    layer slots, the record's ``+0x00`` handler word, and a ``+0x14`` x ``+0x15``
    element window at ``record + 0x18 + 4*i``.
    """
    targets: dict[int, set[str]] = {}
    for root in iter_selector_roots(data):
        for slot in range(4):
            record = _u32(data, root + 0x14 + 4 * slot)
            if not in_rom(data, record):
                continue
            if _u32(data, record) != 0x08008087:
                continue
            count = data[record + 0x14 - ROM_BASE] * data[record + 0x15 - ROM_BASE]
            for index in range(count):
                target = _u32(data, record + 0x18 + 4 * index)
                if in_rom(data, target):
                    targets.setdefault(target, set()).add(
                        f"layer_record:{record:08X}"
                    )
    return targets


def iter_selector_streams(data: bytes):
    """``root + 0x48`` container addresses, with the roots that hold them."""
    found: dict[int, set[str]] = {}
    for root in iter_selector_roots(data):
        container = _u32(data, root + 0x48)
        if in_rom(data, container):
            found.setdefault(container, set()).add(f"root:{root:08X}")
    return found


def iter_bank_containers(data: bytes):
    """The ``root + 0x4C`` selector-bank container table."""
    found: dict[int, set[str]] = {}
    address = BANK_TABLE
    while in_rom(data, address):
        pointer = _u32(data, address)
        if not in_rom(data, pointer):
            break
        found.setdefault(pointer, set()).add(f"bank_table:{address:08X}")
        address += 4
    return found


# --- reporting ---------------------------------------------------------------


@dataclass
class CensusRow:
    address: int
    resource_class: str
    references: int
    wrapper_class: str
    wrapper_words: list[int]
    declared_size: int
    decoded_length: int
    decoded_sha256: str
    anomaly: str = ""


def census(data: bytes, groups: dict[str, dict[int, set[str]]]) -> list[CensusRow]:
    rows: list[CensusRow] = []
    for resource_class, members in groups.items():
        for address in sorted(members):
            kind, declared = wl.read_header(data, address - ROM_BASE)
            anomaly = ""
            decoded = -1
            digest = ""
            try:
                container = wl.unpack(data, address - ROM_BASE)
                decoded = len(container.data)
                digest = hashlib.sha256(container.data).hexdigest()
                if decoded != declared:
                    anomaly = "decoded_length_ne_declared"
            except wl.ContainerError as exc:
                anomaly = f"decode_failed: {exc}"
            if kind not in wl.PACKED_KINDS and kind != wl.STORED:
                anomaly = (anomaly + ";" if anomaly else "") + "unknown_kind"
            rows.append(
                CensusRow(
                    address=address,
                    resource_class=resource_class,
                    references=len(members[address]),
                    wrapper_class=classify_wrapper(data, address),
                    wrapper_words=[_u32(data, address), _u32(data, address + 4)],
                    declared_size=declared,
                    decoded_length=decoded,
                    decoded_sha256=digest,
                    anomaly=anomaly,
                )
            )
    return rows


def census_summary(rows: list[CensusRow]) -> dict[str, object]:
    unique = {row.address for row in rows}
    digests = {row.decoded_sha256 for row in rows if row.decoded_sha256}
    by_class: dict[str, int] = {}
    for row in rows:
        by_class[row.wrapper_class] = by_class.get(row.wrapper_class, 0) + 1
    by_resource: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_resource.setdefault(
            row.resource_class, {"unique_containers": 0, "references": 0}
        )
        bucket["unique_containers"] += 1
        bucket["references"] += row.references
    return {
        "references": sum(row.references for row in rows),
        "unique_containers": len(unique),
        "unique_payload_digests": len(digests),
        "wrapper_classes": by_class,
        "by_resource_class": by_resource,
        "anomalies": [asdict(row) for row in rows if row.anomaly],
        "declared_size_min": min((r.declared_size for r in rows), default=0),
        "declared_size_max": max((r.declared_size for r in rows), default=0),
    }


# --- CLI ---------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom")
    parser.add_argument("--report", action="store_true",
                        help="every section below, in one deterministic pass")
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--census", action="store_true")
    parser.add_argument("--zero-header", action="store_true")
    parser.add_argument("--opening", action="store_true",
                        help="first-token census read from raw bits")
    parser.add_argument("--malformed", action="store_true")
    parser.add_argument("--entry-points", action="store_true")
    parser.add_argument("--json")
    args = parser.parse_args(argv)

    data = load_rom(args.rom)
    out: dict[str, object] = {"rom_sha256": CANONICAL_SHA256}
    do_all = args.report or not (
        args.fixtures
        or args.census
        or args.zero_header
        or args.entry_points
        or args.malformed
        or args.opening
    )

    if args.entry_points or do_all:
        out["entry_points"] = reference.dispatcher_report(data)
        print(json.dumps(out["entry_points"], indent=2))

    if args.fixtures or do_all:
        fixtures = default_fixtures(data)
        out["fixtures"] = [asdict(item) for item in fixtures]
        for item in fixtures:
            status = "AGREE" if item.agrees else "DIFFER"
            print(
                f"[{status}] {item.label:<34} {item.address:08X} "
                f"{item.wrapper_class:<24} declared={item.declared_size:<6} "
                f"project={item.project_length:<6} engine={item.engine_length:<6} "
                f"term={item.engine_terminator}"
            )
            if not item.agrees:
                print(
                    f"         project_error={item.project_error!r} "
                    f"engine_error={item.engine_error!r}"
                )

    if args.census or do_all:
        groups = {
            "dominant_layer_chunk": iter_dominant_chunk_targets(data),
            "selector_stream_root_48": iter_selector_streams(data),
            "selector_bank_root_4c": iter_bank_containers(data),
        }
        rows = census(data, groups)
        summary = census_summary(rows)
        out["census"] = {
            "summary": summary,
            "rows": [asdict(row) for row in rows],
        }
        print(json.dumps(summary, indent=2))

    if args.zero_header or do_all:
        out["zero_header"] = zero_header_report(data)
        print(json.dumps(out["zero_header"], indent=2))

    if args.malformed or do_all:
        out["malformed"] = malformed_report()
        for row in out["malformed"]["cases"]:
            print(f"  {row['case']}")
            print(f"      project   = {row['project']}")
            print(f"      reference = {row['reference']}")
            print(f"      engine    = {row['engine']}")

    if args.opening or do_all:
        out["opening_token"] = opening_token_report(data)
        summary = dict(out["opening_token"])
        summary.pop("examples", None)
        summary.pop("escape_base_byte_histogram", None)
        print(json.dumps(summary, indent=2))

    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


def default_fixtures(data: bytes) -> list[FixtureResult]:
    """A curated span of canonical fixtures across resource classes."""
    chosen: list[tuple[str, str, int, str]] = []

    chunk_targets = iter_dominant_chunk_targets(data)
    ordered = sorted(chunk_targets)
    if ordered:
        picks = [ordered[0], ordered[len(ordered) // 2], ordered[-1]]
        for index, address in enumerate(picks):
            chosen.append(
                (
                    f"dominant_chunk_{index}",
                    "dominant_layer_chunk",
                    address,
                    ",".join(sorted(chunk_targets[address])[:2]),
                )
            )

    streams = sorted(iter_selector_streams(data))
    for index, address in enumerate(streams[:2] + streams[-1:]):
        chosen.append(
            (
                f"selector_stream_{index}",
                "selector_stream_root_48",
                address,
                f"root48:{address:08X}",
            )
        )
    for address in streams:
        if wl.read_header(data, address - ROM_BASE)[0] == 0:
            chosen.append(
                (
                    "zero_header_stored",
                    "selector_stream_root_48",
                    address,
                    f"root48:{address:08X}",
                )
            )
            break

    banks = sorted(iter_bank_containers(data))
    if banks:
        chosen.append(
            ("bank_first", "selector_bank_root_4c", banks[0], "bank_table:08179764")
        )
        chosen.append(
            ("bank_last", "selector_bank_root_4c", banks[-1], "bank_table:08179764")
        )

    # The engine's own default container: kind 0, declared 0. Included so that
    # every row of the evidence document's fixture table is emitted by this
    # command, not only by the integration test.
    chosen.append(
        (
            "engine_default_container",
            "engine_installed_default",
            ENGINE_DEFAULT_CONTAINER,
            f"constructor_pool:{ENGINE_DEFAULT_CONTAINER:#010x}",
        )
    )

    return [
        measure_fixture(
            data, address, label=label, resource_class=resource_class,
            provenance=source,
        )
        for label, resource_class, address, source in chosen
    ]


def zero_header_report(data: bytes) -> dict[str, object]:
    """Every canonically *reachable* container whose first wrapper word is zero.

    Populated only from the accepted resource graphs, so a hit is evidence and
    not a coincidence of an aligned sweep.
    """
    groups = {
        "dominant_layer_chunk": iter_dominant_chunk_targets(data),
        "selector_stream_root_48": iter_selector_streams(data),
        "selector_bank_root_4c": iter_bank_containers(data),
    }
    hits: list[dict[str, object]] = []
    for resource_class, members in groups.items():
        for address in sorted(members):
            kind, declared = wl.read_header(data, address - ROM_BASE)
            if kind != 0:
                continue
            row: dict[str, object] = {
                "address": address,
                "resource_class": resource_class,
                "declared_size": declared,
                "wrapper_words": [kind, declared],
                "references": sorted(members[address])[:4],
                "reference_count": len(members[address]),
                "following_bytes_hex": data[
                    address + 8 - ROM_BASE : address + 8 - ROM_BASE + 16
                ].hex(),
            }
            try:
                container = wl.unpack(data, address - ROM_BASE)
                row["decoded_length"] = len(container.data)
                row["decoded_sha256"] = hashlib.sha256(container.data).hexdigest()
            except wl.ContainerError as exc:
                row["decode_error"] = str(exc)
            hits.append(row)

    # The engine's own default container, referenced by the dominant-layer
    # constructor before it installs anything (LOGX-TILE-001 section 4.4).
    default_row = {
        "address": f"{ENGINE_DEFAULT_CONTAINER:#010x}",
        "wrapper_words": [
            _u32(data, ENGINE_DEFAULT_CONTAINER),
            _u32(data, ENGINE_DEFAULT_CONTAINER + 4),
        ],
        "next_bytes_hex": data[
            ENGINE_DEFAULT_CONTAINER + 8 - ROM_BASE :
            ENGINE_DEFAULT_CONTAINER + 8 - ROM_BASE + 16
        ].hex(),
    }

    return {
        "reachable_zero_header_containers": hits,
        "reachable_zero_header_count": len(hits),
        "engine_default_container": {
            "address": f"{ENGINE_DEFAULT_CONTAINER:#010x}",
            "wrapper_words": [
                _u32(data, ENGINE_DEFAULT_CONTAINER),
                _u32(data, ENGINE_DEFAULT_CONTAINER + 4),
            ],
            "evidence": (
                "The dominant-layer constructor stores this address into the "
                "object's four resident-slot pointers before installing "
                "anything (LOGX-TILE-001 section 4.4). It is kind 0 with a "
                "declared size of 0, and the 0x800 bytes after it are zero."
            ),
        },
        "notes": [
            "A zero first wrapper word selects the engine's stored branch "
            "(0x0803D94C cmp r3,#0 / 0x0803D94E beq 0x0803D95E), which memcpys "
            "container[+0x04] bytes from container+8. It does NOT mean 'empty': "
            "the copy length is the second word.",
        ],
    }


# --- opening token -----------------------------------------------------------


def opening_token_report(data: bytes) -> dict[str, object]:
    """The first token of every reachable packed container, from the raw bits.

    Read without involving any decoder, so it is a check on the grammar rather
    than a consequence of it. The prefix tree is:

    * ``b0`` set -> literal;
    * else ``b1`` set -> long match;
    * else ``b2`` **clear** -> the seven-bit short/control field at ``b3..b9``,
      followed - only when that field is zero - by a two-bit control field at
      ``b10..b11``;
    * else ``b2`` **set** -> the four-bit code at ``b3..b6``, whose zero value is
      the literal-width/base escape; that escape then reads a two-bit field at
      ``b7..b8`` and, when that field is zero, an eight-bit base byte at
      ``b9..b16``.

    Every canonical packed container opens on the four-bit escape. Its two-bit
    field is **not** constant: 3,160 containers select an 8-bit literal width and
    read no base byte at all, while 1,162 keep the 7-bit width and read a base
    byte, which is itself not constant.
    """
    groups = {
        "dominant_layer_chunk": iter_dominant_chunk_targets(data),
        "selector_stream_root_48": iter_selector_streams(data),
        "selector_bank_root_4c": iter_bank_containers(data),
    }
    shapes: dict[str, int] = {}
    prefix_bits: dict[str, int] = {}
    escape_fields: dict[str, int] = {}
    escape_bases: dict[str, int] = {}
    examples: list[dict[str, object]] = []
    total = 0
    for resource_class, members in groups.items():
        for address in sorted(members):
            off = address - ROM_BASE
            kind, declared = wl.read_header(data, off)
            if kind not in wl.PACKED_KINDS:
                continue
            total += 1
            word = struct.unpack_from("<I", data, off + wl.HEADER_SIZE)[0]
            bits = f"{word:032b}"
            prefix_bits[bits[0:3]] = prefix_bits.get(bits[0:3], 0) + 1
            if bits[0] == "1":
                shape = "literal"
            elif bits[1] == "1":
                shape = "long_match"
            elif bits[2] == "0":
                short = int(bits[3:10], 2)
                shape = "short" if short else "seven_bit_control"
            else:
                code = int(bits[3:7], 2)
                shape = f"fourbit_code_{code}" if code else "four_bit_escape"
                if shape == "four_bit_escape":
                    field = int(bits[7:9], 2)
                    escape_fields[str(field)] = escape_fields.get(str(field), 0) + 1
                    if field == 0:
                        base = int(bits[9:17], 2)
                        escape_bases[f"{base:#04x}"] = (
                            escape_bases.get(f"{base:#04x}", 0) + 1
                        )
            shapes[shape] = shapes.get(shape, 0) + 1
            if len(examples) < 8:
                examples.append(
                    {
                        "address": f"{address:#010x}",
                        "resource_class": resource_class,
                        "first_word": f"{word:#010x}",
                        "prefix_bits": bits[0:3],
                        "shape": shape,
                    }
                )
    return {
        "packed_containers": total,
        "prefix_bits_histogram": dict(sorted(prefix_bits.items())),
        "shapes": shapes,
        "escape_two_bit_field": escape_fields,
        "escape_base_byte_histogram": dict(sorted(escape_bases.items())),
        "containers_reading_a_base_byte": sum(escape_bases.values()),
        "distinct_escape_base_bytes": len(escape_bases),
        "examples": examples,
        "note": (
            "Read at the engine's own access width, MSB first from a "
            "little-endian u32. The third prefix bit is a discriminator, not "
            "part of a field: reading the four-bit code at b3 without testing "
            "b2 first takes the wrong branch."
        ),
    }


# --- malformed input ---------------------------------------------------------


def malformed_report() -> dict[str, object]:
    """How the two host decoders answer hostile streams.

    Synthetic data only. Every field is a **host** observation:

    * ``project`` - what ``webfoot_lz.unpack`` does;
    * ``reference`` - what the independent reimplementation does, dispatched the
      same way the engine dispatches (the reference module decodes the packed
      arm only; for stored and unknown forms the engine's own branch is
      reported);
    * ``engine`` - what the engine's instructions would do, reasoned from
      ``0x0803D940`` and stated as "the engine would ...", never as a refusal.

    Nothing here is evidence that the engine validates anything: it validates
    nothing at all.
    """
    cases: list[dict[str, object]] = []

    def container(kind: int, declared: int, payload: bytes) -> bytes:
        return struct.pack("<II", kind, declared) + payload

    trials = {
        "truncated_header": (
            b"\x01\x00\x00",
            "read whatever bytes follow as the two header words",
        ),
        "unknown_kind_3": (
            container(3, 4, b"\x00\x00\x00\x00"),
            "return with the destination untouched",
        ),
        "packed_truncated_payload": (
            container(1, 4096, b"\x00\x00"),
            "read past the container into whatever follows",
        ),
        "packed_declared_zero": (
            container(1, 0, b"\x00\x00\x00\x00"),
            "never read container[+0x04] on the packed path; run the decoder",
        ),
        "stored_runs_past_image": (
            container(0, 0x7FFFFFFF, b"\x00\x00\x00\x00"),
            "memcpy 0x7FFFFFFF bytes from container+8",
        ),
        "stored_declared_zero": (
            container(0, 0, b""),
            "copy zero bytes",
        ),
        "packed_no_end_marker": (
            container(1, 8, b"\xff\xff\xff\xff" * 4),
            "keep decoding; no size comparison is made",
        ),
        "packed_backreference_before_start": (
            container(1, 64, bytes.fromhex("2000114f")),
            "copy from bytes before the destination buffer",
        ),
    }
    for name, (blob, engine_would) in trials.items():
        row: dict[str, object] = {
            "case": name,
            "length": len(blob),
            "engine": engine_would,
        }
        try:
            project = wl.unpack(blob, 0)
            row["project"] = f"accepted:{len(project.data)}"
        except wl.ContainerError as exc:
            row["project"] = f"refused:{exc}"
        if len(blob) >= wl.HEADER_SIZE:
            kind, declared = wl.read_header(blob, 0)
        else:
            kind, declared = -1, 0
        if kind == 0:
            row["reference"] = "no stored-form decoder (engine branch reported)"
        elif kind in wl.PACKED_KINDS:
            try:
                decoded = reference.decode_packed(
                    blob, wl.HEADER_SIZE, declared_size=declared
                )
                row["reference"] = f"accepted:{decoded.actual_size}:{decoded.terminator}"
            except reference.CodecError as exc:
                row["reference"] = f"refused:{exc}"
        else:
            row["reference"] = "no packed-form decoder (engine branch reported)"
        cases.append(row)

    return {
        "cases": cases,
        "note": (
            "Every refusal above is host-side policy. The engine's decoder has "
            "no bounds check, no kind validation beyond the 0/1/2 dispatch, and "
            "no declared-size comparison; the 'engine' column states what its "
            "instructions would do, which is never a refusal."
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
