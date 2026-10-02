# TOOLKIT-011 - Canonical free-space audit

## Result: BLOCKED, no promotion

The audited evidence does **not** establish a production-allocatable canonical
Buu region. This is not a claim that no free space exists. No profile declaration,
allocator policy, graphics writer or capability was changed. The ticket's explicit
stop-on-insufficient-evidence branch applies; the relocation milestone is unmet.

Canonical identity: `buus_fury_usa_rev0_01c1707f`, 8,388,608 bytes,
SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
Baseline: `8ee5d7d1107bb2ac974974b187eff4498b3a1184`.

## Existing evidence audited before probing

Local: TOOLKIT-003 implementation/review and `docs/relocation.md`; TOOLKIT-010
closure and `GRAPHICS_FORMAT.md`; `profile.py`, packaged and compatibility ROM
profiles, `layout.py`, `document.py`, `allocation.py`, `relocation.py`; semantic
graphics, map, text and placement-type reference publishers; `AUTO_RE_<local-state-name>`,
all three PROJECT_STATE files, `consumer-analysis.md`; existing analysis scripts
and text free-space notes. No existing complete occupancy proof was found.

| Pinned upstream | Evidence inspected | Result |
|---|---|---|
| 2genkidev/buusfury `cc53d0cd2d1c167e749419187e2d92017ac07468` | `README.md:3-6`, `build.bat:28-42`, `scatter.ld:15-44`, `asm/buu.s:8-81`, `asm/rest_of_the_game.s:3-15` | Exact canonical SHA-1; one bounded tail candidate, still emitted by INCBIN |
| spicybung/DragonByteZ `b2691209` | `src/rom.cpp:76-92`, `:185-200`, `src/sprite_analysis.cpp:30-31` and graphics research | Graphics reader; no independent full-hash free-space/layout proof |
| Arefu/Legacy `d22a556c` | `README.md:3-5`, `:25-37`, repository inventory | No applicable canonical Buu section accounting |
| BuusFuryToolkit `4353f6a2` | `README.md:3-18`, `:51-62`, repository inventory | Size-constrained dialogue editing; no free-space declaration |
| Buu recomp `453a913a9f67916b9b358776da1c1229b09a6c80` | `baserom.md:7-14`, `game.toml:10-21`, `generated/README.md:3-4` | Different SHA-1 `e657...` / SHA-256 `15df...`; addresses cannot transfer; generated source absent |

Paths in this table are relative to the corresponding ignored `extern/` clone.
No upstream clone or commercial asset is added to Git. This is a binary-layout
question, not a new player-visible behavior investigation.

## Candidate and promotion decision

| Property | Observation |
|---|---|
| File extent (exclusive end) | `[0x007B89A8, 0x00800000)` |
| ROM-address extent | `[0x087B89A8, 0x08800000)` |
| Size | `0x47658` = **292,440 bytes** |
| Boundary alignment | Both boundaries divisible by 8; no allocator alignment declaration made |
| Upstream neighbor | Opaque game INCBIN `[0x003C33F8, 0x007B89A8)` |
| Following neighbor | End of canonical image |
| Byte pattern | **CONFIRMED numeric observation:** entirely `FF` |
| All-byte u32 candidate observations | **516**, of which **99** have word-aligned sources |
| Distinct numerical target offsets | **475** |
| Promotion | **REJECTED / remains CANDIDATE** |

The upstream separates this tail with a `null bytes` comment
(`extern/buusfury/build.bat:40-42`), but the placeholder assembly includes it
verbatim (`extern/buusfury/asm/rest_of_the_game.s:3-15`), and the linker places
that placeholder in `EVERYTHING_ELSE` (`extern/buusfury/scatter.ld:40-42`).
This does not prove that the tail lies outside used sections.

Examples retained as **CANDIDATE**, not live-reference claims:

| Source file offset | Raw target ROM address | Target file offset |
|---|---|---|
| `0x00073E34` | `0x087C8704` | `0x007C8704` |
| `0x0023D70C` | `0x087BA08C` | `0x007BA08C` |
| `0x006002D6` (unaligned) | `0x087B8E2C` | `0x007B8E2C` |

No match was discarded based on an assumed compressed-data or instruction role.
Resolving all these would require separate source/consumer evidence. The current
graph's absence of a known target cannot settle unknown computed references,
unknown compressed extents or signature/checksum use.

No smaller prefix was promoted. An endpoint chosen immediately before the first
numeric hit has no independent upstream section/ownership boundary. Zero hits in
such a prefix would still be only a scan result. Internal graphics gaps were not
scanned: the existing packed-extent measurements are not evidence that gaps are
allocator-owned; broad opaque INCBIN intervals likewise remain UNKNOWN.

**OLD CLAIM:** the upstream's wording might mean a zero-filled unused tail.
**NEW EVIDENCE:** canonical bytes are FF, the tail is INCBINed, and numeric
candidate targets exist throughout the extent.
**RESOLUTION:** record the literal byte observation and upstream wording
separately; neither establishes allocatability. No earlier VERIFIED claim is made.

## Reproducible occupancy and reference method

`tools/research/free_space_audit.py` is a standalone research entry point. It
verifies the exact profile before profile-specific access and writes only JSON
metadata to stdout. It does not emit a ROM, free-region declaration or promotion.

```powershell
.venv/Scripts/python.exe -m tools.research.free_space_audit "roms/Dragon Ball Z - Buu's Fury (U).gba" > build/toolkit011/occupancy.json
```

The occupancy view is a disjoint partition of the full image with overlapping
annotations retained: confirmed graphics containers (their complete measured
compressed extents), object palette, character table/entry anchors, placement
graph anchors, declared stat/map/text tables and text pool, typed/opaque map-slot
extents, declared header/startup, candidate tail, and UNKNOWN elsewhere. One-byte
entry anchors retain their original limited meaning; they are not full structure
extents. An annotation is not automatically complete semantic ownership.

References are taken from the existing graphics and placement-type documents,
the verified text table and typed map-slot publisher. The report checks known
targets against the candidate and separately scans **every byte position** for
absolute little-endian u32 values inside it. Raw addresses use existing address
helpers without Thumb masking or normalization. Numeric observations remain
separate from the production graph: overlapping byte windows cannot all be
authoritative source fields. The report neither claims complete pointer discovery
nor resolves candidate semantics.

`occupancy.json` records every candidate source/target, current known inbound
counts, overlapping annotations, nearest known neighbors and limitations. The
broader upstream INCBIN before the tail is its physical upstream neighbor, not a
decoded asset-owner claim. Unknown containers and indirect uses remain UNKNOWN.

Measured report: **16,977** known reference records (11,254 graphics, 4,100
placement types, 1,534 text, 89 typed map-slot targets), **zero** known inbound
targets and **zero** known owned overlaps in the candidate. All **516** numeric
observations remain candidates. The occupancy contains **9,598 annotations** and
**13,681 disjoint segments**; **5,199,061 bytes** have no known annotation and
remain UNKNOWN. The candidate's own 292,440 bytes have a CANDIDATE annotation,
not verified ownership. These counts show why this is not complete accounting.

## Allocation and relocation outcome

Verified capacity **0 bytes**; allocations **0**; used **0**; remaining verified
capacity **0**; alignment loss **0**. Candidate bytes are not available capacity.
No target selected, no pixel edit or new encoded size, no allocated address,
no reference rewrites, no build output or modified-ROM diff. Every old payload
region remains unchanged. Repeated modified-build and emulator/static visual
relocation proofs are **NOT PERFORMED** because the prerequisite failed.

Existing no-op and synthetic relocation regressions are validation of preserved
behavior, not canonical relocation evidence. The allocator remains profile-only
(`tools/webfoot/allocation.py:44-82`), unresolved candidates still block movement
(`tools/webfoot/relocation.py:64-70`), and the profile parser still requires
`status: CONFIRMED` (`tools/webfoot/profile.py:540-557`). That schema spelling is
the existing implementation of a reviewed free declaration, not permission for
research code to promote candidates.

| Capability | Result |
|---|---|
| Free-space discovery | Bounded CANDIDATE report only |
| Verified free declaration | None established |
| Allocator | Existing deterministic synthetic capability preserved |
| Graphics pixel edit | Existing EDIT unchanged |
| Graphics pixel write in-place | Existing capacity-constrained path unchanged; no new proof |
| Graphics pixel write via relocation | BLOCKED |
| Reference rewrite | Existing synthetic capability; no canonical rewrite |
| Runtime validation | NOT PERFORMED |

## Review, validation and next evidence

Independent upstream review rejected whole-tail promotion and unsupported prefix
carving. The exact tests and the review findings are recorded in this repository;
changing suite totals belongs in PROJECT_STATE.

Next evidence needed: independently resolve candidate source uses and unknown
extent/ownership coverage, or supply another independently bounded free-region
proof matching this exact canonical hash. There is no permission to weaken
candidate policy, expand the ROM or start TOOLKIT-012.
