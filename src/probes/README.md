# src/probes/ - the lifting harness, not the product

Reconstruction does **not** live here. It lives in the real tree: `src/GBARam.c`,
`src/<family>.c`. This directory holds only the machinery that tests it.

- `<family>.c` - a **shim**: `#include "../<family>.c"`. It exists so the compiler
  probe and the lift loop keep one stable entry point while the implementation has
  one home. A plain `#include` means the translation unit a compiler sees is
  identical whichever path invokes it; that is verified by compiling both and
  comparing disassembly, not assumed.
- `<family>_selftest.c` - compiles the reconstruction for the HOST and RUNS it.
  This is the SEMANTIC verdict. It is **not** compiler evidence and must never be
  cited as such: it says nothing about ADS 1.2 code generation. What it can do is
  falsify the reconstruction, and that is worth more than it sounds - a translation
  unit whose C is semantically wrong cannot match the ROM byte-for-byte under ANY
  compiler.

Running the reconstruction early is the technique that paid off: the GBARam pilot
found four real defects this way, a hang, an inverted merge, a misread sentinel and
a signedness error, none of which reading the disassembly had exposed, and none of
which could ever have matched. A compiler run spent before the behavioural run would
have been wasted.

## Current contents

- `GBARam.c` - shim for `src/GBARam.c`, eight Thumb functions at
  `0x0803D4D0..0x0803D740`.
- `gbaram_selftest.c` - 230 assertions over a 256 KiB arena. Exit 0 on success.
- `ByteCodeInterpreter.c` - shim for `src/ByteCodeInterpreter.c`, three Thumb
  functions at `0x08004038..0x08004160`.
- `bci_selftest.c` - 70 assertions driving the dispatch loop over synthetic
  bytecode with recording handlers. Exit 0 on success.
- `ByteCodeInterpreter_handlers.c` - shim for `src/ByteCodeInterpreter_handlers.c`,
  primary dispatch slot 2 at `0x08003CBE`.
- `handler2_selftest.c` - 23 assertions driving the handler with recording native
  routines, including discriminators that separate a byte index from a word index.
  Exit 0 on success.
- `ByteCodeInterpreter_operand.c` - shim for `src/ByteCodeInterpreter_operand.c`,
  primary dispatch slot 1 at `0x08003C8A`.
- `operand_selftest.c` - 42 assertions over the variable-length operand reader,
  exhaustive across every 1-byte input and every valid 2-byte input. Exit 0 on
  success.
- `ByteCodeInterpreter_stack.c` - shim for `src/ByteCodeInterpreter_stack.c`,
  primary dispatch slot 7 at `0x08003D3E`.
- `stack_selftest.c` - 34 assertions over the value-stack consumer, including an
  exhaustive sweep of 65,536 operand pairs and three successive underflows. The
  host context carries real storage BELOW the counter, because an underflowing
  pop writes there and the walk has to be observable and bounded. Exit 0 on
  success.
- `ByteCodeInterpreter_arith.c` - shim for `src/ByteCodeInterpreter_arith.c`,
  primary dispatch slots 8 and 9.
- `arith_selftest.c` - 45 assertions over both arithmetic handlers: an exhaustive
  65,536-pair sweep each, an antisymmetry sweep proving operand order, and the
  underflow results for each. Exit 0 on success.

Both self-checks print the summary line `<STATUS>: <n> check(s), <m> failure(s)`,
and the lift harness parses it, so the wording is load-bearing.

`bci_selftest.c` must be built **32-bit**. The reconstruction holds pointers in
`u32` fields because the machine it models is 32-bit; built 64-bit, the high half
of every stored context address is lost and the first dereference through one
faults. That is recorded per target as `host_build_bits` in
`config/lift_targets.json` rather than widened away.

Status of both: **SEMANTIC PROVEN**, **MODERN_BUILD PASS**, **ADS_MATCH BLOCKED**.
See `docs/LIFT_PILOT.md` for GBARam and `docs/LIFT_SCRIPT.md` for the
ByteCodeInterpreter, which also records what is deliberately left unknown (every
field name, every opcode meaning, and the intent of `sub_08004102`).

Add the next family with `docs/LIFT_LOOP.md`. The original file may **not** be copied
from `2genkidev/buusfury`; that repository carries no licence grant (see
`docs/REFERENCE_AUDIT.md`).
