# src/probes/ - compiler probe candidates

Reconstruction candidates used only to **identify the original compiler**. These
are not the ticket's decompilation product and must not be read as one; they are
the minimum source a compiler needs in order to be tested.

- `GBARam.c` - first hypothesis for the original `src/GBARam.c` translation unit
  at file `0x03D4D0..0x03D740`, named by the surviving build command line
  `tcpp -S -c -cpu ARM7TDMI -O1 src/GBARam.c`.

Status: **not validated**. No ADS 1.2 installation exists on the authoring
machine, so this file has never been compiled by the tool it targets. It compiles
under a modern GCC, which proves only that it is syntactically valid; that run is
tagged `DIAGNOSTIC_CONTROL_NOT_EVIDENCE` and says nothing about the original
compiler.

Assumptions, unresolved questions and the evidence behind each function are in
the file's own header comment, in
[`config/compiler_probes.json`](../../config/compiler_probes.json), and in
[`docs/COMPILER_PROBE.md`](../../docs/COMPILER_PROBE.md).

The original file may **not** be copied from `2genkidev/buusfury`; that
repository carries no licence grant. See
[`docs/REFERENCE_AUDIT.md`](../../docs/REFERENCE_AUDIT.md).
