# DECOMP-LIFT-SCRIPT-001 - the first real engine subsystem

**Status:** the ByteCodeInterpreter entry function is lifted and the loop that
produced it is unchanged from the pilot.
**Target:** `0x08004038`, the bytecode dispatch loop, Thumb.
**Baseline:** `ad947f190063bdfae0f132924995aa7a45bda855`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the dispatch loop behaves correctly, checked by RUNNING it: 70 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x08004038` and emits bytes: 486 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

Nothing here reduces the ADS blocker and nothing may infer a match from the other
two. The comparison carries `is_a_match_claim: false`.

---

## 2. The derived boundary

Nothing below was hand-written. `derive_unit_boundaries` walks the ROM from each
entry, following local branches, and re-checks the result on **every** run; a
disagreement raises rather than being absorbed. `derive_dispatch_table` reads the
table's extent from the ROM.

| Function | Extent | Size | Instructions | Terminators |
| --- | --- | ---: | ---: | --- |
| `sub_08004038` | `0x08004038..0x08004098` | 96 B | 47 | one, at `0x0800408C` |
| `sub_08004098` | `0x08004098..0x08004102` | 106 B | 46 | one, at `0x080040B0` |
| `sub_08004102` | `0x08004102..0x08004156` | 84 B | 42 | one, at `0x08004154` |

Zero gaps, zero undecodable bytes inside each function, and the extents tile the
code body exactly. Two alignment bytes follow the last function, then an 8-byte
literal pool at `0x08004158`. Unit total: 296 bytes, of which 288 are code.

**Why three functions and not one.** They share **one** literal pool, which is
what establishes a single compilation unit, exactly as for GBARam. Lifting the
entry function alone would leave the pool's other consumers unexplained and make
the pool comparison meaningless. Nothing else of the script engine is touched.

### A correction worth recording

An earlier pass in this ticket derived the callers of `0x08004038` with a linear
sweep starting at each code region's first byte. That found **2** callers. A
linear sweep desyncs whenever a region does not begin on an instruction boundary,
and it then misses real branches. Re-doing it as an **aligned chain-walk** from
evidenced entries found **13**:

```
0x080040DC  0x080040EE  0x0800422E  0x080047FE  0x080089C4  0x080089F4
0x08008CE8  0x08008CFE  0x08012310  0x080141FA  0x0801420A  0x08014232  0x0801E182
```

Two of them are inside this unit (`sub_08004098`), the rest are external. The
count is still a **lower bound**: the walk only reaches functions whose entry is
independently evidenced, and one further site at `0x0801E15C` is reachable from
a containing function whose entry is not. The lift harness uses the aligned walk
for the same reason.

`0x08004038` has **one** direct callee in the unit's own code: the indirect-call
thunk `0x080046AA4`, a bare `bx r2` through which every handler is reached.

### The dispatch table, bounded by evidence not by memory

| | |
| --- | --- |
| Address | `0x080554C0` |
| Entries | **31** (slots 0..30) |
| Null entries | **[17]** - the terminate opcode |
| Entries that are Thumb pointers | 30 of 31 |
| What bounds it | the UTF-16 string at `0x0805553C` |

A function-pointer table has no length field. Its extent is proved by what
follows it: slot 30 ends where the assertion string begins. That string is the
engine's own words, **including its surrounding quote characters**:

```
"Expected dialog to start with a code block"
```

Comparing against the unquoted form left a false mismatch until the quotes were
included, which is why the harness reads the string rather than remembering it.

The 31 handler targets and the separate native table are **not** decompiled in
this ticket. They are not needed to prove the loop and the ticket forbids widening
into a broad script-engine decomp.

**Correction, measured by DECOMP-LIFT-SCRIPT-HANDLER-001:** this document
originally repeated a claim that the native table at `0x08055098` holds **283**
entries. That is wrong; it holds **266**. The count is bounded below by the
handler's one-byte index (256 values must all be in range) and above by the
primary dispatch table's base at `0x080554C0`, and 283 entries would reach
`0x08055504`, which is inside that table. See
[`LIFT_HANDLER2.md`](LIFT_HANDLER2.md#4-the-native-table-is-266-entries-not-283).

---

## 3. What is proven, and what is not

### Proven, each tied to an instruction

| Fact | Where |
| --- | --- |
| One byte is read, the cursor advances by one, and the byte indexes the table | `0x08004066..0x0800406E` |
| The handler is called with **r0 = context** and **r1 = the ADDRESS of the cursor slot** | `0x0800408E`, `0x08004090` |
| A handler can therefore consume inline operands by rewriting the slot | proven by running it |
| A **NULL** table entry terminates the run | `0x08004070`, `0x08004072` |
| Entry increments the counter at `0x03001034` and stores the context at `stack[old]` | `0x0800403E..0x08004048` |
| Terminate decrements it and, while it is non-zero, copies the **caller's** `+0x58` into `0x03001030` | `0x08004074..0x08004088` |
| `context+0x00` and `context+0x44` are zeroed on entry | `0x0800405C`, `0x08004060` |
| `context+0x58` and `0x03001030` receive the stream argument, or `context+0x5c` when it is 0 | `0x0800404A..0x08004058` |
| One exit only, at `0x0800408C` | derived |
| The dialog entry branches on the type byte at **record+2**; type 0 runs code at **record+3**, type 4 allocates `type<<9`, unpacks **record+4**, runs it and frees it, anything else asserts with file and line 60 | `0x080040B8..0x080040FA` |
| The context is **0x6C bytes** | `0x080040A4` allocates that; `sub_08001E164` reserves it on its own stack |

### Unknown, deliberately left unknown

- **Every field name.** The disassembly fixes each offset and access width and
  says nothing about what the game called it. Each context member is therefore
  named after its offset (`field_00`, `field_44`, `field_58`, `inline_5c`...), and
  a test asserts that mechanically.
- **What the handlers do.** No opcode has been decoded. The reconstruction
  contains no `switch` and no per-opcode table, and a test asserts that too. No
  meaning is imported from another LoG title.
- **`sub_08004102` keeps its address for a name.** Its control flow and memory
  effects are proven; its intent is not. It searches the nesting stack for a
  context whose `+0x58` equals the argument and, for the **first** match, copies
  four words out of the argument into that context's `+0x5c..+0x68` and re-points
  `+0x58` at its own inline area. Every **later** match is pointed at the first
  match's area, not its own. Why the search compares a pointer for equality, and
  what the four words mean, are unproven and not guessed at.

---

## 4. The comparison

Artifact: `config/lift_bci.json`, regenerated and compared key by key by gate 7.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes in the compared window | 296 | 486 |
| Differing bytes in the overlap | - | 284 |
| Instruction spans keyed on the original's boundaries | 136 | - |
| Spans byte-identical | - | 1 |
| Bytes not covered by an original instruction | 8 (the pool) | - |

The modern build is **190 bytes larger (+64%)**. Reported, not worked around.

### What agrees

| Per function | Original | Modern |
| --- | --- | --- |
| Call counts | 1, 5, 0 | **1, 5, 0** |
| Return points | 1, 1, 1 | **1, 1, 1** |
| Instruction counts | 47, 46, 42 | 75, 51, 58 |
| Literal slots | 2, 1, 1 | 5, 2, 4 |
| Sizes | 96, 106, 84 | 152, 116, 116 |

The **call counts and return structure match exactly**. That is the signal worth
reading: the reconstruction's shape is right and no byte of it is. The literal
counts rise because a modern compiler materialises each absolute address
separately.

### Literals

The unit's literals are **not** one shared run, unlike GBARam. They live in two
places:

| Slot | Value |
| --- | --- |
| `0x08004158` | `0x03001034` - the nesting counter |
| `0x0800415C` | `0x080554C0` - the dispatch table |
| `0x08004198` | `0x0805553C` - the assertion message |

`all_referenced_slots_are_declared` and `all_declared_slots_are_referenced` are
both true: every literal the code loads is a word the unit declares, and every
declared word is used. That accounting is the meaningful property. A "one shared
contiguous run" test would have reported a defect that is not there.

### External calls bound to their original addresses

The unit calls five things it does not contain. They are declared rather than
reconstructed, and the link binds each to the address read out of the unit's own
BL instructions, so every call displacement is right and no stub bytes pollute
the compared window:

| Symbol | Address |
| --- | --- |
| `sub_0803D5B8` | `0x0803D5B8` (the GBARam allocator, lifted in the other target) |
| `sub_0803D63C` | `0x0803D63C` (GBARam free) |
| `sub_0803DF14` | `0x0803DF14` (the assert helper) |
| `sub_08046AA4` | `0x080046AA4` (the `bx r2` call thunk) |
| `sub_08049120` | `0x08049120` (the container unpacker) |

The list is derived from the ROM, and a test re-derives it and asserts the
committed report agrees.

A note on the thunk: the reconstruction reaches handlers through `sub_08046AA4`
in the target build, exactly as `0x08004092` does. The host build calls the
handler directly, because the host has no ARM thunk; the self-check observes the
arguments either way.

---

## 5. Why the host check is built 32-bit

The reconstruction holds pointers in `u32` fields, because the machine it models
is 32-bit. Built with a 64-bit host compiler, every stored context address loses
its high half and the first dereference through one faults with an access
violation. That was observed, not predicted.

The fix is to build the self-check **32-bit** (`vcvars32`), which makes the
conversion lossless and keeps the machine model honest. Widening the typedefs
would have hidden the property instead of honouring it. `host_build_bits` is a
per-target registry field precisely so this cannot be forgotten.

---

## 6. Reproducing it

```powershell
python -m buusfury lift --list-targets
python -m buusfury lift --target bci --rom <baserom>
python -m buusfury lift --target all --rom <baserom> --verify
pwsh -File scripts/check.ps1          # gate 7 verifies every registered target
```

---

## 7. Limits

1. **Three functions of a large subsystem.** The engine also has 30 other
   handlers and a 266-entry native table, none of them touched here.2. **No opcode is decoded.** The reconstruction cannot execute real game
   bytecode; it can only be shown to dispatch, nest, terminate and mutate the
   context correctly.
3. **`ADS_MATCH` remains BLOCKED.** Every number in section 4 describes a modern
   compiler.
4. **The modern build does not fit the original footprint** (486 > 296 bytes).
5. **`sub_08004102` is not understood, only described.**
6. **The caller list is a lower bound**, for the reason given in section 2.

---

## 8. Recommended next ByteCodeInterpreter work

In the order the evidence supports:

1. **Handler 2 at `0x08003CBF`**, the `native_stack` opcode. It indexes the
   native table at `0x08055098` after pushing arguments, so it is the
   bridge between the bytecode layer and the engine and is the smallest step
   that makes the interpreter do something real. Its entry is a table slot, so
   its boundary is already anchored.
2. **The `sm7` varint reader used by opcode 1 at `0x08003C8B`.** Opcode 1 is the
   only other handler whose operand encoding is visible from the loop's cursor
   protocol, so it is the natural second test of the "handler rewrites `*p`"
   contract proven here.
3. **`sub_08004102`'s callers**, to settle what the four copied words mean. It
   cannot be named until something calls it with a known argument.
4. **The dialog type-4 unpacker `0x08049120`**, because `sub_08004098` proves the
   call contract: destination, source at record+4, size `type << 9`. Recovering
   it would make dialog type 4 checkable end to end.

Only after those should a broader handler sweep be attempted.
