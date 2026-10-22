# Naming conventions

Authored for this tree from its own bytes. PROVEN = measured at the retail bytes or in the toolchain; SUPPORTED = reproducible, not byte-exact; HYPOTHESIS = unverified.

## Functions

- Known purpose: `Module_Verb` in PascalCase, module first, one word, no underscores (`GBARam_Malloc`).
- Unknown purpose: `sub_0800XXXX`, the literal `sub_` and the retail address as eight uppercase hex digits (`sub_080143F2`); file offset 0x143F2 is address 0x080143F2.
- Not yet known to be a function: keep the generator form (`loc_0801444C`, `dat_0801440C`). Only evidence promotes a name, never repetition or a match in another project.
- Names are unique across the link, because the symbol text is emitted verbatim into the image.
- `asm/` exports follow the same two forms, and `tools\lint\lints.py` enforces them
  (`NAMING-asm-symbol`): every export is `Module_Verb` or `sub_`/`loc_`/`dat_`/`unk_`/`g_` and eight
  hex digits equal to the symbol's own address. `inc_0x<file start>_0x<file end>` is the one other
  admitted form: it names a raw slice by its extent, and nothing renames it.
- The count of address-named exports is held in `docs/NAMING_BASELINE.txt` and may only fall
  (`NAMING-address-ratchet`): a count above it fails, and a count below it fails until the baseline
  is lowered to the measured figure in the same tree. README's "<a> of the <b> symbols" sentence is
  the same two figures (`README-numbers`).

## Evidence for a name

`sub_` becomes `Module_Verb` only on evidence, and one class of it at a time. A promotion names the
register, call, string or format it proves, never the story around it:

| class | what the evidence is | where to look |
|---|---|---|
| a hardware register or BIOS call it drives | the instruction that writes or reads the register, or the `svc` number, quoted with its address; `python tools\research\name_evidence.py --mode function --function 0x…` prints every hardware access in the function and the literal it resolved from | GBATEK for the register or SWI name |
| a proven caller/callee role | the call sites and the registers they pass, or a tracked page that measured the role and quotes the bytes | `docs/research/`, the ledger's evidence cell |
| a retail string it alone references | the string's address, its index in the string table, and the fact that no other transcribed function loads it | `tools/text/strings_layout.json` |
| a data format a generator in `tools/` already decodes | the pointer or header the function reads into a region one of the generators emits | the generator's own record table |

Every promotion adds one row to `docs/NAMING_LEDGER.csv` (`address,old,new,evidence_class,evidence`)
in the same commit as the rename, and the row's evidence cell must be checkable by itself: the
address, the instruction or page, and the command or file that reprints it. When several functions
drive one register set and nothing further separates them, the name carries the set and a 1-based
ordinal in ascending address order (`Blend_WriteControl1`, `Blend_WriteControl2`); the ordinal is a
disambiguator, not a claim. A name that would claim more than its evidence is left `sub_`.

## Structs, fields and units

- Where the retail symbol names the type, reproduce that name exactly: `__FP19struct_MallocHeader` carries the 19-character type name `struct_MallocHeader`, and a tag named `MallocHeader` mangles to `__FP12MallocHeader` and does not reproduce it.
- Otherwise `typedef struct X { ... } X;` is allowed; a proven extent ends with `// size: 0x0c`, and padding no code reads is declared (`u8 filler_07[0x01];`), never left implicit.
- A proven field is named for its meaning in lowerCamelCase (`size`), never its offset; an unproven field is `unk_XX` with its offset as two lowercase hex digits (`unk_08`).
- One unit is one C file named after its module (`src/GBARam.c`). tcpp emits one literal pool per AREA (K-130), so the unit boundary is the pool boundary; `src/` holds C and C++, `include/` project headers, `asm/` transcribed spans.

## The tcpp mangling rule

Every C unit is compiled by tcpp (Thumb C++, ADS 1.2 build 805), so every definition has C++ linkage. The form is `<name>__F<parameter list>`, each parameter encoded by kind:

| encoding | meaning | example |
|---|---|---|
| `v` | `void` | `GBARam_Init__Fv` = `void GBARam_Init(void)` |
| `i` | `int` | `f__Fi` = `void f(int)` |
| `P` | pointer to the next item | `__FP19struct_MallocHeader` |
| `<n><name>` | a class or struct type, preceded by its DECIMAL length | `19struct_MallocHeader` |

A tagged struct mangles to its tag name, an untagged struct to the typedef name declaring the parameter; `19` is `strlen("struct_MallocHeader")`. `EXPORT |GBARam_Malloc|` is an unmangled `extern "C"` definition (K-130: removing `extern "C"` changes the name, not the code). Take the retail symbol from `asm/`, write the declaration whose mangling reproduces it, and check before linking:

```
tcpp -S -c -cpu ARM7TDMI -O2 -Otime -apcs /nointerwork src/Unit.c -o build/Unit.s
findstr /c:" PROC" build/Unit.s
```

## NONMATCHING-REFERENCE

An unmatched function is neither defined in a built `.c` file nor stubbed. Its retail bytes stay in `asm/` with the ledger row (`origin=transcription`, `evidence=byte-proven`), and the reconstruction is a `NONMATCHING-REFERENCE` header naming the span, the exact flags and a per-body measured table, kept out of `rebuild.cmd`.

`tools\lint\lints.py` requires the marker in every `src/*.c` the build does not compile and refuses it in one it does. When the last body is byte-exact, the asm span leaves, the ledger row retires and the unit joins the build in the ticket that proves the digest.

## Compiler flags

A unit is compiled `-O2 -Otime -apcs /nointerwork`, never `/interwork`, never `-O3` (absent in build 805: `C3056E: bad option '-O3'`). At `-O2` alone tcpp folds two stores of `GBARam_MarkAsUsed` and the function cannot be emitted; at `-O2 -Otime` all 28 instructions match 0x0803D4E8..0x0803D51E, and without `/interwork` `GBARam_Free` is its retail 214 B (K-130). Flags come from the bytes, never a comment (P-321).

A new unit includes `"global.h"` for `u8/u16/u32`, `vu8/vu16/vu32`, `bool8/bool32`, `ARRAY_COUNT` and `EWRAM_BASE`/`IWRAM_BASE`/`ROM_BASE`; `src/GBARam.c` predates it, and the ticket that next touches it deletes its four local declarations (lines 29-33) and adds the include.
