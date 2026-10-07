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

The resolver at `0x08027948` has two loops, and loop 1 runs first:

```
08027960  loop 1: returns the first record whose sprite matches AND +0x0C < 0
0802799C  loop 2: runs only when loop 1 found nothing
080279A6  cmp r5, #0
080279A8  beq 0x080279BC     ; second argument zero -> skip the stat test entirely
080279BC  ldr r0, [r0, #4]   ; the record's sprite
080279C2  cmp r0, r7
080279C6  adds r0, r4, #0    ; return it, whatever the stat sign
```

So a retail object carrying sprite 209 resolves **through loop 2** to canonical
record 42. An appended record carries `+0x0C = -1`, so loop 1 returns it before
loop 2 is reached. Binding a canonically selected id therefore **redirects an
existing object's resolution**; it is a takeover, not an extension. The widening
did that silently, and the previous claim that "the resolver path is unchanged for
every canonical resolution" was false on the message path.

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
