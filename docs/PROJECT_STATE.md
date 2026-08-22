# LOG1 Remake - Verified Project State

This file records current verified facts. Permanent rules live in
[`../DEVELOPMENT.md`](../DEVELOPMENT.md). Detailed evidence and provenance live in
[`reverse-engineering.md`](reverse-engineering.md) and
[`consumer-analysis.md`](consumer-analysis.md).

## Current Baseline

- ROM-011 research baseline: `0d0c0e39c058b7cfba9abcdc30d95849c6310e10` (`feat: capture live spatial-object read`).
- Latest completed and committed research ticket: ROM-012.
- ROM-008 portable baseline: **192 passed, 0 failed, 0 skipped**. Current portable suite after workflow migration: **199 passed, 0 failed, 0 skipped**. Current portable suite after ROM-011: **250 passed, 0 failed, 0 skipped**. Current ROM-012 portable suite: **289 passed, 0 failed, 0 skipped**.
- Persistent the tool workflow migration is installed.
- ROM-011 and ROM-012 are archived at `docs/research/archive/ROM-011.md` and
  `docs/research/archive/ROM-012.md`. `docs/PROJECT_<local-state-name>` records that no
  next ticket is active. ROM-013 is unstarted.

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

## Earlier Runtime Results

ROM-008 established exact object lifecycle attribution and query entries
`0x080126D4`, `0x080127AE`, and `0x08012846`, but no exact callback. ROM-009's
clean state reached the same live family without scheduling a verified query and
ended environment-blocked. ROM-010 confirmed its one-launch harness worked but
the available bounded inputs still scheduled no known post-live query. Detailed
inputs, negative evidence, and safety records remain in the research documents.

## ROM-011 Result

Stock GDB read watchpoints reduced play below 1 FPS. A separate SDL build from exact mGBA commit `26b7884bc25a5933960f3cdcd98bac1ae14d42e2` now provides a dedicated one-shot CPU EWRAM read-range probe with command-driven control and no UI automation; stock mGBA and the ROM are unchanged.
The five-second check observed stock 59.890, disarmed 59.129, and armed 59.727 VCOUNT rollovers/second, rejecting sub-1-FPS behavior. Long sampling gaps and Qt-versus-SDL prevent a valid throughput ratio; the corrected human run supplied the qualitative latency check.
The corrected human run retired discovery breakpoints after native arming; the user reported normal performance. The first exact read was a signed 16-bit load at PC `0x08012748` from live X `0x0203DE7C` offset `+0x04`, inside point-query routine `0x080126D4`. Human context was Goku entering the idle sit-down animation; this does not prove causation.
ROM-011 result is **C - IDLE/NORMAL PROCESSING READ CAPTURED**. Exact-X consumption at the point-query is **CONFIRMED, Level 3**. Dialogue and the specific region subtype remain **UNRESOLVED**; parser readiness remains **NO** because source-descriptor extent/boundary is still unknown.

## ROM-012 Result

Post-load registry reconstruction on private state SHA-256
`58228e1dc4ce81c80182242b650e18c0ee3db71f79473a614e5e373de207e0f7`
validated MapEntry 39, slot `0x03002A68`, X `0x0203DE6C`, descriptor
`0x08294948`, raw/fetch factory `0x08007675/0x08007674`, and half-open bounds
`x=[592,601), y=[136,241)`. Query entity `0x0202E4D0` tracked human movement.

The native exact gate captured PC `0x0801277A` reading `X+0x0C` at query point
`(592,218)`. Receiver `0x0300195C` / dispatch base `0x0804A0AC` invoked
vtable[2] raw/fetch `0x08007769/0x08007768`, which returned 1, then vtable[1]
raw/fetch `0x080125E9/0x080125E8`, which executed and reached downstream target
`0x080075AC`. Human observation, kept separate, was an immediate transition to
the next area followed by dialogue.

ROM-012 result is **B - EXACT TARGET ACTION CAPTURED**. Exact containment,
filter acceptance, and action execution are **CONFIRMED, Level 3**. A
transition-initiating spatial action is **STRONGLY SUPPORTED, Level 4** by the
controlled executable trace plus immediate observation. Dialogue gating,
collision semantics, and a final subtype remain **UNRESOLVED**. Parser
readiness remains **NO** because source-descriptor extent/boundary and a
complete lossless field map are still unestablished.

## Unresolved Questions

- Which higher-level caller invokes point-query `0x080126D4` during the
  ROM-011 idle/normal-processing path?
- What is the complete call tree after ROM-012 action target `0x080125E8`,
  which did not return within the bounded 512-step trace?
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
