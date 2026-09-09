# TOOLKIT-029 - Runtime proof of an authored placement

Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(`Dragon Ball Z - Buu's Fury (U).gba`, 8,388,608 bytes). Read-only throughout;
verified unchanged before and after the runtime session. Baseline `9b6996b`.

**RUNTIME-PROVEN AUTHOR_NEW: YES.**

A map entity that does not exist in the original game was created by the Webfoot
SDK, built into a canonical-derived Buu's Fury ROM, loaded by the original
engine, and **observed in the running game by the project owner**.

## Result chain

```text
SDK-authored placement    map:0040/authored:tk029 (clone of map:0040/placement:0001)
-> canonical-derived ROM  a425ae73... , 56 bytes changed, canonical untouched
-> boot in mGBA 0.10.5    pinned build, FileVersion 0.10.5.0
-> load target map        savestate loads directly into map 40
-> engine reads array     live MapEntry+0x04 = 5, MapEntry+0x14 = 0x087EA420
-> new slot resolves      slot 4 -> 0x087EA400, the authored body
-> entity instantiated    OWNER-OBSERVED: the clone is visible in the map
```

## Target selection - why map 40 and not map 10

TOOLKIT-028 materialized its authored placement into **map 10**. Map 10 could not
be reached in this session, so the ticket's allowance for choosing an observable
target was used, and the same authored case was rebuilt into **map 40**.

The map resolver at `0x080089FC` was disassembled rather than assumed:

```
0x08008A0E  780B  ldrb r3,[r1,#0]   ; entry+0x00
0x08008A10  42A3  cmp  r3,r4
0x08008A12  D104  bne  next
0x08008A14  784B  ldrb r3,[r1,#1]   ; entry+0x01
0x08008A16  42AB  cmp  r3,r5
0x08008A18  D101  bne  next
0x08008A1A  1C08  mov  r0,r1        ; MATCH: return this MapEntry
0x08008A1E  3138  add  r1,#0x38     ; else next 0x38-byte record
```

The lookup key is the 2-tuple `(entry+0x00, entry+0x01)`, first match wins.
Measured across all 452 entries those tuples are **unique** (452 distinct keys,
zero duplicates), so the pair is a genuine map ID. `entry+0x02` and `entry+0x03`
are not read by the resolver at all.

| Map | Key | Count | Reachable in session |
|---|---|---|---|
| 10 | `(0x00, 0x0C)` | 2 | no |
| 40 | `(0x01, 0x0C)` | 4 | **yes - the savestate loads into it** |

Map 40 is also the better acceptance case on the merits: it holds two genuine
placement records (slots 1 and 3, both type 86) at (176,208) and (192,224), so
its coordinate range is known-good, and the clone source is a record that already
lives and renders in that room.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - `output_raw`

**OLD CLAIM.** `MAP_FORMAT.md:158` records `output_raw` (`+0x00`) as UNKNOWN
semantics. An in-session correlation suggested it was a variation-slot index
within a zone, because zone `0x0C` members ordered 10 -> 00, 40 -> 01, 56 -> 02.

**NEW EVIDENCE.** The resolver reads `+0x00` and `+0x01` as a two-byte lookup
key, and those pairs are unique across the whole table.

**RESOLUTION.** `+0x00` is the first byte of the map's resolver key, not an
ordinal. The ordering correlation is a consequence of table layout and is not
used as evidence anywhere here.

## The authored placement

Produced through the supported production path only - `clone_placement` ->
`validate_project` -> `build_project`, against the profile-declared free region
from TOOLKIT-028. No map-40 special case exists anywhere in the SDK.

| Property | Value |
|---|---|
| Identity | `map:0040/authored:tk029` |
| Provenance | `AUTHORED_CLONE` of `map:0040/placement:0001` |
| Authored position | (176, 176) |
| Body address | `0x087EA400` (file `0x7EA400`), 32 bytes |
| Expanded array | `0x087EA420` (file `0x7EA420`), 20 bytes, 5 slots |
| Output SHA-256 | `a425ae73af5c5b4029882e8fb62ca398ee0e3b8a9a4fbb63dee8dc9834d7bed4` |
| Bytes changed | **56** of 8,388,608 |

Changed runs, all intended:

| Offset | Size | Before | After |
|---|---|---|---|
| `0x08EBA4` | 1 | `04` | `05` (MapEntry+0x04 count) |
| `0x08EBB4` | 3 | `905607` | `20a47e` (MapEntry+0x14 owner pointer) |
| `0x7EA400` | 52 | `FF`... | body (32) + expanded array (20) |

The authored body is a faithful clone of its source - same factory `0x0800FD55`,
same `flags_raw` `0x00010007`, same type 86, same descriptor `0x080555A0`, same
child pointer - differing only in the position halfwords. That is what makes a
visible difference attributable to the authoring rather than to a mismatched
template.

## Runtime

| Item | Value |
|---|---|
| Emulator | pinned mGBA 0.10.5, SHA-256 `5A3C98C2...F247`, FileVersion `0.10.5.0` |
| ROM | `build/toolkit029/buu-authored-map40-176-176.gba` (modified) |
| State | working copy of `roms/...ss1`; source hash `2D5740A8...1AAB` unchanged |
| Observer | `tools/runtime/toolkit029_placement_watch.lua`, read-only, Lua-only |

### OBSERVED - engine consumption of the authored structure

Read live from the running game through `0x03001980`, the runtime MapEntry
pointer established by ROM-007:

```text
LIVE map=40 key=(01,0C) cnt=5 arr=087EA420
```

The engine is reading **count 5** and the **relocated array in free space**, not
the canonical count 4 at `0x08075690`. Recorded continuously across ~2,900 frames
in `toolkit029-watch.csv`; the value is stable, not a transient.

Per TOOLKIT-024's disassembly of the map loader at `0x08008C9E..0x08008CD6`, the
outer traversal is a counted loop bounded by `MapEntry+0x04` and indexed into
`MapEntry+0x14` by `index*4`. A count of 5 over that array is therefore exactly
the condition under which slot 4 - the authored body - is dereferenced and passed
to its factory.

### OBSERVED - the entity itself

**The project owner observed the clone in the running game.** This is the
ticket's preferred evidence class: a visible, human-observable result, on the
modified image, in ordinary gameplay.

Supporting artifact: `run-20260909-025705/map40-authored.png` shows the map with
three placement figures present where canonical map 40 declares two placement
records. The savestate of that exact moment is preserved alongside it as
`map40-authored.ss1`.

## What is NOT claimed

* **The automated EWRAM instantiation scan is INVALID / NON-DISCRIMINATING.**
  It returned zero references to the authored record body - but it also returned
  zero for its canonical positive control, so it cannot distinguish "absent" from
  "this instrument sees nothing at all". Its empty result is therefore **not**
  negative evidence, and must not be reinterpreted as such by any later reader.
  The probe labels those rows `CONTROL-ABSENT-scan-uninformative`, and that guard
  is what prevented a false negative from being read as a refutation.

  Preserved for possible future work, **not** an open item on this ticket (owner
  ruling 2026-09-09: TOOLKIT-029 is not held open to repair this instrument):

  * **Defect 1, fixed.** The probe read a fixed array slot 2 rather than the
    authored last slot (`count - 1`), so on map 40 its decoded body columns
    described an untouched canonical sibling (`factory 0x080111A9`) rather than
    the authored record.
  * **Defect 2, undiagnosed.** Why the scan finds neither the authored body nor
    the canonical control is unknown. The scan assumes a constructed placement
    retains a word-aligned pointer to its source record somewhere in EWRAM
    `[0x02000000, 0x02040000)`. That assumption is itself unverified, and a
    failing positive control is exactly what an unsound assumption would look
    like, so it is the first thing a future attempt should test.
* No claim is made about the authored entity's *behavior* - collision, dialogue,
  scripts, or interaction. Only that the engine loaded and instantiated it.
* The `id_raw` of the clone (211) duplicates canonical slot 3's id, inherited
  from the clone source. No engine consequence was observed, and none is claimed
  either way.

## Safety

| Check | Result |
|---|---|
| Canonical ROM SHA-256 before/after | `940ad5f0...f059e`, **unchanged** |
| Canonical savestate SHA-256 | `2D5740A8...1AAB`, unchanged |
| Runtime inputs | working copies only, under ignored `build/` |
| Generated ROM tracked | no - `build/` is ignored |

## Validation

`tests/unit/test_mgba_capture.py`: **59 passed, 0 failed**, including four new
regressions pinning that the probe is read-only, is allowlisted, keeps structure
and instantiation evidence in separate channels, and scans a canonical control.

Three pre-existing tests error under the default pytest temp directory with
`PermissionError: [WinError 5]` - the known Windows sandbox restriction recorded
in VERTICAL-002, not a test failure. With a writable `--basetemp` outside the
repository, the full file passes 59/59.

No production SDK code was changed by this ticket. The only tracked changes are
the new runtime observer, its allowlist entry, its tests, and this document.
