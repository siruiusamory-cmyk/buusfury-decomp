# Definition of done

One target for every ticket: the full image, as `python tools\gate\gate.py` measures it.

## What counts as source

- Code compiled from tracked source.
- A tracked table of plain numbers whose rows have a named layout and a consumer or a structural
  proof. An unlabeled byte dump is not source.
- Asset-directory PCM (733,911 B in 143 records) only through the audio decode route: the parser
  ties each run to the engine's sample and music tables, and a build-time generator emits it from
  that decoded model.
- A byte-exact generator that re-encodes assets from the user's own ROM at build time, with
  nothing from the ROM committed. An identity copy is not source.

## The finish line

- 100 % of the 8,388,608 B image. A byte that cannot be reached is named irreducible, with its
  reason.

## Timing

- Judged on a quiet host only. A TIMING-only failure on a loaded host does not block.

## Current gate output

```
source=7893334 of 8388608 (94.0959 %)
raw-data=494250 (5.8919 %) cited 291487 / runtime-cited 28800 / unreferenced 173963
identity copies=1024 (0.0122 %) extract 1024 / generator identity 0
accounted=8388608 of 8388608 (100.0000 %)
```

README.md carries the same figures; the README-numbers lint (`tools/lint/lints.py`) checks them
against `gate.source_bytes()` and reads README.md only, so this file is not linted for numbers.
