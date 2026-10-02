# Allocator checkpoint D: above-8-MiB runtime proof

The real-ROM runtime proof that the retail engine consumes a resource the
production allocator placed above the original image end, plus the domain
reachable-capacity map.

## 0. Result in one paragraph

A rebuilt retail compressed-dialogue container was placed **above the original
8 MiB boundary** by `tools/webfoot/allocation.py`, chosen from the profile's
declared expansion region by the deterministic policy; the production writer
authorized the appended write from the allocator's own provenance; `build_project`
emitted a 16 MiB derivative and published its sibling manifest; the engine-visible
selector word was repointed to the new address; and mGBA 0.11 recorded the retail
consumer at `0x08012240` reading handle `0x02002641`, selector 1, table entry
`0x08800000`, with the dialogue box displaying the authored line **"Nice work,
Goku!"** where retail says "Good luck, Goku!". The canonical ROM is unchanged.

## 1. The production chain

| Step | What happened | Evidence |
|---|---|---|
| semantic request | `AllocationRequest(..., kind=PACKED_STREAM, addressability=EXPANDED_PERMITTED)` | `tools/webfoot/compressed_dialogue.py:141-152` |
| production allocator | chose file `0x00800000` from the declared expansion region `[0x00800000,0x01000000)` | `tools/webfoot/allocation.py` |
| allocation record | `GeneratedAllocationProvenance`, owner `compressed-dialogue:goku-greeting`, domain `compressed_dialogue` | manifest `generated_allocations[0]` |
| above canonical EOF | file `0x00800000` ≥ `0x00800000`; address `0x08800000` | manifest |
| write authorization | `write.plan_changes` accepted the appended change only because that record owns it | `tools/webfoot/write.py:551-558` |
| derivative | 16,777,216 bytes, SHA-256 `3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb` | emitted by `build_project` |
| provenance manifest | written beside the image by default (Checkpoint B behaviour) | `derivative.gba.dragonbyte.json` |
| reference update | selector slot `0x007B5B68` = `00008008` (LE) = `0x08800000`; the other six table words unchanged | measured in the test |
| engine dereference | `CONSUMER 0x08012240 handle 0x02002641 selector 1 entry 0x08800000` | runtime CSV |
| observable result | dialogue box reads **"Nice work, Goku!"** | screenshot |

### 1.1 The address was the allocator's choice

Two independent proofs, because "it landed at `0x800000`" is also what a
hard-coded constant produces:

* **The input moves, the address moves.** With an earlier build domain issuing a
  256-byte reservation through the build-scoped set the coordinator already
  threads, the payload lands at `0x00800100` / `0x08800100`
  (`test_the_address_is_the_allocators_choice_not_a_hard_coded_constant`).
* **There is no literal to hard-code.** `compressed_dialogue.py` contains none of
  `0x800000`, `0x00800000`, `0x08800000`, `8388608` or `16777216`; the destination
  is `allocation.range.start.value`. The test asserts that list, so a future
  literal fails the suite.

`write.plan_changes` refuses any appended change whose span no allocation record
owns, so even a hand-forced address could not be emitted without minting a
provenance record for it.

## 2. Runtime proof

| Item | Value |
|---|---|
| Emulator | mGBA `0.11.0.0` dev build, `build\tools\mgba-dev\extracted\mGBA-build-2026-08-27-win64-9128-c65e8a3d4666b0ea68a01578232452f31b185332\mGBA.exe`, verified from `VersionInfo.FileVersion` |
| Vehicle | free-running inject-then-load session (`start_capacity001_expansion_session.ps1` / `run_capacity001_expansion.ps1`), because a frame-bounded Lua observer records **zero** ticks under the GDB launcher |
| Fixture | private deterministic savestate, SHA-256 `2D5740A8C54180D153024A11B0E4D1143306957AF55A3AD0664C71CF7D9A1AAB` (byte-identical to the one TOOLKIT-029/030/031 used) |
| Trigger | the state resumes in front of the NPC; the greeting is consumed without any scripted input (the scripted run also walks left and taps A) |
| Expected retail behaviour | the dialogue box reads "Good luck, Goku!" |
| Expected modified behaviour | the same box reads "Nice work, Goku!" |
| Observed | **"Nice work, Goku!"** (screenshot `capacity001-consumer-1-dialogue-box.png` |
| Pointer/address | table entry `0x08800000` for handle `0x02002641`, selector 1 |
| Derivative | SHA-256 `3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb` |

### 2.1 Liveness, stated explicitly

| Run | Target | Liveness | Case |
|---|---|---|---|
| `human-1` | **2 hits** | fired | execution observed |
| `human-2` | 1 hit | fired | execution observed |
| `capture-3` | 1 hit | fired | execution observed |

No run is in the "target silent + liveness silent" case, so none of them is a
null result being read as a negative. The liveness channel is a second scripted
breakpoint on the shared interpreter at `0x08004038`, which dialogue and
cutscenes both reach.

### 2.2 Evidence artifacts (all under ignored `build/`)

| Artifact | SHA-256 |
|---|---|
| `derivative.gba` (16,777,216 bytes) | `3ccbef45940e8f5c27d3f88839639eb04d9cc50f8d942f18bc850872628724cb` |
| `derivative.gba.dragonbyte.json` | `a3cd6a50986326c02e0880c231d7fcfd33d71261f0c6dd8bb46551695651c939` |
| `human-1/capacity001-dialogue.csv` | `03b711479a6f9f6fe656e7586793a7ece1c3ec03ee816f5cb82052ea169cb9ba` |
| `human-2/capacity001-dialogue.csv` | `ad27a5a6c0c080b8406d0bafc6a0b35f917e70a88fb9639b44bd342cd893233b` |
| `human-2/capacity001-consumer-1.png` | `8de45671cf5faa7048312961bdb3bc9aa672ec2fbc15abd0969ed662ed670899` |
| `capture-3/capacity001-dialogue.csv` | `db4f8d7dc9123007d4bb9d10b2a53f0a7fdaad0d2b1c8c2f036490bea183ba7e` |
| `capture-3/...-1-early.png` (+8 frames) | `caef963df79c05fe376a38d6589184f78b55c5d5eee9ca0f0556e4d5d2da18d0` |
| `capture-3/...-1-dialogue-box.png` (+45 frames) | `6af871edf8f007ec12fd16f6ad51cd0f7f27556f3ea49738fee398e272d43b3d` |

The `+8` frame shot is retained deliberately: it shows the world with **no**
dialogue box yet, and is the measurement that the box is not up the instant the
handle is read (the engine still fetches and decompresses 17,932 bytes). A
`+8`-only capture would have looked like the relocation had no visible effect.

### 2.3 Bounded, and honest about it

This proves **one domain at one address range**: the compressed-dialogue selector
path, over the 17,932 bytes the engine actually read
(`0x08800000..0x0880460B`). It does **not** prove that every address through
16 MiB works, that any other domain reaches above EOF, or anything about real
cartridge or flash hardware. Real hardware remains untested, exactly as
`ROM_EXPANSION.md:21-22` already recorded.

## 3. Derivative reopen

| Check | Result |
|---|---|
| canonical-base identity reconstructed | PASS: manifest `base.sha256` = canonical digest, `base.profile_id` = the profile |
| expanded allocation known after reopen | PASS: `reservations_from_manifest` returns the 17,932-byte span |
| the reservation is load-bearing | PASS: **without** it the allocator hands back the same span; with it, the next compatible request lands at `0x0080460C` |
| rebuild determinism | PASS: a second build is byte-identical, manifest allocations equal |

This uses Checkpoint C's reservation semantics unchanged
(`reservations_from_manifest`), not a convenience path.

## 4. Bounded negative control

A request of exactly the real payload size (17,932 bytes) as a kind whose pointer
family Checkpoint A found **unproven** above canonical EOF
(`PLACEMENT_BODY`, canonical-only) is refused with `InsufficientSpaceError`,
while the identical size through `PACKED_STREAM` gets an above-EOF placement. So
the refusal is about addressability and not about capacity, and no unproven domain
silently receives expanded storage. No other pointer domain was probed.

## 5. Addendum: domain reachable-capacity map

`tools/research/domain_reachability.py` carries one row per Checkpoint A domain
(the same sixteen, none invented) with three reachability levels kept apart, and
generates the tables now embedded in
[`ROM_CAPACITY_AND_ALLOCATION.md`](../research/ROM_CAPACITY_AND_ALLOCATION.md) §12.
A test compares the document against the module's own output, so a figure cannot
drift between the two.

| Level | Domains |
|---|---|
| ENCODING (the wire form can hold the address) | **13 / 16** |
| ENGINE-STATIC (a static bound was established) | **0 / 16** |
| RUNTIME-PROVEN (a real derivative was dereferenced) | **1 / 16** |

`ENGINE-STATIC` is empty on purpose. Not finding a bound is not proving there is
none, so every untested domain records UNKNOWN rather than a nominal range. The
raw 8,388,608 bytes of expansion are therefore **not** presented as universally
usable.

| Domain group | Byte capacity | Structural limit | Binds first |
|---|---|---|---|
| Dialogue / packed streams | 8 MiB encodable; 17,932 runtime-proven | **7 containers** | the table |
| Text | 8 MiB encodable | 1,534 entries, no table growth path | the table |
| Maps | 8 MiB encodable | **452** records (code constant) | the constant |
| Objects per map | 8 MiB encodable | **255** (`ldrb` count) | the count byte |
| Static scripts | 8 MiB encodable | **40**, exactly the engine bound | the engine bound |
| Sprites | 8 MiB encodable | **297** definitions + literal terminator | the run |
| Appearances | 8 MiB encodable | **232** (runtime bitmap) | the bitmap |
| Palettes / stat tables | none, fixed addresses in code | 256+256 entries, 141 records | the address |
| All other domains | 8 MiB encodable, **0 proven** | varies; several UNKNOWN | pointer reach |

## 6. Not done here, deliberately

| Out of scope | State |
|---|---|
| Other pointer domains above EOF | untouched; each needs its own targeted proof |
| 32 MiB probing | not attempted |
| Candidate free space | **not promoted**; canonical free is still the 256-byte TOOLKIT-028 window |
| `ROM-CAPACITY-ATLAS-SEED-OVERLAY-001` | **OPEN**; `seed.py` unmodified, and the allocator does not read the atlas |
| Workbench / GUI allocator integration | **not started**; CQA-05/06/07/08 remain deferred |
| Runtime memory campaign | not attempted; Checkpoint A's ceilings stand, marked UNKNOWN where unmeasured |

## 7. Deviations and defects found in this checkpoint

* **One probe file does both observation and input**, where the runtime skill's
  §7 asks for a separate driver file. Reason: injection is one allowlisted script
  per call, and the input schedule has to be frame-aligned with the observer's own
  screenshot timing. The probe writes input and **never** writes emulated memory,
  and says so in its header. The read-only guard test covers named files, not this
  one; the deviation is recorded here rather than hidden.
* **Runner stopped mGBA on the marker's existence** rather than its content, so it
  killed the emulator ~2 s after the state load. Fixed to wait for a completion
  word; the empty CSV it produced looked like a negative result.
* **State-load confirmation race.** `toolkit031_load_state.ps1` confirms the load
  from the Scripting log pane, and that confirmation can race the Run helper when
  it runs seconds after injection. Both runners now retry once. The retry cannot
  double-apply: a failed confirmation means no load happened.
* **Screenshot window was too early** (`+8` frames). Widened to `+8` and `+45`,
  keeping both, because the first is the measurement that shows why.

## 8. Validation

Focused file-scoped tests only; no broad suite.

```text
tests/integration/test_capacity_checkpoint_d_rom.py   -> 5 passed
tests/unit/test_domain_reachability.py                -> 8 passed
tests/unit/test_mgba_capture.py                       -> 73 passed (observer guard)
tests/unit/test_allocation_authority.py
tests/unit/test_allocation_provenance.py
tests/integration/test_rom_expand_001.py
tests/unit/test_capacity_proof.py
    -> see the closure report for the observed totals

runtime: 3 bounded sessions (human-1, human-2, capture-3), each verifying both
ROM hashes; canonical ROM unchanged in every one.
```
