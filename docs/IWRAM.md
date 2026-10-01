# The runtime-copied IWRAM overlay

Part of the game's executable code does not run from the cartridge. At boot the
reset code copies a block of ARM code and data from ROM into IWRAM and runs it
from there, and the rest of the game reaches it through a family of small
trampolines. This document is the subject index for that work.

## How the code gets there

The reset routine programs DMA3 twice: a zero fill above IWRAM, then a verbatim
copy of **4,100 bytes** from ROM `0x087B79A4` to IWRAM `0x03000000`.

Because the copy is verbatim, every byte of the block is statically known: IWRAM
`0x03000000 + k` holds ROM `0x087B79A4 + k`. The transfer size is not assumed - it
is the reading under which the copy ends exactly at the first byte of the `0xFF`
fill in ROM and exactly at the destination of the other DMA setup, and it is
confirmed by the region tiling. See [`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md).

| | |
| --- | --- |
| ROM source | `0x087B79A4` |
| IWRAM destination | `0x03000000` |
| Copied | 4,100 bytes, verbatim |
| Code half | `0x03000000` .. `0x03000F44` (3,908 bytes) |
| Data tail | the remaining 192 bytes |

## How the rest of the game reaches it

There is no direct call into the block. Entry happens two ways:

- **A family of thirteen ROM trampolines** between `0x08049120` and `0x080491CC`,
  each an ARM `ldr pc, [pc, #-4]` whose literal *is* the destination, not a slot
  holding a pointer. Two further entries in the same family branch back into ROM
  rather than into IWRAM.
- **Three stored pointers** read by single ROM instructions, two of which are
  *installations* rather than calls: one writes a handler into the interrupt
  vector table, another installs the interrupt entry point into the GBA BIOS
  vector pointer at `0x03007FFC`.

That last one is worth remembering when reading any search-based conclusion: the
pointer is computed as `0x03007FC0 + 0x3C`, so the literal `0x03007FFC` occurs
nowhere in the image, and a search for the address as a stored word concludes -
wrongly - that the interrupt vector is never installed.

## What is in the block

| Family | Addresses |
| --- | --- |
| block memory: copy and fill in 4-byte and 2-byte units | `0x03000768`, `0x030007A8`, `0x030007FC`, `0x03000858` |
| byte-lane transforms | `0x030002DC`, `0x03000330` |
| strided gather | `0x03000388`, `0x030004C0` |
| Q22.10 fixed-point dot products | `0x03000560`, `0x03000700` |
| Q18.14 signed-byte resampling sampler | `0x03000868` |
| bit-stream decoders (with byte-identical helpers) | `0x03000040`, `0x03000CA0` |
| ten-bit field clamp and de-interleave | `0x03000A4C` |
| interrupt handler protocol | `0x03000AE0` |
| interrupt dispatch and vector table | `0x03000B6C`, table at `0x03000FB0` |

Two of these routines - `0x03000330` and `0x03000414` - are complete and
well-formed but nothing in the image reaches them: no branch, no stored pointer,
no computed jump. They are recorded as inferred dead code, not deleted.

The block has been described as holding twenty ARM functions. The committed
derivation enumerates **eighteen** complete functions, covering 3,876 of the 3,908
code bytes, plus the interworking halfword and a small literal pool. The
difference is recorded rather than papered over.

A census re-derived from the image for
[`LIFT_IWRAM_NUMERIC.md`](LIFT_IWRAM_NUMERIC.md) closes the gap to twenty and
locates the two: `0x0300028C` and `0x03000EF4` are 72-byte helpers reached by nine
`BL`s each from inside the windows of `0x03000040` and `0x03000CA0`, and they are
**byte-identical** to one another. The committed callgraph's `functions` array
predates that measurement; its `unreachable_code_runs` agrees with the census.

## The interrupt entry point

The dispatcher at `0x03000B6C` is the machine's IRQ entry. It saves the status
register, interrupt master enable and interrupt enable registers, computes the
pending set, scans the fourteen GBA interrupt sources in a fixed priority order,
acknowledges the served source **before** running its handler, and calls through a
14-entry vector table by `bx`, returning in Thumb state through a single
halfword.

Two of its behaviours are reproduced rather than corrected, because the original
does exactly that: a pending interrupt of the lowest-priority source spins
forever, and the acknowledgement writes back every flag pending at entry rather
than only the served one.

## What has been reconstructed

| Unit | What it covers |
| --- | --- |
| `src/IwramBlock.c` | the four block memory routines |
| `src/IwramDispatch.c` | the interrupt dispatcher |
| `src/IwramByteLanePair.c` | a byte-lane table transform |
| `src/IwramByteLaneSparse.c` | a sparse byte-lane store |
| `src/IwramQFormat.c` | the Q10 fixed-point transforms |
| `src/IwramQ1814.c` | the Q18.14 signed-byte resampling sampler |
| `src/IwramFieldClamp.c` | the ten-bit field clamp and de-interleave |

## Where the evidence is

| Document | Subject |
| --- | --- |
| [`LIFT_IWRAM_RUNTIME.md`](LIFT_IWRAM_RUNTIME.md) | how the copy works, and the block memory family |
| [`LIFT_IWRAM_DISPATCH.md`](LIFT_IWRAM_DISPATCH.md) | the dispatcher, the vector table and the interrupt protocol |
| [`LIFT_IWRAM_TRANSFORMS.md`](LIFT_IWRAM_TRANSFORMS.md) | the byte-lane and fixed-point transform families |
| [`LIFT_IWRAM_NUMERIC.md`](LIFT_IWRAM_NUMERIC.md) | the Q18.14 sampler and the ten-bit field clamp, and the family census |
| [`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md) | why the block's extent is believed |

## What remains unknown

- which of the two unreachable routines, if any, is reachable at run time through
  a pointer built from two registers;
- the semantics of the data tail at the end of the block;
- what most of the block's callers ultimately use it for: the routines are
  reconstructed, their call sites are not all identified to a subsystem.
