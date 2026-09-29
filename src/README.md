# src/ - C/C++ and C reconstruction

This is the **product tree**: the reconstructed source of the game.

Two function families are lifted here:

- **`src/GBARam.c`**, the small-block heap allocator, file `0x03D4D0..0x03D740`.
  See `docs/LIFT_PILOT.md`.
- **`src/ByteCodeInterpreter.c`**, the script engine's bytecode dispatch loop and
  its two in-unit companions, at `0x08004038..0x08004160`. Named after the path
  the ROM itself preserves (`T:\Source\ByteCodeInterpreter\ByteCodeInterpreter.cpp`).
  See `docs/LIFT_SCRIPT.md`.
- **`src/ByteCodeInterpreter_handlers.c`**, primary dispatch slot 2 at
  `0x08003CBE`, the handler that reaches the native dispatch table. A separate
  translation unit from the interpreter: its literal pool is at `0x08003F40`
  rather than `0x08004158`. See `docs/LIFT_HANDLER2.md`.

`docs/LIFT_LOOP.md` is how the next family is added.

## Conventions

- **One translation unit per original compilation unit.** Where the original
  filename is known from build evidence, use it: the GBARam file is called
  `src/GBARam.c` because the surviving command line names exactly that path.
- **Functions are named `sub_<ROM address>`** (`sub_0803D4D0`). Do not invent
  semantic names: the disassembly fixes offsets and access widths, not the
  names the game used. The lift harness pairs original and modern functions by
  symbol name, so this convention is load-bearing rather than cosmetic.
- **Say what is evidence and what is a placeholder**, in the file's own header.
  Assume a reader who will not trust either without being told which is which.
- **State the three verdicts separately** in each file header: SEMANTIC,
  MODERN_BUILD, ADS_MATCH. They answer different questions and none is evidence
  for another.

## Status vocabulary

| Verdict | Meaning |
| --- | --- |
| `SEMANTIC` | the reconstruction behaves correctly, checked by RUNNING it on the host |
| `MODERN_BUILD` | it compiles, links at its original address and emits bytes |
| `ADS_MATCH` | it reproduces the original compiler's output - **BLOCKED**, the ADS 1.2 on this machine is unlicensed |

## Probes are not the product

`src/probes/` holds the harness: self-checks and thin shims. It is not where
reconstruction lives. A file under `src/probes/` that contains an implementation
is a bug, and a test asserts the GBARam shim has not grown into a second copy.

## Licensing

The reference project's `src/` may **not** be copied here; it carries no licence
grant. See `docs/REFERENCE_AUDIT.md`. Everything in this tree is written from the
disassembly and the ROM's own structure.
