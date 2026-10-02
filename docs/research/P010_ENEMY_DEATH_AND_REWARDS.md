# P-010 enemy death, EXP and drop pipeline

The enemy death and progression pipeline: death-to-EXP timing, recipient
resolution, wolf base EXP, the equipment bonus, the drop structure and actor
lifecycle.

## Result

The enemy death and progression pipeline is implementation-ready:

```text
LETHAL DAMAGE -> DEATH -> EXP AWARD -> OPTIONAL REWARD/DROP -> ACTOR LIFECYCLE
```

Two research debts remain, both narrowed to a named next anchor. Neither
blocks closure.

## External research attestation

External sources established **player-visible behavior only** and were used to
narrow the record before any probe. RE established the entire precision layer.

The decisive external artifact was the Data Crystal RAM map for this game. It
is fetch-blocked by a human-verification interstitial on both `curl` and
WebFetch; the working route is the Wayback mirror:

```text
curl -sL "https://web.archive.org/web/2024/https://datacrystal.tcrf.net/wiki/Dragon_Ball_Z:_Buu%27s_Fury/RAM_map"
```

It supplied `0x03001068` current-character index, `0x0300155C` Zeni,
`0x03001584` Goku XP, `0x0300114C` item count, and per-character stat blocks.
GameFAQs supplied the character-switch glitch, including the detail that the
enemy must be lured onto a **save point** so the switch menu opens before
payout.

**Every one of those addresses was then verified against our own ROM**, because
P-008 refuted a published address set (the LoG2 RNG seeds). The save-block base
was confirmed independently from ROM pool `0x086B7080`, which holds
`0x03001068`. External evidence narrowed the search; it was never accepted as
proof.

This record is the clearest example so far of the standing method: **research
first, reverse engineer only the unresolved precision.**

## Death to EXP timing

**`T_EXP - T_LETHAL` = exactly 1 gameplay tick.** Do not round this to
"immediate"; the delay is real and load-bearing.

Run `20260828-234311-1426d3c4`, breakpoints `0x0800FA50` (HP writer) and
`0x080139F8` (EXP writer), with `p010_death_timeline.lua` supplying the shared
tick:

| Wolf | T_LETHAL | T_EXP | delay |
|---|---:|---:|---:|
| `0x0203DBB0` | 9630 | 9631 | 1 |
| `0x0203D504` | 9744 | 9745 | 1 |

HP goes **negative** at the lethal write (`-22390`, `-24252`) before the branch
at `0x0800FA56` zeroes it, so `HP <= 0` is a genuine signed test on a value that
transiently holds the overkill amount.

## EXP recipient resolution

**The amount is fixed at kill time; the recipient is resolved at payout.** That
asymmetry is the mechanism, not an anecdote.

```text
enemy dies
  -> reward object created, EXP at +0x08 ALREADY includes the equipment bonus
  -> refcount reaches zero -> destructor loop 0x08011A1E
  -> 0x0804F82C reads +0x08 and the live character index
  -> 0x080043D8: block = base + index*0x68 + 0x4F8
  -> 0x08013914 adds it to charblock+0x24
```

Recipient source: `0x080043DA` reads the index with `ldrb r2,[r0]` and
immediately multiplies by the `0x68` stride at `0x080043DC-0x080043DE`. The
index is read **when EXP is paid**, one tick after death.

Writer, at `0x080139F4-0x080139FA`:

```text
ldr  r0,[r4,#0x24]     ; old XP
adds r0,r0,r5          ; r5 = award amount
str  r0,[r4,#0x24]     ; XP += award
ldr  r1,[r4,#0x24]     ; readback, retries on mismatch
```

`r4 = 0x03001560` for Goku, and `0x03001560 + 0x24 = 0x03001584`, matching the
RAM map exactly. Runtime confirmation: LR was `0x08011A5E` on every stop of run
`20260829-000534-be15deff`, proving award-on-destroy at runtime rather than
only statically.

**This explains the documented character-switch glitch exactly.** Killing an
enemy on a save point opens the switch menu inside the one-tick window; the
amount was already fixed, but the recipient index is read afterwards, so the
newly selected character receives the EXP.

## Wolf base EXP

**225**, u32, read from reward object `+0x08` by `0x0804F82E`
(`ldr r1,[r0,#8]`).

Runtime: XP `3700 -> 4000 -> 4225 -> 4450 -> 4675`, four consecutive awards of
225 each, run `20260828-232716-a7e7cd75`.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the 300 award

**OLD CLAIM.** An early capture showed awards of 300 and then 225, suggesting
the per-wolf award was not constant.

**NEW EVIDENCE.** A clean run produced four consecutive 225 awards. The 300
appeared only on the very first stop of the earlier run.

**RESOLUTION.** The 300 was the tail of an award already in progress when the
breakpoint armed. Base wolf EXP is a constant **225**. Do not record 300 as a
second enemy value.

## EXP equipment bonus

**+23 EXP per qualifying equipped item, additive.** CONFIRMED for the tested
configuration.

Run `20260829-000057-5b79657e`, breakpoint `0x08013914` (award-function entry,
`r1` = incoming amount), four controlled phases:

| Equipped | award | delta |
|---|---:|---:|
| nothing | 225 | - |
| 1 Ton Armbands only | 248 | +23 |
| 1 Ton Boots only | 248 | +23 |
| both | **271** | +46 |

`225 + 23 + 23 = 271` matches exactly. **Multiplicative is refuted**: the
per-item ratio `248/225 = 1.102222` compounds to `225 * 1.102222^2 = 273.35`,
i.e. 273, but 271 was observed. Off by 2, so bonuses do not compound.

`23/225 = 10.2222%`, not a round percentage, which is further evidence the
stored bonus is a flat integer rather than a rate.

**Bounded limit:** every observation used base 225, so a flat `+23` cannot be
distinguished from a bonus proportional to base. Separating them needs an enemy
with a different base EXP.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the +46 bonus

**OLD CLAIM.** An earlier run measured a single unexplained `+46` and I noted
that `46/225 = 20.44%` was not a round percentage, so additive was "more
plausible than a multiplier" - explicitly unproven.

**NEW EVIDENCE.** the maintainer isolated the two items. Each contributes exactly +23.

**RESOLUTION.** The +46 was two items at +23 each. Additive composition is now
CONFIRMED and multiplicative is REFUTED by an exact integer.

## Bonus arithmetic site - NARROWED UNKNOWN

**UNKNOWN / DEFERRED.**

Known: the +23-per-item effect is confirmed at the observable reward level, and
the bonus is **already baked into the reward object at creation**.

| run | equipment | reward object `+0x08` |
|---|---|---:|
| `20260829-000534-be15deff` | none | 225 |
| `20260829-000912-69c3fb0e` | both items | **271** |

Not known: the executable arithmetic site that constructs the modified amount.
It is upstream of reward-object creation. `r1` provably passes through
`0x0804F82C` -> `0x080043D8` -> `0x08013914` untouched: `0x0804F82E` loads it
and neither function writes it.

**Next anchor if revisited:** break on the reward-object constructor, identified
by vtable `0x0804A820` at object `+0x00`, and trace its inputs.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: the award queue

**OLD CLAIM.** `0x080033D2` was read as popping a queued EXP award, making it a
candidate bonus site.

**NEW EVIDENCE.** The push side at `0x080033EA` stores `charblock+0x24`, the
character's *current* XP, on the same `0x68` stride.

**RESOLUTION.** The pair is an XP **save/restore**, not an award queue, and not
the bonus arithmetic. The original reading was wrong.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION: an apparent contradiction

**OLD CLAIM.** Reward objects carried an unmodified 225 while the awarder
received 271, which appeared to contradict the finding that `r1` is unmodified
along the award path.

**NEW EVIDENCE.** The equipped re-run showed reward objects carrying 271.

**RESOLUTION.** The two earlier kills were simply **unequipped**; the capture
had not recorded equipment state. The static path reading was correct. This was
a gap in experiment design, not in the analysis.

## Drop structure

Two **independent** four-entry tables. Reward value and presentation are
separate concerns and must not be merged.

### Zeni denomination table

Pointer table at `0x086FC250`; each entry points to a record whose amount is a
**plain integer** at `+0x0C` - no packing, no encoding.

| entry | record | amount |
|---:|---|---:|
| 0 | `0x086FC260` | 5 |
| 1 | `0x086FC378` | 25 |
| 2 | `0x086FC790` | 50 |
| 3 | `0x086FC8A8` | 100 |

Runtime: Zeni `165 -> 325` across 13 pickups, deltas **only {5, 100}** (twelve
+5, one +100). Both amounts matched `[ptr+0x0C]` exactly.

The live pickup object reaches its record through `+0x60`.

### Visual-tier table

A separate 16-byte-record table at `0x086B759C`, reached from pickup object
`+0x10`, resolved by a two-key lookup fully decoded at `0x08013E38`:

```text
find_pickup_type(a, b):
    for i in 0..3:
        rec = 0x086B759C + i*0x10
        if rec[0] == a and rec[1] == b: return rec
    return 0
```

| record | key | payload ptr | IWRAM | flags |
|---|---|---|---|---|
| `0x086B759C` | (4, 2) | `0x086B75DC` | `0x03002B88` | `0x2000` |
| `0x086B75AC` | (10, 4) | `0x086B761C` | `0x03002B8C` | `0x4000` |
| `0x086B75BC` | (16, 6) | `0x086B765C` | `0x03002B90` | `0x4000` |
| `0x086B75CC` | (24, 10) | `0x086B769C` | `0x03002B94` | `0x80004000` |

Every +5 pickup used record 0; the +100 pickup used record 1. The two differ
**only** by this descriptor, so reward-type identity lives at object `+0x10`.

This is the drop **structure**, not a complete loot database. Only the zeni
denominations and these four tiers are decoded.

### Zeni writer

`0x08017EC2`; the add is at `0x08017ED6`:

```text
ldr  r1,[r4,#0x60]     ; pickup -> amount record
ldr  r1,[r1,#0x0C]     ; amount
ldr  r2,[r0]           ; old zeni, r0 = 0x0300155C
adds r1,r2,r1
str  r1,[r0]           ; zeni += amount
ldr/cmp/bne            ; readback-verify retry
```

## Item add function

`0x08004448`:

```text
r0 = inventory + 0xE4              ; count slot, = 0x0300114C
if count == 0xFA: return           ; hard cap 250, silent no-op
count += 1
slot  = old_count * 4
entry = item_id & 0x0FFFFFFF       ; lsls #4 / lsrs #4 clears the top nibble
u32[inventory + 0xE4 + 4 + slot] = entry
```

Inventory is a count followed by a u32 entry array. The top 4 bits of each
entry are a flag field, read back at `0x08004406-0x08004410` with
`lsrs r3,#0x1c` and tested nonzero.

Runtime: item id `0x74` (116), count `0 -> 1`, LR `0x0800D75C`, run
`20260828-233451-af949591`. Quantity behavior beyond the increment was not
established. Not expanded into the inventory subsystem.

A real asymmetry worth preserving: the XP writer (`0x080139F4`) and Zeni writer
(`0x08017ED6`) both use a readback-verify retry loop; the item writer at
`0x08004464` does **not**. Single `str`, no verify.

## Drop roll - NARROWED UNKNOWN

**UNKNOWN / DEFERRED.** Same producer-tracing class as the P-009
critical-producer blocker.

Dataflow stops precisely here: the tables above are decoded and the pickup
object's link to them is confirmed (`+0x10` type, `+0x60` amount), but **the
code that selects which index to spawn was not located**.

Routes attempted and rejected during this record, so they are not retried:

- Literal scans for the descriptor and denomination tables found only the pool
  slot `0x08013E60` and the intra-table pointers; no selector site.
- `0x08013E38` was followed to completion and is a **type resolver**, a
  two-key lookup, not a roll.

Probability was **not** estimated statistically, per the record. The observed
25:1 split of +5 to +100 is a raw count, not a rate, and must not be quoted as
one.

**Next sensible attack point if revisited:** break on the pickup-object
constructor from the death path and capture what selects the index, the same
technique that resolved the EXP caller.

## Actor lifecycle

Confirmed from run `20260828-234311-1426d3c4`:

| stage | evidence |
|---|---|
| lethal HP state | HP crosses to negative at `0x0800FA50`; `0x0800FA56` zeroes it |
| logical death | the `HP <= 0` branch broadcasts event `0x11` via `0x08011C0C` and invokes the vtable death callback at `0x0800FA74` |
| EXP emission | 1 tick after lethal damage, from destructor loop `0x08011A1E` |
| actor removal | reward object refcount reaching zero drives the destructor path |

Respawn was **not** investigated, per scope.

**Death-state duration was not measured.** The observer's own lifecycle rows
were unusable (see below), and the breakpoints cannot see clip transitions, so
the death animation length remains UNKNOWN.

### Tooling defect, recorded rather than hidden

`tools/runtime/p010_death_timeline.lua`'s `looks_like_actor()` heuristic is too
loose: it accepts any EWRAM word whose `+0x238` and `+0x28C` happen to read
plausibly. It produced **73 bogus LETHAL rows for 2 real kills** across 13,513
CSV rows.

**The defect did not reach any result.** Every value in this record comes from
the breakpoint capture, which is independent of the observer's own rows; the
observer's contribution was the shared tick counter, which was correct. Before
that observer's SCAN/LETHAL rows are trusted, discovery must be tightened -
require the controller pointer to resolve into the known behavior-tree table
range, and require HP to match a known enemy maximum.

## Complete wolf fixture

Canonical regression fixture. Both wolves in the run were identical.

```text
WOLF
  initial HP            179200 raw = 175 displayed   (1024 raw units = 1 HP)
  hits to kill          4
  damage per hit        47956 - 52250 raw (47 - 52 displayed)
  lethal damage event   HP crosses to negative, then zeroed
  T_LETHAL              9630 (wolf A) / 9744 (wolf B)
  T_EXP                 9631 (wolf A) / 9745 (wolf B)
  EXP delay             1 gameplay tick
  base EXP              225
  equipped bonus        +23 per qualifying item, additive
  final EXP award       225 unequipped / 248 one item / 271 both items
  recipient             active character index, read AT PAYOUT
  drop result           zeni observed; +5 (x25) and +100 (x1) across 13 pickups
  reward identity       denomination record 0x086FC260 (5) / 0x086FC8A8 (100)
  item drop             id 0x74 (116), inventory count 0 -> 1
  actor removal         driven by reward-object refcount reaching zero
```

## Level threshold table - extra result

Not required by the record; recovered while tracing the award path.

The pool literal `0x086B7080` holds the **save-block pointer** `0x03001068`,
which independently confirms the RAM map base. The XP threshold table begins
immediately after, at `0x086B7084`:

```text
0, 10, 40, 100, 200, 350, 560, 840, 1200, 1650, 2200, 2875, 3700, 4700, 5900,
7325, 9000, 10950, 13200, 15775, 18700, 22025, 25800, 30075, 34900, 40325,
46400, 53175, 60700, 69025, ...
```

Strictly increasing over at least the first 150 entries. Entry `i` is the XP
required for level `i+1`.

Lookup at `0x08013A08-0x08013A1A`: load new XP, index by `level*4`, and continue
only if `XP >= threshold`, then call `0x080135D2` and `0x08013678`.

**Runtime cross-check:** captured XP began at exactly **3700**, which is
threshold entry 12 - the player had just reached level 13. The table lands on
the observed value rather than merely near it.

Not expanded into stat growth or allocation.

## Level cap - extra result

**200**, from `0x08013A00`: `cmp r6, #0xc8`, checked before the threshold
lookup. Matches the level cap documented for LoG2 in the sibling reference.

## Remake-facing specification

```text
on_enemy_lethal_damage(enemy):
    # HP is fixed point: 1024 raw units = 1 displayed HP
    enemy.hp -= damage                  # may go negative; overkill is discarded
    if enemy.hp <= 0:
        enemy.hp = 0
        broadcast(EVENT_DEATH)          # event 0x11
        enter_death_lifecycle(enemy)

        # the reward amount is fixed HERE, with the bonus already applied
        reward.exp = enemy.base_exp + 23 * qualifying_exp_bonus_items
        # wolf base_exp = 225; exact original arithmetic site UNKNOWN

    one_tick_later:                      # T_EXP - T_LETHAL = 1, confirmed
        recipient = active_character      # index read AT PAYOUT, not at kill
        recipient.xp += reward.exp
        if recipient.xp >= threshold[recipient.level]:
            level_up(recipient)           # cap 200

        reward = resolve_enemy_drop(enemy)
        # which index is selected: producer UNKNOWN
        if reward is zeni:
            amount = denomination[i]      # {5, 25, 50, 100} at 0x086FC250
            tier   = visual_tier[j]       # 0x086B759C, presentation only
        if reward is item:
            if item_count < 250:
                inventory[item_count] = item_id & 0x0FFFFFFF
                item_count += 1

    complete_death_lifecycle_and_remove(enemy)
```

## Remaining unknowns

**P-010 - RESOLVED**, with two bounded unknowns recorded as research debts:

1. **EXP bonus arithmetic producer** - UNKNOWN. Next anchor: reward-object
   constructor, vtable `0x0804A820` at object `+0x00`.
2. **Drop probability producer / roll** - UNKNOWN. Producer-side search
   deferred; next anchor is the pickup-object constructor on the death path.

Also unmeasured: death-animation duration, and whether the +23 is flat or
proportional to base EXP.

## Runtime inputs

- Canonical ROM SHA-256:
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.
- Private source state: `build/research/p003-exp/wolf-acquire.ss1`
  (SHA-256 `2D5740A8C54180D153024A11B0E4D1143306957AF55A3AD0664C71CF7D9A1AAB`).
- Launcher: `tools/runtime/run_mgba_capture.ps1`; observer:
  `tools/runtime/p010_death_timeline.lua`.
- Captures: `20260828-231949-e5ac8aa2` (XP watchpoint),
  `20260828-232716-a7e7cd75` (EXP + Zeni), `20260828-233451-af949591`
  (item + wide dump), `20260828-234311-1426d3c4` (death timeline),
  `20260828-235533-20968114` and `20260829-000057-5b79657e` (equipment A/B),
  `20260829-000534-be15deff` and `20260829-000912-69c3fb0e` (reward object).
