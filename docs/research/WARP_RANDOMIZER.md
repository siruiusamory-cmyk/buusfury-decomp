# Seeded warp randomizer

A deterministic, seeded derivative of the canonical Buu's Fury image in which the
safely supported map transitions lead somewhere else, with a manifest that states
every decision, including the records left alone and why, and without the canonical
image being touched.


## What the randomizer does

Produce one deterministic, seeded derivative of the canonical Buu's Fury image in
which the safely supported map transitions lead somewhere else, with a manifest
that states every decision - including the records left alone and why - and
without the canonical image being touched.

## Context

Nothing here is newly reverse engineered. The tool consumes only what is already
recorded:

- the 735-record selector-1 transition family, its 24-byte layout, the two-byte
  destination key and the two ordered intervals (`MAP-WARP-FORMAT-001`,
  `docs/research/LOGX_CONNECTOR_PROVENANCE.md`);
- the arrival point at `+0x14`/`+0x16` and the arrival-facing override in
  `+0x10`'s high nibble, with the low two bits being the door gate and **not** a
  facing (`MAP-WARP-RUNTIME-EDIT-001`, `MAP-WARP-FACING-TRACE-001`);
- the class split: the 566 class hands its stored pair to the warp routine as the
  arrival, the 169 class reads the same pair as a scene-relative delta.
  `set_arrival` refuses the 169 class, which is what makes "randomize the
  destination alone" impossible to do safely there.

The one policy decision this hack adds is the **permutation unit**: a clean mutual
door pair - two records, `f: X -> Y` and `r: Y -> X`, each the other's only door
back, both able to carry an arrival. 248 such pairs exist and cover 496 of the 735
records. The pair is moved as a whole, so the door a player arrives on is always
the door that leads back; the compatibility class is the whole pair set, because
the structure itself is the compatibility. A third rule, the **dead-end guard**,
refuses to link two maps that each hold exactly one door record, since that closes
an isolated 2-cycle with no way on. It is a rule about the door graph's topology,
not progression logic, and it does not guarantee a route.

The two rules after the first one came from runtime, not from review, and the
evidence is kept below: a per-record permutation let an arrival land inside a door
the permutation had pointed elsewhere, and a player who arrives inside a trigger
never crosses its edge; permuting pairs fixed that but closed 2-cycles between
dead-end maps.

## Runtime Inputs

- Canonical image: `roms/Dragon Ball Z - Buu's Fury (U).gba`, SHA-256
  `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, opened
  read-only and re-hashed after every run.
- Generated artefact (ignored tree, never committed):
  `build/warp-randomizer-001/warprand-0ff__white.gba` with its manifest and the
  writer's provenance manifest.

## Scope Boundaries

- No Workbench surface, no capability-count change, no registry change.
- No new reverse engineering: an unresolved field is never guessed, and a record
  that needs one is skipped instead.
- No progression or beatability guarantee. The tool randomizes structure; the
  randomized-warp readiness section of
  [`../research/POST_LOGX_IMPLEMENTATION_ROADMAP.md`](../research/POST_LOGX_IMPLEMENTATION_ROADMAP.md)
  states that solvability is a separate problem, and this hack does not
  contradict it.
- The canonical image is never a write target, and no ROM is committed.

## Runtime Smoke

Human-operated only: the randomizer was launched under the pinned mGBA with a
read-only map-arrival observer (`tools/runtime/warprand001_map_watch.lua`, injected
through the tracked `inject_mgba_lua.ps1`), so the map identities come out of the
live engine rather than out of a map-name guess. No map was required, no route was
scripted and no input was automated.

**Result: ISSUE - the run softlocked.** The engine does consume a randomized
destination (the operator walked out of map 37 into map 34, where retail's record
for that door sends the player to map 35), the randomised ROM boots and plays, but
the operator was trapped in a 34 <-> 37 loop.

The mechanism is a property of the **arrival rule**, and it is measurable without
the operator: the arrival is derived from the destination's *canonical* door back
to the source map, and the permutation may have pointed that same door somewhere
else. Arriving inside a trigger rectangle never crosses its edge, so the door does
not fire; walking on takes the player through the map's other door and back.

For the observed loop: `map:0034/transition:0000` now leads to map 37 with arrival
`(344, 308)`, which lies inside `map:0037/transition:0001`'s region
`(328, 361)/(304, 313)` - the record the permutation retargeted from map 34 to map
35, i.e. the way onward - while `map:0037/transition:0000` sends the player back to
`(344, 20)` in map 34, three pixels south of map 34's own north door. North, loop,
north, loop.

A census over the delivered image finds **168 of 559** randomized arrivals landing
inside a door of the destination that now leads somewhere other than the source
map. That is a policy-level finding, not a structural one: every one of those
arrivals is in bounds, at a door, and internally consistent, which is exactly why
the SDK's own checks pass them.

A stricter arrival rule ("never land inside a foreign live door") was prototyped
and **rejected as too blunt**: it would leave 167 of 559 records unrandomizable and
repair only one. A second shape - nudge the fallback arrival just outside the door
rectangle, which is the offset convention the canonical corpus itself shows - was
drafted and then **withdrawn** in favour of the rule below, because the external
pass showed the industry fixes this earlier in the pipeline.

The observer's player-slot read did not resolve in this session (`0x03001C34` read
0 throughout), so its facing channel is silent and the arrival/facing judgements
are the operator's, as this record intends.

### The `/3` re-run: PASS, as played

The operator re-ran the delivered `/3` image and reported that it worked. The
read-only observer recorded the route from the engine, and every door that moved
came out of a randomized record:

| frame | from → to | record | retail | pair |
| --- | --- | --- | --- | --- |
| 13659 | 33 → 287 | `map:0033/transition:0000` | 34 | `pair:0001` |
| 13752 | 287 → 33 | `map:0287/transition:0001` | 286 | `pair:0001` |
| 14618 | 287 → 283 | `map:0287/transition:0000` | 288 | `pair:0111` |
| 15289 | 283 → 77 | `map:0283/transition:0001` | 284 | `pair:0108` |
| 15543 | 77 → 417 | `map:0077/transition:0000` | 78 | `pair:0042` |

The route that used to end at Broly now runs 33 → 287 → 283 → 77 → 417, with a
deliberate back-and-forth through `pair:0001` (33 ⇄ 287) that exercises the return
door three times. No arrival was unusable, nothing trapped the player, and the
1 → 3 → 4 → 5 → 6 → 0 → 31 → 29 → 1 → 33 opening (scripted moves, no door record)
is unchanged, as expected.

Stated with its limits, because the record asks for a playable ROM and not a
certificate: this is **five randomized links out of 496**, it is the operator's
report ("from what I played") rather than an exhaustive traversal, and progression
is still not guaranteed - `/3` removes the degenerate dead-end shape, not every
pocket a hub can lead into.

### The external practice, and the policy it produced

An external pass was run for this (the record's External-Research-First rule). The
[OoT Entrance Randomizer
wiki](https://wiki.ootrandomizer.com/index.php?title=Entrance_Randomizer) states
the governing rule outright: **"all entrances are kept bidirectional, which means
going through a loading zone from one side, then going back through the same
loading zone will lead back to the original location"**, and entrances are only
ever shuffled "with other entrances of the same type". The
[ALttP Dungeon Randomizer](https://aerinon.github.io/ALttPDoorRandomizer/) is the
2D top-down analogue - it shuffles room-to-room doors in the same kind of engine
this game uses - and ships that discipline plus an explicit one-way exclusion list.

That rule is what policy `/1` was missing, and it is measurable here: the
canonical corpus is built from **248 clean mutual door pairs** (400 exist; 248
have both halves arrival-authorable), covering **496** of the 566 eligible
records.

**Policy `/2` - `reciprocal-door-pairs/2` - implements it.** The permutation unit
is the pair, not the record: a pair's two halves always move together, each
arriving on the other's door, so the door a player arrives on is always the door
that leads back. The compatibility class is the whole pair set, and that is
measured rather than assumed: grouping pairs by the forward record's source map
leaves 175 of 207 groups holding a single pair, so the permutation can only be the
identity and just 46 of 496 destinations move. With the whole set as one class,
492 of 496 move.

Proved on the delivered image, in
`tests/integration/test_warp_randomizer_rom.py`:

- for every randomized record the destination holds a record leading back to its
  source map, and the arrival sits inside **that** record's trigger rectangle
  (named by `counterpart` in the manifest, so the claim is checkable per row);
- **no** randomized arrival lands inside a door that leads elsewhere - the exact
  defect that trapped the first playthrough, where 168 of 559 arrivals did.

Counts move from 559 randomized / 176 skipped to **496 randomized / 239 skipped**
(169 class B + 70 records with no clean mutual pair, each reported with its own
reason). The softlock described above is the `/1` result and is kept as the
evidence for why the policy changed.

### Policy `/3` - the dead-end link guard

The first `/2` playthrough found the next failure mode within minutes, and it is
the one reciprocity cannot fix. 86 maps hold exactly one door record; such a map is
a dead end on its own. `/2` closed a 2-cycle between two of them: its matching sent
the door out of map 33 to map 390 and map 390's record to map 33, so map 33 - which
the operator reaches from Snakeway's scripted transition and which holds exactly
one door - had a single way on, and it was Broly. **12 such links (6 closed
2-cycles)** existed in the `/2` mapping: `33<->390`, `144<->289`, `154<->334`,
`227<->299`, `47<->402`, `115<->422`. Retail never produces that shape: of its
canonical single-door pairs, 67 lead to a hub and only 2 are dead-end-to-dead-end.

Stated precisely, because the retained log is thinner than the policy claim: the
`/2` run shows `33 -> 390` and then a scripted move of `390 -> 1`, not a door back
to 33 (map 1 holds no transition record at all). So what the operator experienced
was a pocket whose only progression was the Broly fight and, on losing it, the
return to Snakeway that leads back to 33 - a loop through a boss, which is why the
report came back as "the only direction to go leads to Broly". The policy fact
that produced it - the `/2` matching pairs 33 with 390 - was reproduced from the
code itself, and the guard is what removes it.

`/3` refuses to link two single-door maps when building the matching. It is a rule
about the door graph's **topology**, not progression logic: it knows nothing about
items, flags or story order. Under `/3` the bad links are **0**, the manifest's forced-link count is **0** (the
guard was satisfiable, and the count is reported so a relaxed rule could never pass
as a satisfied one), and 492 of 496 destinations still move. Map 33 now leads to
the hub at map 287, arriving on its return door.

The limit is stated rather than implied: **this does not guarantee a route.** A hub
can still lead into a pocket, and only reachability logic over the whole graph
would rule that out - which this record puts out of scope. What `/3` removes is the
degenerate shape that made the failure immediate and unavoidable.

Cited as sources, not paraphrased: OoT's own `EntranceShuffle.py` was not read for
this pass, and no claim is made about either project's implementation beyond the
wiki text quoted above.
