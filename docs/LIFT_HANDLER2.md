# Primary dispatch slot 2 (DECOMP-LIFT-SCRIPT-HANDLER-001)

**Status:** the first opcode handler is lifted, and it is the one that reaches the
native dispatch table.
**Target:** `0x08003CBE`, the code entry behind primary table word `0x08003CBF` (slot 2), Thumb.
**Baseline:** `e49e911c47b6fa8388583db73a51dab455ea2fbb`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

---

## 1. Three verdicts, still independent

| Verdict | Result | What it measures |
| --- | --- | --- |
| **SEMANTIC** | **PROVEN** | the cursor, index and selection behaviour, checked by RUNNING it: 23 assertions, 0 failures |
| **MODERN_BUILD** | **PASS** | it compiles, links at `0x08003CBE` and emits bytes: 40 bytes |
| **ADS_MATCH** | **BLOCKED** | whether it reproduces the original compiler: `ADS12_LICENSE_UNAVAILABLE` |

No match is claimed. The comparison carries `is_a_match_claim: false`.

---

## 2. The derived boundary

Derived by aligned chain-walk, re-derived on every run, raising on disagreement.

| | |
| --- | --- |
| Extent | `0x08003CBE..0x08003CD4` |
| Size | **22 bytes** |
| Instructions | **10** |
| Terminators | **one**, at `0x08003CD2` (`pop {r3, pc}`) |
| Gaps | none |
| Literal pool | `0x08003F40`, **620 bytes** past the end of the code |
| Dispatch entry | primary slot 2, table word `0x08003CBF` |

The entry is anchored twice over: the primary dispatch table holds it at slot 2,
and the chain-walk from that address terminates cleanly. A search of every
evidenced function in the image finds **no direct BL site** targeting it - the
handler is reached only through the dispatch table, by the interpreter's
`bx r2` thunk. That absence is the expected result, not a gap in the census.

It is a **separate translation unit** from the interpreter: different code, and a
literal pool at `0x08003F40` rather than `0x08004158`. Four other primary handlers
(slots 21, 22, 23, 24) load from the same pool word, which is what groups them.

---

## 3. The handler, all ten instructions

```
0x08003CBE  push {r3, lr}
0x08003CC0  ldr  r3, [r1]          r3 = the cursor value from the slot
0x08003CC2  ldrb r2, [r3]          r2 = ONE BYTE: the native index
0x08003CC4  adds r3, #1            the cursor advances by ONE
0x08003CC6  str  r3, [r1]          ... written back into the slot
0x08003CC8  lsls r1, r2, #2        index * 4 -> word indexing
0x08003CCA  ldr  r2, [pc, #0x274]  r2 = 0x08055098, the native table base
0x08003CCC  ldr  r1, [r2, r1]      r1 = native[index]
0x08003CCE  bl   0x08046AA2        the `bx r1` thunk
0x08003CD2  pop  {r3, pc}          the single exit
```

### Index encoding

**A single unsigned byte**, read with `ldrb` at `0x08003CC2`. Its range is
`0..255`. The indexed load scales it by four (`lsls r1,r2,#2`), so table entries
are four bytes wide. There is no prefix, no varint and no escape: one byte, one
selection.

### Dispatch calling convention

The engine has a thunk block at `0x08046AA0`, one entry per register:

| Address | Body |
| --- | --- |
| `0x08046AA0` | `bx r0` |
| `0x08046AA2` | `bx r1` |
| `0x08046AA4` | `bx r2` |
| `0x08046AA6` | `bx r3` |

The interpreter uses `bx r2` (handler in `r2`). **This handler uses `bx r1`**, with
the selected routine in `r1`.

Register state at the branch:

| Register | Holds | Argument or artifact? |
| --- | --- | --- |
| `r0` | the context, **unchanged** | **the argument** |
| `r1` | `native[index]` | the call target; also visible to the callee as its own address, because `bx r1` does not clear `r1` |
| `r2` | `0x08055098`, the table base | leftover: measured, not an argument |
| `r3` | the advanced cursor | leftover |

**The handler never writes `r0`.** It is context-transparent, so the context
reaches the native routine exactly as the interpreter passed it. That preserves
the contract the previous ticket proved (`r0 = context`, `r1 = address of the
cursor slot`) - this handler *consumes* `r1` and does not forward it.

To decide whether `r2` is an argument, **12 native routines were disassembled and
inspected** for whether they read a register before writing it:

| | Count |
| --- | ---: |
| read `r0` before writing it | **10 of 12** |
| read `r2` before writing it | **0 of 12** |

So `r0` is the argument and the table base in `r2` is incidental. That is a
bounded measurement over a sample, not a proof about all 266 entries.

### The handler cannot index out of bounds

The index is one byte, so it has 256 possible values; the table has 266 entries.
Every reachable index is therefore in range. That is a property of the two
encodings, not a check the code performs - and there is no bounds test in the
handler, because none is needed.

---

## 4. The native table is 266 entries, not 283

A prior claim in this repository said 283. **It is refuted**, and the refutation
is re-measured on every run rather than remembered.

The count is bounded on **both** sides, which is what makes it a proof rather
than a scan that happened to stop:

| Bound | Value | Why |
| --- | --- | --- |
| Lower | **256** | the index is one byte, so all 256 values must land inside the table or the handler could read past it |
| Upper | **266** | the primary dispatch table begins at `0x080554C0`, an address the interpreter loads for itself, and its own extent is anchored by the assertion string at `0x0805553C` |

`0x08055098 + 266 × 4 = 0x080554C0`, exactly the primary table's base.

Supporting measurements:

| | |
| --- | --- |
| Entries examined | 266 |
| Entries that are not in-cartridge Thumb pointers | **0** |
| Distinct targets | 265 |
| Target range | `0x08000206..0x08003BFC` |
| Words immediately *before* the base that are valid | 0, so the base is the start of the run |

### Why 283 is impossible

```
0x08055098 + 283 × 4 = 0x08055504
primary dispatch table: 0x080554C0 .. 0x0805553C
0x080554C0  <  0x08055504  <  0x0805553C
```

283 entries based at the address the handler loads would run **through** the
primary dispatch table and stop in the middle of it. A table based there cannot
have that many entries.

### An independent cross-check

A 2026 runtime capture in the project's memory recorded that **native slot 178
dispatches to `0x08003030`**. This ticket derived the table base and its indexing
purely statically, from the handler's own instructions. Reading index 178 from
`0x08055098` gives `0x08003031`, whose Thumb bit masks to **`0x08003030`** - an
exact match.

Two independent methods agreeing is the strongest evidence here that the base
address and the word indexing are both right.

---

## 5. The comparison

Artifact: `config/lift_handler2.json`, regenerated and compared key by key by gate 7.

| | Original | Modern |
| --- | ---: | ---: |
| Bytes | 22 | 40 |
| Differing bytes in the overlap | - | 15 |
| Instruction spans keyed on the original's boundaries | 10 | - |
| Spans byte-identical | - | 0 |
| Calls | 1 (`0x080046AA2`) | 1 |
| Literal slots | 1 | 1 |
| Return points | 1 | 1 |

The modern build is **18 bytes larger**, and no byte matches. The **call count,
literal count and return structure all agree**, which is the signal worth
reading: the reconstruction's shape is right and its code generation is not.

---

## 6. A linker defect this ticket found, and fixed for every target

The previous ticket bound each declared-not-reconstructed call with
`-Wl,--defsym=sub_<address>=0x<address>|1`. That is a trap:

**`--defsym` creates an ABSOLUTE symbol with no Thumb marking, and bit 0 of the
value does not change that.** The linker therefore wrapped every external call in
a Thumb-to-ARM interworking veneer:

```
__sub_0803D5B8_from_thumb:
  4778        bx pc
  e7fd        b.n self        (the low half of the ARM instruction)
  ea00e4f9    b 0x0803D5B8    (ARM branch)
```

The veneer does `bx pc`, switches to **ARM state**, and then takes an **ARM
branch** to the target. Every one of those targets is Thumb code, so the call
entered it in the wrong state. The veneer is also eight bytes per call, which
inflated the compared image and the reported modern size.

The `bci` build committed in the previous ticket had **five** such veneers and
reported 486 bytes. It now reports **446**.

### The fix

A generated assembly file marks each symbol as Thumb before assigning it, which
produces a direct Thumb `BL` to the original address and emits nothing at all:

```asm
	.syntax unified
	.thumb
	.globl sub_08046AA2
	.thumb_func
	.set sub_08046AA2, 0x08046AA2
```

Verified: `bl 8046aa2 <sub_08046AA2>` - a direct Thumb branch, no veneer, no
extra bytes. `render_external_symbols` emits this, and a test asserts that no
committed report records a `--defsym` command and that no built ELF contains a
`from_thumb` or `from_arm` symbol.

---

## 7. Proven, and unknown

### Proven

Every fact in section 3, each tied to an instruction, plus:

- the index is used **directly** as a table index - tested by making a byte read
  and a little-endian word read select *different* entries;
- the index is **unsigned and not sign-extended** - tested with `0xFF`;
- the cursor advances by exactly **one** byte, not four;
- the cursor is written back **before** the dispatch: the recording native routine
  reads the watched slot at call time and sees the advanced value;
- the context is passed through **unchanged, including NULL**;
- the handler modifies **nothing else** - it never writes `r0` and does not touch
  the table.

### Unknown, deliberately left unknown

- **What any native routine does.** Not one is reconstructed, and **no native
  index is given a name**. No meaning is imported from another LoG title;
- whether any native routine consumes `r2`, beyond the 12-entry sample;
- why the cursor protocol differs between handlers. This one consumes one byte;
  the interpreter's own loop does not have to.

A test asserts the file contains no `case` label and names no other LoG title, so
the promise is mechanical rather than editorial.

---

## 8. Limits

1. **One handler of thirty-one**, which itself is one of the engine's two tables.
2. **No native routine is touched**, so the handler still cannot do anything
   observable end to end.
3. **`ADS_MATCH` remains BLOCKED.** Every number in section 5 describes a modern
   compiler.
4. **The `r2` finding is a sample**, 12 of 266 entries.
5. **The 266 count is an upper bound from the neighbouring table.** It is the
   exact figure only if the native table ends where the primary table begins,
   which the absence of any invalid word in between supports.

---

## 9. Recommended next work

1. **The `sm7` reader behind opcode 1 at `0x08003C8A`** (table word `0x08003C8B`),
   as the ticket anticipates. It is the only other handler whose operand encoding
   is visible from the cursor protocol, so it is the second and independent test
   of the "handler rewrites `*p`" contract this ticket relied on. Its boundary
   should fall out of the same chain-walk.
2. **Primary slot 21 at `0x08003E84`**, which shares this handler's literal pool
   at `0x08003F40`. It is the cheapest way to establish whether that pool defines
   a translation unit or just a compiler-chosen grouping, which the report
   currently leaves open.
3. **`sub_080046AA2`'s thunk block, as a unit.** Six consecutive `bx rN` entries
   at `0x080046AA0`; lifting them together would close the call path from the
   interpreter through to a handler and from a handler through to a native
   routine, and their extent is self-evident from the register order.
4. **Native slot 178 at `0x08003030`.** It already has an independent runtime
   anchor from a prior capture, so it is the one native routine whose behaviour
   could be validated against an observation rather than only against statically
   read code.
