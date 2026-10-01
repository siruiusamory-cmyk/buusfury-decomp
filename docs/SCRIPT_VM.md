# The script engine

The game's dialogue, event scripting and a good deal of its logic run on a
bytecode interpreter. This document is the subject index for that work; each
reconstructed routine has its own write-up linked at the end.

## How it is recognised

Two things make this the best-documented subsystem in the project. The dispatch
loop's translation unit is bounded by its own literal pool, and the image
preserves the original source path for it as ASCII - the interpreter was written
in C++ by the original developers, and the path survives in the cartridge.

## Structure

| Part | Address | Notes |
| --- | --- | --- |
| dispatch loop | `0x08004038` | the interpreter's main loop |
| dialog entry point | `0x08004098` | calls the loop |
| primary handler table | `0x080554C0` | 31 entries; its extent is proved by the assertion string that follows it |
| native handler table | `0x08055098` | 266 entries; bounded below by the one-byte index and above by the primary table |
| value stack | context `+0x00` | a count, with values at `context + 4 + 4*i` |

A table with no length field is a recurring problem. The primary table's extent is
established by what follows it, not by a round number: slot 30 ends exactly where
the assertion string begins. The native table's 266 entries are fixed from both
sides - a one-byte index needs 256, and the next table's base caps it. An earlier
claim of 283 entries was refuted by that arithmetic rather than by preference.

## The value stack, and what the handlers do with it

Handlers receive a context pointer and manipulate a stack of 32-bit values.
The reconstructed families are:

- **reading operands** - a variable-length sign-magnitude encoding, read from a
  cursor the handler advances;
- **arithmetic** - addition, subtraction and multiplication of the top two
  values, written back to the lower slot;
- **consuming values** - popping a value and passing it into the engine;
- **flags** - a bit array inside an engine object, with a reader, a setter, a
  clearer, a gather that packs a run of bits into a mask, and an applier that
  writes a mask back into a run of flags;
- **boolean materialisation** - replacing the stack top with the truth of a flag,
  and with its inverse;
- **engine objects** - routines that pop values and drive a growable collection.

Several behaviours are reproduced rather than corrected because the original
machine does exactly that, and each is asserted by a test: there are no bounds
checks and no stack guards, an underflow walks the slot address below the context
object, one bypassed flag is used as a *bit index* rather than a truth value, and
a mask wider than 32 bits sets every flag because the ARM7TDMI's
register-controlled shift yields zero at an amount of 32 or more rather than
wrapping.

## What is not known

- what the flags mean. The bit array's contents are reconstructed; the game
  concepts they represent are not named, and no meaning is imported from another
  title in the series.
- what the native handlers do at the game level. Their stack behaviour is known;
  their purpose mostly is not.
- whether any handler's inputs are validated by the caller. Most of the guards the
  project expected to find are absent, which is recorded as the finding.

## Detail

| Document | Subject |
| --- | --- |
| [`LIFT_SCRIPT.md`](LIFT_SCRIPT.md) | the dispatch loop and its translation unit |
| [`LIFT_HANDLER2.md`](LIFT_HANDLER2.md) | the primary handler that reaches the native table |
| [`LIFT_OPERAND.md`](LIFT_OPERAND.md) | the variable-length operand reader |
| [`LIFT_STACK.md`](LIFT_STACK.md) | the value-stack consumer |
| [`LIFT_ARITH.md`](LIFT_ARITH.md) | the arithmetic family |
| [`LIFT_USE.md`](LIFT_USE.md) | the surviving-value consumer |
| [`LIFT_FLAGSTATE.md`](LIFT_FLAGSTATE.md), [`LIFT_FLAGREAD.md`](LIFT_FLAGREAD.md), [`LIFT_FLAGMASK.md`](LIFT_FLAGMASK.md), [`LIFT_BOOLUSE.md`](LIFT_BOOLUSE.md) | the flag and bit-array families |
| [`LIFT_NATIVE178.md`](LIFT_NATIVE178.md), [`LIFT_APPEND.md`](LIFT_APPEND.md), [`LIFT_COLLECTIONREAD.md`](LIFT_COLLECTIONREAD.md), [`LIFT_COLLECTIONWRITE2.md`](LIFT_COLLECTIONWRITE2.md), [`LIFT_COLLECTIONINSERT2.md`](LIFT_COLLECTIONINSERT2.md), [`LIFT_COLLECTIONFLUSH3.md`](LIFT_COLLECTIONFLUSH3.md) | the engine object and collection families |
| [`LIFT_EFFECT.md`](LIFT_EFFECT.md) | the bit-array setter |
| [`LIFT_LAYOUT.md`](LIFT_LAYOUT.md), [`LIFT_OBJECT.md`](LIFT_OBJECT.md) | the engine object layout the handlers act on |
