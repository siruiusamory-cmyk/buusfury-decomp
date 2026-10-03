# Enemy randomizer: how it was established

Evidence record for `RANDOMIZER-ENEMY-PACK-001`. The proof lives here rather than
in production docstrings, per `docs/DEVELOPMENT.md` ("Put the proof in an evidence
document, never in production source", step 9). Source keeps semantic comments and
points here for measurements and history.

Everything below was measured against the canonical Buu's Fury image
(`buus_fury_usa_rev0_01c1707f`, SHA-256 `940ad5f0...f059e`, 8,388,608 bytes), which
was byte-identical before and after every run described.

## 1. What was measured, and with what

| Quantity | Value |
| --- | ---: |
| reachable placement records | 1,559 |
| maps with at least one placement | 268 |
| distinct type selectors | 125 |
| selectors inside the verified enemy-stat extent | 118 |
| selectors outside it (`141,142,145,146,147,148,149`) | 7 |
| placements carrying a verified script event | 57 |
| placements on the script-dispatch handler with an undecoded root | 7 |
| placements whose selector is outside the stat extent | 15 |
| **eligible `ORDINARY_COMBAT_ENEMY` placements** | **1,480** |
| maps with two or more eligible slots | 236 |
| eligible slots inside a transition (door) rectangle | 2 |
| distinct identities `(stat selector, sprite id)` | 137 |
| distinct behaviour-descriptor pointers | 131 |
| distinct flags words | 57 |
| distinct child-pointer arrays | 56 |

Stat field domains over the stat-linked selectors: `exp` u24 0..236,265 (13 records
hold 0), `hp` u24 1..125,000, `level` u8 1..175, `strength` u8 0..130 (25 zeros),
`power` u8 0..110 (47 zeros), `endurance` u8 0..125 (4 zeros).

## 2. Seed architecture

One master seed derives every module seed as
`sha256(MASTER_DOMAIN | seed | module_id)`, with a domain distinct from the warp
randomizer's (`tools/webfoot/warp_randomizer.py::SEED_DOMAIN`, which is
load-bearing and was not touched).

A module seed is a function of the master seed and that module's own name, so
enabling or disabling a module cannot move another module's result. That is
asserted structurally in `tests/unit/test_enemy_randomizer.py` and end to end in
`tests/integration/test_enemy_randomizer_rom.py`: with the stat module disabled,
the type and placement **decisions** are identical, not merely the summaries.

There is no process-global RNG state and no use of `random` or a salted `hash()`,
so a seed reproduces its mapping in any process on any machine.

## 3. Enemy identity is a pair

`+0x08` is the stat selector (`TOOLKIT-009`: Thumb `0800FD56` loads it, the wrapper
computes `(sel*8-sel)*4 + 08711274`, constructor `0800F68C` receives the record) and
`+0x10` is a sprite id (`HUMAN-4`: `0800F6AE` loads it into resolver `08000158`,
which indexes the character pointer table `0x086B6BDC` at `argument - 10`).

They are not redundant: **7 selectors pair with more than one sprite** in the
canonical corpus - selector 15 with `[70,235]`, 20 with `[78,79]`, 37 with
`[123,124]`, 47 with `[70,141,235]`, 59 with `[36,261]`, 86 with
`[209,211,213,215]`, and 141 with `[10,11,227,253]`. Writing the selector alone
therefore leaves the old sprite behind on those seven.

## 4. Eligibility taxonomy

| Class | Rule | Disposition |
| --- | --- | --- |
| `ORDINARY_COMBAT_ENEMY` | no script attachment, selector inside the verified stat extent | randomized |
| `SCRIPTED_ACTOR` | descriptor carries a decoded script event | refused (`script_event`) |
| `SCRIPTED_ACTOR` | descriptor dispatches through `0x0800421F` but the root was never decoded, or the descriptor is unreadable | refused (`script_unresolved`) |
| `UNKNOWN` | selector outside the verified stat extent | refused (`outside_stat_extent`) |

Two further refusals apply to otherwise-eligible slots: `in_door_trigger` (2 slots,
coordinates inside a transition rectangle) and `alone_in_map` (a map with a single
eligible slot has nothing to shuffle against; 23 such maps in the corpus).

Eligibility never reads a combat stat. No rule consults `hp`, `level`, `strength`,
`power` or `exp`; a focused test asserts that eligible selectors span the full
measured level range rather than clustering at one end.

The `script_unresolved` class exists because `PlacementEvents` returns those seven
with `event is None` by design ("admitting them would promote undecoded roots into
the event corpus on reachability alone, which is not evidence",
`tools/webfoot/placement_events.py`). A placement that dispatches a script is a
scripted actor whether or not this project decoded the script, so reading `None` as
"not scripted" is an inference from absence.

## 5. Compatibility pools

The pool is `PROVEN_CANONICAL`: an identity is an ordered pair that some canonical
placement in this profile actually builds. The full set of candidate dimensions was
checked against the corpus and discarded, and the discards are recorded in
`tools/webfoot/enemy_randomizer/compatibility.py` so a later ticket does not repeat
the search.

The safety argument is internal coherence, not movement class: installing a whole
canonical pair puts stats and graphics together, in the combination the retail
engine itself constructs.

### 5.1 The coupling defect, measured and fixed

An earlier revision wrote only `+0x08` and `+0x10`, leaving each slot's own `+0x04`
flags, `+0x14` behaviour descriptor and `+0x18`/`+0x1C` child pointers. Because the
corpus varies all three (131 distinct descriptors, 57 flags values, 56 child
arrays), the result was an object retail never builds. Measured over seed
`123456789`, of 1,002 type-changed slots:

* **54** received a descriptor that no same-map donor of the installed identity had;
* **46** produced an `(identity, descriptor)` combination appearing nowhere in the
  corpus;
* **734** received a flags value no donor had.

That is the graphics/behaviour/stat hybrid the ticket forbids. The fix permutes
identities only among slots that agree on all the coupled fields, so every
resulting object is one a canonical placement already holds. The measured cost:
**1,263 of 1,465** eligible slots in multi-slot maps keep a same-map peer and still
shuffle.

The invariant is now pinned by
`tests/integration/test_enemy_randomizer_rom.py::TestTypeCompatibility::test_every_resulting_combination_already_exists_canonically`,
which requires the exact tuple
`(selector, sprite, flags, descriptor, child_count, children)` to exist canonically
for every changed slot.

### 5.2 The coupling constraint means this module cannot change enemy type

This must be read together with 5.1, because the safety fix removes the module's
effect entirely. Two independent reviews converged on this, the second after an
earlier revision of this document claimed an opt-in mode solved it.

Within one coupled-field group every member has the *same* flags, descriptor and
children **by construction**, so the records differ only in
`(stat selector, sprite id, position)`. Exchanging `(selector, sprite)` between two
such records therefore produces exactly the same pair of records as exchanging
their positions. With the placement shuffle also enabled, the two modules compose
to the identity.

**Installing the coupled fields as well does not fix it.** The factory word is
constant across the corpus (`compatibility.FACTORY_RAW` is one value), so a record
that receives another's `(type, id, flags, descriptor)` has simply *become* that
record; the map then holds the same multiset of canonical records in different
places. Measured on a hash-verified canonical copy, seed `enemy-pack-001`, type
module only: 949 records changed, 706 of them with flags or descriptor rewritten,
and **0 of 949** lacked an exact canonical match in the same map.

So this module cannot change which enemy a player meets. An earlier revision
claimed an opt-in `proven-pair-and-behaviour` mode did; a reviewer measured it and
showed it relocates whole records, and the mode has been **removed** rather than
relabelled.

**Ticket Module C is NOT delivered.** What the module does deliver is a
well-defined, validated permutation over proven slots. It is correct, it is inert
with respect to the world, and it costs one pass over the corpus, so it stays
compiled and tested rather than deleted - but nothing may describe it as an enemy
type shuffle. Every manifest records this as
`configuration.delivers_ticket_module_c: false` and states the effect verbatim in
`configuration.typing_mode_effect`, together with `modules.enemy-type`.

**What delivering Module C would take.** A measured compatibility dimension: some
evidence that an object whose behavior descriptor belongs to a different enemy than
its sprite and stats is coherent, or a set of identities proven interchangeable on
that dimension. None exists today. The candidate dimensions that were checked and
refused are in §5. The next place to look is runtime: pairing an observed enemy
behaviour with its placement record would give a behavioural class to partition on,
which is the dimension this pack could not derive statically.

## 6. Stat policy

`randomized = clamp(floored(original * factor), floor, ceiling)` with `factor` drawn
from the preset band on a 1,024-step rational grid. Multiplicative around each
record's own value, never a draw from a global range, which is what keeps the
progression curve: a weak enemy scaled by the ceiling stays weak.

Domains are the tighter of the storage width and the authority's own:

* `exp`/`hp` u24, `level` 1..200 (the game's level cap measured at `0x08013A00`),
  `strength`/`power`/`endurance` u8.
* Zero is preserved wherever zero is legal (`exp`, `strength`, `power`,
  `endurance`): it is an authored value, not an unset marker.

`hp` in this record is the **displayed** hit-point value. The oracle is the
repository's own: the wolf is found by `find_enemies_by_hp(175)`
(`tools/webfoot/formats/stat_tables.py`), so the record holds 175 - the number the
player sees. P-010's 1024-raw-units-per-displayed-point figure describes the
runtime actor, a different quantity in a different place. An earlier revision
applied it here, putting a floor of 1024 under a field whose values run down to 1:
**37** stat-linked records were clamped upward whatever the seed and **21** left the
band the preset promises. The floor is now 1.

Stats are randomized per stat record, not per placement, because one record is
shared by every placement selecting it. A selector shared with a refused actor is
vetoed and reported.

## 7. Placement policy

Coordinates are never invented: the shuffle permutes the existing `position_raw`
values among the eligible slots **of one map**, so map membership and the signed
halfword encoding are preserved by construction. The set of occupied coordinates
per map is unchanged.

Same-map is the shipping boundary. A slot inside a transition rectangle is excluded
from the pool.

### 7.1 The door test's axis pairing is an OPEN QUESTION

A region's two intervals are ordered but which is horizontal is UNRESOLVED in the
transition format, while the placement's axes ARE established
(`PLACEMENT-POS-001` Phase 3). The test therefore makes one assignment - placement
X against the region's `first` interval, Y against `second` - and is not
axis-symmetric.

**The unsafe direction is under-reporting.** A slot the test fails to identify is a
slot that gets shuffled, which is the outcome the exclusion exists to prevent; a
false positive only withholds a slot from the shuffle, which is harmless. If the
region's axis order is the opposite of the assignment, every hit is spurious and
every real overlap is missed, so the check degrades to "nothing excluded".

The exposure is **not bounded by the 2 slots reported in section 1**. That count
came from this same one-orientation test, so citing it as the bound is circular. An
earlier revision did exactly that, and a reviewer was right to reject it. What is
established: the transition format does not resolve the axis, the placement format
does, and which pairing is correct has not been measured. Settling it needs either
an instrumented run that records a door rectangle and an actor inside it, or a
transition-format finding that names the axis.

Contrast with section 5.1, which is genuinely bounded: the coupling constraint was
measured by counting donors, not by a test that assumes its own conclusion.

## 8. Module composition

Order is fixed and documented in `tools/webfoot/enemy_randomizer/planner.py`:
classify slots, shuffle identities, shuffle placements, randomize stats, merge each
record's intended fields, encode once, validate as one plan, emit. The type and
placement modules read disjoint fields and never depend on each other; their intents
merge so one record produces one attributed change rather than two overlapping
overwrites.

## 9. Corpus results

`build/census/enemy_seed_corpus.py`, run against the frozen candidate:

* **1,000 seeds attempted, 1,000 accepted, 0 rejected**
* **1,000 distinct manifest ids** (no seed reproduced another's manifest)
* 468 ms/seed, 468 s total
* per-seed means: 467.2 type slots changed, 1,183.6 placements moved, 92.5 stat
  records changed
* nested invariants checked on every seed: canonical pairs only, no invented
  coordinate, per-map coordinate multiset preserved, stats inside domain and band,
  no overlapping change, every excluded actor byte-identical
* build-level corpus, 8 seeds emitted through `apply_plan`: all 8 byte-reproducible

No seed was rejected, so there are no rejection reasons to report.

## 10. Runtime evidence

Cold boot, 28,200 frames, 47 captures:
`build/toolkit031/enemypack001-streamsafe-boot-4`. The randomized image booted from
its own output, loaded **21 maps** (resolved through the engine's live `MapEntry`
pointer at `0x03001980`, base `0x0808E2E0`, stride `0x38`), rendered dialogue
through the script VM (the liveness channel), and drove HUD, player, collision,
scrolling and doors with no crash and no capture showing corruption.

**A/B on the identical savestate** is what proves the enemy change, because the two
runtime edits have different lifetimes: a *map/background* edit is assembled at load
and restored from the savestate, while an *enemy placement* edit is read out of the
ROM when the engine constructs the actors. One savestate
(`roms/...ss1`, SHA-256 `2D5740A8...a1aab`, which loads into map 40) was run against
two images with the live record enumerator
(`tools/runtime/enemypack002_live_slots.lua`) under the tracked launcher:

| Slot (record body) | Canonical | Randomized |
| --- | --- | --- |
| `0x08075638` | type 86, id **209**, pos (176,208) | type 86, id **211**, pos (192,224) |
| `0x08075670` | type 86, id **211**, pos (192,224) | type 86, id **209**, pos (176,208) |

Runs: `build/runtime-captures/20261002-144541-27b0f3b7` (canonical) and
`build/runtime-captures/20261002-144436-a690d67f` (randomized).

**What this shows, stated exactly.** The enumerator follows `MapEntry+0x14` to each
object-array slot and reads the *record* the engine is pointed at: `+0x08` and
`+0x10` out of the ROM the emulator currently has loaded. So it establishes that the
running image serves the randomized identity and coordinates where retail served the
originals - which is what distinguishes a build that applied the edits from one that
did not.

**What it does NOT show.** It does not read a *constructed actor*, so it does not by
itself demonstrate that a live actor object ends up carrying the randomized identity.
An earlier revision of this document claimed "the engine constructs the randomized
identity" from this run; that is stronger than the measurement, and a reviewer was
right to reject it. For the default `proven-pair` mode the constructed-actor question
is also moot in a second way: as section 5.2 shows, that mode exchanges identity and
position between field-identical records, so the actor set the engine builds is the
same either way.

**Runtime confirmation of retyping is therefore an OPEN ITEM** - and with the
module's effect now understood (§5.2) it is an open item about a capability this
pack does not have, not about instrumenting one it does. It would need an observer
that enumerates live actor objects (by the placement factory's dispatch, as
`tools/runtime/toolkit029_placement_watch.lua` does for a different question) and
reports their resolved identity, paired with a compatibility dimension that made two
identities genuinely interchangeable.

Cold boot also confirmed the game loads and runs: 21 map loads through the same live
pointer, dialogue through the script VM (the liveness channel), correct HUD, player,
collision, scrolling and doors, no crash, and no capture showing corruption.

Full-game beatability is **not** claimed and was not tested; this is a smoke pass.
No enemy encounter is claimed either - the observer had no combat channel, so
"enemies move and can be fought" is unverified.

## 11. Known residual risk, and the recorded waivers

**A boss cannot be identified.** No field, table or label in this project
distinguishes a boss from an ordinary enemy; a search for `boss` or `arena` across
`tools/`, `docs/` and `src/` returns only English prose, and
`docs/research/ENTITY_FORMAT.md` records classification as NOT ESTABLISHED.

Consequence, stated plainly: a boss with no script descriptor, standing in a map
that has at least one other eligible slot, **is indistinguishable from an ordinary
enemy on current evidence and is randomized** - both relocated and, when the stat
module is on, scaled by up to the preset's band. The common shapes are removed
structurally (a script-attached actor is refused; a lone enemy in its own map is
never shuffled), but the general case is not proven.

### Waiver 1 - boss exclusion (owner decision, 2026-10-03)

The rule from `docs/ROM_SAFETY.md` is to refuse an UNKNOWN rather than guess. This
pack cannot satisfy that rule for bosses, because no positive classifier exists to
refuse *with*. The ticket owner's decision, recorded here so it is auditable rather
than implied:

> The absence of a boss classifier is accepted as a known limitation. A boss that
> is neither script-attached nor alone in its map may be randomized. The pack must
> state this limitation in its evidence and in its manifest rather than presenting
> the exclusion as complete.

The manifest carries this: `exclusions.scope_note` names the gap on every run.

**What would close it.** A positive classifier, from any of: a stat-band or
`type_id` rule validated against a known boss encounter; a map/arena table; a
kill-count or event-flag consumer model; or runtime observation pairing a boss
encounter with its placement record. None exists today, and inventing one from
stat magnitude is exactly what the ticket forbids.

### Waiver 2 - Module C not delivered (owner decision, 2026-10-03)

The ticket requires enemy identity to be atomic (section 14) *and* requires an
enemy-type shuffle (section 12). Section 5.2 shows these cannot both hold: on
current evidence the only coherent identity swap is provably a relocation, and a
swap that would really change the enemy produces an unproven behaviour/sprite/stats
mismatch. The owner's decision:

> Ship the provably coherent module and state its true effect. Do not deliver
> Module C, do not claim it, and do not produce the unproven hybrid to manufacture
> the appearance of a type shuffle. Record that Module C is undelivered and what
> would be needed to deliver it.

The manifest carries this on every run as `configuration.delivers_ticket_module_c`
(false) and `configuration.typing_mode_effect`.

### Other bounded unknowns

* Whether anything outside the placement table can spawn an enemy by stat selector.
  `eligible_stat_selectors` rules a record out only when a *placement* shares it with
  a refused actor.
* Whether a placement's position depends on its descriptor or child fields. The
  placement shuffle moves positions without matching them (the type shuffle does
  match them, for the reasons in section 5.1).

## 12. Earlier reviewer findings, and their disposition

Recorded because the review history explains several invariants above.

| Finding | Disposition |
| --- | --- |
| `hp` treated as fixed point | fixed: floor is 1, see section 6 |
| `--spoiler` could overwrite the input ROM | fixed and pinned by `test_the_spoiler_may_not_be_the_input` |
| scripted actors with undecoded roots passed as ordinary | fixed: `script_unresolved`, see section 4 |
| type shuffle broke identity atomicity | fixed: coupled-field grouping, see section 5.1 |
| the fast stat path skipped the profile contract | fixed and pinned by `tests/integration/test_enemy_randomizer_profile_gate_rom.py` |
| write-safety guards untested | fixed: `tests/integration/test_enemy_randomizer_command_rom.py` |
