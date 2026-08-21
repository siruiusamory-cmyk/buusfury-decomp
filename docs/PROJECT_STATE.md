# LOG1 Remake - Verified Project State

This file records current verified facts. Permanent rules live in
[`../DEVELOPMENT.md`](../DEVELOPMENT.md). Detailed evidence and provenance live in
[`reverse-engineering.md`](reverse-engineering.md) and
[`consumer-analysis.md`](consumer-analysis.md).

## Current Baseline

- ROM-009 baseline: `5b39389e5b9a663e2465ee454f27da9a55c787fd`
  (`feat: prepare clean-state spatial callback tracing`).
- Latest completed research ticket: ROM-009.
- ROM-009 research is committed in the baseline above.
- ROM-008 portable baseline: **192 passed, 0 failed, 0 skipped**.
- Current portable suite after workflow migration: **199 passed, 0 failed, 0 skipped**.
- Current portable suite after ROM-009: **208 passed, 0 failed, 0 skipped**.
- Persistent the tool workflow migration is installed.
- `docs/PROJECT_<local-state-name>` is ROM-010; archived ROM-009 is committed.

## Verified ROM

Canonical local profile:

| Property | Value |
|---|---|
| Profile ID | `buus_fury_usa_rev0_01c1707f` |
| Size | 8,388,608 bytes |
| CRC32 | `01C1707F` |
| MD5 | `3a74fce97f1ea2b28c2a50ec3df0acee` |
| SHA-1 | `f1c4b07554d2a3b1ad2f325307051e775ce68087` |
| SHA-256 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| GBA title | `DBZBUUSFURY` |
| Game code | `BG3E` |
| Maker | `70` |
| Revision | `0` |
| Header checksum | `0x84`, valid |
| Status | `VERIFIED` |

The separate Buu's Fury recomp image with SHA-1 beginning `e65738e9` is a
different profile. Its offsets are not transferable without independent
validation.

## Established MapEntry Format

For the trusted profile:

- GBA table address: `0x0808E2E0`.
- File offset: `0x0008E2E0`.
- Record size and stride: `0x38`.
- Record count: 452.
- Exclusive end: `0x000945C0`.
- Iteration is fixed-count, with no sentinel.
- All 452 records parse and serialize byte-exactly.
- The physical layout is implemented and documented.
- Uncertain field meanings remain raw.

## Established Pointer and Variation Findings

ROM-003 observed nine pointer-labelled words across all 452 entries:

- 4,068 total observations.
- 2,827 null.
- 1,241 valid in-ROM.
- 0 out of range.

`variation_array_pointer_raw` is valid, unique, and 4-byte aligned in all 452
entries. ROM-004 read exactly one little-endian `u32` from each validated target:

- 452 attempted and 452 successful.
- 0 bounds failures.
- Every `first_word_raw` is nonzero, ROM-address-shaped, and 4-byte aligned.
- Its global semantic meaning remains `UNKNOWN`.

## Established Executable Flow

Thumb fetch `0x080089CC` resolves:

```text
MapEntry[+0x2C] + 4 * (selector - 1)
```

Selector `1` therefore selects `first_word_raw` at target `+0x00`.

ROM-006 verified this at runtime on the trusted ROM:

| MapEntry | Expected | Observed |
|---:|---:|---:|
| 1 | `0x082B5FA0` | `0x082B5FA0` |
| 4 | `0x082B5B2C` | `0x082B5B2C` |

This is Level 3 evidence.

## Established Population Flow

Thumb function `0x08009670` receives a selected value, reads words at
`selected +0x40/+0x44`, and calls `0x08012664`.

`0x08012664` receives manager, count, and pointer-array base; iterates
descriptors; loads each descriptor's factory pointer; dispatches indirectly;
and stores returned runtime objects in an IWRAM registry.

One observed runtime tuple included:

- `field_40_raw = 0x00000002`.
- `field_44_raw = 0x08294960`.
- manager `0x03002A64`.

This path is not graphics evidence.

## Spatial Object Research

ROM-007 and ROM-008 established this factory family:

| Property | Value |
|---|---|
| Raw factory target | `0x08007675` |
| Thumb fetch | `0x08007674` |
| Example descriptor | `0x08294948` |
| Allocation size | `0x18` bytes |
| Dispatch-table base | `0x0804A09C` |
| Runtime bounds | signed halfwords at `+0x04/+0x06/+0x08/+0x0A` |
| Retained descriptor | object `+0x14` |
| Callback-like reference | object `+0x0C` |

The factory creates a 24-byte rectangle-aware runtime object. The population
manager then registers the returned object. Construction paths in the observed
registry are heterogeneous.

Supported classification:

**STRONGLY SUPPORTED: generic 24-byte rectangle-aware runtime object.**

Not proven: collision, trigger, activation, transition, event, or interaction.

## ROM-008 Result and Current Blocker

ROM-008 dynamically reproduced the target factory, exact returned object,
registry insertion, bounds, and lifecycle attribution. It did not reach an
AABB query or callback for that exact object. A callback from another object is
not evidence for this object.

Verified query entries are `0x080126D4`, `0x080127AE`, and `0x08012846`.
Direct point-query callback paths include `0x08012784` and `0x0801279C`.

Current evidence level: **Level 3**.

Parser readiness for the `0x08007675` descriptor family: **NO** as of ROM-008.

## ROM-009 Result

Private input hashes: state 72,775 bytes /
`ea500f3a774d42032202d9c3d7bfb437478417ba37e4b72c634993d7d701ac82`;
save 8,192 bytes / `9bbd7cb67b724fbe1263d9b5b7cedf0a6c935a2ff6448befd0a0348b7607f46a`.
Runtime reproduced MapEntry 39, descriptor `0x08294948`, raw factory
`0x08007675`, X `0x0203DE7C`, slot `0x03002A68`, and bounds
`(592,136)..(601,241)`. No verified query, caller, guard, exact AABB, or callback
ran after X became live; context slot `0x03001C34` was raw zero at insertion.
Result: **D. ENVIRONMENT BLOCKED**; dialogue **UNRESOLVED**; cause `UNKNOWN`;
evidence Level 3. Parser readiness remains **NO** because source-descriptor
extent/boundary and a complete lossless field map remain unestablished.

## Unresolved Questions

- Which different verified dialogue-free state or scoped route instantiates a
  non-null point-query scheduler context for the exact object?
- What scheduler decision prevents the verified query-capable callers in the
  ROM-009 input? No instruction-level rejecting guard was reached.
- What immediate behavior follows the exact callback, if captured?
- Is the `0x08007675` source descriptor structurally bounded well enough for a
  future minimal read-only parser?
- Which semantic subtype, if any, is justified for this rectangle-aware family?

## Upstream Pins

These verified pins mirror `../upstreams.lock`; that lock file remains the
operational source of truth.

| Upstream | Commit |
|---|---|
| DragonByteZ | `b2691209fa873cc0c1d7aa9cdea7c1da4430afe4` |
| Legacy | `d22a556cd33dee56513d5b606b6ae8065ccc5752` |
| buusfury | `cc53d0cd2d1c167e749419187e2d92017ac07468` |
| gbarecomp | `6571cb39858af70d691914132f81b01a4558d815` |
| Legacy of Goku recomp | `fbe502a3d44256402262cd3f5baeb072a7235932` |
| Legacy of Goku II recomp | `add98b5d76fb2b822be870f29fa27b22c9a95631` |
| Buu's Fury recomp | `453a913a9f67916b9b358776da1c1229b09a6c80` |

## State Update Policy

At the end of each completed ticket:

- record only facts actually established;
- preserve unresolved status where evidence is insufficient;
- update portable test counts and evidence levels;
- record a baseline SHA only after its commit exists;
- keep detailed evidence in the research documents;
- keep this file concise rather than chronological.
