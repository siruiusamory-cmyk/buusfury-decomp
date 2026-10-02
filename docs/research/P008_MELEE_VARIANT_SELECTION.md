# P-008 normal melee variant selection

How the game chooses among the three observed normal-melee animation clips, and
whether they are mechanically equivalent.

## Objective

Determine **how** the game chooses among the three observed normal-melee
animation clips, and confirm cheaply that they are mechanically equivalent.

Do **not** spend runtime probes proving there is no combo. External research
already settled that; see below.

## External research pass

Required by the External-Research-First rule in the repository rules. Seven angles
opened before authorizing any probe.

**Settled externally, do not re-derive:**

- The IGN control list documents `A` as "Melee attack" with no combo notation.
- `<reference-checkout>\docs\REFERENCE.md:518`, drawn from the retail
  instruction booklet read cover to cover, records that the real behavior is
  "a single repeating attack alternating punch/kick animations, so the plan
  implements one attack, not a combo string". **There is no melee combo.**
- The same reference at line 273 records that a critical hit is **exactly twice**
  normal melee damage, with chance rising with STR.
- Line 494 records that the public record contains **zero** attack, hitstun, or
  knockback frame data for either game, confirmed absent rather than unfound.

**Left open, and therefore the actual record:**

- Which mechanism selects the clip on each attack.
- Whether the three clips differ in any gameplay parameter.

**Useful lead, unverified here:** line 491 records LoG2 RNG seeds at
`0x03003890` and `0x03003894`, 4-byte little-endian, from the TASVideos GBA
resource page. P-007 separately observed leaf node `0x0875028C` referencing
IWRAM `0x03003898`. The adjacency is suggestive and nothing more; it is not
evidence until a runtime read establishes it.

## Canonical Inputs

- Accepted-punch anchor: player object `+0x04C`, the animation-clip pointer.
- Idle clip `0x0851C618`; punch clips `0x0851C680`, `0x0851C6C0`, `0x0851C6A0`.
- Accepted punch is idle to punch clip while A is held.
- Authoritative target HP: `target+0x28C`, signed 32-bit.
- Incoming damage: `record+0x18`. Authoritative writer: `0x0800FA50`.
- Minimum accepted-punch cadence: 20 ticks; median 26.

## Work performed

1. Record a long air-punch sequence and extract the ordered clip series.
2. Test the order against three hypotheses, in this order:
   - **previous-animation avoidance**, meaning no immediate repeat;
   - **fixed cycle**, meaning a repeating period;
   - **random**, meaning repeats occur at the rate chance predicts.
   Report the observed repeat rate against the rate each hypothesis predicts.
3. Only if the series looks random, trace the clip-pointer assignment backward
   to its source and check whether it reads an RNG word.
4. Compare the three clips on accepted-attack duration and, where a hit lands,
   on `record+0x18` and the HP mutation at `0x0800FA50`.

## Scope Boundaries

- Do not attempt to prove a combo system. Reopen that only if runtime sequencing
  directly contradicts the external evidence, and say so explicitly if it does.
- Do not investigate the critical-hit probability curve; the multiplier is
  already documented and the curve is a separate record.
- Do not investigate knockback, world position, death, XP, or rewards.
- Do not broaden into the general RNG subsystem. Read a seed word only if step 3
  is actually reached.

## Result

| # | Question | Answer |
|---|---|---|
| 1 | Clip selection | uniform random among the three |
| 2 | Duration | identical, 16 ticks, zero variance |
| 3 | Damage | indistinguishable across variants |

The three clips are **presentation variants**, not combo steps. They are
contiguous indices 4, 5 and 6 of the character animation table at
`0x0851C898`.

**Selection**, run `20260828-105601-6865162d`, 266 accepted punches, human
input: counts 91 / 91 / 84, chi-square 0.37 on 2 df against a 5% critical value
of 5.99. Avoidance refuted by 94 immediate repeats in 265 transitions; fixed
cycle refuted by 26 to 34% self-match at lags 2 through 6 where a true period
requires 100%.

**Duration**, run `20260828-110417-0e6ef2a1`, 50 punches, scripted input: every
observation exactly 16 ticks across all three variants.

**Damage**, run `20260828-111132-b8551f49`, human combat: 22 unambiguous hits,
per-variant means 51018, 49884 and 50358, with each variant's internal spread of
2000 to 3600 exceeding the between-variant difference of about 1100.

### Mechanism UNKNOWN

Uniform random is a behavioral result. The executable selector was never
located; the only aligned reference to the clip-table base is a data slot in a
per-character table, not an instruction. The published LoG2 RNG seeds at
`0x03003890` and `0x03003894` are **not** this game's RNG, having stayed frozen
across all 532 rows while selection varied 266 times.

### Combo hypothesis RETRACTED

The balanced clip counts first seen in P-006C do not indicate a deterministic
three-step combo. Selection is random, durations are identical, and damage is
indistinguishable.

### Unexplained outliers

Two hits at 1.43 and 1.50 times baseline. Interpretation **UNKNOWN**. A critical
hit is documented as exactly twice normal damage, so these are not criticals and
must not be labelled as such without executable provenance.

### Deferred

Critical-hit mechanism, knockback, ki and special-attack semantics, and death,
XP and rewards.
