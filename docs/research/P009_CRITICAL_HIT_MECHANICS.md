# P-009 critical hit mechanics

Critical hit semantics recovered from two independent directions: the
discriminator, the multiplier and the presentation path, with the producer of the
critical roll left open.

## Result: critical hit semantics confirmed, producer unresolved

P-009 reached its §25-B evidence blocker. The critical discriminator, the
multiplier, and the presentation path are confirmed from two independent
directions. The critical *roll* - its RNG source and STR-dependent probability
- is blocked on a hit-resolution-side search that this record does not open.

## Objective

Recover the minimum executable specification needed to reproduce normal-melee
critical hits: the discriminator, the damage multiplier and where it applies,
the critical roll, the STR provenance, the presentation flag, and whether
criticals select a distinct reaction path.

## External research attestation

P-009 was narrowed by external research before any runtime work. The behavioral
prior taken from documentation was: criticals occur on normal melee, deal
double damage, become more likely with STR, display in yellow rather than red,
and are reported to knock enemies back. RE scope therefore began at *how
exactly*, not *do criticals exist*.

One element of that prior is now **contradicted by the binary** (see below).
Per the External-Research-First rule in the repository rules, the runtime observation
wins, because the binary is ground truth for this project.

## Confirmed results

### HP and damage are fixed-point, scaled by 1024

`target+0x28C` and `record+0x18` are **not** raw HP units. They carry ten
fractional bits. Two independent proofs:

- The number-refresh path at `0x0800AB9A` loads the accumulator at `obj+0x14`,
  adds literal `0x3FF` (pool `0x0800AD84`), executes `asrs r2, r0, #0xA`, and
  passes the result to formatter `0x0803DC96` with the format string at
  `0x0800AD88`, which is `"%d"` in UTF-16LE. The displayed number is therefore
  `(raw + 1023) >> 10`, a ceiling divide.
- The heal counterpart at `0x0800FA80` computes `(record[0] + 0x3FF) >> 10 << 10`,
  adds it to `+0x28C`, and clamps against `maxHP << 10`. The explicit `<< 10`
  on an unscaled max independently fixes the scale.

Against P-006B's captured event: raw HP `141884` displays as **139**, raw damage
`51338` displays as **51**. That is roughly 50 damage against a 139 HP wolf,
about three hits to kill, which matches observed gameplay. The former
"~50,000 damage per punch" figures were raw fixed-point units throughout.

HP is not a multiple of 1024 (`141884 mod 1024 = 572`), so the field carries
genuine fractional residue rather than being a shifted integer.

This is a **different** scale from world position, which is 8.8 (`asrs #8` at
`0x0800FE78` on `+0x1A0`/`+0x1A4`). The two must not be conflated.

**CONFIRMED** (static, two paths; consistent with prior runtime capture).

### The critical discriminator is `record+0x10`

Statically, `0x0800E94E` tests `record+0x10` and branches:

| `record+0x10` | spawner mode | flag | number asset |
|---|---:|---:|---|
| `== 0` | 3 | 0 | `0x0806E050` |
| `!= 0` | 4 | 1 | `0x0806F150` |

The flag rides to number-object `+0x1C`; `0x0800AB6A` tests it and selects
between the two assets from context table `0x08071700`. The heal path
(`0x0800E97E`) uses mode 6, so mode is the number *type* selector.

At runtime, capture `20260828-213108-fab01490` broke at `0x0800FA2A` with
`--dump-register r1` and took 60 stops. Across the 59 usable records,
`record+0x10` was the **sole** field that separated the special hits from the
rest: every other record offset was either constant across all hits or was the
damage magnitude itself. It was nonzero on exactly 2 of 59 hits.

**CONFIRMED** (static branch plus runtime discrimination).

### The critical multiplier is exactly x1.5, not x2

Both flagged hits are exactly three halves of an integer base that lands on the
same 38-raw-unit lattice all damage uses, and both bases fall inside the
observed normal range:

```text
76494 = 1.5 * 50996      (50996 divisible by 38)
75924 = 1.5 * 50616      (50616 divisible by 38)
```

Normal hits: n = 57, range 47804 to 52440 raw (47 to 52 displayed), mean 50250.
All damage values, critical and normal alike, are multiples of 38 raw units.

The documented "critical hits deal double damage" claim is therefore
**contradicted** for this game. It is recorded as EXTERNAL_BEHAVIOR that runtime
evidence overturned, not as a confirmed fact.

**CONFIRMED** (runtime, exact in integer arithmetic, two independent events).

### Presentation

The displayed number is **not** `record+0x18` read directly. `0x0800E8E6` runs
*before* the HP subtraction at `0x0800FA4E`, accumulates `record[0x18]` into a
number object's `+0x14`, and that accumulator is what the ceiling divide above
converts for display. Two distinct assets are selected by the flag, which is the
executable form the red/yellow distinction takes.

**CONFIRMED** for the branch and the assets. The claim that asset `0x0806F150`
renders *yellow* specifically is **not** established here; only that it is the
distinct critical-side asset.

### P-008 anomalies reclassified

P-008 recorded two unexplained events at 1.43x and 1.50x baseline and refused
to call them critical hits, because the documented multiplier was 2x and these
were not. With the multiplier now measured at 1.5x, those events are
**reclassified as genuine critical hits**. They looked anomalous only because
the external prior was wrong.

**RESOLVED.** The P-008 refusal was correct on the evidence available then; the
reclassification rests on new executable and runtime evidence, not on
association with the topic of this record.

## Unknown and deferred

These are **blocked**, not merely unfinished. They require a new
hit-resolution-side search, which P-009 does not open.

- RNG source and range used by the critical roll
- STR-dependent critical probability formula
- the producer that writes `record+0x10` and `record+0x18`
- the exact arithmetic site implementing the x1.5 multiply, and therefore
  whether it applies before or after defense and clamps

Two further limits, stated rather than smoothed over:

- Only two critical events were observed. The 2-of-59 rate is a raw count, not
  a probability estimate, and must not be quoted as one.
- Both observed bases were even multiples of 38, so the x1.5 multiply produced
  an exact integer in both cases. **No fractional case was observed**, and the
  rounding rule for an odd base is therefore UNKNOWN.
- Whether criticals select a distinct reaction or knockback path was not
  reached. Objective 13 is UNKNOWN.

## Producer trace: two routes attempted and failed

Recorded so future work does not repeat them.

### Route 1 - walking up the call stack from the consumer. FAILED.

Capture `20260828-213908-6dd2f261` broke at `0x080187A8` for 60 stops. LR was
`0x0801902A` on **all 60**. That is inside `0x0801900A`, a *generic
behavior-tree child iterator*: it walks `node+0x10[i]`, calls each child through
vtable `+0x04`, ANDs the results, and early-exits on 2. Every frame above it is
also plumbing - `0x08019298` is a thin node-type dispatcher, and the persistent
chain entries `0x08706C94`, `0x086FDBC8` and `0x08706C30` are composite nodes
carrying the documented `{entry, update, exit, count, child[]}` layout.

Decisively, node `0x08706C30` contains `0x0801920F`, the HURT entry established
in P-006B. **This chain is the reaction tree, downstream of damage.** The damage
arithmetic completes before the behavior tree is entered, so no amount of
walking upward from `0x0800FA2A` reaches the producer. This is structural, not a
sampling shortfall.

`0x0800FA2A` also has **zero** direct BL callers; it is reached only through
relative-vtable dispatch, exactly as P-006A found for `0x08039182`.

### Route 2 - a write watchpoint on the damage field. FAILED.

The damage record is **stack scratch**, observed at `0x03007D3C` in both prior
runs, so `record+0x18` is `0x03007D54`. Capture `20260828-214512-d8e5d344` armed
a 4-byte Z2 write watchpoint there for 40 stops and caught only two program
counters in a fixed repeating cycle with no gameplay ticks: `0x08007E4C`
(LR `0x08007E34`) and `0x08029CE2` (LR `0x08029CCC`). Both are unrelated
stack-local sprite and position writes that reuse the same slot.

The address is meaningful only *during* the damage call. A persistent watchpoint
on a stack slot is dominated by unrelated reuse, so this instrument cannot
isolate the producer regardless of tuning.

### What was deliberately not attempted

Four static scans were run and their output **rejected rather than reported**,
because none discriminated and mining them would have manufactured a false
lead of the kind P-008 already produced: a relative-table scan (230 arithmetic
coincidences), stores to `[rN,#0x18]` (584 sites), record-builder shape
matching (50+), and `lsls #10` proximity (40+). No candidate from these is
recorded anywhere, and none should be revived.

## Remake-facing specification

Frozen for the remake, with integer behavior preserved:

```text
on a normal melee hit:
    critical = <UNKNOWN roll>                  # see below
    damage   = base_damage                     # fixed-point, 1024 units = 1 HP
    if critical:
        damage = damage * 3 / 2                # exactly x1.5
        presentation = critical_number_asset   # 0x0806F150
    else:
        presentation = normal_number_asset     # 0x0806E050

    displayed_number = (damage + 1023) >> 10   # ceiling divide
    target_hp -= damage                        # target+0x28C, signed 32-bit
    if target_hp <= 0: target_hp = 0; death
```

**Critical probability: UNKNOWN. A placeholder is required until the producer is
recovered.** Do not derive it from manuals, and do not estimate it from the
2-of-59 observed rate. Both are explicitly out of bounds.

Rounding for an odd base is likewise UNKNOWN and needs a placeholder decision
recorded as such in the remake, not a guess presented as recovered behavior.

## Continuation

Further work is a **new record**, not an extension of this one:

**P-010 candidate - Critical Producer & Hit-Resolution Path.** Approach the
damage record from the attack and hit-resolution side rather than the
damage-application side, since both consumer-side routes are closed.

Authorize P-010 only if exact critical probability becomes important enough to
justify the deeper search.

## Runtime inputs

- Canonical ROM SHA-256:
  `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.
- Private source state: `build/research/p003-exp/wolf-acquire.ss1`
  (SHA-256 `2D5740A8C54180D153024A11B0E4D1143306957AF55A3AD0664C71CF7D9A1AAB`).
- Launcher: `tools/runtime/run_mgba_capture.ps1`; analysis:
  `tools/runtime/p009_crit_report.py`.
- Captures: `20260828-213108-fab01490` (damage records, 60 stops),
  `20260828-213908-6dd2f261` (caller trace, 60 stops),
  `20260828-214512-d8e5d344` (watchpoint, 40 stops, negative).
