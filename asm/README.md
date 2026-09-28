# asm/ - assembly reconstruction

Empty at DECOMP-BASELINE-001 by design.

What belongs here: hand-written assembly for regions that cannot be expressed in
C/C++ with matching codegen, and the scatter/link inputs.

The reference project keeps its assembly here too, but its files may **not** be
copied (see `docs/REFERENCE_AUDIT.md`). The only thing reproduced from it is the
region map and the command lines, which live in `config/regions.json` and
`tools/buusfury/build.py`.
