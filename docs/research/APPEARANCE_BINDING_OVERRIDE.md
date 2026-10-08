# An explicit takeover of a retail sprite binding

APPEARANCE-BINDING-OVERRIDE-001, inside the appearance line. Base: the frozen
appearance candidate plus the reverted widening (`8288663`).

## Why this exists

The appearance work first refused every sprite id a canonical record selects, on
the reasoning that the engine returns the earliest matching record and an appended
one would therefore be unreachable or would replace the retail resolution. A later
change admitted the ids that only non-negative-stat records select, on the
reasoning that those records cannot compete. **That reasoning was wrong**, and an
independent review of it found the loop that had been missed.

The resolver at `0x08027948` has two loops, loop 1 runs first, and what each
returns depends on the caller's second argument:

```
08027960  loop 1
08027972  cmp r5, #0            ; the second argument
08027978  blt -> skip           ; argument set: skip records with +0x0C < 0
0802798E  cmp r0, #0
08027990  bge -> skip           ; argument zero: skip records with +0x0C >= 0
08027992  return the index      ; so the argument decides which sign is a candidate
0802799C  loop 2, only if loop 1 found nothing
080279A6  cmp r5, #0
080279A8  beq 0x080279BC        ; argument zero: skip the stat test entirely
080279BC  compare the record's sprite and return it, whatever its sign
```

Consequences, both of which the rule follows:

- **Argument zero** (the caller at `0x08010312`): loop 1 returns the first record
  whose sprite matches AND whose `+0x0C` is negative; loop 2 would return the first
  match whatever its sign. A retail object carrying sprite 209 resolves through
  loop 2 to canonical record 42 today. An appended record carries `+0x0C = -1`, so
  loop 1 returns it **before** loop 2 is reached, and that lookup moves from the
  retail record to the authored one. **This is the takeover the opt-in is for.**
- **Argument set** (the caller at `0x0800FB72`, passing `[actor+0x224]`): both loops
  require `+0x0C >= 0` and a computed stat-record pointer to equal the argument, so
  an appended record is **never returned on that path at all**. Lookups through it
  are not redirected, and the surface says so rather than claiming every lookup
  changes.

And one id class that can never be taken over: if a canonical record with a
**negative** stat selects the id, loop 1 returns *that* record before any appended
one, at index 60-something rather than 232, so the authored record can never be
returned even with the opt-in set. 88 of the 198 canonical sprite ids are in that
class, and they are refused outright on the same grounds as id 149.

## The contract

- **Default refusal stands.** A sprite id any canonical record selects is refused,
  and the refusal names the opt-in rather than the id.
- **The opt-in is explicit and persisted.** `AuthoredAppearance.override` is a
  document field, always written, defaulting to off. It is never inferred from the
  sprite id: a reader of the document can see whether a takeover was asked for.
- **The build fails closed.** `new_records` is the single gate, so `validate_project`
  reports the collision as a problem and a build refuses it, unless **that exact
  record** carries the opt-in.
- **Duplicate authored ids remain forbidden**, unchanged.
- **The surface states the consequence.** The dialog carries a control labelled
  "Take over a sprite identity the retail table already uses" and this wording:

  > Taking over a retail binding redirects existing actors. The engine's search
  > returns an appended record before the retail one, so any actor in the game that
  > already carries this sprite id would show this authored appearance instead -
  > its on-screen name, description, portrait and stat record become the ones this
  > definition states. Enable this only when that redirection is what you intend,
  > and leaving it off keeps the retail resolution unchanged.

- The retail-selected ids are **listed in the surface**, labelled with the record
  that selects them, so taking one over is a deliberate choice rather than
  something reachable only by typing a number.

Nothing in the roster relocation or its census is touched by this ticket.

## What is proven, and by what

| claim | how |
| --- | --- |
| a collision is refused by default, and the refusal names the opt-in | ROM-gated test |
| the same collision is admitted when that record opts in | ROM-gated test |
| the build boundary fails closed | `validate_project` reports the problem |
| the built image carries the takeover record, stat `-1` | built image is read back |
| the intent is a document field, defaulting off, validated | model round-trip test |
| the surface warns in those words and defaults off | Workbench test |
| the two-loop mechanism above | disassembly, independently reviewed |

## Runtime acceptance

The chain, and what was observed through the explicit opt-in path
(`build/roster001/takeover.gba`, sha256 `DE9660F2...`, built from a document whose
every definition carries `override = true`):

| link | observation | where |
| --- | --- | --- |
| a retail actor using a colliding sprite id | objects `0x086B1DE8`, `0x086B1FE0`, `0x086B23D0` carry sprite ids 209, 211 and 215 | `takeover-run2` |
| an explicit authored override enabled | those records exist only because the document opted in; the same ids are refused without it | build and tests |
| the resolver returns an authored appearance >= 232 | `resolved index=232/233/235 past_canonical=true`, with `compare index=232 matched=true` | `takeover-run2`, frames 3466 and 4302 |
| the authored appearance data is visibly consumed | the Scouter's character screen shows **GOKU** and the Goku description for an object whose retail record says **Fighter** / "This is a martial artist from the Other World" | `takeover-run2`, `at-04000.png` |
| the post-canonical seen flag is written | **not observed on this build.** It was observed on the earlier engine-identical build (appended record at index 232, sprite 209, `+0x0C = -1`), whose only difference is the authoring-side gate the engine never sees: `flag_write index=232` and `flag index=232 value=0x01` | earlier campaign |

The strings settle the fourth link because they cannot be confused. Canonical record
42 binds text 988, which reads "Fighter"; appended record 232 binds text 1188, which
reads "Goku" and whose successor 1189 is the Goku description. A screen showing the
second pair for an object whose retail record holds the first is the authored record
being displayed.

The fifth link is the one gap. The message path that returns an appended record
appends the resolved index to a list (`0x0801031E`-`0x0801032E`) and does not
construct the appearance object, so the flag is written by a later step - in the
earlier campaign about five hundred frames after the resolution. The opt-in session
that reached the resolver ended roughly twelve hundred frames later, before that
step, and the run was never continued. Recording it as a gap rather than describing
it as satisfied.
