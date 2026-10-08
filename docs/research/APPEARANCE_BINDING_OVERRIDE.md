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

The chain to observe, through the explicit opt-in path only:

```
retail actor using a colliding sprite id
  -> explicit authored override enabled
  -> resolver returns an authored appearance >= 232
  -> post-canonical seen flag written
  -> authored appearance data visibly consumed
```

The takeover observations recorded before this ticket existed are supporting
evidence only until the same behaviour is reproduced this way.

## The review, and what it changed

The first focused review of this contract returned **NOT SOUND**, with two blocking
findings, both verified here before the fix:

1. **The override was accepted for 88 ids where nothing is taken over.** An id a
   negative-stat canonical record selects is resolved by loop 1 to *that* record
   before any appended one, so the opt-in could not do anything. This inverted part
   of the earlier reasoning: the sign of the canonical record's stat decides whether
   an id is overridable at all, and the ids that *can* be taken over are exactly
   those whose canonical records are all non-negative. Those 88 ids are now refused
   outright.
2. **The two-loop description covered only a zero second argument.** With the
   argument set, an appended record is never returned, so the surface's warning
   overstated the effect. The wording now names the sprite-only lookup and says that
   stat-matched lookups are unaffected, and the docstrings state both cases.

Also fixed from the same review: duplicate entries in the sprite list when the
canonical vocabulary is the fallback, a label that named the first record selecting
an id rather than the one that resolves it, and wording that still said colliding
ids are refused without mentioning the opt-in.

Two tests were added at its request: one mixing an opted-in definition with a
colliding one that did not opt in, which a rule reading the opt-in once per
document would wrongly pass; and one using a negative-stat id, which the previous
helper never produced.

## Known limits of this contract

Recorded rather than left implicit, because each is a way the surface can mislead:

- **An opt-in on an id no canonical record selects does nothing.** The flag is
  accepted and the build is unaffected, because there is no retail resolution to
  take over. It is harmless, but it is not a silent takeover and the document says
  so; a reader of the build sees an ordinary appended record.
- **Taking over sprite 146 also redirects whatever carries 149.** The engine
  searches for 149 as 146 at `0x0802794E`-`0x0802795E` before it compares anything, so
  the two share a lookup. The surface labels 146 with that fact, and 149 itself
  remains unauthorable because a request for it is rewritten before any record is
  examined.
- **The takeover applies to the sprite-only search.** On the stat-matched path an
  appended record is never returned, so actors looked up that way keep their retail
  resolution. The warning states this rather than claiming every lookup changes.
- **No canonical id currently has two negative-stat records**, so the label that
  names the resolving record is unambiguous today. If one ever did, the label names
  the first, which is what the engine returns.
