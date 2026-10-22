# Contributing

## Naming

Follow [docs/NAMING.md](docs/NAMING.md). A function whose purpose is known is `Module_Verb`; one
whose purpose is not yet known is `sub_0800XXXX` at its retail address. The symbol text is emitted
verbatim into the image, so a name that does not reproduce the retail symbol is a wrong build,
whatever the code does.

## Formatting

[.clang-format](.clang-format) is the style, and `format.cmd` applies it in place to every `.c`,
`.cpp`, `.h` and `.hpp` under `src\` and `include\`. The pre-commit hook in [`.githooks/`](.githooks/)
refuses a staged C or C++ file that is not format clean, and refuses a `tools\lint\lints.py`
finding; enable it with `git config core.hooksPath .githooks`.

## Converting a unit

- A unit is one `.c` file and its measured flags. Take the flags from the bytes, not from a
  comment: `tcpp -O2 -Otime -apcs /nointerwork`, never `/interwork`, and never `-O3`, which build
  805 does not have. A comment that names flags is a hypothesis until the emitted assembly shows
  them.
- The unit's start and the resume point where its bytes end must both be 0 mod 4. `armlink`
  refuses a region that is not word aligned (`L6268E`) and `armasm` refuses an `ALIGN=1` area
  (`A1481E`), so a unit at a 2 mod 4 offset cannot be placed at all.
- An unmatched unit is neither linked nor stubbed. Its retail bytes stay transcribed in `asm/`,
  and the reconstruction is parked as a `NONMATCHING-REFERENCE`: `tools\lint\lints.py` requires
  the marker in the header comment of every `src/*.c` that `rebuild.cmd` does not compile, and
  refuses the marker in a file it does compile. When the last body becomes byte-exact, the unit
  joins the build in the same change that proves the digest.

## Before you file

Run `python tools\gate\gate.py` and get `DIGEST MATCH` before the change is reviewed.
`python tools\check_links.py` and `python tools\lint\lints.py` must also pass; CI runs both on a
single-commit checkout.
