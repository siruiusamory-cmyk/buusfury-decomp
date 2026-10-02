# Authored behavior trigger - TOOLKIT-034

Evidence for Required Work item 1, the bounded external-research pass, and the
scheduler-versus-trigger question it exists to inform.

This document records what outside sources establish, what they do NOT establish,
and which claims therefore still require runtime evidence from this project. It
deliberately separates the two, because the value of the external pass is that it
supplies an independent vocabulary for the engine rather than a second opinion
formed from our own traces.

## EXTERNAL TRIGGER OBSERVATION

### 1. The engine has a first-class trigger concept with a bounded array

The Legacy of Goku II Japanese release retains a C++ assertion string that the
USA release does not:

```text
K:\Source\GameData.cpp    Index < NumberOfTriggers
```

Recorded by The Cutting Room Floor's Legacy of Goku II article, in its
Development-Related Text section
(<https://tcrf.net/Dragon_Ball_Z:_The_Legacy_of_Goku_II>).

Three things follow from the assertion's own wording, without interpretation:

- The engine's own name for the concept is **trigger**, not event, not schedule.
- Triggers live in an **indexable array with a known count**, since the assertion
  bounds an index against `NumberOfTriggers`.
- That array is owned by **`GameData`**, which in this engine is the
  save-persisted game-state module, not by `MapManager` or the sprite system.

The last point is the useful one. A trigger indexed out of `GameData` is
per-save progression state. That is a categorically different mechanism from an
actor being ticked while it is resident on a map, and it gives us a concrete
alternative hypothesis to test against our own traces rather than only a vague
"maybe it is the scheduler".

### 2. Verified against the real ROMs rather than trusted from the wiki

TCRF's table was checked byte-for-byte against the canonical images in this
project rather than accepted on the wiki's authority.

Legacy of Goku II USA, `Dragon Ball Z - The Legacy of Goku II (USA).gba`, the
four documented USA offsets are exact:

| Offset | String recovered from the ROM |
|---|---|
| `0x0042F4` | `K:\Source\CharacterData.cpp` + `Unable to find sprite index in character display data` |
| `0x00A0F4` | `K:\Source\ByteCodeInterpreter\ByteCodeFunctionList.cpp` + `CharacterSpecialAttack() is deprecated` |
| `0x00B148` | `K:\Source\ByteCodeInterpreter\ByteCodeVariableList.cpp` + `Unable to set variable` |
| `0x00EBDC` | `K:\Source\AreaEntry.cpp` + `Unable to find area` |

So TCRF's transcription is reliable, which is what licenses using its
Japanese-version rows as evidence at all.

**`NumberOfTriggers` is Japanese-release-only.** A literal search of both
canonical USA images returns zero occurrences of `NumberOfTriggers` and zero of
the bare substring `Trigger`:

| Image | `NumberOfTriggers` | `Trigger` |
|---|---|---|
| Buu's Fury USA | 0 hits | 0 hits |
| Legacy of Goku II USA | 0 hits | 0 hits |

### 3. Buu's Fury keeps the filenames but not the assertion messages

Buu's Fury USA retains the same C++ source-path debris under a different drive
letter, `T:\Source\` where Legacy of Goku II used `K:\Source\`:

| Offset | String |
|---|---|
| `0x004822` | `T:\Source\GameData.cpp` |
| `0x008A66` | `T:\Source\AreaEntry.cpp` |
| `0x00416A` | `T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp` |

`GameData.cpp` is therefore present in Buu's Fury as a compilation unit, which
is consistent with the trigger array surviving into this game. But the assertion
**text** was stripped from the release build, and a scan for 32-bit pointers to
each of those three string offsets finds **no code references at all** to any of
them. They are dead debris in a release build, not a live diagnostic path.

That is an important negative: the external sources tell us the concept exists
and what the developers called it, and they give us nothing whatsoever about
where the array lives in Buu's Fury, how wide an entry is, or how a trigger is
evaluated. Those remain ours to establish.

### 4. Prior art surveyed, and what it does not cover

Four community reverse-engineering efforts on this exact engine family were
reviewed for existing trigger documentation:

| Project | Scope | Covers triggers? |
|---|---|---|
| [Arefu/Legacy](https://github.com/Arefu/Legacy) | LoG/LoGII/Buu research, IDA Pro, asset compression, character IDs, string tables | No |
| [spicybung/DragonByteZ](https://github.com/spicybung/DragonByteZ) | Analyzer for ALGP/ALFP/ALFE/BG3E: header, graphics, soundtrack, decompression | No |
| [4cecoder/webfoot-engine-recovery](https://github.com/4cecoder/webfoot-engine-recovery) | IDA plugin: memory segments, player-state structs, debug artifacts, text tables | No |
| [Data Crystal, Buu's Fury](https://datacrystal.tcrf.net/wiki/Dragon_Ball_Z:_Buu%27s_Fury) | ROM map, character codes, palette recolor hacks | No |

Every one of them stops at assets, text, graphics, audio, and player stats. None
documents the event or trigger system, the bytecode dispatch path, or object
lifetime. Arefu's own project summary says the state of the art plainly: the
games "compress the ever living hell out of basically everything... and it seems
no one has bothered to document how".

This satisfies the objective exemption for deriving freely: the named searches
for existing implementations found none covering trigger semantics, and the four
projects above are exactly where such work would live if it existed.

### 5. Player-visible trigger vocabulary from walkthroughs

Walkthrough coverage was consulted for the player-facing side of the same
question, mainly the GameFAQs guides index and the SayainPrince guide
(<https://gamefaqs.gamespot.com/gba/920530-dragon-ball-z-buus-fury/faqs>).

Two shapes of scripted moment recur, and they are worth distinguishing:

- **Threshold-during-combat.** The Majin Vegeta fight ends on damage taken, not
  on death: "At three-fourths of his health gone, the screen will fade" into a
  cutscene. The condition is evaluated against a live combat stat.
- **Progress-gated area events.** Entering an area produces a fixed scripted
  event, as with Gotenks meeting Buu on entry to West City.

Both are consistent with a `GameData`-owned trigger array being consulted, and
neither is consistent with an actor merely being ticked. Note, though, that this
is genre-level corroboration only. A walkthrough describes what a player sees; it
cannot attribute an engine mechanism, and nothing here is treated as evidence of
one.

## WHY IT IS USEFUL AS A CONTROL

The external pass earns its place by supplying a **falsifiable alternative** to
the reading our own traces invite, which is the specific failure mode the ticket
asks us to guard against.

Our runtime evidence shows the authored descriptor being reached through an
object-lifetime path. The external evidence says the engine separately maintains
a bounded, `GameData`-owned, save-persisted trigger array. Those are different
mechanisms, and they predict different observations:

| If the mechanism is | Then the condition should | And repetition should |
|---|---|---|
| A `GameData` trigger | survive a reload, being save-persisted | be gated after first fire |
| Object lifetime | reset with the object on every map load | repeat on every teardown |

That gives runtime trials something to decide between, rather than only
confirming that dispatch happened. It also sets the naming bar: an author-facing
name may claim a gameplay condition only if the trial distinguishes these two.

The walkthrough material supplies the canonical positive control's vocabulary,
and the Majin Vegeta threshold is the reminder that "the fight ended" and "the
enemy died" are not the same predicate in this engine.

## WHAT THE EXTERNAL PASS DOES NOT ESTABLISH

Recorded explicitly so nothing here is later mistaken for a settled mechanism:

- Where Buu's Fury stores its trigger array, how many entries it has, or an
  entry's layout. `NumberOfTriggers` is a Japanese Legacy of Goku II string, and
  no equivalent survives in either USA image.
- Whether the destructor path our traces observed
  (`0x08011A3A` / `0x08011A40` / `0x08011A5C`) is related to the trigger array at
  all. No external source describes that path.
- Whether the engine has a defeat predicate distinct from object teardown.
- Any mapping from a placement type to a trigger.
## RESOLVED: `on_defeat` IS THE CORRECT NAME

Recorded in the repository's `OLD CLAIM` / `NEW EVIDENCE` / `RESOLUTION` form,
because a hypothesis stated in this document was refuted by measurement and must
not be quietly dropped.

**OLD CLAIM.** Before the runtime trials, this document argued that the evidence
supported something closer to `on_object_release` than `on_defeat`. The
reasoning was that the only attributed capture available at the time,
`build/toolkit031/tk034-no-kill-03/`, was labelled **no-kill** yet still showed
the destructor path reaching the authored descriptor: `ACTOR-EVENT-CREATE`,
`DESTRUCTOR-FIRST-DECISION` x8, `DESTRUCTOR-DECREMENT` x8,
`DESTRUCTOR-DISPATCH` and `TRAMPOLINE`, every row noting `semantics UNKNOWN`.
A repeated decrement followed by a single dispatch is the shape of a
reference-count teardown, which is object lifetime rather than a defeat
predicate. `CONFIRMED_ENEMY_STAT_LINK` was also observed to be computed at
`tools/webfoot/entities.py:54` as merely "has a linked enemy stat record",
which says nothing about when the descriptor is consumed.

That claim rested on reading the capture's FILENAME as its contents, and it is
WITHDRAWN. A filename is not evidence. The claim that `tk034-no-kill-03`
demonstrates authored behavior firing WITHOUT a defeat is false and is
withdrawn with it.

**NEW EVIDENCE.** One clean replacement run, `tk034-trial-d-20260910-D2`,
supersedes the earlier trials. It is a SINGLE capture containing both halves of
the A/B, produced by the current final observer, so the negative and the
positive share one instrument, one load and one residency proof. Frames 9120,
generated image
`bbd0bbbe1f01b4d715b89bb20a22f63276e36ec4fd2dc443e34ae3b99880ff35`, canonical
ROM verified unchanged before and after.

*Phase 1, alive window, frames 1440 to 8820.* The authored actor `0x0203CE58`
was positively resident and alive across **124 consecutive `ACTOR-HEARTBEAT` /
`AUTHORED-ACTOR-ALIVE` samples**, each re-validating the actor's `+0x228`
attachment against the authored descriptor `0x087EA420` before reading its HP.
Observed HP was `0x0002BC00` for 123 samples; one HP sample at frame 8820
showed the authored actor damaged but still alive, at `0x00019A8C`. Across that
entire window there were **zero** `SCRIPT`, `NATIVE-OPCODE`, `NATIVE-HANDLER`,
`TRAMPOLINE`, `DESTRUCTOR-DISPATCH` and `SCREENSHOT` rows.

This is the negative control the ticket asked for. The authored entity was
resident and alive throughout, and one HP sample at frame 8820 showed it damaged
but still alive, with no authored behavior started. That single damaged sample
is the whole of the damage observation and is not generalised further here.

*Phase 2, defeat, frames 8879 to 8902.* The complete causal chain:

| Frame | Row | Detail |
|---|---|---|
| 8879 | `DEATH-CALLBACK` / `AUTHORED-ACTOR-DEATH` | actor `0x0203CE58`, descriptor `0x087EA420`, HP `0` |
| 8879 | `ACTOR-EVENT-CREATE` / `AUTHORED-ACTOR` | `0x0800F868` |
| 8880-8887 | `DESTRUCTOR-FIRST-DECISION` x8, `DESTRUCTOR-DECREMENT` x8 | `AUTHORED-EVENT-OBJECT` |
| 8887 | `DESTRUCTOR-DISPATCH` | `0x08011A5C` |
| 8887 | `TRAMPOLINE` / `AUTHORED-DESCRIPTOR-PAYLOAD` | descriptor `0x087EA420`, payload `0x087EA428` |
| 8887 | `SCRIPT` / `AUTHORED-SCRIPT` | authored script cursor |
| 8887 | `NATIVE-OPCODE` / `AUTHORED-NATIVE-SLOT-178` | slot `0xB2` |
| 8887 | `NATIVE-HANDLER` / `AUTHORED-NATIVE-178-EXPECTED-ARGS` | depth 3, args 1525 / 120 / 105 |
| 8888, 8892, 8902 | `SCREENSHOT` / `AUTHORED-EFFECT-CAPTURED` | `MATCH 2 FIGHT!` visible |

The banner is confirmed in the captured frames and was separately seen live by
the operator; keep the latter as a FIRSTHAND USER OBSERVATION, distinct from the
captured evidence.

A second capture, `tk034-trial-d-20260910-D1`, independently reproduces the
Phase 2 chain from a separate load: `DEATH-CALLBACK` at frame 6642 through
`NATIVE-HANDLER` at 6650 with the same descriptor, slot and arguments, and the
banner captured. Its alive window carries no evidence, for the instrumentation
reason recorded below, so only its defeat chain is cited. That capture also
contains two `CANONICAL-NULL-ACTOR-DEATH` rows at frames 6440 and 6517,
descriptor `0x080555A0`, which is the canonical positive control: the death
channel is shown detecting known kills, so a later silence is a real negative
rather than an unproven instrument.

**RESOLUTION.** The `on_object_release` hypothesis is REFUTED. A resident,
alive authored entity produced zero authored starts across roughly 7,400
measured frames, while defeat ran the authored script and rendered the banner in
both D1 and D2. Defeat is the discriminator, so `on_defeat` is the correct and
appropriately narrow name.

One limit of this evidence is recorded rather than smoothed over: in both runs
the authored script is reached exclusively through `DESTRUCTOR-DISPATCH`. There
is no capture in which the script runs without teardown, nor in which this
object's teardown occurs without the script running. Defeat and teardown are
therefore CONFOUNDED in the measured data. Separating them would require
reverse engineering this ticket explicitly scopes out, so `on_defeat` is named
after the observed gameplay condition, not after a mechanism the evidence can
isolate.

| Observation | Defeat? | Entity resident and alive? | Authored script ran? |
|---|---|---|---|
| D2 alive window, frames 1440-8820 | no | **yes, 124 positive samples, HP > 0, one damaged sample at frame 8820** | **no** |
| D2 defeat, frames 8879-8887 | yes | n/a | yes, banner |
| D1 defeat, frames 6642-6650 | yes | n/a | yes, banner |
| D1 canonical control, frames 6440/6517 | yes, non-authored | n/a | n/a, proves death channel live |

**SCHEDULER VERSUS TRIGGER.** These calls are not ordinary actor ticking. Under
the ticket's Phase A distinction, ticking would dispatch on some schedule
regardless of gameplay state. It does not: across roughly 7,400 frames with the
authored entity positively sampled as resident and alive, zero authored script
starts occurred, and the script ran only after a defeat, within eight frames of
a measured HP-zero death callback for that specific actor. The observed calls
are therefore a **trigger**, not scheduler time.

**WHAT THE TRIGGER DECLARATION ACTUALLY DOES.** `on_defeat` exposes and
validates an EXISTING engine trigger contract for the authored placement type.
The trigger declaration itself adds no new ROM bytes; it provides semantic
authoring attribution and validation over the engine behavior already
represented by that placement/behavior structure. Webfoot does not inject a new
trigger mechanism, and this document does not claim it does. The engine
relationship remains the ordinary placement-record `+0x14` descriptor pointer.

Note also that the `+0x14` binding is traversed during object teardown as well.
What defeat gates is execution of the authored SCRIPT, which is the
author-visible effect this trigger names.

## INSTRUMENTATION NOTES

**The alive window needed a channel that did not previously exist.** Every other
channel in `tools/runtime/toolkit034_dispatch_caller_watch.lua` is
breakpoint-driven, so an authored actor sitting alive and untouched wrote no row
at all: its residency and HP went unrecorded and an alive window was
indistinguishable from an absent entity. That is why the earlier dedicated
trigger-negative attempts carry no weight. A read-only `ACTOR-HEARTBEAT` channel
was added for the replacement run: it re-acquires the authored actor by scanning
EWRAM for an object whose `+0x228` is the authored descriptor, re-validates that
attachment on every sample, and writes residency and raw HP every 60 frames. It
uses `emu:read*` only; the observer remains read-only and
`tests/unit/test_mgba_capture.py` passes unchanged.

`tk034-trial-d-20260910-D1` was run before that channel worked correctly. Its
heartbeat latched the actor address from the `0x0800F866` event-object creation
breakpoint, which the D1 timeline shows firing at frame 6642, the same frame as
the death callback, so the latch could only ever populate post-mortem. D1's
alive window is therefore empty by construction and is not cited as a negative;
its defeat chain is unaffected and is cited.

**`tk034-no-kill-03` is historical only.** Its label describes only its first
phase; the capture record shows a kill was requested and performed
mid-capture, so its completed chain belongs to that kill. Its pre-kill segment
may be cited as supporting context. Its missing `DEATH-CALLBACK` row is NOT used
for any claim, and no explanation for that absence is offered here. The
replacement run supersedes it, and no further forensic reconstruction of that
capture was performed.

**HOW TO READ `map_index` IN THESE CSVs.** `current_map()` is called only from
`write_row` (`tools/runtime/toolkit034_dispatch_caller_watch.lua:105`), so the
map is sampled only when some other breakpoint has already produced a row. The
`maps seen` line in a finish summary is therefore a statement about when rows
were written, not a positional claim. With the heartbeat channel active this
caveat is much weaker, since the heartbeat itself writes rows on a fixed
cadence and samples the map with them.

## Sources

- The Cutting Room Floor, Legacy of Goku II: <https://tcrf.net/Dragon_Ball_Z:_The_Legacy_of_Goku_II>
- Data Crystal, Buu's Fury: <https://datacrystal.tcrf.net/wiki/Dragon_Ball_Z:_Buu%27s_Fury>
- Arefu/Legacy: <https://github.com/Arefu/Legacy>
- spicybung/DragonByteZ: <https://github.com/spicybung/DragonByteZ>
- 4cecoder/webfoot-engine-recovery: <https://github.com/4cecoder/webfoot-engine-recovery>
- GameFAQs guides index, Buu's Fury: <https://gamefaqs.gamespot.com/gba/920530-dragon-ball-z-buus-fury/faqs>
- Hidden Palace, Buu's Fury prototypes: <https://hiddenpalace.org/Dragon_Ball_Z:_Buu%27s_Fury_(prototype_A)>

Canonical images used for verification, unmodified and read-only:
`Dragon Ball Z - Buu's Fury (U).gba` and
`Dragon Ball Z - The Legacy of Goku II (USA).gba`.
