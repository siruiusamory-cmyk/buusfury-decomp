# P-007 - Wolf AI & Attack Behavior

## Status

CLOSED. All eight closure criteria met.

## Objective

Recover an implementation-useful specification for the wolf's ordinary combat
behavior: idle, player acquisition, approach, attack decision, attack start,
attack execution, attack recovery, and re-engage or disengage.

## Result

The actor system is a behavior tree whose nodes are
`{entry, update, exit, count, child[count]}`. One reusable distance primitive,
`0x08029BE0` and its instruction-for-instruction twin `0x08029C90`, compares
`dx*dx + dy*dy` between body-rectangle centers against a threshold copied from
the owning node, using a signed `bgt` so the test is inclusive.

```text
IDLE 434
  - dist_sq <= 10000           -> HUB 435

HUB 435
  - dist_sq <= 524             -> ATTACK 437
  - otherwise                  -> PURSUIT 438 / 439

ATTACK 437
  - after 35 ticks             -> HUB 435

DISENGAGE: NONE
```

| Criterion | Status |
|---|---|
| 1. Player acquisition condition | MET, `dist_sq <= 10000`, r 100 |
| 2. Pursuit / approach behavior | MET, selectors 438 near and 439 far |
| 3. Attack-range decision | MET, `dist_sq <= 524`, r ~22.9 |
| 4. Attack-start anchor | MET, entry to selector 437 |
| 5. Attack recovery / next state | MET, 437 to 435 after 35 ticks |
| 6. Minimum attack cadence | MET, 36 ticks |
| 7. Disengagement behavior | MET, none |
| 8. Minimal transition graph | MET |

Attack duration was exactly 35 ticks in 52 of 52 episodes, all returning to the
hub. The 36-tick cadence is the minimum observed spacing, not a proven timer;
the counter at `+0x12` was tested and refuted as its driver.

## Evidence

Captures, all Lua-only with zero executable breakpoints on mGBA 0.10.5:

| Run | Purpose |
|---|---|
| `20260828-011749-80c914d1` | passive baseline, attack state identified |
| `20260828-012216-462a65e4` | controlled cadence, player parked in range |
| `20260828-012734-586c44d8` | timer hypothesis refuted |
| `20260828-100719-3a8e0ca3` | retreat to radius 157, no disengagement |
| `20260828-101954-32dfd87b` | acquisition, two wolves leaving idle |

States: `single-wolf.ss1` SHA-256 `c7c97aa7...`, and `wolf-acquire.ss1`
SHA-256 `2d5740a8...` for the acquisition runs.

## Corrections

The reading of hub constant 8100 (r 90) as the acquisition radius is
**SUPERSEDED**; acquisition belongs to idle node `0x08706A38` at 10000. Absolute
EWRAM addresses are not permanent actor identity: `0x0203DBB0` behaves as a wolf
here despite older notes associating it with player context.

## Deferred

The player three-clip pattern remains **UNKNOWN** and must not be promoted to
combo semantics. Knockback and world position remain **DEFERRED**. Separate
invulnerability remains **UNKNOWN**. Death, XP, and rewards are out of scope.
The complete wolf state machine was not required.

## Stop

Stopped on closure. P-008 not started.
