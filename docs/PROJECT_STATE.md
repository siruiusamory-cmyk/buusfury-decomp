# LOG1 Remake - Verified Project State

This file records the project's current verified facts: measured ROM identities,
addresses and offsets, established format rules, behaviour that reproduces, the
hypotheses that have been confirmed or refuted, and the questions still open.
Permanent rules live in [`DEVELOPMENT.md`](DEVELOPMENT.md) and
[`ROM_SAFETY.md`](ROM_SAFETY.md). Detailed derivations and
per-system evidence live in [`reverse-engineering.md`](reverse-engineering.md),
[`consumer-analysis.md`](consumer-analysis.md) and the files under
[`research/`](research/).

Claims below use the project's evidence labels. A measured value is stated as
measured; an interpretation that is not independently proven is marked
`INFERRED`, `PARTIALLY CONFIRMED` or `UNKNOWN`, and the term `REFUTED` marks a
claim that measurement overturned.

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

The canonical savestate is
`2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab`, 67,351
bytes. The canonical image is never a write target.

## MapEntry table and record

For the trusted profile:

- GBA table address `0x0808E2E0`.
- File offset `0x0008E2E0` (also written `0x08E2E0`).
- Record size and stride `0x38`.
- Record count 452.
- Exclusive end `0x000945C0` (also written `0x0945C0`).
- Iteration is fixed-count, with no sentinel.
- All 452 records parse and serialize byte-exactly.
- The two bytes at `+0x00` are used as a big-endian lookup key. They are not
  promoted to a proven physical big-endian `u16` schema field or a semantic map
  ID.
- `+0x0C` is physically a little-endian `u32` whose canonical high halves are
  zero. Its low half resolves through the verified text-pointer
  infrastructure; player-visible map-name semantics remain unproven.
- `+0x2C` is a verified indexed-word source, and selector 1 consumes its target's
  `+0x00`. The selected root's semantic identity remains unresolved.
- `+0x2C` is live on all 452 entries (452 distinct targets, zero shared),
  addressing one heterogeneous factory-tagged stream `0x080728CC..0x0808E1E0`
  (112,916 bytes, 40 interleaved families).
- The physical layout is implemented and documented. Uncertain field meanings
  remain raw.

## Pointer and variation findings

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

## Established executable flow

Thumb fetch `0x080089CC` resolves:

```text
MapEntry[+0x2C] + 4 * (selector - 1)
```

Selector `1` therefore selects `first_word_raw` at target `+0x00`. The selector-1
root is reached on the ordinary map-load route through `0x08008AC2` and that
accepted `0x080089CC` root resolver.

ROM-006 verified this at runtime on the trusted ROM:

| MapEntry | Expected | Observed |
|---:|---:|---:|
| 1 | `0x082B5FA0` | `0x082B5FA0` |
| 4 | `0x082B5B2C` | `0x082B5B2C` |

This is Level 3 evidence.

## Established population flow

Thumb function `0x08009670` receives a selected value, reads words at
`selected +0x40/+0x44`, and calls `0x08012664`. The pair at `root + 0x40` /
`root + 0x44` is a proven engine count/pointer pair, not a census-only
inference: the engine advances the base to `+0x40` and reads both fields with one
8-byte `ldm` (`0x08009672` `adds r1,#0x40`, then `0x08009676` `ldm r1,{r1,r2}`),
so no constant-offset load of either word exists and a displacement scan finds
nothing.

`0x08012664` receives manager, count, and pointer-array base; walks exactly the
accepted count at a 4-byte element stride (`lsls r0,r4,#2`); takes each selected
record's `+0x00` word as a function pointer (`ldr r1,[r0]`, executed through the
`bx r1` trampoline `0x08046aa2`); appends the returned object at
`registry + 4 + 4*n`; and iterates index `count-1` down to `0`. One observed
runtime tuple had `field_40_raw = 0x00000002`, `field_44_raw = 0x08294960`, and
manager `0x03002A64`. This path is not graphics evidence.

Kept distinct rather than collapsed: `+0x40` physical field **CONFIRMED**,
`+0x40` count semantic **CONFIRMED**, `+0x44` physical pointer field
**CONFIRMED**, `+0x44` list relationship **CONFIRMED**; only the name
"connector" stays **PARTIALLY CONFIRMED**.

Root census: 452 roots, 104 zero/null and 348 non-zero/non-null, with
`count == 0` if and only if `list == 0` (452/452), count sum 735, maximum 14,
348 distinct `+0x44` targets, none shared between roots.
`root + 0x44 == root - 4 * root[+0x40]` holds on all 348 non-null roots; it is
recorded as a corpus layout invariant and not as an engine rule. Record
population: 735 references, 735 unique records, 0 shared, 0 malformed, block
stride 24 bytes. References, unique records and distinct destination keys are
three separate numbers and are never collapsed.

## Spatial object research

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

The factory creates a 24-byte rectangle-aware runtime object, which the
population manager then registers; construction paths in the observed registry
are heterogeneous. **STRONGLY SUPPORTED: generic 24-byte rectangle-aware runtime
object.** Not proven: collision, trigger, activation, transition, event, or
interaction.

The 20-byte rectangle family (`0x0800742D`) has zero run starts referenced from
the MapEntry table at three indirection levels; its subtype words are vtable
getters returning IWRAM addresses, so class identity is built at load time; the
one confirmed rectangle is a transition receiver; and no walkability grid exists
(0 low-entropy targets across 784 live MapEntry pointers). Correction recorded:
`0x08046AA4` is a gcc `__call_via_rN` veneer, not a point query, and `+0x54` is
a virtual method slot.

## Runtime query, transition and object results

ROM-008 established exact object lifecycle attribution and query entries
`0x080126D4`, `0x080127AE`, and `0x08012846`, but no exact callback. ROM-009's
clean state reached the same live family without scheduling a verified query and
ended environment-blocked. ROM-010 confirmed its one-launch harness worked but
the available bounded inputs still scheduled no known post-live query.

Stock GDB read watchpoints reduced play below 1 FPS, so a separate SDL build from
mGBA commit `26b7884bc25a5933960f3cdcd98bac1ae14d42e2` supplied a one-shot CPU
EWRAM read-range probe; stock mGBA and the ROM are unchanged. The five-second
check observed 59.890 stock, 59.129 disarmed, and 59.727 armed VCOUNT
rollovers/second, rejecting sub-1-FPS behavior. The first exact read was a signed
16-bit load at PC `0x08012748` from live X `0x0203DE7C` offset `+0x04`, inside
point-query `0x080126D4`. Exact-X consumption is **CONFIRMED, Level 3**. Dialogue
and region subtype remain **UNRESOLVED** and parser readiness remains **NO**.

Post-load reconstruction on private state SHA-256 `58228e1d...` validated
MapEntry 39, slot `0x03002A68`, X `0x0203DE6C`, descriptor `0x08294948`, factory
`0x08007675/0x08007674`, and bounds `x=[592,601), y=[136,241)`. The native gate
captured PC `0x0801277A` reading `X+0x0C` at `(592,218)`; receiver `0x0300195C`
and dispatch base `0x0804A0AC` invoked filter `0x08007769/0x08007768`, which
returned 1, then action `0x080125E9/0x080125E8`, reaching `0x080075AC`. Result is
**CONFIRMED, Level 3**, and with the human observation **STRONGLY SUPPORTS,
Level 4** a transition-initiating action. Dialogue gating, collision semantics,
and subtype remain **UNRESOLVED**; parser readiness remains **NO**.

Descriptor `0x08294948` began with bounds `x=[592,601), y=[136,241)`. A generated
ROM changed only file byte `0x00294954`, `0x59 -> 0x50`. Fresh runtime slot
`0x03002A68` linked object `0x0203DEBC` to that descriptor/factory and reported
`x=[592,592), y=[136,241)`. The canonical ROM remained unchanged. Human
observation separately found the transition still occurred. The patch propagated
but the behaviour persisted, and the remaining source is **UNKNOWN**. No
controlled playable ROM modification was achieved on this path.

## Ghidra static-analysis calibration

Ghidra 12.1.2, Temurin 21.0.11+10, and `pudii/gba-ghidra-loader` commit
`9bfb2d1fe891aa78bab7093a328feb3a52318ab7` were calibrated; all local tools, ROM
copies, projects, caches, and reports remain ignored under `build/ghidra/`. The
verified ROM imported as `ARM:LE:32:v4t:default` with ROM at `0x08000000`, mapped
GBA regions, a parsed header, and an ARM entry at `0x080000C0`. Bounded default
analysis timed out at 900 seconds but saved the project. Blind analysis missed
all five target functions and chose the wrong ARM/Thumb context for four;
established entry/callsite seeds then yielded matching point-query, factory, and
callback bodies, but not the indirect action path to `0x080075AC`. Outcome:
**B - ADOPT WITH REQUIRED CORRECTIONS**. Use Ghidra as the default static
database only with explicit Thumb checks, conservative labels, and corroboration
of boundaries and indirect targets. Headless reporting is verified;
[`ghidra-workflow.md`](ghidra-workflow.md) has full details. No broad BSM
transfer, Data Crystal import, or further executable-system research occurred.

## Webfoot container wrapper and packed codec

The Webfoot container wrapper is the engine's own Thumb dispatcher
`0x0803D940`, established as an engine code path rather than inferred from an
external tool. It receives exactly `(source, destination)`: its first instruction
`adds r2, r0, #0` discards the incoming third argument, so it never receives an
output-capacity argument. It reads `container[+0x00]` and dispatches on storage
form:

- **form 0 is the stored/raw form**: `memcpy(destination, container + 8,
  container[+0x04])` through the ROM ARM memcpy at `0x08046D18`;
- **forms 1 and 2 dispatch to the packed decoder** through the Thumb to ARM stub
  `0x08049120`;
- any other value returns with the destination **untouched**.

Wrapper and codec are kept as separate layers and are not collapsed: the wrapper
owns the form word, the declared-size word, the `+0x08` payload offset and the
stored/packed choice; the codec owns the bit grammar, the literal-width and base
escapes, the distance and count codings and the end marker.

The relocation relationship is preserved and not simplified into a fixed-address
claim: the stub `0x08049120` resolves to IWRAM `0x03000040`, which is ROM
`0x087B79E4`, inside the blob copied from ROM `0x087B79A4` to IWRAM `0x03000000`,
with accepted startup DMA3 evidence for 4100 bytes. The packed decoder is blob
base plus `0x40`; `0x087B7A9C` is an interior bit-loop label, not an entry.

A first wrapper word of zero means **stored data**, byte count at `+0x04` and
payload at `+0x08`; it does **not** mean empty, sentinel or invalid, except when
the declared size is itself zero. Canonical instances: two selector-stream
containers declaring 4 bytes, and the engine's own default container `0x08070808`
(form 0, declared 0), which the dominant-layer constructor installs into its four
resident-slot pointers. `UnknownHeader` is not a canonical wrapper form: the
accepted dispatcher recognises only `0`, `1` and `2`, and no accepted engine path
skips four arbitrary bytes and then invokes this decoder as a separate container
form. **64 KiB is not an engine or format limit**; it is host-tool convenience
and is never documented as a maximum.

The packed codec is described as **JCALG1-like / derived**, preserving separation
between observed engine bitstream behaviour, external naming and exact byte
compatibility; exact vanilla JCALG1 identity is not promoted. The two packed
kinds share one decoder and differ only in initial literal width, and the opener
sets that width to 8 explicitly, so the token stream is kind-agnostic. An
authored body is emitted as kind 1, the kind the engine demonstrably renders
3,745 times.

Canonical census over the accepted selector-root corpus: 421 distinct selector-1
roots, 4520 references, 4324 unique containers, 4324 unique decoded payload
digests, 4322 packed, 2 stored, 2 stored/zero-first-word, 0 malformed, 0 digest
collisions, declared sizes 4..16384 and source consumption 12..8708. References,
unique containers, unique payload digests, stored forms and packed forms are kept
as separate populations and are never collapsed. All 4322 / 4322 packed
containers decode byte-identically under both checked implementations, produce
exactly their declared decoded size and meet their end marker at that same output
length, recorded as a canonical observation and kept distinct from any general
format requirement. The packed decoder receives **no caller-supplied destination
capacity**: an independent enumeration of every comparison in it found no
output-pointer bound comparison, and no broader overflow claim is made.

### Decoder success contract and the literal base

The shipping decoder did not strictly enforce exact declared-size completion: a
final match, and separately a raw-literal run, could pass the declared decoded
size and be silently clipped, so a malformed or truncated stream could appear to
succeed. Both paths now refuse, as do truncation, early termination and invalid
back-references; success means exactly the declared size or an error. The change
is behaviour-preserving on accepted input: all 7,390 reachable canonical
containers decode byte- and extent-identically to the independent reference and
to the pre-change decoder, no container needs either clip, the run token is
unused by the whole corpus, `packed_end` is unchanged, and `pack` to `unpack` is
exact.

When a packed stream returns to 8-bit literals, that return clears a 7-bit run's
literal base. The shipping decoder retained the stale base, so affected atlas
banks decoded with correct tile geometry and palette indices shifted by it. The
rule is `CONFIRMED_RUNTIME` from MAP-GFX-DIAG-001 against the engine's own
character memory (a complete 16,384-byte bank reproduced byte-for-byte), and it
stands in the SDK decoder (`webfoot_lz._unpack_stream`), the export reader and
the research reference, which is also what makes the two implementations agree on
all 77 previously divergent banks. Blast radius, measured: 77 of 187 banks and
369 of 452 assembled map character blocks change; **0** of 3,745 chunk
containers, **0** of 7,390 sprite graphics containers, **0** of 452 selector
streams and **0** of 2,721 animated-tile frames change. Every changed byte in
those 77 banks is a literal emitted under the stale base or a match copy of one
(exact set equality per bank, 77/77, 307,890 bytes). The production decoder
reaches the engine's own screen ceiling (`0.9390`) and differs from the engine's
complete captured bank payload at 0 of 16,384 bytes.

### Packed-stream termination rule

The retail packed decoder (`0x087B79E4` = IWRAM `0x03000040`, via the veneer
`0x08049120`) takes `(source, destination)`, keeps no output counter and compares
nothing against its destination cursor, so it terminates on the bitstream's own
escape and on nothing else: **twelve zero bits at a token boundary**
(`000` + `0000000` + `00`). The declared decompressed length is a host-side bound,
not the engine's rule, and the decoder can read past the nominal payload until it
meets the escape. That a specific authored stream caused visible runtime
corruption remains **INFERRED** and is not claimed as observed.

The encoder now emits the engine's own escape. `_WordBitWriter.write_end_marker()`
writes it through the existing bit writer and `pack` calls it after the final data
token and **before** the final word is padded, so the order is data tokens,
escape, padding, and every output self-terminates independently of its alignment,
its allocation's padding or the bytes that follow it. The cost is measured, not
assumed: nothing or one packed word. `webfoot_lz.validate_retail_termination` is
the single production implementation of the postcondition (exactly the declared
output, a reachable explicit escape at that boundary, no malformed or truncated
token), and the shipped compressed-dialogue path and the sprite payload planner
both invoke it and fail closed before any size or allocation decision.

The pinned discriminator `pack(b"A" * 64)` is pre-fix
`0200000040000000fe53d020` (12 bytes, zero padding bits: host-decodable, refused
by the validator) and post-fix `0200000040000000fe53d02000000000`. A generated
corpus (alignments, powers of two, repeats, patterns, incompressible, shortest,
empty) is 100% self-terminating and round-trip is exact. Canonical corpus
thresholds: 13,168 structurally valid / 13,162 accepted at the narrow cap and
13,189 / 13,183 at the wide cap, with the same six suspect headers refused
identically by both readers and **0** disagreements. A Phase-1 record's
`pack(b"A" * 64)` packed length of 292 bytes was wrong (a row-carry from a
different payload's probe row); the measured value is **12**, pinned as a fixture
in both directions.

## Map root template

Engine behaviour, not LOGExtractor's renderer, establishes the selector-1 root as
a **per-map load-time definition template** consumed by the map-load paths. Thumb
`0x0800953e` takes the template and copies scalar values into RAM map state while
handing its pointer fields to downstream loaders; `0x0800938c` then programs
`BG0CNT..BG3CNT`, the palette and `DISPCNT` and indexes an engine table with root
`+0x3c`.

- `+0x08`/`+0x0a` are physically halfwords holding **map extent in pixels minus
  one**. They are read with `ldrh` and stored as `extent - 1`.
- The root's declared extent is the camera's maximum scroll: the engine saturates
  the requested camera origin to `[0, extent - 1]` at `0x080094F0` and again in
  play at `0x08009744`. The extent gates the camera only; no actor-position code
  reads it.
- Two earlier published claims are **corrected**: that `extent - 1 + 239` is the
  camera maximum, and that `0x0800938C` offsets the BG scroll base.
- Three count/pointer pairs, `+0x0c`/`+0x10`, `+0x24`/`+0x28` and
  `+0x40`/`+0x44`, are each exactly null-coupled across all 452 selector-1 roots;
  no stronger subsystem name is assigned to them.
- `+0x14`/`+0x18`/`+0x1c`/`+0x20` point into layer-record structures exposing a
  Thumb handler at `+0x00` (`0x08008087` dominant), separate chunk-dimension
  bytes at `+0x14`/`+0x15`, and a container-pointer array at `+0x18`.
- `+0x48` is a compressed, delta-coded `u16` selector stream, and `+0x4c` is the
  same engine-global word on every observed root; neither is named more narrowly
  than the evidence supports.
- `root + 0x48` decoded `u16` values satisfy the engine recurrence
  `abs[0] = raw[0]`, `abs[i] = (raw[i] + abs[i-1] + 1) & 0xFFFF`, and each
  absolute selector resolves as a **(bank, tile) pair** through `root + 0x4c`:
  `value >> 8` indexes the bank array, `value & 0xff` selects a 64-byte tile
  inside that bank's `0x4000`-byte payload.
- **`0x179764` is corrected**: file offset `0x179764` / GBA address `0x08179764`
  is not itself the bank table structure but the value stored at `root + 0x4c`,
  invariant across all 452 selector-1 roots, leading to a **187-entry
  bank-container table** (186 entries declaring `0x4000` bytes, entry 186
  declaring `0x3c40`; largest bank index used 186).
- **`cmp r6, #4`** is a **four-entry streaming-cache warm-up limit**, not a
  permanent total-entry cap.

## Layer records

The four selector-1 root layer slots (`+0x14`, `+0x18`, `+0x1c`, `+0x20`) are
populated across all 452 canonical roots: **1808 layer references resolving to
1464 unique layer records** in `0x080707FC..0x082B8BC8`, **35 shared** between
maps, and **zero null slots**. An unused layer is the shared zero-dimension
record `0x080707FC` (referenced 249 times), not an absent pointer. A map root
carries exactly four layer-slot pointers, all non-null on all 452 canonical
roots, so "create a layer" means activating such a slot with a new dominant
record; no dynamic layer list is modelled. **Eleven canonical roots are shared**
by more than one map, and a shared root is refused outright because it holds the
slot pointers and the extent.

A layer record's `+0x00` is an **odd Thumb code entry**, not a numeric type ID:
**five** distinct entries occur (`0x08008087` 1420 records / 1516 references,
`0x0800897B` 41/41, `0x08007A41` 1/249, `0x08007B63` 1/1, `0x080088BD` 1/1), and
they do not share a proven schema. Only the dominant form has an established
consumer.

The dominant `0x08008087` form is established: constructor `0x08007b78` reads
`+0x14`/`+0x15` as two physically separate unsigned byte fields (`ldrb` at
`0x08007bdc`/`0x08007bde`, `muls` at `0x08007be0`) and the streaming consumer
indexes as `y * record[+0x14] + x` at `0x08007c86`, so **`+0x14` is the X/count
dimension and `+0x15` the Y/count dimension**; they are never merged into a
`u16`. **`+0x18` is the chunk-pointer array**, indexed `record + 0x18 + 4*i`
(`0x08007bf2`); the previously established **`0x18`-byte element stride belongs to
the separate ROOT `+0x24`/`+0x28` subsystem** and is not assigned to it.

LOGExtractor's reading of record `+0x0d`/`+0x11` as X/Y coordinates is
**REFUTED for this form** (0 on 1458 and 1453 of 1464 records, and absent from the
established consumer path). The accepted conclusion is narrower than a global
absence claim: the broader ROM does contain offset-`0x0d`/`0x11` accesses (2035
undecodable halfwords with `ldrsb`, `ldrsh` and offset-`0x0d`/`0x11` accesses
present), so **actual layer positioning remains UNRESOLVED** and no replacement
signed transform was invented. The earlier false "no consumer" claim for
`+0x0c`..`+0x13` is corrected: those bytes are **consumed as two words copied to
`object+0x44`/`object+0x48`**.

**A dominant layer record is header plus window and nothing else.** Measured over
all 1,516 canonical dominant records the record length is exactly
`0x18 + 4 * columns * rows` (28 bytes for 1x1 through 104 for 5x4), and the bytes
immediately after the window belong to the next structure; on map 40 BG1 the word
after the window is the kind-1 container header BG2's cell 0 points at. A grid
that grows therefore cannot stay where it was: the record is re-emitted whole,
with its `+0x04`, `+0x08`, `+0x0C`, `+0x10` and `+0x16` fields carried verbatim
because their semantics remain `UNKNOWN`, and the map root's own layer-slot field
is repointed at it.

## Tile chunks

The dominant `0x08008087` layer container format is established, for that handler
only. `record + 0x18 + 4*i` points **directly** at a Webfoot container; there is
no second pointer dereference. The accepted census keeps five units distinct:
**1516** layer references enumerate **4274** grid cells, **156** null and **4118**
aligned non-null with **0** malformed, resolving to **3745 unique targets** of
which **165 are shared** with a maximum reuse of **10**. Every target is kind-1,
declares `0x800` bytes and decodes to 2048 bytes; all 3745 payload digests are
distinct.

The accepted physical format is **1024 little-endian `u16` entries** in a
**32 column x 32 row** grid with a **64-byte** row stride, from `(row & 31) * 64`,
`(col & 31) * 2` and a halfword load at `0x0800806a`..`0x08008074` plus the
64-byte VRAM row copy; entry width is `u16`. The engine-confirmed visual tile
unit is **8 x 8 pixels** (`asrs #3` on both axes, the 64-byte per-tile copy and
the `>> 8` chunk index), so a dominant-form chunk covers **256 x 256 pixels**.

- Entry **bits 0-9 are a CONFIRMED tile ordinal field**: the total-coverage
  invariant found **1,241,888** nonzero entries and **0** outside the union of the
  map's static selector ordinals and its animation destination ranges; this is not
  strengthened into "final VRAM tile number". The maximum observed ordinal is 895.
- **Bits 10 and 11** are used in canonical data (**46,034** and **15,668**
  occurrences; 5,239 both) but their horizontal/vertical direction is only
  **PARTIALLY CONFIRMED**: the assignment rests on the platform BG entry layout
  under the engine's own 8bpp `BGxCNT` value, and no payload consumer reads them.
- **Bits 12-15** are zero across all **3,834,880** entries and are classified
  **RESERVED / CONSTANT IN CANONICAL DATA**, not "unused by the format". As
  palette bank they are zero in all 3,834,880 entries.

The chunk object model was measured, not assumed: over all 452 MapEntry records,
**1,516 dominant layers hold 4,274 chunk cells (156 null) naming 3,745 distinct
bodies**. There is **no chunk catalog** (a chunk is discovered only from a layer
window) and **no metadata outside the plane**. Cell references are four-byte
little-endian GBA addresses at `record + 0x18 + 4*cell`, observed
`0x08179A50..0x082B8BAC`, **4-byte aligned** (residues mod 16 spread evenly, so
16 is not required). Chunks **are shared**: 165 bodies serve more than one cell
and **160 of those across different maps**, which is why copy independence is
load-bearing. **Screen-entry ordinals are map-scoped**: a 42-map sample produced
42 distinct assembled character blocks, so an authored chunk is composed against
one map and placed only in that map's layers.

A tooling correction is preserved: a strict `>` in `find_field_extractions` made
`right_shift == 0` unreachable, so earlier absence statements about bits-0..9
masking sites were **vacuously true rather than measured**; the predicate was
fixed, the scan re-measured from 959 to **1532** pairs, and the invalid absence
claims are not restored. The applicability boundary is explicit: the model is not
generalized to `0x0800897b`, `0x08007a41`, `0x08007b63` or `0x080088bd`.

## Tile banks and the inferred authoring atlas

The raw tile banks now have an inferred authoring atlas. A bank container is 256
tiles in *storage order*, and storage order carries no meaning; a raw sheet's
jigsaw appearance is the storage order of the art, not a format layer. The
missing structure is already in the ROM: every decoded map layer is a regular-BG
screen-entry plane, so the engine has recorded which tiles appear next to which.
The authority is `tools/webfoot/tileset_compositor.py`, with the CLI entry point
`webfoot tileset census|atlas`.

The algorithm, in the order it runs: census every screen-entry occurrence across
all 452 maps, resolving each char-block ordinal through that map's own selector
stream to a `bank:tile` source; score directional cardinal adjacency by support
**and** conditional confidence, so a common filler tile that borders everything
predicts nothing; count repeated 2x2 and 3x3 motifs; grow motif components by
merging compatible repeated arrangements, where a tie is recorded rather than
forced; pack components on a deterministic, roughly-square tile canvas with at
least a one-tile gutter.

Measured over all 187 banks, as the fraction of a sheet's four-neighbour cell
pairs whose two tiles were ever observed adjacent in a decoded map: raw **0.378**,
inferred **0.731** (median 0.383 to 0.747; banks at or above 0.60: **0 / 187** to
**156 / 187**). **All 187 banks improve** and the smallest gain is **+0.069**.
Corpus: 452 maps, 1,808 layers, **4,562,944** cells, **0 map failures**, with
24,331 unattributable cells counted under their own name rather than dropped.
Three banks carry before/after evidence (0, 11 and 79, the most-used
least-coherent raw sheets): 0.327/0.425/0.323 rising to 0.814/0.703/0.705.
Provenance is per cell: every displayed cell resolves to a real source tile
through a census usage record carrying its palette banks, flip states, maps,
layer forms, chunk containers, raw 16-bit screen-entry words, an occurrence
digest and exact occurrence samples; every placement carries exactly one evidence
record (`motif`, `adjacency` or `no_constraint`). Conflicts
(`ambiguous_successor`, `ambiguous_motif_anchor`, `instance_budget_reached`) are
recorded, enumerated to a cap, and digested in full by `conflicts_sha256` with
`conflict_count`.

Recorded limits: mean inferred coherence is 0.731, not 1.0; bank 178 has no
repeated 2x2 or 3x3 arrangement at all, so its inferred sheet *is* storage order
and the tool says so rather than inventing a layout; duplicate presentation
instances mean a sheet holds more cells than the bank holds tiles, and both
quantities are reported separately; motif pair support is anchor-scoped and every
manifest states that rule.

**A correction worth carrying forward.** A supplied compiled library under
`Buu's Fury Resources/Tilesets/` is the **pre-correction** compile: decoding each
of its 187 `Sheet.png` files against the shipped decoder matches **110** and
differs on **77**, exactly the 77/187 banks WEBFOOT-LZ-LITERAL-BASE-001 changed.
`Tileset N` is bank N-1, confirmed by container address (`Tileset 1` =
`0x080945c0` = bank 0).

## Connector and transition records

Transition records are the `root + 0x44` arrays established in the population
flow above. The record begins with a **two-word (8-byte) class/prefix region**
that is not padding: `+0x00` is the callable entry and takes exactly two values
over the corpus (`0x08007675` on 566 records, `0x080072cd` on 169), and `+0x04`
is `0x0800776d` on all 735. **Two record classes are observed; their semantic
meanings remain unresolved**, and the records are not named door, exit, warp, edge
transition or interior transition.

- At `+0x08` begins a sequence of **four physical little-endian `u16`
  interval-bound fields**; read as `(A,B,C,D)` they satisfy `A <= C` and `B <= D`
  on **735/735** records with **0** zero-area pairs, 155 distinct values in
  `0..977`, every value `0` or `8k+1`. They are recorded as **two ordered
  intervals** and are not named left/top/right/bottom. Still unresolved: axis
  identity, coordinate units, coordinate origin, signedness beyond what the
  accepted instructions establish, inclusive/exclusive edge semantics, and the
  exact region-membership test.
- `+0x10` is a selector byte (`0..3` on 725 records), `+0x13` a further
  engine-read byte (`{0:561, 1:174}`), and `+0x14`/`+0x16` engine-read fields;
  none is promoted to spawn position, facing, direction, script, transition effect
  or entry point.
- The **destination key is byte-wise**: `record + 0x11` is the high byte and
  `+0x12` the low byte, and treated in that order it resolves to an accepted
  `MapEntry + 0x00` two-byte lookup key on **735/735** records. The engine handles
  the identifier byte-wise in three independent places (the record consumer,
  `ldrb` at `0x0800728c`/`0x0800728e`; the `MapEntry` lookup `0x080089fc`, two
  byte loads plus a byte `cmp`; and the transition path `0x08008d44`, two
  `strb`), so LOGExtractor's physical "big-endian `u16` destination map ID" model
  is **REFUTED**; big-endian is a correct display of the pair, not the physical
  representation.
- Link graph by the accepted counting method: **694** directed links, **674**
  reciprocal, **20** one-way, **3** self-links (maps 125, 126, 127), **350**
  distinct destination keys on **348** maps. Gameplay necessity is not inferred
  from topology.
- LOGExtractor's `X += 8` viewer adjustment remains **UNRESOLVED** and is not
  promoted to a format rule.
- The constant-immediate census is **3147** in-scope sites at real instruction
  boundaries, **0** misses, **0** misreports. A previously circulated figure of
  `31,971 of 31,973` did not survive re-measurement and is rejected rather than
  adopted. The methodology lesson stands: a constant-offset scan is **not**
  sufficient evidence of field absence, and absence claims must account for
  base-pointer adjustment followed by an aggregate `ldm`/`stm` access.

### Measured transition field semantics

Each field is resolved on a named instrument:

- **Destination**: the two-byte map key at `+0x11`/`+0x12`, resolved by the
  MapEntry key scan.
- **Region**: the four `u16` at `+0x08..+0x0F` as two ordered intervals, exposed
  positionally with no axis and no unit invented.
- **Arrival**: x at `+0x14`, y at `+0x16`/`+0x17`. The **566 class** passes the
  record's own pair to the engine, which applies its `-112`/`-76` bias at
  `0x08008D52`/`0x08008D5C`; the **169 class** builds a signed delta against the
  region and truncates. The two classes are **not interchangeable**, and a
  sentinel at or above `0xFFF8` means no authored arrival.
- **`+0x10` is `((arrival_direction + 1) << 4) | gate_direction`**: the low two
  bits select the door gate and the high nibble is the arrival-facing override, so
  a zero high nibble states no facing and a corpus census finds no record with a
  low nibble of 4 or more.

**One earlier claim is withdrawn.** `+0x10 = 0x02` does not mean "face West". The
facing was settled by instrument: with the record carrying `0x42`, the engine
replaced the player object (`0x0203CEB4` to slot null during the load to
`0x0202CCDC`) and the new player's own `+0x10` first read `03` = East from a
westward approach, matching `(0x42 >> 4) - 1 = 3`, while `0x03001A34` read `0` on
every sample. **What `0x03001A34` selects stays UNRESOLVED and its non-zero case
is UNTESTED.** A practice correction was recorded with it: a transition is
consumed when its trigger fires, so the first trigger after a load is valid
evidence and leave-and-re-enter is not a general prerequisite for warp proof; the
re-entry rule stays scoped to map and background assembly.

### Authoring an existing transition

`maps/transitions.toml` stores `TransitionIdentity(source map, array index)` with
each editable field as a prior/authored pair. The production build loads the
canonical record by that identity, verifies the stored prior, applies the edit
through the one authority, serializes only that 24-byte record in place, and
records provenance: a fixed-width overwrite with **no allocation, no relocation
and no second serializer**. A group that is absent is not authored, so an
untouched field is structurally incapable of changing, and a project authored
against a different image fails closed. Retail `map:0040/transition:0000` sends
map 40 to map 39; the same identity in a built derivative sends it to map 378
(Volcano) and to map 435 (Stomach), the latter playable end to end (timeline
40 to 435 to 434 to 435).

### Creating a transition the image does not contain

A transition can be created by a project and materialized by the normal build.
Its identity is `map:NNNN/transition:<name>` (the source map's durable key plus an
authored name) and it deliberately contains **no** ROM address, **no** allocated
address and **no** array index, because the index a created record occupies does
not exist until a build appends it. The record is composed over a required
**566-class template of the same source map**: the region (`+0x08..+0x0F`), the
destination key (`+0x11`/`+0x12`), the arrival pair (`+0x14`/`+0x16`/`+0x17`) and
`+0x10`'s high nibble are authored, while `+0x00`, `+0x04`, `+0x13` and `+0x10`'s
low nibble are carried from the template and published field by field in the
manifest. The preserved bytes are pinned as priors and checked against the live
template before anything is written, so a drifted template is refused rather than
silently re-initializing the new record. A template of another map, a 169-class
template, an unknown template, a drifted prior, a shared root and a composition
byte-identical to its template are each refused by name. A map with no supported
566-class record of its own cannot gain a transition; 298 of the 348
record-owning maps can, and that narrowing is the fail-closed answer.

This is the first transition domain that allocates. Two `EXPANDED_ONLY`
allocation kinds place a 24-byte record and the expanded `root + 0x44` pointer
array above canonical EOF; the canonical element pointers are copied into the
expanded array verbatim followed by the created element, `root + 0x40` grows from
N to N+1 and `root + 0x44` is re-pointed. Proven on
`map:0040/transition:volcano-gate` to map 435: count **2 -> 3**, array
`0x0829346C` to file `0x00800000` / GBA `0x08800000` (12 bytes), record file
`0x0080000C` / GBA `0x0880000C` (24 bytes) appended at index 2. All **735**
canonical records are byte-identical at identical addresses and the canonical
array is untouched in place; **within the original 8,388,608-byte span exactly
4 bytes changed** (map 40's count byte and three array-pointer bytes), while the
derivative is a 16 MiB generated image whose expansion additionally carries the
two allocated spans.

Addressability is **encoding-proven and runtime-proven**. `root + 0x44` and every
array element are full 32-bit little-endian GBA addresses by full census (452 of
452 roots, 735 of 735 elements, nothing masked or truncated), so an above-EOF
pointer encodes; and a human-operated mGBA run established that the retail
engine follows one, reading both authored structures at file `0x00800000` and
`0x0080000C`. That run is the capability's runtime proof: see
[`research/MAP_WARP_CREATE_RUNTIME.md`](research/MAP_WARP_CREATE_RUNTIME.md).

## Character appearance definitions

The engine's own instructions address a **232-record, `0x10`-stride** table at
file offset `0x74D380` (GBA `0x0874D380`): its start is supported by eight
`ldr Rt,[pc,#imm]` literal-load sites found by a whole-image even-offset scan, its
stride by eight `index << 4` sites (one per literal load), and its count by three
`cmp rN,#0xE8` loop bounds plus a 232-bit runtime bitmap; index **231** is the
last valid index and **232** falls outside.

- **`+0x00` and `+0x02` are `u16` indices into the verified text pointer table
  `0x0806BCE8`** (four loads from three pool words, `x4` scale,
  `ldr r1,[r1,r0]`), with 154 distinct `+0x00` indices resolving to **152**
  distinct strings and 154 distinct `+0x02` indices to **104**; `+0x02 == +0x00 +
  1` on 232 of 232.
- **`+0x04` is a `u32` index into the pointer array selected by accessor
  `0x08000158`**, whose accepted lookup is `u32 at 0x086B6BDC + 4*id - 0x28` for
  `id >= 10`, the `-0x28` being the compiler's fold of `-4*10`. LOGExtractor's
  `0x6B6BB4` is that folded arithmetic base and **not** the canonical beginning of
  the pointer run, which starts at **`0x086B6BDC` with 297 valid ascending
  entries** terminated by the non-ROM word `0x03001068` at `0x086B7080`; which
  byte is the run's first entry is **UNRESOLVED**.
- **`+0x08` is a `u32` index into the pointer array at `0x086F393C`** (the
  accessor's own literal), **163 slots** wide with slots `0..7` zero and `8..162`
  holding 155 valid ascending pointers, whose field values are `0` plus a
  110-element subset of the valid slots.
- **`+0x0C` is a signed `i32` index into the `0x08711274` family at a `0x1C`
  stride**, 123 distinct observed values over 144 non-negative references with
  **88 negative** values the engine skips with `blt`; its higher-level semantic
  identity remains **PARTIALLY CONFIRMED**.

The accepted table identity is deliberately narrower than a generic "character
table": **named appearance definitions with optional slot and stat-record
indices**, **PARTIALLY CONFIRMED**, because the 152 labels span fighters, generic
enemies, machinery and body parts and the attributes are optional (98 records
carry `+0x08 == 0`, 88 carry `+0x0C < 0`); completeness is UNKNOWN.
LOGExtractor's `+0x02` field is not skipped (three engine readers), its
"unresolved" `+0x0C` reading is superseded, and its addresses were confirmed to be
**file offsets**, not GBA addresses.

## Sprite definitions and animations

The `+0x04` accessor's array is **297 entries** at **`0x086B6BDC`**, logical ids
**`10..306`** with run index **`id - 10`**, all valid ROM pointers, strictly
ascending, **297 unique targets**, terminated by the non-ROM word `0x03001068` at
`0x086B7080`. **Ids `0..9` are party-slot aliases, not run indices**, and run
index 0 is simply **logical id 10** with no established special meaning.
**`0x086B6BB4` is not a run start**: it is the inline animation array of the
definition at **`0x086B6B60`**, the run's final definition, **id 306**,
`count = 10`, spanning **`0x086B6BB4..0x086B6BDC`** and ending exactly where the
run begins; LOGExtractor's `0x6B6BB4` reading is **superseded**.

A definition's **`+0x00` low byte is the count of elements in its inline
animation-pointer array** (`ANIMATION-COUNT SEMANTIC: CONFIRMED`): five engine
sites read it with `ldrb`, compare it against the requested index, load
`+0x54 + 4*index` and null-test the element, and the object extent
`0x54 + 4*count` holds for **231 of 296** adjacent pairs and **232 of 297**
boundaries, with the remaining **65 gaps** each exactly **`0x100`** bytes and each
gap pointed at by the **successor's** `+0x04`.

**`+0x54` begins an inline, count-bounded, variable-length, sparse array** of
32-bit ROM pointers (`ANIMATION-ARRAY SEMANTIC: CONFIRMED`): **4070 slots**,
**1721** non-null animation pointers, **2349** nulls, index 0 non-null in **297 of
297**. The **fixed ~23-slot model is REFUTED as a physical fixed-length model**,
and LOGExtractor's `stand`/`walk`/`run`/`attack...` slot names remain external
claims, mostly UNRESOLVED, and are not promoted. Selection is direct at
`0x0800ECDA(obj, index)` with **no range check** (162 sites, **161** passing a
constant in `0..21`); `0x0800ECF0` and `0x0800ED3E` translate state through the
**25-entry table at `0x08072670`** (`0..15` identity, `16..22` to `17..23`, states
`23`/`24` aliasing `10`/`11`), read by exactly **four** engine sites, one a
predicate. Frame selection uses `16 * frame + 4 * direction + 4`.

The accepted contradiction with `tools/webfoot/graphics.py::_animations_in` is
recorded and deliberately not repaired: its stated ground that no header field
bounds the animation list is **superseded** by `definition + 0x00`, its traversal
includes **4160 extra slots** that are all nonzero and non-ROM-pointer, yet
correcting it is a numerical no-op because the accepted corpus figures still
reproduce exactly (`1017 - 4 = 1013`, `13660 - 64 = 13596`, `10964 - 5 = 10959`,
`1562` deduplicated).

## Animation frames and pieces

An **animation object** is `u32 frame_count` at `+0x00` followed from `+0x04` by
a **4-byte-stride table of `4 * frame_count` 32-bit cell pointers**;
**`FRAME-COUNT SEMANTIC: CONFIRMED`**, the count being the number of table rows,
enforced by the frame advance (`0x0800DE78`..`0x0800DE90`, wrap form
`0x0800DEBA`..`0x0800DECC`). The engine indexes a **two-dimensional frame x
direction cell table** as **`animation + 0x04 + 16*frame + 4*direction`**, and the
frame index, direction index, frame/direction cell and pointed frame record stay
distinct populations, never a one-dimensional frame list. There are **four**
direction cells per frame, independent of `frame_count`: **13,660 cells** over
the 1,017 unique animation objects, **none null**, **3,415 in each position**.
The four-position structure is engine-grounded (the facing computers at
`0x0800A890` and `0x080159B0` write `obj+0x10` from a compare of `|dx|` against
`|dy|` and write only `{0, 1, 2, 3}`, the horizontal pair `2`/`3` chosen first
with the sign selecting within each axis), and the decisive corpus evidence is
that all **989** shared frame targets are confined to **one frame index** while
being reachable from multiple direction indices. **Individual direction names and
their physical order remain UNRESOLVED**; nothing north/south/east/west is
promoted.

The selected cell pointer is loaded into `obj+0x50`, and `0x0800EF38` computes
`*(u32*)(obj+0x50 + 16*obj[0x11] + 4*obj[0x10] + 4)` into `obj+0x54`. The
structured sprite resources reach 7,390 containers, all decoding, at file offsets
`0x003C34D0..0x006A87A8`, reached through `definition +0x54` to animation to cell
to frame record to piece `+0x08`, with each piece's stated extents equal to its
container's own declared decoded size.

A **frame record** is an **8-byte header** (`u32 piece_count` plus the frame's own
bounding box: `s8 min_x`, `s8 min_y`, `u8 width`, `u8 height`) followed by
`piece_count` **12-byte** piece records; the render loop `0x0800F3C0` computes
`r7 = frame + 8 + 12*index`, and `FRAME HEADER SIZE = 0x08` with
`PIECE STRIDE = 0x0C` are accepted. The bounding box reproduces exactly on
**10,980 of 10,980** frames and is the **rendered frame's** box, not a hitbox,
collision box, feet box or origin. There are **11,005 piece records over 10,980
distinct frames**: 10,959 declare one piece, **19 declare two and 2 declare
four**, so "all frames are single-piece" is **REFUTED**. **The old 4-byte-header
plus 16-byte-piece model is REFUTED**: under the accepted 8+12 layout
**11,005 of 11,005** pieces resolve to a container whose own declared decoded
length equals `piece[+0x02] * piece[+0x03]`, and no counted extent crosses the
next known frame start, whereas 4+16 **fails on 25 pieces** and **overruns the
following record on 16**.

A piece's **`+0x04` is the packed GBA OBJ attribute pair**
`(attribute1 << 16) | attribute0`, loaded at `0x0800F1C2` and `0x0800F24C` and
merged into the outgoing OAM word under the mask literal `0xFE00FFFF` (pool
`0x0800F4B0`); over all 11,005 pieces colour-256 is set on **11,005**, shape is
in `{0, 1, 2}` with the reserved shape 3 never used, horizontal flip is set on
**2,848**, vertical flip on **none**, and the shape/size decode reproduces the
stored extents on **11,005 of 11,005**, so `GRAPHICS_FORMAT.md`'s bit layout is
**confirmed** while its **offset was wrong**. Raw attribute bits are kept
separate from derived pixel width/height. A piece's **`+0x08` is the
graphics-container pointer** the rendering path uses (`0x0800F3CE`), and it is
the input the discovery census consumes; `GRAPHICS_FORMAT.md`'s "unique graphics
containers 7,355" is **confirmed as an exact subset**: 7,355 is precisely the set
reached by single-piece frames, while the corpus reaches **7,390** distinct
container offsets, the extra **35** being what the 21 multi-piece frames reach,
because the accepted reader's 16-byte stride rejects all 21 of them.
LOGExtractor's `value << 2` is given a narrower physical explanation rather than
retained: the stored word is a row count and the shift walks a row, which is why
`count * 4` still reproduced the flat cell count.

**A correction made under review is preserved rather than hidden.** An earlier
revision concluded that attribute-1 bit 12 correlated with a different graphic,
"the opposite of a stored horizontal-flip flag". That was **wrong**: the count had
compared **frame records** instead of **graphics containers**, and two distinct
frame records routinely name the same container. The corrected measurement is
that in the **2,600** poses where directions 2 and 3 differ in bit 12, the two
cells name the **same** container in **2,599** cases, a stored flip applied to
shared art.

## Graphics discovery census

LOGExtractor's `ImageScan` scanner was reconstituted from `mainant/LOGExtractor`
revision `3a78bb35ad181082fbc9da01057538e5a78e8c2d` (the only commit that ever
touched `ImageScan/MainForm.cs` or `ImageScan/Gba/JCALG1.cs`) and measured against
the accepted engine-reachable container graphs rather than trusted. Its algorithm
walks **every byte offset** from `0x200`, requires the first word to be exactly
`1`, requires `1 <= declared < 0x20000` **and** `declared % 4 == 0`, then accepts
the position when the decode returns without raising, with **no alignment,
palette, dimension or visual-plausibility test and no duplicate suppression**, and
with its only post-decode size test (`decoded length == 256`) changing **sort
priority** only.

On the canonical image that yields **8,388,093** positions tested, **29,504**
form-word matches, **13,463** submitted after the size filters and **12,990**
candidates. Recall against the **11,715**-container known-positive corpus is
**11,513 / 11,715 = 98.3%**, including **7,390 / 7,390 = 100% of the accepted
sprite-graphics containers, digest-exact**, 3,745 / 3,745 map chunks and 187 / 187
`root + 0x4C` banks. **Portrait recall is UNMEASURED**, that class was not
enumerated, and no map or bank class has an established graphics identity, so only
the sprite class is a graphics denominator.

**Recall is high but incomplete, and the gaps are the scanner's own filters, not
engine limits.** `kind == 1` makes the stored/form-0 resources invisible (**3**
known containers missed), and `declared % 4 == 0` rejects **199 genuine selector
streams** whose declared lengths are `4k + 2`. The modulo-4 rule has **no accepted
engine basis**. Correspondingly, stored-form coverage is structurally incomplete,
and stored resources are not called non-graphics merely because this scanner
cannot see them.

**A successful decode is not graphics.** A matching first word, a plausible
declared size and a clean decode establish VALID CONTAINER at most; they never
establish LIKELY GRAPHICS, let alone ENGINE-REFERENCED GRAPHICS. Of the **1,476**
external-model candidates at addresses no accepted structured graph reaches,
**1,453** are named by a word in the image, **16** are class F and **7** are the
unreferenced remainder; none is promoted to new, unused or unknown graphics. The
engine-informed **residual set is 5,479** (a different population from the 1,476),
of which **387 are packed and engine-referenced**. No graphics semantic and no new
canonical resource class is claimed for the 387, and they are not a homogeneous
tile-bank family: their declared sizes run 128..65,474 bytes, **129 declare 256
bytes**, and only **26 reach 8 KiB**. The concrete lead for synthesis is the
pointer/reference structure around **`0x087B5B64`**.

Scanner suitability: shipping discovery tool **NO**, forensic/research tool
**YES**, canonical resource enumerator **NO**. Its precision comes from the
corpus, not from the method (form 0 makes a scan accept essentially anything), so
structured engine graph traversal remains authoritative.

Corrections that changed scanner correctness and are preserved: the four-bit
code's `value == 0` arm (which moves one map-chunk container, making the two
grammars disagree on **78** of 11,712 known kind-1 containers and giving
map-chunk digest agreement **3,744**); a false-positive class named "inside a
known container" that was counting candidates inside **other candidates**
(**0 / 4 / 267** inside a known container against **2 / 7,084 / 15,320** inside
another candidate); a non-disjoint class sum of **11,717** against the true
distinct **11,715**; an overstated residual set; and a diagnostic field that
contradicted its own status on **414** rows. The first attempted `GetInteger`
correction was **itself inverted** and that is not sanitized out.

The synthesis classification of the 387 packed engine-referenced residuals:
**6** belong to the known `compressed_text` 7-word selector table at
`0x087B5B64` (consumer literal `0x080123CC`), **177** lie in two size-locked
tables (`0x086F395C`, 155 x 4096; `0x082ABF08`, 140 x 1024) with no consumer
evidence, and the rest retain their accepted classifications. **Overall residual
semantic: `UNCLASSIFIED`; no new graphics semantic and no new canonical resource
class.** Portrait scanner recall is `UNMEASURED / NON-BLOCKING`.

The consolidated canonical resource graph, the per-system schemas, the **39
refuted LOGExtractor assumptions in one list**, a read-support matrix over **15
resource classes** and an authoring-readiness matrix over **19** capabilities are
in [`research/LOGX_SYNTHESIS.md`](research/LOGX_SYNTHESIS.md). Its accepted
cautions in the terminology the work earned:

- MapEntry `+0x00` is two ordered key bytes, not a generic physical big-endian
  `u16`; `+0x0C` is a physical `u32` with a confirmed text-table relationship
  whose higher-level purpose is unresolved, not universally visible map-name
  semantics.
- The map root is a load-time definition/template; layer `+0x00` is a Thumb
  handler/function entry, not a numeric layer type; the dominant-layer findings
  apply to handler `0x08008087` only.
- Tile chunks are precise: 32 x 32 = 1024 little-endian `u16` entries = 2048
  decoded bytes; bits 12..15 are constant/reserved in the canonical corpus, not
  generally unused.
- The connector destination is two independent key bytes at `+0x11`/`+0x12`.
- Sprite definitions carry a count-bounded inline animation array (the fixed
  23-slot physical model is refuted); a frame record is an 8-byte header with a
  rendered-frame bounding box plus 12-byte pieces, piece `+0x04` the packed OBJ
  attribute pair and `+0x08` the graphics container; the accepted corpus is
  **10980 frames / 11005 pieces / 21 multipart frames**.
- Appearance records are named appearance definitions with optional slot and stat
  indices, not a "character table".
- The Webfoot wrapper dispatches at `0x0803D940` (form 0 stored, forms 1/2
  packed, `+0x04` declared decoded size, `+0x08` payload); the packed algorithm is
  JCALG1-like / derived; `UnknownHeader`-as-container and the 64 KiB engine limit
  are refuted; the decoder receives no caller-supplied destination capacity.

## UI, HUD and portrait graphics

A deterministic, literal-named UI/HUD container population exists: **34**
containers, **23 stored / 11 packed**, **0 overlap** with the 11,715-container
accepted corpus (the corpus filter removed **0** of the 34, and the intersection is
taken on the pre-filter set so the zero is a measurement and not a restatement of
the filter), **0 decode failures**, **20 named by more than one site**. The rule is
the engine's own addressing convention: a Thumb `ldr Rt,[pc,#imm8*4]` loads the
container address out of the code's literal pool; of 9,341 decodable load sites
and 4,556 distinct literal values, 4,522 are not containers, and the 34 are
word-aligned with a valid header and an exact decode. **The literal proves the code
names the address, not that it decodes it**: only **10 of the 34** have a
`bl 0x0803D940` within 32 bytes of their load site, so the role of the remaining
24 is **INFERRED** from literal plus header, and "10/34 observed dispatched" is
reported rather than smoothed over.

**Two earlier graphics leads are CORRECTED.** `0x08071700` is **not** a UI
graphics descriptor table: it is a word inside a table of subsystem blocks and
holds `0x03001C4C`, the font subsystem's EWRAM glyph buffer; `0x0800AB54` loads it
with `0x0800AB66 ldr r1,[pc,#0x214]` (pool `0x0800AD7C`) and reads `[r1,#4]` /
`[r1,#8]`. And `0x0806E050` (normal) / `0x0806F150` (critical) are **text/format
records**, not graphics: each `+0x00` is a **kind 0 / declared 0** word, the
engine's zero-length default container, so the damage number is drawn through the
font/OAM machinery and there is **no damage-number graphics container family**;
the visible red/yellow distinction is a record swap. The critical branch itself is
re-asserted unchanged (`0x0800E94E ldr r2,[r6]` / `0x0800E952 cmp` /
`0x0800E954 beq` to `0x0800E958 movs r2,#4` critical against `0x0800E962
movs r2,#3` normal).

Format: the accepted Webfoot container, no new decoder, 8-byte
`{u32 kind, u32 declared_size}` header, kind 1 the packed bitstream
`webfoot_lz` decodes exactly, and every one of the 34 decodes to exactly its
declared size. The header carries **no dimension field**, so a dimension is a
reading of the size, not a stored fact.

**CONFIRMED_RENDER for 7 assets**, rendered against the accepted object palette
and inspected: the **title screen** `0x083BE3D4`, the **copyright/legal screen**
`0x08055620`, three **publisher logos** `0x086F9EC8` (Atari) / `0x086FA398`
(FUNimation) / `0x086FABF4` (Webfoot Technologies), all
`38,400 = 240 * 160 * 1` bytes, plus a **240x16 HUD strip** `0x0807248C`
(`3,840` bytes, named by **8** code sites in 6 functions, moved to OBJ VRAM
`0x06010000` in 32-byte tiles with a 512-byte stride, a 240-pixel row at 8bpp) and
a **16x16 orange/yellow energy burst** `0x086B7E8C`. **Five of the six
38,400-byte screens render; the sixth, `0x08732604`, is an explicit render
failure** (240x160 noise) and is recorded as such. 25 of the 34 are whole-tile
sizes; **9 are not tile-aligned at either 8bpp or 4bpp** and their graphics
identity is **UNKNOWN**, as is that of the 27 containers not rendered to a
recognisable asset. The count is a count *for the literal rule*, and the rule
cannot see `add Rd,pc,#imm`, register-computed bases, wide encodings, data-table
entries, or a loader inside a RAM-relocated overlay, and **no UI pointer table was
located**, so unlike portraits nothing bounds the family's length. A related but
unestablished lead is the **55 kind-1 data-referenced containers in
`0x087315E8..0x0874D044`** (52 with exactly one aligned word reference, 3 with
none; ratio `declared/packed_extent` 5.33x..63.16x against a corpus median of ~3x,
inside the font glyph-source region), the leading glyph/UI-sheet table candidate.

Portraits are a deterministically enumerable, DATA-bounded run of **155**
containers (kind 1, declared and decoded size 4096, 0 decode failures) via array
`0x086F393C` read from accessor `0x08011F20`'s constant-pool word `0x08012194`,
disjoint from the 11,715-container known corpus; geometry is INFERRED and render
UNKNOWN. The portrait field `+0x08` belongs to the **232-record
appearance-definition table at `0x0874D380`** (stride `0x10`), **not** to the
297-entry `+0x04` run at `0x086B6BDC`. That was settled from the image: the
consumer `0x08025056` loads `0x0874D380` from pool `0x08025310`, scales the index
with `lsls r0,r0,#4`, forms `r7` with `adds r7,r0,r1`, reads `ldr r0,[r7,#8]` and
only then calls the accessor `0x08011F20`. The 297-entry run's own records carry
**16 distinct `+0x08` values, 7 of them zero and none in the portrait slot
range**, so they are not a portrait population.

Measured on all 232 records: **134 carry a portrait reference, 98 carry none, 110
distinct slots, range `8..162`, 0 in the reserved slots `1..7`, 0 above `162`**,
and **all 134 resolve inside the 155-entry run, 0 outside**. The run is a strict
**superset, not an equality**: **45 run entries carry no appearance-definition
reference** and **at least 22 carry no reference from any portrait-slot source
located**; those entries are structurally identical portraits inside the same
contiguous packed block, so they are not evidence of a missing portrait, but
**their consumer is UNKNOWN**. All three `bl` callers of the accessor were read
and **no third slot source exists**: `0x080250D2` and `0x0802605C` both resolve
the appearance `+0x08` (the second through an object cache written at `0x08025E9A`
from pool `0x0802618C`), and `0x0801548E` resolves the party table's slot-1 byte;
the accessor's own slots `1..6` read bytes `0x10..0x15` of the 24-byte-stride
table at `0x086B82EC` (**54** whole records, **60** distinct values `0..159`,
none at or above `163`), so no source escapes the run, though that party bound is
**INFERRED**, because the path indexes from unclamped runtime bytes. The run's
width stays **data-bounded** (no engine clamp found), corroborated by the block
ending exactly 4 bytes before the array base and by slot 163 holding `0x0011E502`
followed by non-pointer halfwords; **render identity (palette, dimensions,
placement) is NOT claimed**.

The **font** graphics path is located (`0x08753A18` to `0x087548DC`, blitter
`0x0802BF8E`) but its glyph population is unresolved. **No separate
ki-blast/effect graphics table** is proven; effects are INFERRED to ride the
actor/sprite machinery. The residual load-descriptor table `0x087B5B64` (6 ~65 KB
containers) and title/static/cutscene semantics remain open.

## Resource library and export

The resource exporter lives in `tools/export/` and walks the accepted post-LOGX
graphs; it never substitutes a heuristic scan for them, so `GFXSCAN` candidates
are not enumerated and no residual container is exported. The generated library is
a romhack/fangame resource pack: structural metadata only, **zero generated
prose**, no ROM-derived name invented, numeric IDs canonical, and heuristic
`GFXSCAN` residuals excluded from the canonical set.

Accepted coverage and populations:

```text
MAP ENTRIES                      452
TOTAL MAP LAYER REFERENCES      1808
  dominant                      1516   (handler 0x08008087)
  absent_placeholder             249   (handler 0x08007A41)
  static_graphical_screenblock    42   (0x08007B63: 1, 0x0800897B: 41)
  static_graphical_terrain_field   1   (0x080088BD: 1, map 19)
CLASSIFIED                      1808 / 1808
SILENTLY OMITTED                   0
GRAPHICAL LAYERS EXPORTED       1559
UNRESOLVED GRAPHICAL LAYERS        0
MAP COMPOSITES GENERATED         452
MAP COMPOSITES WITHHELD            0
TILE BANKS                       187
INDIVIDUAL TILES              47,857
DOMINANT UNIQUE CHUNKS         3,745
SPRITE DEFINITIONS               297
COUNT-BOUNDED ANIMATION SLOTS  4,070
NON-NULL ANIMATION REFERENCES  1,721
FRAME RECORDS                 10,980
SPRITE PIECES                 11,005
MULTIPART FRAMES                  21
STRUCTURED SPRITE GRAPHICS     7,390
GENERATED PROSE FILES              0
HEURISTIC GFXSCAN ASSETS           0
GENERATED ASSETS TRACKED           0
```

The structured sprite-graphics figure is **7,390**; the stale **7,355** value is
retired as a corpus total and must not be revived. The curated resource library
holds 27,945 files / 100,386,075 bytes with ROM-derived and neutral one-based
names, a deterministic rebuild, and a complete curated-to-raw source map; all 452
maps, 1,559 graphical layers, 452 composites, 3,745 chunks, 297 sprites and
palettes are retained, while shared payloads and repeated direction cells collapse
and structurally distinct pixel-identical resources stay separate.

**Map 19's terrain field:**

```text
MAP 19   handler 0x080088BD   slot +0x1C   record 0x082ABF00
CLASS    static_graphical_terrain_field
140 containers x 0x400 bytes, each a 32x32 plane of 8-bit tile ordinals
container_index = y * grid_width + x  ->  448 x 320 ordinals = 3584 x 2560 pixels
tile source: map 19's own assembled 539-tile character block
ordinals used 1..228 (ordinal 0 unused); destination 0x0600F000 (BG2 map base 30)
```

The unit was established by a **semantic** measurement, not by appearance: exactly
33 of the 228 ordinals select a character-block tile that is more than half water
(lowest share 35 of 64 pixels) while all 195 others sit at 24 of 64 or less, and
the plane-level water fraction falls from 0.6188 as read to a median of 0.0981 over
200 seeded random ordinal permutations. The superseded destination `0x06008000`
and the rejected palette-pixel / false-colour reading survive only as explicit
correction history.

**Composite framing - accepted caveat, do not overstate.** The 452 composites are
deterministic derived resource-library artifacts. They are **not**
runtime-validated, and runtime screen composition is a separate question from
resource completeness:

- **runtime-validated composites: 0**; every `map.json` records
  `composite_placement_model: origin_aligned_descending_addend_bg` and
  `composite_runtime_status: provisional_runtime_capture_unavailable`;
- **map 19's full 3584x2560 composite is DERIVED-UTILITY-ONLY /
  runtime-provisional.** No claim is made that the GBA displays it as one static
  plane, and its two 256x256 companion layers touch only 16,320 of its 9,175,040
  pixels;
- never report "452/452 runtime-validated".

**Map 19's world-map hypothesis is `PARTIALLY CONFIRMED`** and must not be
promoted: that the visible flying-overworld scene uses map 19, and that player
flight drives its viewport, are both unproven. Human visual resemblance is
supporting context only.

**Row stride / display mode.** The `0x40` destination step is compatible with a
4 KiB BG map row representation (size field 2 is 4 KiB in either mode, 64 bytes on
a row). **`BGxCNT` bit 6 is the mosaic bit and does not select affine mode**;
affine-ness comes from the DISPCNT video mode, and map 19's exact DISPCNT mode
remains **unresolved** because the runtime capture never entered map 19. A
recorded negative result: the mGBA 0.10.5 attempt remained at the title screen
(`active_map_ptr` = 0), so its `DISPCNT`, `BGxCNT`, scroll, affine and
`0x0600F000` values are **not** map 19 evidence, and runtime placement is **NOT
VALIDATED**.

**Caller census.** The whole-image Capstone 5.0.7 census stands: **24,226 `BL` +
5,283 `BLX` = 29,509** sites. The former `scan_thumb_bl_callers` matched raw
halfword pairs, so it invented 1,552 call sites (all second halfwords with bit 0
set, which `BLX` T2 reserves), recovered only 16,196 of the accepted 29,509 sites
(54.9%), and resolved 2,568 `BLX` targets two bytes high because it omitted
`Align(PC, 4)`. Enumeration is now by decoding every halfword-aligned window
(`iter_thumb_calls` / `scan_thumb_calls`), accepting only a four-byte `bl`/`blx`
and reporting the encoding, and `resolve_thumb_bl` applies the architectural
alignment. Independently reproduced: 24,226 `BL` + 5,283 `BLX` = 29,509 sites,
set-identical to an unfiltered Capstone sweep (0 false positives, 0 false
negatives, 0 target/kind disagreements). The census is a **static site count**: it
cannot separate code from data and is not a reachability claim. Its sole live
consumer, `logx_sprite_probe.selector_argument_census`, was migrated and its
census is unchanged (162 sites, all `bl`). The research records that cited the
helper carry dated correction notes with re-derived counts (all unchanged: one
caller of `0x08007B78`, none of `0x08008086`, 121 of `0x08000158`, 19 of
`0x0801713C`, and 57 in the remaining case). The narrow second-halfword predicate
covers 24,226 `BL` and 0 `BLX`;
`resolve_thumb_bl` is correct for every `BL` and every word-aligned `BLX`, and
2 bytes high for the 868 matched `BLX` sites at `2 (mod 4)`.

## Desktop application state

The shipped DragonByte Z desktop application renders supported retail maps from
the immutable canonical ROM through the production `render_map` SDK path and uses
those maps as the primary placement-authoring surface. Supported retail maps now
render directly from the canonical immutable ROM through `render_map(rom, map_id)`
with no VRAM capture in production. Runtime and static evidence prove the
delta-coded tile-selector stream, `0x4000` atlas banks, sequential 64-byte 8bpp
tile assembly across multiple containers, frame-zero animation decoding, row-major
32x32 logical layout chunks, and circular runtime screen storage
`(y & 31) * 32 + (x & 31)`. Maps 39 and 40 render deterministically without
production map-ID branches and match the retained VRAM oracle exactly after the
proven circular transform and pinned runtime-state normalization.

Map viewability and editability on canonical Buu's Fury USA rev0: **452 maps
viewable, 341 editable, 111 read-only** (110 dominant grids that use a single
chunk and so have nothing to substitute; 1 map, `map:0008`, with no dominant
layer); 1,516 dominant slots of which 1,093 offer at least two chunks; 4,274
dominant cells of which 156 are null. A semantic Maps workspace spans all 452
known maps as 3 Editable, 265 Partial and 184 Read-only, composes retail and
project-authored placements, exposes known placement to entity to behavior/script
relationships and backlinks, and presents semantic Pending Changes with
project-level Revert. Builds use the normal `validate_project` / `build_project`
path with shared build-scoped reservations and one merged plan.

The Map Browser's Layout mode reassigns one 256x256 chunk cell of a compatible
map's dominant layer to another existing non-null chunk from the same layer,
previews the swap in memory, and saves pending edits to a new ROM. The Grand Kai
proof case (`map:0040` BG1 cell 0, `0x082928DC` to `0x08292A54` at file
`0x00292CA0`) changes exactly two bytes and re-renders with **29,208** changed
pixels, all inside that cell's 256x256 region, the layer's other three regions
pixel-identical; no-op saves are byte-identical.

A ROM this feature wrote reopens: Save As writes a provenance manifest beside the
image, and the Atlas open accepts a modified image only when that provenance
proves it is the canonical image plus declared, policy-legal layout edits
(canonical base SHA-256 and the profile of that image, a matching emitted digest
and byte count, four-byte dominant-layer fields named by their own
`map:NNNN layer S cell C` owner whose replacement the layer already uses
elsewhere, and a reconstruction of the declared old values that hashes back to the
canonical image). Arbitrary modified images, provenance mismatches and manifests
claiming unsupported edits are refused with the reason stated; the canonical image
is still accepted by identity before any manifest is consulted. A derivative
renders its edited layout from the reconstructed canonical bytes and is read-only.
Save As builds at temporary sibling paths, verifies there, and only then replaces
the destination, so a failed emit, verification or publish leaves an existing file
byte-for-byte intact and no temporary file behind; every path a save touches is
refused against the source.

Chunk creation ships: an author duplicates a chunk a dominant layer already draws,
rearranges its 32x32 screen-entry plane using only entries that same layer already
displays, saves it as a project-owned resource with its own `chunk:<name>`
identity, paints a map cell with it, and builds. The authority is
`tools/webfoot/map_chunk.py`. `maps/chunks.toml` holds each chunk as an identity
plus a sparse delta with the entry each cell replaced, and a `maps/layout.toml`
cell may hold either the layer's 1-based ordinal or a `chunk:<name>` identity;
`read_project` refuses a cell naming an undeclared chunk. The template is resolved
against the canonical image only, so painting can never re-point a template. An
authored chunk rearranges existing graphics only (no new tiles, palettes or
imported artwork) and is **map-scoped**.

The Map Browser also ships map growth with supported layer authoring through
`tools/webfoot/map_resize.py` (Phase 2C). Growth is only, top-left anchored: an
existing cell keeps its coordinate and only the cells the growth adds are
initialized, from a 1-based ordinal into the layer's own chunk vocabulary or a
`chunk:<name>` identity. **Shrink is refused** with its reason: the references of
the cells it would remove have not been shown to be safe to drop. A
project-authored layer can also be grown: `[layer]` declares the grid it is
created at and `[resize]` on the same slot the grid it is grown to, as a strict
growth emitting one record, one root-slot write and one reservation. Special
handlers, the terrain-field form, unused slots and zero-dimension records are
refused, and a shared root is refused.

Tile painting ships: in the Map Browser's Layout mode, pick a chunk the current
dominant layer already uses and click or drag it onto a 256x256 chunk cell.
Single-cell paint, drag paint, eyedropper, undo, redo, no-op handling, Apply and
Revert, save and reopen, and build are all delivered on one undo history where a
stroke is one gesture. The editable unit is one four-byte chunk-cell reference
(`record + 0x18`) to an existing 256x256 chunk, a 32x32 plane of 16-bit screen
entries; it is not an individual 8x8 hardware tile, and no surface pretends
otherwise. A cell may only receive a chunk the same layer already uses at another
of its cells, so a single-chunk layer is read-only. The replacement is a fixed
four-byte in-place write, so a build changes only the painted cells, measured at
exactly two bytes over the whole 8 MiB image; no allocation or relocation is
required for it. The retail engine displays the authored cell, proven by a matched
A/B pair after a genuine map rebuild in each run rather than from assembled state:
the authored cell's boundary is visible and the retail frame has no such seam.

The Maps editor's Warps mode lists a map's connections and retargets a
destination, arrival and facing with Apply/Revert on the editor's own undo
history; the Create transition form authors a transition the image does not
contain under the durable identity `map:NNNN/transition:<name>`, composed over a
same-map 566-class template with a new 24-byte record and an expanded pointer
array above the original ROM EOF, built deterministically. Every supported
transition is drawn on the map surface as its trigger region, with a click to
select and a drag of the region as one undoable gesture. Fail-closed limits: the
169-class family (its stored arrival is a scene-relative delta) and a connection
root shared with another map are refused, unsupported forms fail closed, the
unresolved bytes `+0x13` and the low nibble of `+0x10` are preserved and not
editable, the `0x03001A34` selector's non-zero arrival-facing case is untested,
there is no transition deletion, a shadowed stale staged creation has no per-row
discard action (Apply refuses and both values survive), and a transition the
project creates is drawn read-only on the canvas because it has no record in the
image. Runtime proof:
a human-operated mGBA run consumed an authored transition, and the engine's own
loaded record array held the authored entry above the original image's end.

A project mutation and a session change are separate lifecycles.
`on_project_mutated()` re-reads only what a project can change and retains staged
map-layout edits, the placement undo history, unapplied palette state and typed
dialogue state, and the Maps editor re-asserts its own mode so the mode strip and
the editor cannot disagree; `on_session_changed()` is reached only by a genuine ROM
or session replacement, resets session-bound state and follows its editor into
Browse. A project mutation leaves the placement undo stack intact and a session
change clears it, with the shell's Edit menu routed to the surviving stack. Dirty
work is never discarded silently: opening another image and closing the window both
ask first, gated on the same unsaved-edit count the title and status bar advertise,
and there is no auto-save. Expected GUI and domain failures are contained where
they are reported: the ROM open path converts the SDK's declared failure families
into the session's single error type with the SDK's own reason, so an expected
failure is never a dead click, and a session transition contains an expected
failure per panel, because an exception raised inside a slot reached through a Qt
signal is printed and swallowed and never reaches the emitter. A malformed
decoded-text artifact is reported as an atlas build error rather than leaking a
bare JSON decode error.

The palette and editor pathological work is removed: a full repaint now costs one
whole-project parse instead of 257, and a 256-swatch repaint completes in
**0.433 s** against **104.896 s** before. Those are supporting measurements, not
test assertions; the primary evidence is structural and call-count based. The CI
test job installs the shipping GUI and research dependency set
(`.[dev,workbench,research]`, with a declared `research` extra for capstone) and
runs the required GUI surface headlessly; a required GUI module that stops
executing fails the CI job rather than skipping quietly, and whole-module
collection collapses went from **17 to zero**.

The desktop visual direction is a light / mid-light editor with a pink product
identity derived from Buu's own in-game sprite, not from the game at large. The
canonical source is **`graphic:0903` (32x64) with `graphic:0904` (64x64)**,
identified by scoring every decoded graphic on carrying all four of the
character's design colour families at once (pink skin, violet cape, white mantle,
dark outline) and then confirmed by rendering. The shipped direction uses four
steps of Buu's pink where a grey ramp would be used: `#f2ccdf` shell, `#eebfd6`
chrome, `#a81560` interaction, `#6d0c3c` high-contrast edges. The work surfaces
are the sprite's white mantle; type and borders come from its outline ramp; the
belt gold is a rare secondary accent. Selection uses the interaction step rather
than a tint of the shell, so it cannot be mistaken for chrome. Two roles are
documented exceptions because the sprite cannot supply them: `success` (green) and
`research` (violet).

Structure, as accepted: menus `File / Edit / View / Tools / Help` and one compact
strip; four primary destinations **Atlas / Inspector / Maps / Graphics**; Maps
consolidated into one editor with **Browse / Layout / Objects** modes and a
contextual inspector that no longer offers a second mode selector; Build and Run
are project actions opening content-sized dialogs, not workspaces; the Graphics
palette is compact bank blocks and there is one selected-sprite preview, with the
animation stepped and played in it. The shell has one physical status bar, and
project status is authoritative: `no ROM`, `no project`, `not validated` /
`not built`, and `stale` only where a result existed and a change invalidated it.

One measured performance correction: `indexed_pixmap` applies index-0
transparency as one bulk byte translation feeding `QImage.setAlphaChannel`. The
first implementation walked `pixelIndex(x, y)` per pixel, which cost a Qt call per
pixel and blocked the UI thread because the Objects-mode canvas shares the helper:
a representative 3584x2560 (9.18 Mpx) composite took **~3.3 s** by that path
against **~0.04 s** shipped. Rendered output is identical in every case tested
(`QPixmap` bytes, PNG bytes and scaled bytes), so exported PNG content is
unchanged. The figures are one machine's measurements, not a benchmark guarantee.

Four screens had been drawing a status sentence twice (Atlas, the Map workspace,
the Scene editor, and the Graphics status contradiction that started it); all are
closed, and each is guarded by a test proven to fail when the defect is restored.
A status-duplication probe walks nine screens for the whole class.

## Resource library curation

The canonical raw resource library is curated into a separate human-browsable
resource pack with a deterministic rebuild and a complete curated-to-raw source
map. The curated library holds 27,945 files / 100,386,075 bytes with ROM-derived
and neutral one-based names, no underscores and no generated prose. The raw library
(86,444 files; 85,981 PNG + 463 JSON, 0 other extensions) is never written and
stays byte-for-byte unchanged. The merged-code export is byte-identical to the
accepted isolated library (86,444 rows, 0 added / 0 removed / 0 changed). Against
the previous canonical base the delta is exact and bounded: **73 PNGs added, 0
PNGs changed, 0 unrelated PNGs changed**, plus the 452 `map.json` records that
gained the placement fields and `metadata/maps.json`, so every newly written
artifact is a map layer or composite the map-handler correction recovered and no
existing image changed.

## Text format

Buu's Fury text is **UTF-16LE**, terminator `0x0000`, pool
`0x0005792C..0x0006BCE6` (82,874 bytes), pointer table `0x0006BCE8` with
**1,534** strictly ascending, duplicate-free entries tiling the pool
**exhaustively**. Control grammar: `0x0008` plus operand (100 occurrences; operand
semantics UNKNOWN, preserved opaquely) and `0x000A` newline (24); `%d`/`%s` are
in-band ASCII. The pool base has exactly **one** inbound word-aligned reference
(the table); the table base has **51**, so access is by index. Exactly **5**
coincidental address matches exist, all in compressed graphics data, CANDIDATE and
fail-closed. 153 texts repeat but never share storage. No custom character table is
needed; the upstream `.tbl` is redundant and its `00=space` row is wrong. All
1,534 re-encode byte-identically over the full extent; no-op extract/build still
reproduces canonical SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. Canonical
text **growth remains blocked**: no verified free region is large enough, and free
space is never inferred from fill patterns. The growth path is proved
synthetically, and a 1,535th string would need the pointer table grown and its 51
code references rewritten.

A type-0 dialog renders text on screen, and the text is that same table
`0x0806BCE8`. Chain: `dialog -> native slot 178 -> 0x0802BFBC -> text table
0x0806BCE8`, and `-> 0x0802BECC -> OAM sprite text`. The family was chosen by
measurement, not by operands that looked like text ids: each of the **107 native
slots** the 236 type-0 dialogs use was asked whether its call graph reaches
`0x0806BCE8`, and **exactly one answered yes** (slot 178, depth 1, 8 dialogs); the
other 106 were excluded by that scan, which a test re-runs and which fails if a
second slot ever qualifies. The ranking that produced the candidates reproduces a
known result at the top (slot 29, the proven save-flag SET). Handler
`0x08003030` **pops three, index deepest** (read from the handler at
`0x0800303E`/`0x0800304C`/`0x0800305A`, never inferred from operand position);
`0x0802BFC0` `ldr r1,=0x0806BCE8` then `0x0802BFC4` `lsls r0,#2` / `ldr
r4,[r1,r0]` is byte-for-byte the access shape proved at `0x0801F85E` for the item
consumer; `0x0803FFE8` walks that pointer as UTF-16LE halfwords to NUL summing
per-glyph advance widths, so the pointer is consumed *as text*; `0x0802BFEC` emits
**8-byte OAM entries** (8-bit Y, 9-bit X, 32-pixel step) and `0x0802BF8E` blits
glyph tiles into `0x06010000`, the GBA OBJ VRAM base, while `0x0802BF5E` centres
the string on the supplied X. **Seven dialogs carry literal indices**: 290..298 to
text 1525..1532 to `"Match 2 Fight!"`..`"Match 9 Fight!"`, all at **X=120, the
exact centre of the 240-pixel screen**.

The Buu `event_resource` records behind table **`0x0879B704`** are decoded, and
they are **scripts for the VM the toolkit already models**. The engine's own term
is **dialog**, read out of the shipped image rather than inferred: consumer
`0x0800327E` reaches `0x08004098`, which fails an assertion carrying `"Expected
dialog to start with a code block"` and the source path
`T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp` line 60. That is a
**naming** fact only; what a dialog does on screen beyond the rendering above is
otherwise unclaimed. The interpreter `0x08004038` dispatches through
`0x080554C0`, whose **31 handlers (0..30, 17 absent)** are byte-for-byte the
`_BUU_HANDLERS` tuple already in `script_specs.py`; opcode 1 is the same
signed-magnitude varint and opcode 2 indexes the same native table `0x08055098`.
**No second VM exists.** The two consumer families do not share a downstream
worker: `0x080030F8` (slot 182, pops 2) reaches `0x08012588`, a generic
constructor (allocs 8, vtable `0x08049D18`, queues `0x03002A58`), while
`0x0800327E` (slot 216, pops 3) reaches `0x08004098` and runs the record. **Two
record fields promoted, because only two are read before branching**: `+0x00` a
pointer the consumer dereferences (521 of 522 land in the pool), and dialog `+0x02`
the type byte branched on at `0x080040BA..0x080040C2`. Type distribution
**0:236 / 3:2 / 4:141 / 5:139 / 6:2 / 7:2**; type 0 runs a code block at
dialog+0x03, type 4 expands via `0x08049120`, an ARM veneer to IWRAM `0x03000040`,
so it is declared **UNSUPPORTED rather than guessed**. **No fixed record format**:
two whole-corpus schemas were tested against all 522 records and both rejected
rather than shipped ("pointer run then count word = n-1" holds for 190, "pointer
run then NULL" for 463; the four reachable records agreeing was a coincidence).

The four map-reachable dialogs (`event_resource:0393/0506/0508/0509`, all type 0)
are save-state and scene-control logic: they do not present text, and they do not
reach another dialog. Each of the **13 native slots** those four dialogs call
(0, 4, 5, 26, 29, 55, 100, 107, 119, 120, 138, 186, 187) was walked as a whole
call graph to **depth 10**, slot 119 alone expanding to **70 nodes**, and none
reaches text table `0x0806BCE8` or dialog table `0x0879B704`, unchanged at depths
4, 6, 8 and 10. The same walker reproduced all three known positives: slot 178
`0x08003030 -> 0x0802BFBC -> literal@0x0802C06C` (text), slot 182
`0x080030F8 -> literal@0x080031C0` and slot 216 `0x0800327E -> literal@0x08003444`
(dialog). A correctness note that mattered: **opcode 0 is `push_byte`, not a
native call** (only opcodes 2 and 3 dispatch natively), so counting it would have
invented slots out of pushed constants. Save flags resolved to all three
operations: `0x08004364` **ands = TEST**, `0x08004380` **orrs = SET**,
`0x08004396` **bics = CLEAR**, sharing one bit-addressing shape on
`[0x08054FBC + 0x14]`.

The `0x0879B704` table is READ: 522 ascending pointers, extent
`0x0879B704..0x0879BF2C`, pool `0x0877C5A4..0x0879B704` tiled **exhaustively at
127,328 bytes** with zero gap or overlap, sizes min 16 / max 3,168 / 166 distinct,
all word-aligned. Only the **236 type-0 dialog records are ROUND_TRIP**; the
remaining **286 are structurally classified by type byte and explicitly refused**.
Save flags 266/267 SET, 31/31 dispatch handlers, 236 type-0 ROUND_TRIP / 10,263
code bytes / 286 refused. Compressed text `0x0879BF2C` is untouched.

Lifecycle: `construct -> queue` is established by three independent paths, while
`wait` and `close` were **not** found and are **not** claimed. Slot 139, the most
common terminal call (27 dialogs) and so the strongest lifecycle candidate, is a
**bitfield condition selector**: `0x08008AA0` filters a list through evaluator
`0x08004784` and pushes passers, with no input poll, no UI write and no font
routine, so `wait_for_input` is refused as a context-guessed name. Slots 48/83 are
construct-and-queue, slot 83 appending via `0x0801936A` (a linked-list tail walk).
Slots 100 and 107 allocate `0x0803D5B8`, install a vtable and append via
`0x0801936A` to `[0x08054FBC + 0x1C]`, the same shape as `0x080030F8` and slot 83
but a different destination with no identity claimed. Slot 187, called by dialogs
506/508/509, reaches CLEAR at `0x08003358`, so the older claim that `0x08004396`
is "unreached by this corpus, so only SET is claimed" is **superseded**; it is
recorded as a separate `dialog_save_flag` contract entry, kept apart from the
event-level `save_flag` because a different consumer proved it. Slot 119, the
dominant call in 508/509, pops five, matching `push_many(5, ...)` in both
callers.

### Dialogue handles and variable-length dialogue

The handle codec has one implementation. A packed dialogue handle is: **selector
in bits 0-5, decoded start in bits 6-20, decoded length in bits 21-31**, both
offsets in halfwords, **no reserved bits** (6+15+11 = 32). It was re-derived from
the retail consumer at `0x08012240`, where two independent implementations,
`0x08012230` and `0x080122B4`, agree, and corroborated structurally by the
consumer's `0x10000` scratch buffer (the 15-bit start field's 65,534-byte maximum)
and its `0x1008` object whose inline string plus terminator is exactly the 11-bit
length field's 4,094-byte maximum plus two. `DialogueHandle` exposes `decode` /
`replace` / `encode`, and no writer path shifts bits itself.

The container's layout policy is measured, not assumed. Selector 1's decoded
container holds 447 distinct records with **absolute** decoded starts, 410 of 446
adjacent pairs consecutive, and **exactly one record intersects the edited span
`0x132..0x152`, the target itself**. Growth therefore splices at the record's own
end and shifts every record at or after it; a container whose records cross the
edited span is refused with that reason rather than reinterpreted. A packed handle
is read only from a record word whose byte `+0x02` is the dispatch key `0x05`
(runtime-proven). Selector-1 words that merely *unpack* plausibly number **46,298
distinct values over 59,491 occurrences**, of which only **143** are ever read as
handles; rewriting the rest would corrupt Thumb code.

An existing compressed-dialogue record can be replaced by text of a different
decoded length, and the durable handle is authored rather than frozen. Replacing
`goku-greeting`'s retail `Good luck, Goku!` (32 decoded bytes) with the 72-byte
authored line re-authored the record's handle from `0x02002641` to `0x04802641`
(same decoded start `0x132`, new decoded length), grew the decoded container
65,474 to 65,514 bytes, rebuilt the layout for **444 affected records** (the
edited record plus **443 displaced**), and repointed **470** handle words (467
displaced-record references plus the edited record's 3). Of the 443 distinct
superseded handles, three values also occur 15 times outside the engine's
handle-carrying structure; all 15 are data and all 15 were left untouched, so the
reference inventory is ownership-filtered, never a global word replace. **446 of
447** records decode byte-identically afterwards, the only difference being the
authored record. The container repacked 16,856 to 17,952 bytes and the production
allocator placed it at file `0x00800000` / ROM `0x08800000`; the selector word at
`0x007B5B68` was repointed, the writer authorized the appended write from the
allocator's own provenance, and the existing manifest recorded the edit as
`dialogue_edits`. The derivative is 16,777,216 bytes, SHA-256
`dbeba9abc58db5343bd4a7c004207636c8fa6932b0f9527a866fe09ee2aba036`; the canonical
ROM is unchanged. Runtime proof: the retail consumer at `0x08012240` read the
re-authored handle `0x04802641`, selector 1, entry `0x08800000`, and the retail
dialogue box displayed the complete line wrapped as
`Hot take: SSJ3 is the / worst form imo`, 36 characters, no truncation.

**Three different capacity numbers, kept apart.** The length field ENCODES 4,094
decoded bytes and the start field addresses 65,534; the toolkit's own
container-decoder safety limit is 64 KiB of decoded output, which a retail
dialogue container already fills to within 62 bytes, making this target's
production ceiling **94 decoded bytes**; and the ENGINE-PROVEN maximum is **72
decoded bytes**. Nothing claims the field's arithmetic maximum is runtime-safe.
Because the decoder limit is the stricter of the two, a displaced record's shifted
start cannot overflow the start field while the limit holds.

**Two corrections retained rather than smoothed over.** (A) An intermediate
conclusion that no key input reached the emulated core was **wrong**, and the
comparison behind it was flawed. Measured against a no-input baseline, mGBA's
single-key API works (`emu:addKey(C.GBA_KEY.START)` opens the STATUS menu,
RIGHT/UP/DOWN walk the player, LEFT held from a fresh boot skips the intro, and A
pulses press START at the title) while the plural mask form
(`emu:setKeys`/`addKeys`) delivers nothing. The greeting is an interaction rather
than something the fixture replays: it was consumed automatically in only one of
twenty identical runs. (B) For this consumer hit the `STRING` row is **not** the
displayed text (`decoded_bytes=14`, non-text bytes); the deferred read is only
reliable for a heap object, so the visual capture is the dialogue-content evidence
and no artifact claims otherwise.

## Script VM

Buu's Fury has a real bytecode script VM: interpreter `0x08004038` fetches one
opcode byte, indexes dispatch table `0x080554C0` and calls handlers through the
`__call_via` veneer, terminating on the null slot `0x11`. The table holds
**exactly 31 slots (0x00..0x1E)** because slot `0x1F` onward is UTF-16 text, a
measured bound. A ROM-wide census of contiguous Thumb-pointer runs finds only
**five** candidate dispatch tables; three belong to this VM, so Buu has one VM,
not several. The architecture matches the LOGII VM (abstractions reused) but the
**encodings differ**, all 31 opcodes re-derived from Buu handler code with nothing
transferred: branch displacements are **two-byte big-endian** (not one byte),
measured from the **pre**-operand cursor (not post), `0x1C` **subtracts**, and
slot `0x1E` is a real handler.

The selected Buu corpus **static40**: one walker (`0x080141EE`, table
`0x08720564`, bound `cmp r6,#0x28`) yields **40 records / 120 roots**, all
non-null, distinct and strictly ascending, over a **548-byte** pool at
`0x08720340` ending exactly where the table begins. **ROUND_TRIP**: 328
instructions, 120 terminators, decode coverage **548/548 bytes with 0 uncovered**,
0 failing roots, re-encode byte-identical and enforced inside `load_scripts`. The
honest bound is recorded, not glossed: the corpus uses only opcodes whose widths
are identical in both games, so LOGII's grammar also tiles and round-trips it; the
round-trip proves boundedness and losslessness but does **not** discriminate the
Buu branch contract, which the handler disassembly does. An earlier draft claiming
the tiling confirmed *every* operand width was measured, found wrong, and
corrected.

The LOGII static43 script bytecode: 86 entry slots, 86 unique blocks, 323
instructions, six encountered opcodes, 539 bytes at file
`[0x006D66C0,0x006D68DB)`, exhaustively identical. Its dialogue path remains
DISCOVERED; that corpus has no fixed text consumers.

A static Buu record owns a script. All 29 interpreter call sites were censused by
the instruction that last defines the cursor register: 3 static, 2 static-record,
1 unreferenced dead proc, 23 runtime-object or caller-register. Selected site
`0x0801E182`: proc `0x0801E164` gates on owner byte `+0x00` bit 1 then interprets
`[r0+0x30]`, and both its callers form `r0` as `table + 52*index` over base
**`0x083BD2F8`**, which is loaded from **twelve** independent literals ROM-wide; a
thirteenth site `0x0801E1FE` reads `table + 52*index + 0x30` and tests it against
zero to set a capability flag. Site `0x0800F67A` was inspected and rejected
because proc `0x0800F62C` has **zero inbound references of any kind**. Owner
identity was established by its own text, not an upstream name: 83 item records of
52 bytes, text index `0x028E` decodes to `"Miso Soup"` and `0x0291` to its
description. The `item_use` family reaches ROUND_TRIP: **23 roots** (of 83 owners;
60 have a null `+0x30`), all distinct and strictly ascending, **86 blocks, 351
instructions, 703 bytes** at `0x083BBBB0..0x083BBE6F`, **703/703 covered with 0
uncovered**, 0 failing roots, re-encode byte-identical. It uses **9 distinct
opcodes** against static40's 5. The branch contract was promoted from
handler-only to corpus-backed: this corpus contains **42 branches** (21 x `0x12`,
21 x `0x13`); round-trip still does not discriminate, but under LOGII's one-byte
reading all 42 branches have displacement 0 and jump to their own fallthrough
(65 blocks).

Text references were promoted on proof: `0x0801F818` loads the verified text
pointer table `0x0806BCE8`, and `0x0801F85E..0x0801F862` reads record `+0x02`,
shifts left by two and indexes it, a real dereference; all 83 records carry four
in-range decodable indices (332 total). static40's `0x0266..0x028D` stay
**CANDIDATE** deliberately: item ids begin at `0x028E` immediately after them, and
adjacency to a proven range is not a consumer. Eight native handlers resolve
structurally, none named; `0x080007B7` does not occur here. Under Buu's two-byte
big-endian reading all 42 branches are real jumps (86 blocks, 84 edges, 0 unknown
targets, 0 off-boundary), while `0x1C` remains handler-derived only because no
supported corpus exercises it. Attachments are exposed at item level only; no map,
placement or placement-type attachment exists in this family and none is claimed.
The two families are declared separately, not merged, because they are enumerated
from different static owners.

**Authoring a new script body.** A production assembler,
`script_vm.assemble_source`, encodes only `none`/`u8` operands and refuses branch
(`be16`) and varint (`sm7`) widths **by name**; it is deliberately not a compiler.
An authored body `00 54 00 4B 07 14 11` is
`push_byte(0x54); push_byte(0x4B); add; pop; terminate`, all five opcodes already
CONFIRMED_ROM, with no branch, native call, dialogue, flag or variable. **Three
bytes was measured and rejected as a novelty claim**: `00 2A 11` occurs 3x in
canonical data, `00 37 11` 4x, `00 5B 11` 5x and `00 7D 11` 2x, while the
seven-byte body occurs **0 times** in the full 8 MB image, so the strong claim
("the content is new") is available instead of the weak one ("the address is
new"). The authored descriptor `{0x0800421F, 0x087EA428}` at `0x087EA420` is
serialized by the production `DescriptorRecord`, and its payload is asserted equal
to the allocated script address read back from the built ROM, because the correct
handler alone is not sufficient. Runtime observed three executions on map 40, each
with trampoline `pc 0x08004220`, `r0 = 0x087EA420`, `[r0+4] = 0x087EA428`, then
interpreter `pc 0x0800403A` with live cursor `0x087EA428` and the seven bytes read
back from that cursor equal to the authored body. The cursor check is the
discriminator that watching the trampoline alone cannot supply once the script
itself is the authored artifact. Liveness channels fired on map 39 as well, where
the authored entity does not exist, so the instrument proved itself on ground
where the result cannot occur.

**Native gameplay-effect handlers.** A visible authored behaviour is proven: the
bounded evidence pass selected native slot 178, because canonical dialog 290
contains the unique `push_many(3,1525,120,65); native_stack(178)` invocation at
file `0x78B5A7`, handler table pointer `0x08003031` / entry `0x08003030`. The
narrow semantic `show_centered_sprite_text text:NNNN X Y` expands only for the
verified Buu profile and assembles through the production VM codec. The authored
body at `0x087EA428` is `1D 03 97 6A 81 70 81 52 02 B2 11` =
push text 1525 / X120 / Y105, call slot 178, terminate; it has **zero
occurrences** in canonical Buu. Runtime captured authored descriptor
`0x087EA420` to authored cursor `0x087EA428` to native opcode handler
`0x08003CC0`, live operand cursor `0x087EA431` / slot 178, selected handler
`0x08003032`, stack depth 3 and exact arguments 1525/120/105, and the frame
visibly showed **MATCH 2 FIGHT!** centred at the authored Y=105. A
canonical-argument positive control rendered the same banner at canonical Y=65,
and the same authored entity with the native opcode removed executed but showed no
banner. Gameplay-effect opcodes route through `native_stack` (`0x02`) and
`native_pop` (`0x03`), both of unknown semantics, with table `0x08055098` holding
283 handlers with no established meaning; one handler suffices for an intentional
visible effect.

## Placement format

The placement corpus and its shared type structure:

- All **1,295 placements / 215 maps / 41,440 bytes** retain their supported
  extent and position-only edit.
- **101** stable shared type selectors (corrected from an earlier 111) select
  `0x08711274 + 28 * selector` through wrapper `0x0800FD55` / constructor
  `0x0800F68C`, CONFIRMED static LEVEL 2.
- **95 types / 1,284 placements** link to existing enemy-stat identities and
  round-trip **2,660 bytes** through the existing codec; six selectors (141, 142,
  146, 147, 148, 149), used by 11 placements, remain reference-only with no record
  extent or enemy claim.
- The common graph has **4,100** confirmed references, including explicit
  read-only index encoding.
- Anchors, classified and reverse references, profile-only free space,
  deterministic allocation, atomic batch relocation and provenance are proved
  synthetically (`0x100/8 -> 0x208/39`); old bytes are preserved and candidate
  references block.
- Opaque slot accounting is **112 arrays / 596 slots**, typed **35/89**; 108
  unreachable and 168 non-conforming remain excluded.

The production variable-length placement codec reaches **1,442 records / 240 maps
/ 240 runs**, preserving all **1,295 legacy IDs** and adding 147. The descriptor
model has **82 shared records**; the owned `placement_descriptor_event` family
exposes **57 placements / 10 maps / 25 roots / 202 instructions / 514 bytes**,
including all three canonical `0x1C` branches. Exclusions (7 unreached records, 76
unreferenced descriptors, 19 unowned roots) remain excluded, and no text consumer
or gameplay-handler semantics are promoted. Opaque slot accounting corrected to
**108 arrays / 556 slots**, typed **35/89**; the legacy view retains 112/596. An
exact position edit at file `0x72908` (`3C -> 4C`) passes.

Project v1 distinguishes named AUTHORED_CLONE declarations from extracted
placements; exact canonical reconciliation and position WRITE are preserved, and
the production codec serializes clones including supported child counts 1..4. A
map 0010 example is 2 canonical + 1 authored record, 96 body + 12 pointer bytes.
Build stops at the non-relocatable run and the unknown engine
count-termination and suffix-ownership contract, before allocation; synthetic
capacity alone does not authorize the reference rewrite. AUTHOR_NEW representation
is available, materialization is not.

### Verified capacity and canonical AUTHOR_NEW materialization

**Written ROM capacity: yes. Canonical AUTHOR_NEW ROM materialization: yes**, for
the one declared region; runtime validity is not claimed for it generally.

The verified region is `[0x007EA400,0x007EA500)`, **256 bytes**, evidence class
CONFIRMED, declared in both `config/roms.yaml` and `tools/webfoot/data/roms.yaml`
and not enlarged beyond that proof. It is a carve of the previously proposed tail,
not that tail: `[0x007B89A8,0x00800000)` (also written `0x7B89A8` to `0x800000`)
stays REJECTED. Seven checks pass on
canonical bytes (FF fill, 0 known inbound references, 0 known overlaps, 0
candidate targets at any alignment including interior bytes, 0 candidate sources,
clearance 1,717 below / 2,816 above against a required 1,024, clear of the
header). **Exact allocation demand, measured by instrumenting `allocation.allocate`
through the real transaction: 44 bytes** (authored body 32 bytes alignment 4, then
expanded array 12 bytes alignment 4; two `allocate` calls, 44-byte occupied span,
no alignment loss). Body first is a hard ordering constraint: the array payload
must contain the body's address before the array is written. An earlier 108-byte
proposed request is **superseded**: `AuthoredRun.allocation_request` is a
single-block proposal (3 pointer slots + 3 whole bodies) the build never issues,
and the two canonical bodies are re-pointed, not rewritten. The 108 figure is
pinned by test so it cannot become the sizing rule.

**All 516 historical candidate references remain unresolved and unwhitelisted;
none is waived**, and candidate-blocking policy is unchanged globally. Their 475
distinct targets do not tile the tail (474 candidate-free intervals exist, largest
4,788 bytes), so the region is carved so none overlaps it; separately measured,
**zero** of the 516 are sourced inside the tail. Four positive controls were all
REJECTED, each on its named check: a declared header (`bounds`,`fill`); the largest
declared table `text_pool` (`known_overlap`); the most-referenced target `0x00FD55`
(`known_inbound`); and a window at the real candidate `0x7B8E2C`
(`candidate_target`). The last is decisive: it is FF-filled bytes inside the same
tail and is still rejected, so **FF padding appearance does not imply free
space**. Tests pin that a blinded scanner fails its own control and that a control
failing for the wrong reason does not count.

Canonical materialization: body at file `0x7EA400` (32 bytes), expanded array at
`0x7EA420` (12 bytes), disjoint, both inside the declared region; canonical slots
carried byte-for-byte (`fc280708`, `1c290708`); the third slot holds `0x087EA400`;
owner pointer `MapEntry+0x14` at `0x08E524` rewritten `0x0807293C -> 0x087EA420`;
derived count `MapEntry+0x04` at `0x08E514` `2 -> 3`. **Exactly 48 bytes changed**,
all intended. Generated ROM SHA-256
`ac7caf10c7d08e3d7cb7ab3637ddad51205e1668294ee6061e987529fee3a57c`. Repeated
builds are byte-identical. A `Maps.changes()` defect was fixed rather than worked
around: it re-encoded every MapEntry record and every object array, so for an
authored map it re-encoded the record at its canonical count and owner pointer and
the array at its canonical home, both contradicting the expansion and raising
`OverlappingChangeError`. `Maps.changes` now takes `authored_maps` and yields both
structures for those maps to the expansion, which emits the MapEntry as one
record-wide change with relocated pointer and derived count folded in; the
MapEntry has a single writer, `MAP_FIELDS` still refuses `*_count_raw` as directly
editable, and maps outside that set encode exactly as before.

Two further measured allocation demands, each a property of its target rather than
a constant:

- An authored placement with an attached behaviour script: **71 bytes** (32
  placement + 8 descriptor + 11 script + 20 array), leaving **184 bytes** in the
  verified 256-byte region; generated ROM SHA-256
  `bbd0bbbe1f01b4d715b89bb20a22f63276e36ec4fd2dc443e34ae3b99880ff35`, **75
  changed bytes**.
- A new behaviour script attached to a map-40 placement: **67 bytes** (32
  placement body, 20 expanded array, 8 descriptor, 7 script; bodies first then
  array), leaving 188 of 256. An earlier 59-byte claim is **superseded**: the
  12-byte array measured on map 10 was that map's 2 canonical slots, while map 40
  has 4, so its array is 5 slots x 4 = 20. Generated ROM
  `3f32b629925b737074f3e18d76724a90d927f3e157dd396d4a757fb324e6490c`, **71
  changed bytes**.

## Capacity, allocation and above-EOF writes

The canonical 8 MiB retail image partitions into OWNED 3,037,940 / REFERENCED 87 /
**VERIFIED_FREE 256** / UNKNOWN 5,350,325 bytes. 115 candidate runs totalling
23,595 bytes were identified and remain **candidates, not promoted**; production
free space is still the single 256-byte window above. A 16 MiB generated image is
engine-proven, giving **8,388,608 bytes of raw physical expansion**. Expanded
storage is not universally usable: it is global physical storage plus
domain-specific addressability.

Domain reachability is mapped for 16 of 16 domains: **13** can *encode* an
above-EOF address; **0** were promoted on static inference alone, because not
finding a bound is not proving there is none; **1** is runtime-proven above EOF
(`PACKED_STREAM` / compressed dialogue).

There is one production allocator, `tools/webfoot/allocation.py`: semantic request
kinds, explicit allocation records, a deterministic `lowest-aligned-first-fit/v2`
policy, collision- and alignment-safe, with `UNKNOWN` / `OWNED` / `REFERENCED`
refused, `VERIFIED_FREE` and explicitly authorized generated expansion permitted,
candidate runs never consumed, and domain range policy enforced. Expanded writes
require a matching `GeneratedAllocationProvenance`: **no allocation record, no
expanded write**, and a larger file authorizes nothing on its own.

**Real above-EOF proofs, each scoped to the span the engine exercised:**

- The retail `goku-greeting` compressed-dialogue container was rebuilt and placed
  by the production allocator at file `0x00800000` / address `0x08800000` (17,932
  bytes), authorized by the production writer, emitted by `build_project` with its
  default sibling manifest, and repointed by the engine-visible selector word at
  file `0x007B5B68`. mGBA 0.11 recorded the retail consumer at `0x08012240`
  reading handle `0x02002641`, selector 1, entry `0x08800000`, and the dialogue box
  displayed the authored line. Derivative SHA-256
  `3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb`. **The
  17,932 bytes are the span the engine exercised in this proof, not a global
  capacity maximum.** Reopen reconstructs canonical-base identity, restores the
  allocation as a reservation, and without that reservation the allocator does
  re-select the span, so the reservation is load-bearing.
- A 408-byte authored chunk body was placed at file `0x00800000` / ROM address
  `0x08800000` on a 16 MiB derivative (SHA-256
  `5c51ece754fbe7b3d54b872a94fbe4404dfa4b7e350d3c11f26c5a6c6f0675a0`), and
  **exactly three bytes changed in the canonical region**
  (`0x00292CA0..2`, the painted cell's pointer). `AllocationKind.CHUNK_BODY` is the
  first allocating kind whose pointer is a full 32-bit address; the
  generated-image policy is derived from the **union** of every allocating
  domain's spans so two domains can both expand. The engine's own live layer
  record held retail `0x082928DC` at 8,388,608 bytes against authored `0x08800000`
  at 16,777,216 bytes, and its own uploaded tilemap showed **BG1 differs in 593 of
  1,024 screen entries (rows 1-31, columns 0-30)** carrying the authored mirror
  ordering, **while BG0, BG2 and BG3 are byte-identical**, which rules out a
  camera shift. Matched frames differ in 11,429 of 35,264 counted pixels (32.4%),
  over the whole visible area.
- `AllocationKind.LAYER_RECORD` is placed through the production allocator with an
  explicit `Addressability.EXPANDED_ONLY`. On map 40 BG0, grown 1x1 to 2x1, the
  matched runtime pair sits at **camera x = 79 in both runs**: 1,024 frame pixels
  differ and all of them lie inside the added cell's band with zero outside, the
  BG0 screenblock gains 32 entries, and BG1 is byte-identical. The live BG0 slot
  went from `0x082928C0` at 1x1 to `0x08800000` at 2x1 with the added cell
  `0x087EA400`, and the clamp rose 88 to 271; the authored camera reached **158**,
  70 pixels past retail's hard clamp. The authored-layer half is independently
  proven: map 39's BG0 went from `0x080707FC` at 0x0 with 0 drawn entries to
  `0x08800128` at 3x2 with **223**, `DISPCNT` and `BG0CNT` identical in both runs.
  The retail engine's own live layer records held `0x08800000`, `0x08800030`,
  `0x08800128` and `0x08800158`, all above the 8 MiB image, and read their grids
  and chunk windows. The claim is scoped to the map/layer reference domains
  actually demonstrated.

**Debt closed:** a 16 MiB derivative was not reopened by the shared derivative
verifier, which reconstructed and hashed the canonical image from the whole file;
this was pre-existing and shared with compressed dialogue since ROM-EXPAND-001.
`DERIVATIVE-16M-REOPEN-001` fixed it: the verifier now checks only the canonical
span stated by the profile identity, so a valid expanded derivative reopens.
`tests/unit/test_authored_image.py:500` and
`tests/unit/test_map_layout_provenance.py:172` assert it.

**The runtime rebuild rule.** A savestate restores emulated RAM and VRAM,
including the already-assembled background, so the engine never re-reads the map
from ROM under a state load. Two different ROMs loaded with one state produce
byte-identical VRAM and screenblocks. The engine builds a map only on entering an
area, so the rebuild is per run, never per state:

```text
state -> leave the map -> re-enter the map -> let the rebuild settle -> capture
```

The capture guard refuses to capture unless it observed the leave, the return,
the settle, and the target map still active. Any future "does a ROM-side map or
graphics edit reach the engine" question starts from this rule. The live
screenblock is **not** the chunk plane verbatim: its entries match neither the
retail nor the authored chunk entry-for-entry at a 32-entry stride or at the
layer's 64-tile stride, so a VRAM dump cannot currently be decoded back to a chunk
identity and the engine's map-upload transformation is **UNKNOWN**. This belongs
to the ROM to charblock/screenblock blocker.

## Combat, damage and rewards

### Behavior controller and reactions

State-machine primitives: `0x0800AA9C` push (guards `depth < 5`), `0x0800AA4A`
replace, `0x0800AAD8` pop, `0x0800AB0C` update, each taking a controller pointer
and selector index. A controller holds depth at `+0x04` and 8-byte
`{node, table_slot}` entries at `+0x08`; the **state-table base is `0x0870F514`**,
stride 8. Nodes are `{entry, update, exit, param, child, sibling}`.

**Correction:** `0x0801920F` is a generic clip-entry handler shared by ~170
selectors, so executing `0x0801920E`/`0x0801920F` alone does **not** establish
HURT semantics; any earlier claim resting on that PC alone is superseded. Wolf
selector 436 has primary node `0x08706BC4` with reaction node `0x08706BA8` as its
child; wolf selectors are contiguous 434-439. Reading `wolf+0x238` per frame
reproduced these selectors with zero stops, confirming the table at Level 3.

**Correction:** the player has **no** behavior controller. A structural probe over
every 4-byte offset of each actor matched only `wolf+0x238`. Any interpretation
assuming a player controller is superseded.

A landed hit pushes a reaction state (depth 1 to 2), coinciding with authoritative
HP decreases and not observed on unrelated events: push 708/pop 732 and push
1241/pop 1265, both **24 ticks**, the canonical low-perturbation duration. An
earlier 28-tick observation is retained as historical evidence from a
three-breakpoint run and is **superseded and explained** by that instrumentation's
pacing perturbation.

`T_ATTACK_ACCEPT` is player object `+0x04C`, the current animation-clip pointer.
`0x0851C618` is idle; `0x0851C680`, `0x0851C6C0` and `0x0851C6A0` are punch clips
observed only with A held. An accepted punch is idle to punch clip with A held;
`+0x050` and `+0x014` move with it. A capture recorded 154 accepted punches:
minimum interval **20 ticks**, median 26, against 330 raw A edges at minimum 8.
Raw A assertion is therefore not equivalent to an accepted punch, and 20 ticks is
the minimum observed acceptance cadence for that capture and configuration. The
three clips occurred at roughly similar counts; combo semantics must not be
inferred from that observation alone.

Rejected anchors, non-authoritative unless future evidence explicitly rehabilitates
them: `0x080342A8`, `0x08034298`, `0x080342AE`, `0x08029FFE`, and the
attack-object `+0x08` phase watch.

P-006A confirmed signed current HP at `target+0x28C`, incoming damage at
`record+0x18`, writer `0x0800FA50`, and death threshold `HP <= 0`. `0x080101C6`
and `target+0x04` are position-derived, not HP; all HP, healing, damage and re-hit
claims derived from them are **SUPERSEDED**. A controlled punch run entered
reaction node `0x08706BA8` at tick 320 and wrote HP at tick 323, so HURT preceded
damage by 3 ticks; controller state is rooted at `target+0x238`. A writer-only
mash run recorded post-ki HP writes at ticks 673, 976 and 992, giving intervals of
303 and 16 ticks; the latter ended in the death path, and neither establishes an
immunity timer.

Open, not blocking: separate invulnerability **UNKNOWN**; reaction/HURT exit
condition **UNKNOWN**; authoritative world position **DEFERRED**; knockback
kinematics **DEFERRED**; possible three-clip combo cycle **OBSERVED PATTERN /
DEFERRED**.

### Wolf combat behaviour

The wolf uses one reusable distance primitive with a per-node threshold. Both
`0x08029BE0` and `0x08029C90` are instruction-for-instruction equivalent: they
take each actor's body rectangle from `0x0800FDFA`, reduce it to a center via
`(lo + hi) >> 1`, compute `dx*dx + dy*dy`, and compare against the constant copied
from the owning node into instance `+0x0C`. The branch is a signed `bgt` to
failure, so the test is inclusive.

```text
dx = centerA.x - centerB.x
dy = centerA.y - centerB.y
distance_squared = dx*dx + dy*dy
in_range = distance_squared <= node_threshold
```

Distances are in world units; positions are 8.8 fixed point at `+0x1A0` (X) and
`+0x1A4` (Y), so a raw delta is divided by 256 before squaring.

| Rule | Condition | Result |
|---|---|---|
| Acquire | `distance_squared <= 10000` (r 100) while idle | enter combat hub |
| Attack | `distance_squared <= 524` (r ~22.9) from hub | enter attack state |
| Otherwise | from hub | pursuit behavior |
| Attack duration | 35 gameplay ticks | return to hub |
| Attack spacing | 36 ticks minimum observed | not a proven timer |
| Disengage | none | no leash |

```text
IDLE 434
  - dist_sq <= 10000           -> HUB 435

HUB 435
  - dist_sq <= 524             -> ATTACK 437
  - otherwise                  -> PURSUIT 438 / 439

ATTACK 437
  - after 35 ticks             -> HUB 435

DISENGAGE: NONE
```

Selector 438 is near pursuit, 439 far pursuit; both return to the hub. Selector
436 is observed returning to the hub but its condition is **UNKNOWN**. Attack
duration was exact in 52 of 52 episodes, and all 52 returned to the hub. The
36-tick figure is the minimum observed spacing, consistent with the 35-tick state
plus the earliest following start; no executable cooldown timer was found, and the
counter at `+0x12` was tested and refuted as its driver.

**Disengagement: NONE, CONFIRMED BEHAVIOR.** The wolf does not disengage once
acquired. Runtime testing observed continued engagement out to at least radius
157, and firsthand gameplay experience independently confirms wolves do not drop
aggro. The radius 157 figure is a lower bound on observed engagement, not a leash
value, and must not be implemented as one.

The earlier reading of hub constant 8100 (r 90) as the acquisition radius is
**SUPERSEDED**; acquisition belongs to the idle node at 10000. The 8100 band is
real but its role is unmapped. Absolute EWRAM addresses are not permanent actor
identity: `0x0203DBB0` behaves as a wolf in `wolf-acquire.ss1` despite older notes
associating that address with player context, so structural provenance overrides
address-based naming.

### Normal melee variants

The three normal-melee clips are presentation variants, not combo steps. On each
accepted attack the game selects uniformly among them.

```text
on accepted normal melee attack:
    clip = uniform_choice(0x0851C680, 0x0851C6A0, 0x0851C6C0)
    duration = 16 gameplay ticks
    damage = same for all three
```

The clips are contiguous indices 4, 5 and 6 of the character animation table at
`0x0851C898`, whose index 0 is the idle clip `0x0851C618`. Selection evidence: 266
accepted punches, counts 91 / 91 / 84, chi-square 0.37 on 2 degrees of freedom
against a 5% critical value of 5.99. Avoidance was refuted by 94 immediate repeats
in 265 transitions, and a fixed cycle by self-match rates of 26 to 34% at lags 2
through 6 where a true period requires 100%. Duration evidence: 50 scripted
punches, every observation exactly 16. Damage evidence: 22 unambiguous hits,
per-variant means 51018, 49884 and 50358; the between-variant difference is about
1100 while each variant's internal spread is 2000 to 3600, so the variation within
a variant exceeds that between variants. **Do not conflate 16 with 20**: the
animation runs 16 ticks while the minimum accepted-punch cadence is 20, so at
maximum mash rate there are about 4 non-attacking ticks between swings.

The mechanism is **UNKNOWN**. Uniform random is a behavioral result from the
observed distribution; the executable selector was never located, the only aligned
reference to the clip table base being a data slot in a per-character table. Do
not record this as a decoded `rand() % 3`. The published LoG2 RNG seeds at
`0x03003890` and `0x03003894` are **not** this game's RNG; they and `0x03003898`
stayed frozen across all 532 rows of the selection run while selection varied 266
times. Two hits measured 1.43 and 1.50 times the baseline mean were recorded as
UNKNOWN at the time and are now **reclassified as genuine critical hits** by the
critical-hit measurement below.

### Critical hits

**PARTIAL.** Critical semantics are confirmed; the roll that decides a critical is
not.

```text
on a normal melee hit:
    critical = <UNKNOWN roll>                  # placeholder required
    damage   = base_damage                     # fixed-point, 1024 units = 1 HP
    if critical:
        damage = damage * 3 / 2                # exactly x1.5
        presentation = critical_asset          # 0x0806F150
    else:
        presentation = normal_asset            # 0x0806E050

    displayed_number = (damage + 1023) >> 10   # ceiling divide
    target_hp -= damage                        # target+0x28C, signed 32-bit
    if target_hp <= 0: target_hp = 0; death
```

`target+0x28C` and `record+0x18` carry **ten fractional bits**; 1024 raw units are
1 HP. The display path at `0x0800AB9A` adds `0x3FF`, executes `asrs #0xA`, and
formats with `"%d"` from `0x0800AD88`. The heal path at `0x0800FA80`
independently confirms the scale by clamping against `maxHP << 10`. Raw HP
`141884` is **139** on screen; raw damage `51338` is **51**. Earlier "~50,000 per
hit" figures were raw units, not displayed damage. This is **not** the 8.8
world-position scale (`asrs #8` at `0x0800FE78` on `+0x1A0` and `+0x1A4`); do not
conflate the two.

| # | Question | Answer |
|---|---|---|
| 1 | Critical discriminator | damage `record+0x10`, nonzero means critical |
| 2 | Multiplier | exactly 1.5, contradicting the documented 2 |
| 3 | Presentation | two assets selected by the same flag |
| 4 | Critical probability | **UNKNOWN**, placeholder required |

Discriminator evidence, two directions. Statically, `0x0800E94E` tests
`record+0x10` and selects spawner mode 4 with flag 1 against mode 3 with flag 0;
the flag reaches number-object `+0x1C`, where `0x0800AB6A` picks asset `0x0806F150`
or `0x0806E050` from context table `0x08071700`. At runtime, across 60 stops at
`0x0800FA2A`, `record+0x10` was the **sole** field separating the 2 special hits
from the other 57; every other offset was constant or was the damage magnitude
itself. Multiplier evidence: `76494 = 1.5 * 50996` and `75924 = 1.5 * 50616`.
Both bases are exact integers on the same 38-raw-unit lattice that all damage
uses, and both fall inside the observed normal range of 47804 to 52440 (mean
50250, n = 57). The heal counterpart is mode 6 (`0x0800E97E`), so mode is the
number *type* selector rather than a damage-specific value.

Documentation records criticals as exactly twice normal damage. The binary
disagrees, and the runtime observation wins. "Double damage" is retained as
external behavior that runtime evidence **overturned**, never as a confirmed fact.
The claim that the critical number renders *yellow* specifically is **not**
established; only that `0x0806F150` is the distinct critical-side asset.

**Blocked, not merely unfinished:** the RNG source, the STR-dependent probability
formula, the producer that writes `record+0x10` and `record+0x18`, and the exact
arithmetic site of the 1.5 multiply. Because the multiply site is unlocated,
whether it applies before or after defense and clamps is also unknown. Two
consumer-side routes were attempted and failed for structural reasons; do not
retry either. Walking up from `0x0800FA2A` reaches only behavior-tree plumbing,
because that chain is the reaction tree and runs downstream of the damage
arithmetic. A write watchpoint on `record+0x18` is swamped by unrelated reuse,
because the record is stack scratch and the address is meaningful only during the
damage call.

Limits that must not be over-read: only **2** critical events were observed, so
the 2-of-59 rate is a raw count and **not** a probability estimate; both observed
bases were **even** multiples of 38, so the 1.5 multiply landed exactly, and
**no fractional case was observed**, leaving the rounding rule for an odd base
**UNKNOWN**; whether criticals select a distinct reaction or knockback path was
not reached and is **UNKNOWN**.

### Enemy death and rewards

**RESOLVED.** All 11 acceptance criteria met, with two bounded unknowns.

```text
on_enemy_lethal_damage(enemy):
    enemy.hp -= damage                  # fixed point, 1024 raw units = 1 HP
    if enemy.hp <= 0:                   # signed; may go negative, overkill discarded
        enemy.hp = 0
        broadcast(EVENT_DEATH)          # event 0x11 via 0x08011C0C
        reward.exp = enemy.base_exp + 23 * qualifying_exp_bonus_items

    one_tick_later:                     # T_EXP - T_LETHAL = 1, confirmed
        recipient = active_character    # index read AT PAYOUT, not at kill
        recipient.xp += reward.exp
        if recipient.xp >= threshold[recipient.level]: level_up(recipient)

        if drop is zeni: amount = denomination[i]   # {5,25,50,100}
        if drop is item and item_count < 250:
            inventory[item_count] = item_id & 0x0FFFFFFF; item_count += 1
```

| # | Question | Answer |
|---|---|---|
| 1 | EXP delay | exactly 1 gameplay tick after lethal damage |
| 2 | Recipient | active character index, resolved at payout |
| 3 | Wolf base EXP | 225 |
| 4 | Equipment bonus | +23 per item, additive |
| 5 | Zeni denominations | 5, 25, 50, 100 |

| Item | Address |
|---|---|
| save-block base | `0x03001068` (from ROM pool `0x086B7080`) |
| character block | base + `index*0x68` + `0x4F8`; XP at block `+0x24` |
| Goku XP | `0x03001584` |
| Zeni | `0x0300155C` |
| item count | `0x0300114C` |
| EXP writer | `0x08013914`, store at `0x080139F8` |
| Zeni writer | `0x08017EC2`, store at `0x08017ED6` |
| item add | `0x08004448`, cap 250 |
| award-on-destroy | destructor loop `0x08011A1E` |
| level thresholds | `0x086B7084`, cap 200 at `0x08013A00` |

**The amount/recipient asymmetry.** The award **amount** is fixed when the reward
object is created, with the equipment bonus already applied (`+0x08` read 225
unequipped, 271 equipped). The **recipient** is read one tick later at payout.
That asymmetry is the exact mechanism behind the documented save-point
character-switch glitch: switching after the kill changes who receives the EXP,
never how much.

Wolf fixture: initial HP 179200 raw (175 displayed), 4 hits to kill, damage
47956-52250 raw (47-52 displayed), base EXP 225, final award 225/248/271 for
zero/one/two bonus items.

Bounded unknowns: the EXP bonus **arithmetic site** is upstream of reward-object
creation and unlocated; the next anchor is the constructor, vtable `0x0804A820`
at `+0x00`. The **drop roll** that selects a table index is unlocated, same
producer class as the critical-hit blocker. Death-animation duration was not
measured, and a flat +23 cannot be distinguished from one proportional to base,
since every observation used base 225.

## Established safety rules

**Output path safety** has one owner, `tools/webfoot/write.py`:

| Name | Policy |
| --- | --- |
| `paths_are_the_same_file(source, destination)` | Does this destination denote the same file? |
| `ensure_not_source_alias(source, destination)` | Source-alias safety, refuse. |
| `ensure_new_destination(destination)` | Overwrite, refuse an existing output; kept separate on purpose. |
| `OutputPathError` | Derives from `WriteError` (`ValueError`), so every existing CLI/GUI boundary already reports it. |

The rule is filesystem-aware in two halves, because neither alone suffices:
`os.path.samefile` (device+inode / volume+file index) catches a **hard-link
alias**, which no string comparison can see, and `resolve()` plus `normcase()`
covers a destination that does not exist yet (the ordinary export), relative
spellings, `.`/`..`, junctions/symlinks in existing components, and case or
separator variation on Windows. Both earlier implementations of the rule were
routed through it rather than kept. The rule is: the source is an input on every
path and can never be an output destination. `graphics export --out <existing
file>` and the Workbench export still silently replace an existing PNG while the
ROM writers refuse one; that CLI/GUI agreement with each other and divergence from
the ROM writers is deliberate and belongs to the open overwrite-policy finding.

**Atlas and ROM identity.** `tools/webfoot/profile.py` carries `AtlasIdentity`,
`AtlasIdentityMismatch`, `RomProfile.identity` and `RomProfile.require_identity`.
It is called from exactly one production site, before the atlas is assigned and
before maps or text are loaded, so a refusal leaves the session with no
atlas-backed state at all. Both halves are checked because each alone is
insufficient: the profile id alone would accept a differently-revised dump of the
same game, and the base hash alone would accept an atlas whose offsets were
resolved against another profile; image size is checked with them. The comparison
reads the atlas's identity structurally, so `webfoot.profile` does not import
`webfoot.atlas`, and a value that does not declare the triple is refused by name
rather than defaulted. The failure arrives as the product's existing
`SessionError`, naming both identities; there is no silent rebuild and no
automatic atlas regeneration. A trusted derivative resolves against canonical-base
provenance, not its own output digest, so a derivative's own hash differing from
the canonical hash does not require a rebuilt atlas. **`VERIFIED_FREE` cannot
cross an identity mismatch**, and a focused regression drives the real open path
with a structurally valid atlas carrying a genuine `VERIFIED_FREE` span built for
another profile: it is refused, the session holds no atlas, and the same span
under the right identity is accepted.

**Profile authority for extents.** The canonical identity (six owners), the
map-entry table address, count and stride, the text pointer-table address and
count, the stat extents, both palette addresses and the GBA base were migrated to
one authority. The export stack resolves identity and extents through a thin
`tools/export/profile_authority.py` over the packaged catalog, with the reader
object carrying accessors (`map_entry_count()`, `map_entry_table_address()`,
`text_table()`, `object_palette_address()`, `bg_palette_address()`) instead of
module constants. The text codec lost the game extents it could not own and takes
them from its caller. Four live index bounds read the profile: the export reader's
text index, the placement-contract dialog text count, the authored script effect's
text count, and the character-roster bound. The four contract-hash gates compare
against `profile.sha256`, with each contract's own literal retained as a pinned
cross-check asserted against the catalog for every profile. The GBA base has one
authority, `tools/webfoot/binary.GBA_ROM_BASE`; the other production spellings are
aliases of it. Format constants stay in the format layer (record strides and
widths, the string terminator and control units, screenblock geometry), and
evidence and provenance labels stay where they are records rather than authorities
(`atlas_build.PROFILE_ID`, the atlas producers' `EXPECTED_SHA`, the profile-id
keys that select a data dict). Test oracles stay independent on purpose.

**Shared binary interpretation has one production authority.**
`tools/webfoot/formats/map_graphics.py` decodes the MapEntry table and record
fields, layer records and their handler classification, dominant chunk windows and
their grid stitching, the selector delta stream, the two screen-entry plane
handlers, the Map 19 terrain field, animated-tile records, character-block assembly
and the bank table; `formats/bg_tilemap.py` owns the screen-entry bits and the one
entry-to-pixels render; `formats/sprite_graphics.py` owns tile unswizzle, tile flip
and the GBA colour expansion. Eighteen shared map/graphics concepts were being
decoded twice in production; sixteen were equivalent-but-independent and **two
were genuine divergences**: the two stacks disagreed on which layer handlers they
understood, and on whether a tile bank must decode to exactly `0x4000` bytes or to
its container's declared extent. Both are reconciled, and the remaining tile-bank
extent difference is an accepted outer acceptance policy over that one decode. No
module under `tools/webfoot` imports `tools.export`; the dependency points SDK
authority to export consumer and never the reverse. The Map 19 divergence is
classified rather than left unexplained: the terrain-field and screen-entry handler
forms are decoded by the shared reader for both surfaces, the renderer accepts only
the dominant chunk grid `0x08008087` and refuses the rest by its accepted contract,
and the layout writer's single four-byte chunk-pointer operation has no
terrain-field window, so the editor refuses it by name.

## Capability registry

DragonByte Z reads **21 / 24 (88%)**: READ 5/5, EDIT 8/8, AUTHOR 4/7, DELIVER 4/4.
The three unshipped capabilities are new sprites, appearance authoring and new
maps. Phase 2 (map editing) is complete: tile painting, chunk creation, map
resizing with layer authoring and warp/connection editing all ship. Phase 3 has
started: graphics import shipped 2026-10-03, and the next capability is sprite,
animation and frame authoring, which the roadmap marks `next`, deliberately
distinct from `in-progress`. The exact per-capability limits and proof levels live
in [`capability-registry.md`](capability-registry.md), and the reconciliation of
this paragraph against the registry is recorded in
[`research/PROJECT_STATE_AUDIT_RECONCILIATION.md`](research/PROJECT_STATE_AUDIT_RECONCILIATION.md).

## Research posture

The ten-system LOGExtractor research queue is complete and its consolidation
exists, so the broad archaeology freeze has ended. **Do not create another broad
archaeology queue**: additional research is targeted and capability-driven only,
and each new question must name the blocked authoring operation it unblocks. The
separation between research gaps (engine and semantic unknowns) and engineering
gaps (parser correction, validation, serialization, allocation, relocation,
encoding, UX, runtime verification) is maintained: "not implemented yet" is not
"not understood". A ROM value enters shipped data only once measured and
confirmed; anything still unmeasured is marked temporary and named as such.
Structural warp destination-key randomization is supported after bounded
engineering and validation, but it is not proof that a seed is completable, since
progression and softlock validation is a separate problem; arbitrary new
trigger-region authoring, new warp records and spawn/arrival/facing control are not
solved.

## Known deferred production defects

1. `tools/webfoot/graphics.py::_animations_in` does not honor the definition
   `+0x00` count bound (it walks to the next structure). This is the single
   remaining stale-assumption audit hit.
2. The multipart composite display and replacement path is unbuilt.
3. `webfoot_strict`'s marker-terminated extent exceeds the write-bounding
   `packed_end` by 4 bytes on 2,728 containers; the behaviour is documented, not
   changed.
4. The pre-existing `declared_size == 0` acceptance remains.
5. The live screenblock is not the chunk plane verbatim, so the engine's
   map-upload transformation (ROM to charblock/screenblock) remains unknown.
6. The atlas seed overlay work is open, and the production allocator does not use
   the atlas seed as its free-space authority.
7. `tools/webfoot/atlas_producers/scan.py::_compression_rows` is a stride-4
   heuristic sweep whose own docstring calls its output noise (24,285 hits /
   68.7 MiB); it is outside the SDK's canonical path.

The former defect 5, that a 16 MiB derivative was not reopened by the shared
derivative verifier, is **fixed**: `DERIVATIVE-16M-REOPEN-001` made the verifier
check only the canonical span stated by the profile identity, so a valid
expanded derivative reopens. `tests/unit/test_authored_image.py:500` and
`tests/unit/test_map_layout_provenance.py:172` assert it.

## Open questions

- Which higher-level caller invokes point-query `0x080126D4` during the
  idle/normal-processing path?
- What is the complete call tree after action target `0x080125E8`, which did not
  return within 512 steps?
- Is the `0x08007675` source descriptor bounded well enough for a future lossless
  read-only parser?
- Which semantic subtype, if any, is justified for the rectangle-aware family?
- Which additional object or mechanism causes the remaining transition after
  descriptor `0x08294948` is empty?
- Connector geometry and spawn semantics, layer positioning, animation slot names,
  frame origin, the animation trailer words, the tile-bit role and the appearance
  `+0x0C` higher semantics all stay unresolved or partial.
- The critical-hit RNG and its STR-dependent probability, the producer that writes
  `record+0x10`/`record+0x18`, and the exact site of the 1.5 multiply.
- The EXP bonus arithmetic site and the drop roll.
- The physical order and names of the four animation directions, and which byte is
  the pointer run's first entry.
- Map 19's exact `DISPCNT` mode, and the consumer of the 45 portrait-run entries
  that carry no appearance-definition reference.
- The graphics identity of the 27 UI containers not rendered to a recognisable
  asset, the 9 UI containers that are not tile-aligned, and the 55 kind-1
  data-referenced containers in `0x087315E8..0x0874D044`.
- The remaining semantic identity of `+0x03001A34` in the transition arrival path,
  whose non-zero case is untested.
- Whether an untriggered placement descriptor's script fires on player
  interaction: the consumer is the getter behind actor-vtable slot `+0x78`
  dispatched from `0x08032CE4`.

## Where the detail lives

- [`reverse-engineering.md`](reverse-engineering.md): the main durable evidence
  record, including the ten accepted post-LOGX corrections.
- [`consumer-analysis.md`](consumer-analysis.md): executable-consumer evidence.
- [`research/`](research/): per-system format and provenance documents, including
  [`LOGX_SYNTHESIS.md`](research/LOGX_SYNTHESIS.md) for the consolidated canonical
  resource graph, the 39 refuted LOGExtractor assumptions, and the read-support
  and authoring-readiness matrices.
- [`research/ARCH_INVENTORY.md`](research/ARCH_INVENTORY.md): the architecture map
  of `tools/webfoot/`.
- [`research/PROJECT_CODE_QUALITY_AUDIT.md`](research/PROJECT_CODE_QUALITY_AUDIT.md):
  the live engineering risk register.
- [`research/POST_LOGX_IMPLEMENTATION_ROADMAP.md`](research/POST_LOGX_IMPLEMENTATION_ROADMAP.md):
  the post-research plan and its phases.
- [`testing.md`](testing.md): the named validation gates.
- [`decisions/`](decisions/): the decision records, including canonical ROM
  immutability, derivative trust, proof levels and naming precedence.
