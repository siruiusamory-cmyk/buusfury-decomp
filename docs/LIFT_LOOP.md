# The lifting loop - how to add the next function family

`docs/LIFT_PILOT.md` records the first run and its results. This document is the
procedure: what to add, in what order, and which checks must pass before the family
counts as lifted.

No custom script is needed. The loop is data-driven from two files.

---

## The loop in one picture

```
config/lift_targets.json        <- one entry per translation unit (you add this)
config/compiler_probes.json     <- function boundaries, DERIVED from the ROM
        |
        v
src/<family>.c                  <- the decompiled source (you write this)
        |
        +--> compile  -mcpu=arm7tdmi -mthumb -O1     (modern toolchain)
        +--> link     at the unit's original ROM address
        +--> objcopy  -O binary
        |
        +--> SEMANTIC      run it on the host         src/probes/<family>_selftest.c
        +--> MODERN_BUILD  did it compile and emit bytes?
        +--> ADS_MATCH     BLOCKED (unlicensed ADS)   never inferred from the above
        |
        v
config/lift_<id>.json           <- the committed comparison
```

---

## Step 0 - is the family ready to lift?

Do not lift a family whose boundaries are not independently established. It qualifies
only if **all** of these hold:

- the region is an `isa` with `executable=confirmed` in `config/rom_map.json`;
- its functions were recovered by chain-walk recursive descent with **zero gaps and
  zero undecodable bytes**;
- its literal pool is accounted for, so the code body and the pool are separated;
- the region ends on an independently anchored boundary (another region start, a
  padding run, a table base).

A family found by the windowed classifier alone does not qualify. That classifier is
capped at `medium` precisely because this engine's Thumb data decodes like code.

---

## Step 1 - derive the boundaries, do not declare them

Boundaries belong in `config/compiler_probes.json`, which is regenerated from the ROM
and verified whole on every test run:

```powershell
python -m buusfury compiler-probe --write-manifest
python -m buusfury compiler-probe --rom <baserom> --verify-manifest
```

If the family is a new translation unit, add it to
`tools/buusfury/compiler_probe.py` the way `GBARAM_TU` is defined, including its
`boundary_evidence`. If it belongs to an existing unit, the unit already covers it.

**Never write function start/end pairs by hand.** A hand-written boundary is a claim
with no evidence behind it, and the whole point is that the ROM, not the author, says
where each function ends.

There are two supported ways to satisfy that, and they differ in what the ROM gives you:

| Path | Use when | Where the boundary lives |
| --- | --- | --- |
| **manifest** | the unit's literal pool is adjacent to its code, so the probe manifest's `(code_end, end_address)` schema fits | `config/compiler_probes.json`, derived and whole-document verified there |
| **derived** | the unit's literals are NOT adjacent, or a table's extent must be proved by what follows it | `tools/buusfury/lift.py`: `BCI_TU`, `BCI_FUNCTIONS`, and `derive_unit_boundaries`, re-derived and checked on EVERY run |

The ByteCodeInterpreter uses the **derived** path because two alignment bytes separate
its last function from its pool and a third literal word sits 86 bytes further on, which
the manifest schema cannot express. `derive_unit_boundaries` tile-checks the extents,
requires exactly one terminator per function and zero gaps, and **raises** on a
disagreement rather than absorbing it. `derive_dispatch_table` proves a function-pointer
table's length by decoding the string that follows it, because such a table has no length
field.

Use the aligned **chain-walk** for both derivation and any caller census. A linear sweep
from a region's first byte desyncs whenever that byte is not an instruction boundary and
then silently misses real branches; an earlier pass in this project under-counted the
callers of `0x08004038` as 2 when an aligned walk found 13.

If the family is a new translation unit on the **manifest** path, add it to
`tools/buusfury/compiler_probe.py` the way `GBARAM_TU` is defined, including its
`boundary_evidence`. If it takes the **derived** path, add its `TranslationUnit` and
function tuple to `lift.py` and make `derive_unit_boundaries` re-derive them.

---

## Step 2 - write the source in the real tree

Put the implementation at `src/<family>.c`, not under `src/probes/`. The probes
directory is for the harness, not for the product.

Naming: the reconstruction names each function `sub_<ROM address>` (for example
`sub_0803D4D0`). This is load-bearing - the lift harness pairs original and modern
functions **by symbol name**, so the pairing is exact and needs no heuristic. Do not
invent semantic names; the offsets and widths are evidence, the names are not.

Header comment requirements:

- state which original source file the surviving build evidence names, if any;
- separate what is **evidence** from what is a **placeholder**;
- record the three verdicts as three separate lines, since they are independent.

---

## Step 3 - add a probe shim, so there is one source of truth

`src/probes/<family>.c` is a shim:

```c
#include "../<family>.c"
```

A plain `#include`, so the compiler sees the same token stream whether it is invoked
through the probe path or the lift path. Verify it rather than assuming:

```
compile both entry points, disassemble both objects, compare the sha1 of the
disassembly. They must be identical.
```

If they differ, the shim is not a shim.

---

## Step 4 - register the target

Add an entry to `config/lift_targets.json`:

```json
{
  "id": "<family>",
  "name": "...",
  "ticket": "...",
  "probe_translation_unit": "<unit id>",
  "decomp_source": "src/<family>.c",
  "probe_source": "src/probes/<family>.c",
  "selftest_source": "src/probes/<family>_selftest.c",
  "semantic_minimum_checks": 0,
  "host_build_bits": 32,
  "compiler": { "cpu": "arm7tdmi", "isa": "thumb", "optimization": "-O1", "extra_flags": [] },
  "role": "...",
  "notes": "...why this family and why now..."
}
```

The compiler block describes the **modern** configuration only. It is not a claim
about the original compiler.

`semantic_minimum_checks` is per target on purpose: one global number would either wave
through a truncated run of a small self-check or fail a genuinely smaller one.

`host_build_bits` selects the host toolchain width. **A reconstruction that holds
pointers in `u32` fields models a 32-bit machine and must be built 32-bit.** Built
64-bit, the high half of every stored address is lost and the first dereference through
one faults with an access violation; that was observed, not predicted. Widening the
typedefs would hide the machine model rather than honour it. GBARam happens to work at
64-bit because its host mode never stores a pointer in a `u32` field; the
ByteCodeInterpreter does, so it declares 32.

---

## Step 5 - make the semantics checkable, and then check them

Write `src/probes/<family>_selftest.c` and **run it**. This is the single highest-value
step: the GBARam pilot found four real defects this way, and none of them could ever
have matched the ROM, so a compiler run before the behavioural run would have been
wasted.

Requirements:

- it compiles the reconstruction for the HOST and executes it;
- it prints exactly one summary line matching `<STATUS>: <n> check(s), <m> failure(s)`;
- it returns non-zero if any check fails;
- the harness compares `n` against the target's `semantic_minimum_checks` and reports
  `PARTIAL`, never `PROVEN`, when fewer checks ran than required. A self-check that
  stopped early otherwise looks exactly like one that passed.

What to assert: payloads inside the arena, no overlap, free list walkable with
symmetric links, totals conserved, and every documented sentinel actually firing. The
cheap invariants are the ones that catch reversed merges and lost nodes.

Two traps this project has already paid for, both worth reading before writing one:

1. **Read anything behind a cursor pointer from INSIDE a handler.** The cursor slot is a
   frame local of the function under test and is dead once it returns; dereferencing a
   saved pointer to it afterwards reads a dead stack frame.
2. **Make every synthetic program terminate deliberately.** When a NULL dispatch entry
   is the exit condition, a test whose stop handler clears the wrong slot runs off the
   end of the buffer and reports nonsense counts. Design the discriminator so that the
   wrong behaviour produces a *different* count, and assert the count.

If the unit calls code it does not contain, the link needs a value for each. Do **not**
add stub objects: they add bytes to the compared window. `derive_external_calls` reads
the unit's own BL targets out of the ROM and binds each `sub_<address>` symbol to its
original address, so every call displacement is right and nothing extra is emitted.

**Do not bind those symbols with `--defsym`.** It creates an absolute symbol with no
Thumb marking and bit 0 of the value does not change that, so the linker wraps every
external call in a Thumb-to-ARM interworking veneer: `bx pc` then an ARM branch, which
enters Thumb code in ARM state, plus eight bytes per call in the compared image. The
`bci` build carried five such veneers before this was caught. Use
`render_external_symbols`, which emits

```asm
	.syntax unified
	.thumb
	.globl sub_080046AA2
	.thumb_func
	.set sub_080046AA2, 0x080046AA2
```

and produce a direct Thumb `BL` with nothing emitted. A test asserts that no committed
report records a `--defsym` command and that no built ELF contains a `from_thumb` or
`from_arm` symbol.

---

## Step 6 - run the loop

```powershell
python -m buusfury lift --target <family> --rom <baserom> --write config/lift_<family>.json
python -m buusfury lift --target <family> --rom <baserom> --verify
```

Read the three verdicts separately. A `MODERN_BUILD PASS` with `SEMANTIC FAILED` means
the C is wrong; a `SEMANTIC PROVEN` with `MODERN_BUILD FAIL` means the plumbing is
wrong; `ADS_MATCH` is BLOCKED either way and is never inferred from the other two.

Then read the comparison for what it is: a measurement. Check that

- the call counts and literal-slot counts line up per function - if they do not, the
  reconstruction's *shape* is wrong and that is a real defect worth chasing;
- the pool structure is reported (one shared run in the original, more in the modern);
- `bytes_not_covered_by_an_original_instruction` is only the pool size.

---

## Step 7 - gate it

Add the target to gate 7 in `scripts/check.ps1` (or extend the existing invocation if
the gate already loops over targets), and add tests to `tests/test_lift.py` covering:

- the three verdicts are present and each is in its own vocabulary;
- `ADS_MATCH` is BLOCKED and carries `not_inferable_from_modern_build`;
- the comparison is not a match claim (`is_a_match_claim` is false);
- every count is clamped and adds up;
- every function is paired by name;
- the committed report is environment independent (no absolute path, LF only);
- `verify_report` fails when a key is changed - a verification that cannot fail is
  not a verification.

---

## Rules that the pilot established

1. **Run the reconstruction before spending a compiler run.** Behavioural defects
   cannot match under any compiler.
2. **Compare at translation-unit scope.** A function with a literal load has no
   meaning standalone.
3. **Key instruction-level comparison on the target's boundaries**, never on a
   positional text diff of two disassemblies.
4. **Three verdicts, three vocabularies.** Collapsing them is the defect class this
   design exists to prevent.
5. **Never call a modern build a match.** Record `is_a_match_claim: false` and mean it.
6. **An explicit toolchain root is authoritative.** Fail closed rather than silently
   using a different toolchain.
7. **A missing toolchain is BLOCKED, not FAIL** - the same contract as the ADS gates.
8. **Derive boundaries by aligned chain-walk, and re-derive on every run.** A linear
   sweep desyncs and under-counts.
9. **Prove a table's extent by what follows it.** A function-pointer table has no
   length field; the string after it does.
10. **Name fields by offset, and say plainly what is unknown.** No opcode meaning may be
    imported from another title, and the reconstruction should contain no `switch` over
    opcodes until one is proven.
11. **Build a 32-bit machine model 32-bit.** Do not widen a typedef to make a
    truncation warning go away.
