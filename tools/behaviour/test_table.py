from __future__ import annotations

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import testkit

import harness

OBJECT = 0x02000000
OUTPUT = 0x02000300
TABLE = 0x02000200
ENTRY = 0x02000200
SLOT = 0x02000400
POINTER = struct.pack("<I", SLOT)
CACHE = {}

ROWS = {
    0x0803E5AC: ({"0": OBJECT},
                 {OBJECT + 0x48: bytes([5, 0, 0, 2]), OBJECT + 0x10: b"\xf0"},
                 [(OBJECT + 0x48, 1, 3), (OBJECT + 0x12, 1, 3), (OBJECT + 0x10, 1, 0xF0)],
                 []),
    0x0803E5DA: ({"0": OBJECT},
                 {OBJECT + 0x48: bytes([0x3F, 0, 0, 2])},
                 [(OBJECT + 0x48, 1, 0x41), (OBJECT + 0x48, 1, 0x40),
                  (OBJECT + 0x4A, 1, 0), (OBJECT + 0x12, 1, 0x40),
                  (OBJECT + 0x10, 1, 0x10)], []),
    0x08004448: ({"0": OBJECT, "1": 0x12345678},
                 {OBJECT + 0xE4: struct.pack("<I", 2)},
                 [(OBJECT + 0xE4, 4, 3), (OBJECT + 0xF0, 4, 0x02345678)], []),
    0x08014124: ({"0": OBJECT}, {},
                 [(OBJECT + 0x04, 4, 0), (OBJECT + 0x00, 4, 0x0804A254),
                  (OBJECT + 0x08, 4, 0), (OBJECT + 0x0C, 4, 0),
                  (OBJECT + 0x14, 4, 0), (OBJECT + 0x18, 1, 0),
                  (OBJECT + 0x10, 4, 0), (OBJECT + 0x1C, 4, 0)], []),
    0x08015FFC: ({"0": OBJECT, "1": 0x11, "2": 0x22},
                 {OBJECT + 0x4C: struct.pack("<I", 1)},
                 [(OBJECT + 0x4C, 4, 2), (OBJECT + 0x5C, 4, 0x11),
                  (OBJECT + 0x60, 4, 0x22), (OBJECT + 0x64, 4, 0x0806E050),
                  (OBJECT + 0x110, 4, 0)], [0x0803FFE8]),
    0x0804F944: ({"0": OUTPUT, "1": OBJECT},
                 {OBJECT + 0x1A0: struct.pack("<II", 0x00012300, 0x000456FF)},
                 [(OUTPUT, 4, 0x123), (OUTPUT + 4, 4, 0x456)], []),
    0x08009220: ({"0": OBJECT}, {},
                 [(OBJECT, 4, 0), (OBJECT + 4, 4, 1), (OBJECT + 8, 4, 2),
                  (OBJECT + 0xC, 4, 3)], [0x08007A40] * 4),
    0x0800FA16: ({"0": OBJECT, "1": 2}, {},
                 [(OBJECT + 0x224, 4, 0x087112AC)], []),

    0x08050D30: ({0: OBJECT}, {OBJECT + 4: struct.pack("<I", SLOT), SLOT: struct.pack("<I", 0x02000600)},
         [
             (OBJECT + 0x0, 4, 0x8049ACC),
         ], [0x08046AA4]),

    0x0800A9D0: ({0: OBJECT}, {OBJECT + 0x30: struct.pack("<I", 1), OBJECT + 0x34: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x30, 4, 0x0),
         ], [0x08046AA2]),

    0x0801157E: ({0: OBJECT}, {OBJECT + 0x208: struct.pack("<I", 1), OBJECT + 0x20C: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x208, 4, 0x0),
         ], [0x0803DA62, 0x08046AA2]),

    0x08012628: ({0: OBJECT}, {OBJECT: struct.pack("<I", 1), OBJECT + 4: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x0, 4, 0x0),
             (OBJECT + 0xD0, 4, 0x1),
             (OBJECT + 0xC4, 4, 0x1),
             (OBJECT + 0xCC, 4, 0x0),
             (OBJECT + 0xC8, 4, 0x1),
         ], [0x08046AA4]),

    0x08011E94: ({0: OBJECT}, {OBJECT + 0x40C: struct.pack("<I", 1), OBJECT + 0x410: struct.pack("<I", ENTRY), ENTRY: POINTER},
         [
             (OBJECT + 0x4, 4, 0x1),
             (OBJECT + 0x8, 4, 0x2000200),
             (OBJECT + 0x40C, 4, 0x0),
         ], [0x08046AA2]),

    0x0801268A: ({0: OBJECT, 1: ENTRY}, {OBJECT: struct.pack("<I", 2), OBJECT + 4: struct.pack("<I", ENTRY), OBJECT + 8: struct.pack("<I", SLOT), ENTRY: POINTER},
         [
             (OBJECT + 0x0, 4, 0x1),
         ], [0x08049138, 0x08046AA4]),

    0x08013A90: ({0: OBJECT, 1: 0x5A}, {},
         [
             (OBJECT + 0xD, 1, 0x5A),
             (OBJECT + 0x2E, 1, 0x0),
             (OBJECT + 0x2F, 1, 0x0),
             (OBJECT + 0xC, 1, 0x1),
         ], []),

    0x08011200: ({0: OBJECT, 1: 0}, {},
         [
             (OBJECT + 0x69C, 1, 0x0),
             (OBJECT + 0x69D, 1, 0x0),
         ], []),

    0x0801137C: ({0: OBJECT, 1: 1}, {},
         [
             (OBJECT + 0x69E, 1, 0xFF),
             (OBJECT + 0x6A5, 1, 0xFF),
             (OBJECT + 0x6A4, 1, 0x0),
             (OBJECT + 0x69B, 1, 0x1),
             (OBJECT + 0x1, 1, 0x1),
         ], []),

    0x0804E490: ({0: OBJECT, 1: 0x02000600, 2: 0x20}, {0x02000600: bytes(range(0x20))},
         [
             (OBJECT + 0x0, 1, 0x1),
             (OBJECT + 0x2, 2, 0x1C4C),
         ], [0x0801124C, 0x08049138]),

    0x08011568: ({0: OBJECT}, {OBJECT + 0xC: struct.pack("<H", 3)},
         [
             (OBJECT + 0xC, 2, 0xFFFF),
         ], [0x0801142A]),

    0x08011818: ({0: OBJECT}, {OBJECT + 0xE: struct.pack("<H", 7)},
         [
             (OBJECT + 0xC, 2, 0x1C4C),
         ], [0x0801124C]),

    0x0800432C: ({0: OBJECT}, {},
         [
             (OBJECT + 0x4D0, 4, 0x0),
         ], []),

    0x08006880: ({0: OBJECT}, {},
         [
             (OBJECT + 0x4, 4, 0x0),
             (OBJECT + 0x0, 4, 0x804BF3C),
             (OBJECT + 0x8, 4, 0x0),
             (OBJECT + 0xC, 4, 0x0),
             (OBJECT + 0x10, 4, 0x0),
             (OBJECT + 0x14, 4, 0x0),
             (OBJECT + 0x1C, 4, 0x0),
             (OBJECT + 0x18, 4, 0xFFFFFFFE),
         ], []),

    0x080091B8: ({0: OBJECT}, {},
         [
             (OBJECT + 0x0, 4, 0x0),
             (OBJECT + 0x4, 4, 0x0),
             (OBJECT + 0x8, 4, 0x0),
             (OBJECT + 0xC, 4, 0x0),
             (OBJECT + 0x10, 4, 0x0),
         ], [0x08009A2A, 0x08011E0E, 0x080210F2]),

    0x0803362A: ({0: OBJECT}, {},
         [
             (OBJECT + 0x20, 4, 0x806E050),
             (OBJECT + 0x18, 4, 0x78),
             (OBJECT + 0x1C, 4, 0x10),
             (OBJECT + 0x15, 1, 0x8),
         ], [0x08046E40, 0x08049150]),

    0x08033664: ({0: OBJECT}, {},
         [
             (OBJECT + 0x20, 4, 0x806EE6C),
             (OBJECT + 0x18, 4, 0x78),
             (OBJECT + 0x1C, 4, 0x18),
             (OBJECT + 0x15, 1, 0x10),
         ], [0x08046E40, 0x08049150]),

    0x0803E8BC: ({0: OBJECT}, {},
         [
             (OBJECT + 0x51, 1, 0x0),
             (OBJECT + 0x30, 4, 0x0),
             (OBJECT + 0x10, 1, 0x2),
         ], []),

    0x08010D7C: ({0: OBJECT}, {},
         [
             (OBJECT + 0x1CC, 4, 0x0),
         ], [0x0800ECDA, 0x0800ED18]),

    0x08011874: ({0: OBJECT, 1: 1, 2: 2, 3: 3}, {},
         [
             (OBJECT + 0xC, 4, 0x1),
             (OBJECT + 0x10, 4, 0x2),
             (OBJECT + 0x14, 4, 0x3),
             (OBJECT + 0x0, 4, 0x804ABA0),
         ], [0x0804E490]),
    0x0800B2BE: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049F60),
        (0x0200000C, 4, 0x8049F90),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0801142A, 0x0801142A, 0x0803F58C, 0x0803D63C]),
    0x0800C7B6: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804CE00),
        (0x02000000, 4, 0x804E454),
    ], [0x0803D63C]),
    0x0800CE5A: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804E2FC),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x0800D9F0: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804A85C),
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x0800E6F8: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804D0F8),
    ], [0x0800E85E, 0x0803D63C]),
    0x0800E85E: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804C888),
    ], [0x08004102, 0x0800EC34, 0x0803D63C]),
    0x08013EEC: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049880),
        (0x02000000, 4, 0x804929C),
    ], [0x0803D63C, 0x0803D63C]),
    0x08016240: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049898),
        (0x02000000, 4, 0x804929C),
    ], [0x0803D63C, 0x0803D63C]),
    0x08016384: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804A298),
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0803D63C, 0x0801142A, 0x0803D63C]),
    0x08017C90: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804C92C),
    ], [0x08004102, 0x0800EC34, 0x0803D63C]),
    0x080185B8: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804C534),
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x080212FA: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804A33C),
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0803E302, 0x0801142A, 0x0803D63C]),
    0x08024768: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804BFCC),
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x08025EF0: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804A52C),
        (0x02000000, 4, 0x80491F0),
    ], [0x0803D63C]),
    0x08026DA8: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804E148),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x08028782: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x08028CCA: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x0802A3A8: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x080356B2: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x080370CC: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804AF24),
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0803E302, 0x0801142A, 0x0803D63C]),
    0x08037F8A: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x08038498: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x08038BB2: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x02000000, 4, 0x804E454),
    ], [0x0801142A, 0x0803D63C]),
    0x08039182: ({0: OBJECT, 1: 1}, {},
        [
        (0x02000000, 4, 0x804D514),
    ], [0x0800A9FE, 0x0800E6F8, 0x0803D63C]),
    0x0800B854: ({0: OBJECT}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x0200000E, 2, 0x500),
        (0x0200000C, 2, 0x1C4C),
        (0x02000000, 4, 0x8049FEC),
        (0x02000008, 1, 0x10),
        (0x02000004, 4, 0x0),
        (0x02000028, 4, 0x8),
        (0x02000014, 4, 0x0),
        (0x02000018, 4, 0x0),
        (0x0200002C, 4, 0x0),
        (0x02000010, 4, 0x0),
        (0x0200001C, 1, 0xFF),
    ], [0x0801124C]),
    0x0800C0C8: ({0: OBJECT}, {},
        [
        (0x02000000, 4, 0x8049680),
        (0x0200000E, 2, 0xF00),
        (0x0200000C, 2, 0x1C4C),
        (0x02000000, 4, 0x804D8C8),
        (0x02000010, 1, 0x0),
        (0x02000018, 4, 0x0),
        (0x02000014, 4, 0x0),
        (0x02000004, 4, 0x0),
        (0x02000008, 1, 0x11),
        (0x02000028, 4, 0x806E050),
        (0x02000020, 4, 0x78),
        (0x02000024, 4, 0xB),
        (0x0200001F, 1, 0x2),
        (0x0200001E, 1, 0x1),
        (0x0200003C, 4, 0x803F5A5),
        (0x0200001C, 1, 0x1),
    ], [0x0801124C, 0x0803F540]),
    0x08017160: ({0: OBJECT}, {},
        [
        (0x02000000, 4, 0x804920C),
        (0x02000004, 4, 0x0),
        (0x0200010C, 4, 0x0),
        (0x02000108, 4, 0x0),
        (0x02000110, 4, 0x0),
        (0x02000000, 4, 0x804B024),
        (0x02000120, 4, 0x0),
        (0x02000114, 4, 0x0),
        (0x0200011C, 4, 0x0),
        (0x02000118, 4, 0x0),
    ], []),
    0x08011DB4: ({0: OBJECT}, {},
        [
        (0x02000BFC, 4, 0x3003E5C),
        (0x02000BF8, 4, 0xE00),
        (0x02000610, 4, 0x0),
        (0x02000004, 4, 0x0),
        (0x0200040C, 4, 0x0),
    ], [0x08011C0C, 0x08011D36, 0x0803E44C, 0x0803D5B8, 0x08046DD0, 0x08011B04]),
    0x08050544: ({0: OBJECT}, {},
        [
        (0x02000000, 4, 0x8049EFC),
        (0x02000004, 4, 0x0),
        (0x02000008, 4, 0x0),
        (0x0200000C, 4, 0x0),
    ], []),
    0x0800C4DA: ({0: OBJECT}, {},
        [
        (0x02000004, 4, 0x0),
        (0x02000030, 4, 0x0),
        (0x0200002C, 4, 0x0),
    ], []),
    0x0800EEFE: ({0: OBJECT}, {},
        [
        (0x02000034, 4, 0x0),
        (0x02000030, 4, 0x0),
    ], []),
    0x080216E6: ({0: OBJECT}, {},
        [
        (0x0200002C, 4, 0x0),
        (0x02000030, 4, 0x0),
    ], []),
    0x0803B410: ({0: OBJECT}, {},
        [
        (0x02000008, 4, 0x0),
        (0x02000004, 4, 0x0),
    ], []),
    0x0802A8AA: ({0: OBJECT}, {},
        [
        (0x02000038, 4, 0x0),
        (0x02000038, 4, 0x0),
    ], []),
    0x0803E3E4: ({0: OBJECT}, {},
        [
        (0x02000010, 1, 0x0),
        (0x02000050, 1, 0x0),
        (0x02000090, 1, 0x0),
        (0x020000D0, 1, 0x0),
        (0x02000110, 1, 0x0),
        (0x02000150, 1, 0x0),
        (0x02000190, 1, 0x0),
        (0x020001D0, 1, 0x0),
        (0x02000210, 1, 0x0),
        (0x02000250, 1, 0x0),
        (0x02000290, 1, 0x0),
        (0x020002D0, 1, 0x0),
        (0x02000310, 1, 0x0),
        (0x02000350, 1, 0x0),
        (0x02000390, 1, 0x0),
        (0x020003D0, 1, 0x0),
    ], []),
    0x0803E42A: ({0: OBJECT}, {},
        [
        (0x02000034, 1, 0x0),
        (0x02000010, 1, 0x10),
        (0x02000074, 1, 0x0),
        (0x02000050, 1, 0x10),
        (0x020000B4, 1, 0x0),
        (0x02000090, 1, 0x10),
        (0x020000F4, 1, 0x0),
        (0x020000D0, 1, 0x10),
        (0x02000134, 1, 0x0),
        (0x02000110, 1, 0x10),
        (0x02000174, 1, 0x0),
        (0x02000150, 1, 0x10),
        (0x020001B4, 1, 0x0),
        (0x02000190, 1, 0x10),
        (0x020001F4, 1, 0x0),
        (0x020001D0, 1, 0x10),
        (0x02000234, 1, 0x0),
        (0x02000210, 1, 0x10),
        (0x02000274, 1, 0x0),
        (0x02000250, 1, 0x10),
        (0x020002B4, 1, 0x0),
        (0x02000290, 1, 0x10),
        (0x020002F4, 1, 0x0),
        (0x020002D0, 1, 0x10),
        (0x02000334, 1, 0x0),
        (0x02000310, 1, 0x10),
        (0x02000374, 1, 0x0),
        (0x02000350, 1, 0x10),
        (0x020003B4, 1, 0x0),
        (0x02000390, 1, 0x10),
        (0x020003F4, 1, 0x0),
        (0x020003D0, 1, 0x10),
    ], []),
    0x0803F0E6: ({0: OBJECT}, {},
        [
        (0x02000062, 1, 0x0),
        (0x02000077, 1, 0x0),
        (0x02000070, 1, 0x0),
        (0x02000028, 1, 0x0),
        (0x02000044, 4, 0x2000018),
        (0x020000C2, 1, 0x0),
        (0x020000D7, 1, 0x0),
        (0x020000D0, 1, 0x0),
        (0x02000088, 1, 0x0),
        (0x020000A4, 4, 0x2000078),
        (0x02000122, 1, 0x0),
        (0x02000137, 1, 0x0),
        (0x02000130, 1, 0x0),
        (0x020000E8, 1, 0x0),
        (0x02000104, 4, 0x20000D8),
        (0x02000182, 1, 0x0),
        (0x02000197, 1, 0x0),
        (0x02000190, 1, 0x0),
        (0x02000148, 1, 0x0),
        (0x02000164, 4, 0x2000138),
        (0x020001E2, 1, 0x0),
        (0x020001F7, 1, 0x0),
        (0x020001F0, 1, 0x0),
        (0x020001A8, 1, 0x0),
        (0x020001C4, 4, 0x2000198),
        (0x02000242, 1, 0x0),
        (0x02000257, 1, 0x0),
        (0x02000250, 1, 0x0),
        (0x02000208, 1, 0x0),
        (0x02000224, 4, 0x20001F8),
        (0x020002A2, 1, 0x0),
        (0x020002B7, 1, 0x0),
        (0x020002B0, 1, 0x0),
        (0x02000268, 1, 0x0),
        (0x02000284, 4, 0x2000258),
        (0x02000302, 1, 0x0),
        (0x02000317, 1, 0x0),
        (0x02000310, 1, 0x0),
        (0x020002C8, 1, 0x0),
        (0x020002E4, 4, 0x20002B8),
        (0x02000362, 1, 0x0),
        (0x02000377, 1, 0x0),
        (0x02000370, 1, 0x0),
        (0x02000328, 1, 0x0),
        (0x02000344, 4, 0x2000318),
        (0x020003C2, 1, 0x0),
        (0x020003D7, 1, 0x0),
        (0x020003D0, 1, 0x0),
        (0x02000388, 1, 0x0),
        (0x020003A4, 4, 0x2000378),
        (0x02000422, 1, 0x0),
        (0x02000437, 1, 0x0),
        (0x02000430, 1, 0x0),
        (0x020003E8, 1, 0x0),
        (0x02000404, 4, 0x20003D8),
        (0x02000482, 1, 0x0),
        (0x02000497, 1, 0x0),
        (0x02000490, 1, 0x0),
        (0x02000448, 1, 0x0),
        (0x02000464, 4, 0x2000438),
        (0x020004E2, 1, 0x0),
        (0x020004F7, 1, 0x0),
        (0x020004F0, 1, 0x0),
        (0x020004A8, 1, 0x0),
        (0x020004C4, 4, 0x2000498),
        (0x02000542, 1, 0x0),
        (0x02000557, 1, 0x0),
        (0x02000550, 1, 0x0),
        (0x02000508, 1, 0x0),
        (0x02000524, 4, 0x20004F8),
        (0x020005A2, 1, 0x0),
        (0x020005B7, 1, 0x0),
        (0x020005B0, 1, 0x0),
        (0x02000568, 1, 0x0),
        (0x02000584, 4, 0x2000558),
    ], []),
    0x0803F18C: ({0: OBJECT}, {},
        [
        (0x0200004C, 1, 0x0),
        (0x02000028, 1, 0x10),
        (0x020000AC, 1, 0x0),
        (0x02000088, 1, 0x10),
        (0x0200010C, 1, 0x0),
        (0x020000E8, 1, 0x10),
        (0x0200016C, 1, 0x0),
        (0x02000148, 1, 0x10),
        (0x020001CC, 1, 0x0),
        (0x020001A8, 1, 0x10),
        (0x0200022C, 1, 0x0),
        (0x02000208, 1, 0x10),
        (0x0200028C, 1, 0x0),
        (0x02000268, 1, 0x10),
        (0x020002EC, 1, 0x0),
        (0x020002C8, 1, 0x10),
        (0x0200034C, 1, 0x0),
        (0x02000328, 1, 0x10),
        (0x020003AC, 1, 0x0),
        (0x02000388, 1, 0x10),
        (0x0200040C, 1, 0x0),
        (0x020003E8, 1, 0x10),
        (0x0200046C, 1, 0x0),
        (0x02000448, 1, 0x10),
        (0x020004CC, 1, 0x0),
        (0x020004A8, 1, 0x10),
        (0x0200052C, 1, 0x0),
        (0x02000508, 1, 0x10),
        (0x0200058C, 1, 0x0),
        (0x02000568, 1, 0x10),
    ], []),
}


def image():
    if "rom" not in CACHE:
        CACHE["rom"] = testkit.rom_bytes(os.path.join(harness.ROOT, "baserom.gba"),
                                         digest=harness.ROM_SHA256, size=0x800000)
    return CACHE["rom"]


def result(address):
    registers, memory, _writes, _calls = ROWS[address]
    retail = image()
    if ("body", address) not in CACHE:
        CACHE[("body", address)] = harness.body(retail, address)
    found = harness.run(retail, address, CACHE[("body", address)],
                        {int(key): value for key, value in registers.items()}, memory)
    writes = [item for item in found.writes if 0x02000000 <= item[0] <= 0x0203FFFF]
    return writes, [target for _site, target in found.calls]


def test_object_advance_timer1_subtracts_the_delta_and_sets_the_timer_flag():
    assert result(0x0803E5AC) == ROWS[0x0803E5AC][2:]


def test_object_advance_timer2_adds_the_delta_and_clamps_it_at_0x40():
    assert result(0x0803E5DA) == ROWS[0x0803E5DA][2:]


def test_object_append_entry1_counts_the_entries_and_masks_the_value_to_28_bits():
    assert result(0x08004448) == ROWS[0x08004448][2:]


def test_object_construct1_stores_the_table_word_and_the_arguments_at_fixed_offsets():
    assert result(0x08014124) == ROWS[0x08014124][2:]


def test_object_append_record1_appends_a_12_byte_record_and_clears_the_flag():
    assert result(0x08015FFC) == ROWS[0x08015FFC][2:]


def test_object_read_position1_shifts_the_two_fixed_point_words_right_by_eight():
    assert result(0x0804F944) == ROWS[0x0804F944][2:]


def test_object_rebuild_slots1_replaces_each_of_the_four_slots_with_a_new_handle():
    assert result(0x08009220) == ROWS[0x08009220][2:]


def test_object_write_table_pointer1_stores_the_table_entry_the_index_names():
    assert result(0x0800FA16) == ROWS[0x0800FA16][2:]

def test_object_install_handler_table1_stores_the_handler_table_word_at_0_and_reaches_the_handler_the_object_at_4_names():
    assert result(0x08050D30) == ROWS[0x08050D30][2:]

def test_list_release_all1_walks_the_count_at_0x30_and_clears_it():
    assert result(0x0800A9D0) == ROWS[0x0800A9D0][2:]

def test_list_release_all2_walks_the_count_at_0x208_and_clears_it():
    assert result(0x0801157E) == ROWS[0x0801157E][2:]

def test_list_release_all3_clears_the_count_and_arms_the_block_at_0xc0():
    assert result(0x08012628) == ROWS[0x08012628][2:]

def test_list_pop_all1_moves_the_entries_into_the_array_at_4_and_clears_the_count():
    assert result(0x08011E94) == ROWS[0x08011E94][2:]

def test_list_remove1_removes_the_entry_the_argument_names_and_shifts_the_rest():
    assert result(0x0801268A) == ROWS[0x0801268A][2:]

def test_list_append_byte1_writes_the_byte_after_the_count_and_clears_the_tail_slots():
    assert result(0x08013A90) == ROWS[0x08013A90][2:]

def test_table_unlink1_unlinks_the_record_from_its_two_neighbours():
    assert result(0x08011200) == ROWS[0x08011200][2:]

def test_table_init_link1_writes_the_two_link_bytes_and_advances_the_owner():
    assert result(0x0801137C) == ROWS[0x0801137C][2:]

def test_gfx_begin_tile_load1_increments_the_byte_and_stores_the_tile_index():
    assert result(0x0804E490) == ROWS[0x0804E490][2:]

def test_handle_release1_unregisters_the_handle_and_stores_0xffff():
    assert result(0x08011568) == ROWS[0x08011568][2:]

def test_handle_acquire1_looks_the_id_up_and_stores_the_handle():
    assert result(0x08011818) == ROWS[0x08011818][2:]

def test_object_subtract_delta1_subtracts_the_global_word_from_the_counter():
    assert result(0x0800432C) == ROWS[0x0800432C][2:]

def test_object_construct2_stores_the_table_word_and_the_stack_arguments():
    assert result(0x08006880) == ROWS[0x08006880][2:]

def test_state_copy_block1_copies_the_five_default_words_and_calls_three_resetters():
    assert result(0x080091B8) == ROWS[0x080091B8][2:]

def test_gfx_init_block1_stores_the_budget_the_count_and_the_copied_block():
    assert result(0x0803362A) == ROWS[0x0803362A][2:]

def test_gfx_init_block2_stores_the_second_budget_the_count_and_the_copied_block():
    assert result(0x08033664) == ROWS[0x08033664][2:]

def test_math_scale_by_table1_scales_the_field_by_the_two_tables_and_sets_the_bit():
    assert result(0x0803E8BC) == ROWS[0x0803E8BC][2:]

def test_table_clear_slot1_clears_the_slot_word_and_calls_the_two_record_helpers():
    assert result(0x08010D7C) == ROWS[0x08010D7C][2:]

def test_object_construct3_stores_the_table_word_and_the_three_arguments():
    assert result(0x08011874) == ROWS[0x08011874][2:]

def test_object_destroy1_stores_the_three_tables_and_frees_the_object():
    assert result(0x0800B2BE) == ROWS[0x0800B2BE][2:]

def test_object_destroy2_stores_the_two_tables_and_frees_the_object():
    assert result(0x0800C7B6) == ROWS[0x0800C7B6][2:]

def test_object_destroy3_stores_the_two_tables_relinks_and_frees_the_object():
    assert result(0x0800CE5A) == ROWS[0x0800CE5A][2:]

def test_object_destroy4_stores_the_three_tables_and_frees_the_object():
    assert result(0x0800D9F0) == ROWS[0x0800D9F0][2:]

def test_object_destroy5_stores_the_table_and_frees_through_the_other_destructor():
    assert result(0x0800E6F8) == ROWS[0x0800E6F8][2:]

def test_object_destroy6_stores_the_table_and_frees_the_object():
    assert result(0x0800E85E) == ROWS[0x0800E85E][2:]

def test_object_destroy7_stores_the_two_tables_and_frees_the_field_and_the_object():
    assert result(0x08013EEC) == ROWS[0x08013EEC][2:]

def test_object_destroy8_stores_the_two_tables_and_frees_the_field_and_the_object():
    assert result(0x08016240) == ROWS[0x08016240][2:]

def test_object_destroy9_stores_the_three_tables_and_frees_the_field_and_the_object():
    assert result(0x08016384) == ROWS[0x08016384][2:]

def test_object_destroy10_stores_the_table_and_frees_the_object():
    assert result(0x08017C90) == ROWS[0x08017C90][2:]

def test_object_destroy11_stores_the_three_tables_and_frees_the_object():
    assert result(0x080185B8) == ROWS[0x080185B8][2:]

def test_object_destroy13_stores_the_three_tables_and_frees_the_object():
    assert result(0x080212FA) == ROWS[0x080212FA][2:]

def test_object_destroy14_stores_the_three_tables_and_frees_the_object():
    assert result(0x08024768) == ROWS[0x08024768][2:]

def test_object_destroy15_stores_the_two_tables_and_frees_the_object():
    assert result(0x08025EF0) == ROWS[0x08025EF0][2:]

def test_object_destroy16_stores_the_two_tables_and_frees_the_object():
    assert result(0x08026DA8) == ROWS[0x08026DA8][2:]

def test_object_destroy17_stores_the_two_tables_and_frees_the_object():
    assert result(0x08028782) == ROWS[0x08028782][2:]

def test_object_destroy18_stores_the_two_tables_and_frees_the_object():
    assert result(0x08028CCA) == ROWS[0x08028CCA][2:]

def test_object_destroy19_stores_the_two_tables_and_frees_the_object():
    assert result(0x0802A3A8) == ROWS[0x0802A3A8][2:]

def test_object_destroy20_stores_the_two_tables_and_frees_the_object():
    assert result(0x080356B2) == ROWS[0x080356B2][2:]

def test_object_destroy21_stores_the_three_tables_and_frees_the_object():
    assert result(0x080370CC) == ROWS[0x080370CC][2:]

def test_object_destroy22_stores_the_two_tables_and_frees_the_object():
    assert result(0x08037F8A) == ROWS[0x08037F8A][2:]

def test_object_destroy23_stores_the_two_tables_and_frees_the_object():
    assert result(0x08038498) == ROWS[0x08038498][2:]

def test_object_destroy24_stores_the_two_tables_and_frees_the_object():
    assert result(0x08038BB2) == ROWS[0x08038BB2][2:]

def test_object_destroy25_stores_the_table_and_frees_the_object():
    assert result(0x08039182) == ROWS[0x08039182][2:]

def test_object_construct4_stores_the_two_tables_and_initialises_the_fields():
    assert result(0x0800B854) == ROWS[0x0800B854][2:]

def test_object_construct5_stores_the_two_tables_and_initialises_the_fields():
    assert result(0x0800C0C8) == ROWS[0x0800C0C8][2:]

def test_object_construct6_stores_the_two_tables_and_initialises_the_fields():
    assert result(0x08017160) == ROWS[0x08017160][2:]

def test_object_construct8_stores_the_two_tables_and_clears_the_three_fields():
    assert result(0x08011DB4) == ROWS[0x08011DB4][2:]

def test_object_create1_stores_the_table_and_the_argument_and_clears_the_two_fields():
    assert result(0x08050544) == ROWS[0x08050544][2:]

def test_object_clear_fields1_clears_the_three_words():
    assert result(0x0800C4DA) == ROWS[0x0800C4DA][2:]

def test_object_clear_fields2_clears_the_two_words():
    assert result(0x0800EEFE) == ROWS[0x0800EEFE][2:]

def test_object_clear_fields3_clears_the_two_words():
    assert result(0x080216E6) == ROWS[0x080216E6][2:]

def test_object_clear_fields4_clears_the_two_words():
    assert result(0x0803B410) == ROWS[0x0803B410][2:]

def test_object_clear_fields5_clears_the_word_twice():
    assert result(0x0802A8AA) == ROWS[0x0802A8AA][2:]

def test_object_clear_stride_field1_clears_the_byte_at_0x10_of_sixteen_records():
    assert result(0x0803E3E4) == ROWS[0x0803E3E4][2:]

def test_object_set_stride_fields1_sets_the_byte_at_0x34_and_ors_0x10_into_the_byte_at_0x10_of_sixteen_records():
    assert result(0x0803E42A) == ROWS[0x0803E42A][2:]

def test_object_init_stride_links1_clears_the_fields_and_points_each_record_at_its_own_block_of_fifteen_records():
    assert result(0x0803F0E6) == ROWS[0x0803F0E6][2:]

def test_object_set_stride_field1_sets_the_byte_at_0x28_and_clears_the_byte_at_0x4c_of_fifteen_records():
    assert result(0x0803F18C) == ROWS[0x0803F18C][2:]

