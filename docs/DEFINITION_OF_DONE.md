# Definition of done

One target for every change: the full image, as `python tools\gate\gate.py` measures it.

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

## The gate's accounting

```
source=<B> of 8388608 (<%>)                     code and data built from tracked source or a byte-exact generator
raw-data=<B> (<%) cited <B> / runtime-cited <B> /
                   unreferenced <B>             bytes the assembler still embeds from extracted slices
identity copies=<B> (<%) extract <B> / generator identity <B>
accounted=<B> of 8388608 (<%>)                  source plus raw-data; 100 % when every byte is in one
```

`source` is the image size minus the bytes `asm/*.s` INCBINs, so it cannot drift from what the
assembler reads.

## Timing

- Judged on a quiet host only. A TIMING-only failure on a loaded host does not block.

README.md carries the live figures; the README-numbers lint (`tools/lint/lints.py`) checks them
against `gate.source_bytes()` and reads README.md only, so this file is not linted for numbers.
