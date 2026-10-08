# Authoring a genuinely new map (MAP-NEW-AUTHORING-001)

Baseline `efdabce8fa81d254593f12779a4549eadee4008e` (`origin/master`, verified).
Branch `ticket/map-new-authoring-001`, clean, in a fresh worktree of its own.
Canonical image sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

This record holds the measured storage and engine facts a new-map capability
depends on, the decision they force, and the implementation plan. It is written
before implementation; the verification record written afterwards supersedes
nothing here and adds the runtime result.

## 1. Storage contract

| item | value | evidence |
| --- | --- | --- |
| table address / file offset | `0x0808E2E0` / `0x0008E2E0` | `docs/rom-profiles.md:21`, `tests/integration/test_logx_map_record_rom.py:33` |
| stride | `0x38` | `tools/webfoot/formats/map_entry.py:21` |
| canonical count | 452 | profile `tools/webfoot/data/roms.yaml:45-48` |
| extent | `[0x0008E2E0, 0x000945C0)` | `docs/research/LOGX_MAP_RECORD_PROVENANCE.md:42-60` |
| first byte past the table | file `0x0945C0` = Tileset bank 0, a live container | `docs/PROJECT_STATE.md`, measured bytes at `0x0945C0` are not a record |
| count representation | no count word, no terminator; a code constant | `docs/research/ROM_CAPACITY_AND_ALLOCATION.md:367` |
| project identity spelling | `map:%04d`, the table index | `tools/webfoot/maps.py:70-86` |
| engine identity key | two `u8` at record `+0x00` / `+0x01` | `docs/reverse-engineering.md:76` |

The tail is live data, so the table cannot grow in place: a 453rd row has to sit
in a relocated copy. Resolution is by **key**, not by index
(`docs/research/LOGX_CONNECTOR_PROVENANCE.md:480-492`), so row order inside the
relocated copy is free; only the scanned span matters.

## 2. The bounded compiled limit, measured

Disassembled from the canonical image with capstone (Thumb), file offsets:

```text
080125E0  movs r0, #0xff          ; the whole count helper
080125E2  adds r0, #0xc5          ; 0xff + 0xc5 = 0x1c4 = 452
080125E4  bx   lr
```

A whole-image BL census (every 2-byte Thumb instruction, re-derived by
`tests/integration/test_map_authoring_rom.py::test_the_count_helper_has_exactly_one_caller`)
finds **exactly one** caller of `0x080125E0`: `0x08008A02`, inside the map
lookup `0x080089FC`. The helper is map-table specific.

The lookup loads its own base from a pool word:

```text
08008A0A  ldr r1, [pc, #0x4c]     ; -> pool 0x08008A58
```

A whole-image scan finds **exactly one** occurrence of the value `0x0808E2E0`,
at file `0x8A58`, at any byte offset (aligned or not), and exactly one
instruction loads that pool word (re-derived by
`tests/integration/test_map_authoring_rom.py::test_exactly_one_word_in_the_image_names_the_table_base`).
The five lookup call sites (`0x08004A82`, `0x08008D2A`, `0x08008D6C`,
`0x08008E94`, `0x08009056`) follow the base automatically because they call the
function that loads it.

Six data words elsewhere in the image name individual records
(`0x083FAC78`, `0x084524DC`, `0x085757BC`, `0x085BAE04`, `0x085BB3D0`,
`0x085E11E8`; two of them are byte-identical repeated blocks). Their
neighbourhoods are compressed payload, not pointer tables. They are harmless
under relocation: the canonical table is retained verbatim, so a word naming a
retail record still reads that record's original bytes.

**So the engine-side surface of the map table is two patch sites**: one pool
word (base) and one halfword (count). Everything else about the table is
addressed through them.

## 3. Decision

A new map identity is realizable without inventing any unresolved engine
semantics:

1. **Relocate the table.** Emit the 452 canonical records verbatim plus the
   authored records at an expanded allocation, and patch the base pool word at
   file `0x8A58`.
2. **Raise the bound.** Patch the `adds r0,#0xc5` immediate at file `0x125E2`
   to `0xc5 + N`. `adds` carries `imm8`, so the encodable ceiling is
   `0xff + 0xff = 510` rows, i.e. **58 authored maps**; 59 fails closed.
3. **Give the new row its own root.** `MapEntry+0x2C` is a word whose value is
   the selector-1 root. Both the word and the root are emitted above EOF. The
   engine already follows an above-EOF pointer held in a root
   (`u32(root+0x14)` = `0x08800030`, runtime-proven in
   `docs/research/MAP_RESIZE_AND_LAYERS.md:224-243`), so this is the same read
   class; the runtime proof settles it rather than assumption.
4. **Carry donor values for every field whose semantics are unresolved.** The
   root (`+0x0c/+0x10`, `+0x24/+0x28`, `+0x34/+0x38`, `+0x3C`, `+0x48`, `+0x4C`)
   and the record's `unknown_0a/0b/0c` and pointer words are copies of a named
   donor's own bytes. This is the same rule the shipped resize path already uses
   for layer fields it cannot name (`docs/PROJECT_STATE.md:418-426`), not a new
   licence to invent semantics.
5. **Compose the shipped authoring authorities** for the map's content: layer
   records through `LAYER_RECORD`, the root's slot pointers, the extent words,
   transitions through the existing creation authority.

Layers and chunks may be **shared** with the donor: layer records are already
shared canonically (1464 unique records behind 1808 references, 35 shared) and
chunk bodies are shared across maps (160 of 165 reused bodies cross a map
boundary). Sharing is the lazy correct choice for v1 and needs no new
allocation kind.

## 5. Reachability: the door into the new map

Resolution is by key, so a retail map can reach the new one as soon as a
transition record names the new row's two bytes. The shipped creation authority
already writes such a record, but it resolved every destination through the
canonical table, so an authored index was outside its declared range. The seam is
therefore one fact, not a second implementation of the record:

```
AuthoredMapFact(index, key, extent_x_raw, extent_y_raw)
```

`tools/webfoot/map_transitions.py` takes a tuple of those on
`read_map_transitions`, `_read_corpus` and `materialize_transition_creations`, and
uses them in exactly two answers: `MapTransitions.key_for` (through the extended
key list) and `destination_bounds` (from the stored halfwords instead of from a
table the image does not hold). Everything else about creating a transition -
the same-map 566-class template, the region, the arrival inside the destination's
extent, the expanded pointer array, the `root + 0x40` count and the
`root + 0x44` pointer - is the shipped code, unchanged.

`map_authoring.authored_map_facts` states the facts from the project document plus
the donor's own root, and three callers use it: the build domain, the transition
authoring API (`set_transition_creations`, `set_transition_edits`) and the Warps
editor, so the destination a surface offers, the destination an authoring check
accepts and the destination a build writes are one set.

Measured, one authored map (donor 40, key `0x9901`) plus one created transition
from map 40 into it, built from the canonical image:

| property | value |
| --- | --- |
| relocated table | file `0x800070`, address `0x08800070`, 453 rows |
| count immediate | `0x30C6` = 453 |
| new row | index 452, key bytes `0x99 0x01`, root `0x08800044`, BG0 slot `0x08800024` |
| source map 40 root | count 2 -> 3, array `0x08800000` |
| created element | index 2 -> record `0x0880000C` |
| created record | class `0x08007675`, destination bytes `0x99 0x01`, arrival `(0x40, 0x40)` |
| canonical bytes changed elsewhere | `0` |
| rebuild | byte-identical |

## 6. What is genuinely new code

| piece | authority today |
| --- | --- |
| the map table as a relocatable anchor | absent: published as `kind="record_table"` (`tools/webfoot/atlas_producers/seed.py:293`), not in `layout.RELOCATION_ELIGIBLE_KINDS` |
| allocation kinds for the table, the `+0x2C` word and the root | absent from `AllocationKind` |
| the two executable/data patches | absent: no SDK path patched an instruction or a pool word |
| a project document for a created map | absent: `maps/maps.toml` is keyed by canonical index and requires `raw` |
| a root emitter | absent: `materialize_map_structure` reads the root and writes only its slot words and extents |
| authored rows in the transition corpus | absent: every answer resolved against the canonical table |
| a product entry point | absent: no create-map action in the Maps editor or CLI |

Everything else the roadmap listed for this capability already ships:
dimensions/layers/chunks, placements, graphics, dialogue, warps/connections,
deterministic build and provenance.

## 7. Plan and status

1. **Evidence and census test.** Done:
   `tests/integration/test_map_authoring_rom.py` re-derives both patch sites and
   the count helper's single caller, so removing a consumer fails the test.
2. **Project document.** Done: `maps/authored.toml`, `AuthoredMap` /
   `AuthoredMaps`, a narrow writer that deletes an empty file, a reader that fails
   closed on an unknown or missing key.
3. **SDK planner.** Done: `tools/webfoot/map_authoring.py` plans the relocation,
   the `+0x2C` word, the root and the layer copy through `allocation.allocate`,
   and refuses an unrecognised canonical image, a missing donor, a duplicate key
   and the 59th map.
4. **Build and validate wiring.** Done: one domain in `build.py` after the
   transition creations, plus `_check_authored_maps` in the validate pass.
5. **Reachability.** Done: the `AuthoredMapFact` seam above.
6. **Workbench surface.** Done: the Maps editor's "New map..." command, and the
   Warps editor offers an authored map as a destination.
7. **Runtime. DONE.** The governed stack only: `Start-MgbaSession` through
   `tools/runtime/start_mapnew001_session.ps1`, the observer allowlist, a
   savestate run. The observer is `tools/runtime/mapnew001_live_identity.lua`,
   which derives the loaded row from the engine's own active-MapEntry pointer
   `0x03001980`, the base from the pool word the lookup loads at `0x08008A58`,
   and the row bound from the count helper at `0x080125E0` - so an authored index
   is reported as the row the engine loaded rather than asserted.

   **Instrument check, measured** (26 rows, 25 heartbeats, 0 unresolved): the
   running engine reported `table_base = 0x08800094` and `row_bound = 453`, its
   own readings of the two patches. A savestate written on the canonical image
   restores a canonical-era row pointer (`entry = 0x0808EB68`,
   `versus = prior_table`, key `0x01 0x0b` = map 39), which is the state a
   state-load run starts in and is reported as a state.

   **Accepted run**, derivative sha256
   `A70C9D262947C3E4D38FB82614998938319A08A321B9305DDB70BC5C3B4D51B8`, savestate
   sha256 `CBEB1585EA80DD125B53DE247AE441B94BACFA4C2402C755C9B6DE574FD09417`,
   mGBA `0.11.0.0`, run directory `build/mapnew001/mapnew-retarget-004`:

   ```text
   frame 1      versus=prior_table  key=010b   (restored retail row)
   frame 1200   index=40            key=010c
   frame 1440   index=452           key=9901   source=0x0880001C root=0x08800020 slot0=0x08800000
   frame 1920   index=40            key=010c   (walked back out)
   frame 2040   index=452           key=9901
   frame 2160   index=40            key=010c   (walked back out)
   frame 2400   index=39            key=010b
   ```

   The engine's own loaded row became index 452 - an index the canonical bound of
   452 cannot express - with the authored key `0x9901` and its selector word,
   root and layer slot all above canonical EOF. The player spent the whole of
   frames 1440-1920 and 2040-2160 in the new map and then walked out of it, which
   is both the movement evidence and the return-transition evidence.

   **What the runs taught about the door.** Three configurations were tried
   before the accepted one, and each failure is a fact about the engine rather
   than about the build:

   | configuration | result |
   | --- | --- |
   | created record, template's own region, arrival `(64, 64)`, donor 40 | the retail record's trigger fired instead; the appended record never took the player, and the terrain the arrival landed in was not walkable |
   | created record, whole-map region, arrival `(64, 64)`, donor 40 | the new map loaded (index 452 at frame 2040), but the arrival was land-locked |
   | created record, whole-map region, arrival `(0, 139)`, donor 40 | the new map loaded twice, and the arrival was land-locked again |
   | **accepted**: map 40's existing `40 -> 41` door retargeted at the new map, arrival untouched, donor 41 | the door, the arrival and the destination agree, so the player lands and walks |

   The rule the accepted run follows is the one `warp_randomizer.py` states in
   its own words: a **destination bundle** is the key, the arrival and the
   facing together, and "a destination edit that leaves those behind places the
   player using the *previous* destination's geometry". The three failures were
   that half-edit. A new map inherits its donor's record, root and layer, so the
   donor must be the map whose geometry the door's own arrival was measured for.
   The created-record path is implemented and tested, but its trigger is shadowed
   by a retail record covering the same region, which is a stated limit.

8. **Closure.** Registry `map-new` to `shipped`, rendered status, then independent
   review of the frozen candidate, then integration.

## 8. Risks carried openly

The relocated table means the engine's own base is no longer the profile's
declared address. A reader in this toolkit that reads the map table from the
profile still reads the canonical rows, which are retained verbatim, so a retail
row is still answered correctly; a project-authored row is reached through the
project, not by re-extracting the derivative.

- An above-EOF `MapEntry+0x2C` has no prior observation. It is the read class
  already proven for root slot pointers; the runtime proof is what decides it.
- The engine's fallback when an arrival is `>= 0xFFF8` is not established, so the
  authored transition always carries an explicit arrival inside the new map.
- The SDK's own map viewer reads the canonical address, so a built derivative is
  viewed through its project, not by re-extracting it. Stated as a limit.
- A new map name is out of reach: the text pointer table has no growth path, so
  a created map reuses an existing text id the way authored appearances do.
