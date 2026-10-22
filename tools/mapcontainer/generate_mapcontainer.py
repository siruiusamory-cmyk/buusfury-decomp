"""Extract, emit and verify a packed-container block: the map block 0x179A50..0x2B8BC8, the
sprite block 0x3C34D0..0x6A88AC, the end-of-ROM block 0x6B7E8C..0x7B79A4 and the record-only
sprite family 0x6A88AC..0x6B7E8C. `--block map|sprite|endrom|spritedefs` selects the walk, the
record families and the measured contract.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import multiprocessing
import os
import pickle
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "gate"))
sys.path.insert(0, os.path.join(ROOT, "tools", "webfoot"))
sys.path.insert(0, os.path.join(ROOT, "tools", "spritecontainer"))

import ainodes
import cellmap
import assetdir
import assetdir2
import def50
import emitted
import encode_cache
import endrombank
import endromcontainer
import endromfacing
import endromrecords
import pairsprite
import enemystats
import eventindex
import eventpool
import gate  # noqa: E402
import globalstate
import glyphtable
import mapcontainer
import payload_store
import romfile
import rowtable
import spritecontainer
import spritefamily
import webfoot_lz

ROM_SHA256 = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
ROM_BASE = 0x08000000
KIND = 1
COMPRESS = os.path.join(ROOT, "tools", "compress", "compress.exe")
CARVE_OUT_FIELDS = ("container_file_offset", "stored_size", "declared_size", "disposition",
                    "reason")
ORACLE_WORKERS = 32
DECODE_WORKERS = 8
MANIFEST_FIELDS = ("kind", "start", "end", "bytes", "index", "container_file_offset",
                   "declared_size", "stored_size", "payload_file", "stored_sha256")
MEMBERS_STORE_VERSION = 1


@dataclass(frozen=True)
class Block:

    name: str
    walk: object
    start: int
    end: int
    edges: tuple
    max_payload: int
    prefix: str
    out_dir: str
    carve_manifest: str
    expected_containers: int
    expected_marker_union: int
    expected_declared: dict
    carve_outs: frozenset
    before_slice: tuple
    after_slice: tuple
    expected_early_union: int | None = None
    expected_tails: dict | None = None
    expected_records: dict | None = None
    serializers: dict = None
    record_walk: object = None
    ledger_region: str = ""
    records_store: str = "assets/maprecords"
    records_exact: bool = True
    scan_walk: object = None
    scan_max_payload: int = None

    @property
    def record_families(self) -> tuple:
        return () if not self.serializers else tuple(self.serializers)


MAP_RECORDS = {mapcontainer.ROOT: (427, 34160, 426, 34080),
               mapcontainer.DOMINANT_FAMILY: (1439, 51184, 1438, 51140),
               mapcontainer.SCREENBLOCK_A: (1, 12, 1, 12),
               mapcontainer.SCREENBLOCK_B: (41, 1312, 41, 1312),
               mapcontainer.TERRAIN_FAMILY: (1, 568, 1, 568),
               mapcontainer.ROOT_TABLE: (949, 22776, 949, 22776),
               mapcontainer.ROOT_POINTER: (740, 2960, 740, 2960),
               mapcontainer.MODE_ROW: (358, 28288, 358, 28288)}
MAP_SERIALIZERS = {family: mapcontainer.serialize_record for family in MAP_RECORDS}
MAP_SERIALIZERS[mapcontainer.MODE_ROW] = mapcontainer.serialize_mode_row


SPRITE_FAMILY_RECORDS = {spritefamily.DEFINITION: (297, 57868, 297, 57868),
                         spritefamily.INDEX: (1, 1188, 1, 1188),
                         spritefamily.ANIMATION: (1017, 58708, 1, 52),
                         spritefamily.FRAME: (10980, 219900, 12, 240),
                         def50.FAMILY: (10, 696, 0, 0),
                         def50.CELL_FAMILY: (126, 3656, 0, 0)}
SPRITE_BLOCK_RECORDS = {spritefamily.ANIMATION: (1017, 58708, 1016, 58656),
                        spritefamily.FRAME: (10980, 219900, 10968, 219660),
                        def50.FAMILY: (10, 696, 10, 696),
                        def50.CELL_FAMILY: (126, 3656, 126, 3656)}
SPRITE_FAMILY_SERIALIZERS = dict.fromkeys(spritefamily.FAMILIES, spritefamily.serialize_record)
SPRITE_FAMILY_SERIALIZERS[def50.FAMILY] = def50.serialize_record
SPRITE_FAMILY_SERIALIZERS[def50.CELL_FAMILY] = def50.serialize_record
SPRITE_BLOCK_SERIALIZERS = dict.fromkeys((spritefamily.ANIMATION, spritefamily.FRAME),
                                         spritefamily.serialize_record)
SPRITE_BLOCK_SERIALIZERS[def50.FAMILY] = def50.serialize_record
SPRITE_BLOCK_SERIALIZERS[def50.CELL_FAMILY] = def50.serialize_record
SPRITE_RECORDS_STORE = "assets/spriterecords"


def sprite_block_extents(rom):
    rows = spritefamily.extents(rom, spritefamily.ANIMATION)
    rows.update(spritefamily.extents(rom, spritefamily.FRAME))
    rows.update(def50.extents(rom))
    return rows


def spritedefs_extents(rom):
    rows = spritefamily.extents(rom)
    rows.update(def50.extents(rom))
    return rows

ENDROM_RECORDS = {endromrecords.FAMILY: (162, 7128, 162, 7128),
                  endrombank.FAMILY: (1, 652, 1, 652),
                  ainodes.FAMILY: (2505, 53168, 2504, 53152),
                  rowtable.FAMILY: (828, 6624, 828, 6624),
                  enemystats.FAMILY: (150, 4200, 150, 4200),
                  eventindex.FAMILY: (1, 2088, 1, 2088),
                  eventpool.FAMILY: (522, 127328, 522, 127328),
                  globalstate.FAMILY: (1, 40, 1, 40),
                  glyphtable.FAMILY: (85, 680, 85, 680),
                  cellmap.FAMILY: (53, 848, 53, 848),
                  pairsprite.FAMILY: (4, 96, 4, 96),
                  endromfacing.FAMILY: (4, 32, 4, 32),
                  "endrom_sprite_record_r20": (4, 144, 4, 144),
                  "endrom_sprite_record_r25": (4, 144, 4, 144)}
ENDROM_RECORD_SERIALIZERS = {endromrecords.FAMILY: endromrecords.serialize_record,
                             endrombank.FAMILY: endrombank.serialize_record,
                             ainodes.FAMILY: ainodes.serialize_record,
                             rowtable.FAMILY: rowtable.serialize_record,
                             enemystats.FAMILY: enemystats.serialize_record,
                             eventindex.FAMILY: eventindex.serialize_record,
                             eventpool.FAMILY: eventpool.serialize_record,
                             globalstate.FAMILY: globalstate.serialize_record,
                             glyphtable.FAMILY: glyphtable.serialize_record,
                             cellmap.FAMILY: cellmap.serialize_record,
                             pairsprite.FAMILY: pairsprite.serialize_record,
                             endromfacing.FAMILY: endromfacing.serialize_record,
                             "endrom_sprite_record_r20": pairsprite.serialize_record,
                             "endrom_sprite_record_r25": pairsprite.serialize_record}
ENDROM_RECORDS_STORE = "assets/endromrecords"


ASSETDIR_RECORDS = {assetdir.DIRECTORY: (64, 768, 64, 768),
                    assetdir.BLOCK: (64, 390901, 64, 390901),
                    assetdir2.DIRECTORY: (79, 948, 79, 948),
                    assetdir2.BLOCK: (79, 343010, 79, 343010)}
ASSETDIR_SERIALIZERS = {assetdir.DIRECTORY: assetdir.serialize_record,
                        assetdir.BLOCK: assetdir.serialize_record,
                        assetdir2.DIRECTORY: assetdir2.serialize_record,
                        assetdir2.BLOCK: assetdir2.serialize_record}
ASSETDIR_RECORDS_STORE = "assets/assetdirrecords"


def assetdir_extents(rom):
    rows = assetdir.extents(rom)
    rows.update(assetdir2.extents(rom))
    return rows


def endrom_record_extents(rom):
    rows = endromrecords.extents(rom)
    rows.update(endrombank.extents(rom))
    rows.update(ainodes.extents(rom))
    rows.update(rowtable.extents(rom))
    rows.update(enemystats.extents(rom))
    rows.update(eventindex.extents(rom))
    rows.update(eventpool.extents(rom))
    rows.update(globalstate.extents(rom))
    rows.update(glyphtable.extents(rom))
    rows.update(cellmap.extents(rom))
    rows.update(pairsprite.extents(rom))
    rows.update(endromfacing.extents(rom))
    return rows


MAP = Block("map", mapcontainer.container_offsets, 0x179A50, 0x2B8BC8, (0x179A50, 0x2B8BC8), 0x800,
            "mapc_%07x.bin", "mapcontainer", "tools/mapcontainer/mapcontainer_manifest.csv", 5069,
            1056476, {            34: 1, 64: 2, 82: 1, 84: 1, 88: 1, 104: 2, 108: 1, 112: 1, 116: 1, 118: 1, 120: 1,
                        128: 1, 144: 1, 158: 1, 176: 2, 182: 1, 186: 2, 194: 2, 198: 1, 200: 1, 204: 1, 208: 2,
                        210: 3, 214: 1, 216: 1, 222: 1, 224: 2, 230: 1, 236: 2, 238: 1, 242: 1, 244: 1, 246: 2,
                        256: 7, 262: 1, 266: 1, 268: 2, 270: 1, 272: 2, 276: 1, 280: 1, 288: 1, 290: 1, 292: 1,
                        294: 1, 296: 1, 298: 2, 302: 1, 304: 1, 308: 3, 310: 2, 314: 1, 318: 3, 328: 1, 332: 1,
                        338: 3, 340: 2, 346: 2, 348: 2, 350: 2, 354: 3, 356: 2, 360: 3, 362: 2, 364: 1, 370: 2,
                        372: 2, 376: 1, 380: 1, 384: 1, 386: 1, 388: 1, 392: 1, 394: 2, 400: 1, 402: 2, 404: 1,
                        406: 2, 408: 1, 410: 4, 412: 2, 414: 1, 420: 1, 422: 1, 426: 2, 428: 1, 430: 2, 432: 2,
                        436: 1, 440: 2, 442: 2, 446: 3, 450: 2, 452: 1, 454: 1, 456: 5, 458: 4, 460: 1, 464: 3,
                        466: 2, 468: 3, 474: 2, 476: 1, 478: 3, 480: 1, 482: 2, 484: 1, 488: 1, 492: 2, 494: 2,
                        496: 1, 498: 1, 502: 3, 504: 1, 508: 2, 512: 8, 514: 1, 518: 3, 522: 3, 526: 3, 528: 1,
                        530: 3, 532: 1, 534: 1, 538: 1, 540: 3, 542: 2, 544: 1, 548: 2, 552: 1, 554: 1, 560: 1,
                        562: 1, 564: 1, 566: 1, 572: 1, 574: 1, 582: 1, 586: 2, 588: 1, 592: 1, 594: 2, 596: 1,
                        598: 1, 600: 1, 602: 1, 612: 1, 614: 2, 618: 1, 620: 1, 634: 1, 636: 1, 638: 1, 642: 1,
                        646: 1, 648: 1, 656: 2, 658: 1, 664: 1, 666: 1, 668: 1, 684: 1, 690: 2, 692: 3, 694: 4,
                        700: 3, 704: 1, 710: 1, 714: 1, 720: 1, 734: 1, 740: 1, 742: 2, 746: 1, 748: 2, 750: 2,
                        752: 1, 754: 2, 762: 1, 768: 2, 776: 1, 780: 1, 804: 1, 808: 1, 814: 2, 818: 1, 822: 1,
                        824: 1, 830: 1, 836: 1, 842: 1, 844: 2, 848: 1, 852: 1, 854: 1, 860: 1, 862: 2, 882: 2,
                        884: 2, 886: 3, 888: 1, 890: 2, 896: 1, 900: 1, 904: 1, 912: 1, 916: 1, 946: 1, 956: 1,
                        958: 1, 970: 1, 976: 1, 988: 1, 990: 1, 992: 1, 996: 1, 1018: 1, 1024: 163, 1026: 1,
                        1030: 1, 1036: 2, 1044: 1, 1056: 1, 1060: 1, 1078: 2, 1080: 3, 1088: 1, 1104: 1,
                        1130: 1, 1132: 1, 1162: 1, 1168: 1, 1174: 1, 1180: 1, 1186: 1, 1196: 1, 1200: 1,
                        1208: 1, 1216: 1, 1220: 1, 1226: 1, 1228: 1, 1244: 1, 1268: 1, 1280: 2, 1300: 1,
                        1304: 1, 1306: 1, 1318: 1, 1340: 1, 1374: 1, 1376: 1, 1408: 1, 1414: 1, 1430: 1,
                        1496: 1, 1498: 1, 1512: 1, 1514: 1, 1520: 1, 1536: 3, 1538: 1, 1548: 1, 1558: 1,
                        1586: 1, 1598: 1, 1602: 1, 1614: 1, 1616: 1, 1634: 1, 1648: 1, 1654: 1, 1662: 1,
                        1674: 1, 1676: 1, 1678: 1, 1712: 1, 1718: 1, 1720: 1, 1726: 1, 1728: 1, 1734: 1,
                        1740: 1, 1744: 1, 1748: 1, 1750: 1, 1756: 1, 1768: 1, 1784: 1, 1792: 7, 1920: 1,
                        2048: 3830, 2112: 1, 2304: 5, 2432: 1, 2560: 4, 2816: 5, 3072: 7, 3584: 1, 4096: 11,
                        4352: 1, 5120: 5, 6144: 5, 6912: 1, 7168: 1, 7424: 1, 7936: 1, 8192: 598, 8704: 3,
                        9984: 1, 12608: 1, 15872: 1}, frozenset([0x29B308]), (0x179764, 0x179A50),
            (0x2B8BC8, 0x3715C0), 1048692, {0: 3123, 4: 1946},
            expected_records=MAP_RECORDS, serializers=MAP_SERIALIZERS,
            scan_walk=mapcontainer.packed_container_offsets, scan_max_payload=0x10000)
SPRITE = Block("sprite", spritecontainer.container_offsets, 0x3C34D0, 0x6A88AC,
               (0x3C34D0, 0x6A88AC), 0x4000, "sprite_%07x.bin", "spritecontainer",
               "tools/spritecontainer/spritecontainer_manifest.csv", 7390, 2753456,
               {64: 6, 128: 4, 256: 29, 512: 2890, 1024: 3251, 2048: 281, 4096: 929},
               frozenset(), (0x3C33F8, 0x3C34D0), (0x6A88AC, 0x7B79A4),
               expected_records=SPRITE_BLOCK_RECORDS, serializers=SPRITE_BLOCK_SERIALIZERS,
               record_walk=sprite_block_extents,
               records_store=SPRITE_RECORDS_STORE, records_exact=False)
ENDROM = Block("endrom", endromcontainer.container_offsets, 0x6B7E8C, 0x7B79A4, (0x6B7E8C, 0x7B5B64),
               0x10000, "endrom_%07x.bin", "endrom", "tools/mapcontainer/endromcontainer_manifest.csv",
               427, 440696,
               {64: 7, 128: 16, 192: 4, 256: 168, 264: 1, 320: 1, 384: 2, 436: 1, 477: 1, 512: 2,
                576: 2, 832: 1, 960: 1, 1152: 1, 1216: 1, 1408: 2, 1600: 1, 1664: 1, 1984: 2,
                2048: 2, 2112: 1, 2176: 2, 2368: 1, 2560: 1, 2752: 1, 2880: 2, 3072: 2, 3200: 1,
                3264: 1, 3648: 1, 3904: 1, 4096: 155, 4160: 1, 4480: 1, 4544: 1, 4800: 1, 5184: 1,
                5376: 1, 5824: 1, 6080: 1, 6336: 1, 9024: 1, 9408: 1, 9536: 1, 10816: 1, 11392: 2,
                11776: 2, 11904: 1, 13568: 1, 14400: 1, 15296: 1, 15936: 1, 18048: 1, 20480: 1,
                23552: 1, 27712: 1, 33856: 1, 37184: 2, 38400: 6, 65322: 1, 65334: 1, 65348: 1,
                65394: 1, 65464: 1, 65474: 1},
               frozenset(), (0x6A7EB0, 0x6B7E8C), (0x7B5B64, 0x7B79A4), 440000, {0: 253, 4: 174},
               expected_records=ENDROM_RECORDS, serializers=ENDROM_RECORD_SERIALIZERS,
               record_walk=endrom_record_extents, records_store=ENDROM_RECORDS_STORE)
SPRITEDEFS = Block("spritedefs", lambda rom: [], 0x6A88AC,
                   0x6B7E8C, (0x6A88AC, 0x6B7E8C),
                   0, "spritedefs_%07x.bin", "spritedefs",
                   "tools/spritecontainer/spritecontainer_manifest.csv", 0, 0, {},
                   frozenset(), (0x6A88AC, spritefamily.DEFINITION_START),
                   (spritefamily.TABLE_END, 0x6B7E8C), serializers=SPRITE_FAMILY_SERIALIZERS,
                   expected_records=SPRITE_FAMILY_RECORDS, record_walk=spritedefs_extents,
                   ledger_region="spritedefs_%x_%s", records_store=SPRITE_RECORDS_STORE,
                   records_exact=False)
ASSETDIR = Block("assetdir", lambda rom: [], 0x2B8BC8, 0x3715C0, (0x2B8BC8, 0x3715C0), 0,
                 "assetdir_%08X.bin", "assetdir",
                 "tools/mapcontainer/endromcontainer_manifest.csv", 0, 0, {}, frozenset(),
                 (0x2B8BC8, 0x2B8BC8), (0x3715C0, 0x3715C0),
                 expected_records=ASSETDIR_RECORDS, serializers=ASSETDIR_SERIALIZERS,
                 record_walk=assetdir_extents, ledger_region="assetdir_%x_%s",
                 records_store=ASSETDIR_RECORDS_STORE)
BLOCKS = {block.name: block for block in (MAP, SPRITE, ENDROM, SPRITEDEFS, ASSETDIR)}
BLOCK = MAP


def set_block(name):
    global BLOCK
    BLOCK = BLOCKS[name]
    return BLOCK


def read_rom(path):
    return romfile.read_rom(path, ROM_SHA256)


def members_cache():
    return os.path.join(ROOT, "build", BLOCK.out_dir, "members.pickle")


MAP_SOURCE = os.path.join(ROOT, "asm", "rest_of_the_game.s")


def foreign_runs(span, text=None):
    text = emitted.source_text(ROOT, MAP_SOURCE) if text is None else text
    own = ("build", BLOCK.out_dir)
    out = []
    for token, (start, end) in emitted.token_ranges(text):
        parts = token.replace("\\", "/").split("/")
        if len(parts) > 1 and (parts[0], parts[1]) == own:
            continue
        if not token.endswith(".bin") or not (span[0] <= start and end <= span[1]):
            continue
        out.append((start, end))
    return out


def carve_manifest_path():
    return os.path.join(ROOT, BLOCK.carve_manifest)


def source_key(rom):
    parts = [hashlib.sha256(rom).hexdigest()]
    paths = [__file__, carve_manifest_path(), os.path.join(HERE, "mapcontainer.py"),
             os.path.join(ROOT, "tools", "webfoot", "webfoot_lz.py"),
             sys.modules[BLOCK.walk.__module__].__file__]
    for path in dict.fromkeys(paths):
        parts.append(hashlib.sha256(open(path, "rb").read()).hexdigest())
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def cached_members(rom):
    path = members_cache()
    try:
        with open(path, "rb") as handle:
            version, key, walked, members = pickle.load(handle)
    except Exception:
        return None
    if version != MEMBERS_STORE_VERSION or key != source_key(rom):
        return None
    return walked, members


def store_members(rom, offsets, members):
    path = members_cache()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as handle:
        pickle.dump((MEMBERS_STORE_VERSION, source_key(rom), offsets, members), handle)
    os.replace(tmp, path)


def read_members(rom, pool=None, published=False, workers=DECODE_WORKERS):
    if not BLOCK.expected_containers:
        if BLOCK.walk(rom):
            raise SystemExit("the %s block's walk reaches containers, so it is not record-only"
                             % BLOCK.name)
        return []
    held = cached_members(rom) if not published else None
    store = not published and held is None
    if held is None:
        offsets = BLOCK.walk(rom)
        members = decode_offsets(rom, offsets, workers)
        if BLOCK.scan_walk:
            records = (BLOCK.record_walk or mapcontainer.record_extents)(rom)
            excluded = [(member.offset, member.offset + member.stored_size) for member in members]
            excluded += [(start, start + size) for rows in records.values() for start, size in rows]
            excluded += foreign_runs((BLOCK.start, BLOCK.end))
            scanned = BLOCK.scan_walk(rom, (BLOCK.start, BLOCK.end), excluded)
            offsets = sorted(set(offsets) | set(scanned))
            members = members + decode_offsets(rom, scanned, workers, BLOCK.scan_max_payload)
            members.sort(key=lambda member: member.offset)
    else:
        offsets, members = held
    foreign = foreign_runs((BLOCK.start, BLOCK.end))
    kept = [member for member in members
            if not any(max(member.offset, start) < min(member.offset + member.stored_size, end)
                       for start, end in foreign)]
    dropped = len(members) - len(kept)
    members = kept
    offsets = [member.offset for member in members]
    if published and BLOCK.expected_early_union is not None:
        early = decode_extents(rom, offsets, workers,
                               BLOCK.scan_max_payload or BLOCK.max_payload)
    marker_union = sum(member.stored_size for member in members)
    declared = {}
    for member in members:
        declared[member.declared_size] = declared.get(member.declared_size, 0) + 1
    if len(members) != BLOCK.expected_containers:
        raise SystemExit("%d containers, expected %d" % (len(members), BLOCK.expected_containers))
    if marker_union != BLOCK.expected_marker_union:
        raise SystemExit("marker union %d; expected %d"
                         % (marker_union, BLOCK.expected_marker_union))
    if published and BLOCK.expected_early_union is not None:
        early_union = sum(early)
        tails = {}
        for member, early_size in zip(members, early):
            tail = member.stored_size - early_size
            tails[tail] = tails.get(tail, 0) + 1
        if early_union != BLOCK.expected_early_union:
            raise SystemExit("early union %d; expected %d" % (early_union,
                                                              BLOCK.expected_early_union))
        if tails != BLOCK.expected_tails:
            raise SystemExit("terminator tails %s; expected %s" % (tails, BLOCK.expected_tails))
    if (members[0].offset, members[-1].offset + members[-1].stored_size) != BLOCK.edges:
        raise SystemExit("the population spans %#x..%#x, not the measured %s"
                         % (members[0].offset, members[-1].offset + members[-1].stored_size,
                            tuple("%#x" % edge for edge in BLOCK.edges)))
    if declared != BLOCK.expected_declared:
        raise SystemExit("declared sizes %s" % declared)
    if any(member.kind != KIND for member in members):
        raise SystemExit("not every container is kind %d" % KIND)
    if read_carve_outs(carve_manifest_path()) != BLOCK.carve_outs:
        raise SystemExit("the carve-out manifest is not the %d expected offset(s)"
                         % len(BLOCK.carve_outs))
    for member in members:
        if member.offset in BLOCK.carve_outs:
            row = carve_out_rows(carve_manifest_path())[member.offset]
            if (row[0], row[1]) != (member.stored_size, member.declared_size):
                raise SystemExit("carve-out %#x is stored %d declared %d, not the manifest's %s"
                                 % (member.offset, member.stored_size, member.declared_size, row))
    if dropped:
        print("containers inside another emitter's generated run, so not this plan's: %d" % dropped)
    if store:
        store_members(rom, offsets, members)
    return members


def carve_out_rows(path):
    if not os.path.exists(path):
        raise SystemExit("the carve-out manifest %s is missing" % path)
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != CARVE_OUT_FIELDS:
            raise SystemExit("carve-out manifest columns are %s" % (reader.fieldnames,))
        rows = list(reader)
    if len(rows) != len(BLOCK.carve_outs):
        raise SystemExit("the carve-out manifest holds %d rows" % len(rows))
    found = {}
    for row in rows:
        if row["disposition"] != "carve-out":
            raise SystemExit("carve-out row %s is disposition %s"
                             % (row["container_file_offset"], row["disposition"]))
        found[int(row["container_file_offset"], 0)] = (int(row["stored_size"]),
                                                       int(row["declared_size"]))
    return found


def read_carve_outs(path):
    return frozenset(carve_out_rows(path))


def payload_name(offset):
    return BLOCK.prefix % offset


def section_output(section):
    if section.kind in BLOCK.record_families or (
            section.kind == mapcontainer.CONTAINER and BLOCK.serializers):
        return os.path.join("build", BLOCK.out_dir,
                            "%s_%08X_%08X.bin" % (BLOCK.name, section.start, section.end))
    if section.kind == mapcontainer.CONTAINER:
        return os.path.join("build", BLOCK.out_dir, "gen_%x_%x.bin" % (section.start, section.end))
    return "baserom.gba_0x%x_0x%x.extracted" % (section.start, section.end)


def compressor(exe, scratch):
    local = threading.local()

    def compress(payload):
        if not hasattr(local, "stem"):
            local.stem = os.path.join(scratch, "mapcontainer-%d" % threading.get_ident())
        stem = local.stem
        try:
            os.remove(stem + ".out")
        except OSError:
            pass
        with open(stem + ".in", "wb") as handle:
            handle.write(payload)
        proc = subprocess.run([exe, stem + ".in", stem + ".out"], capture_output=True)
        try:
            blob = open(stem + ".out", "rb").read()
        except OSError:
            raise SystemExit("compress.exe exit %d on %d bytes wrote no output: %s"
                             % (proc.returncode, len(payload),
                                (proc.stdout + proc.stderr).decode("utf-8", "replace").strip()))
        if proc.returncode != 0:
            raise SystemExit("compress.exe exit %d on %d bytes: %s"
                             % (proc.returncode, len(payload),
                                (proc.stdout + proc.stderr).decode("utf-8", "replace").strip()))
        return blob

    return compress


def load_store(payloads, members):
    path = payload_store.path(payloads)
    if not members:
        return ([0, 0] if not os.path.exists(path) else payload_store.stamp(path)), {}
    try:
        store = payload_store.read(path)
    except (OSError, ValueError) as exc:
        raise SystemExit("the payload store %s is unreadable: %s" % (path, exc))
    for member in members:
        payload = store.get(member.offset)
        if payload is None or len(payload) != member.declared_size:
            raise SystemExit("the payload store holds no %d-byte payload at %#x"
                             % (member.declared_size, member.offset))
    return payload_store.stamp(path), store


def payload_member(member, store):
    return mapcontainer.Member(member.kind, member.declared_size, store[member.offset],
                               member.stored_size, member.offset)


def payload_members(runs, store):
    return {start: [payload_member(member, store) for member in run]
            for start, run in runs.items()}


def read_records(rom, members=None):
    if not BLOCK.serializers:
        members = read_members(rom) if members is None else members
        return None
    walk = BLOCK.record_walk or mapcontainer.record_extents
    extents = walk(rom)
    members = read_members(rom) if members is None else members
    if mapcontainer.MODE_ROW in BLOCK.record_families:
        claimed = [(member.offset, member.offset + member.stored_size) for member in members]
        claimed += [(offset, offset + length) for rows in extents.values()
                    for offset, length in rows]
        claimed += foreign_runs((BLOCK.start, BLOCK.end))
        extents[mapcontainer.MODE_ROW] = mapcontainer.mode_row_sites(
            rom, (BLOCK.start, BLOCK.end), claimed)
    for family, (records, total, inside, inside_bytes) in BLOCK.expected_records.items():
        rows = extents[family]
        kept = mapcontainer.clip(rows, (BLOCK.start, BLOCK.end))
        if len(rows) != records or sum(length for _, length in rows) != total:
            raise SystemExit("%s walks to %d records / %d B, not the measured %d / %d"
                             % (family, len(rows), sum(length for _, length in rows),
                                records, total))
        if len(kept) != inside or sum(end - start for start, end in kept) != inside_bytes:
            raise SystemExit("%s keeps %d in-block records / %d B, not the measured %d / %d"
                             % (family, len(kept), sum(end - start for start, end in kept),
                                inside, inside_bytes))
    if members:
        spans = sorted((member.offset, member.offset + member.stored_size) for member in members)
        records = sorted((offset, offset + length, family)
                         for family, rows in extents.items() for offset, length in rows)
        index = 0
        for start, end, family in records:
            while index + 1 < len(spans) and spans[index + 1][0] <= start:
                index += 1
            while index < len(spans) and spans[index][0] < end:
                if spans[index][1] > start:
                    raise SystemExit("%s at %#x overlaps the container at %#x, so it is not new"
                                     % (family, start, spans[index][0]))
                index += 1
    return extents


def plan_records(rom, members=None):
    return (read_records(rom, members), BLOCK.serializers, BLOCK.expected_records)


def read_plan(rom, manifest, pool=None, published=False):
    carve_outs = read_carve_outs(manifest)
    members = read_members(rom, pool, published)
    extents, spec, expected = plan_records(rom, members)
    records = extents is not None
    families = BLOCK.record_families
    kept = None
    if records:
        kept = {family: mapcontainer.clip(extents[family], (BLOCK.start, BLOCK.end))
                for family in families}
    container_offsets = [member.offset for member in members]
    if records:
        runs = mapcontainer.record_sections(BLOCK.start, BLOCK.end, kept, families)
        offsets = container_offsets + list(runs[0])
        sizes = [member.stored_size for member in members] + list(runs[1])
        kinds = [mapcontainer.CONTAINER] * len(members) + list(runs[2])
        order = sorted(range(len(offsets)), key=lambda index: offsets[index])
        sections = mapcontainer.plan_sections(
            BLOCK.start, BLOCK.end, [offsets[index] for index in order],
            [sizes[index] for index in order],
            carve_outs, [kinds[index] for index in order])
    else:
        sections = mapcontainer.plan_sections(
            BLOCK.start, BLOCK.end, container_offsets,
            [member.stored_size for member in members], carve_outs)
    runs = mapcontainer.members_of(sections, members)
    if not records:
        return members, sections, {"containers": runs, "records": {}, "extents": None,
                                   "all": None, "families": (), "expected": None}
    return members, sections, {"containers": runs,
                               "records": mapcontainer.record_members(sections, kept, families),
                               "extents": kept, "all": extents, "families": families,
                               "expected": expected}


def _decode_chunk(arguments):
    rom, offsets, maximum = arguments
    return [mapcontainer.decode(rom, offset, maximum) for offset in offsets]


def _extent_chunk(arguments):
    rom, offsets, maximum = arguments
    return [mapcontainer.early_extent(rom, offset, maximum) for offset in offsets]


def decode_offsets(rom, offsets, workers, maximum=None):
    maximum = BLOCK.max_payload if maximum is None else maximum
    if workers <= 1:
        return _decode_chunk((rom, offsets, maximum))
    with multiprocessing.Pool(workers) as pool:
        chunks = pool.map(_decode_chunk, _split(rom, offsets, maximum, workers))
    return [member for chunk in chunks for member in chunk]


def decode_extents(rom, offsets, workers, maximum=None):
    maximum = BLOCK.max_payload if maximum is None else maximum
    if workers <= 1:
        return _extent_chunk((rom, offsets, maximum))
    with multiprocessing.Pool(workers) as pool:
        chunks = pool.map(_extent_chunk, _split(rom, offsets, maximum, workers))
    return [extent for chunk in chunks for extent in chunk]


def _split(rom, offsets, maximum, parts):
    step = max(1, len(offsets) // parts)
    return [(rom, offsets[start:start + step], maximum)
            for start in range(0, len(offsets), step)]


def write_incbin(path, sections):
    lines = ["        INCBIN  %s" % section_output(section).replace(os.sep, "\\")
             for section in sections]
    with open(path, "w", newline="\n", encoding="ascii") as handle:
        handle.write("\n".join(lines) + "\n")
    return lines


def record_payloads(rom, extents):
    return [(offset, family, size, BLOCK.serializers[family](rom, family, offset, size))
            for family in BLOCK.record_families
            for offset, size in extents[family]]


def load_record_store(path, payloads, exact=True):
    try:
        store = payload_store.read(path)
    except (OSError, ValueError) as exc:
        raise SystemExit("the record store %s is unreadable: %s" % (path, exc))
    keys = {offset for offset, _, _, _ in payloads}
    holds = set(store) == keys if exact else keys <= set(store)
    if not holds:
        raise SystemExit("the record store holds %d entries, the plan %s %d"
                         % (len(store), "has" if exact else "needs at least", len(keys)))
    for offset, family, size, _ in payloads:
        if len(store[offset]) != size:
            raise SystemExit("the record store's %#x is %d bytes, the %s is %d"
                             % (offset, len(store[offset]), family, size))
    return store


def cmd_extract(args):
    rom = read_rom(args.rom)
    members = read_members(rom, published=True)
    declared = {}
    for member in members:
        declared[member.declared_size] = declared.get(member.declared_size, 0) + 1
    if members:
        os.makedirs(args.payloads, exist_ok=True)
        stamped = payload_store.write(payload_store.path(args.payloads),
                                      [(member.offset, member.payload) for member in members])
        print("containers=%d first=0x%x last_end=0x%x kinds=%s declared=%s"
              % (len(members), members[0].offset,
                 members[-1].offset + members[-1].stored_size, {KIND: len(members)},
                 dict(sorted(declared.items()))))
        print("wrote %d payloads to %s, %d bytes" % (len(members),
                                                     payload_store.path(args.payloads), stamped[0]))
    records = read_records(rom, members)
    if records is None:
        return 0
    payloads = record_payloads(rom, records)
    for offset, family, size, blob in payloads:
        if blob != rom[offset:offset + size]:
            raise SystemExit("%s at %#x does not re-serialize to its own bytes" % (family, offset))
        if family not in BLOCK.record_families:
            raise SystemExit("%s at %#x is not this block's record" % (family, offset))
    if len({offset for offset, _, _, _ in payloads}) != len(payloads):
        raise SystemExit("two records claim one store key")
    os.makedirs(args.records, exist_ok=True)
    stamp = payload_store.write(payload_store.path(args.records),
                                [(offset, blob) for offset, _, _, blob in payloads])
    for family in BLOCK.record_families:
        rows = [item for item in payloads if item[1] == family]
        print("records %-24s %5d records %7d bytes"
              % (family, len(rows), sum(item[2] for item in rows)))
    print("wrote %d records to %s, %d bytes" % (len(payloads), payload_store.path(args.records),
                                                stamp[0]))
    return 0


def digest(data):
    return hashlib.sha256(data).hexdigest()


def skip_unchanged(path, blob, written):
    return (written.get(path) == [len(blob), digest(blob)] and os.path.exists(path)
            and os.path.getsize(path) == len(blob))


def sections_match(sections, written):
    for section in sections:
        path = os.path.join(ROOT, section_output(section))
        recorded = written.get(path)
        if recorded is None or not os.path.exists(path) or os.path.getsize(path) != recorded[0]:
            return False
    return True


def assert_encode_accounting(cache, population):
    spawns, hits, total = cache["spawns"], cache["hits"], cache["total"]
    if total != population or spawns + hits != population:
        raise SystemExit("encode accounting: %d spawn(s) + %d hit(s) over a cache total of %d,"
                         " against the %d-member population this run encoded"
                         % (spawns, hits, total, population))


def cmd_build(args):
    started = time.perf_counter()
    rom = read_rom(args.rom)
    walked = time.perf_counter()
    cache_dir = encode_cache.default_cache_dir()
    with concurrent.futures.ThreadPoolExecutor(max_workers=ORACLE_WORKERS) as decoders:
        members, sections, plan = read_plan(rom, args.manifest, decoders)
        planned = time.perf_counter()
        record_path = os.path.join(args.out_dir, "emitted.json")
        os.makedirs(args.out_dir, exist_ok=True)
        record = json.load(open(record_path)) if os.path.exists(record_path) else {}
        written = record.get("sections", {}) if isinstance(record, dict) else {}
        stamps, store = load_store(args.payloads, members)
        record_store = None
        record_store_digest = None
        if plan["records"]:
            record_path_store = payload_store.path(args.records)
            record_store = load_record_store(record_path_store,
                                             record_payloads(rom, plan["all"]),
                                             exact=BLOCK.records_exact)
            record_store_digest = digest(open(record_path_store, "rb").read())
        generated = [section for section in sections
                     if section.kind == mapcontainer.CONTAINER]
        scratch = tempfile.mkdtemp(prefix="mapcontainer-")
        rows = []
        totals = {}
        skipped = 0
        record_store_same = (record_store_digest is None
                             or record.get("record_store_digest") == record_store_digest)
        manifest_path = (encode_cache.trusted_store(COMPRESS, cache_dir)
                         and record.get("payloads") == stamps
                         and record_store_same
                         and sections_match(sections, written))
        try:
            if manifest_path:
                loaded = emitted = time.perf_counter()
                skipped = len(sections)
                cache = {"spawns": 0, "hits": 0, "misses": 0, "trusted": 1,
                         "total": sum(len(plan["containers"][section.start])
                                      for section in generated)}
                print("manifest path: payload sizes and mtimes unchanged, encoder trusted,"
                      " every section file present")
            else:
                runners = payload_members(plan["containers"], store)
                loaded = time.perf_counter()
                compress, cache, cache_close = encode_cache.cached_compress(
                    compressor(COMPRESS, scratch), COMPRESS, cache_dir)
                members_of_run = [member for section in generated
                                  for member in runners[section.start]]
                blobs = dict(zip([member.offset for member in members_of_run],
                                 decoders.map(lambda member: compress(member.payload),
                                              members_of_run)))
                for section in sections:
                    if section.kind == mapcontainer.CONTAINER:
                        blob = b"".join(blobs[member.offset] for member in runners[section.start])
                        if len(blob) != section.end - section.start:
                            raise SystemExit("run %#x is %d bytes against its %d"
                                             % (section.start, len(blob),
                                                section.end - section.start))
                    elif section.start in plan["records"]:
                        blob = b"".join(record_store[offset]
                                        for offset, size, family in plan["records"][section.start])
                        if len(blob) != section.end - section.start:
                            raise SystemExit("record run %#x is %d bytes against its %d"
                                             % (section.start, len(blob),
                                                section.end - section.start))
                    elif section.kind in mapcontainer.RETAIL_KINDS:
                        blob = rom[section.start:section.end]
                    else:
                        raise SystemExit("section %#x..%#x has kind %r, which is neither a"
                                         " container run, a record run nor retail"
                                         % (section.start, section.end, section.kind))
                    path = os.path.join(ROOT, section_output(section))
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    if skip_unchanged(path, blob, written):
                        skipped += 1
                    else:
                        with open(path, "wb") as handle:
                            handle.write(blob)
                    written[path] = [len(blob), digest(blob)]
                cache_close()
                assert_encode_accounting(cache, len(members_of_run))
                emitted = time.perf_counter()
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        for section in sections:
            length = section.end - section.start
            totals[section.kind] = totals.get(section.kind, 0) + length
            rows.append({"kind": section.kind, "start": "0x%x" % section.start,
                         "end": "0x%x" % section.end, "bytes": length})
    for member in members:
        rows.append({"index": member.offset, "container_file_offset": "0x%x" % member.offset,
                     "declared_size": member.declared_size,
                     "stored_size": member.stored_size,
                     "payload_file": payload_name(member.offset),
                     "stored_sha256": digest(
                         rom[member.offset:member.offset + member.stored_size])})
    with open(record_path, "w", newline="\n", encoding="utf-8") as handle:
        emitted_record = {"sections": written, "payloads": stamps}
        if record_store_digest is not None:
            emitted_record["record_store_digest"] = record_store_digest
        json.dump(emitted_record, handle)
    with open(os.path.join(args.out_dir, "manifest.csv"), "w", newline="\n",
              encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, MANIFEST_FIELDS, restval="")
        writer.writeheader()
        writer.writerows(rows)
    lines = write_incbin(os.path.join(args.out_dir, "incbin.txt"), sections)
    if not {section.kind for section in sections} <= mapcontainer.section_kinds(plan["families"]):
        raise SystemExit("the plan holds a kind the emitter does not know: %s"
                         % sorted({section.kind for section in sections}
                                  - mapcontainer.section_kinds(plan["families"])))
    counts = {kind: sum(1 for section in sections if section.kind == kind)
              for kind in mapcontainer.section_kinds(plan["families"])}
    record_kinds = {family: counts[family] for family in plan["families"]}
    print("sections=%d generated=%d carve-out=%d retail=%d incbin_lines=%d"
          " containers=%d records=%d"
          % (len(sections), counts[mapcontainer.CONTAINER] + sum(record_kinds.values()),
             counts["carve-out"], counts["retail"], len(lines),
             counts[mapcontainer.CONTAINER], sum(record_kinds.values())))
    if sum(record_kinds.values()):
        print("record runs=%s" % record_kinds)
    print("oracle spawns=%d cache hits=%d misses=%d files rewritten=%d skipped=%d"
          % (cache["spawns"], cache["hits"], cache["misses"], len(sections) - skipped, skipped))
    print("encode_cache_misses=%d trusted=%d total=%d"
          % (cache["misses"], cache["trusted"], cache["total"]))
    print("phases: read %.2fs plan %.2fs payloads %.2fs encode+emit %.2fs total %.2fs"
          % (walked - started, planned - walked, loaded - planned, emitted - loaded,
             time.perf_counter() - started))
    generated_bytes = sum(length for kind, length in totals.items()
                          if kind not in mapcontainer.RETAIL_KINDS)
    print("generated bytes=%d carve-out bytes=%d retail bytes=%d total=%d"
          % (generated_bytes, totals.get("carve-out", 0), totals.get("retail", 0),
             sum(totals.values())))
    return 0


def cmd_verify(args):
    rom = read_rom(args.rom)
    members, sections, plan = read_plan(rom, args.manifest)
    _, store = load_store(args.payloads, members)
    if plan["records"]:
        payloads = record_payloads(rom, plan["all"])
        records = load_record_store(payload_store.path(args.records), payloads,
                                    exact=BLOCK.records_exact)
        for offset, family, size, blob in payloads:
            if records[offset] != blob or blob != rom[offset:offset + size]:
                print("VERIFY FAIL: the %s's %#x is not the record's own bytes" % (family, offset))
                return 1
        populations = {family: sum(1 for item in payloads if item[1] == family)
                       for family in plan["families"]}
        print("record basis: each record's fields parsed out of the image and packed back,"
              " compared with the store and with the image")
        print("components: " + " ".join("%s=%d" % (family, count)
                                        for family, count in populations.items()))
        print("records %d/%d byte-equal and retail" % (len(payloads), len(payloads)))
    scratch = tempfile.mkdtemp(prefix="mapcontainer-")
    equal = fitted = 0
    failures = []
    try:
        compress = compressor(COMPRESS, scratch)
        for member in members:
            blob = compress(store[member.offset])
            retail = rom[member.offset:member.offset + member.stored_size]
            same = blob == retail
            fits = len(blob) == member.stored_size
            if member.offset in BLOCK.carve_outs:
                if same or fits:
                    failures.append(member.offset)
                verdict = "DIFFER" if not same else "EQUAL"
            else:
                equal += same
                fitted += fits
                if not (same and fits):
                    failures.append(member.offset)
                verdict = "EQUAL" if same and fits else "DIFFER"
            print("container %#07x kind %d declared %4d stored %4d oracle %4d %s"
                  % (member.offset, member.kind, member.declared_size, member.stored_size,
                     len(blob), verdict))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("extent basis: marker-aware validate_retail_termination().packed_end")
    print("%d/%d byte-equal and fitted at the marker-aware extent; carve-out outside=%d"
          % (equal, len(members) - len(BLOCK.carve_outs),
             len(BLOCK.carve_outs) if not failures else 0))
    if (equal != len(members) - len(BLOCK.carve_outs)
            or fitted != len(members) - len(BLOCK.carve_outs)):
        print("VERIFY FAIL: %d containers do not reproduce: %s"
              % (len(failures), ["%#x" % offset for offset in failures[:8]]))
        return 1
    if BLOCK.carve_outs:
        print("the carve-out at %#x re-encodes differently at the same extent, so its retail bytes"
              " stay" % next(iter(BLOCK.carve_outs)))
    before, after = BLOCK.before_slice, BLOCK.after_slice
    source = args.source if os.path.isabs(args.source) else os.path.join(ROOT, args.source)
    rows, problems = emitted.source_rows(ROOT, rom, emitted.source_text(ROOT, source),
                                         (before[0], after[1]))
    if problems:
        print("VERIFY FAIL: %s" % problems[0])
        return 1
    at = next((index for index, row in enumerate(rows)
               if row[0] == sections[0].start), None)
    if at is None:
        print("VERIFY FAIL: no source row starts at the block's first section 0x%x"
              % sections[0].start)
        return 1
    found = [row for row in rows[at:] if row[0] < sections[-1].end]
    problems = emitted.tiling_problems(sections, found, section_output)
    if problems:
        print("VERIFY FAIL: the INCBIN tokens do not tile the planned sections")
        for problem in problems[:8]:
            print("  %s" % problem)
        print("  source tokens=%d planned=%d" % (len(found), len(sections)))
        return 1
    print("INCBIN tokens=%d tile 0x%x..0x%x exactly and carry the retail bytes"
          % (len(found), found[0][0], found[-1][1]))
    generated = [section for section in sections
                 if section.kind in (mapcontainer.CONTAINER,) + plan["families"]]
    print("ledger rows to append: %d" % len(generated))
    return 0


def cmd_ledger(args):
    rom = read_rom(args.rom)
    members, sections, plan = read_plan(rom, args.manifest)
    written = 0
    total = 0
    with open(args.ledger, "a", newline="\n", encoding="utf-8") as handle:
        for section in sections:
            if section.start in plan["containers"]:
                if args.provenance == "record":
                    continue
                length = sum(member.stored_size for member in plan["containers"][section.start])
                region = "%s_container_run_%x" % (BLOCK.name, section.start)
            elif section.start in plan["records"]:
                if args.provenance == "container":
                    continue
                length = sum(size for _, size, _ in plan["records"][section.start])
                names = "+".join(sorted({family for _, _, family
                                         in plan["records"][section.start]}))
                if BLOCK.ledger_region:
                    region = BLOCK.ledger_region % (section.start, names)
                else:
                    region = "%s_record_run_%x_%s" % (BLOCK.name, section.start, names)
            else:
                continue
            handle.write(gate.ledger_line((section.start, length, "data", region,
                                           "asm/rest_of_the_game.s", "generated", "byte-proven", 0)))
            written += 1
            total += length
    print("appended %d generated-run rows to %s for %d bytes" % (written, args.ledger, total))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("extract", "build", "verify", "ledger"):
        sub = commands.add_parser(name)
        sub.add_argument("--block", choices=sorted(BLOCKS), default="map")
        default_block = BLOCKS[next(action.default for action in sub._actions
                                    if action.dest == "block")]
        if name in ("extract", "build", "verify", "ledger"):
            sub.add_argument("--rom", required=True)
        if name in ("extract", "build", "verify"):
            sub.add_argument("--payloads", required=True)
        if name in ("extract", "build", "verify", "ledger"):
            sub.add_argument("--records", "--spriterecords", dest="records", default=None)
        if name in ("extract", "build", "verify", "ledger"):
            sub.add_argument("--manifest", required=name != "extract",
                             default=default_block.carve_manifest)
        if name == "build":
            sub.add_argument("--out-dir", required=True)
        if name == "verify":
            sub.add_argument("--source", required=True)
        if name == "ledger":
            sub.add_argument("--ledger", required=True)
            sub.add_argument("--provenance", choices=("any", "container", "record"), default="any")
        sub.set_defaults(run=globals()["cmd_" + name])
    args = parser.parse_args(argv)
    set_block(args.block)
    if args.records is None:
        args.records = BLOCK.records_store
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
