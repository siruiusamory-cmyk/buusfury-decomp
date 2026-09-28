# src/ - C/C++ reconstruction

Empty at DECOMP-BASELINE-001 by design: **no gameplay function has been
decompiled yet**, and the stop condition of this ticket forbids starting.

What belongs here, from DECOMP-ROM-MAP-001 / DECOMP-COMPILER-PROBE-001 onwards:

- C/C++ reconstruction of the regions `config/regions.json` marks `class: "ads"`,
  and later of the opaque `incbin` regions.
- One translation unit per original compilation unit, named after the region id
  where the original name is unknown.

Read `docs/DECOMP_BASELINE.md` first. The reference project's `src/` may **not**
be copied here (see `docs/REFERENCE_AUDIT.md`).
