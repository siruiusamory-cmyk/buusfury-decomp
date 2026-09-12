"""ROM-ATLAS-001 evidence producers: the scripts that write the atlas inputs.

`tools/webfoot/atlas_build.py` assembles ten artifacts into one atlas, but the
scripts that *produced* those artifacts lived only in session scratchpads and
were never tracked. This package is those producers, promoted: every module here
is a port of one recovered scratchpad script, with its hardcoded repository path
replaced by explicit `rom_path` / `out_dir` parameters and its thresholds,
ordering, tie-breaking and serialization preserved byte-for-byte.

Two defects in the historical chain are deliberately NOT preserved:

* `atlas_scan.py` gated its six passes behind an `argv` pass selector, and the
  artifacts prove it ran in three partial invocations whose argv was never
  recorded. `scan` here always runs all six; the passes are mutually independent
  (each derives from `data` and the seed rows only).
* `regen.py` read `code_regions.jsonl` and overwrote that same file, so the
  artifact depended on a now-lost earlier version of itself. `regions` here
  derives every row from ROM bytes plus the two function files, never from a
  prior `code_regions.jsonl`.

`pipeline.run` is the canonical entry point and the only order that is claimed
to be reproducible.
"""

from .pipeline import run

__all__ = ["run"]
