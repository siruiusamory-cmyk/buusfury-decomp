# Runtime proof of an existing transition edit

The instrument and derivative built for a runtime proof of a project transition
edit, the destination choice, the run procedure and what remains unestablished.

## 1. The target transition

Established from the production authority, not guessed:

| Property | Value |
| --- | --- |
| Source map | `map:0040` |
| Transition identity | **`map:0040/transition:0000`** - element 0 of map 40's own `root + 0x44` array |
| Retail destination | `map:0039` |
| Retail destination key | `01 0b` (high at `+0x11`, low at `+0x12`) |
| Retail region | `first=(0, 9)`, `second=(112, 169)` |
| Class word | `0x08007675` (a measured, supported form) |
| Record file offset | `0x29343C` (record survives the edit in place) |

Map 40 carries exactly two transitions: `transition:0000` -> map 39 and
`transition:0001` -> map 41. **The record's control is respected**: the same
identity `map:0040/transition:0000` is the one edited and the one both runs
activate. The other Map 40 exit is never used as a comparison.

## 2. Destination choice

**Map 41** was chosen, as the record prefers. It is the strongest available choice
on evidence rather than convenience:

- map 40's **own second transition** already targets map 41 with the identical key
  value `01 0d`, so the 41 key is a destination this very map's records already
  carry;
- map 41 is an ordinary map the engine loads (`map:0041` has its own two
  transitions, one back to map 40), so nothing exotic is being asked of it;
- the region is **not** touched: `TARGET`'s stored position is left exactly as
  retail has it, because destination-position semantics are `UNRESOLVED` and the
  record forbids inventing them.

**A discriminating-power fact worth stating plainly.** Only **one** byte differs
in the derivative. Map 39's key is `010b` and map 41's is `010d`, so they share
their high byte (`0x01`) - keys ascend `010a..010e` across maps 38..42. The engine
compares the record's two bytes **separately** (`0x08008A0E`/`0x08008A14`) against
`MapEntry[+0x00]` and `[+0x01]`, so a one-byte difference is still a different key;
but the locality claim in this record is "inside the two key bytes", not "both key
bytes", and it is asserted in exactly those terms.

If map 41 turns out to be an unsuitable arrival - crash, softlock, or a rejection
of the caller-supplied position - it is recorded as unsuitable and another
**existing** valid destination is tried. Nothing about the position is authored to
work around it.

## 3. The project edit, and the derivative

The derivative came from the record's required path and from nothing else:

```text
canonical ROM
  -> extract_project (SDK extractor, no graphics)
  -> set_transition_edits (SDK authoring API; writes maps/transitions.toml and
     MEASURES the stored prior from the canonical image)
  -> build_project (the production build)
  -> derivative
```

`maps/transitions.toml` as written by the SDK:

```toml
[transition]

[transition."map:0040"]

[transition."map:0040".0000]
prior_destination = "map:0039"
destination = "map:0041"
```

No hex edit, no one-off ROM patch, and no research script that writes a
destination byte: the driver only calls the SDK and the build.

| Property | Value |
| --- | --- |
| Derivative | `build/warp_runtime001/warpedit001-authored.gba` |
| Size | `8,388,608` bytes (unchanged) |
| SHA-256 | `b2824a275b04efaea1a19f689cca2919db5b2ac59807579416bf9efc171966fa` |
| Differing bytes vs canonical | exactly one: file offset `0x29344E` |
| Key span | `0x29344D` (high, unchanged `0x01`) and `0x29344E` (low, `0x0b` -> `0x0d`) |
| Region bytes | unchanged |
| Unresolved bytes (`+0x00`, `+0x04`, `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17`) | unchanged |
| Re-read through the authority | destination `map:0041`, key `010d`, region `(0,9)/(112,169)` |
| Canonical ROM | SHA-256 `940ad5f0…f059e` before and after |

The build's manifest records the edit as `map:0040/transition:0000`,
`map:0039 -> map:0041`, with `region_changed: false` and `changed_byte_count: 1`.

## 4. The instrument

Modelled on the vehicle `MAP-TILE-PAINT-001` proved for human-played sessions, and
reusing the tracked injection and state-load helpers rather than reconstructing
them.

| File | Role |
| --- | --- |
| `tools/runtime/warpedit001_transition_watch.lua` | read-only observer: the live map identity every time it changes, the target record's destination key read **through the engine's own route**, the map that key resolves to, the region, and heartbeats |
| `tools/runtime/start_warpedit001_live.ps1` | launches one mGBA on a caller-named ROM with an **exact** digest, injects the observer, loads the savestate after injection, prints the run directory, and exits - it holds no wait loop, starts no job and kills nothing |
| `tools/runtime/finish_warpedit001_session.ps1` | after the operator closes the window: re-verifies the ROM and the private save, prints the target record, the map timeline, the first departure from map 40 and whether one followed a leave-and-re-enter, and writes `summary.txt` |
| `tools/runtime/inject_mgba_lua.ps1` | the observer registered in `$allowedLua` (required: injection refuses anything not allowlisted) |
| `tests/unit/test_mgba_capture.py` | two focused regressions: the observer is read-only and derives the record rather than pinning its address; the launcher verifies identity and owns no session lifetime |

**The record is proved to be the engine's own.** The observer does not read a
hardcoded record address. Each time the map changes it walks
`MapEntry[map]+0x2C -> word[0] -> root+0x44 -> element 0 -> record`, logs every hop
into the CSV, and reads the two key bytes there. A pinned address would have proved
nothing about which record the engine would use; this does.

**Read-only, with no input path.** The observer contains none of the input- or
memory-modifying API names the repo's guard greps for, and no driver for this
record exists in the tree. Two focused tests assert it.

**The private save is isolated.** The emulator is pointed at
`-C savegamePath=<run dir>\savegame`, the same switch the proven capture launcher
uses, and the save beside the image is hashed before and after
(`7CF0A516…2A86` as of this writing).

**Liveness is built in.** Heartbeat rows make a silent observer distinguishable
from a quiet one, and a route that never resolves is reported as
`TARGET_UNRESOLVED` rather than omitted - a silent channel is not evidence of
absence.

## 5. The run procedure

Pre-validated with `-DryRun` for both runs (exact digit pins, savestate, emulator
version, observer allowlist, no mGBA already running).

**A. Retail** (canonical image `940ad5f0…f059e`), then **B. Authored** (derivative
`b2824a27…6fa`), with the same savestate and the same trigger:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/runtime/start_warpedit001_live.ps1 `
  -RomPath "<checkout>\roms\Dragon Ball Z - Buu's Fury (U).gba" `
  -RomSha256 "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e" `
  -StatePath "<checkout>\roms\Dragon Ball Z - Buu's Fury (U).ss1" `
  -Label "A-retail"
```

The operator then, **by hand** (no scripted input, no input injection):

1. play out of map 40 and back into it, so the engine **rebuilds** the area from
   the ROM rather than inheriting it from the savestate;
2. walk into the doorway that retail's `map:0040/transition:0000` fires on;
3. note where the engine arrives;
4. close the mGBA window.

Then collect, and repeat with the derivative and `-Label "B-authored"`.

**Why step 1 is not optional.** A savestate restores emulated state, including
whatever the engine built when the area last loaded, so a ROM-side record change
can only be observed after a genuine re-entry. The observer marks a departure from
map 40 that followed an observed leave-and-re-enter with
`rebuilt-after-leaving`, and the finisher reports that edge separately from the
first one - so a run that only ever saw the pre-rebuild trigger cannot be mistaken
for the proof.

## 6. Safety

- The canonical ROM is never a write target, and its hash is re-verified after each
  run by the finisher.
- The savestate is copied into the run directory and the copy verified; the private
  original is never what the emulator loads.
- The save beside the image is isolated and re-hashed.
- No run directory is deleted: the launcher **refuses** a label that already
  exists, because a prior run directory is evidence.
- Run directories live under the ignored `build/` tree; no savestate, capture,
  save, derivative or other proprietary artifact is tracked.

## 7. What is NOT yet established

**The runtime result itself.** Everything above is preparation: the record edit,
its locality, and an instrument that has been syntax-checked, guard-tested and
dry-run, but not yet driven by a human. Until both runs are captured, this record
has **not** proved that the retail engine enters a different map, and no part of
this document may be read as that proof.

Also still open, and neither fixed nor worked around: whether map 41 accepts the
caller-supplied arrival position at all (the record's own stated risk), and the
`UNRESOLVED` destination-position semantics that would explain it if it does not.
