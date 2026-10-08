# The delivered friend v3 image: the crash, the tail, and a stability pass

Ticket: FRIEND-V3-FINAL-STABILITY-001. Verdict: **PASS, safe to deliver**, with the two
standing risks in section 7. Baseline `origin/master` `f3955e1b`, branch
`ticket/friend-v3-final-stability-001`.

Claims carry `CONFIRMED`, `INFERRED` or `UNKNOWN`, with `LEVEL 3` and `LEVEL 4` for the
runtime ones, as `docs/DEVELOPMENT.md` requires. The private friend images and saves are
not in this repository, so the v3 numbers cannot be reproduced from a clone; every image
and save used is hashed here instead.

**No byte of any ROM was changed by this ticket.** The two items it was asked to
investigate are both already resolved in the delivered image, one by an earlier fix and
one by measurement, and nothing demonstrated needed a third edit. A scripted route driver
was built, found not to work in this environment, and reverted rather than shipped; the
worktree carries this record and nothing else.

## 1. The question, and the answer

| asked | answered |
| --- | --- |
| Is the `F0674DD8` crash caused by the unsafe tail allocation at `0x7B89C0..0x7FFFFF`? | **No.** CONFIRMED twice over: the tail-only build walked the crash route cleanly for 3,600 frames in an earlier session, and the frame-budget audit in section 4 finds the actual cause elsewhere and confirms the fix already present. |
| Is any demonstrated hazard left? | **No.** The composition-budget overflow that caused the crash is fixed in the delivered image, and no slot in it is over budget. |
| Is the ROM safe to deliver? | **Yes**, with the two standing risks in section 7 recorded rather than fixed. |

## 2. Identity

| what | sha256 | bytes |
| --- | --- | --- |
| canonical image | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` | 8388608 |
| the friend's own modded image | `a6f4442290c0fe88b83e6affd0250a7eff28b240e7320e04bba7767aa9f065a1` | 9732800 |
| `v3.gba`, the crash vehicle | `38504057` (prefix; the map-134 fault reproduces on it) | 9740166 |
| `v3-safe.gba`, the fixed base | `b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5` | 9740320 |
| **the delivered image** | `d401d71c0ed3fbf93476aaa1825ea8c680e3caac7f7d7fbc05cbfe16344ab0f5` | 10132968 |
| map-134 route save | `29f89867cdfb1e6e9956f461727b2e01bff91929351bd47e23c2c2a5af44e66a` | 8192 |
| Kibito-scene save (section 6) | `f6d79dc8896c52943da38e012b3dee0bbc119cfd4ac7d54ef3bc0862140315b7` | 8192 |

The canonical image is byte-identical before and after this ticket.

## 3. What the crash actually was, and where the fix lives

CONFIRMED, established in an earlier session and unchanged: ROM `0x0800F380-0x0800F3F6`
composes a character frame. It reads the frame object at `[actor+0x54]`, takes the box
from bytes `[obj+6] x [obj+7]`, and copies each piece's `w*h` bytes into a scratch buffer
the actor structure declares. For slot 292 that buffer is `0x200` and its canonical frames
are `16x32 = 512 = 0x200`, an exact fit. The friend's tool resized those frames to
`32x32 = 1024`, so each composition wrote 512 bytes past the buffer, over the actor's own
animation pointer, and the loop then re-read its own corrupted state and copied tens of
kilobytes through EWRAM. That corridor wiped the object at `0x0203DE54`, whose first word
held a ROM code pointer; the engine later computed a call target from it and executed a
wild jump, which is the reported invalid address.

The fix is one field, and it is present in the delivered image:

| image | file offset `0x6B692A` (slot 292 buffer) | largest frame demand |
| --- | --- | --- |
| canonical | `0x200` | 512 |
| friend's original | `0x200` | 1024 |
| `v3.gba`, `v3-final` | `0x200` | 1024 |
| `v3-safe.gba` | `0x400` | 1024 |
| **the delivered image** | **`0x400`** | **1024** |

## 4. The frame-budget audit of the delivered image

Run read-only as a separate analysis, against all three images, from raw piece bytes
rather than
from a decode, so no frame can hide by failing a check. Evidence and scripts under
ignored `build/frame-budget-audit/`.

| measurement | value, identical in all three images |
| --- | --- |
| character slots examined | 297 |
| distinct frame records | 10,980 |
| slot-frame references | 17,331 |
| pieces | 11,005 (10,959 single, 19 double, 2 quadruple) |
| frames skipped by the project's walk | **0** |
| slots whose demand exceeds the declared buffer | **NONE** |

The instrument is proven, because "none" is a negative: the same audit flags **exactly
slot 292** in the friend's original and in `v3.gba`, declared 512, demand 1024, over by
512 bytes, with all eight of its frames over. The known crash is recovered from the bytes
alone. Cross-checked against the project's own `ActorSprites` walk: per-slot animation and
frame sets identical for 297/297 slots. That analysis also caught a real bug in its own
first walk (it iterated `frame_count` pointers instead of `frame_count*4`, seeing one
direction in four) and reports the numbers above only after the fix.

The audit's own limits, recorded: no emulator run, so the runtime allocation of that
buffer from this field was not observed; sprites outside the 297-entry table, frames
reachable only from a record outside the inferred `+0x54` window, container payload
integrity, and per-actor runtime frame selection were not covered.

## 5. The tail window

CONFIRMED, re-measured here rather than quoted:

| measurement | value |
| --- | --- |
| canonical bytes in `[0x7B89C0, 0x800000)` | all `0xFF` |
| bytes the mod wrote over them | **275,033** (identical in the friend's image, `v3-safe` and the delivered image) |
| word-aligned ROM-address pointers into `[0x087B89A8, 0x08800000)` | **99** |
| of those, whose target bytes the mod overwrote | **93** |
| of those, whose stored value the mod changed | **0** |

So 99 canonical references still hold their canonical values and now resolve to bytes a
third party wrote. The intended causal link to the crash was **refuted by measurement**:
a build of canonical plus only those 275,033 bytes walked the map-134 route for 3,600
frames clean, and section 4 shows the crash needed the sprite overrun instead.

The count is sensitive to what is being counted, which is worth recording because a first
pass here got it wrong: the same scan over *file-offset values* rather than ROM addresses
finds 362 dwords, and the mod overwrote none of their targets. Only the ROM-address form
is the population a reader would dereference.

Whether any of the 99 is reachable at runtime, meaning actually loaded as a pointer by
code that runs, is the question that decides demonstrated versus latent. A separate
read-only analysis swept the whole image for literal loads (Capstone, Thumb at both even
parities plus ARM, `skipdata` mandatory because a plain disassembly stops 90 instructions
in and silently yields a three-word scan) and marked 113,083 aligned words as
literal-loaded: **none of the 99**. Under a uniform-random null about 143 would be expected.

| evidence that the 99 are not consumed | value |
| --- | --- |
| source words whose address is materialised by a literal load | **0 of 99** |
| source words appearing as a reference source in the project's own graph | **0 of 99** (graph has 19,720 references over 10,238 anchors) |
| source words with an adjacent ROM-address word | 1 of 99 |
| source words sitting inside verified packed container payload | 42 of 99 |
| source words covered by no anchor at all | 57 of 99 |

The instrument is proven by controls that must fire and do: documented literal pools
resolve 7/7 (the startup code), 51/51 (the text pointer table), 13/13 (the enemy stat
table), 5/5 (the appearance table, reproducing the documented holder offsets), 1/1 (the
map entry table), 1/1 (the portrait array).

**Verdict: LATENT, not demonstrated.** The hazard is real in the bytes - the canonical
image reads `0xFF` where the delivered images read payload, 71 of the 99 target windows
are now entirely non-`0xFF`, and exactly one target, `0x7BB114`, is a kind-1 container
header declaring `0x400` - but no consumer was demonstrated for any of them. The census
was reproduced with the project's own free-space tool: 516 candidates into the window, 99
word-aligned, 95 distinct targets, sources from file `0x073E34` to `0x7AD3C0`, and all 99
source words byte-identical in the canonical image, the friend's image and `v3-safe`.

## 6. Runtime regression on the delivered image

Hand-driven, at the operator's hands, cold boot from the battery save with no savestate,
using the launcher and read-only observer merged by
FRIEND-V3-COLD-BOOT-ACCEPTANCE-001. Two independent runs on the map-134 route:

| run | frames reached | every program counter seen maps to |
| --- | --- | --- |
| 1 | 5,400 | BIOS idle `0x1C4`, IWRAM `0x03000xxx`, ROM `0x0803Exxx`/`0x0803Fxxx` |
| 2 | 4,740 | BIOS idle `0x1C4`, IWRAM `0x03000xxx`, ROM `0x0803Exxx`/`0x0803Fxxx` |

**No program counter in either run lies outside a mapped region** (LEVEL 3): not one
sample in unmapped space, which is what the fault looks like from inside. Both runs show
the player in the world on the tournament grounds, the second mid-dialogue, and the ROM
copy is byte-identical after each run. The route save for this map is the one the earlier
reproduction used.

The positive control is the audit in section 4 plus these preserved traces from the
earlier crash work, same save and same route: `build/crash-repro/run1/live.csv` ends at
map 134 `(306,339)` and `build/crash-repro/fixed-run/trace.csv` ends at the same
coordinate on an unfixed build with **no completion marker**. Those are prior-session
evidence, re-read here, not re-driven: the fault on an unfixed image is already
established and re-driving it would destroy game state for no new information.

**The cold-boot Kibito acceptance is preserved and still applies.** Its evidence is intact
in the cold-boot ticket's own worktree, under its ignored `build/friendv3-coldboot/`
directory (three runs, 122 files), re-read here: 13,440 frames on the delivered image,
6,900 on the known-bad control, 10,440 on the shipped reference. The delivered image is
byte-identical to the image that acceptance passed on, so no regression run is owed.

**The last change disturbed none of the verified content.** Diffed against its base
`v3-safe.gba`: 417 differing bytes inside the shared span, every one below `0x2F0000`,
and **zero** in the sprite and actor structures, the portrait pointer array, the character
stat table, the granted-level bytes, the credits pointer, or the tail window.

## 7. Standing risks, recorded and not fixed

1. **Zero slack on every composition buffer.** The audit found declared size equal to the
   largest single-frame demand on **297 of 297 slots in every image**. No slot has
   headroom, so any future frame growth on any slot overflows it exactly as slot 292 did,
   and the project's container/piece invariant does not catch it: declared size still
   equals the pieces' union, because the violated bound is a runtime buffer the ROM does
   not declare. A writer that resizes a frame should enlarge that slot's field with it.
2. **The tail write is a latent hazard with no demonstrated consumer.** 275,033 bytes of
   the third party's payload sit over the targets of 99 canonical references that still
   hold their canonical values, and none of those 99 is reachable by any instrument
   applied in section 5. Undoing the write would mean relocating that payload and
   repointing the mod's own references, which risks the verified graphics for no
   demonstrated gain. What keeps this a risk rather than a closed matter is the reach the
   instruments do not have: an indexed read through a computed base is invisible to the
   literal-load sweep, and the decompilation map calls only 104 KB of the 8 MB image code,
   though no member of the 99 sits in a region it calls code.

## 8. Limits of this pass

* The audit is static. It did not observe the buffer being allocated at runtime, and the
  delivered image's crash-free behaviour on the route is established by two hand-driven
  runs, not by an unattended campaign over the whole game.
* Scripted menu input did not take effect in this environment: two runs driven by script
  sat on the title screen and honestly recorded `map=-1` for their whole length while
  hand-driven runs in the same harness entered the world. Mechanism not established
  (INFERRED: the front-end owns the key mask while unfocused). The driver was therefore
  reverted, and route regressions here are hand-driven.
* Same save, same route, one operator. A different route is a different experiment.
* **The tail sweep cannot see everything.** It finds PC-relative literal loads. An indexed
  read through a computed base, and whether the record structures two of the 99 sources
  belong to are reachable at runtime at all, are outside it; and the decompilation map
  covers 104 KB of the 8 MB image's code, so a consumer in unmapped code would not have
  been visible. The LATENT verdict in section 5 rests on that static evidence plus the
  3,600-frame A/B, not on a write or read watchpoint.
* Not covered: the `F0674DD8` fault on any route other than map 134; sprites outside the
  297-entry table; and anything the tail write might affect that no measurement has yet
  reached.

## 9. Changes in this ticket

This record only. No ROM, no product code, no tooling. A route driver and its launcher
parameter were written, found not to work here, and reverted before commit.
