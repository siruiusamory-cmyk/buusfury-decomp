# TOOLKIT-031 - Runtime-Prove Attached Behavior Execution

Status: **COMPLETE - Outcome A.** Baseline `86eb9dc`.
Previous closure: [TOOLKIT-030](archive/TOOLKIT-030-COMPLETE.md).

## Result

> **RUNTIME-PROVEN AUTHORED BEHAVIOR: YES**
>
> **NEXT BLOCKER: author NEW behavior content, rather than attaching behavior
> the game already contains**

The original engine executes the behavior the SDK attached to a newly authored
entity. The program counter reached the script trampoline five times in one
session, each time carrying the authored descriptor and its script root, with
the interpreter entered on the same frame. A control build differing in exactly
one word - with the same entity type - reached it zero times while the same
instrument recorded other scripts running throughout.

```text
SDK-authored placement    map:0040/authored:tk030 (clone of map:0040/placement:0001)
-> authored attachment    +0x14 = 0x0808D788, written from project state
-> engine instantiates    live slot carries 0x0808D788      (TOOLKIT-030, 67 samples)
-> handler reached        PC 0x08004220, r0 = 0x0808D788    <- NEW
-> script root consumed   [r0+4] = 0x0808D77C               <- NEW
-> interpreter executes   0x08004038 entered, same frame    <- NEW
-> STOP
```

Full evidence: [AUTHORED_BEHAVIOR_EXECUTION.md](../research/AUTHORED_BEHAVIOR_EXECUTION.md).

## Closure answers

| Item | Value |
|---|---|
| Outcome | **A** |
| Commit hash | (recorded at commit) |
| Static call-site census | handler `0x0800421E` has **zero** direct callers; reached only through a descriptor's `+0x00`. Constructor `0x0800F68C` **stores** the placement's `+0x14` at `actor+0x228` (`0x0800F6F0`/`0x0800F6F4`) and returns. That slot has one writer and four readers; the getter `0x0804F860` is actor-vtable slot `+0x78`, dispatched from `0x08032CE4` inside `0x08032B98`, itself virtual. |
| Invocation / trigger | **Not map construction** - refuted statically and by runtime. Gameplay-driven and intermittent: hits at 43.0 s, 92.5 s, 109.0 s, 161.7 s, 198.6 s, gaps 49.6 / 16.5 / 52.6 / 37.0 s, so not periodic either. The exact player action is **not claimed** on five samples with no per-hit input record. |
| Positive-control result | **PASS as a liveness control.** The canonical owner of this descriptor is map 428, unreachable from the map-40 savestate (zone 1 vs zone 21; no zone-1 map has a script placement). A canonical script-bearing record was therefore cloned into map 40. The instrument recorded **20 interpreter entries** in every run, so no run is blind. |
| Authored runtime result | **5 trampoline hits**, 13,680 frames |
| Descriptor observed | `0x0808D788` at every hit |
| Payload / root observed | `0x0808D77C` at every hit |
| Owner attribution | live placement slot read `+0x14 = 0x0808D788` within a second either side of all five hits |
| Independence control | TOOLKIT-029 ROM `a425ae73...`: same type `0x56`, same id `0xD3`, descriptor `0x080555A0` - **0 hits** in 7,380 frames, liveness 20 |
| Harness changes | `run_mgba_capture.ps1` gained `-GeneratedRomSha256 <exact digest>`; canonical guard unchanged and still the default. New `start_toolkit031_session.ps1` / `finish_toolkit031_session.ps1` for free-running Lua sessions. |
| `RUNTIME-PROVEN AUTHORED BEHAVIOR` | **YES** |
| `public progress impact` | **UPDATED** |
| Live-site status | milestone split into COMPLETE "Attach and execute behavior" + CURRENT "Author new behavior"; progress held at 80% |
| Canonical ROM SHA-256 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, unchanged |
| Canonical savestate SHA-256 | `2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab`, unchanged |

## OBSERVED

| | authored | inheritance control | type control |
|---|---|---|---|
| ROM SHA-256 | `f6595c4e` | `a425ae73` | `59f28fea` |
| body type / id | `0x56` / `0xD3` | **`0x56` / `0xD3`** | `0x06` / `0x20` |
| body `+0x14` | **`0x0808D788`** | `0x080555A0` | `0x0808D788` |
| **trampoline hits** | **5** | **0** | **0** |
| interpreter (liveness) | 20 | 20 | 20 |
| frames | 13,680 | 7,380 | 8,460 |

The authored/inheritance pair differs in **one word**. Entity type is held
constant across it, so the operator's type observation is controlled for.

## What is NOT claimed

**No visible gameplay consequence.** The attached script sets a collision
rectangle at tiles (6,24)..(10,25) from literal operands, nowhere near the
authored entity at (22,22), and TOOLKIT-030 showed that region reads saturated.
The ticket permits this: a visible consequence is desirable but not mandatory
when execution attribution is exact, and here it is exact.

**The type control's movement is not script-driven.** That entity moves because
of its own type; its trampoline count was zero.

**The exact trigger action is not identified**, only its shape: gameplay-driven,
intermittent, neither construction-time nor periodic.

## Corrections made during the ticket

**The first "positive control" was not one.** Cloning map 40's own slot and
overriding its descriptor reproduced TOOLKIT-030's authored ROM **byte for
byte**, so it would have confirmed whatever the authored build did. Replaced by
cloning the canonical record itself.

**Map construction was refuted as the trigger** before any runtime work, by the
static census. TOOLKIT-030's next-blocker note had left it open.

**Two harness bugs killed live play sessions** - a deadline that counted setup,
and a `finally` block firing when the hosting `Start-Job` was torn down. Both
fixed; the rule is now recorded in `docs/DEVELOPMENT.md` and the `mgba-runtime` skill.

## Validation

| Suite | Result |
|---|---|
| `tests/unit` (full) | **971 passed** |
| `tests/integration/test_authored_behavior_execution_rom.py` | 6 passed (new) |
| `npm run check` | 0 errors, 0 warnings, 0 hints |
| `npm run build` | 1 page built |

Canonical ROM and savestate hashes verified unchanged before and after every
run. Generated ROMs remain under the ignored `build/` tree. Unrelated worktree
changes preserved.

## Durable capture

The runtime tooling rules this ticket learned the hard way are now permanent in
[`docs/DEVELOPMENT.md`](../../docs/DEVELOPMENT.md) "Runtime tooling rules", pointed to from
`docs/DEVELOPMENT.md`: reuse the tracked launcher, never author `.lua`/`.ps1` through a
bash heredoc, never let anything own the emulator's lifetime during human play,
verify the emulator from its binary, and never read a silent instrument as
negative evidence.

Two local convenience skills (`mgba-runtime`, `progress-site`) were also written
under the ignored `<tool-state>/` tree, by the maintainer's decision to keep them machine-local.
They are not repository artifacts, and the tracked docs above are authoritative.

## stopping point

Stopped at the measured Outcome A. **Do not begin TOOLKIT-032.**
