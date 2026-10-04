# SPRITE-NEW-BEHAVIOR-REGISTRATION-001: what populates `actor + 0x1B0`

Baseline `0ff29c1d32f20a1fd40b2618366ae476d865efb6`. Ticket worktree
`C:\Dev\log1-remake-sprite-new-behavior-001`, branch
`ticket/sprite-new-behavior-001`. Canonical image read only throughout and
re-verified after every run
(`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`).

## Verdict

The dispatch table at `actor + 0x1B0` is not populated by any registration step.
It is a pointer to a `{count, entry[count]}` array that lives **inside the source
record**, and the record's `+0x18` word names the behaviour entry. The Cui actor
does not receive what comparable retail actors receive because the record it was
cloned from carries a **different class of entry**: the donor is one of the two
stationary map-102 NPCs.

**BEHAVIOR REGISTRATION BOUNDARY: CONFIRMED.**

## 1. The writer

`0x0800A93C(block, table)` is the only writer. It is reached from the actor
constructors, and it is three stores:

```text
0800a93e  adds r4, r1, #0     ; r4 = table
0800a94e  movs r1, #0xff
0800a950  strb r1, [r0, #4]   ; block[+0x04] = -1        (signed byte index)
0800a952  movs r1, #0
0800a954  str  r1, [r0, #0]   ; block[+0x00] = 0         (current node)
0800a956  str  r4, [r0, #8]   ; block[+0x08] = table     <-- the answer
```

The dispatcher `0x0800A95A` then walks `block[+0x08]` as `table[0] = count`,
`table[1 + index] = entry`, calls `*(entry)` and stores the result in
`block[+0x00]`. Both the block and the table are per actor; only the block is
allocated per actor, and the table is always a pointer into a record.

| class | block | table passed to `0x0800A93C` | source |
| --- | --- | --- | --- |
| map-102 family (factory `0x08017DA3`) | `actor + 0x1B0` | `record + 0x14` | `0x08017DA2 -> 0x08017C1C -> 0x080110D8` |
| `0x0800FD55` placement family | `actor + 0x22C` | `record + 0x18` | `0x0800F68C` |
| third authored family (`0x080111A8`) | `actor + 0x1B0` | `record + 0x10` | `FUN_080111A8` |

The offset is a property of the record family, not of the actor. Inside the
map-102 family the chain is exact: `0x08017DA2` passes `record + 0x0C`,
`record + 0x14` and `record + 8`; `0x08017C1C` forwards `record + 0x14` as
`0x080110D8`'s third argument; `0x080110D8` does
`adds r0, +0xFF; adds r0, +0xB1` (= `+0x1B0`) and calls `0x0800A93C` with it and
that third argument. `0x080110D8`'s other constant, `0x03001B0C`, is a **different**
thing: it is the third argument of the shared actor base initialiser
`0x0800FD74 -> 0x0800F58C -> 0x0800EB60`, not the dispatch table.

## 2. The deciding input

For the map-102 family the record is `[0x1C-byte header][behaviour template]`:

```text
+0x00 factory (0x08017DA3)   +0x04 +0x08 position / data
+0x0C data pointer           +0x10 sprite id
+0x14 COUNT                 +0x18 ENTRY[0]  -> the dispatched node
+0x1C entry[0]'s own body (the template the NEXT record's +0x18 names)
```

So the deciding input is `*(record + 0x18)`, and the first word of that node is
the handler the dispatcher calls. Two handler classes appear on map 102:
`0x0800A7A1` (a 0x58-byte walking behaviour built by `0x0800A7A0`) and
`0x0800A223` (an 8-byte behaviour built by `0x0800A222`).

## 3. Retail measurement (canonical image, cold boot, map 102)

Run `br003-retail`. The installer channel `0x0800A93C` gives the table for every
actor; the dispatcher channel `0x0800A9A4` gives the entry it hands over.

| record | sprite | table | count | entry | `[entry]` | moves |
| --- | --- | --- | --- | --- | --- | --- |
| `0x08078348` | 36 | `0x0807835C` | 1 | `0x08078338` | `0x0800A7A1` | yes |
| `0x08078374` | 181 | `0x08078388` | 1 | `0x08078364` | `0x0800A7A1` | yes |
| `0x080783A0` | 261 | `0x080783B4` | 1 | `0x08078390` | `0x0800A7A1` | yes |
| `0x080783CC` | 180 | `0x080783E0` | 1 | `0x080783BC` | `0x0800A7A1` | yes |
| `0x080783F8` | 294 | `0x0807840C` | 1 | `0x080783E8` | `0x0800A7A1` | yes |
| `0x0807841C` | 204 | `0x08078430` | 1 | `0x08078414` | `0x0800A223` | no |
| `0x08078440` | 69 | `0x08078454` | 1 | `0x08078438` | `0x0800A223` | no |
| `0x0807846C` | 69 | `0x08078480` | 1 | `0x0807845C` | `0x0800A7A1` | yes |
| `0x08078498` | 69 | `0x080784AC` | 1 | `0x08078488` | `0x0800A7A1` | yes |

Every table is exactly `record + 0x14`, every count is 1, and every entry is
`*(record + 0x18)`. Seven of the nine constructed actors dispatch a class-A node
and their `+0x1A0/+0x1A4` position words change across the run; the two that
dispatch a class-B node do not move. The count is a real field and not a
constant: map 103's actor (frame 1106) dispatches a table with count 12 and
twelve entries.

## 4. Why Cui does not get a moving actor's entry

SPRITE-NEW-RUNTIME-001's record at `0x08801F38` was cloned from the retail donor
`0x08078440` and differs only in position and sprite id, so it inherited the
donor's `+0x18` verbatim:

```text
0x08801F38 +0x14 = 0x00000001
0x08801F38 +0x18 = 0x08078438   <- the donor's stale value, class word 0x0800A223
0x08801F38 +0x1C = 0x0800A7A1   <- its own template, never named by +0x18
```

`0x08078440` is one of the **two stationary NPCs** on map 102 (section 3). Its
`+0x18` names the class-B node that belongs to `0x0807841C`, so the clone selects
a stationary behaviour class by exactly the same rule that makes its donor
stationary. Nothing failed to register: the block, the table, the count and the
entry are all present and correct, and the dispatcher does run for it. The entry
simply names the wrong class of behaviour.

## 5. The experiment

`tools/research/sprite_new_behavior_registration.py` reproduces
SPRITE-NEW-RUNTIME-001's image byte for byte and then changes **one word**:

| image | sha256 | new record `+0x18` |
| --- | --- | --- |
| `before` | `29f9195a...` (the runtime ticket's recorded build, reproduced) | `0x08078438` (inherited) |
| `after` | `9e384a7bab58ff7190d70e077a0fbf152c4c8a82b335d9338062e2fc312713ce` | `0x08801F54` = the record's own `+0x1C` |

Three bytes differ (`0x00801F50..0x00801F52`; the high byte `0x08` is shared), no
canonical byte changes, and the script refuses to emit an image otherwise. The
record's own template is asserted byte-identical to the retail template at
`0x0807845C`, which is the entry retail record `0x0807846C` (sprite 69, the other
half of the same donor pair) dispatches and which moves. The `after` arm
therefore gives Cui exactly the registration condition of a comparable, moving
retail actor, and nothing else.

## 6. Runtime before / after

Observer `tools/runtime/spritenew004_registration.lua` (read only, allowlisted).
Cold boot with the recorded private save, `menu` schedule, map 102, 1800 frames.

| measurement | before (`br009-before`) | after (`br010-after`) |
| --- | --- | --- |
| installer blocks | 11 (10 map-102, 1 map-103) | 11 |
| Cui block / actor | `0x0202D27C` / `0x0202D0CC` | `0x0202D27C` / `0x0202D0CC` |
| Cui table | `0x08801F4C` = record `+0x14` | `0x08801F4C` = record `+0x14` |
| Cui count | 1 | 1 |
| Cui entry handed over | `0x08078438` | **`0x08801F54`** |
| entry's class word | `0x0800A223` | **`0x0800A7A1`** |
| class-A behaviour objects built | 7, none for sprite 307 | **8, one for record `0x08801F38` sprite 307** |
| Cui behaviour object | none | `0x0203C428`, target word `+0x24` `0x254 -> 0x234` |
| Cui actor position `+0x1A0/+0x1A4` | `0x0000D100 / 0x00024400` to same | `0x0000D100 / 0x00024400` to same |
| retail movers (7 class-A records) | all change position | all change position |
| retail non-movers (`0x0807841C`, `0x08078440`) | unchanged | unchanged |
| canonical image after run | unchanged | unchanged |
| source save after run | unchanged | unchanged |

Answers to the ticket's observation list: a behaviour entry exists in **both**
arms, the dispatcher receives it in **both**, and in the `after` arm the engine
builds the walking behaviour object for the Cui record. Cui's own position words
do not change in the measured window, so "Cui begins normal movement" is **not**
yet demonstrated.

## 7. Instrument notes

1. **Breakpoint sites that are silent while their neighbours fire.**
   `0x0800A95A` and `0x0800A222` / `0x0800A7A0` entry breakpoints reported no hit
   in this ticket's sessions while `0x0800A93C`, `0x0800A9A4` (inside the same
   dispatcher as `0x0800A95A`) and `0x0800A7C0` (inside `0x0800A7A0`) all fired.
   The earlier ticket's zero-hit report on `0x0800A9A4` did **not** reproduce: it
   fires here, once per actor per run. Callback-entry sites are therefore not
   used and every channel is a site inside the routine it reports on.
2. **A swallowed callback error looks exactly like a dead site.** The first
   corrected observer arm produced an empty dispatch channel with zero actor
   samples because `local table = r32(...)` shadowed the Lua `table` library and
   `table.concat` raised inside the callback. The observer now wraps every
   callback in `pcall` and writes the message to `error.txt`; the same run
   reported `attempt to index a number value (local 'table')` verbatim.
3. **Launcher defect fixed.** `start_spritenew001_session.ps1` passed
   `-PostCommand ''` to the injector; Windows PowerShell's `-File` argument
   parsing drops the empty argument and the injector aborts with `Missing an
   argument for parameter 'PostCommand'` before the observer is sent. The switch
   is now omitted when there is no state to load. This is why a cold-boot run
   could not be launched from the merged tree at all.
4. A run launched without `-SavePath` boots a new game and never reaches map 102.
   The two arms here both staged the recorded save, and the finisher re-verified
   the source save and both images afterwards.

## 8. Acceptance

- **Writer / populator routine:** `0x0800A93C`, called by the actor constructors,
  writes `table` into `block[+0x08]`.
- **Exact deciding input, proven at runtime:** the record's `+0x14` count and
  `+0x18` first entry; the dispatched node is `*(record + 0x18)` and its first
  word selects the handler class.
- **Why Cui differs:** its record was cloned from a stationary donor and
  inherited that donor's `+0x18`, a class-B (stationary) entry. This is the same
  rule that keeps the donor static.
- **Smallest remaining unknown:** with a class-A entry the behaviour object is
  built and stepped (its target word changes), but the actor's own position does
  not move. The clone still carries the stationary donor's other inherited
  fields, and `+0x0C` (the per-record data pointer, kept by the actor at
  `+0x1D0`) is the first candidate.
- **NOT done, deliberately:** no productization of sprite-new, no further Cui
  animations, no direction mapping, no dialogue, no composition budget, no
  placement redesign.
