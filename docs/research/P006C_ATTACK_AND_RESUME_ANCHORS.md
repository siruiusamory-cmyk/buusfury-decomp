# P-006C - Accepted Attack & AI Resume Anchors

## Status

AUTHORIZED NARROW CONTINUATION

## Objective

Close only the two remaining P-006 timing blockers:

1. exact accepted normal-punch start event and minimum observed cadence;
2. exact wolf normal-AI-resume event after HURT.

Do not begin P-007 or investigate knockback/world position, the complete wolf
AI state machine, death/XP/rewards, ki behavior, or generalized damage.

## Canonical P-006B Evidence

- Current HP: target `+0x28C`, signed 32-bit.
- Incoming damage: record `+0x18`.
- Authoritative writer: `0x0800FA50`.
- Prior controlled run: HURT entry tick 320, damage tick 323, controller exit
  tick 348. Preserve HURT-to-damage `+3` and the 28-tick controller lifetime,
  but revalidate deltas rather than requiring the same absolute ticks.
- Later writer ticks 673, 976, and 992 are observations only; tick 992 was
  terminal. They do not establish normal-punch cadence, re-hit cooldown, or
  immunity.
- Separate invulnerability remains UNKNOWN. Knockback remains DEFERRED.

## Accepted Normal-Punch Anchor

Use the established P-003 chain first:

```text
A press -> attack object creation -> m1 phase machine -> m5 contact -> HURT
```

Find the earliest stable executable event meaning the player's normal punch
actually started. It must execute once per accepted normal punch, not fire for
raw A assertion alone, and be distinguishable from unrelated actions. Prefer
an existing PC/state anchor such as attack-object creation, normal-melee state
entry, phase initialization, or controller/animation entry.

For one controlled punch, use one shared gameplay tick and capture raw A,
`T_ATTACK_ACCEPT`, `T_HURT_ENTER`, `T_DAMAGE`, `T_HURT_EXIT`, and
`T_AI_RESUME`. Report `T_HURT_ENTER - T_ATTACK_ACCEPT`,
`T_DAMAGE - T_ATTACK_ACCEPT`, and whether HURT-to-damage `+3` revalidates.
Raw button-to-hit latency may be separate but cannot substitute for acceptance.

## Minimum Normal-Punch Cadence

After validating `T_ATTACK_ACCEPT`, perform a held/mash-A test and record every
raw A assertion and accepted attack. Report accepted ticks, consecutive
intervals, and the minimum observed interval independently of contact/damage.
Held versus repeated-A behavior is supplemental and cannot block closure.

## Exact Normal-AI Resume

Begin at the confirmed HURT exit path. Trace only the immediate transition:

```text
PRE-HIT NORMAL -> HURT -> POST-HURT NORMAL/RECOVERY
```

Use an executable handler, state function/ID, node pointer, controller slot, or
dispatch index. Define `T_AI_RESUME` as the first gameplay tick after HURT when
the normal wolf AI control path executes again. If RECOVERY intervenes, preserve
it and keep HURT exit distinct from AI resume. Movement alone is corroboration.
Capture the HURT exit condition only if directly visible without broadening
scope; otherwise leave it UNKNOWN.

Report `AI suppression duration = T_AI_RESUME - T_HURT_ENTER`. Only call this
normal-melee hitstun after executable AI resumption is resolved.

## Desired Results

```text
T_ATTACK_ACCEPT: 0
T_HURT_ENTER:    +N
T_DAMAGE:        +N
T_HURT_EXIT:     +N
T_AI_RESUME:     +N
```

Also report accepted attack ticks, consecutive intervals, minimum observed
cadence, raw A cadence, and held-A behavior or UNKNOWN.

P-006 may close when the attack anchor/cadence and post-HURT executable
control/timing are both established. Exact invulnerability, world coordinates,
knockback, complete wolf AI, and death details may remain UNKNOWN/DEFERRED.

## Runtime and Validation

- Reuse `tools/runtime/run_mgba_capture.ps1` and its sole GDB client.
- Use `build/research/p003-exp/single-wolf.ss1` only through the launcher's
  ignored working copy and dynamically rediscover runtime objects each load.
- ROM SHA-256: `940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.
- State SHA-256: `C7C97AA7EB673F6260F08E9A9B315D8561F3EBAB2764266F7AA05B36CB2BD6A2`.
- Baseline commit `0ad7c3d`; dirty user worktree preserved; index empty; no
  commit required.
- Baseline validation: 362 passed with 3 warnings; launcher regression and
  `git diff --check` passed; no proprietary files tracked/staged.

Before closure run full portable tests, launcher regression, `git diff --check`,
ROM/state identity checks, staged/proprietary audit, and independent review.

## Stop

Stop immediately when both accepted normal-punch timing/cadence and exact
normal-AI-resume timing are established. Do not begin P-007.
